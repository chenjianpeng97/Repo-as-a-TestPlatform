"""Static catalog scans. No pytest --collect-only, no SUT, no git writes."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

SKIP_DIR_NAMES = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache"}
METHOD_RE = re.compile(r"""^\s*method\s*=\s*['\"]([A-Za-z]+)['\"]""", re.M)
PATH_RE = re.compile(r"""^\s*path\s*=\s*['\"]([^'\"]+)['\"]""", re.M)
MAX_SCAN_FILES = 4000
MAX_PARSE_BYTES = 256_000


def scan_ddl(root: Path) -> list[dict[str, Any]]:
    ddl_dir = root / "assets" / "ddl"
    ddl: list[dict[str, Any]] = []
    if not ddl_dir.is_dir():
        return ddl
    children = sorted(p for p in ddl_dir.iterdir() if p.name not in SKIP_DIR_NAMES)
    subdirs = [p for p in children if p.is_dir()]
    files = [p for p in children if p.is_file() and p.suffix.lower() == ".sql"]
    if subdirs:
        for folder in subdirs:
            tables = sorted(
                p.stem
                for p in folder.iterdir()
                if p.is_file() and p.suffix.lower() == ".sql" and p.name not in SKIP_DIR_NAMES
            )
            ddl.append(
                {
                    "datasource": folder.name,
                    "path": _rel(root, folder),
                    "table_count": len(tables),
                    "tables": tables,
                }
            )
        return ddl
    if files:
        tables = sorted(p.stem for p in files)
        ddl.append(
            {
                "datasource": "default",
                "path": _rel(root, ddl_dir),
                "table_count": len(tables),
                "tables": tables,
            }
        )
    return ddl


def scan_sql_files(root: Path) -> list[dict[str, str]]:
    sql_dir = root / "assets" / "sql"
    rows: list[dict[str, str]] = []
    if not sql_dir.is_dir():
        return rows
    for path in _iter_files(sql_dir):
        if path.suffix.lower() != ".sql":
            continue
        rows.append({"path": _rel(root, path), "name": path.name})
    return rows


def scan_api_objects(root: Path) -> list[dict[str, Any]]:
    base = root / "packages" / "api_objects"
    if not base.is_dir():
        return []
    rows = []
    for path in _iter_files(base):
        if path.suffix not in {".py", ".yml", ".yaml", ".json"} or path.name.startswith("test_"):
            continue
        if path.name in {"__init__.py", "conftest.py"}:
            continue
        rel = _rel(root, path)
        text = _read_text(path)
        method_match = METHOD_RE.search(text)
        path_match = PATH_RE.search(text)
        rows.append(
            {
                "method": (method_match.group(1) if method_match else "GET").upper(),
                "path": path_match.group(1) if path_match else f"/{path.stem}",
                "file": rel,
                "name": path.stem,
            }
        )
    return rows


def scan_page_objects(root: Path) -> list[dict[str, Any]]:
    base = root / "packages" / "page_objects"
    if not base.is_dir():
        return []
    rows = []
    for path in _iter_files(base):
        if path.suffix != ".py" or path.name in {"__init__.py", "conftest.py"} or path.name.startswith("test_"):
            continue
        rel = _rel(root, path)
        rows.append({"path": rel, "name": path.stem})
    return rows


def scan_features(root: Path) -> list[dict[str, Any]]:
    features = []
    search = root / "tests"
    if not search.is_dir():
        search = root
    for path in _iter_files(search):
        if path.suffix != ".feature":
            continue
        rel = _rel(root, path)
        features.append(_parse_feature(rel, _read_text(path)))
    return features


def scan_pytest_nodes(root: Path) -> list[dict[str, str]]:
    base = root / "tests" / "pytest"
    if not base.is_dir():
        return []
    nodes = []
    for path in _iter_files(base):
        if path.suffix != ".py" or path.name in {"conftest.py", "__init__.py"}:
            continue
        rel = _rel(root, path)
        nodes.append({"nodeid": rel, "file": rel, "name": path.stem})
    return nodes


def scan_data_files(root: Path) -> list[dict[str, str]]:
    base = root / "data"
    if not base.is_dir():
        return []
    rows = []
    for path in _iter_files(base):
        if path.name.startswith("."):
            continue
        rel = _rel(root, path)
        rows.append({"path": rel, "name": path.name})
    return rows


def read_git_meta(root: Path) -> dict[str, str | None]:
    git_dir = root / ".git"
    if git_dir.is_file():
        text = git_dir.read_text(encoding="utf-8").strip()
        if text.lower().startswith("gitdir:"):
            raw = text.split(":", 1)[1].strip()
            candidate = Path(raw)
            git_dir = candidate if candidate.is_absolute() else (root / candidate)
    if not git_dir.is_dir():
        return {"branch": None, "sha": None}
    head_file = git_dir / "HEAD"
    if not head_file.is_file():
        return {"branch": None, "sha": None}
    head = head_file.read_text(encoding="utf-8").strip()
    if head.startswith("ref:"):
        ref = head.split(":", 1)[1].strip()
        branch = ref.removeprefix("refs/heads/")
        ref_file = git_dir / ref
        sha = ref_file.read_text(encoding="utf-8").strip() if ref_file.is_file() else None
        if not sha:
            packed = git_dir / "packed-refs"
            if packed.is_file():
                needle = f" {ref}"
                for line in packed.read_text(encoding="utf-8").splitlines():
                    if line.endswith(needle):
                        sha = line.split(" ", 1)[0].strip()
                        break
        return {"branch": branch, "sha": sha}
    return {"branch": None, "sha": head or None}


def _parse_feature(rel: str, text: str) -> dict[str, Any]:
    feature_name = Path(rel).stem
    feature_tags: list[str] = []
    pending_tags: list[str] = []
    scenarios: list[dict[str, Any]] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("@"):
            pending_tags = [part.lstrip("@") for part in stripped.split() if part.startswith("@")]
            continue
        lower = stripped.lower()
        if lower.startswith("feature:"):
            name = stripped.split(":", 1)[1].strip()
            feature_name = name or feature_name
            feature_tags = pending_tags
            pending_tags = []
            continue
        if lower.startswith("scenario outline:") or lower.startswith("scenario:"):
            kind = "outline" if "outline" in lower else "scenario"
            name = stripped.split(":", 1)[1].strip()
            scenarios.append({"name": name, "tags": pending_tags, "type": kind})
            pending_tags = []
    return {"path": rel, "name": feature_name, "tags": feature_tags, "scenarios": scenarios}


def _iter_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return
    count = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        count += 1
        if count > MAX_SCAN_FILES:
            return
        yield path


def _rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _read_text(path: Path) -> str:
    try:
        size = path.stat().st_size
        if size > MAX_PARSE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
