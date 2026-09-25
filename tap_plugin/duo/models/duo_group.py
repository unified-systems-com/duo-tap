"""Duo Group — A Duo group: a named set of users that an application can be restricted to and that a group policy targets. Its own status can put every member into bypass or disable them."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class DuoGroup(BaseModel):
    """A Duo group: a named set of users that an application can be restricted to and that a group policy targets. Its own status can put every member into bypass or disable them.

    Spec: specs/spec-duo-v0.md (req-duo-group). Domain article: domain/duo_group.md.
    """

    ENTITY_TYPE: ClassVar[str] = "duo__duo_group"
    ENTITY_NAME: ClassVar[str] = "Duo Group"
    ENTITY_DESCRIPTION: ClassVar[str] = (
        "A Duo group: a named set of users that an application can be restricted to and that a group policy targets. Its own status can put every member into bypass or disable them."
    )
    ENTITY_ICON: ClassVar[str] = "duo-group"
    # The Duo surface this type belongs to (domain/dimensions/duo.surface.md). No dcom or
    # deployment.environment default: those belong to the observation, not the type.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {"duo.surface": "directory"}
    # Names are unique only within an account, so the key is (account_name, name). A design names
    # the group before it exists; group_id (DG…) is the stable id and the key moves to
    # (account_name, that id) when req-duo-collector makes it observable.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("account_name", "name")
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#6DB33F", "label": "#2E5A12"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "account_name": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "group_id": {"type": "string"},
        "description": {"type": "string"},
        "status": {"type": "string", "enum": ["", "Active", "Bypass", "Disabled"]},
    }
    # Datetime fields are typed DateTimeFields; their own validation is the right layer, so they
    # carry no JSON-Schema entry here (the CRUD schema describes only the inbound JSON shape).
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "account_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "group_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "description": {"validation": "jsonschema", "schema": {"type": "string"}},
        "status": {
            "validation": "jsonschema",
            "schema": {"type": "string", "enum": ["", "Active", "Bypass", "Disabled"]},
        },
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["account_name", "name"]

    #: The name of the Duo account this object lives in: the duo__duo_account's natural key. A
    #: scoping column, not a copy of the account: the account's own facts live on the account, and
    #: HOLDS_ACCOUNT_OBJECT__duo is what a traversal follows. It is here because two accounts can
    #: each hold an object with the same name (every account has a "Global Policy"), and the key
    #: must tell them apart, so the fact the key rests on is a column.
    account_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # The group's name.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # Duo's group id (`DG…`).
    group_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # The group's description (`desc`).
    description = models.TextField(blank=True, default="")
    # The group's status as Duo reports it: `Active`, `Bypass` or `Disabled`.
    status = models.CharField(max_length=16, blank=True, default="")

    class Meta(BaseModel.Meta):
        db_table = "duo__duo_group"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
