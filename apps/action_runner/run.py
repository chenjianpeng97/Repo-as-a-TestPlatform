"""Execute one action word. Imports packages.action_words lazily."""
from __future__ import annotations

import json
from typing import Any


class ActionRunnerError(ValueError):
    pass


def run_word(
    word_id: str,
    *,
    expect_category: str,
    params: dict[str, Any] | list[Any] | None = None,
    example: bool = False,
) -> tuple[int, dict[str, Any]]:
    if not expect_category or not word_id.startswith(f"{expect_category}."):
        raise ActionRunnerError(
            f"word_id {word_id!r} is not in category {expect_category!r}"
        )

    from packages.action_words import ActionContext, get

    cls = get(word_id)
    if example:
        raw: dict[str, Any] = dict(cls.example_params)
    else:
        raw = dict(params or {})

    with ActionContext() as ctx:
        try:
            result = cls(ctx).run_from_dict(raw)
        except AssertionError as exc:
            return 1, {"ok": False, "error": str(exc)}
    payload = result.model_dump(mode="json")
    return (0 if result.ok else 1), payload


def parse_params_json(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    data = json.loads(raw)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ActionRunnerError("params must be a JSON object")
    return data
