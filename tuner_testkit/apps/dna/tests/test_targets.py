"""tuner-dna --ide targets: render Cursor DNA into other IDE layouts."""
from __future__ import annotations

from pathlib import Path

import pytest

from tuner_testkit.apps.dna import targets as t
from tuner_testkit.apps.dna.cli import main

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_parse_targets() -> None:
    assert t.parse_targets(None) == ["cursor"]
    assert t.parse_targets("claude,codex") == ["claude", "codex"]
    assert t.parse_targets("all") == list(t.ALL_TARGETS)
    with pytest.raises(ValueError):
        t.parse_targets("vim")


def test_render_cursor_is_verbatim_dna() -> None:
    files = t.render_target(REPO_ROOT, "cursor")
    assert ".cursor/rules/commit-convention.mdc" in files
    assert "AGENTS.md" in files and "tools/git-hooks/commit-msg" in files


def test_render_claude_layout() -> None:
    files = t.render_target(REPO_ROOT, "claude")
    assert ".claude/skills/create-app/SKILL.md" in files
    assert ".claude/agents/sut-self-learning.md" in files
    assert not any(rel.startswith(".cursor/") for rel in files)  # nothing Cursor-shaped leaks
    assert not any(rel.endswith("hooks.json") for rel in files)  # hook schemas are not translated
    claude_md = files["CLAUDE.md"].decode("utf-8")
    assert "@AGENTS.md" in claude_md
    assert "### commit-convention" in claude_md  # always-on rule inlined
    assert "`apps-authoring`" in claude_md  # glob rule listed with its path
    agent = files[".claude/agents/sut-self-learning.md"].decode("utf-8")
    assert agent.startswith("---\nname: sut-self-learning\n")


def test_render_agents_and_codex_alias() -> None:
    agents = t.render_target(REPO_ROOT, "agents")
    codex = t.render_target(REPO_ROOT, "codex")
    assert ".agents/skills/maintain-index/SKILL.md" in agents
    assert agents == codex
    assert "CLAUDE.md" not in agents


def test_sync_and_check_cli_with_ide(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("TUNER_DNA_ROOT", str(REPO_ROOT))
    assert main(["sync", "--target", str(tmp_path), "--ide", "claude,agents"]) == 0
    assert (tmp_path / "CLAUDE.md").is_file()
    assert (tmp_path / ".claude" / "skills" / "dump-ddl" / "SKILL.md").is_file()
    assert (tmp_path / ".agents" / "skills" / "dump-ddl" / "SKILL.md").is_file()
    assert not (tmp_path / ".cursor").exists()  # cursor not requested
    assert main(["check", "--target", str(tmp_path), "--ide", "claude"]) == 0
    (tmp_path / "CLAUDE.md").write_text("edited\n", encoding="utf-8")
    assert main(["check", "--target", str(tmp_path), "--ide", "claude"]) == 1
    assert main(["sync", "--target", str(tmp_path), "--ide", "claude", "--overwrite"]) == 0
    assert main(["check", "--target", str(tmp_path), "--ide", "claude"]) == 0
    assert main(["targets"]) == 0
