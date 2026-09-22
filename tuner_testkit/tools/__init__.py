"""Tool manifests: describe a CLI tool (``apps/<name>`` or a kit app) so the
workspace catalog, the local workbench and any future runner can list it,
render its parameters as a form and rebuild the command line.

Public surface::

    from tuner_testkit.tools import tool, discover, export_tools, get_tool, build_argv

``@tool`` decorates an import-safe ``build_parser()`` factory in
``apps/<name>/tool.py`` (or ``tuner_testkit/apps/<name>/tool.py``). The
argparse parser is introspected into a JSON Schema (``params_schema``) plus an
``argv_plan`` that maps schema keys back onto CLI flags.
"""
from __future__ import annotations

from tuner_testkit.tools.manifest import (
    RuntimeKind,
    ToolSpec,
    Visibility,
    build_argv,
    discover,
    export_tools,
    get_tool,
    register_tool,
    reset_registry_for_tests,
    spec_to_dict,
    tool,
    validate_params,
)

__all__ = [
    "RuntimeKind",
    "ToolSpec",
    "Visibility",
    "build_argv",
    "discover",
    "export_tools",
    "get_tool",
    "register_tool",
    "reset_registry_for_tests",
    "spec_to_dict",
    "tool",
    "validate_params",
]
