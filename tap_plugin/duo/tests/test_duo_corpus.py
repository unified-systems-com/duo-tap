"""Behaviour tests for the Duo corpus: every model (req-duo-account … req-duo-endpoint) and edge (req-duo-edges)."""

from __future__ import annotations

import pytest
from tap_plugin.duo import models as duo_models
from tap_plugin.duo.tests.seed import seed_estate

from tap_grid.models import Edge, Entity
from tap_grid.services import WriteOperation, create_node, delete_node, write_batch

#: (entity type, minimal create payload, the field CREATE_REQUIRED names)
MINIMAL = [
    ("duo__duo_account", {"name": "acct"}, "name"),
    ("duo__duo_user", {"user_id": "DU1"}, "user_id"),
    ("duo__duo_group", {"account_name": "acct", "name": "grp"}, "name"),
    ("duo__duo_phone", {"phone_id": "DP1"}, "phone_id"),
    ("duo__duo_hardware_token", {"token_id": "DH1"}, "token_id"),
    ("duo__duo_webauthn_credential", {"webauthnkey": "WA1"}, "webauthnkey"),
    ("duo__duo_bypass_code", {"bypass_code_id": "DB1"}, "bypass_code_id"),
    ("duo__duo_application", {"account_name": "acct", "name": "app"}, "name"),
    ("duo__duo_policy", {"account_name": "acct", "name": "pol"}, "name"),
    ("duo__duo_administrator", {"admin_id": "DE1"}, "admin_id"),
    ("duo__duo_endpoint", {"epkey": "EP1"}, "epkey"),
]
SURFACE = {
    "duo__duo_account": None,
    "duo__duo_user": "directory",
    "duo__duo_group": "directory",
    "duo__duo_phone": "authenticators",
    "duo__duo_hardware_token": "authenticators",
    "duo__duo_webauthn_credential": "authenticators",
    "duo__duo_bypass_code": "authenticators",
    "duo__duo_application": "access",
    "duo__duo_policy": "access",
    "duo__duo_administrator": "administration",
    "duo__duo_endpoint": "device_trust",
}


def _model(type_slug: str):
    return next(m for m in (getattr(duo_models, n) for n in duo_models.__all__) if m.ENTITY_TYPE == type_slug)


@pytest.mark.django_db
@pytest.mark.parametrize(("type_slug", "payload", "required"), MINIMAL)
class TestModels:
    def test_created_with_only_its_required_field(self, type_slug, payload, required) -> None:
        """The minimal create succeeds; every other field stays blank (not observed).

        req-duo-account-1, req-duo-user-1, req-duo-group-1, req-duo-phone-1, req-duo-hardware-token-1, req-duo-webauthn-credential-1, req-duo-bypass-code-1, req-duo-application-1, req-duo-policy-1, req-duo-administrator-1, req-duo-endpoint-1
        """
        result = create_node(type_slug, payload)
        assert result.success, result
        row = _model(type_slug).all_objects.get(entity_id=result.entity_id)
        assert getattr(row, required) == payload[required]
        assert Entity.objects.get(id=result.entity_id).name == payload[required]

    def test_required_field_enforced(self, type_slug, payload, required) -> None:
        """A create without the key field is refused.

        req-duo-account-2, req-duo-user-2, req-duo-group-2, req-duo-phone-2, req-duo-hardware-token-2, req-duo-webauthn-credential-2, req-duo-bypass-code-2, req-duo-application-2, req-duo-policy-2, req-duo-administrator-2, req-duo-endpoint-2
        """
        result = create_node(type_slug, {})
        assert not result.success

    def test_surface_dimension(self, type_slug, payload, required) -> None:
        """The type stamps its duo.surface (none on the account, and never dcom).

        req-duo-account-3, req-duo-user-3, req-duo-group-3, req-duo-phone-3, req-duo-hardware-token-3, req-duo-webauthn-credential-3, req-duo-bypass-code-3, req-duo-application-3, req-duo-policy-3, req-duo-administrator-3, req-duo-endpoint-3
        """
        result = create_node(type_slug, payload)
        dims = Entity.objects.get(id=result.entity_id).dimensions
        assert dims.get("duo.surface") == SURFACE[type_slug]
        assert "dcom" not in dims


def test_every_key_is_a_field() -> None:
    """Every natural key rests on fields the model carries.

    req-duo-account-4, req-duo-user-4, req-duo-group-4, req-duo-phone-4, req-duo-hardware-token-4, req-duo-webauthn-credential-4, req-duo-bypass-code-4, req-duo-application-4, req-duo-policy-4, req-duo-administrator-4, req-duo-endpoint-4
    """
    for name in duo_models.__all__:
        model = getattr(duo_models, name)
        fields = {f.name for f in model._meta.get_fields()}
        assert model.NATURAL_KEY and all(k in fields for k in model.NATURAL_KEY), name


@pytest.mark.django_db
class TestFieldVocabulary:
    def test_user_status_is_closed(self) -> None:
        """req-duo-user-5: a status outside Duo's vocabulary is refused; blank (not observed) is allowed."""
        assert create_node("duo__duo_user", {"user_id": "DU2", "status": ""}).success
        assert not create_node("duo__duo_user", {"user_id": "DU3", "status": "enabled"}).success

    def test_account_edition_is_closed(self) -> None:
        """req-duo-account-5: edition is one of Duo's editions, or blank."""
        assert create_node("duo__duo_account", {"name": "a1", "edition": "federal_mfa"}).success
        assert not create_node("duo__duo_account", {"name": "a2", "edition": "gold"}).success

    def test_policy_new_user_behavior_is_closed(self) -> None:
        """req-duo-policy-5: new_user_behavior is enroll / no-mfa / deny, or blank."""
        assert create_node("duo__duo_policy", {"account_name": "acct", "name": "p1", "new_user_behavior": "no-mfa"}).success
        assert not create_node("duo__duo_policy", {"account_name": "acct", "name": "p2", "new_user_behavior": "allow"}).success

    def test_enrollment_null_is_not_false(self) -> None:
        """req-duo-user-6: is_enrolled defaults to null (not observed), never false."""
        result = create_node("duo__duo_user", {"user_id": "DU4"})
        assert _model("duo__duo_user").all_objects.get(entity_id=result.entity_id).is_enrolled is None


def _edge(src: str, dst: str, edge_type: str, props: dict | None = None):
    return write_batch(
        [
            WriteOperation(
                verb="create_edge",
                from_target=src,
                to_target=dst,
                edge_type=edge_type,
                payload={"properties": props} if props else {},
            )
        ]
    )


@pytest.mark.django_db
class TestEdges:
    def test_estate_seeds(self) -> None:
        """req-duo-edges-1: every edge type is accepted between its declared endpoints (the seed writes each)."""
        estate = seed_estate()
        assert Edge.objects.filter(from_entity_id=estate["acct"], edge_type="HOLDS_ACCOUNT_OBJECT__duo").count() == 17

    def test_undeclared_source_refused(self) -> None:
        """req-duo-edges-2: a type that declares its outbound edges cannot emit one it does not declare
        and whose definition does not name it as a source (only an application PERMITS_GROUP).

        Endpoint lists are enforced under the grid's permission union: a node type that declares no
        OUTBOUND_EDGES / INBOUND_EDGES is unconstrained on that side, so the refusal is proven from a
        type that declares them."""
        user = create_node("duo__duo_user", {"user_id": "DU9"}).entity_id
        group = create_node("duo__duo_group", {"account_name": "acct", "name": "g9"}).entity_id
        assert not _edge(user, group, "PERMITS_GROUP__duo").success
        assert _edge(user, group, "MEMBER_OF_GROUP__duo").success

    def test_enforces_policy_needs_apply_type(self) -> None:
        """req-duo-edges-3: ENFORCES_POLICY carries apply_type; unknown properties are refused."""
        app = create_node("duo__duo_application", {"account_name": "acct", "name": "a9"}).entity_id
        pol = create_node("duo__duo_policy", {"account_name": "acct", "name": "p9"}).entity_id
        assert not _edge(app, pol, "ENFORCES_POLICY__duo").success
        assert not _edge(app, pol, "ENFORCES_POLICY__duo", {"apply_type": "app", "colour": "green"}).success
        assert _edge(app, pol, "ENFORCES_POLICY__duo", {"apply_type": "app"}).success

    def test_requests_second_factor_open_source(self) -> None:
        """req-duo-edges-4: any node may request a second factor of a Duo application; fail_mode is closed."""
        app = create_node("duo__duo_application", {"account_name": "acct", "name": "okta", "integration_type": "okta"}).entity_id
        protected = create_node("duo__duo_endpoint", {"epkey": "EPX"}).entity_id  # any type stands in for a foreign one
        assert not _edge(protected, app, "REQUESTS_SECOND_FACTOR__duo", {"fail_mode": "open"}).success
        assert _edge(
            protected, app, "REQUESTS_SECOND_FACTOR__duo", {"mechanism": "universal_prompt", "fail_mode": "secure"}
        ).success

    def test_issues_sso_assertion_open_target(self) -> None:
        """req-duo-edges-5: a Duo SSO application may assert to any node; protocol is required."""
        app = create_node("duo__duo_application", {"account_name": "acct", "name": "sso", "integration_type": "sso-generic"}).entity_id
        sp = create_node("duo__duo_group", {"account_name": "acct", "name": "stand-in"}).entity_id
        assert not _edge(app, sp, "ISSUES_SSO_ASSERTION__duo").success
        assert _edge(app, sp, "ISSUES_SSO_ASSERTION__duo", {"protocol": "saml"}).success

    def test_surface_on_edges(self) -> None:
        """req-duo-edges-6: edges stamp their duo.surface; tenancy spans every surface and stamps none."""
        estate = seed_estate()
        member = Edge.objects.get(from_entity_id=estate["alice"], edge_type="MEMBER_OF_GROUP__duo")
        assert member.entity.dimensions.get("duo.surface") == "directory"
        tenancy = Edge.objects.filter(edge_type="HOLDS_ACCOUNT_OBJECT__duo").first()
        assert "duo.surface" not in tenancy.entity.dimensions


@pytest.mark.django_db
class TestContainment:
    def test_account_cascade_retires_its_tree(self) -> None:
        """req-duo-account-6: deleting an account (contained) retires what it holds and, through the
        user, the user's WebAuthn credentials and bypass codes; the other account is untouched."""
        e = seed_estate()
        result = delete_node(e["acct"], cascade="contained")
        assert result.success, result
        live = set(Entity.objects.filter(deleted_at__isnull=True).values_list("id", flat=True))
        for key in (
            "okta_app",
            "global",
            "alice",
            "bob",
            "alice_phone",
            "owner",
            "laptop",
            "alice_key",
            "admin_key",
            "bob_code",
        ):
            assert e[key] not in {str(x) for x in live}, key
        for key in ("other", "other_app", "other_user", "other_phone"):
            assert e[key] in {str(x) for x in live}, key

    def test_shared_phone_survives_its_user(self) -> None:
        """req-duo-phone-5: a phone is a reference from a user, not contained — deleting the user leaves it."""
        e = seed_estate()
        assert delete_node(e["alice"], cascade="contained").success
        live = {str(x) for x in Entity.objects.filter(deleted_at__isnull=True).values_list("id", flat=True)}
        assert e["alice_phone"] in live
        assert e["alice_key"] not in live


@pytest.mark.django_db
def test_same_name_in_two_accounts_stays_two_objects() -> None:
    """req-duo-group-5: name-keyed design types do not merge across accounts — two accounts each
    holding a group named "engineers" hold two entities, and retiring one account leaves the
    other's group live. (The natural key is not consulted on the write path today,
    req-grid-entity-natural-key-9; the key moves to Duo's own ids with req-duo-collector.)"""
    a = create_node("duo__duo_account", {"name": "one"}).entity_id
    b = create_node("duo__duo_account", {"name": "two"}).entity_id
    ga = create_node("duo__duo_group", {"account_name": "one", "name": "engineers"}).entity_id
    gb = create_node("duo__duo_group", {"account_name": "two", "name": "engineers"}).entity_id
    assert ga != gb
    assert _edge(a, ga, "HOLDS_ACCOUNT_OBJECT__duo").success
    assert _edge(b, gb, "HOLDS_ACCOUNT_OBJECT__duo").success
    assert delete_node(a, cascade="contained").success
    live = {str(x) for x in Entity.objects.filter(deleted_at__isnull=True).values_list("id", flat=True)}
    assert str(gb) in live and str(ga) not in live


#: The name-keyed Duo types: names are unique only within an account, so each carries its account.
SCOPED = ("duo__duo_application", "duo__duo_group", "duo__duo_policy")


@pytest.mark.parametrize("type_slug", SCOPED)
def test_name_keyed_types_are_scoped_by_account(type_slug) -> None:
    """req-duo-application-4, req-duo-group-4, req-duo-policy-4: the key is (account_name, name), so
    every account's "Global Policy" is its own object."""
    assert _model(type_slug).NATURAL_KEY == ("account_name", "name")


@pytest.mark.django_db
@pytest.mark.parametrize("type_slug", SCOPED)
def test_name_keyed_types_refuse_a_missing_account(type_slug) -> None:
    """req-duo-application-2, req-duo-group-2, req-duo-policy-2: a create without its account is
    refused, because without the account the key cannot tell two accounts' objects apart."""
    assert not create_node(type_slug, {"name": "Global Policy"}).success
    assert create_node(type_slug, {"account_name": "one", "name": "Global Policy"}).success


@pytest.mark.django_db
def test_backfill_takes_the_holding_accounts_name() -> None:
    """Migration 0005: an object written before account_name existed takes the name of the one
    live account holding it; an object held by two accounts is left empty rather than guessed."""
    import importlib

    from django.apps import apps as django_apps

    backfill = importlib.import_module("tap_plugin.duo.migrations.0005_backfill_account_name").backfill_account_name
    one = create_node("duo__duo_account", {"name": "one"}).entity_id
    two = create_node("duo__duo_account", {"name": "two"}).entity_id
    held = create_node("duo__duo_policy", {"account_name": "x", "name": "Global Policy"}).entity_id
    shared = create_node("duo__duo_group", {"account_name": "x", "name": "everyone"}).entity_id
    assert _edge(one, held, "HOLDS_ACCOUNT_OBJECT__duo").success
    assert _edge(one, shared, "HOLDS_ACCOUNT_OBJECT__duo").success
    assert _edge(two, shared, "HOLDS_ACCOUNT_OBJECT__duo").success
    policy, group = _model("duo__duo_policy"), _model("duo__duo_group")
    policy.all_objects.filter(entity_id=held).update(account_name="")  # as written before 0004
    group.all_objects.filter(entity_id=shared).update(account_name="")
    backfill(django_apps, None)
    assert policy.all_objects.get(entity_id=held).account_name == "one"
    assert group.all_objects.get(entity_id=shared).account_name == ""
