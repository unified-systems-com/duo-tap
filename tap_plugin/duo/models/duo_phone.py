"""Duo Phone — A phone enrolled in Duo — a Duo Mobile device that can approve Duo Push, or a number that receives SMS passcodes or phone calls. Its capabilities decide which factors it can deliver."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoPhone(BaseModel):
    """A phone enrolled in Duo — a Duo Mobile device that can approve Duo Push, or a number that receives SMS passcodes or phone calls. Its capabilities decide which factors it can deliver.

    Spec: specs/spec-duo-v0.md (req-duo-phone). Domain article: domain/duo_phone.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_phone"
    ENTITY_NAME: ClassVar[str] = "Duo Phone"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "A phone enrolled in Duo — a Duo Mobile device that can approve Duo Push, or a number that receives SMS passcodes or phone calls. Its capabilities decide which factors it can deliver."
    )
    ENTITY_ICON: ClassVar[str] = "duo-phone"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "authenticators"}
    # Duo's phone id (DP…). Phones are observed, never designed.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("phone_id",)
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "phone_id": {"type": "string", "minLength": 1},
        "name": {"type": "string"},
        "platform": {"type": "string"},
        "phone_type": {"type": "string", "enum": ["", "Mobile", "Landline"]},
        "model": {"type": "string"},
        "capabilities": {"type": ["array", "null"], "items": {"type": "string"}},
        "activated": {"type": ["boolean", "null"]},
        "encrypted": {"type": "string"},
        "fingerprint": {"type": "string"},
        "screenlock": {"type": "string"},
        "tampered": {"type": "string"},
        "last_seen": {"type": ["string", "null"]},
        "tags": {"type": "object"},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "phone_id": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string"}},
        "platform": {"validation": "jsonschema", "schema": {"type": "string"}},
        "phone_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "Mobile", "Landline"]}},
        "model": {"validation": "jsonschema", "schema": {"type": "string"}},
        "capabilities": {
            "validation": "jsonschema",
            "schema": {"type": ["array", "null"], "items": {"type": "string"}},
        },
        "activated": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
        "encrypted": {"validation": "jsonschema", "schema": {"type": "string"}},
        "fingerprint": {"validation": "jsonschema", "schema": {"type": "string"}},
        "screenlock": {"validation": "jsonschema", "schema": {"type": "string"}},
        "tampered": {"validation": "jsonschema", "schema": {"type": "string"}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["phone_id"]

    # Duo's phone id (`DP…`).
    phone_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # The phone's free-form name, if an administrator set one.
    name = models.CharField(max_length=255, blank=True, default="")
    # As reported: e.g.
    platform = models.CharField(max_length=255, blank=True, default="")
    # Duo's `type`: `Mobile` or `Landline`.
    phone_type = models.CharField(max_length=16, blank=True, default="")
    # The device model Duo Mobile reports.
    model = models.CharField(max_length=255, blank=True, default="")
    # What the phone can deliver, as reported: `push`, `sms`, `phone`, `mobile_otp`, `auto`.
    capabilities = models.JSONField(null=True, blank=True, default=None)
    # Whether Duo Mobile is activated on the phone.
    activated = models.BooleanField(null=True, blank=True, default=None)
    # Device encryption as Duo Mobile reports it (e.g.
    encrypted = models.CharField(max_length=255, blank=True, default="")
    # Biometric configuration as Duo Mobile reports it (e.g.
    fingerprint = models.CharField(max_length=255, blank=True, default="")
    # Screen lock as Duo Mobile reports it (e.g.
    screenlock = models.CharField(max_length=255, blank=True, default="")
    # Jailbreak/root detection as Duo Mobile reports it (e.g.
    tampered = models.CharField(max_length=255, blank=True, default="")
    # When Duo last saw the phone.
    last_seen = models.DateTimeField(null=True, blank=True)
    # TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_phone"

    def get_name(self) -> str:
        return self.name or self.model or self.phone_id or ""

    def __str__(self) -> str:
        return self.get_name()
