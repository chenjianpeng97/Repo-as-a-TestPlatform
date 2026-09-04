"""DNA overlay paths — Cursor rules/skills plus git hooks and specs."""

from __future__ import annotations

# Relative to the template source root (or a bundled payload that mirrors it).
DNA_PATHS: tuple[str, ...] = (
    ".cursor/rules",
    ".cursor/skills",
    ".cursor/agents",
    ".cursor/hooks",
    ".cursor/hooks.json",
    "docs/spec",
    "tools/git-hooks",
    "AGENTS.md",
)
