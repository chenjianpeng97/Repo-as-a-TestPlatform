"""Stamp Markdown front-matter with git identity (C1).

``tuner-workspace meta stamp <path>`` writes ``author`` / ``created`` / ``updated``
from ``git config user.email`` (override with ``--author``). Skills call this
instead of inventing an email. ``check_author`` compares the stamped author
against ``git log --diff-filter=A`` (first committer) for catalog ``--check``.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from tuner_testkit.catalog.front_matter import parse_front_matter, replace_front_matter
from tuner_testkit.catalog.scan import git_config_value, git_first_author


def resolve_author(root: Path, override: str | None = None) -> str | None:
    if override and override.strip():
        return override.strip()
    return git_config_value(root, "user.email") or git_config_value(root, "user.name")


def stamp_file(
    root: Path,
    path: Path,
    *,
    author: str | None = None,
    kind: str | None = None,
    today: str | None = None,
) -> dict[str, Any]:
    """Write/update front-matter on *path* (relative to *root* or absolute)."""
    target = path if path.is_absolute() else (root / path)
    if not target.is_file():
        raise FileNotFoundError(f"cannot stamp missing file: {target}")
    original = target.read_text(encoding="utf-8")
    meta = parse_front_matter(original)
    email = resolve_author(root, author)
    if email:
        meta["author"] = email
    day = today or date.today().isoformat()
    if not meta.get("created"):
        meta["created"] = day
    meta["updated"] = day
    if kind and not meta.get("kind"):
        meta["kind"] = kind
    if "title" not in meta:
        heading = next((ln[2:].strip() for ln in original.splitlines() if ln.startswith("# ")), target.stem)
        meta["title"] = heading
    stamped = replace_front_matter(original, meta)
    if stamped != original:
        target.write_text(stamped, encoding="utf-8", newline="\n")
    git_author = git_first_author(root, target.relative_to(root).as_posix()) if target.is_relative_to(root) else None
    mismatch = bool(email and git_author and email.lower() != git_author.lower())
    return {
        "path": str(target.relative_to(root)) if target.is_relative_to(root) else str(target),
        "author": meta.get("author"),
        "created": meta.get("created"),
        "updated": meta.get("updated"),
        "kind": meta.get("kind"),
        "git_first_author": git_author,
        "author_mismatch": mismatch,
        "written": stamped != original,
    }


def check_author(root: Path, rel_path: str, stamped_author: str | None) -> dict[str, Any]:
    first = git_first_author(root, rel_path)
    mismatch = bool(stamped_author and first and stamped_author.lower() != first.lower())
    return {"path": rel_path, "author": stamped_author, "git_first_author": first, "author_mismatch": mismatch}
