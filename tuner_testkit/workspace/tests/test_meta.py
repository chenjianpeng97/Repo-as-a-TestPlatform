from __future__ import annotations

from pathlib import Path

from tuner_testkit.catalog.front_matter import parse_front_matter
from tuner_testkit.workspace.meta import stamp_file


def test_stamp_writes_author_and_dates(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("tuner_testkit.workspace.meta.git_config_value", lambda root, key: "qa@example.com" if key == "user.email" else None)
    monkeypatch.setattr("tuner_testkit.workspace.meta.git_first_author", lambda root, rel: "qa@example.com")
    target = tmp_path / "note.md"
    target.write_text("# Hello\n\nbody\n", encoding="utf-8")
    result = stamp_file(tmp_path, target, kind="testreport", today="2026-09-22")
    assert result["author"] == "qa@example.com"
    assert result["kind"] == "testreport"
    assert result["written"] is True
    meta = parse_front_matter(target.read_text(encoding="utf-8"))
    assert meta["author"] == "qa@example.com"
    assert meta["created"] == "2026-09-22"
    assert meta["title"] == "Hello"
