"""CLI: regenerate or check .cursor/REGISTRY.md.

    python -m tuner_testkit.apps.index_ai            # regenerate REGISTRY.md
    python -m tuner_testkit.apps.index_ai --check    # exit 1 if REGISTRY.md is stale
"""
from __future__ import annotations

import argparse
import sys

from tuner_testkit.apps.index_ai import registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tuner_testkit.apps.index_ai",
        description="Scan .cursor/** and render .cursor/REGISTRY.md (AI component registry).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if REGISTRY.md is out of date",
    )
    args = parser.parse_args(argv)

    if args.check:
        if registry.is_current():
            print("REGISTRY.md is up to date.")
            return 0
        print(
            "REGISTRY.md is stale — run `python -m tuner_testkit.apps.index_ai` to regenerate.",
            file=sys.stderr,
        )
        return 1

    path = registry.write()
    print(f"Wrote {path.relative_to(registry._repo_root())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
