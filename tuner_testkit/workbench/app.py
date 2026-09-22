"""FastAPI application for the local workbench."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tuner_testkit.catalog.build import build_catalog
from tuner_testkit.project import project_root
from tuner_testkit.tools.runner import DestructiveNotConfirmed, RunRequest, run_tool

PACKAGE_DIR = Path(__file__).resolve().parent


def create_app(*, root: Path | None = None) -> FastAPI:
    repo = Path(root).resolve() if root is not None else project_root()
    templates = Jinja2Templates(directory=str(PACKAGE_DIR / "templates"))
    app = FastAPI(title="tuner workbench", docs_url=None, redoc_url=None)
    static = PACKAGE_DIR / "static"
    if static.is_dir():
        app.mount("/static", StaticFiles(directory=str(static)), name="static")
    app.state.root = repo

    def catalog() -> dict[str, Any]:
        return build_catalog(repo, include_kit_tools=True)

    def _render(request: Request, name: str, **ctx: Any) -> HTMLResponse:
        payload = catalog()
        return templates.TemplateResponse(
            request,
            name,
            {"root": str(repo), "catalog": payload, **ctx},
        )

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return _render(request, "home.html")

    @app.get("/tools", response_class=HTMLResponse)
    def tools_page(request: Request, q: str = "") -> HTMLResponse:
        payload = catalog()
        items = _directory(payload, q)
        return templates.TemplateResponse(
            request,
            "tools.html",
            {"root": str(repo), "catalog": payload, "items": items, "q": q},
        )

    @app.get("/tools/{item_id}", response_class=HTMLResponse)
    def tool_detail(request: Request, item_id: str) -> HTMLResponse:
        item = _find_item(catalog(), item_id)
        if item is None:
            raise HTTPException(404, f"unknown tool {item_id}")
        readme = _readme_text(repo, item)
        return _render(request, "tool.html", item=item, readme=readme, error=None)

    @app.post("/tools/{item_id}/run")
    async def tool_run(request: Request, item_id: str) -> RedirectResponse:
        form = await _parse_urlencoded(request)
        try:
            params = json.loads(form.get("params_json") or "{}")
        except json.JSONDecodeError as exc:
            raise HTTPException(400, f"invalid params JSON: {exc}") from exc
        if not isinstance(params, dict):
            raise HTTPException(400, "params must be a JSON object")
        confirm = bool(form.get("confirm"))
        try:
            result = run_tool(RunRequest(tool_id=item_id, params=params, confirm=confirm), root=repo)
        except DestructiveNotConfirmed as exc:
            raise HTTPException(400, str(exc)) from exc
        except (KeyError, ValueError) as exc:
            raise HTTPException(400, str(exc)) from exc
        return RedirectResponse(url=f"/runs/{result.run_id}", status_code=303)

    @app.get("/runs", response_class=HTMLResponse)
    def runs_page(request: Request) -> HTMLResponse:
        return _render(request, "history.html", runs=_list_runs(repo))

    @app.get("/runs/{run_id}", response_class=HTMLResponse)
    def run_detail(request: Request, run_id: str) -> HTMLResponse:
        run = _load_run(repo, run_id)
        if run is None:
            raise HTTPException(404, f"unknown run {run_id}")
        return _render(request, "run.html", run=run)

    @app.get("/env", response_class=HTMLResponse)
    def env_page(request: Request) -> HTMLResponse:
        return _render(request, "env.html", env_state=_env_view(repo))

    @app.post("/env")
    async def env_switch(request: Request) -> RedirectResponse:
        form = await _parse_urlencoded(request)
        name = (form.get("name") or "").strip()
        error = _switch_env(repo, name)
        if error:
            raise HTTPException(400, error)
        return RedirectResponse(url="/env", status_code=303)

    @app.get("/knowledge", response_class=HTMLResponse)
    def knowledge(request: Request) -> HTMLResponse:
        payload = catalog()
        return _render(
            request,
            "knowledge.html",
            assets=payload.get("knowledge", {}).get("assets", []),
            inbox=payload.get("artifacts", {}).get("inbox", {}),
            features=payload.get("tests", {}).get("features", []),
        )

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "root": str(repo)}

    @app.get("/api/catalog")
    def api_catalog() -> JSONResponse:
        return JSONResponse(catalog())

    @app.get("/api/tools")
    def api_tools(q: str = Query("")) -> JSONResponse:
        return JSONResponse({"items": _directory(catalog(), q)})

    @app.post("/api/tools/{item_id}/run")
    def api_run(item_id: str, body: dict[str, Any] | None = None) -> JSONResponse:
        body = body or {}
        params = body.get("params") if isinstance(body.get("params"), dict) else {
            k: v for k, v in body.items() if k not in {"confirm", "params"}
        }
        confirm = bool(body.get("confirm"))
        try:
            result = run_tool(RunRequest(tool_id=item_id, params=params, confirm=confirm), root=repo)
        except DestructiveNotConfirmed as exc:
            raise HTTPException(400, str(exc)) from exc
        except (KeyError, ValueError) as exc:
            raise HTTPException(400, str(exc)) from exc
        return JSONResponse(result.to_dict())

    @app.get("/api/runs")
    def api_runs() -> JSONResponse:
        return JSONResponse({"runs": _list_runs(repo)})

    @app.get("/api/env")
    def api_env() -> JSONResponse:
        return JSONResponse(_env_view(repo))

    @app.post("/api/env")
    def api_env_switch(body: dict[str, Any] | None = None) -> JSONResponse:
        body = body or {}
        name = str(body.get("name") or "").strip()
        error = _switch_env(repo, name)
        if error:
            raise HTTPException(400, error)
        return JSONResponse(_env_view(repo))

    return app


def _directory(payload: dict[str, Any], q: str) -> list[dict[str, Any]]:
    needle = (q or "").strip().lower()
    items: list[dict[str, Any]] = []
    for row in payload.get("tools", []):
        if row.get("visibility") == "local":
            continue
        items.append(_tool_item(row))
    for row in payload.get("action_words", []):
        if "word_id" not in row:
            continue
        items.append(_word_item(row))
    if needle:
        items = [it for it in items if needle in it["id"].lower() or needle in (it.get("name") or "").lower()]
    return items


def _tool_item(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["tool_id"],
        "kind": "tool",
        "name": row.get("name") or row["tool_id"],
        "group": row.get("group") or "general",
        "summary": row.get("summary") or "",
        "destructive": bool(row.get("destructive")),
        "params_schema": row.get("params_schema") or {},
        "readme_path": row.get("readme_path"),
        "origin": row.get("origin"),
    }


def _word_item(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["word_id"],
        "kind": "action_word",
        "name": row.get("name") or row["word_id"],
        "group": str(row.get("category") or "action"),
        "summary": (row.get("description") or "")[:200],
        "destructive": bool(row.get("destructive")),
        "params_schema": row.get("params_schema") or {},
        "readme_path": None,
        "origin": "workspace",
    }


def _find_item(payload: dict[str, Any], item_id: str) -> dict[str, Any] | None:
    for it in _directory(payload, ""):
        if it["id"] == item_id:
            return it
    return None


def _env_view(root: Path) -> dict[str, Any]:
    """Named environments only — never include credentials or URLs."""
    import os

    from tuner_testkit.config import (
        EnvProfileError,
        environments_of,
        load_env_local,
        read_active_env_file,
        resolve_active_name,
    )

    os.environ["TUNER_ROOT"] = str(root)
    local = load_env_local()
    if local is None:
        return {"mode": "missing", "available": [], "active": None}
    envs = environments_of(local)
    if envs is None:
        return {"mode": "flat", "available": [], "active": None}
    names = sorted(str(k) for k in envs)
    try:
        active = resolve_active_name(
            available=names,
            module_default=str(getattr(local, "ACTIVE_ENV", None) or "") or None,
            active_file_text=read_active_env_file(),
        )
    except EnvProfileError:
        active = None
    return {"mode": "named", "available": names, "active": active}


def _switch_env(root: Path, name: str) -> str | None:
    import os

    from tuner_testkit.config import environments_of, load_env_local, write_active_env

    os.environ["TUNER_ROOT"] = str(root)
    if not name:
        return "environment name is required"
    local = load_env_local()
    if local is None:
        return "no config/env_local.py — copy the example and fill values on this machine"
    envs = environments_of(local)
    if envs is None:
        return "env_local.py has no ENVIRONMENTS map"
    if name not in envs:
        return f"unknown environment {name!r}; available: {sorted(envs)}"
    write_active_env(name)
    return None


async def _parse_urlencoded(request: Request) -> dict[str, str]:
    """Parse application/x-www-form-urlencoded without python-multipart."""
    from urllib.parse import parse_qs

    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def _readme_text(root: Path, item: dict[str, Any]) -> str:
    rel = item.get("readme_path")
    if not rel:
        return ""
    path = root / rel
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _list_runs(root: Path) -> list[dict[str, Any]]:
    base = root / "artifacts" / "runs"
    if not base.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for child in sorted(base.iterdir(), reverse=True):
        if not child.is_dir():
            continue
        manifest = child / "manifest.json"
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        data["dir"] = str(child)
        rows.append(data)
    return rows


def _load_run(root: Path, run_id: str) -> dict[str, Any] | None:
    for row in _list_runs(root):
        if row.get("run_id") == run_id:
            run_dir = Path(row["dir"])
            stdout = run_dir / "stdout.log"
            stderr = run_dir / "stderr.log"
            envelope = run_dir / "envelope.json"
            row["stdout"] = stdout.read_text(encoding="utf-8", errors="replace") if stdout.is_file() else ""
            row["stderr"] = stderr.read_text(encoding="utf-8", errors="replace") if stderr.is_file() else ""
            if envelope.is_file():
                try:
                    row["envelope"] = json.loads(envelope.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    row["envelope"] = None
            return row
    return None

