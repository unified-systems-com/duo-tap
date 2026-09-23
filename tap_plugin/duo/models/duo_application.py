"""Duo Application — A protected application in Duo (an Admin API 'integration'): the Okta authenticator, a Duo SSO SAML/OIDC app, an RDP or Unix host, an Auth Proxy, or an Admin API application that can read or change Duo itself."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoApplication(BaseModel):
    """A protected application in Duo (an Admin API 'integration'): the Okta authenticator, a Duo SSO SAML/OIDC app, an RDP or Unix host, an Auth Proxy, or an Admin API application that can read or change Duo itself.

    Spec: specs/spec-duo-v0.md (req-duo-application). Domain article: domain/duo_application.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_application"
    ENTITY_NAME: ClassVar[str] = "Duo Application"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "A protected application in Duo (an Admin API 'integration'): the Okta authenticator, a Duo SSO SAML/OIDC app, an RDP or Unix host, an Auth Proxy, or an Admin API application that can read or change Duo itself."
    )
    ENTITY_ICON: ClassVar[str] = "duo-application"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "access"}
    # A design names the application before it exists; integration_key (DI…) is the stable id and
    # the key moves to it when req-duo-collector makes it observable.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("name",)
    # Edge permission (union with the edge definitions' own sources/targets); declared so the
    # containment declaration can name it (req-grid-service-delete-cascade-12).
    OUTBOUND_EDGES: ClassVar[list[dict[str, Any]]] = [
        {"nodes": [{"type": "duo__duo_group"}], "edges": [{"type": "PERMITS_GROUP__duo"}]},
        {"nodes": [{"type": "duo__duo_policy"}], "edges": [{"type": "ENFORCES_POLICY__duo"}]},
    ]
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "name": {"type": "string", "minLength": 1},
        "integration_key": {"type": "string"},
        "integration_type": {"type": "string"},
        "user_access": {"type": "string", "enum": ["", "ALL_USERS", "NO_USERS", "PERMITTED_GROUPS"]},
        "adminapi_permissions": {"type": ["array", "null"], "items": {"type": "string"}},
        "self_service_allowed": {"type": ["boolean", "null"]},
        "tags": {"type": "object"},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "integration_key": {"validation": "jsonschema", "schema": {"type": "string"}},
        "integration_type": {"validation": "jsonschema", "schema": {"type": "string"}},
        "user_access": {
            "validation": "jsonschema",
            "schema": {"type": "string", "enum": ["", "ALL_USERS", "NO_USERS", "PERMITTED_GROUPS"]},
        },
        "adminapi_permissions": {
            "validation": "jsonschema",
            "schema": {"type": ["array", "null"], "items": {"type": "string"}},
        },
        "self_service_allowed": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["name"]

    # The application's name in Duo.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # The integration key (`DI…`), Duo's stable id for the application.
    integration_key = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # Duo's integration type string, as reported: e.g.
    integration_type = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # Who may authenticate: `ALL_USERS`, `NO_USERS`, or `PERMITTED_GROUPS` (only members of the groups on
    # `PERMITS_GROUP`).
    user_access = models.CharField(max_length=32, blank=True, default="")
    # For an `adminapi` application only: the permissions granted, by Duo's flag name (e.g.
    adminapi_permissions = models.JSONField(null=True, blank=True, default=None)
    # Whether users may manage their own devices through the self-service portal from this application.
    self_service_allowed = models.BooleanField(null=True, blank=True, default=None)
    # TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_application"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
