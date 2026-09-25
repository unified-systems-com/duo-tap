"""Fill account_name on existing Duo applications, groups and policies from the account holding them.

0004 added account_name empty, so every object written before it would share the ("", name) key
this change exists to split. The owning account is already on the grid: its HOLDS_ACCOUNT_OBJECT__duo
edge. Each object held by exactly one live account takes that account's name; an object held by
none or by several is left empty, because guessing an owner would invent a fact. History rows keep
the value they recorded. Direct ORM access is the sanctioned path in migrations.
"""

from typing import Any

from django.db import migrations

_HOLDS = "HOLDS_ACCOUNT_OBJECT__duo"
_SCOPED = ("DuoApplication", "DuoGroup", "DuoPolicy")


def backfill_account_name(apps: Any, schema_editor: Any) -> None:
    Edge = apps.get_model("tap_grid", "Edge")
    Account = apps.get_model("duo", "DuoAccount")
    account_names = dict(Account._base_manager.values_list("entity_id", "name"))
    for model_name in _SCOPED:
        model = apps.get_model("duo", model_name)
        for row in model._base_manager.filter(account_name=""):
            holders = set(
                Edge._base_manager.filter(
                    edge_type=_HOLDS,
                    to_entity_id=row.entity_id,
                    entity__deleted_at__isnull=True,
                ).values_list("from_entity_id", flat=True)
            )
            names = {account_names[h] for h in holders if account_names.get(h)}
            if len(names) == 1:
                model._base_manager.filter(pk=row.pk).update(account_name=names.pop())


class Migration(migrations.Migration):
    dependencies = [
        ("duo", "0004_scope_by_account_drop_tags"),
    ]

    operations = [migrations.RunPython(backfill_account_name, migrations.RunPython.noop)]
