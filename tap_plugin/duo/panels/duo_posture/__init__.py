"""duo-posture — the front of a Duo account in one strip: MFA coverage, factor mix, access,
administration and device trust, each count over what the grid holds for the selected account.

Spec: specs/spec-duo-v0.md (req-duo-panel-posture).

Reads go through Gryphon (``execute_gryphon_raw``, gated on ``grid.read``). The page's
``?account=`` names the account (its natural key, ``name``); absent, every account in the grid is
counted together, which is the one account when the grid holds one — and when it holds several
the strip says so and links each.

Three states, never two. A count over a field no collector has observed is not a zero: users
whose ``is_enrolled`` is null, phones whose ``capabilities`` are null and endpoints with no
Duo Desktop version are counted as *not observed*, beside the counts they would otherwise
silently inflate or deflate.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import urlencode

if TYPE_CHECKING:
    from django.http import HttpRequest

    from tap_web.models import Panel

logger = logging.getLogger(__name__)

T_ACCOUNT = "duo__duo_account"
T_USER = "duo__duo_user"
T_GROUP = "duo__duo_group"
T_APP = "duo__duo_application"
T_POLICY = "duo__duo_policy"
T_ADMIN = "duo__duo_administrator"
T_PHONE = "duo__duo_phone"
T_TOKEN = "duo__duo_hardware_token"
T_ENDPOINT = "duo__duo_endpoint"

#: The account predicate every read shares (see the page searches' input description): the
#: empty string selects every account; a name selects that account.
ACCT = "a.name STARTS_WITH $account AND a.name ENDS_WITH $account"
HOLDS = "(a:duo__duo_account)-[:HOLDS_ACCOUNT_OBJECT__duo]->"

QUERIES: dict[str, str] = {
    "accounts": "MATCH (a:duo__duo_account) RETURN a",
    "held": f"MATCH {HOLDS}(o) WHERE {ACCT} RETURN o",
    "user_webauthn": (
        f"MATCH {HOLDS}(u:duo__duo_user)-[:ENROLLS_WEBAUTHN_CREDENTIAL__duo]->(w:duo__duo_webauthn_credential) "
        f"WHERE {ACCT} RETURN u, w"
    ),
    "admin_webauthn": (
        f"MATCH {HOLDS}(ad:duo__duo_administrator)-[:ENROLLS_WEBAUTHN_CREDENTIAL__duo]->(w:duo__duo_webauthn_credential) "
        f"WHERE {ACCT} RETURN ad, w"
    ),
    "codes": f"MATCH {HOLDS}(u:duo__duo_user)-[:HOLDS_BYPASS_CODE__duo]->(b:duo__duo_bypass_code) WHERE {ACCT} RETURN b",
    "enforce": f"MATCH {HOLDS}(p:duo__duo_application)-[:ENFORCES_POLICY__duo]->(q:duo__duo_policy) WHERE {ACCT} RETURN p, q",
}

#: Admin API grants that change Duo rather than read it.
WRITE_GRANTS = frozenset(
    {
        "adminapi_write_resource",
        "adminapi_admins",
        "adminapi_integrations",
        "adminapi_settings",
        "adminapi_allow_to_set_permissions",
    }
)
PHISHABLE_METHODS = frozenset({"sms", "phonecall"})


@dataclass
class Tile:
    label: str
    value: int | str | None
    tone: str = "plain"  # bad | warn | good | look (not observed) | plain
    note: str = ""
    title: str = ""


@dataclass
class Section:
    key: str
    title: str
    tiles: list[Tile] = field(default_factory=list)


@dataclass
class AccountHead:
    name: str
    edition: str
    api_hostname: str
    helpdesk_bypass: str
    lockout_threshold: int | None
    href: str


def _data(element: dict[str, Any]) -> dict[str, Any]:
    """The data lane of an envelope node or edge (an edge's endpoints, type and properties live here)."""
    return dict(element.get("data") or {})


def _fetch(account: str) -> dict[str, dict[str, Any]]:
    from tap_grid.gryphon.executor import execute_gryphon_raw

    envs: dict[str, dict[str, Any]] = {}
    for key, query in QUERIES.items():
        inputs = {} if key == "accounts" else {"account": account}
        envs[key] = execute_gryphon_raw(query, inputs, layer="full")
    return envs


def _of(nodes: list[dict[str, Any]], entity_type: str) -> list[dict[str, Any]]:
    return [n for n in nodes if n.get("entity_type") == entity_type]


def _principals_with(env: dict[str, Any], principal_type: str) -> set[str]:
    """Entity ids of `principal_type` nodes that are the source of an edge in `env`."""
    ids = {n["entity_id"] for n in env.get("nodes", []) if n.get("entity_type") == principal_type}
    return {_data(e).get("from_entity_id") for e in env.get("edges", [])} & ids


def _pos(n: int, tone: str) -> str:
    return tone if n else "good"


def build_posture(envs: dict[str, dict[str, Any]], account: str) -> dict[str, Any]:
    """Fold the reads into the strip's context. Pure over envelopes (the tests feed real ones)."""
    all_accounts = sorted(_of(envs["accounts"].get("nodes", []), T_ACCOUNT), key=lambda n: str(n.get("name") or ""))
    selected = [n for n in all_accounts if not account or (n.get("name") or "") == account]
    heads = [
        AccountHead(
            name=str(n.get("name") or ""),
            edition=str(_data(n).get("edition") or ""),
            api_hostname=str(_data(n).get("api_hostname") or ""),
            helpdesk_bypass=str(_data(n).get("helpdesk_bypass") or ""),
            lockout_threshold=_data(n).get("lockout_threshold"),
            href="?" + urlencode({"account": n.get("name") or ""}),
        )
        for n in selected
    ]
    held = envs["held"].get("nodes", [])
    users = _of(held, T_USER)
    groups = _of(held, T_GROUP)
    apps = _of(held, T_APP)
    policies = _of(held, T_POLICY)
    admins = _of(held, T_ADMIN)
    phones = _of(held, T_PHONE)
    tokens = _of(held, T_TOKEN)
    endpoints = _of(held, T_ENDPOINT)
    codes = [n for n in envs["codes"].get("nodes", []) if n.get("entity_type") == "duo__duo_bypass_code"]
    user_webauthn = [
        n for n in envs["user_webauthn"].get("nodes", []) if n.get("entity_type") == "duo__duo_webauthn_credential"
    ]
    admin_webauthn = [
        n for n in envs["admin_webauthn"].get("nodes", []) if n.get("entity_type") == "duo__duo_webauthn_credential"
    ]
    webauthn = {n["entity_id"]: n for n in [*user_webauthn, *admin_webauthn]}.values()

    status = [str(_data(u).get("status") or "") for u in users]
    enrolled = [_data(u).get("is_enrolled") for u in users]
    n_bypass = status.count("bypass")
    n_locked = status.count("locked out")
    n_disabled = status.count("disabled")
    n_no_factor = sum(1 for v in enrolled if v is False)
    n_enrol_unobserved = sum(1 for v in enrolled if v is None)
    n_never_expire = sum(1 for c in codes if _data(c).get("expiration") in (None, ""))
    n_group_bypass = sum(1 for g in groups if _data(g).get("status") == "Bypass")

    caps = [_data(p).get("capabilities") for p in phones]
    n_push = sum(1 for c in caps if isinstance(c, list) and "push" in c)
    n_sms_only = sum(1 for c in caps if isinstance(c, list) and "push" not in c and ({"sms", "phone"} & set(c)))
    n_caps_unobserved = sum(1 for c in caps if c is None)
    labels = [str(_data(w).get("label") or "") for w in webauthn]
    n_keys = sum(1 for lbl in labels if lbl == "Security Key")
    n_platform = sum(1 for lbl in labels if lbl and lbl != "Security Key")
    n_label_unobserved = sum(1 for lbl in labels if not lbl)
    users_with_webauthn = _principals_with(envs["user_webauthn"], T_USER)
    admins_with_webauthn = _principals_with(envs["admin_webauthn"], T_ADMIN)

    all_users = [a for a in apps if _data(a).get("user_access") == "ALL_USERS"]
    adminapi = [a for a in apps if _data(a).get("integration_type") == "adminapi"]
    adminapi_write = [a for a in adminapi if WRITE_GRANTS & set(_data(a).get("adminapi_permissions") or [])]
    app_policy_ids = {
        _data(e).get("from_entity_id")
        for e in envs["enforce"].get("edges", [])
        if _data(e).get("edge_type") == "ENFORCES_POLICY__duo"
        and (_data(e).get("properties") or {}).get("apply_type") == "app"
    }
    on_global = [
        a for a in apps if a["entity_id"] not in app_policy_ids and _data(a).get("integration_type") != "adminapi"
    ]
    no_mfa = [p for p in policies if _data(p).get("new_user_behavior") == "no-mfa"]
    phishable = [p for p in policies if PHISHABLE_METHODS & set(_data(p).get("allowed_auth_methods") or [])]
    has_global = any(_data(p).get("is_global") is True for p in policies)

    roles = [str(_data(a).get("role") or "") for a in admins]
    admin_status = [str(_data(a).get("status") or "") for a in admins]
    trusted = [_data(e).get("trusted_endpoint") for e in endpoints]
    reporting = [bool(_data(e).get("health_app_client_version")) for e in endpoints]

    sections = [
        Section(
            "coverage",
            "MFA coverage",
            [
                Tile("Users", len(users), title="Every Duo user in the account."),
                Tile(
                    "In bypass", n_bypass, _pos(n_bypass, "bad"), title="Status bypass: these users skip MFA entirely."
                ),
                Tile(
                    "No authenticator",
                    n_no_factor,
                    _pos(n_no_factor, "bad"),
                    title="is_enrolled false: nothing to challenge them with. What happens at login is the New User Policy.",
                ),
                Tile(
                    "Enrollment not observed",
                    n_enrol_unobserved,
                    "look" if n_enrol_unobserved else "plain",
                    title="is_enrolled was never read for these users — unknown, not enrolled.",
                ),
                Tile("Locked out", n_locked, _pos(n_locked, "warn"), title="Status locked out."),
                Tile("Disabled", n_disabled, title="Status disabled."),
                Tile(
                    "Bypass codes",
                    len(codes),
                    _pos(len(codes), "bad"),
                    note=f"{n_never_expire} never expire" if n_never_expire else "",
                    title="Outstanding bypass codes: MFA satisfied by a passcode, no authenticator needed.",
                ),
                Tile(
                    "Groups in bypass",
                    n_group_bypass,
                    _pos(n_group_bypass, "bad"),
                    title="A group with status Bypass exempts every member.",
                ),
            ],
        ),
        Section(
            "factors",
            "Factor mix",
            [
                Tile("Duo Push phones", n_push, title="Phones whose capabilities include push."),
                Tile(
                    "SMS / voice only",
                    n_sms_only,
                    _pos(n_sms_only, "warn"),
                    title="Phones that can receive SMS or calls but not Duo Push: phishable factors only.",
                ),
                Tile(
                    "Phone capability not observed",
                    n_caps_unobserved,
                    "look" if n_caps_unobserved else "plain",
                    title="Phones whose capabilities were never read.",
                ),
                Tile(
                    "Security keys",
                    n_keys,
                    title="Roaming WebAuthn credentials (label Security Key): phishing-resistant.",
                ),
                Tile(
                    "Platform authenticators",
                    n_platform,
                    note=f"{n_label_unobserved} unlabelled" if n_label_unobserved else "",
                    title="WebAuthn platform authenticators (Touch ID, Windows Hello): phishing-resistant.",
                ),
                Tile("Hardware tokens", len(tokens), title="OTP hardware tokens: phishable."),
                Tile(
                    "Users with WebAuthn",
                    f"{len(users_with_webauthn)} / {len(users)}",
                    "good" if users and len(users_with_webauthn) == len(users) else "plain",
                    title="Users with at least one phishing-resistant credential enrolled.",
                ),
            ],
        ),
        Section(
            "access",
            "Access",
            [
                Tile("Protected applications", len(apps)),
                Tile(
                    "Open to all users",
                    len(all_users),
                    _pos(len(all_users), "warn"),
                    title="user_access ALL_USERS: every Duo user may authenticate.",
                ),
                Tile(
                    "On the Global Policy only",
                    len(on_global),
                    note="" if has_global else "no Global Policy on the grid",
                    title="Applications (other than Admin API) that enforce no custom app-level policy of their own.",
                ),
                Tile(
                    "Admin API applications",
                    len(adminapi),
                    _pos(len(adminapi_write), "warn"),
                    note=f"{len(adminapi_write)} can write" if adminapi_write else "",
                    title="Standing credentials to Duo itself; write grants can change who has to do MFA.",
                ),
                Tile(
                    "Policies letting unenrolled users in",
                    len(no_mfa),
                    _pos(len(no_mfa), "bad"),
                    title="New User Policy no-mfa.",
                ),
                Tile(
                    "Policies allowing SMS or voice",
                    len(phishable),
                    _pos(len(phishable), "warn"),
                    title="Allowed methods include sms or phonecall.",
                ),
            ],
        ),
        Section(
            "admin",
            "Administration",
            [
                Tile("Administrators", len(admins)),
                Tile("Owners", roles.count("Owner")),
                Tile(
                    "Without WebAuthn",
                    len(admins) - len(admins_with_webauthn),
                    _pos(len(admins) - len(admins_with_webauthn), "bad"),
                    title="Administrators with no phishing-resistant credential enrolled.",
                ),
                Tile(
                    "Not active",
                    sum(1 for s in admin_status if s and s != "Active"),
                    title="Disabled, Expired or Pending Activation.",
                ),
            ],
        ),
        Section(
            "devices",
            "Device trust",
            [
                Tile("Endpoints", len(endpoints)),
                Tile("Trusted", sum(1 for t in trusted if t is True)),
                Tile("Duo Desktop reporting", sum(reporting)),
                Tile(
                    "Posture not reported",
                    len(endpoints) - sum(reporting),
                    "look" if len(endpoints) - sum(reporting) else "plain",
                    title="No Duo Desktop version: this device's health is unknown, not healthy.",
                ),
            ],
        ),
    ]
    return {
        "posture_error": None,
        "account_param": account,
        "heads": heads,
        "choose": [
            AccountHead(str(n.get("name") or ""), "", "", "", None, "?" + urlencode({"account": n.get("name") or ""}))
            for n in all_accounts
        ]
        if len(all_accounts) > 1
        else [],
        "unknown_account": bool(account) and not selected,
        "sections": sections,
        "empty": not held,
    }


class DuoPosturePanelType:
    """The posture strip, rendered by the panel's own template."""

    slug: ClassVar[str] = "duo-posture"
    label: ClassVar[str] = "Duo posture"
    view: ClassVar[str] = "duo/panels/duo_posture.html"
    css: ClassVar[list[str]] = ["duo/css/duo_posture.css"]
    js: ClassVar[list[str]] = []
    editor_view: ClassVar[str] = ""
    config_defaults: ClassVar[dict[str, Any]] = {}

    @classmethod
    def get_view_context(cls, panel: Panel, request: HttpRequest) -> dict[str, Any]:
        """Run the reads and fold them; render the failure rather than a blank frame."""
        account = str(request.GET.get("account", "") or "")
        try:
            envs = _fetch(account)
        except Exception:  # noqa: BLE001 — the panel renders its failure, never a blank frame
            logger.exception("[d7a1] duo posture reads failed for panel %s", panel.entity_id)
            return {
                "posture_error": "Duo posture reads failed — see the server log ([d7a1]).",
                "sections": [],
                "heads": [],
                "choose": [],
            }
        return build_posture(envs, account)
