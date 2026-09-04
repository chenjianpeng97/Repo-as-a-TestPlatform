"""CLI 离线：--help / 参数校验（不启 headed 浏览器）。"""
from __future__ import annotations

from pathlib import Path

import pytest

from tuner_testkit.apps.page_recorder.cli import build_parser, main
from tuner_testkit.apps.page_recorder.session import resolve_start_url


def test_help_exits_zero():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0


def test_app_is_required():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_main_help():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_resolve_start_url_joins_relative(monkeypatch):
    monkeypatch.setattr(
        "tuner_testkit.config.get_ui_base_url",
        lambda: "https://plane.example",
    )
    assert resolve_start_url("/sign-in") == "https://plane.example/sign-in"
    assert resolve_start_url("https://other.example/x") == "https://other.example/x"


def test_resolve_start_url_requires_base(monkeypatch):
    monkeypatch.setattr("tuner_testkit.config.get_ui_base_url", lambda: "")
    with pytest.raises(SystemExit, match="TEST_UI_BASE_URL"):
        resolve_start_url(None)


def test_changelog_appended(tmp_path: Path):
    from tuner_testkit.apps.page_recorder.cli import _write_changelog

    _write_changelog(tmp_path, app="plane", items=["plane.sign_in@v1"])
    text = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "page_recorder" in text
    assert "plane.sign_in@v1" in text
    assert "record-pages" in text
