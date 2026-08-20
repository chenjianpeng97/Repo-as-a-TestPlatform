"""Opt-in Plane marks for action words.

``@register`` remains the BDD/pytest catalog. Only words also marked here
appear in TestCopilot Formulation / Jobs.
"""
from __future__ import annotations

from typing import Any, Callable

from packages.action_words.base import ActionCategory, ActionWord
from packages.action_words.registry import list_all, register

PLANE_KIND_ATTR = "_plane_kind"
ACTION_WORD_KINDS: tuple[str, ...] = tuple(item.value for item in ActionCategory)
DESTRUCTIVE_KINDS = frozenset({"db_seed", "api_request", "ui_action"})
TIMEOUT_BY_KIND = {
    "db_seed": 300,
    "db_assert": 180,
    "api_request": 180,
    "api_assert": 180,
    "ui_action": 300,
    "ui_assert": 180,
}
ACTION_WORD_ARGV = ["python", "-m", "packages.action_words", "run"]
ACTION_WORD_ARGV_PLAN = [
    {"key": "word_id", "kind": "positional"},
    {"key": "params", "kind": "json_option", "flag": "--params"},
    {"key": "example", "kind": "store_true", "flag": "--example"},
]


def _mark_action_word(kind: str) -> Callable[[type[ActionWord]], type[ActionWord]]:
    def decorator(cls: type[ActionWord]) -> type[ActionWord]:
        register(cls)
        if str(cls.category) != kind:
            raise ValueError(f"{cls.word_id}: @plane_{kind} requires category={kind}")
        setattr(cls, PLANE_KIND_ATTR, kind)
        return cls

    return decorator


plane_db_seed = _mark_action_word("db_seed")
plane_db_assert = _mark_action_word("db_assert")
plane_api_request = _mark_action_word("api_request")
plane_api_assert = _mark_action_word("api_assert")
plane_ui_action = _mark_action_word("ui_action")
plane_ui_assert = _mark_action_word("ui_assert")


def export_plane_action_words() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cls in list_all():
        kind = getattr(cls, PLANE_KIND_ATTR, None)
        if kind not in ACTION_WORD_KINDS:
            continue
        row = cls.describe()
        row.update(
            {
                "plane_kind": kind,
                "plane_runnable": True,
                "destructive": kind in DESTRUCTIVE_KINDS,
                "timeout": TIMEOUT_BY_KIND.get(kind, 180),
                "module": "packages.action_words",
                "argv": list(ACTION_WORD_ARGV),
                "argv_plan": list(ACTION_WORD_ARGV_PLAN),
                "job_params_schema": {
                    "type": "object",
                    "properties": {
                        "word_id": {
                            "type": "string",
                            "pattern": rf"^{kind}\.[a-z][a-z0-9_]*$",
                        },
                        "params": {"type": "object"},
                        "example": {"type": "boolean"},
                    },
                    "required": ["word_id"],
                    "additionalProperties": False,
                },
            }
        )
        rows.append(row)
    return rows
