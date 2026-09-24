"""The /duo page bundle (req-duo-page), its searches, and the posture strip (req-duo-panel-posture).

The searches are executed for real against a seeded two-account estate, so each one is proven to
return the selected account's objects and never the other's — the property the page's ?account=
contract rests on.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import jsonschema
import pytest
from tap_plugin.duo.panels.duo_posture import QUERIES, _fetch, build_posture
from tap_plugin.duo.tests.seed import seed_estate

import tap_grid
from tap_auth.actors import BOOTLOADER, acting_as, get_builtin_actor
from tap_grid.gryphon.executor import execute_gryphon_raw

BUNDLE = Path(__file__).resolve().parents[1] / "grift" / "duo-page.grift.json"
DOC = json.loads(BUNDLE.read_text())
NODES = DOC["batches"][0]["nodes"]
EDGES = DOC["batches"][0]["edges"]
SEARCHES = {n["node"]["name"]: n["node"] for n in NODES if n["entity"]["entity_type"] == "search"}
DB = pytest.mark.django_db(transaction=True, databases=["default", "search_readonly"])


def _q(name_fragment: str) -> str:
    matches = [s for n, s in SEARCHES.items() if name_fragment in n]
    assert len(matches) == 1, name_fragment
    return "\n".join(matches[0]["definition"]["query"])


def _run(name_fragment: str, account: str | None) -> dict:
    """Run one page search; ``None`` is ?account= absent (the schema default), every account."""
    return execute_gryphon_raw(_q(name_fragment), {"account": account}, layer="full")


def _names(env: dict) -> set[str]:
    return {n["name"] for n in env["nodes"]}


class TestBundle:
    def test_validates_against_the_grift_schema(self) -> None:
        """req-duo-page-1: the bundle is a valid GRIFT document."""
        schema = json.loads((Path(tap_grid.__file__).parent / "schemas" / "grift-document.schema.json").read_text())
        jsonschema.validate(DOC, schema)

    def test_ids_unique(self) -> None:
        ids = [x["entity"]["entity_id"] for x in [*NODES, *EDGES]] + [DOC["batches"][0]["batch_entity"]["entity_id"]]
        assert len(ids) == len(set(ids))

    def test_every_slot_has_exactly_one_panel(self) -> None:
        """req-duo-page-2: layout panel-ids and USES_PANEL hotlink values agree exactly."""
        page = next(n for n in NODES if n["entity"]["entity_type"] == "page")
        slots = [r["panel-id"] for c in page["node"]["layout"]["columns"].values() for r in c["rows"].values()]
        uses = [e["edge"]["properties"]["hotlink"]["value"] for e in EDGES if e["edge"]["edge_type"] == "USES_PANEL"]
        assert sorted(slots) == sorted(uses)
        assert slots[0] == "map"

    def test_graph_is_icon_badge_and_edges_are_named(self) -> None:
        """req-duo-page-3: the map is icon-badge, and no scene search is an unfiltered edge search."""
        projection = next(n for n in NODES if n["entity"]["entity_type"] == "projection")
        assert projection["node"]["definition"]["node_style"] == {"mode": "icon-badge"}
        for name, search in SEARCHES.items():
            assert search["search_type"] == "gryphon", name
            query = " ".join(search["definition"]["query"])
            assert "[:" in query or "[e:" in query, name  # every search names the edge types it walks

    def test_every_search_takes_the_account_input(self) -> None:
        """req-duo-page-4: every search accepts ?account=, nullable with a null default, and filters with
        `$account IS NULL OR …`: absent is every account, a name is matched exactly."""
        for name, search in SEARCHES.items():
            account = search["input_schema"]["properties"]["account"]
            assert account["type"] == ["string", "null"] and account["default"] is None, name
            query = " ".join(search["definition"]["query"])
            assert "$account IS NULL OR" in query and "STARTS_WITH" not in query, name

    def test_okta_org_clicks_through_to_okta(self) -> None:
        """req-duo-page-9: the map routes a click on an Okta org to /okta for that org; nothing else navigates.
        The rule is panel config naming a page path, not a dependency: duo still declares none on okta."""
        from tap_viz.panels.graph_panel import _apply_nav_rules

        panel = next(n for n in NODES if n["entity"]["entity_type"] == "panel" and n["node"]["view"] == "tap_viz/panels/graph_panel.html")
        org = {"entity_type": "okta__okta_org", "data": {"name": "Acme Okta"}}
        app = {"entity_type": "duo__duo_application", "data": {"name": "Okta"}}
        _apply_nav_rules([org, app], panel["node"]["config"]["nav_rules"], "duo-account-map")
        assert org["display"]["tap_viz"]["nav_url"] == "/okta?org=Acme%20Okta"
        assert "display" not in app
        manifest = tomllib.loads((BUNDLE.parents[1] / "tap-plugin.toml").read_text())
        assert "okta" not in {d["slug"] for d in manifest.get("depends_on", [])}

    def test_no_dotted_dimension_paths(self) -> None:
        """Dotted dimension keys must be bracketed in Gryphon; a dotted path silently matches nothing."""
        for name, search in SEARCHES.items():
            assert ".dimensions." not in " ".join(search["definition"]["query"]), name


@DB
class TestImport:
    def test_imports_into_a_grid(self) -> None:
        """req-duo-page-5: the bundle imports cleanly (strict dangling edges) and the page resolves."""
        from tap_grid.grift.importer import grift_import
        from tap_web.models import Page

        with acting_as(get_builtin_actor(BOOTLOADER)):
            result = grift_import(DOC)
        assert result.success, [i.message for i in result.errors]
        assert Page.objects.filter(slug="/duo").exists()


@DB
class TestSearches:
    def test_scene_core_is_account_scoped(self) -> None:
        """req-duo-page-6: the map's core scene holds the account, its applications, policies and groups only."""
        seed_estate()
        env = _run("account, applications, policies, groups", "Duo Federal")
        assert _names(env) == {
            "Duo Federal",
            "Okta",
            "TAP collector",
            "Global Policy",
            "Okta — phishing resistant",
            "Contractors",
            "engineers",
            "contractors",
        }
        assert "Other VPN" in _names(_run("account, applications, policies, groups", None))

    def test_scene_edges(self) -> None:
        seed_estate()
        assert _names(_run("applications' policies", "Duo Federal")) == {
            "Okta",
            "Okta — phishing resistant",
            "Contractors",
        }
        assert _names(_run("permitted groups", "Duo Federal")) == {"Okta", "engineers", "contractors"}
        devices = _run("phones and hardware tokens", "Duo Federal")
        assert {n["entity_type"] for n in devices["nodes"]} == {
            "duo__duo_account",
            "duo__duo_phone",
            "duo__duo_hardware_token",
        }
        assert len([n for n in devices["nodes"] if n["entity_type"] == "duo__duo_phone"]) == 2
        assert _names(_run("WebAuthn credentials", "Duo Federal")) == {"YubiKey 5C"}

    def test_users_attention_three_states(self) -> None:
        """req-duo-page-7: bypass, locked out, not enrolled AND enrollment-not-observed are listed; the other account's are not."""
        seed_estate()
        assert _names(_run("users not doing MFA", "Duo Federal")) == {"bob", "carol", "dave", "erin"}
        assert "mallory" in _names(_run("users not doing MFA", None))

    def test_assignments_and_codes_rows(self) -> None:
        seed_estate()
        rows = _run("policy assignments", "Duo Federal")["rows"]
        assert {(r["application"], r["policy"], r["apply_type"]) for r in rows} == {
            ("Okta", "Okta — phishing resistant", "app"),
            ("Okta", "Contractors", "group_app"),
        }
        codes = _run("bypass codes", "Duo Federal")["rows"]
        assert codes == [
            {
                "username": "bob",
                "user_status": "bypass",
                "created": None,
                "expires": False,
                "expiration": None,
                "reuse_count": 1,
                "issued_by": "helpdesk@example.com",
            }
        ]

    def test_tables_envelope_mode(self) -> None:
        """Tables bind envelope searches (typed nodes), scoped to the account."""
        seed_estate()
        assert _names(_run("protected applications", "Duo Federal")) == {"Okta", "TAP collector"}
        assert _names(_run("policies of an account", "Duo Federal")) == {
            "Global Policy",
            "Okta — phishing resistant",
            "Contractors",
        }
        assert _names(_run("administrators", "Duo Federal")) == {"Owner One"}
        assert _names(_run("endpoints", "Duo Federal")) == {"alice-mbp"}

    def test_unknown_account_matches_nothing(self) -> None:
        seed_estate()
        assert _names(_run("protected applications", "Duo")) == set()


@DB
class TestPosture:
    def test_counts_for_one_account(self) -> None:
        """req-duo-panel-posture-1..3: counts are the selected account's, and not-observed is its own count."""
        seed_estate()
        ctx = build_posture(_fetch("Duo Federal"), "Duo Federal")
        assert [h.name for h in ctx["heads"]] == ["Duo Federal"]
        tiles = {(s.key, t.label): t for s in ctx["sections"] for t in s.tiles}
        assert tiles[("coverage", "Users")].value == 5
        assert tiles[("coverage", "In bypass")].value == 1
        assert tiles[("coverage", "No authenticator")].value == 1
        assert tiles[("coverage", "Enrollment not observed")].value == 1
        assert tiles[("coverage", "Enrollment not observed")].tone == "look"
        assert tiles[("coverage", "Bypass codes")].value == 1
        assert tiles[("coverage", "Bypass codes")].note == "1 never expire"
        assert tiles[("factors", "Duo Push phones")].value == 1
        assert tiles[("factors", "SMS / voice only")].value == 1
        assert tiles[("factors", "Security keys")].value == 1
        assert tiles[("factors", "Platform authenticators")].value == 1
        assert tiles[("factors", "Users with WebAuthn")].value == "1 / 5"
        assert (
            tiles[("access", "On the Global Policy only")].value == 0
        )  # Okta has its own; the Admin API app is not counted
        assert tiles[("access", "Admin API applications")].value == 1
        assert tiles[("access", "Admin API applications")].note == ""  # read-only grants
        assert tiles[("admin", "Without WebAuthn")].value == 0
        assert tiles[("devices", "Posture not reported")].value == 1

    def test_unobserved_expiry_is_not_never(self) -> None:
        """req-duo-panel-posture-6: a bypass code whose expiry was not observed is not counted as never
        expiring; only expires=false is."""
        from tap_grid.services import WriteOperation, create_node, write_batch

        e = seed_estate()
        code = create_node("duo__duo_bypass_code", {"bypass_code_id": "DBUNKNOWN00000000001"}).entity_id
        assert write_batch(
            [
                WriteOperation(
                    verb="create_edge",
                    from_target=e["bob"],
                    to_target=code,
                    edge_type="HOLDS_BYPASS_CODE__duo",
                    payload={},
                )
            ]
        ).success
        tiles = {
            (s.key, t.label): t
            for s in build_posture(_fetch("Duo Federal"), "Duo Federal")["sections"]
            for t in s.tiles
        }
        assert tiles[("coverage", "Bypass codes")].value == 2
        assert tiles[("coverage", "Bypass codes")].note == "1 never expire, 1 expiry not observed"

    def test_several_accounts_without_a_choice(self) -> None:
        """req-duo-panel-posture-4: with several accounts and no ?account=, the strip offers each."""
        seed_estate()
        ctx = build_posture(_fetch(None), None)
        assert [c.name for c in ctx["choose"]] == ["Duo Federal", "Other"]
        assert ctx["choose"][0].href == "?account=Duo+Federal"

    def test_queries_name_their_edges(self) -> None:
        for key, query in QUERIES.items():
            assert key == "accounts" or "[:" in query, key

    def test_named_account_is_exact(self) -> None:
        """req-duo-panel-posture-5: with accounts "A" and "ABA", ?account=A counts A alone, and so do the
        page's searches: an account whose name merely starts and ends with "A" is not selected."""
        from tap_grid.services import WriteOperation, create_node, write_batch

        ids = {}
        for name, user in (("A", "DUA000000000000000001"), ("ABA", "DUABA0000000000000001")):
            ids[name] = create_node("duo__duo_account", {"name": name}).entity_id
            uid = create_node("duo__duo_user", {"user_id": user, "status": "bypass"}).entity_id
            assert write_batch(
                [
                    WriteOperation(
                        verb="create_edge",
                        from_target=ids[name],
                        to_target=uid,
                        edge_type="HOLDS_ACCOUNT_OBJECT__duo",
                        payload={},
                    )
                ]
            ).success
        ctx = build_posture(_fetch("A"), "A")
        tiles = {(s.key, t.label): t for s in ctx["sections"] for t in s.tiles}
        assert tiles[("coverage", "Users")].value == 1
        assert "ambiguous_with" not in ctx
        assert len(_run("users not doing MFA", "A")["nodes"]) == 1
        assert len(_run("users not doing MFA", None)["nodes"]) == 2

    def test_blank_account_is_a_value_on_the_strip_and_the_tables(self) -> None:
        """req-duo-page-4: a blank ?account= names no account, for the strip and the page's searches alike,
        so the strip never counts every account above tables that show none. Absent is every account."""
        seed_estate()
        ctx = build_posture(_fetch(""), "")
        assert ctx["heads"] == [] and ctx["unknown_account"] is True
        assert _run("users not doing MFA", "")["nodes"] == []
        assert build_posture(_fetch(None), None)["unknown_account"] is False


def _panel_id(slug: str) -> str:
    """The panel's URL id: <slug>--<uuid> (tap_web.page.parse_panel_url_id)."""
    uuid = next(
        n["entity"]["entity_id"] for n in NODES if n["entity"]["entity_type"] == "panel" and n["node"]["slug"] == slug
    )
    return f"{slug}--{uuid}"


@DB
class TestRender:
    """The page and its panel fragments render server-side through Django's test client, over the
    imported bundle and a seeded estate. Client-side drawing (Cytoscape, Tabulator) is not exercised
    here; that is a browser check."""

    def _client(self):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group
        from django.test import Client

        from tap_grid.grift.importer import grift_import

        with acting_as(get_builtin_actor(BOOTLOADER)):
            assert grift_import(DOC).success
        seed_estate()
        user, _ = get_user_model().objects.get_or_create(username="duo-viewer")
        user.groups.add(Group.objects.get(name="tap_viewer"))
        client = Client()
        client.force_login(user)
        return client

    def test_page_and_fragments_render(self) -> None:
        """req-duo-page-8: /duo renders every slot; the posture strip and tables render the selected account."""
        client = self._client()
        page = client.get("/duo", {"account": "Duo Federal"})
        assert page.status_code == 200
        posture = client.get(f"/panel/{_panel_id('duo-posture')}/", {"account": "Duo Federal"})
        assert posture.status_code == 200
        body = posture.content.decode()
        assert "Duo Federal" in body and "In bypass" in body and "Enrollment not observed" in body
        users = client.get(f"/panel/{_panel_id('duo-users-attention')}/", {"account": "Duo Federal"})
        assert users.status_code == 200
        assert "carol" in users.content.decode() and "mallory" not in users.content.decode()
        graph = client.get(f"/panel/{_panel_id('duo-account-map')}/", {"account": "Duo Federal"})
        assert graph.status_code == 200
        text = graph.content.decode()
        assert "account-map.js" in text and "Okta" in text and "Other VPN" not in text
