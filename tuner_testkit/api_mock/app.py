"""FastAPI app: replay mock definitions and expose a control plane.

Route table = ``packages/api_objects`` assets (the request contract, via
``iter_api_models``) merged with ``data/mocks/**.json`` (the response
definition). An asset with no mock file is listed as undefined rather than
guessed at; a mock file with no asset still serves, so ad-hoc routes work
before anything is frozen.

Registration order matters: the control plane mounts first so the catch-all
does not swallow ``/__mock__/*``.

Requires the ``mock`` extra (``uv sync --extra mock``).
"""
from __future__ import annotations

import asyncio
import json
import re
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Deque

from fastapi import APIRouter, FastAPI, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from tuner_testkit.logging import log_api_call, log_info

from .errors import ApiMockError, MockSpecError, RouteNotFoundError, ScenarioNotFoundError
from .spec import ResponseSpec, RouteMock, route_key
from .store import MockStore

__all__ = ["DEFAULT_ADMIN_PREFIX", "RequestLog", "create_app"]

DEFAULT_ADMIN_PREFIX = "/__mock__"
_SERVED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
_SENSITIVE_HEADER_RE = re.compile(
    r"(authorization|cookie|set-cookie|token|secret|password|session)", re.IGNORECASE
)


@dataclass
class RequestLog:
    """One received request, sanitised. Bodies are reduced to key names."""

    at: str
    method: str
    path: str
    query: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    body_keys: list[str] | None = None
    content_type: str = ""
    matched_route: str | None = None
    scenario: str | None = None
    status: int = 501


class ActiveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    path: str
    scenario: str


class ScenarioRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    path: str
    scenario: str
    response: ResponseSpec
    activate: bool = Field(False, description="Make this scenario live immediately")


class RouteRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str | None = None
    path: str | None = None


def create_app(
    *,
    store: MockStore | None = None,
    mocks_dir: Any = None,
    models: list[Any] | None = None,
    load_models: bool = True,
    admin_prefix: str = DEFAULT_ADMIN_PREFIX,
    max_request_log: int = 200,
    allow_cors: bool = True,
) -> FastAPI:
    """Build the mock server.

    ``models`` accepts pre-loaded ``ApiModelRef``s; when omitted and
    ``load_models`` is true they are discovered from ``packages/api_objects``.
    """
    active_store = store if store is not None else MockStore(mocks_dir)
    active_store.reload()

    asset_refs = models
    if asset_refs is None and load_models:
        from packages.api_objects.registry import iter_api_models

        asset_refs = iter_api_models()
    asset_refs = list(asset_refs or [])
    assets_by_key = {ref.route_key: ref for ref in asset_refs}

    request_log: Deque[RequestLog] = deque(maxlen=max(1, int(max_request_log)))

    app = FastAPI(
        title="api_mock server",
        description=(
            "Replays packages/api_objects routes from data/mocks definitions. "
            f"Control plane at {admin_prefix}."
        ),
        version="1.0.0",
        docs_url=f"{admin_prefix}/docs",
        openapi_url=f"{admin_prefix}/openapi.json",
    )
    if allow_cors:
        # A local test double consumed by a platform UI; not a production surface.
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.state.store = active_store
    app.state.assets_by_key = assets_by_key
    app.state.request_log = request_log
    app.state.admin_prefix = admin_prefix

    _register_exception_handlers(app)
    app.include_router(
        _build_admin_router(active_store, assets_by_key, request_log, admin_prefix),
        prefix=admin_prefix,
    )
    _register_catch_all(app, active_store, request_log, admin_prefix)

    log_info(
        "api_mock app created",
        mocks_dir=str(active_store.mocks_dir),
        mock_routes=len(active_store.routes()),
        assets=len(assets_by_key),
        admin_prefix=admin_prefix,
    )
    return app


def _register_exception_handlers(app: FastAPI) -> None:
    """Map library errors to control-plane status codes instead of bare 500s."""

    @app.exception_handler(RouteNotFoundError)
    async def _route_missing(_request: Request, exc: RouteNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"error": "route_not_found", "message": str(exc)})

    @app.exception_handler(ScenarioNotFoundError)
    async def _scenario_missing(_request: Request, exc: ScenarioNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"error": "scenario_not_found", "message": str(exc)})

    @app.exception_handler(MockSpecError)
    async def _bad_spec(_request: Request, exc: MockSpecError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"error": "invalid_mock_spec", "message": str(exc)})

    @app.exception_handler(ApiMockError)
    async def _generic(_request: Request, exc: ApiMockError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"error": "api_mock_error", "message": str(exc)})


# --- catch-all -------------------------------------------------------------


def _register_catch_all(
    app: FastAPI,
    store: MockStore,
    request_log: Deque[RequestLog],
    admin_prefix: str,
) -> None:
    @app.api_route("/{full_path:path}", methods=_SERVED_METHODS, include_in_schema=False)
    async def _serve_mock(full_path: str, request: Request) -> Response:  # noqa: ARG001
        path = request.url.path
        method = request.method.upper()

        body_bytes = await request.body()
        entry = RequestLog(
            at=datetime.now(timezone.utc).isoformat(),
            method=method,
            path=path,
            query=dict(request.query_params),
            headers=_sanitize_headers(request.headers),
            body_keys=_body_keys(body_bytes, request.headers.get("content-type", "")),
            content_type=request.headers.get("content-type", ""),
        )

        route = store.match(method, path)
        if route is None:
            entry.status = 501
            request_log.append(entry)
            log_api_call(method, path, status=501, summary="no mock definition")
            return JSONResponse(
                status_code=501,
                content={
                    "error": "no_mock_definition",
                    "message": f"No mock defined for {route_key(method, path)}",
                    "hint": (
                        f"Define it via PUT {admin_prefix}/scenario, "
                        "or seed from a recorded asset with "
                        "'python -m tuner_testkit.apps.mock_server seed'."
                    ),
                    "mocks_dir": str(store.mocks_dir),
                },
            )

        response_spec = route.active_response()
        if response_spec is None:
            entry.matched_route = route.route_key
            entry.status = 500
            request_log.append(entry)
            log_api_call(method, path, status=500, summary="route has no scenarios")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "empty_route",
                    "message": f"{route.route_key} has no scenario to serve",
                },
            )

        entry.matched_route = route.route_key
        entry.scenario = route.active
        entry.status = response_spec.status
        request_log.append(entry)

        if response_spec.delay_ms:
            await asyncio.sleep(response_spec.delay_ms / 1000)

        log_api_call(
            method,
            path,
            status=response_spec.status,
            scenario=route.active,
            mocked=True,
        )
        return _to_response(response_spec)


def _to_response(spec: ResponseSpec) -> Response:
    headers = dict(spec.headers)
    if spec.body is None:
        return Response(status_code=spec.status, headers=headers)
    if isinstance(spec.body, (dict, list)):
        # JSONResponse sets application/json unless the definition overrides it.
        return JSONResponse(status_code=spec.status, content=spec.body, headers=headers)
    media_type = headers.pop("Content-Type", None) or headers.pop("content-type", None)
    return Response(
        content=str(spec.body),
        status_code=spec.status,
        headers=headers,
        media_type=media_type or "text/plain; charset=utf-8",
    )


def _sanitize_headers(headers: Any) -> dict[str, str]:
    return {
        str(k): ("***" if _SENSITIVE_HEADER_RE.search(str(k)) else str(v))
        for k, v in headers.items()
    }


def _body_keys(body: bytes, content_type: str) -> list[str] | None:
    """Key names only — bodies may be large or carry credentials."""
    if not body:
        return None
    if "json" not in (content_type or "").lower():
        return None
    try:
        parsed = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return None
    if isinstance(parsed, dict):
        return sorted(str(k) for k in parsed)
    return None


# --- control plane ---------------------------------------------------------


def _build_admin_router(
    store: MockStore,
    assets_by_key: dict[str, Any],
    request_log: Deque[RequestLog],
    admin_prefix: str,
) -> APIRouter:
    router = APIRouter(tags=["mock control plane"])

    def _route_summary(route: RouteMock | None, key: str) -> dict[str, Any]:
        asset = assets_by_key.get(key)
        model = getattr(asset, "model", None)
        method, _, path = key.partition(" ")
        return {
            "key": key,
            "method": method,
            "path": path,
            "has_mock": route is not None,
            "active": route.active if route else None,
            "scenarios": sorted(route.scenarios) if route else [],
            "dirty": store.is_dirty(method, path),
            "asset_id": getattr(model, "id", None),
            "asset_file": getattr(asset, "file", None),
            "auth_required": bool((getattr(model, "auth_policy", None) or {}).get("required")),
            "body_format": getattr(model, "body_format", None),
            "query_keys": sorted(getattr(model, "query_schema", None) or {}),
            "body_keys": sorted(getattr(model, "body_schema", None) or {}),
        }

    @router.get("/health", summary="Liveness plus counts")
    def health() -> dict[str, Any]:
        routes = store.routes()
        return {
            "ok": True,
            "mocks_dir": str(store.mocks_dir),
            "mock_routes": len(routes),
            "assets": len(assets_by_key),
            "pending_changes": store.dirty_keys(),
            "requests_recorded": len(request_log),
        }

    @router.get("/routes", summary="Every known route: asset contract + mock state")
    def list_routes() -> dict[str, Any]:
        by_key: dict[str, RouteMock | None] = {key: None for key in assets_by_key}
        for route in store.routes():
            by_key[route.route_key] = route
        rows = [_route_summary(route, key) for key, route in sorted(by_key.items())]
        return {"count": len(rows), "routes": rows}

    @router.get("/routes/detail", summary="One route with all scenario bodies")
    def route_detail(
        method: str = Query(..., description="HTTP method, e.g. POST"),
        path: str = Query(..., description="Route path, e.g. /prod-api/foo"),
    ) -> dict[str, Any]:
        key = route_key(method, path)
        route = store.get(method, path)
        summary = _route_summary(route, key)
        summary["definition"] = route.to_json_dict() if route else None
        return summary

    @router.put("/active", summary="Switch which scenario is served")
    def set_active(payload: ActiveRequest) -> dict[str, Any]:
        route = store.set_active(payload.method, payload.path, payload.scenario)
        log_info("mock scenario activated", route=route.route_key, scenario=route.active)
        return {"ok": True, "route": route.route_key, "active": route.active}

    @router.put("/scenario", summary="Define or overwrite a scenario's response")
    def put_scenario(payload: ScenarioRequest) -> dict[str, Any]:
        route = store.upsert_scenario(
            payload.method,
            payload.path,
            payload.scenario,
            payload.response,
            activate=payload.activate,
        )
        log_info(
            "mock scenario defined",
            route=route.route_key,
            scenario=payload.scenario,
            status=payload.response.status,
            active=route.active,
        )
        return {
            "ok": True,
            "route": route.route_key,
            "scenario": payload.scenario,
            "active": route.active,
            "scenarios": sorted(route.scenarios),
            "persisted": False,
        }

    @router.delete("/scenario", summary="Remove a scenario")
    def delete_scenario(
        method: str = Query(...),
        path: str = Query(...),
        scenario: str = Query(...),
    ) -> dict[str, Any]:
        route = store.delete_scenario(method, path, scenario)
        return {
            "ok": True,
            "route": route.route_key,
            "active": route.active,
            "scenarios": sorted(route.scenarios),
        }

    @router.post("/persist", summary="Write pending changes to data/mocks")
    def persist(payload: RouteRef | None = None) -> dict[str, Any]:
        ref = payload or RouteRef()
        written = store.persist(ref.method, ref.path)
        return {"ok": True, "written": written, "count": len(written)}

    @router.post("/reset", summary="Drop in-memory changes and re-read disk")
    def reset(reload: bool = Query(False, description="Also re-read files from disk")) -> dict[str, Any]:
        dropped = store.reset()
        reloaded = store.reload() if reload else None
        return {"ok": True, "dropped_overrides": dropped, "routes_reloaded": reloaded}

    @router.get("/requests", summary="Recent received requests (sanitised)")
    def list_requests(limit: int = Query(50, ge=1, le=1000)) -> dict[str, Any]:
        items = list(request_log)[-limit:]
        return {"count": len(items), "total_recorded": len(request_log), "requests": [asdict(i) for i in items]}

    @router.delete("/requests", summary="Clear the request log")
    def clear_requests() -> dict[str, Any]:
        cleared = len(request_log)
        request_log.clear()
        return {"ok": True, "cleared": cleared}

    return router
