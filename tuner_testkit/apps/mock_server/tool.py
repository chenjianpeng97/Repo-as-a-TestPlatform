"""Import-safe tool manifest for the mock server.

``runtime="long_lived"`` — this is a resident service, not a job: the catalog
and the workbench list it and know how to launch it, but never run it under a
job timeout. Only the ``serve`` arguments are described here; ``seed`` /
``routes`` are local maintenance commands. No fastapi/uvicorn import here.
"""
from __future__ import annotations

import argparse

from tuner_testkit.tools import tool

from .cli import DEFAULT_ADMIN_PREFIX, DEFAULT_HOST, DEFAULT_PORT


@tool(
    tool_id="mock_server",
    name="API mock server",
    summary="Serve frozen api_objects routes from data/mocks with a runtime control plane.",
    group="services",
    module="tuner_testkit.apps.mock_server",
    argv=["python", "-m", "tuner_testkit.apps.mock_server", "serve"],
    runtime="long_lived",
    timeout=0,
    readme_path="tuner_testkit/apps/mock_server/README.md",
)
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tuner_testkit.apps.mock_server serve",
        description=(
            "Serve frozen api_objects routes from data/mocks definitions, with "
            "a control plane for redefining responses at runtime."
        ),
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="bind address")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="port")
    parser.add_argument("--mocks-dir", default=None, help="mock definitions dir (default data/mocks)")
    parser.add_argument("--admin-prefix", default=DEFAULT_ADMIN_PREFIX, help="control-plane prefix")
    parser.add_argument(
        "--no-assets",
        action="store_true",
        help="serve only data/mocks, skip packages/api_objects discovery",
    )
    return parser
