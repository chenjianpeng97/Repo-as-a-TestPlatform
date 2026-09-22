"""Workbench directory slice: ``@tool`` + ``@register`` only.

Hot path for ``tuner-workbench`` list/search. Never walks ``assets/``, never
runs ``git log``. Full workspace catalog stays in ``build.py``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from tuner_testkit.action_words.registry import _WORD_SUBPACKAGES
from tuner_testkit.catalog.scan import scan_action_words

_CACHE: dict[str, tuple[tuple[tuple[str, int], ...], dict[str, Any]]] = {}

WORD_CATEGORIES: tuple[str, ...] = _WORD_SUBPACKAGES


def entry_mtimes(root: Path) -> tuple[tuple[str, int], ...]:
    """mtime stamp of workbench entry files only (``tool.py`` + category word modules)."""
    root = root.resolve()
    stamps: list[tuple[str, int]] = []
    apps = root / "apps"
    if apps.is_dir():
        for child in sorted(apps.iterdir()):
            if not child.is_dir() or child.name.startswith(("_", ".")):
                continue
            tool = child / "tool.py"
            if tool.is_file():
                stamps.append((str(tool), tool.stat().st_mtime_ns))
    words = root / "packages" / "action_words"
    if words.is_dir():
        for sub in WORD_CATEGORIES:
            folder = words / sub
            if not folder.is_dir():
                continue
            for path in sorted(folder.rglob("*.py")):
                rel_parts = path.relative_to(folder).parts
                if path.name.startswith("_"):
                    continue
                if any(part.startswith("_") or part == "__pycache__" for part in rel_parts):
                    continue
                stamps.append((str(path), path.stat().st_mtime_ns))
    return tuple(stamps)


def clear_directory_cache(root: Path | None = None) -> None:
    if root is None:
        _CACHE.clear()
        return
    _CACHE.pop(str(Path(root).resolve()), None)


def build_directory(
    root: Path | None = None,
    *,
    include_kit_tools: bool = True,
    refresh: bool = False,
) -> dict[str, Any]:
    """List workbench-visible tools and action words.

    Cached per root until an entry file's mtime changes. ``refresh=True``
    bypasses the cache. Never calls git.
    """
    from tuner_testkit.project import project_root
    from tuner_testkit.tools import export_tools

    repo = Path(root).resolve() if root is not None else project_root()
    key = str(repo)
    stamp = entry_mtimes(repo)
    cached = _CACHE.get(key)
    if not refresh and cached is not None and cached[0] == stamp:
        return cached[1]

    tools = [row for row in export_tools(repo, include_kit=include_kit_tools) if row.get("visibility") != "local"]
    words = [
        row
        for row in scan_action_words(repo, isolate=False)
        if "word_id" in row and row.get("visibility") != "local"
    ]
    counts_by_kind: dict[str, int] = {"apps": len(tools)}
    for category in WORD_CATEGORIES:
        counts_by_kind[category] = sum(1 for row in words if row.get("category") == category)
    payload = {
        "root": key,
        "tools": tools,
        "action_words": words,
        "counts_by_kind": counts_by_kind,
    }
    _CACHE[key] = (stamp, payload)
    return payload
