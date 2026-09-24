"""Duo User — A person's account in Duo: the identity that enrolls authenticators and is challenged for a second factor. Carries Duo's status (active, bypass, disabled, locked out) and whether any authenticator is enrolled."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoUser(BaseModel):
    """A person's account in Duo: the identity that enrolls authenticators and is challenged for a second factor. Carries Duo's status (active, bypass, disabled, locked out) and whether any authenticator is enrolled.

    Spec: specs/spec-duo-v0.md (req-duo-user). Domain article: domain/duo_user.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_user"
    ENTITY_NAME: ClassVar[str] = "Duo User"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "A person's account in Duo: the identity that enrolls authenticators and is challenged for a second factor. Carries Duo's status (active, bypass, disabled, locked out) and whether any authenticator is enrolled."
    )
    ENTITY_ICON: ClassVar[str] = "duo-user"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "directory"}
    # Duo's own user id (DU…), stable across renames and unique across Duo. An observed user has it at
    # creation; a design that seeds a user supplies a placeholder that cannot be mistaken for Duo's.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("user_id",)
    # Edge permission (union with the edge definitions' own sources/targets); declared so the
    # containment declaration can name it (req-grid-service-delete-cascade-12).
    OUTBOUND_EDGES: ClassVar[list[dict[str, Any]]] = [
        {"nodes": [{"type": "duo__duo_group"}], "edges": [{"type": "MEMBER_OF_GROUP__duo"}]},
        {"nodes": [{"type": "duo__duo_phone"}], "edges": [{"type": "ENROLLS_PHONE__duo"}]},
        {"nodes": [{"type": "duo__duo_hardware_token"}], "edges": [{"type": "ENROLLS_HARDWARE_TOKEN__duo"}]},
        {"nodes": [{"type": "duo__duo_webauthn_credential"}], "edges": [{"type": "ENROLLS_WEBAUTHN_CREDENTIAL__duo"}]},
        {"nodes": [{"type": "duo__duo_bypass_code"}], "edges": [{"type": "HOLDS_BYPASS_CODE__duo"}]},
        {"nodes": [{"type": "duo__duo_endpoint"}], "edges": [{"type": "AUTHENTICATES_FROM_ENDPOINT__duo"}]},
        {"nodes": [{"type": "identity_core__human"}], "edges": [{"type": "HELD_BY_HUMAN__identity_core"}]},
    ]
    # What retires with this node (domain article: Identity / Boundaries).
    CONTAINMENT_EDGES: ClassVar[tuple[str, ...]] = ("ENROLLS_WEBAUTHN_CREDENTIAL__duo", "HOLDS_BYPASS_CODE__duo")
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "user_id": {"type": "string", "minLength": 1},
        "username": {"type": "string"},
        "realname": {"type": "string"},
        "email": {"type": "string"},
        "status": {"type": "string", "enum": ["", "active", "bypass", "disabled", "locked out", "pending deletion"]},
        "is_enrolled": {"type": ["boolean", "null"]},
        "last_login": {"type": ["string", "null"]},
        "last_directory_sync": {"type": ["string", "null"]},
        "created": {"type": ["string", "null"]},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "user_id": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "username": {"validation": "jsonschema", "schema": {"type": "string"}},
        "realname": {"validation": "jsonschema", "schema": {"type": "string"}},
        "email": {"validation": "jsonschema", "schema": {"type": "string"}},
        "status": {
            "validation": "jsonschema",
            "schema": {
                "type": "string",
                "enum": ["", "active", "bypass", "disabled", "locked out", "pending deletion"],
            },
        },
        "is_enrolled": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["user_id"]

    # Duo's user id (`DU…`, 20 characters).
    user_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # The username Duo matches at primary authentication.
    username = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # The user's full name as Duo holds it.
    realname = models.CharField(max_length=255, blank=True, default="")
    # The user's email as Duo holds it.
    email = models.CharField(max_length=255, blank=True, default="")
    # Duo's user status, as reported: `active` (must complete MFA), `bypass` (skips MFA), `disabled`,
    # `locked out`, or `pending deletion`.
    status = models.CharField(max_length=32, blank=True, default="")
    # Whether the user has at least one authenticator enrolled (Duo's `is_enrolled`).
    is_enrolled = models.BooleanField(null=True, blank=True, default=None)
    # Duo's last successful login for the user.
    last_login = models.DateTimeField(null=True, blank=True)
    # When a directory sync last updated the user; null for a user managed by hand in Duo, or not
    # observed.
    last_directory_sync = models.DateTimeField(null=True, blank=True)
    # When the user was created in Duo.
    created = models.DateTimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_user"

    def get_name(self) -> str:
        return self.username or self.user_id or ""

    def __str__(self) -> str:
        return self.get_name()
