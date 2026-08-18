"""Portable logging kit for tests and CLI tools.

Works with behave (via optional ``hooks``), pytest, and plain scripts.
Typical imports::

    from packages.logging import (
        get_logger,
        log_data_setup, log_api_call, log_ui_action, log_assertion,
        log_info, log_warn, log_error,
    )
    from packages.logging import hooks as log_hooks  # behave environments only

See ``packages/logging/README.md`` for the end-to-end integration guide.

Note: the package is named ``logging`` on purpose so callers read naturally
(``from packages.logging import ...``). Python 3's absolute-import rule means
internal ``import logging`` statements still reach the stdlib module; we
never shadow it.
"""
from __future__ import annotations

from . import hooks as hooks  # noqa: F401 -- public submodule re-export
from .core import (
    get_log_file_path,
    get_logger,
    log_dir,
)
from .helpers import (
    log_api_call,
    log_assertion,
    log_data_setup,
    log_error,
    log_info,
    log_ui_action,
    log_warn,
)

__all__ = [
    "get_logger",
    "get_log_file_path",
    "log_dir",
    "log_info",
    "log_warn",
    "log_error",
    "log_data_setup",
    "log_api_call",
    "log_ui_action",
    "log_assertion",
    "hooks",
]
