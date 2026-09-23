"""Duo Endpoint — A device Duo has seen users authenticate from — laptop, desktop or mobile browser — with the posture Duo Desktop reports (disk encryption, firewall, password, OS) and whether it is a Trusted Endpoint."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoEndpoint(BaseModel):
    """A device Duo has seen users authenticate from — laptop, desktop or mobile browser — with the posture Duo Desktop reports (disk encryption, firewall, password, OS) and whether it is a Trusted Endpoint.

    Spec: specs/spec-duo-v0.md (req-duo-endpoint). Domain article: domain/duo_endpoint.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_endpoint"
    ENTITY_NAME: ClassVar[str] = "Duo Endpoint"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "A device Duo has seen users authenticate from — laptop, desktop or mobile browser — with the posture Duo Desktop reports (disk encryption, firewall, password, OS) and whether it is a Trusted Endpoint."
    )
    ENTITY_ICON: ClassVar[str] = "duo-endpoint"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "device_trust"}
    # Duo's endpoint key. Observed only; see the article for what an epkey means without Duo Desktop.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("epkey",)
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "epkey": {"type": "string", "minLength": 1},
        "device_name": {"type": "string"},
        "endpoint_type": {"type": "string"},
        "os_family": {"type": "string"},
        "os_version": {"type": "string"},
        "model": {"type": "string"},
        "trusted_endpoint": {"type": ["boolean", "null"]},
        "disk_encryption_status": {"type": "string"},
        "firewall_status": {"type": "string"},
        "password_status": {"type": "string"},
        "health_app_client_version": {"type": "string"},
        "health_data_last_collected": {"type": ["string", "null"]},
        "last_updated": {"type": ["string", "null"]},
        "tags": {"type": "object"},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "epkey": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "device_name": {"validation": "jsonschema", "schema": {"type": "string"}},
        "endpoint_type": {"validation": "jsonschema", "schema": {"type": "string"}},
        "os_family": {"validation": "jsonschema", "schema": {"type": "string"}},
        "os_version": {"validation": "jsonschema", "schema": {"type": "string"}},
        "model": {"validation": "jsonschema", "schema": {"type": "string"}},
        "trusted_endpoint": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
        "disk_encryption_status": {"validation": "jsonschema", "schema": {"type": "string"}},
        "firewall_status": {"validation": "jsonschema", "schema": {"type": "string"}},
        "password_status": {"validation": "jsonschema", "schema": {"type": "string"}},
        "health_app_client_version": {"validation": "jsonschema", "schema": {"type": "string"}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["epkey"]

    # Duo's endpoint key.
    epkey = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # The device name, when Duo Desktop reports one.
    device_name = models.CharField(max_length=255, blank=True, default="")
    # Duo's `type`: the device class (e.g.
    endpoint_type = models.CharField(max_length=255, blank=True, default="")
    # Operating-system family.
    os_family = models.CharField(max_length=255, blank=True, default="")
    # Operating-system version.
    os_version = models.CharField(max_length=255, blank=True, default="")
    # Device model.
    model = models.CharField(max_length=255, blank=True, default="")
    # Whether the device is a Trusted Endpoint (registered through a management integration).
    trusted_endpoint = models.BooleanField(null=True, blank=True, default=None)
    # As Duo Desktop reports it.
    disk_encryption_status = models.CharField(max_length=255, blank=True, default="")
    # As Duo Desktop reports it.
    firewall_status = models.CharField(max_length=255, blank=True, default="")
    # As Duo Desktop reports it.
    password_status = models.CharField(max_length=255, blank=True, default="")
    # The Duo Desktop version; blank means Duo Desktop is not reporting, so the posture fields are not
    # observed rather than failing.
    health_app_client_version = models.CharField(max_length=255, blank=True, default="")
    # When Duo Desktop last reported posture.
    health_data_last_collected = models.DateTimeField(null=True, blank=True)
    # When Duo last updated the endpoint record.
    last_updated = models.DateTimeField(null=True, blank=True)
    # TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_endpoint"

    def get_name(self) -> str:
        return self.device_name or self.epkey or ""

    def __str__(self) -> str:
        return self.get_name()
