"""Tool manifest: argparse → schema/argv_plan, discovery, argv rebuild."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from tuner_testkit.tools import manifest as m


def setup_function() -> None:
    m.reset_registry_for_tests()


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="x")
    p.add_argument("--count", type=int, required=True, help="how many")
    p.add_argument("--label", default="sample", help="label prefix")
    p.add_argument("--style", choices=("plain", "upper"), default="plain")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--params", help="json blob")
    p.add_argument("target", nargs="?")
    return p


def test_plan_and_schema_types_defaults_enums() -> None:
    plan, schema = m.plan_and_schema(_parser(), json_params=("params",))
    props = schema["properties"]
    assert props["count"] == {"type": "integer", "description": "how many"}
    assert props["label"] == {"type": "string", "description": "label prefix", "default": "sample"}
    assert props["style"]["enum"] == ["plain", "upper"]
    assert props["dry_run"] == {"type": "boolean", "default": False}
    assert props["params"]["type"] == "object"
    assert props["target"] == {"type": "string"}
    assert schema["required"] == ["count"]
    kinds = {step["key"]: step["kind"] for step in plan}
    assert kinds == {
        "count": "option",
        "label": "option",
        "style": "option",
        "dry_run": "store_true",
        "params": "json_option",
        "target": "positional",
    }


def test_register_and_build_argv() -> None:
    spec = m.register_tool(
        _parser,
        tool_id="demo",
        name="Demo",
        module="apps.demo",
        json_params=("params",),
    )
    argv = m.build_argv(spec, {"count": 3, "label": "x", "dry_run": True, "params": {"a": 1}, "target": "t"})
    assert argv == ["python", "-m", "apps.demo", "--count", "3", "--label", "x", "--dry-run", "--params", '{"a": 1}', "t"]
    assert m.build_argv(spec, {"count": 1, "dry_run": False}) == ["python", "-m", "apps.demo", "--count", "1"]


def test_validate_params_reports_missing_unknown_type_enum() -> None:
    _, schema = m.plan_and_schema(_parser(), json_params=("params",))
    errors = m.validate_params(schema, {"label": "x", "bogus": 1, "style": "loud"})
    assert any("missing required parameter: count" in e for e in errors)
    assert any("unknown parameter: bogus" in e for e in errors)
    assert any("style" in e for e in errors)
    assert m.validate_params(schema, {"count": "3", "dry_run": "true"}) == []


def test_register_rejects_bad_ids_and_modules() -> None:
    with pytest.raises(ValueError):
        m.register_tool(_parser, tool_id="Bad-Id", name="x", module="apps.x")
    with pytest.raises(ValueError):
        m.register_tool(_parser, tool_id="ok", name="x", module="somewhere.else")


def test_discover_workspace_and_kit_tools(tmp_path: Path) -> None:
    app = tmp_path / "apps" / "hello"
    app.mkdir(parents=True)
    (tmp_path / "apps" / "__init__.py").write_text("", encoding="utf-8")
    (app / "__init__.py").write_text("", encoding="utf-8")
    (app / "tool.py").write_text(
        "import argparse\n"
        "from tuner_testkit.tools import tool\n"
        "\n"
        "@tool(tool_id='hello', name='Hello', module='apps.hello', group='demo', destructive=True)\n"
        "def build_parser():\n"
        "    p = argparse.ArgumentParser()\n"
        "    p.add_argument('--who', default='world')\n"
        "    return p\n",
        encoding="utf-8",
    )
    (tmp_path / "apps" / "_private").mkdir()
    rows = m.export_tools(tmp_path)
    by_id = {row["tool_id"]: row for row in rows}
    assert by_id["hello"]["origin"] == "workspace"
    assert by_id["hello"]["destructive"] is True
    assert by_id["hello"]["params_schema"]["properties"]["who"]["default"] == "world"
    # kit manifests (tuner_testkit/apps/*/tool.py) ride along
    assert by_id["mock_server"]["origin"] == "kit"
    assert by_id["mock_server"]["runtime"] == "long_lived"
    assert m.export_tools(tmp_path, include_kit=False) == rows  # already discovered; still present in registry
