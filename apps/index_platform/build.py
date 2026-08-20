"""Build the catalog payload Plane stores as CatalogSnapshot."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps._shared.plane_app import export_tools
from apps.index_platform.catalog import (
    read_git_meta,
    scan_api_objects,
    scan_data_files,
    scan_ddl,
    scan_features,
    scan_page_objects,
    scan_pytest_nodes,
    scan_sql_files,
)


def build_catalog(root: Path | None = None) -> dict[str, Any]:
    repo = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    tools = export_tools(repo)
    from packages.action_words import export_catalog as export_action_words

    action_words = export_action_words()
    api_objects = scan_api_objects(repo)
    page_objects = scan_page_objects(repo)
    ddl = scan_ddl(repo)
    sql_files = scan_sql_files(repo)
    features = scan_features(repo)
    pytest_nodes = scan_pytest_nodes(repo)
    data_files = scan_data_files(repo)
    git = read_git_meta(repo)
    return {
        "catalog_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git": git,
        "counts": {
            "apps": len(tools),
            "action_words": len(action_words),
            "api_objects": len(api_objects),
            "page_objects": len(page_objects),
            "ddl_tables": sum(block["table_count"] for block in ddl),
            "sql_files": len(sql_files),
            "features": len(features),
            "scenarios": sum(len(item["scenarios"]) for item in features),
            "pytest_nodes": len(pytest_nodes),
            "data_files": len(data_files),
        },
        "tools": tools,
        "components": {
            "action_words": action_words,
            "api_objects": api_objects,
            "page_objects": page_objects,
        },
        "knowledge": {"ddl": ddl, "sql_files": sql_files},
        "tests": {"features": features, "pytest_nodes": pytest_nodes},
        "data": data_files,
    }
