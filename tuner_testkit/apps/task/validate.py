"""Deterministic checks for task files and test-design documents."""

from __future__ import annotations

from pathlib import Path

from tuner_testkit.catalog.front_matter import parse_front_matter, split_front_matter

TESTDESIGN_HEADINGS = (
    "范围",
    "不测",
    "风险",
    "策略",
    "点击路径",
    "用例大纲",
    "执行反馈",
    "证据与来源",
)


def validate_testdesign(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    meta = parse_front_matter(text)
    _, body = split_front_matter(text)
    errors: list[str] = []
    if meta.get("kind") != "testdesign":
        errors.append("front-matter kind must be testdesign")
    for title in TESTDESIGN_HEADINGS:
        if f"## {title}" not in body:
            errors.append(f"missing heading ## {title}")
    evidence = meta.get("evidence")
    source = meta.get("source")
    has_evidence = bool(evidence) if not isinstance(evidence, list) else len(evidence) > 0
    if not has_evidence and not source:
        errors.append("front-matter needs evidence or source")
    return errors


def validate_task_meta(meta: dict) -> list[str]:
    errors: list[str] = []
    if meta.get("kind") != "task":
        errors.append("kind must be task")
    if meta.get("type") not in {"explore", "test-design", "test-execution"}:
        errors.append("type is not a known task type")
    if meta.get("type") == "test-execution" and not meta.get("design"):
        errors.append("test-execution task needs design")
    return errors
