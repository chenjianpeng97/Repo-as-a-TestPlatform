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
    assert (dest / "config" / "env.py").is_file()
    assert (dest / "packages" / "action_words" / "__init__.py").is_file()
    assert (dest / ".cursor" / "rules").is_dir()
    assert any(line.startswith("copy config/env.py") for line in actions)
    assert any("dna sync (exit 0)" in line for line in actions)


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
    assert any(line.startswith("copy config/env.py") for line in actions)
    assert any("dna sync (exit 0)" in line for line in actions)
