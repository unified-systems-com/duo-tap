"""Behaviour tests for duo__duo_account (req-duo-account)."""

from __future__ import annotations

import pytest
from tap_plugin.duo.models import DuoAccount

from tap_grid.caller_context import CallerContext
from tap_grid.services import WriteOperation, write_batch

TYPE = "duo__duo_account"


@pytest.mark.django_db
class TestDuoAccount:
    def test_create_with_name_only(self) -> None:
        """req-duo-account-1: a design-phase node needs only its name."""
        result = write_batch(
            [WriteOperation(verb="create_node", type_slug=TYPE, payload={"name": "staging"})],
            caller_context=CallerContext(),
        )
        assert result.results[0].success
        row = DuoAccount.all_objects.get(entity_id=result.results[0].entity_id)
        assert row.name == "staging"
        assert row.api_hostname == ""

    def test_name_required(self) -> None:
        """req-duo-account-2: a write without a name is refused."""
        result = write_batch(
            [WriteOperation(verb="create_node", type_slug=TYPE, payload={"api_hostname": "x"})],
            caller_context=CallerContext(),
        )
        assert not result.results[0].success


def test_keyed_by_name() -> None:
    """req-duo-account-4: the key rests only on a field the model carries."""
    assert DuoAccount.NATURAL_KEY == ("name",)
    names = {f.name for f in DuoAccount._meta.get_fields()}
    assert all(k in names for k in DuoAccount.NATURAL_KEY)


def test_no_free_form_record() -> None:
    """req-duo-account-7: the account declares no free-form `configuration` field."""
    assert "configuration" not in DuoAccount.FIELD_CRUD_SCHEMA
    assert "configuration" not in DuoAccount.FIELD_VALIDATION_SCHEMA
    assert "configuration" not in {f.name for f in DuoAccount._meta.get_fields()}


@pytest.mark.django_db
def test_configuration_write_is_refused() -> None:
    """req-duo-account-7: a create_node write carrying `configuration` is refused, so the settings
    response cannot be passed through whole."""
    result = write_batch(
        [WriteOperation(verb="create_node", type_slug=TYPE, payload={"name": "staging", "configuration": {"secret": "sentinel"}})],
        caller_context=CallerContext(),
    )
    assert not result.results[0].success
