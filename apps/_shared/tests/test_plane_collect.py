"""Tests for Plane asset file discovery (API / page marks)."""
from __future__ import annotations

from pathlib import Path

from apps._shared.plane_asset import collect_plane_api_objects, collect_plane_page_objects


def test_collect_skips_unmarked_helpers(tmp_path: Path) -> None:
    pkg = tmp_path / "packages" / "api_objects"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "helpers.py").write_text("HELPER = True\n", encoding="utf-8")
    (pkg / "create_invoice.py").write_text(
        "from packages.api_objects.plane import plane_apiobject\n"
        "\n"
        "class _Model:\n"
        "    method = 'POST'\n"
        "    path = '/invoices'\n"
        "    name = 'create invoice'\n"
        "    id = 'create_invoice'\n"
        "\n"
        "CREATE = plane_apiobject(_Model())\n",
        encoding="utf-8",
    )
    rows = collect_plane_api_objects(tmp_path)
    files = {row["file"] for row in rows}
    assert "packages/api_objects/create_invoice.py" in files
    assert "packages/api_objects/helpers.py" not in files


def test_collect_page_objects_skips_broken_init(tmp_path: Path) -> None:
    pkg = tmp_path / "packages" / "page_objects"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("from .pages import Pages\n", encoding="utf-8")
    (pkg / "login.py").write_text(
        "from packages.page_objects.plane import plane_pageobject\n"
        "\n"
        "@plane_pageobject\n"
        "class LoginPage:\n"
        "    pass\n",
        encoding="utf-8",
    )
    rows = collect_plane_page_objects(tmp_path)
    assert any(row["name"] == "LoginPage" for row in rows)
