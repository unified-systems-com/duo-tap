"""Event time (core's req-grid-entity-event-time, tap 0.4.7): what each duo model declares, and what core
derives from it.

The first class pins the declarations, so a model added later without one, or one that names the wrong
field, fails here. The second applies core's own derivation to plain values, so the bypass code's open
end (Duo's `expiration` null: the code never expires) is read as no end rather than as no event time.
"""

from datetime import UTC, datetime

from tap_plugin.duo.models import (
    DuoAccount,
    DuoAdministrator,
    DuoApplication,
    DuoBypassCode,
    DuoEndpoint,
    DuoGroup,
    DuoHardwareToken,
    DuoPhone,
    DuoPolicy,
    DuoUser,
    DuoWebauthnCredential,
)

from tap_grid.event_time import NO_EVENT_TIME, Interval, declaration_problems, derive
from tap_grid.registry import get_model_class, list_entity_types

DECLARED = {
    DuoUser: Interval(start="created", kind="created"),
    DuoWebauthnCredential: Interval(start="date_added", kind="created"),
    DuoBypassCode: Interval(start="created", kind="created", end="expiration"),
    DuoAccount: NO_EVENT_TIME,
    DuoAdministrator: NO_EVENT_TIME,
    DuoApplication: NO_EVENT_TIME,
    DuoEndpoint: NO_EVENT_TIME,
    DuoGroup: NO_EVENT_TIME,
    DuoHardwareToken: NO_EVENT_TIME,
    DuoPhone: NO_EVENT_TIME,
    DuoPolicy: NO_EVENT_TIME,
}

ISSUED = datetime(2026, 11, 2, 9, 30, tzinfo=UTC)
EXPIRES = datetime(2026, 11, 9, 9, 30, tzinfo=UTC)


class TestDeclarations:
    def test_every_model_of_the_plugin_decides(self) -> None:
        own = {get_model_class(slug) for slug in list_entity_types() if slug.startswith("duo__")}
        assert own == set(DECLARED)
        assert {model: model.EVENT_TIME for model in own} == DECLARED

    def test_core_accepts_each_declaration(self) -> None:
        for model in DECLARED:
            assert declaration_problems(model) == [], model.__name__


class TestDerivation:
    def test_a_bypass_code_holds_from_issue_to_expiration(self) -> None:
        values = {"created": ISSUED, "expiration": EXPIRES}
        derived = derive(DuoBypassCode.EVENT_TIME, values.get)
        assert (derived.event_start, derived.event_end, derived.kind) == (ISSUED, EXPIRES, "created")

    def test_a_bypass_code_that_never_expires_has_no_end(self) -> None:
        values = {"created": ISSUED, "expiration": None}
        derived = derive(DuoBypassCode.EVENT_TIME, values.get)
        assert (derived.event_start, derived.event_end, derived.kind) == (ISSUED, None, "created")

    def test_a_user_with_no_creation_date_has_none(self) -> None:
        derived = derive(DuoUser.EVENT_TIME, {"created": None}.get)
        assert (derived.event_start, derived.event_end, derived.kind) == (None, None, None)
