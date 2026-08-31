"""packages.fake CLI."""
from __future__ import annotations

import json

from packages.fake.catalog import catalog
from packages.fake.cli import main


def test_cli_list_and_describe(capsys):
    assert main(["list"]) == 0
    rows = json.loads(capsys.readouterr().out)
    ids = {row["id"] for row in rows}
    assert "udi" in ids
    assert "uscc" in ids
    assert main(["describe", "udi"]) == 0
    desc = json.loads(capsys.readouterr().out)
    assert desc["id"] == "udi"
    assert "with_gs" in desc["params_schema"]["properties"]
    assert "count" not in desc["params_schema"].get("properties", {})


def test_cli_run_lines_count(capsys):
    assert main(["run", "uscc", "--count", "10", "--seed", "1"]) == 0
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert len(lines) == 10


def test_cli_udi_gs_escaped(capsys):
    assert main(["run", "udi", "--count", "1", "--set", "with_gs=true", "--seed", "3"]) == 0
    line = capsys.readouterr().out.strip()
    assert "\\x1d" in line
    assert "\x1d" not in line


def test_cli_run_json_values_match_display(capsys):
    assert main(["run", "udi", "--count", "3", "--format", "json", "--seed", "4"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] == 3
    assert len(payload["values"]) == len(payload["display_values"]) == 3


def test_catalog_every_item_has_schema():
    items = catalog()
    assert len(items) >= 40
    for item in items:
        assert item["id"]
        assert item["name"]
        assert item["category"]
        assert "params_schema" in item
        assert item["params_schema"].get("type") == "object"
        props = item["params_schema"].get("properties") or {}
        assert "count" not in props
