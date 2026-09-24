"""CLI: persist / list sanitized MCP evidence under artifacts/evidence/<run_id>/.

    python -m tuner_testkit.apps.evidence persist --run-id ID --scenario explore:x --network captures.jsonl
    python -m tuner_testkit.apps.evidence routes --run-id ID
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tuner_testkit.logging import log_error
from tuner_testkit.project import ensure_project_on_path, project_root

from .persist import attach, load_jsonl, load_run, persist


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tuner_testkit.apps.evidence",
        description=(
            "Sanitize Playwright MCP / network dumps and persist them under "
            "artifacts/evidence/<run_id>/ as JSON (LLM-consumable)."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    persist_p = sub.add_parser("persist", help="write sanitized evidence for one run")
    persist_p.add_argument("--run-id", required=True, help="ASCII run id, e.g. 20260913T134137Z-issue-slice")
    persist_p.add_argument("--scenario", required=True, help="scenario_id or explore:<intent>")
    persist_p.add_argument("--network", required=True, type=Path, help="JSONL of captures (one object per line)")
    persist_p.add_argument("--actions", type=Path, default=None, help="optional actions JSONL")
    persist_p.add_argument("--intent", default="", help="short intent blurb for generated run_summary.md")
    persist_p.add_argument("--summary", type=Path, default=None, help="optional run_summary.md to copy")
    persist_p.add_argument("--task-id", default="", help="work task id, stored on the run manifest")
    persist_p.add_argument("--screenshot", type=Path, action="append", default=[], help="image copied under screenshots/")
    persist_p.add_argument("--log", type=Path, action="append", default=[], help="log excerpt, redacted, under logs/")
    persist_p.add_argument("--api", type=Path, action="append", default=[], help="JSON response, sanitized, under api/")
    persist_p.add_argument(
        "--root",
        type=Path,
        default=None,
        help="project root (default: tuner project_root())",
    )

    attach_p = sub.add_parser("attach", help="add screenshots, logs, or API JSON to a run")
    attach_p.add_argument("--run-id", required=True)
    attach_p.add_argument("--scenario", default="attach")
    attach_p.add_argument("--intent", default="")
    attach_p.add_argument("--task-id", default="")
    attach_p.add_argument("--screenshot", type=Path, action="append", default=[])
    attach_p.add_argument("--log", type=Path, action="append", default=[])
    attach_p.add_argument("--api", type=Path, action="append", default=[])
    attach_p.add_argument("--root", type=Path, default=None)

    routes_p = sub.add_parser("routes", help="print unique method+path from an existing run")
    routes_p.add_argument("--run-id", required=True)
    routes_p.add_argument("--root", type=Path, default=None)
    return parser


def _print_json(payload: object) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, default=str))
    sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ns = build_parser().parse_args(argv)
    root = ns.root
    if root is None:
        ensure_project_on_path()
        root = project_root()
    try:
        if ns.cmd == "persist":
            captures = load_jsonl(ns.network)
            actions = load_jsonl(ns.actions) if ns.actions else None
            summary = ns.summary.read_text(encoding="utf-8") if ns.summary else None
            payload = persist(
                run_id=ns.run_id,
                scenario_id=ns.scenario,
                captures=captures,
                actions=actions,
                intent=ns.intent,
                summary_text=summary,
                root=root,
                task_id=ns.task_id,
                screenshots=ns.screenshot,
                logs=ns.log,
                apis=ns.api,
            )
            _print_json(payload)
            return 0
        if ns.cmd == "attach":
            _print_json(attach(
                run_id=ns.run_id,
                root=root,
                scenario_id=ns.scenario,
                intent=ns.intent,
                task_id=ns.task_id,
                screenshots=ns.screenshot,
                logs=ns.log,
                apis=ns.api,
            ))
            return 0
        if ns.cmd == "routes":
            _print_json(load_run(ns.run_id, root=root))
            return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        log_error("evidence cli failed", error=f"{type(exc).__name__}: {exc}")
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
