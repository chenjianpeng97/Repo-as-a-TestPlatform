"""API mock toolkit: serve ``packages/api_objects`` routes with canned responses.

Layers mirror ``tuner_testkit.api_test``:

- **definition** — :class:`~tuner_testkit.api_mock.spec.RouteMock` /
  :class:`~tuner_testkit.api_mock.spec.ResponseSpec`, the per-scenario response
  contract stored in ``data/mocks/**.json``.
- **state** — :class:`~tuner_testkit.api_mock.store.MockStore`, disk baseline plus
  in-memory overrides written by the admin API.
- **serving** — :func:`~tuner_testkit.api_mock.app.create_app`, a FastAPI app whose
  catch-all replays definitions and whose ``/__mock__`` control plane lets a
  test platform redefine responses at runtime.

``create_app`` needs the ``mock`` extra (``uv sync --extra mock``); it is
exported lazily so importing this package stays cheap and dependency-free.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .errors import (
    ApiMockError,
    MockSpecError,
    RouteNotFoundError,
    ScenarioNotFoundError,
)
from .router import PathPattern, RouteTable, path_matches
from .spec import (
    DEFAULT_SCENARIO,
    ResponseSpec,
    RouteMock,
    mock_relpath,
    route_key,
    scan_sensitive,
)
from .store import DEFAULT_MOCKS_DIRNAME, MockStore, default_mocks_dir

if TYPE_CHECKING:  # pragma: no cover
    from .app import create_app

__all__ = [
    "DEFAULT_MOCKS_DIRNAME",
    "DEFAULT_SCENARIO",
    "ApiMockError",
    "MockSpecError",
    "MockStore",
    "PathPattern",
    "ResponseSpec",
    "RouteMock",
    "RouteNotFoundError",
    "RouteTable",
    "ScenarioNotFoundError",
    "create_app",
    "default_mocks_dir",
    "mock_relpath",
    "path_matches",
    "route_key",
    "scan_sensitive",
]


def __getattr__(name: str) -> Any:
    """Defer the FastAPI import so ``tuner_testkit.api_mock`` works without the extra."""
    if name == "create_app":
        from .app import create_app as _create_app

        return _create_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
