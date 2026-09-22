from __future__ import annotations

from tuner_testkit.catalog.front_matter import (
    dump_front_matter,
    parse_front_matter,
    parse_yaml_block,
    replace_front_matter,
    split_front_matter,
)

DOC = """---
domain: platform
source: plan 2026-09-22
date: 2026-09-22
version: 1.0.0
confidence: high
tags: [dogfood, fixture]
evidence:
  - artifacts/evidence/a
  - artifacts/evidence/b
result: {total: 10, passed: 9, failed: 1}
nested:
  owner: qa@example.com
  flags:
    - x
---

# Title

body
"""


def test_parse_front_matter_subset() -> None:
    meta = parse_front_matter(DOC)
    assert meta["domain"] == "platform"
    assert meta["source"] == "plan 2026-09-22"
    assert meta["version"] == "1.0.0"
    assert meta["tags"] == ["dogfood", "fixture"]
    assert meta["evidence"] == ["artifacts/evidence/a", "artifacts/evidence/b"]
    assert meta["result"] == {"total": 10, "passed": 9, "failed": 1}
    assert meta["nested"] == {"owner": "qa@example.com", "flags": ["x"]}


def test_split_and_missing_front_matter() -> None:
    block, body = split_front_matter(DOC)
    assert block is not None and body.startswith("\n# Title")
    assert parse_front_matter("# no meta\n") == {}


def test_dump_round_trip_and_replace() -> None:
    data = {"kind": "app", "author": "qa@example.com", "tags": ["a", "b"], "version": "0.1.0", "ok": True, "n": 3}
    text = dump_front_matter(data)
    assert parse_yaml_block(text.strip().strip("-").strip()) == data
    replaced = replace_front_matter("# Hello\n", {"author": "x@y"})
    assert replaced.startswith("---\nauthor: x@y\n---\n")
    assert replaced.endswith("# Hello\n")
    again = replace_front_matter(replaced, {"author": "z@y", "kind": "app"})
    assert parse_front_matter(again) == {"author": "z@y", "kind": "app"}
    assert again.count("---") == 2
