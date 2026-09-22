"""Workbench kind plugins: one module per kit category, looked up by id.

Adding a kit ``ActionCategory`` means adding a file here and registering it
in ``KIND_REGISTRY``. List/detail templates and home cards follow the kind,
so the workbench does not grow a chain of ``if category == …``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tuner_testkit.catalog.directory import WORD_CATEGORIES

from . import app_generic, word_db_seed, word_generic

_DESTRUCTIVE_WORDS = frozenset({"db_seed", "api_request", "ui_action"})


@dataclass(frozen=True)
class Kind:
    kind_id: str
    label: str
    item_type: str
    category: str | None
    destructive_default: bool
    list_path: str
    list_template: str
    detail_template: str
    home_card: bool


def _kind(raw: dict[str, Any]) -> Kind:
    return Kind(**raw)


APP_GENERIC = _kind(app_generic.KIND)
WORD_DB_SEED = _kind(word_db_seed.KIND)
WORD_GENERIC = _kind(word_generic.KIND)

KIND_REGISTRY: dict[str, Kind] = {
    APP_GENERIC.kind_id: APP_GENERIC,
    WORD_DB_SEED.kind_id: WORD_DB_SEED,
}


def generic_word_kind(category: str) -> Kind:
    raw = dict(word_generic.KIND)
    raw.update(
        {
            "kind_id": category,
            "label": word_generic.LABELS.get(category, category),
            "category": category,
            "destructive_default": category in _DESTRUCTIVE_WORDS,
            "list_path": f"/words/{category}",
        }
    )
    return _kind(raw)


def known_word_kind(kind_id: str) -> Kind | None:
    if kind_id == APP_GENERIC.kind_id:
        return None
    if kind_id in KIND_REGISTRY:
        registered = KIND_REGISTRY[kind_id]
        if registered.item_type == "word":
            return registered
    if kind_id in WORD_CATEGORIES:
        return generic_word_kind(kind_id)
    return None


def kind_for_item(item: dict[str, Any]) -> Kind:
    if item.get("kind") == "tool":
        return APP_GENERIC
    category = str(item.get("category") or item.get("group") or "")
    if category in KIND_REGISTRY and KIND_REGISTRY[category].item_type == "word":
        return KIND_REGISTRY[category]
    if category in WORD_CATEGORIES:
        return generic_word_kind(category)
    return WORD_GENERIC


def home_cards(counts_by_kind: dict[str, int]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    ordered = [APP_GENERIC, *[KIND_REGISTRY.get(cat) or generic_word_kind(cat) for cat in WORD_CATEGORIES]]
    for spec in ordered:
        if not spec.home_card:
            continue
        cards.append(
            {
                "kind_id": spec.kind_id,
                "label": spec.label,
                "count": int(counts_by_kind.get(spec.kind_id, 0)),
                "href": spec.list_path,
            }
        )
    return cards
