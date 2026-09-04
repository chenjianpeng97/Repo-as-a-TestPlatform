"""Project-root resolution for the installed kit."""

from __future__ import annotations

from pathlib import Path

import pytest

from tuner_testkit.project import (
    ProjectRootError,
    project_root,
    reset_path_cache,
    template_source_root,
)


def test_project_root_from_cwd(monkeypatch):
    reset_path_cache()
    monkeypatch.delenv("TUNER_ROOT", raising=False)
    monkeypatch.chdir(Path(__file__).resolve().parents[2])
    root = project_root()
    assert (root / "pyproject.toml").is_file()
    assert (root / "packages").is_dir()


def test_tuner_root_override(tmp_path, monkeypatch):
    reset_path_cache()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "packages").mkdir()
    monkeypatch.setenv("TUNER_ROOT", str(tmp_path))
    assert project_root() == tmp_path.resolve()


def test_missing_root_raises(tmp_path, monkeypatch):
    reset_path_cache()
    monkeypatch.delenv("TUNER_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ProjectRootError):
        project_root(cwd=tmp_path)


def test_template_source_root_finds_this_repo():
    found = template_source_root()
    assert found is not None
    assert (found / "tuner_testkit" / "project.py").is_file()
    assert (found / ".cursor" / "rules").is_dir()
