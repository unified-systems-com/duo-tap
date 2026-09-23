"""Duo Bypass Code — An outstanding Duo bypass code held by a user: a passcode that satisfies MFA without any enrolled authenticator, with its expiry, remaining uses and issuing administrator."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoBypassCode(BaseModel):
    """An outstanding Duo bypass code held by a user: a passcode that satisfies MFA without any enrolled authenticator, with its expiry, remaining uses and issuing administrator.

    Spec: specs/spec-duo-v0.md (req-duo-bypass-code). Domain article: domain/duo_bypass_code.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_bypass_code"
    ENTITY_NAME: ClassVar[str] = "Duo Bypass Code"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "An outstanding Duo bypass code held by a user: a passcode that satisfies MFA without any enrolled authenticator, with its expiry, remaining uses and issuing administrator."
    )
    ENTITY_ICON: ClassVar[str] = "duo-bypass-code"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "authenticators"}
    # Duo's bypass-code id. Observed only; the code value is never stored.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("bypass_code_id",)
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "bypass_code_id": {"type": "string", "minLength": 1},
        "created": {"type": ["string", "null"]},
        "expiration": {"type": ["string", "null"]},
        "reuse_count": {"type": ["integer", "null"]},
        "admin_email": {"type": "string"},
        "tags": {"type": "object"},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "bypass_code_id": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "reuse_count": {"validation": "jsonschema", "schema": {"type": ["integer", "null"]}},
        "admin_email": {"validation": "jsonschema", "schema": {"type": "string"}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["bypass_code_id"]

    # Duo's id for the code.
    bypass_code_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # When the code was issued.
    created = models.DateTimeField(null=True, blank=True)
    # When the code expires.
    expiration = models.DateTimeField(null=True, blank=True)
    # Remaining uses as Duo reports it; Duo's semantics for 0/null (unlimited) are recorded as reported,
    # not reinterpreted.
    reuse_count = models.IntegerField(null=True, blank=True, default=None)
    # The email of the administrator who created the code, as reported.
    admin_email = models.CharField(max_length=255, blank=True, default="")
    # TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_bypass_code"

    def get_name(self) -> str:
        return self.bypass_code_id or ""

    def __str__(self) -> str:
        return self.get_name()
