"""Duo WebAuthn Credential — A WebAuthn/FIDO2 credential enrolled in Duo — a roaming security key or a platform authenticator (Touch ID, Windows Hello). The phishing-resistant factor."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoWebauthnCredential(BaseModel):
    """A WebAuthn/FIDO2 credential enrolled in Duo — a roaming security key or a platform authenticator (Touch ID, Windows Hello). The phishing-resistant factor.

    Spec: specs/spec-duo-v0.md (req-duo-webauthn-credential). Domain article: domain/duo_webauthn_credential.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_webauthn_credential"
    ENTITY_NAME: ClassVar[str] = "Duo WebAuthn Credential"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "A WebAuthn/FIDO2 credential enrolled in Duo — a roaming security key or a platform authenticator (Touch ID, Windows Hello). The phishing-resistant factor."
    )
    ENTITY_ICON: ClassVar[str] = "duo-webauthn"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "authenticators"}
    # Duo's WebAuthn credential key (WA…). Observed only.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("webauthnkey",)
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "webauthnkey": {"type": "string", "minLength": 1},
        "credential_name": {"type": "string"},
        "label": {"type": "string"},
        "date_added": {"type": ["string", "null"]},
        "date_last_used": {"type": ["string", "null"]},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "webauthnkey": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "credential_name": {"validation": "jsonschema", "schema": {"type": "string"}},
        "label": {"validation": "jsonschema", "schema": {"type": "string"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["webauthnkey"]

    # Duo's credential key (`WA…`).
    webauthnkey = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # The name the user gave the credential (e.g.
    credential_name = models.CharField(max_length=255, blank=True, default="")
    # Duo's kind label, e.g.
    label = models.CharField(max_length=255, blank=True, default="")
    # When the credential was enrolled.
    date_added = models.DateTimeField(null=True, blank=True)
    # When the credential was last used; null if never used or not observed.
    date_last_used = models.DateTimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_webauthn_credential"

    def get_name(self) -> str:
        return self.credential_name or self.label or self.webauthnkey or ""

    def __str__(self) -> str:
        return self.get_name()
