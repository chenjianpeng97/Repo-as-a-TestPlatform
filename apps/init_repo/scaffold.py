"""Scaffold a new project repo: six-layer skeleton + optional platform DNA."""
from __future__ import annotations

import pathlib
import shutil

from apps.init_repo.manifest import PLATFORM_PATHS, REPO_ROOT

# Six-layer skeleton (empty dirs get a .gitkeep).
SKELETON_DIRS: tuple[str, ...] = (
    "assets/ddl",
    "assets/sql",
    "assets/usecases",
    "assets/domain-notes",
    "assets/testreport",
    "packages/action_words",
    "packages/api_objects",
    "packages/page_objects",
    "apps",
    "data",
    "tests/features/ui_steps",
    "tests/features/api_steps",
    "tests/pytest",
    "docs/spec",
    "config",
    "logs",
    "artifacts",
)

# What to copy as shared platform DNA (subset of PLATFORM_PATHS; excludes
# project-specific packages so the new repo starts clean where appropriate).
DNA_PATHS: tuple[str, ...] = PLATFORM_PATHS


_IGNORE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache"}
_IGNORE_SUFFIXES = {".pyc", ".pyo"}


def _copy_file(src: pathlib.Path, dst: pathlib.Path, *, overwrite: bool) -> bool:
    if dst.exists() and not overwrite:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _copy_tree(src: pathlib.Path, dst: pathlib.Path, *, overwrite: bool) -> int:
    """Merge-copy a directory, skipping existing files unless ``overwrite``."""
    copied = 0
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _IGNORE_PARTS for part in path.parts):
            continue
        if path.suffix in _IGNORE_SUFFIXES:
            continue
        rel = path.relative_to(src)
        if _copy_file(path, dst / rel, overwrite=overwrite):
            copied += 1
    return copied


def scaffold(target: pathlib.Path, *, with_ai: bool = True, overwrite: bool = False) -> list[str]:
    """Create the skeleton at ``target``; optionally copy platform DNA.

    Returns a list of human-readable actions taken. Non-destructive by default:
    existing files are left untouched unless ``overwrite`` is set.
    """
    actions: list[str] = []
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)

    for rel in SKELETON_DIRS:
        d = target / rel
        d.mkdir(parents=True, exist_ok=True)
        keep = d / ".gitkeep"
        if not any(d.iterdir()) and not keep.exists():
            keep.write_text("", encoding="utf-8")
        actions.append(f"dir  {rel}")

    if with_ai:
        for rel in DNA_PATHS:
            src = REPO_ROOT / rel
            dst = target / rel
            if not src.exists():
                continue
            if src.is_dir():
                copied = _copy_tree(src, dst, overwrite=overwrite)
                actions.append(f"copy {rel} ({copied} files)")
            elif _copy_file(src, dst, overwrite=overwrite):
                actions.append(f"copy {rel}")
            else:
                actions.append(f"skip {rel} (exists)")

    return actions
