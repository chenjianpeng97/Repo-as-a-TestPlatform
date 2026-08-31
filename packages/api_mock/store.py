"""Load mock definitions from disk and hold runtime overrides in memory.

Two layers:

* **disk** — ``data/mocks/**.json``, the committed baseline.
* **overrides** — whatever the admin API changed since startup.

Overrides win on read and stay in memory until :meth:`MockStore.persist` writes
them out. That split is deliberate: the Plane runner must be able to redefine a
response without the server writing into the checked-out repo (see
``apps/index_platform/README.md`` — catalog jobs do not write git).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from packages.logging import log_info, log_warn

from .errors import MockSpecError, RouteNotFoundError, ScenarioNotFoundError
from .router import RouteTable
from .spec import ResponseSpec, RouteMock, mock_relpath, route_key, scan_sensitive

__all__ = ["DEFAULT_MOCKS_DIRNAME", "MockStore", "default_mocks_dir"]

DEFAULT_MOCKS_DIRNAME = "mocks"


def default_mocks_dir(root: str | Path | None = None) -> Path:
    repo_root = Path(root) if root is not None else _repo_root()
    return repo_root / "data" / DEFAULT_MOCKS_DIRNAME


class MockStore:
    def __init__(self, mocks_dir: str | Path | None = None) -> None:
        self.mocks_dir = Path(mocks_dir) if mocks_dir is not None else default_mocks_dir()
        self._disk: dict[str, RouteMock] = {}
        self._overrides: dict[str, RouteMock] = {}
        self._source_files: dict[str, Path] = {}
        self._table: RouteTable[RouteMock] | None = None

    # --- loading -----------------------------------------------------------

    def reload(self) -> int:
        """Re-read every ``*.json`` under ``mocks_dir``. Drops overrides."""
        self._disk.clear()
        self._overrides.clear()
        self._source_files.clear()
        self._table = None
        if not self.mocks_dir.is_dir():
            return 0

        for path in sorted(self.mocks_dir.rglob("*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                log_warn("mock definition unreadable", file=str(path), error=str(exc))
                continue
            try:
                route = RouteMock.from_json_dict(raw, source=str(path))
            except MockSpecError as exc:
                log_warn("mock definition invalid", file=str(path), error=str(exc))
                continue

            key = route.route_key
            existing = self._disk.get(key)
            if existing is not None and existing.version >= route.version:
                continue
            self._disk[key] = route
            self._source_files[key] = path

        log_info("mock definitions loaded", dir=str(self.mocks_dir), routes=len(self._disk))
        return len(self._disk)

    def reset(self) -> int:
        """Discard in-memory overrides, keep the disk baseline."""
        dropped = len(self._overrides)
        self._overrides.clear()
        self._table = None
        return dropped

    # --- reading -----------------------------------------------------------

    def routes(self) -> list[RouteMock]:
        merged = {**self._disk, **self._overrides}
        return [merged[key] for key in sorted(merged)]

    def get(self, method: str, path: str) -> RouteMock | None:
        """Exact ``method + path`` lookup (no dynamic-segment matching)."""
        key = route_key(method, path)
        return self._overrides.get(key) or self._disk.get(key)

    def match(self, method: str, path: str) -> RouteMock | None:
        """Lookup honouring ``{id}`` / ``{uuid}`` patterns in definitions."""
        exact = self.get(method, path)
        if exact is not None:
            return exact
        if self._table is None:
            self._table = RouteTable(
                self.routes(),
                method_of=lambda route: route.method,
                path_of=lambda route: route.path,
            )
        return self._table.match(method, path)

    def is_dirty(self, method: str, path: str) -> bool:
        return route_key(method, path) in self._overrides

    def dirty_keys(self) -> list[str]:
        return sorted(self._overrides)

    # --- writing (in-memory) -----------------------------------------------

    def upsert(self, route: RouteMock) -> RouteMock:
        self._overrides[route.route_key] = route
        self._table = None
        return route

    def upsert_scenario(
        self,
        method: str,
        path: str,
        name: str,
        response: ResponseSpec,
        *,
        activate: bool = False,
        create_route: bool = True,
    ) -> RouteMock:
        """Add or replace one scenario. Creates the route when unknown."""
        current = self.get(method, path)
        if current is None:
            if not create_route:
                raise RouteNotFoundError(f"no mock route for {route_key(method, path)}")
            current = RouteMock(method=method, path=path, scenarios={}, active=name)
        scenarios = {**current.scenarios, name: response}
        active = name if activate or current.active not in scenarios else current.active
        return self.upsert(current.model_copy(update={"scenarios": scenarios, "active": active}))

    def set_active(self, method: str, path: str, name: str) -> RouteMock:
        current = self.get(method, path)
        if current is None:
            raise RouteNotFoundError(f"no mock route for {route_key(method, path)}")
        if name not in current.scenarios:
            raise ScenarioNotFoundError(
                f"{route_key(method, path)} has no scenario {name!r} "
                f"(have: {sorted(current.scenarios)})"
            )
        return self.upsert(current.model_copy(update={"active": name}))

    def delete_scenario(self, method: str, path: str, name: str) -> RouteMock:
        current = self.get(method, path)
        if current is None:
            raise RouteNotFoundError(f"no mock route for {route_key(method, path)}")
        if name not in current.scenarios:
            raise ScenarioNotFoundError(f"{route_key(method, path)} has no scenario {name!r}")
        scenarios = {k: v for k, v in current.scenarios.items() if k != name}
        if not scenarios:
            raise MockSpecError(f"{route_key(method, path)}: cannot delete the last scenario")
        active = current.active if current.active in scenarios else next(iter(scenarios))
        return self.upsert(current.model_copy(update={"scenarios": scenarios, "active": active}))

    # --- writing (disk) ----------------------------------------------------

    def persist(self, method: str | None = None, path: str | None = None) -> list[str]:
        """Write overrides to ``data/mocks/``. Whole set unless a route is named."""
        if (method is None) != (path is None):
            raise ValueError("persist requires both method and path, or neither")

        if method is not None and path is not None:
            key = route_key(method, path)
            if key not in self._overrides:
                raise RouteNotFoundError(f"no pending changes for {key}")
            targets: Iterable[str] = [key]
        else:
            targets = list(self._overrides)

        written: list[str] = []
        for key in targets:
            route = self._overrides[key]
            leaked = scan_sensitive(route)
            if leaked:
                log_warn(
                    "mock persist contains credential-shaped values",
                    route=key,
                    fields=leaked,
                )
            target = self._source_files.get(key) or (
                self.mocks_dir / mock_relpath(route.method, route.path, version=route.version)
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(route.to_json_dict(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            self._disk[key] = route
            self._source_files[key] = target
            written.append(str(target))

        for key in list(targets):
            self._overrides.pop(key, None)
        self._table = None
        log_info("mock definitions persisted", count=len(written), dir=str(self.mocks_dir))
        return written


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file() and (parent / "packages").is_dir():
            return parent
    return here.parents[2]
