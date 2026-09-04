#!/usr/bin/env python
"""afterFileEdit hook: keep .cursor/REGISTRY.md in sync with .cursor/** edits.

When an edit touches a rule / skill / agent / hooks.json, regenerate the
registry deterministically via ``apps.index_ai``. Fail-open: any error exits 0
so it never blocks edits. Skips edits to REGISTRY.md itself to avoid loops.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

_TRIGGERS = (".cursor/rules", ".cursor/skills", ".cursor/agents", ".cursor/hooks.json")


def main() -> int:
    try:
        raw = sys.stdin.read()
    except Exception:  # noqa: BLE001 -- hook must never block
        return 0

    norm = raw.replace("\\\\", "/").replace("\\", "/")
    if "REGISTRY.md" in norm:
        return 0
    if not any(t in norm for t in _TRIGGERS):
        return 0

    try:
        subprocess.run(
            [sys.executable, "-m", "tuner_testkit.apps.index_ai"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            timeout=30,
            check=False,
        )
    except Exception:  # noqa: BLE001 -- fail open
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
