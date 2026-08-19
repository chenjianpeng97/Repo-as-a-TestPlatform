"""CLI: python -m apps.action_runner run --expect-category <cat> <word_id> [--params JSON] [--example]"""
from __future__ import annotations

import json
import sys

from apps.action_runner.plane import build_run_parser
from apps.action_runner.run import ActionRunnerError, parse_params_json, run_word


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print(
            "usage: python -m apps.action_runner run --expect-category <category> "
            "<word_id> [--params JSON] [--example]",
            file=sys.stderr,
        )
        return 0 if args and args[0] in {"-h", "--help"} else 2
    if args[0] != "run":
        print(f"unknown command {args[0]!r} (only 'run' is supported)", file=sys.stderr)
        return 2

    parser = build_run_parser()
    ns = parser.parse_args(args[1:])
    try:
        params = {} if ns.example else parse_params_json(ns.params)
        exit_code, payload = run_word(
            ns.word_id,
            expect_category=ns.expect_category,
            params=params,
            example=bool(ns.example),
        )
    except ActionRunnerError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    except KeyError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(payload, ensure_ascii=False, default=str))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
