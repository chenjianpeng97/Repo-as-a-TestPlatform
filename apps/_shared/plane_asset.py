"""Opt-in Plane asset marks: re-export package decorators and collect catalog rows.

Import-safe: no DB / HTTP. Discovery loads marked modules by file path so a
broken ``packages.page_objects.__init__`` cannot hide sibling page files.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from packages.action_words.plane import (
    ACTION_WORD_ARGV,
    ACTION_WORD_ARGV_PLAN,
    ACTION_WORD_KINDS,
    DESTRUCTIVE_KINDS,
    PLANE_KIND_ATTR,
    TIMEOUT_BY_KIND,
    export_plane_action_words,
    plane_api_assert,
    plane_api_request,
    plane_db_assert,
    plane_db_seed,
    plane_ui_action,
    plane_ui_assert,
)
from packages.api_objects.plane import plane_apiobject
from packages.page_objects.plane import plane_pageobject

__all__ = [
    "ACTION_WORD_ARGV",
    "ACTION_WORD_ARGV_PLAN",
    "ACTION_WORD_KINDS",
    "DESTRUCTIVE_KINDS",
    "PLANE_KIND_ATTR",
    "TIMEOUT_BY_KIND",
    "collect_plane_api_objects",
    "collect_plane_page_objects",
    "export_plane_action_words",
    "plane_api_assert",
    "plane_api_request",
    "plane_apiobject",
    "plane_db_assert",
    "plane_db_seed",
    "plane_pageobject",
    "plane_ui_action",
    "plane_ui_assert",
]


def collect_plane_api_objects(repo_root: str | Path | None = None) -> list[dict[str, Any]]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    rows: list[dict[str, Any]] = []
    for rel, obj in _iter_marked(root, "packages.api_objects", "api_object"):
        method = str(getattr(obj, "method", "GET") or "GET").upper()
        path = str(getattr(obj, "path", "") or "")
        name = str(getattr(obj, "name", "") or Path(rel).stem)
        ident = str(getattr(obj, "id", "") or name)
        rows.append(
            {
                "id": ident,
                "name": name,
                "method": method,
                "path": path,
                "file": rel,
                "plane_kind": "api_object",
                "plane_runnable": False,
            }
        )
    return rows


def collect_plane_page_objects(repo_root: str | Path | None = None) -> list[dict[str, Any]]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    rows: list[dict[str, Any]] = []
    for rel, obj in _iter_marked(root, "packages.page_objects", "page_object"):
        name = getattr(obj, "__name__", None) or getattr(obj, "name", None) or Path(rel).stem
        rows.append(
            {
                "name": str(name),
                "path": rel,
                "plane_kind": "page_object",
                "plane_runnable": False,
            }
        )
    return rows


def _iter_marked(root: Path, package: str, kind: str) -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []
    seen: set[int] = set()
    pkg_root = root.joinpath(*package.split("."))
    if not pkg_root.is_dir():
        return found
    for path in sorted(pkg_root.rglob("*.py")):
        if path.name.startswith("test_") or path.name == "conftest.py":
            continue
        if any(part.startswith(".") or part == "__pycache__" for part in path.relative_to(pkg_root).parts):
            continue
        rel = path.relative_to(root).as_posix()
        mod_name = ".".join(path.relative_to(root).with_suffix("").parts)
        if not all(part.isidentifier() for part in mod_name.split(".")):
            continue
        mod = _load_module(mod_name, path)
        if mod is None:
            continue
        for value in vars(mod).values():
            if getattr(value, PLANE_KIND_ATTR, None) != kind:
                continue
            marker = id(value)
            if marker in seen:
                continue
            seen.add(marker)
            found.append((rel, value))
    return found


def _load_module(mod_name: str, path: Path) -> Any | None:
    resolved = path.resolve()
    existing = sys.modules.get(mod_name)
    if existing is not None:
        existing_file = getattr(existing, "__file__", None)
        if existing_file and Path(existing_file).resolve() == resolved:
            return existing
        return _exec_module(f"_plane_asset_scan.{mod_name}.{abs(hash(str(resolved)))}", path)
    return _exec_module(mod_name, path)


def _exec_module(mod_name: str, path: Path) -> Any | None:
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(mod_name, None)
        return None
    return mod


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]
