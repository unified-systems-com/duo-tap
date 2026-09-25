"""Duo Administrator — A Duo administrator: a separate login to the Admin Panel with a role (Owner, Administrator, Application Manager, User Manager, Security Analyst, Help Desk, Billing, Read-only, or a custom role) and its own authenticators."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoAdministrator(BaseModel):
    """A Duo administrator: a separate login to the Admin Panel with a role (Owner, Administrator, Application Manager, User Manager, Security Analyst, Help Desk, Billing, Read-only, or a custom role) and its own authenticators.

    Spec: specs/spec-duo-v0.md (req-duo-administrator). Domain article: domain/duo_administrator.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_administrator"
    ENTITY_NAME: ClassVar[str] = "Duo Administrator"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "A Duo administrator: a separate login to the Admin Panel with a role (Owner, Administrator, Application Manager, User Manager, Security Analyst, Help Desk, Billing, Read-only, or a custom role) and its own authenticators."
    )
    ENTITY_ICON: ClassVar[str] = "duo-administrator"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "administration"}
    # Duo's administrator id (DE…). Observed only.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("admin_id",)
    # Edge permission (union with the edge definitions' own sources/targets); declared so the
    # containment declaration can name it (req-grid-service-delete-cascade-12).
    OUTBOUND_EDGES: ClassVar[list[dict[str, Any]]] = [
        {"nodes": [{"type": "duo__duo_phone"}], "edges": [{"type": "ENROLLS_PHONE__duo"}]},
        {"nodes": [{"type": "duo__duo_hardware_token"}], "edges": [{"type": "ENROLLS_HARDWARE_TOKEN__duo"}]},
        {"nodes": [{"type": "duo__duo_webauthn_credential"}], "edges": [{"type": "ENROLLS_WEBAUTHN_CREDENTIAL__duo"}]},
        {"nodes": [{"type": "identity_core__human"}], "edges": [{"type": "HELD_BY_HUMAN__identity_core"}]},
    ]
    # What retires with this node (domain article: Identity / Boundaries).
    CONTAINMENT_EDGES: ClassVar[tuple[str, ...]] = ("ENROLLS_WEBAUTHN_CREDENTIAL__duo",)
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "admin_id": {"type": "string", "minLength": 1},
        "name": {"type": "string"},
        "email": {"type": "string"},
        "role": {"type": "string"},
        "status": {"type": "string", "enum": ["", "Active", "Disabled", "Expired", "Pending Activation"]},
        "last_login": {"type": ["string", "null"]},
        "restricted_by_admin_units": {"type": ["boolean", "null"]},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "admin_id": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string"}},
        "email": {"validation": "jsonschema", "schema": {"type": "string"}},
        "role": {"validation": "jsonschema", "schema": {"type": "string"}},
        "status": {
            "validation": "jsonschema",
            "schema": {"type": "string", "enum": ["", "Active", "Disabled", "Expired", "Pending Activation"]},
        },
        "restricted_by_admin_units": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["admin_id"]

    # Duo's administrator id (`DE…`).
    admin_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # The administrator's name.
    name = models.CharField(max_length=255, blank=True, default="")
    # The administrator's email — their Admin Panel login.
    email = models.CharField(max_length=255, blank=True, default="")
    # The administrator's role as reported: `Owner`, `Administrator`, `Application Manager`, `User
    # Manager`, `Security Analyst`, `Help Desk`, `Billing`, `Read-only`, or a custom role's name.
    role = models.CharField(max_length=64, blank=True, default="")
    # As reported: `Active`, `Disabled`, `Expired` (blocked for inactivity), or `Pending Activation`.
    status = models.CharField(max_length=32, blank=True, default="")
    # The administrator's last Admin Panel login.
    last_login = models.DateTimeField(null=True, blank=True)
    # Whether the administrator's reach is limited to administrative units.
    restricted_by_admin_units = models.BooleanField(null=True, blank=True, default=None)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_administrator"

    def get_name(self) -> str:
        return self.name or self.email or self.admin_id or ""

    def __str__(self) -> str:
        return self.get_name()
