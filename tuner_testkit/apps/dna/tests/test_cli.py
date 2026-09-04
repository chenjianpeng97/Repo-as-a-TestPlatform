"""DNA sync copies overlay files into a target project."""

from __future__ import annotations

from pathlib import Path

from tuner_testkit.apps.dna.cli import main


def test_dna_sync_and_check(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\nversion='0'\n\n[tool.tuner-testkit]\n",
        encoding="utf-8",
    )
    (tmp_path / "packages").mkdir()
    assert main(["sync", "--target", str(tmp_path)]) == 0
    assert (tmp_path / ".cursor" / "rules").is_dir()
    assert (tmp_path / "docs" / "spec").is_dir()
    assert (tmp_path / "tools" / "git-hooks" / "commit-msg").is_file()
    assert (tmp_path / ".tuner-dna-version").is_file()
    assert main(["check", "--target", str(tmp_path)]) == 0
