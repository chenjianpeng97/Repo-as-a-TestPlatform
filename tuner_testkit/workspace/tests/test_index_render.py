from __future__ import annotations

from pathlib import Path

from tuner_testkit.workspace.index_render import check_index, render_index, render_text

CATALOG = {
    "knowledge": {
        "ddl": [{"datasource": "main", "tables": ["orders"], "path": "assets/ddl/main", "table_count": 1}],
        "sql_files": [],
        "assets": [{"path": "assets/usecases/a.md", "category": "usecases", "domain": "d", "source": "s", "confidence": "high", "title": "A"}],
    },
    "api_objects": [{"method": "GET", "path": "/orders", "file": "packages/api_objects/orders/GET.v1.py"}],
    "page_objects": [],
    "action_words": [{"word_id": "db_seed.x", "name": "X", "category": "db_seed"}],
    "tools": [
        {"tool_id": "t", "origin": "workspace", "argv": ["python", "-m", "apps.t"], "summary": "T", "readme_path": "apps/t/README.md"},
        {"tool_id": "kit", "origin": "kit", "argv": ["x"], "summary": "K"},
    ],
    "tests": {"features": [{"path": "tests/features/a.feature", "scenarios": [{}, {}], "tags": ["x"]}]},
}

INDEX = """# idx

<!-- auto:begin:ddl -->
old
<!-- auto:end:ddl -->

manual text stays

<!-- auto:begin:apps -->
| a |
<!-- auto:end:apps -->

<!-- auto:begin:mystery -->
keep
<!-- auto:end:mystery -->
"""


def test_render_text_replaces_known_zones_only() -> None:
    new_text, rendered, unknown = render_text(INDEX, CATALOG)
    assert rendered == ["ddl", "apps"]
    assert unknown == ["mystery"]
    assert "manual text stays" in new_text
    assert "| `main` | `orders` | `assets/ddl/main` |" in new_text
    assert "| `t` | `python -m apps.t` | T | `apps/t/README.md` |" in new_text
    assert "`kit`" not in new_text  # kit tools are not workspace apps
    assert "keep" in new_text


def test_render_and_check_round_trip(tmp_path: Path) -> None:
    index = tmp_path / "INDEX.project.md"
    index.write_text(INDEX, encoding="utf-8")
    first = render_index(tmp_path, catalog=CATALOG)
    assert first["changed"] is True and first["zones"] == ["ddl", "apps"]
    assert check_index(tmp_path, catalog=CATALOG)["up_to_date"] is True
    second = render_index(tmp_path, catalog=CATALOG)
    assert second["changed"] is False
    stale = dict(CATALOG)
    stale["tools"] = []
    result = check_index(tmp_path, catalog=stale)
    assert result["up_to_date"] is False and result["stale_zones"] == ["apps"]
