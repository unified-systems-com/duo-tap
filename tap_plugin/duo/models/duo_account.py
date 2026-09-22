"""Duo Account — a Duo account: one Duo Security tenant that enrolls users and devices and answers second-factor challenges for integrated applications."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoAccount(BaseModel):
    """A Duo account: one Duo Security tenant that enrolls users and devices and answers second-factor challenges for integrated applications.

    v0 is the outer node only: a design can place it before any access exists, so its one
    identifying field stays blank (not observed) until a collector reads it.

    Spec: specs/spec-duo-v0.md (req-duo-model).
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_account"
    ENTITY_NAME: ClassVar[str] = "Duo Account"
    ENTITY_DESCRIPTION: ClassVar[str] = "A Duo account: one Duo Security tenant that enrolls users and devices and answers second-factor challenges for integrated applications."
    ENTITY_ICON: ClassVar[str] = "duo-account"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so the bundle that seeds a node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # A design-phase node has no observed identifier; its name is the only fact it carries.
    # Revisit when the collector makes api_hostname observable (req-duo-collector).
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("name",)
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
        "configuration": {"type": "object"},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "api_hostname": {"validation": "jsonschema", "schema": {"type": "string"}},
        "configuration": {"validation": "jsonschema", "schema": {"type": "object"}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["name"]

    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # The account's API hostname (api-XXXXXXXX.duosecurity.com). Blank until observed.
    api_hostname = models.CharField(max_length=255, blank=True, default="")
    configuration = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_account"

    def get_name(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.get_name()
