from __future__ import annotations

import json

from apps._shared.plane_app import export_tools, reset_registry_for_tests
from apps.action_runner.run import ActionRunnerError, parse_params_json, run_word


def setup_function() -> None:
    reset_registry_for_tests()


def test_discover_reload_overwrites_same_app_id() -> None:
    """importlib.reload after reset must not treat the new factory as a duplicate."""
    import apps.action_runner.plane  # noqa: F401

    export_tools()
    reset_registry_for_tests()
    tools = {row["app_id"] for row in export_tools()}
    assert "db_seed" in tools


def test_category_tools_registered() -> None:
    import apps.action_runner.plane  # noqa: F401

    tools = {row["app_id"]: row for row in export_tools()}
    assert "db_seed" in tools
    assert "db_assert" in tools
    assert "dump_ddl" not in tools
    seed = tools["db_seed"]
    assert seed["module"] == "apps.action_runner"
    assert seed["argv"] == [
        "python",
        "-m",
        "apps.action_runner",
        "run",
        "--expect-category",
        "db_seed",
    ]
    assert seed["destructive"] is True
    assert seed["plane_runnable"] is True
    assert seed["argv_plan"]
    kinds = {step["key"]: step["kind"] for step in seed["argv_plan"]}
    assert kinds["word_id"] == "positional"
    assert kinds["params"] == "json_option"
    assert kinds["example"] == "store_true"
    assert "expect_category" not in kinds
    pattern = seed["params_schema"]["properties"]["word_id"]["pattern"]
    assert pattern.startswith("^db_seed\\.")


def test_wrong_category_rejected() -> None:
    try:
        run_word("db_seed.create_example", expect_category="db_assert")
    except ActionRunnerError as exc:
        assert "not in category" in str(exc)
        return
    raise AssertionError("expected ActionRunnerError")


def test_parse_params_object() -> None:
    assert parse_params_json('{"n": 1}') == {"n": 1}
    assert parse_params_json("") == {}
    try:
        parse_params_json("[1]")
    except ActionRunnerError:
        return
    raise AssertionError("expected ActionRunnerError")
