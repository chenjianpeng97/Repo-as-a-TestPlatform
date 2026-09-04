from __future__ import annotations

from tuner_testkit.apps._shared.plane_app import reset_registry_for_tests
from tuner_testkit.apps.index_platform.build import build_catalog
from tuner_testkit.action_words.registry import reset_registry_for_tests as reset_words


def setup_function() -> None:
    reset_registry_for_tests()
    reset_words()


def test_catalog_tools_are_plane_apps_only() -> None:
    payload = build_catalog()
    ids = {row["app_id"] for row in payload["tools"]}
    assert "db_seed" not in ids
    assert "api_request" not in ids
    assert "dump_ddl" not in ids
    assert "recorder" not in ids
    assert "index_ai" not in ids
    assert "index_platform" not in ids
    assert payload["catalog_version"] == 2
    assert "action_words" in payload["components"]
    assert payload["counts"]["apps"] == len(payload["tools"])
    word_ids = {row.get("word_id") for row in payload["components"]["action_words"]}
    assert "context" not in word_ids
    assert "__main__" not in word_ids
    api_files = {row.get("file") for row in payload["components"]["api_objects"]}
    assert not any(str(item).endswith("auth.py") for item in api_files)
