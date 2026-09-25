"""Duo Hardware Token — An OTP hardware token registered in Duo (HOTP-6, HOTP-8, YubiKey AES, or Duo-D100) and assigned to users or administrators."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoHardwareToken(BaseModel):
    """An OTP hardware token registered in Duo (HOTP-6, HOTP-8, YubiKey AES, or Duo-D100) and assigned to users or administrators.

    Spec: specs/spec-duo-v0.md (req-duo-hardware-token). Domain article: domain/duo_hardware_token.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_hardware_token"
    ENTITY_NAME: ClassVar[str] = "Duo Hardware Token"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "An OTP hardware token registered in Duo (HOTP-6, HOTP-8, YubiKey AES, or Duo-D100) and assigned to users or administrators."
    )
    ENTITY_ICON: ClassVar[str] = "duo-hardware-token"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "authenticators"}
    # Duo's token id (DH…). Tokens are observed, never designed.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("token_id",)
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "token_id": {"type": "string", "minLength": 1},
        "serial": {"type": "string"},
        "token_type": {"type": "string", "enum": ["", "h6", "h8", "yk", "d1"]},
        "totp_step": {"type": ["integer", "null"]},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "token_id": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "serial": {"validation": "jsonschema", "schema": {"type": "string"}},
        "token_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "h6", "h8", "yk", "d1"]}},
        "totp_step": {"validation": "jsonschema", "schema": {"type": ["integer", "null"]}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["token_id"]

    # Duo's token id (`DH…`).
    token_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # The token's serial number.
    serial = models.CharField(max_length=255, blank=True, default="")
    # Duo's `type`: `h6` (HOTP-6), `h8` (HOTP-8), `yk` (YubiKey AES), `d1` (Duo-D100).
    token_type = models.CharField(max_length=8, blank=True, default="")
    # The TOTP time step in seconds, for time-based tokens; null for counter-based or not observed.
    totp_step = models.IntegerField(null=True, blank=True, default=None)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_hardware_token"

    def get_name(self) -> str:
        return (f"{self.token_type} {self.serial}".strip() if self.serial else self.token_id) or ""

    def __str__(self) -> str:
        return self.get_name()
