"""Duo Account — A Duo account: one Duo tenant (commercial or Duo Federal) that enrolls users and their authenticators, holds the protected applications and the policies they enforce, and answers second-factor challenges for them."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoAccount(BaseModel):
    """A Duo account: one Duo tenant (commercial or Duo Federal) that enrolls users and their authenticators, holds the protected applications and the policies they enforce, and answers second-factor challenges for them.

    Spec: specs/spec-duo-v0.md (req-duo-account). Domain article: domain/duo_account.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_account"
    ENTITY_NAME: ClassVar[str] = "Duo Account"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "A Duo account: one Duo tenant (commercial or Duo Federal) that enrolls users and their authenticators, holds the protected applications and the policies they enforce, and answers second-factor challenges for them."
    )
    ENTITY_ICON: ClassVar[str] = "duo-account"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so the bundle that seeds a node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # A design-phase node has no observed identifier; its name is the only fact it carries.
    # Revisit when the collector makes api_hostname observable (req-duo-collector).
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("name",)
    # Edge permission (union with the edge definitions' own sources/targets); declared so the
    # containment declaration can name it (req-grid-service-delete-cascade-12).
    OUTBOUND_EDGES: ClassVar[list[dict[str, Any]]] = [
        {
            "nodes": [
                {"type": "duo__duo_user"},
                {"type": "duo__duo_group"},
                {"type": "duo__duo_application"},
                {"type": "duo__duo_policy"},
                {"type": "duo__duo_administrator"},
                {"type": "duo__duo_phone"},
                {"type": "duo__duo_hardware_token"},
                {"type": "duo__duo_endpoint"},
            ],
            "edges": [{"type": "HOLDS_ACCOUNT_OBJECT__duo"}],
        }
    ]
    # What retires with this node (domain article: Identity / Boundaries).
    CONTAINMENT_EDGES: ClassVar[tuple[str, ...]] = ("HOLDS_ACCOUNT_OBJECT__duo",)
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "name": {"type": "string", "minLength": 1},
        "api_hostname": {"type": "string"},
        "edition": {
            "type": "string",
            "enum": ["", "essentials", "advantage", "premier", "federal_mfa", "federal_access", "other"],
        },
        "helpdesk_bypass": {"type": "string", "enum": ["", "allow", "limit", "deny"]},
        "lockout_threshold": {"type": ["integer", "null"]},
        "inactive_user_expiration": {"type": ["integer", "null"]},
        "configuration": {"type": "object"},
        "tags": {"type": "object"},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "api_hostname": {"validation": "jsonschema", "schema": {"type": "string"}},
        "edition": {
            "validation": "jsonschema",
            "schema": {
                "type": "string",
                "enum": ["", "essentials", "advantage", "premier", "federal_mfa", "federal_access", "other"],
            },
        },
        "helpdesk_bypass": {
            "validation": "jsonschema",
            "schema": {"type": "string", "enum": ["", "allow", "limit", "deny"]},
        },
        "lockout_threshold": {"validation": "jsonschema", "schema": {"type": ["integer", "null"]}},
        "inactive_user_expiration": {"validation": "jsonschema", "schema": {"type": ["integer", "null"]}},
        "configuration": {"validation": "jsonschema", "schema": {"type": "object"}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["name"]

    # The account's name as the design or the Admin Panel gives it.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # The account's API hostname — `api-XXXXXXXX.duosecurity.com` for a commercial account, `api-
    # XXXXXXXX.duofederal.com` for Duo Federal.
    api_hostname = models.CharField(max_length=255, blank=True, default="")
    # The Duo edition the account is licensed for: `essentials`, `advantage`, `premier` (commercial),
    # `federal_mfa`, `federal_access` (Duo Federal, the FedRAMP-authorized service), or `other`.
    edition = models.CharField(max_length=32, blank=True, default="")
    # Whether Help Desk administrators may generate bypass codes: `allow` (Duo's default), `limit`, or
    # `deny`.
    helpdesk_bypass = models.CharField(max_length=16, blank=True, default="")
    # Consecutive failed authentications before a user's status becomes `locked out`.
    lockout_threshold = models.IntegerField(null=True, blank=True, default=None)
    # Days of inactivity after which Duo deletes a user, from the account settings.
    inactive_user_expiration = models.IntegerField(null=True, blank=True, default=None)
    # The Admin API account-settings response (`GET /admin/v1/settings`) verbatim, for the settings not
    # promoted to a field above.
    configuration = models.JSONField(default=dict, blank=True)
    # TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_account"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
