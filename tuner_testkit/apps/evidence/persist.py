"""Sanitize and persist Playwright MCP captures under artifacts/evidence/<run_id>/."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

from tuner_testkit.api_objects.recording.capture import build_capture
from tuner_testkit.api_objects.recording.normalize import normalize_path
from tuner_testkit.api_objects.recording.sanitize import sanitize_mapping
from tuner_testkit.logging import log_info
from tuner_testkit.project import project_root

RUN_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
EVIDENCE_REL = Path("artifacts") / "evidence"


def new_run_id(short: str, *, now: datetime | None = None) -> str:
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", short.strip()) or "explore"
    return f"{stamp}-{slug}"[:80]


def evidence_root(*, root: Path | None = None) -> Path:
    base = Path(root) if root is not None else project_root()
    return base / EVIDENCE_REL


def run_dir(run_id: str, *, root: Path | None = None) -> Path:
    if not RUN_ID_RE.fullmatch(run_id):
        raise ValueError(f"run_id must be ASCII [A-Za-z0-9._-], got {run_id!r}")
    path = evidence_root(root=root) / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _as_url(req: Mapping[str, Any]) -> str:
    url = str(req.get("url") or "").strip()
    if url:
        return url
    host = str(req.get("host") or "").strip()
    path = str(req.get("path") or "/")
    if host:
        scheme = "https" if ":443" in host else "http"
        return f"{scheme}://{host}{path}"
    return f"http://evidence.invalid{path if path.startswith('/') else '/' + path}"


def capture_row(
    item: Mapping[str, Any],
    *,
    scenario_id: str,
    run_id: str,
    timestamp: str,
) -> dict[str, Any]:
    """Turn a loose MCP/network dict into one sanitized evidence JSON object."""
    req = item.get("request") if isinstance(item.get("request"), Mapping) else item
    resp = item.get("response") if isinstance(item.get("response"), Mapping) else {}
    if not isinstance(req, Mapping):
        req = {}
    method = str(req.get("method") or item.get("method") or "GET")
    url = _as_url(req)
    req_headers = req.get("headers") if isinstance(req.get("headers"), Mapping) else {}
    resp_headers = resp.get("headers") if isinstance(resp.get("headers"), Mapping) else {}
    status = resp.get("status") if resp.get("status") is not None else item.get("status")
    try:
        status_i = int(status if status is not None else 0)
    except (TypeError, ValueError):
        status_i = 0
    body = req.get("body")
    if body is None:
        body = req.get("request_body")
    resp_body = resp.get("body_sample")
    if resp_body is None:
        resp_body = resp.get("body")

    req_content: bytes | str | None
    if isinstance(body, (dict, list)):
        req_content = json.dumps(body, ensure_ascii=False)
        merged_req_headers = dict(req_headers)
        merged_req_headers.setdefault("content-type", "application/json")
    else:
        req_content = body if body is None or isinstance(body, (bytes, str)) else str(body)
        merged_req_headers = dict(req_headers)

    resp_content: bytes | str | None
    merged_resp_headers = dict(resp_headers)
    if isinstance(resp_body, (dict, list)):
        resp_content = json.dumps(resp_body, ensure_ascii=False)
        merged_resp_headers.setdefault("content-type", "application/json")
    else:
        resp_content = (
            resp_body if resp_body is None or isinstance(resp_body, (bytes, str)) else str(resp_body)
        )

    cap = build_capture(
        method=method,
        url=url,
        request_headers=merged_req_headers,
        request_content=req_content,
        response_status=status_i,
        response_headers=merged_resp_headers,
        response_content=resp_content,
        tool="evidence",
    )
    host = cap.host
    if host in {"evidence.invalid", ""}:
        parsed = urlsplit(url)
        host = parsed.netloc or str(req.get("host") or "")
    return {
        "scenario_id": str(item.get("scenario_id") or scenario_id),
        "run_id": run_id,
        "timestamp": str(item.get("timestamp") or timestamp),
        "request": {
            "method": cap.method,
            "host": host,
            "path": cap.path,
            "normalized_path": cap.normalized_path,
            "query": cap.query,
            "headers": cap.request_headers,
            "body": cap.request_body,
        },
        "response": {
            "status": cap.response_status,
            "headers": cap.response_headers,
            "body_sample": cap.response_body,
        },
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, default=str))
            handle.write("\n")


def unique_routes(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        req = row.get("request") if isinstance(row.get("request"), Mapping) else {}
        resp = row.get("response") if isinstance(row.get("response"), Mapping) else {}
        method = str((req or {}).get("method") or row.get("method") or "")
        path = str(
            (req or {}).get("normalized_path")
            or (req or {}).get("path")
            or row.get("path")
            or ""
        )
        if not method or not path:
            continue
        npath = path if path.startswith("/") and "{" in path else normalize_path(path)
        key = (method.upper(), npath)
        seen[key] = {
            "method": method.upper(),
            "normalized_path": npath,
            "status": (resp or {}).get("status"),
        }
    return [seen[k] for k in sorted(seen)]


def _summary_markdown(
    *,
    run_id: str,
    scenario_id: str,
    intent: str,
    routes: list[dict[str, Any]],
) -> str:
    lines = [
        f"---",
        f"run_id: {run_id}",
        f"scenario_id: {scenario_id}",
        f"sanitizer: tuner_testkit.api_objects.recording.sanitize",
        f"---",
        "",
        f"# Evidence {run_id}",
        "",
        intent.strip() or "(no intent provided)",
        "",
        "## Routes",
        "",
    ]
    for route in routes:
        status = route.get("status")
        extra = f" → {status}" if status is not None else ""
        lines.append(f"- `{route['method']} {route['normalized_path']}`{extra}")
    lines.extend(
        [
            "",
            "## Sanitizer",
            "",
            "Applied. No Authorization / Cookie / Set-Cookie / *token* / *password* keys persisted.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_manifest(
    dest: Path,
    *,
    run_id: str,
    scenario_id: str,
    intent: str,
    count: int,
    routes: list[dict[str, Any]],
    root: Path | None,
) -> None:
    """Run-level manifest (docs/spec/artifacts-layout.md §2) so catalogs and the workbench can list evidence runs."""
    from tuner_testkit.artifacts import RunManifest, default_producer

    manifest = RunManifest(
        kind="evidence",
        run_id=run_id,
        producer=default_producer(root, suite="tuner-evidence persist"),
        params={"scenario_id": scenario_id, "intent": intent},
        dir=dest,
    )
    manifest.finish("succeeded", exit_code=0, summary={"captures": count, "routes": len(routes)})


def persist(
    *,
    run_id: str,
    scenario_id: str,
    captures: Iterable[Mapping[str, Any]],
    actions: Iterable[Mapping[str, Any]] | None = None,
    intent: str = "",
    summary_text: str | None = None,
    root: Path | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Write sanitized evidence files. Return a JSON-serialisable summary."""
    ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dest = run_dir(run_id, root=root)
    rows = [
        capture_row(item, scenario_id=scenario_id, run_id=run_id, timestamp=ts)
        for item in captures
    ]
    write_jsonl(dest / "network.jsonl", rows)
    files = ["network.jsonl"]
    if actions is not None:
        safe_actions = [sanitize_mapping(dict(row)) for row in actions]
        write_jsonl(dest / "actions.jsonl", safe_actions)
        files.append("actions.jsonl")
    routes = unique_routes(rows)
    summary = summary_text if summary_text is not None else _summary_markdown(
        run_id=run_id,
        scenario_id=scenario_id,
        intent=intent,
        routes=routes,
    )
    (dest / "run_summary.md").write_text(summary, encoding="utf-8", newline="\n")
    files.append("run_summary.md")
    _write_manifest(dest, run_id=run_id, scenario_id=scenario_id, intent=intent, count=len(rows), routes=routes, root=root)
    files.append("manifest.json")
    payload = {
        "run_id": run_id,
        "dir": dest.as_posix(),
        "files": files,
        "count": len(rows),
        "routes": routes,
        "sanitizer": "tuner_testkit.api_objects.recording.sanitize",
    }
    log_info("evidence persisted", run_id=run_id, count=len(rows), dir=str(dest))
    return payload


def load_run(run_id: str, *, root: Path | None = None) -> dict[str, Any]:
    dest = evidence_root(root=root) / run_id
    network = dest / "network.jsonl"
    if not network.is_file():
        raise FileNotFoundError(network)
    rows = load_jsonl(network)
    return {
        "run_id": run_id,
        "dir": dest.as_posix(),
        "count": len(rows),
        "routes": unique_routes(rows),
        "sanitizer": "tuner_testkit.api_objects.recording.sanitize",
    }
