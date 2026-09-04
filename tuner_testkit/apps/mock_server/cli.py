"""CLI for the api_mock server.

    python -m tuner_testkit.apps.mock_server serve --port 8931
    python -m tuner_testkit.apps.mock_server seed --dry-run
    python -m tuner_testkit.apps.mock_server routes

Import-safe on purpose: ``build_parser`` must be reachable from
``tuner_testkit/apps/mock_server/plane.py`` without importing fastapi/uvicorn, so the Plane
catalog scan works whether or not the ``mock`` extra is installed. Heavy
imports live inside the command handlers.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tuner_testkit.logging import log_info

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8931
DEFAULT_ADMIN_PREFIX = "/__mock__"


def _repo_root() -> Path:
    from tuner_testkit.project import project_root

    return project_root()


def _default_mocks_dir() -> str:
    from tuner_testkit.project import mocks_dir

    return str(mocks_dir())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tuner_testkit.apps.mock_server",
        description=(
            "Serve packages/api_objects routes with canned responses from "
            "data/mocks, and expose a control plane so a test platform can "
            "redefine status / headers / body at runtime."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_serve = sub.add_parser("serve", help="Start the mock HTTP server")
    p_serve.add_argument("--host", default=DEFAULT_HOST, help=f"Bind address (default {DEFAULT_HOST})")
    p_serve.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port (default {DEFAULT_PORT})")
    p_serve.add_argument("--mocks-dir", default=None, help="Mock definitions dir (default data/mocks)")
    p_serve.add_argument(
        "--admin-prefix",
        default=DEFAULT_ADMIN_PREFIX,
        help=f"Control-plane prefix (default {DEFAULT_ADMIN_PREFIX})",
    )
    p_serve.add_argument(
        "--no-assets",
        action="store_true",
        help="Skip loading packages/api_objects; serve only what data/mocks defines",
    )
    p_serve.add_argument(
        "--max-request-log",
        type=int,
        default=200,
        help="How many received requests to keep in memory (default 200)",
    )
    p_serve.add_argument("--log-level", default="info", help="uvicorn log level (default info)")

    p_seed = sub.add_parser("seed", help="Generate data/mocks entries from frozen api_objects")
    p_seed.add_argument("--mocks-dir", default=None, help="Output dir (default data/mocks)")
    p_seed.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing mock files (default: keep them and skip)",
    )
    p_seed.add_argument("--dry-run", action="store_true", help="Report what would be written, write nothing")

    p_routes = sub.add_parser("routes", help="List discovered assets and their mock state")
    p_routes.add_argument("--mocks-dir", default=None, help="Mock definitions dir (default data/mocks)")
    p_routes.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON instead of a table")

    return parser


def _cmd_serve(args: argparse.Namespace) -> int:
    try:
        import uvicorn
    except ModuleNotFoundError:
        print(
            "mock server needs the 'mock' extra: uv sync --extra mock",
            file=sys.stderr,
        )
        return 2

    from tuner_testkit.api_mock import create_app

    mocks_dir = args.mocks_dir or _default_mocks_dir()
    app = create_app(
        mocks_dir=mocks_dir,
        load_models=not args.no_assets,
        admin_prefix=args.admin_prefix,
        max_request_log=args.max_request_log,
    )

    base = f"http://{args.host}:{args.port}"
    print(f"api_mock serving on {base}")
    print(f"  control plane : {base}{args.admin_prefix}/routes")
    print(f"  openapi docs  : {base}{args.admin_prefix}/docs")
    print(f"  definitions   : {mocks_dir}")
    print(f"  point tests at it with TEST_BASE_URL={base}")
    # uvicorn.run blocks; without an explicit flush the banner sits in the
    # block-buffered pipe and the user sees nothing until shutdown.
    sys.stdout.flush()
    log_info("api_mock serve", host=args.host, port=args.port, mocks_dir=str(mocks_dir))

    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)
    return 0


def _cmd_seed(args: argparse.Namespace) -> int:
    from tuner_testkit.apps.mock_server.seed import seed_mocks

    mocks_dir = args.mocks_dir or _default_mocks_dir()
    report = seed_mocks(mocks_dir, overwrite=args.overwrite, dry_run=args.dry_run)

    verb = "would write" if args.dry_run else "wrote"
    print(f"{verb} {len(report.created)} mock definition(s) under {mocks_dir}")
    print(f"  from recorded samples : {report.from_recording}")
    print(f"  from response_hints   : {report.from_hints}")
    if report.skipped:
        print(f"  skipped (exists)      : {len(report.skipped)}  (use --overwrite to replace)")
    if report.failed:
        print(f"  failed                : {len(report.failed)}")
        for item in report.failed:
            print(f"    - {item}")
    if report.from_recording:
        print(
            "note: recorder samples are truncated (5 list items, depth 6); "
            "treat seeded bodies as a starting point."
        )
    return 1 if report.failed else 0


def _cmd_routes(args: argparse.Namespace) -> int:
    from tuner_testkit.api_mock import MockStore
    from packages.api_objects.registry import iter_api_models

    store = MockStore(args.mocks_dir or _default_mocks_dir())
    store.reload()

    rows = []
    seen: set[str] = set()
    for ref in iter_api_models():
        route = store.get(ref.model.method, ref.model.path)
        seen.add(ref.route_key)
        rows.append(
            {
                "method": ref.model.method.upper(),
                "path": ref.model.path,
                "mock": bool(route),
                "active": route.active if route else None,
                "scenarios": sorted(route.scenarios) if route else [],
                "asset": ref.file,
            }
        )
    for route in store.routes():
        if route.route_key in seen:
            continue
        rows.append(
            {
                "method": route.method,
                "path": route.path,
                "mock": True,
                "active": route.active,
                "scenarios": sorted(route.scenarios),
                "asset": None,
            }
        )

    if args.as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    if not rows:
        print("no api_objects assets and no mock definitions found")
        return 0
    width = max(len(f"{r['method']} {r['path']}") for r in rows)
    print(f"{'ROUTE'.ljust(width)}  MOCK  ACTIVE      SCENARIOS")
    for row in rows:
        label = f"{row['method']} {row['path']}".ljust(width)
        mark = "yes " if row["mock"] else "no  "
        active = (row["active"] or "-").ljust(10)
        print(f"{label}  {mark}  {active}  {','.join(row['scenarios']) or '-'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = build_parser().parse_args(argv)
    handlers = {
        "serve": _cmd_serve,
        "seed": _cmd_seed,
        "routes": _cmd_routes,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
