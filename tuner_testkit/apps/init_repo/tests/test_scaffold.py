"""scaffold must work from a blank cwd (uv tool install, no SUT yet)."""

from __future__ import annotations

from pathlib import Path

from tuner_testkit.apps.init_repo.scaffold import scaffold

_REPO_ROOT = Path(__file__).resolve().parents[4]
_STUB_ENV = Path(__file__).resolve().parents[1] / "stubs" / "config" / "env.py"


def _forbid_project_root(*_args, **_kwargs):
    raise AssertionError("scaffold must not call project_root()")


def test_scaffold_from_non_project_cwd(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("tuner_testkit.project.project_root", _forbid_project_root)
    dest = tmp_path / "new-sut"
    actions = scaffold(dest, with_ai=True, overwrite=False)
    assert dest.is_dir()
    assert (dest / "pyproject.toml").is_file()
    assert "[tool.tuner-testkit]" in (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.12,<3.14"' in (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert (dest / ".python-version").read_text(encoding="utf-8") == "3.12\n"
    assert (dest / "config" / "env.py").is_file()
    assert (dest / "packages" / "action_words" / "__init__.py").is_file()
    assert (dest / ".cursor" / "rules").is_dir()
    assert (dest / "artifacts" / "inbox").is_dir()
    assert (dest / "data" / "sut-accounts.example.yaml").is_file()
    assert "replace-me" in (dest / "data" / "sut-accounts.example.yaml").read_text(encoding="utf-8")
    assert any(line.startswith("copy config/env.py") for line in actions)
    assert any("dna sync (exit 0)" in line for line in actions)
    # 5.x stubs: gitignore, project index with auto fences, behave environments + G/W/T steps, pytest conftest
    assert "artifacts/runs/" in (dest / ".gitignore").read_text(encoding="utf-8")
    assert "<!-- auto:begin:apps -->" in (dest / "INDEX.project.md").read_text(encoding="utf-8")
    for stage in ("api", "ui"):
        assert "report_run_begin" in (dest / "tests" / "features" / f"{stage}_environment.py").read_text(encoding="utf-8")
        for kind in ("given", "when", "then"):
            assert (dest / "tests" / "features" / f"{stage}_steps" / f"{kind}.py").is_file()
    assert (dest / "tests" / "pytest" / "conftest.py").is_file()
    assert not (dest / "packages" / "api_objects" / "plane.py").exists()
    assert (dest / ".cursor" / "REGISTRY.md").is_file()
    assert any(line.startswith("write .cursor/REGISTRY.md") for line in actions)


def test_scaffold_uses_packaged_stubs_when_not_editable(tmp_path: Path, monkeypatch):
    """Simulate `uv tool install` (no template checkout beside site-packages)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("tuner_testkit.project.template_source_root", lambda: None)
    monkeypatch.setattr("tuner_testkit.project.project_root", _forbid_project_root)
    monkeypatch.setenv("TUNER_DNA_ROOT", str(_REPO_ROOT))
    dest = tmp_path / "from-wheel"
    actions = scaffold(dest, with_ai=True, overwrite=False)
    assert _STUB_ENV.is_file()
    assert (dest / "config" / "env.py").read_text(encoding="utf-8") == _STUB_ENV.read_text(
        encoding="utf-8"
    )
    assert (dest / "artifacts" / "inbox").is_dir()
    assert (dest / "data" / "sut-accounts.example.yaml").is_file()
    assert any(line.startswith("copy config/env.py") for line in actions)
    assert any("dna sync (exit 0)" in line for line in actions)
