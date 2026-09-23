"""A small Duo estate written through the service layer, for the corpus and page-search tests.

Two accounts, so every account-scoped search can be shown not to leak across accounts:

- ``Duo Federal`` (the one the page tests scope to): an Okta application under a custom policy,
  an Admin API application with no policy of its own (it inherits the Global Policy), a group
  policy, users in each status the page cares about, every authenticator kind, a bypass code,
  an administrator and an endpoint.
- ``Other`` holds one application, one user in bypass and one phone, and must never appear in a
  ``Duo Federal``-scoped result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tap_grid.services import WriteOperation, create_node, write_batch


@dataclass
class Estate:
    ids: dict[str, str] = field(default_factory=dict)

    def __getitem__(self, key: str) -> str:
        return self.ids[key]


def _node(estate: Estate, key: str, type_slug: str, payload: dict[str, Any]) -> str:
    result = create_node(f"duo__{type_slug}", payload)
    assert result.success, (key, result)
    estate.ids[key] = str(result.entity_id)
    return estate.ids[key]


def _edges(estate: Estate, triples: list[tuple[str, str, str, dict[str, Any] | None]]) -> None:
    ops = [
        WriteOperation(
            verb="create_edge",
            from_target=estate[src],
            to_target=estate[dst],
            edge_type=f"{edge}__duo",
            payload={"properties": props} if props else {},
        )
        for src, edge, dst, props in triples
    ]
    batch = write_batch(ops)
    assert batch.success, [r for r in batch.results if not r.success]


def seed_estate() -> Estate:
    e = Estate()
    _node(e, "acct", "duo_account", {"name": "Duo Federal", "edition": "federal_mfa", "helpdesk_bypass": "deny"})
    _node(e, "other", "duo_account", {"name": "Other"})

    _node(
        e,
        "okta_app",
        "duo_application",
        {"name": "Okta", "integration_type": "okta", "user_access": "PERMITTED_GROUPS"},
    )
    _node(
        e,
        "admin_api",
        "duo_application",
        {
            "name": "TAP collector",
            "integration_type": "adminapi",
            "user_access": "NO_USERS",
            "adminapi_permissions": ["adminapi_read_resource", "adminapi_read_log"],
        },
    )
    _node(e, "global", "duo_policy", {"name": "Global Policy", "is_global": True, "new_user_behavior": "deny"})
    _node(
        e,
        "okta_policy",
        "duo_policy",
        {
            "name": "Okta — phishing resistant",
            "is_global": False,
            "new_user_behavior": "deny",
            "allowed_auth_methods": ["webauthn-roaming", "webauthn-platform", "duo-push"],
        },
    )
    _node(e, "contractor_policy", "duo_policy", {"name": "Contractors", "is_global": False})
    _node(e, "engineers", "duo_group", {"name": "engineers", "status": "Active"})
    _node(e, "contractors", "duo_group", {"name": "contractors", "status": "Active"})

    _node(
        e,
        "alice",
        "duo_user",
        {"user_id": "DUALICE0000000000001", "username": "alice", "status": "active", "is_enrolled": True},
    )
    _node(
        e,
        "bob",
        "duo_user",
        {"user_id": "DUBOB000000000000002", "username": "bob", "status": "bypass", "is_enrolled": True},
    )
    _node(
        e,
        "carol",
        "duo_user",
        {"user_id": "DUCAROL0000000000003", "username": "carol", "status": "active", "is_enrolled": False},
    )
    _node(
        e,
        "dave",
        "duo_user",
        {"user_id": "DUDAVE00000000000004", "username": "dave", "status": "locked out", "is_enrolled": True},
    )
    _node(
        e, "erin", "duo_user", {"user_id": "DUERIN00000000000005", "username": "erin", "status": "active"}
    )  # is_enrolled not observed

    _node(
        e,
        "alice_phone",
        "duo_phone",
        {
            "phone_id": "DPALICE0000000000001",
            "platform": "Apple iOS",
            "phone_type": "Mobile",
            "capabilities": ["auto", "push", "sms", "phone", "mobile_otp"],
        },
    )
    _node(
        e,
        "dave_phone",
        "duo_phone",
        {"phone_id": "DPDAVE00000000000002", "phone_type": "Mobile", "capabilities": ["sms", "phone"]},
    )
    _node(
        e, "token", "duo_hardware_token", {"token_id": "DHTOKEN0000000000001", "serial": "123456", "token_type": "d1"}
    )
    _node(
        e,
        "alice_key",
        "duo_webauthn_credential",
        {"webauthnkey": "WAALICE0000000000001", "credential_name": "YubiKey 5C", "label": "Security Key"},
    )
    _node(e, "admin_key", "duo_webauthn_credential", {"webauthnkey": "WAADMIN0000000000001", "label": "Touch ID"})
    _node(
        e,
        "bob_code",
        "duo_bypass_code",
        {"bypass_code_id": "DBBOB000000000000001", "reuse_count": 1, "admin_email": "helpdesk@example.com"},
    )
    _node(
        e,
        "owner",
        "duo_administrator",
        {"admin_id": "DEOWNER0000000000001", "name": "Owner One", "role": "Owner", "status": "Active"},
    )
    _node(
        e,
        "laptop",
        "duo_endpoint",
        {"epkey": "EPLAPTOP000000000001", "device_name": "alice-mbp", "trusted_endpoint": True},
    )

    _node(e, "other_app", "duo_application", {"name": "Other VPN", "integration_type": "radius"})
    _node(e, "other_user", "duo_user", {"user_id": "DUOTHER0000000000001", "username": "mallory", "status": "bypass"})
    _node(e, "other_phone", "duo_phone", {"phone_id": "DPOTHER0000000000001", "capabilities": ["sms"]})

    held = [
        "okta_app",
        "admin_api",
        "global",
        "okta_policy",
        "contractor_policy",
        "engineers",
        "contractors",
        "alice",
        "bob",
        "carol",
        "dave",
        "erin",
        "alice_phone",
        "dave_phone",
        "token",
        "owner",
        "laptop",
    ]
    _edges(e, [("acct", "HOLDS_ACCOUNT_OBJECT", h, None) for h in held])
    _edges(e, [("other", "HOLDS_ACCOUNT_OBJECT", h, None) for h in ["other_app", "other_user", "other_phone"]])
    _edges(
        e,
        [
            ("okta_app", "ENFORCES_POLICY", "okta_policy", {"apply_type": "app"}),
            (
                "okta_app",
                "ENFORCES_POLICY",
                "contractor_policy",
                {"apply_type": "group_app", "group_names": ["contractors"], "group_position": 0},
            ),
            ("okta_app", "PERMITS_GROUP", "engineers", None),
            ("okta_app", "PERMITS_GROUP", "contractors", None),
            ("alice", "MEMBER_OF_GROUP", "engineers", None),
            ("carol", "MEMBER_OF_GROUP", "contractors", None),
            ("alice", "ENROLLS_PHONE", "alice_phone", None),
            ("dave", "ENROLLS_PHONE", "dave_phone", None),
            ("owner", "ENROLLS_HARDWARE_TOKEN", "token", None),
            ("alice", "ENROLLS_WEBAUTHN_CREDENTIAL", "alice_key", None),
            ("owner", "ENROLLS_WEBAUTHN_CREDENTIAL", "admin_key", None),
            ("bob", "HOLDS_BYPASS_CODE", "bob_code", None),
            ("alice", "AUTHENTICATES_FROM_ENDPOINT", "laptop", None),
        ],
    )
    return e
