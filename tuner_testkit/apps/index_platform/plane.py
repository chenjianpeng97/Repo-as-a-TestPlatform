"""Import-safe Plane registration. expose=False — Sync is the only runner."""
from __future__ import annotations

import argparse

from tuner_testkit.apps._shared.plane_app import plane_app


@plane_app(
    app_id="index_platform",
    name="Index platform catalog",
    module="apps.index_platform",
    argv=["python", "-m", "apps.index_platform", "--out", "-"],
    expose=False,
    result="catalog_json",
    timeout=180,
    readme_path="tuner_testkit/apps/index_platform/README.md",
)
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tuner_testkit.apps.index_platform",
        description="Scan the test repo and print a catalog JSON for Plane.",
    )
    parser.add_argument(
        "--out",
        default="-",
        help="output path, or '-' for stdout (Plane Sync uses '-')",
    )
    return parser
