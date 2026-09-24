"""Duo Policy — A Duo policy: the Global Policy every application inherits, or a custom policy applied to applications or to groups within them — allowed authentication methods, new-user behaviour, remembered devices, device health, networks and location."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoPolicy(BaseModel):
    """A Duo policy: the Global Policy every application inherits, or a custom policy applied to applications or to groups within them — allowed authentication methods, new-user behaviour, remembered devices, device health, networks and location.

    Spec: specs/spec-duo-v0.md (req-duo-policy). Domain article: domain/duo_policy.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_policy"
    ENTITY_NAME: ClassVar[str] = "Duo Policy"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "A Duo policy: the Global Policy every application inherits, or a custom policy applied to applications or to groups within them — allowed authentication methods, new-user behaviour, remembered devices, device health, networks and location."
    )
    ENTITY_ICON: ClassVar[str] = "duo-policy"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "access"}
    # Names are unique only within an account, so the key is (account_name, name). A design names
    # the policy before it exists; policy_key (PO…) is the stable id and the key moves to
    # (account_name, that id) when req-duo-collector makes it observable.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("account_name", "name")
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "account_name": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "policy_key": {"type": "string"},
        "is_global": {"type": ["boolean", "null"]},
        "new_user_behavior": {"type": "string", "enum": ["", "enroll", "no-mfa", "deny"]},
        "allowed_auth_methods": {"type": ["array", "null"], "items": {"type": "string"}},
        "sections": {"type": "object"},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "account_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "policy_key": {"validation": "jsonschema", "schema": {"type": "string"}},
        "is_global": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
        "new_user_behavior": {
            "validation": "jsonschema",
            "schema": {"type": "string", "enum": ["", "enroll", "no-mfa", "deny"]},
        },
        "allowed_auth_methods": {
            "validation": "jsonschema",
            "schema": {"type": ["array", "null"], "items": {"type": "string"}},
        },
        "sections": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["account_name", "name"]

    #: The name of the Duo account this object lives in: the duo__duo_account's natural key. A
    #: scoping column, not a copy of the account: the account's own facts live on the account, and
    #: HOLDS_ACCOUNT_OBJECT__duo is what a traversal follows. It is here because two accounts can
    #: each hold an object with the same name (every account has a "Global Policy"), and the key
    #: must tell them apart, so the fact the key rests on is a column.
    account_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # The policy's name (`policy_name`).
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # Duo's policy key (`PO…`).
    policy_key = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # True for the account's Global Policy, which every application inherits section by section unless an
    # application or group policy overrides it.
    is_global = models.BooleanField(null=True, blank=True, default=None)
    # The New User Policy: what happens to an unenrolled user after primary authentication — `enroll`
    # (Duo's default), `no-mfa` (let them in without MFA), or `deny`.
    new_user_behavior = models.CharField(max_length=16, blank=True, default="")
    # The Authentication Methods section's allowed list, as Duo names methods: `duo-push`, `duo-passcode`,
    # `webauthn-roaming`, `webauthn-platform`, `hardware-token`, `sms`, `phonecall`, `smart-card` (Duo
    # Federal only), `bypass`, and the passwordless `-pwl` variants.
    allowed_auth_methods = models.JSONField(null=True, blank=True, default=None)
    # The policy's section data from the Policies API v2 verbatim (`authentication_methods`, `new_user`,
    # `remembered_devices`, `duo_desktop`, `trusted_endpoints`, `authorized_networks`, `user_location`,
    # `screen_lock`, `operating_systems`, `browsers`, …).
    sections = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_policy"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
