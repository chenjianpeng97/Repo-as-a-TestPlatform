"""CLI: python -m tuner_testkit.apps.index_platform --out -"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from tuner_testkit.apps.index_platform.build import build_catalog
from tuner_testkit.apps.index_platform.plane import build_parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ns = build_parser().parse_args(argv)
    payload = build_catalog()
    text = json.dumps(payload, ensure_ascii=False, default=str)
    if ns.out in {"-", ""}:
        sys.stdout.write(text)
        sys.stdout.write("\n")
        return 0
    path = Path(ns.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
