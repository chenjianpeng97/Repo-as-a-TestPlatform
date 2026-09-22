"""Assemble the workspace catalog (``catalog_version`` 3)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tuner_testkit.catalog.scan import (
    git_first_author,
    read_git_meta,
    scan_action_words,
    scan_ai_components,
    scan_api_objects,
    scan_apps_readmes,
    scan_assets,
    scan_data_files,
    scan_ddl,
    scan_docs,
    scan_features,
    scan_inbox,
    scan_page_objects,
    scan_pytest_nodes,
    scan_run_manifests,
    scan_sql_files,
)

CATALOG_VERSION = 3
DEFAULT_CATALOG_REL = "artifacts/catalogs/workspace.json"


def build_catalog(root: Path | None = None, *, include_kit_tools: bool = True) -> dict[str, Any]:
    from tuner_testkit.project import project_root
    from tuner_testkit.tools import export_tools

    repo = Path(root).resolve() if root is not None else project_root()
    tools = export_tools(repo, include_kit=include_kit_tools)
    readmes = scan_apps_readmes(repo)
    for row in tools:
        meta = readmes.get(row["tool_id"]) or {}
        row["author"] = meta.get("author")
        row["created"] = meta.get("created")
        if not row.get("readme_path") and meta.get("readme_path"):
            row["readme_path"] = meta["readme_path"]
        _attach_author_check(repo, row, row.get("readme_path"))
    action_words = scan_action_words(repo)
    api_objects = scan_api_objects(repo)
    page_objects = scan_page_objects(repo)
    ddl = scan_ddl(repo)
    sql_files = scan_sql_files(repo)
    assets = scan_assets(repo)
    for row in assets:
        _attach_author_check(repo, row, row.get("path"))
    features = scan_features(repo)
    pytest_nodes = scan_pytest_nodes(repo)
    data_files = scan_data_files(repo)
    docs = scan_docs(repo)
    inbox = scan_inbox(repo)
    runs = scan_run_manifests(repo, "runs")
    reports = scan_run_manifests(repo, "reports")
    evidence = _count_dirs(repo / "artifacts" / "evidence")
    ai = scan_ai_components(repo)
    git = read_git_meta(repo)
    words_ok = [row for row in action_words if "word_id" in row]
    return {
        "catalog_version": CATALOG_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(repo),
        "git": git,
        "counts": {
            "tools": len(tools),
            "workspace_tools": sum(1 for t in tools if t.get("origin") == "workspace"),
            "action_words": len(words_ok),
            "api_objects": len(api_objects),
            "page_objects": len(page_objects),
            "ddl_tables": sum(block["table_count"] for block in ddl),
            "sql_files": len(sql_files),
            "assets": len(assets),
            "features": len(features),
            "scenarios": sum(len(item["scenarios"]) for item in features),
            "pytest_nodes": len(pytest_nodes),
            "data_files": len(data_files),
            "docs": docs["count"],
            "inbox": inbox["total"],
            "inbox_open": sum(v for k, v in inbox["by_status"].items() if k not in {"done", "closed"}),
            "runs": runs["total"],
            "reports": reports["total"],
            "evidence_runs": evidence,
            "ai_components": ai["rules"] + ai["skills"] + ai["agents"] + ai["hooks"],
        },
        "tools": tools,
        "action_words": action_words,
        "api_objects": api_objects,
        "page_objects": page_objects,
        "knowledge": {"ddl": ddl, "sql_files": sql_files, "assets": assets},
        "tests": {"features": features, "pytest_nodes": pytest_nodes},
        "data": data_files,
        "docs": docs,
        "artifacts": {"inbox": inbox, "runs": runs, "reports": reports, "evidence_runs": evidence},
        "ai_components": ai,
    }


def _attach_author_check(root: Path, row: dict[str, Any], rel_path: str | None) -> None:
    """Stamp git first-author + mismatch flag (C1). Never blocks the catalog."""
    first = git_first_author(root, rel_path) if rel_path else None
    author = row.get("author")
    row["git_first_author"] = first
    row["author_mismatch"] = bool(author and first and str(author).lower() != first.lower())


def write_catalog(payload: dict[str, Any], out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return out


def _count_dirs(base: Path) -> int:
    if not base.is_dir():
        return 0
    return sum(1 for child in base.iterdir() if child.is_dir())
