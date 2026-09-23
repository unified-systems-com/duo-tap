"""Behaviour tests for duo__duo_account (req-duo-model)."""

from __future__ import annotations

import pytest
from tap_plugin.duo.models import DuoAccount

from tap_grid.caller_context import CallerContext
from tap_grid.services import WriteOperation, write_batch

TYPE = "duo__duo_account"


@pytest.mark.django_db
class TestDuoAccount:
    def test_create_with_name_only(self) -> None:
        """req-duo-model-1: a design-phase node needs only its name."""
        result = write_batch(
            [WriteOperation(verb="create_node", type_slug=TYPE, payload={"name": "staging"})],
            caller_context=CallerContext(),
        )
        assert result.results[0].success
        row = DuoAccount.all_objects.get(entity_id=result.results[0].entity_id)
        assert row.name == "staging"
        assert row.api_hostname == ""

    def test_name_required(self) -> None:
        """req-duo-model-2: a write without a name is refused."""
        result = write_batch(
            [WriteOperation(verb="create_node", type_slug=TYPE, payload={"api_hostname": "x"})],
            caller_context=CallerContext(),
        )
        assert not result.results[0].success


def test_keyed_by_name() -> None:
    """req-duo-model-3: the key rests only on a field the model carries."""
    assert DuoAccount.NATURAL_KEY == ("name",)
    names = {f.name for f in DuoAccount._meta.get_fields()}
    assert all(k in names for k in DuoAccount.NATURAL_KEY)
