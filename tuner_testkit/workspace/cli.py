"""CLI: ``tuner-workspace`` / ``python -m tuner_testkit.workspace``.

    tuner-workspace catalog [--out artifacts/catalogs/workspace.json | --out -] [--root DIR] [--no-kit-tools]
    tuner-workspace index render|check [--file INDEX.project.md] [--root DIR]
    tuner-workspace run <tool_id> [--params JSON | --params-file F] [--confirm] [--root DIR]
    tuner-workspace meta stamp <path> [--author EMAIL] [--root DIR]

All sub-commands print JSON to stdout (``--out -`` for catalog) and log via
``tuner_testkit.logging``; nothing touches the SUT or git history.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tuner_testkit.catalog.build import DEFAULT_CATALOG_REL, build_catalog, write_catalog
from tuner_testkit.logging import log_error


def _resolve_root(raw: str | None) -> Path:
    if raw:
        return Path(raw).resolve()
    from tuner_testkit.project import project_root

    return project_root()


def _print_json(payload: object) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    sys.stdout.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tuner-workspace",
        description="Deterministic workspace operations: catalog, index auto-zones, tool runs, metadata stamps.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    cat = sub.add_parser("catalog", help="scan the workspace into artifacts/catalogs/workspace.json")
    cat.add_argument("--out", default=None, help=f"output path (default {DEFAULT_CATALOG_REL}); '-' for stdout")
    cat.add_argument("--root", default=None, help="workspace root (default: tuner project_root())")
    cat.add_argument("--no-kit-tools", action="store_true", help="list only apps/ tools, not kit tool manifests")

    idx = sub.add_parser("index", help="render or check INDEX auto zones from the catalog")
    idx.add_argument("action", choices=("render", "check"))
    idx.add_argument("--file", default=None, help="index file (default: INDEX.project.md if present else INDEX.md)")
    idx.add_argument("--root", default=None)

    if _has_module("tuner_testkit.tools.runner"):
        run = sub.add_parser("run", help="run a tool or action word by id with JSON params (writes artifacts/runs/<run_id>/)")
        run.add_argument("tool_id", help="tool_id from the catalog, or an action word id such as db_seed.xxx")
        run.add_argument("--params", default=None, help="JSON object of parameters")
        run.add_argument("--params-file", default=None, help="path to a JSON file of parameters")
        run.add_argument("--confirm", action="store_true", help="required for destructive tools")
        run.add_argument("--run-id", default=None, help="override the generated run id")
        run.add_argument("--timeout", type=int, default=None, help="override the tool timeout (seconds)")
        run.add_argument("--root", default=None)

    if _has_module("tuner_testkit.workspace.meta"):
        meta = sub.add_parser("meta", help="metadata helpers for front-matter")
        meta_sub = meta.add_subparsers(dest="meta_cmd", required=True)
        stamp = meta_sub.add_parser("stamp", help="write author/created/updated into a Markdown front-matter")
        stamp.add_argument("path", help="Markdown file to stamp")
        stamp.add_argument("--author", default=None, help="override author (default: git config user.email)")
        stamp.add_argument("--kind", default=None, help="set the `kind` field when absent (app / testreport / inbox …)")
        stamp.add_argument("--root", default=None)
    return parser


def _has_module(name: str) -> bool:
    import importlib.util

    return importlib.util.find_spec(name) is not None


def _cmd_catalog(ns: argparse.Namespace) -> int:
    root = _resolve_root(ns.root)
    payload = build_catalog(root, include_kit_tools=not ns.no_kit_tools)
    if ns.out in {"-"}:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
        return 0
    out = Path(ns.out) if ns.out else root / DEFAULT_CATALOG_REL
    if not out.is_absolute():
        out = root / out
    write_catalog(payload, out)
    _print_json({"written": str(out), "counts": payload["counts"]})
    return 0


def _cmd_index(ns: argparse.Namespace) -> int:
    from tuner_testkit.workspace.index_render import check_index, render_index

    root = _resolve_root(ns.root)
    if ns.action == "render":
        result = render_index(root, ns.file)
        _print_json(result)
        return 0
    result = check_index(root, ns.file)
    _print_json(result)
    return 0 if result["up_to_date"] else 1


def _cmd_run(ns: argparse.Namespace) -> int:
    from tuner_testkit.tools.runner import RunRequest, run_tool

    root = _resolve_root(ns.root)
    if ns.params_file:
        params = json.loads(Path(ns.params_file).read_text(encoding="utf-8"))
    else:
        params = json.loads(ns.params or "{}")
    result = run_tool(
        RunRequest(tool_id=ns.tool_id, params=params, confirm=ns.confirm, run_id=ns.run_id, timeout=ns.timeout),
        root=root,
    )
    _print_json(result.to_dict())
    return 0 if result.status == "succeeded" else 1


def _cmd_meta(ns: argparse.Namespace) -> int:
    from tuner_testkit.workspace.meta import stamp_file

    root = _resolve_root(ns.root)
    result = stamp_file(root, Path(ns.path), author=ns.author, kind=ns.kind)
    _print_json(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ns = build_parser().parse_args(argv)
    handlers = {"catalog": _cmd_catalog, "index": _cmd_index, "run": _cmd_run, "meta": _cmd_meta}
    try:
        return handlers[ns.cmd](ns)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        log_error("tuner-workspace failed", command=ns.cmd, error=f"{type(exc).__name__}: {exc}")
        sys.stderr.write(f"tuner-workspace {ns.cmd}: {type(exc).__name__}: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
