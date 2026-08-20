"""Release manifest: version + content hashes of the bundled platform assets.

The manifest lets us detect drift: if any tracked common asset changes but the
``template_version`` was not bumped, ``check_drift`` reports it. Deterministic,
stdlib-only.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from dataclasses import dataclass

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST_PATH = pathlib.Path(__file__).resolve().parent / "release_manifest.json"

# The shared "platform DNA" that init_repo bundles and version-tracks. Paths are
# repo-root-relative; directories are walked recursively.
PLATFORM_PATHS: tuple[str, ...] = (
    ".cursor/rules",
    ".cursor/skills",
    ".cursor/agents",
    ".cursor/hooks",
    ".cursor/hooks.json",
    "docs/spec",
    "packages",
    "config",
    "apps/_shared",
    "apps/__init__.py",
    "apps/dump_ddl.py",
    "apps/recorder",
    "apps/index_ai",
    "apps/index_platform",
    "apps/init_repo",
    "tools/git-hooks",
    "AGENTS.md",
    "INDEX.md",
    "behave.ini",
    "pyproject.toml",
)

_EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache"}
_EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
# Manifest itself is excluded to avoid a self-referential hash.
_EXCLUDE_NAMES = {"release_manifest.json"}


def read_template_version(root: pathlib.Path = REPO_ROOT) -> str:
    """Read ``[project] version`` from pyproject.toml (stdlib tomllib)."""
    pyproject = root / "pyproject.toml"
    try:
        import tomllib

        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        return str(data.get("project", {}).get("version", "0.0.0"))
    except Exception:  # noqa: BLE001 -- fall back to regex
        m = re.search(r'^version\s*=\s*"([^"]+)"', pyproject.read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else "0.0.0"


def _iter_files(root: pathlib.Path) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for rel in PLATFORM_PATHS:
        target = root / rel
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            for path in target.rglob("*"):
                if not path.is_file():
                    continue
                if any(part in _EXCLUDE_PARTS for part in path.parts):
                    continue
                if path.suffix in _EXCLUDE_SUFFIXES or path.name in _EXCLUDE_NAMES:
                    continue
                files.append(path)
    return sorted(set(files))


def compute_hashes(root: pathlib.Path = REPO_ROOT) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in _iter_files(root):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rel = str(path.relative_to(root)).replace("\\", "/")
        hashes[rel] = digest
    return hashes


def build_manifest(root: pathlib.Path = REPO_ROOT, version: str | None = None) -> dict:
    import datetime as _dt

    return {
        "template_version": version or read_template_version(root),
        "generated_at": _dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "tracked_paths": list(PLATFORM_PATHS),
        "files": compute_hashes(root),
    }


def write_manifest(root: pathlib.Path = REPO_ROOT, version: str | None = None) -> pathlib.Path:
    manifest = build_manifest(root, version)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return MANIFEST_PATH


def load_manifest() -> dict | None:
    if not MANIFEST_PATH.exists():
        return None
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


@dataclass
class Drift:
    added: list[str]
    removed: list[str]
    changed: list[str]

    @property
    def any(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def check_drift(root: pathlib.Path = REPO_ROOT) -> Drift | None:
    """Compare current tracked files against the stored manifest.

    Returns None when there is no manifest yet. Otherwise a ``Drift`` (possibly
    empty) describing added/removed/changed tracked files.
    """
    manifest = load_manifest()
    if manifest is None:
        return None
    stored: dict[str, str] = manifest.get("files", {})
    current = compute_hashes(root)
    stored_keys = set(stored)
    current_keys = set(current)
    added = sorted(current_keys - stored_keys)
    removed = sorted(stored_keys - current_keys)
    changed = sorted(
        k for k in (stored_keys & current_keys) if stored[k] != current[k]
    )
    return Drift(added=added, removed=removed, changed=changed)
