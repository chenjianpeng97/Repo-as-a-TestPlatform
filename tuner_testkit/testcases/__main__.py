"""CLI: python -m tuner_testkit.testcases [assets/testcases]."""

from __future__ import annotations

import sys
from pathlib import Path

from tuner_testkit.testcases.validate import validate_tree


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    target = Path(args[0] if args else "assets/testcases")
    errors = validate_tree(target)
    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        print(f"{len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"ok {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
