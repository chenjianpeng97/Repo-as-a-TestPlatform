from __future__ import annotations

from apps._shared.plane_app import reset_registry_for_tests
from apps.index_platform.build import build_catalog


def setup_function() -> None:
    reset_registry_for_tests()


def test_catalog_tools_are_plane_apps_only() -> None:
    payload = build_catalog()
    ids = {row["app_id"] for row in payload["tools"]}
    assert "db_seed" in ids
    assert "api_request" in ids
    assert "dump_ddl" not in ids
    assert "recorder" not in ids
    assert "index_ai" not in ids
    assert "index_platform" not in ids
    assert payload["catalog_version"] == 2
    assert "action_words" in payload["components"]
    assert "counts" in payload
    assert payload["counts"]["apps"] == len(payload["tools"])
