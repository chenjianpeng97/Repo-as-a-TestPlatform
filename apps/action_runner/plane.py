"""Import-safe Plane registration for action_runner.

Do not import ``packages.action_words`` here — index_platform discover() loads
this module.
"""
from __future__ import annotations

import argparse

from apps._shared.plane_app import register_plane_app

CATEGORIES: tuple[tuple[str, str, bool, int], ...] = (
    ("db_seed", "DB seed", True, 300),
    ("db_assert", "DB assert", False, 180),
    ("api_request", "API request", True, 180),
    ("api_assert", "API assert", False, 180),
    ("ui_action", "UI action", True, 300),
    ("ui_assert", "UI assert", False, 180),
)

MODULE = "apps.action_runner"
README = "apps/action_runner/README.md"


def build_run_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m apps.action_runner",
        description="Run one packages.action_words word as a Plane job.",
    )
    parser.add_argument(
        "--expect-category",
        required=True,
        help="category lock from Plane app_id (not a user-facing param)",
    )
    parser.add_argument("word_id", help="registered word id, e.g. db_seed.create_example")
    parser.add_argument(
        "--params",
        default="{}",
        help="JSON object of word params (default {})",
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="run with the word's example_params",
    )
    return parser


def _register_categories() -> None:
    for app_id, name, destructive, timeout in CATEGORIES:
        register_plane_app(
            build_run_parser,
            app_id=app_id,
            name=name,
            module=MODULE,
            argv=["python", "-m", MODULE, "run", "--expect-category", app_id],
            destructive=destructive,
            timeout=timeout,
            json_params=("params",),
            hide_params=("expect_category",),
            word_id_pattern=rf"^{app_id}\.[a-z][a-z0-9_]*$",
            readme_path=README,
        )


_register_categories()
