/**
 * duo account map — a Duo account as a hub (req-duo-page, req-duo-layout-account-map).
 *
 * Reusable: the module reads only entity types and edges, never entity ids, so any page that
 * mounts a Duo account scene (the plugin's /duo, or an instance page) gets the same picture.
 *
 *                 [Phones ×n]  [WebAuthn credentials ×n]  [Hardware tokens ×n]
 *
 *   [Okta org] → [Okta app]                                         [Okta — phishing resistant]
 *   [VPN]      → [VPN app]          ──────  [ ACCOUNT ]  ──────      [Global Policy]
 *                [Admin API app]                                    [Contractors]
 *
 *                        [engineers]  [contractors]  (groups the applications admit)
 *
 * - Every duo__duo_account in the scene is a hub; blocks sit side by side when there are several.
 * - What an account holds comes from its HOLDS_ACCOUNT_OBJECT__duo edges. Those tenancy edges are
 *   hidden: the hub IS the tenancy.
 * - Applications form a column left of the hub. Whatever REQUESTS_SECOND_FACTOR__duo into an
 *   application (an Okta org, a VPN — another plugin's node, the edge's open source) and whatever a
 *   Duo SSO application ISSUES_SSO_ASSERTION__duo to sits further left, level with its application.
 * - Policies form a column right of the hub, the Global Policy first, then in the order of the
 *   applications that enforce them. ENFORCES_POLICY__duo edges are drawn application → policy.
 * - Groups form a row beneath; PERMITS_GROUP__duo edges are drawn application → group.
 * - Phones, hardware tokens and WebAuthn credentials are FOLDED: hidden, and replaced by one tile
 *   per enrolled-device type above the hub carrying its count. An account with none shows one
 *   muted tile saying so. The strength split within a type is the posture strip's.
 * - Anything else in the scene is still drawn, in a row under the picture, and reported as a
 *   warning — never dropped.
 *
 * Standard tap layout module: `export async function execute(context)`
 * (spec-viz-layouts.md, req-viz-layout-module-contract).
 */

import {applyStandardChrome} from "/static/tap_viz/js/runtime/chrome.js";

const T = {
    account: "duo__duo_account",
    application: "duo__duo_application",
    policy: "duo__duo_policy",
    group: "duo__duo_group",
    phone: "duo__duo_phone",
    token: "duo__duo_hardware_token",
    webauthn: "duo__duo_webauthn_credential",
};
const E = {
    holds: "HOLDS_ACCOUNT_OBJECT__duo",
    enforces: "ENFORCES_POLICY__duo",
    permits: "PERMITS_GROUP__duo",
    requests: "REQUESTS_SECOND_FACTOR__duo",
    sso: "ISSUES_SSO_ASSERTION__duo",
};
const FOLDED = new Set([T.phone, T.token, T.webauthn]);
const SYN_CLASS = "duo-synthetic";
const FOLD_CLASS = "duo-folded";

const GEOM = {
    leaf: {width: 190, height: 54},
    hub: {width: 230, height: 76},
    tile: {width: 180, height: 54},
    colGap: 150,       // hub edge → column edge
    outerGap: 120,     // application column → external column
    rowGap: 26,
    bandGap: 110,      // columns → groups row / device row
    blockGap: 320,     // between account blocks
    labelMax: 168,
};

//: The device tiles, one per enrolled-device type. The graph panel lifts no model fields onto
//: a cy node (only name, type, dimensions and tags), so the map folds by TYPE; the capability
//: split (Duo Push versus SMS/voice-only phones, security keys versus platform authenticators)
//: is the posture strip's, which reads the fields.
const TILES = [
    {kind: "phone", type: T.phone, label: "Phones"},
    {kind: "webauthn", type: T.webauthn, label: "WebAuthn credentials"},
    {kind: "token", type: T.token, label: "Hardware tokens"},
];
const TILE_COLORS = {
    phone: {fill: "#FFFFFF", border: "#6DB33F", label: "#2E5A12"},
    webauthn: {fill: "#ECF8E7", border: "#2F7A1F", label: "#1D4D12"},
    token: {fill: "#FFFFFF", border: "#8A8F99", label: "#3A3E46"},
    none: {fill: "#F3F4F6", border: "#B8BCC4", label: "#5D6270"},
};

const _type = (n) => n.data("entity_type");
//: The graph panel carries an edge's type as its label (panel-graph.js); prefer edge_type if set.
const _etype = (e) => e.data("edge_type") || e.data("label") || "";

export async function execute(context) {
    const {cy} = context;
    const warnings = [];
    const warn = (category, message) => {
        warnings.push({category, message});
        console.warn(`[duo account-map] ${category}: ${message}`);
    };

    // Re-entry: drop what an earlier pass added, un-fold what it hid.
    cy.remove(cy.elements("." + SYN_CLASS));
    cy.elements("." + FOLD_CLASS).removeClass(FOLD_CLASS);

    applyStandardChrome(cy, {leafTypes: [], edgeLabels: false});

    const edgesOf = (type) => cy.edges().filter((e) => _etype(e) === type);
    const holds = edgesOf(E.holds);
    const accounts = cy.nodes().filter((n) => _type(n) === T.account).sort((a, b) => String(a.data("label")).localeCompare(String(b.data("label"))));
    const placed = new Set();
    if (accounts.empty()) {
        warn("duo_no_account", "no duo__duo_account in the scene; nothing to centre the map on");
    }

    // Credentials reach the scene through users, which are not drawn, so they carry no edge to an
    // account. With one account they are its own; with several they cannot be attributed.
    const looseWebauthn = cy.nodes().filter((n) => _type(n) === T.webauthn);
    if (accounts.length > 1 && looseWebauthn.nonempty()) {
        warn("duo_webauthn_unattributed", `${looseWebauthn.length} WebAuthn credential(s) are in a multi-account scene; counted under ${accounts[0].data("label")}`);
    }

    let cursorX = 0;
    accounts.forEach((hub, i) => {
        const held = holds.filter((e) => e.source().id() === hub.id()).targets();
        const block = _placeAccount(cy, hub, held, i === 0 ? looseWebauthn : cy.collection(), placed, warn);
        // Shift the whole block so blocks sit side by side.
        const dx = cursorX - block.left;
        block.nodes.forEach((n) => n.position({x: n.position("x") + dx, y: n.position("y")}));
        cursorX += block.right - block.left + GEOM.blockGap;
    });

    // Tenancy is the hub itself: its edges are not drawn.
    holds.addClass("duo-tenancy");

    // Anything the map does not name: drawn under the picture, never dropped.
    const rest = cy.nodes().filter((n) => !placed.has(n.id()) && !n.hasClass(FOLD_CLASS) && !n.hasClass(SYN_CLASS) && !n.data("_is_badge"));
    if (rest.nonempty()) {
        const bb = cy.nodes().filter((n) => placed.has(n.id())).boundingBox();
        let x = (Number.isFinite(bb.x1) ? bb.x1 : 0) + GEOM.leaf.width / 2;
        const y = (Number.isFinite(bb.y2) ? bb.y2 : 0) + GEOM.bandGap;
        rest.sort((a, b) => String(a.data("label")).localeCompare(String(b.data("label")))).forEach((n) => {
            warn("duo_unmapped", `${n.data("label")} (${_type(n)}) has no place in the account map; drawn under it`);
            _size(n, GEOM.leaf);
            n.position({x, y});
            x += GEOM.leaf.width + GEOM.rowGap;
        });
    }

    _style(cy);
    return {warnings};
}

// ---------------------------------------------------------------------------
// One account block, placed around (0, 0); returns its nodes and horizontal extent.
// ---------------------------------------------------------------------------

function _placeAccount(cy, hub, held, extraCredentials, placed, warn) {
    const byType = (t) => held.filter((n) => _type(n) === t).sort((a, b) => String(a.data("label")).localeCompare(String(b.data("label"))));
    const apps = byType(T.application).toArray();
    const groups = byType(T.group).toArray();
    const policyNodes = byType(T.policy).toArray();
    const devices = held.filter((n) => FOLDED.has(_type(n))).union(extraCredentials);
    const nodes = [];
    const put = (n, x, y, size) => {
        _size(n, size);
        n.position({x, y});
        placed.add(n.id());
        nodes.push(n);
    };

    _size(hub, GEOM.hub);
    hub.position({x: 0, y: 0});
    hub.addClass("duo-hub");
    placed.add(hub.id());
    nodes.push(hub);

    const step = GEOM.leaf.height + GEOM.rowGap;
    const colY = (i, count) => (i - (count - 1) / 2) * step;
    const appX = -(GEOM.hub.width / 2 + GEOM.colGap + GEOM.leaf.width / 2);
    const extX = appX - (GEOM.leaf.width + GEOM.outerGap);
    const polX = GEOM.hub.width / 2 + GEOM.colGap + GEOM.leaf.width / 2;

    // Applications, and what sends users to them / what Duo SSO signs into, level with each.
    apps.forEach((app, i) => put(app, appX, colY(i, apps.length), GEOM.leaf));
    const externals = [];
    apps.forEach((app) => {
        const outside = cy.edges().filter((e) =>
            (_etype(e) === E.requests && e.target().id() === app.id()) ||
            (_etype(e) === E.sso && e.source().id() === app.id()));
        outside.forEach((e) => {
            const other = e.source().id() === app.id() ? e.target() : e.source();
            if (placed.has(other.id()) || externals.includes(other.id())) return;
            externals.push(other.id());
            const k = externals.filter((id) => cy.getElementById(id).data("_duo_app") === app.id()).length;
            other.data("_duo_app", app.id());
            put(other, extX, app.position("y") + k * (step / 2), GEOM.leaf);
        });
    });

    // Policies: Global first, then in the order of the applications that enforce them.
    const firstApp = (p) => {
        const idx = apps.findIndex((a) => cy.edges().some((e) => _etype(e) === E.enforces && e.source().id() === a.id() && e.target().id() === p.id()));
        return idx < 0 ? apps.length : idx;
    };
    //: is_global is not on the cy node (see TILES); Duo names the Global Policy "Global Policy".
    const isGlobal = (p) => /^global policy$/i.test(String(p.data("label")).trim());
    policyNodes.sort((a, b) => (isGlobal(b) - isGlobal(a)) || (firstApp(a) - firstApp(b)) || String(a.data("label")).localeCompare(String(b.data("label"))));
    policyNodes.forEach((p, i) => put(p, polX, colY(i, policyNodes.length), GEOM.leaf));

    const colHalf = Math.max(apps.length, policyNodes.length, 1) * step / 2;

    // Groups beneath.
    const gStep = GEOM.leaf.width + GEOM.rowGap;
    groups.forEach((g, i) => put(g, (i - (groups.length - 1) / 2) * gStep, colHalf + GEOM.bandGap, GEOM.leaf));

    // Devices folded into tiles above.
    const tiles = [];
    TILES.forEach((spec) => {
        const members = devices.filter((d) => _type(d) === spec.type);
        if (members.empty()) return;
        tiles.push({spec, members});
    });
    devices.addClass(FOLD_CLASS);
    const tStep = GEOM.tile.width + GEOM.rowGap;
    const tileY = -(Math.max(colHalf, GEOM.hub.height / 2) + GEOM.bandGap);
    if (tiles.length === 0) {
        const n = _tile(cy, hub, "none", "No enrolled devices on the grid", null, TILE_COLORS.none);
        put(n, 0, tileY, GEOM.tile);
    }
    tiles.forEach(({spec, members}, i) => {
        const icon = members[0].data("icon_url") || "";
        const n = _tile(cy, hub, spec.kind, `${spec.label} ×${members.length}`, {type: spec.type, icon}, TILE_COLORS[spec.kind]);
        put(n, (i - (tiles.length - 1) / 2) * tStep, tileY, GEOM.tile);
    });

    const xs = nodes.map((n) => n.position("x"));
    const half = GEOM.leaf.width / 2;
    return {nodes, left: Math.min(...xs) - half, right: Math.max(...xs) + half};
}

function _tile(cy, hub, kind, label, typeInfo, colors) {
    return cy.add({
        group: "nodes",
        data: {
            id: `duo-tile:${hub.id()}:${kind}`,
            label,
            entity_type: typeInfo ? typeInfo.type : "",
            icon_url: typeInfo ? typeInfo.icon : "",
            shape: "round-rectangle",
            fill_color: colors.fill,
            border_color: colors.border,
            label_color: colors.label,
        },
        classes: `${SYN_CLASS} duo-tile duo-tile--${kind}`,
    });
}

function _size(n, size) {
    n.style({width: size.width, height: size.height});
}

// ---------------------------------------------------------------------------
// Style
// ---------------------------------------------------------------------------

function _style(cy) {
    cy.style()
        .selector("node")
        .style({"text-valign": "center", "text-halign": "center", "text-margin-y": 0, "text-wrap": "ellipsis", "text-max-width": `${GEOM.labelMax}px`})
        .selector(".duo-hub")
        .style({"font-size": "16px", "font-weight": 600, "border-width": 3})
        .selector("." + FOLD_CLASS)
        .style({"display": "none"})
        .selector(".duo-tenancy")
        .style({"display": "none"})
        .selector(".duo-tile")
        .style({"border-width": 2, "border-style": "solid", "font-size": "13px"})
        .selector(".duo-tile--none")
        .style({"border-style": "dashed"})
        .selector(`edge[label = "${E.enforces}"]`)
        .style({"line-color": "#3B8526", "target-arrow-color": "#3B8526", "width": 2.5, "curve-style": "unbundled-bezier", "control-point-distances": [60], "control-point-weights": [0.5]})
        .selector(`edge[label = "${E.permits}"]`)
        .style({"line-color": "#8A8F99", "target-arrow-color": "#8A8F99", "line-style": "dashed", "width": 1.8, "curve-style": "bezier"})
        .selector(`edge[label = "${E.requests}"]`)
        .style({"line-color": "#1E4F8A", "target-arrow-color": "#1E4F8A", "width": 2.5, "curve-style": "bezier"})
        .selector(`edge[label = "${E.sso}"]`)
        .style({"line-color": "#6F42C1", "target-arrow-color": "#6F42C1", "line-style": "dotted", "width": 2.2, "curve-style": "bezier"})
        .update();
}
