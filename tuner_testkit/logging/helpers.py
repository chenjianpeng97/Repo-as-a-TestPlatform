"""Business-semantic helpers for step authors.

Use these instead of ``get_logger().info(...)`` inside step functions so the
log output stays structurally consistent and easy to grep:

- :func:`log_data_setup` -- "I prepared N users / M fixture rows / ..."
- :func:`log_api_call` -- a single API interaction summary
- :func:`log_ui_action` -- a single UI action summary
- :func:`log_assertion` -- an explicit claim being checked
- :func:`log_warn` / :func:`log_error` / :func:`log_info` -- free-form catch-alls

Every helper emits exactly one log line. Extra fields are rendered as
``key=value`` pairs after the main message, so a line like::

    log_api_call("GET", "/api/v1/items", status=200, total=42, page=1)

becomes::

    2026-... INFO  [api] [feature::scenario] [API    ] GET /api/v1/items -> 200 total=42 page=1
"""
from __future__ import annotations

from typing import Any, Mapping

from .context import use_kind
from .core import get_logger


# ---------------------------------------------------------------------------
# Internal formatting
# ---------------------------------------------------------------------------
def _fmt_fields(fields: Mapping[str, Any]) -> str:
    """Render ``key=value`` suffix; values are coerced via ``repr`` when structural."""
    if not fields:
        return ""
    parts: list[str] = []
    for k, v in fields.items():
        if v is None:
            parts.append(f"{k}=None")
        elif isinstance(v, bool):
            parts.append(f"{k}={v}")
        elif isinstance(v, (int, float)):
            parts.append(f"{k}={v}")
        elif isinstance(v, str):
            parts.append(f"{k}={v}" if "\n" not in v and " " not in v else f"{k}={v!r}")
        else:
            parts.append(f"{k}={v!r}")
    return " " + " ".join(parts)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------
def log_info(message: str, **fields: Any) -> None:
    """Free-form INFO line; use when nothing more specific fits."""
    with use_kind("INFO"):
        get_logger().info("%s%s", message, _fmt_fields(fields))


def log_warn(message: str, **fields: Any) -> None:
    """Non-fatal warning."""
    with use_kind("WARN"):
        get_logger().warning("%s%s", message, _fmt_fields(fields))


def log_error(message: str, **fields: Any) -> None:
    """Fatal / step-breaking error (without raising)."""
    with use_kind("ERROR"):
        get_logger().error("%s%s", message, _fmt_fields(fields))


def log_data_setup(what: str, **fields: Any) -> None:
    """Describe a chunk of business data that was just prepared.

    Example::

        log_data_setup("concurrent_sales_users", count=len(users),
                       sample=[u.display for u in users[:3]])
    """
    with use_kind("DATA"):
        get_logger().info("prepared %s%s", what, _fmt_fields(fields))


def log_api_call(
    method: str,
    path: str,
    *,
    status: int | None = None,
    summary: str = "",
    **fields: Any,
) -> None:
    """Summarise a single API interaction.

    Keep the summary short -- ideally the 2-3 values that matter for the
    assertion that follows (e.g. ``total=42``). For bulk payloads use
    :func:`log_data_setup` on the prepared collection instead of dumping the
    raw response.
    """
    with use_kind("API"):
        msg = f"{method.upper()} {path}"
        if status is not None:
            msg += f" -> {status}"
        if summary:
            msg += f" {summary}"
        get_logger().info("%s%s", msg, _fmt_fields(fields))


def log_ui_action(
    action: str,
    *,
    target: str = "",
    **fields: Any,
) -> None:
    """Summarise a single UI action.

    Example::

        log_ui_action("click", target="登录按钮")
        log_ui_action("fill", target="用户名", value="admin")
    """
    with use_kind("UI"):
        msg = action if not target else f"{action} @ {target}"
        get_logger().info("%s%s", msg, _fmt_fields(fields))


def log_assertion(
    claim: str,
    *,
    expected: Any = None,
    actual: Any = None,
    passed: bool = True,
    **fields: Any,
) -> None:
    """Log a single assertion claim with expected/actual and its outcome.

    The level follows the outcome: PASS -> INFO, FAIL -> ERROR, so a grep for
    ``ASSERT.*FAIL`` in the log file surfaces every failed check at once.
    """
    outcome = "PASS" if passed else "FAIL"
    suffix = _fmt_fields(fields)
    logger = get_logger()
    with use_kind("ASSERT"):
        if passed:
            logger.info(
                "%s expected=%r actual=%r -> %s%s",
                claim, expected, actual, outcome, suffix,
            )
        else:
            logger.error(
                "%s expected=%r actual=%r -> %s%s",
                claim, expected, actual, outcome, suffix,
            )
