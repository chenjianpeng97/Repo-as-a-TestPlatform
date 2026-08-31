"""Import-safe Plane registration.

``runtime="long_lived"`` — this is a resident service, not a job. Plane lists it
in the catalog (``plane_runnable`` stays False in ``spec_to_tool``) so the
platform knows the mock server exists and how to launch it, without a job
runner trying to execute it under a timeout.

Only the ``serve`` arguments are described here: ``seed`` / ``routes`` are local
maintenance commands. No fastapi/uvicorn import at module level.
"""
from __future__ import annotations

import argparse

from apps._shared.plane_app import plane_app

from .cli import DEFAULT_ADMIN_PREFIX, DEFAULT_HOST, DEFAULT_PORT


@plane_app(
    app_id="mock_server",
    name="API mock server",
    module="apps.mock_server",
    argv=["python", "-m", "apps.mock_server", "serve"],
    runtime="long_lived",
    expose=True,
    result="logs",
    timeout=0,
    readme_path="apps/mock_server/README.md",
)
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m apps.mock_server serve",
        description=(
            "Serve frozen api_objects routes from data/mocks definitions, with "
            "a control plane for redefining responses at runtime."
        ),
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="bind address")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="port")
    parser.add_argument("--mocks-dir", default=None, help="mock definitions dir (default data/mocks)")
    parser.add_argument(
        "--admin-prefix",
        default=DEFAULT_ADMIN_PREFIX,
        help="control-plane prefix",
    )
    parser.add_argument(
        "--no-assets",
        action="store_true",
        help="serve only data/mocks, skip packages/api_objects discovery",
    )
    return parser
