"""Render / check the ``auto:`` fenced zones of an INDEX file from the workspace catalog.

Zones are Markdown comment fences::

    <!-- auto:begin:ddl -->
    ...rendered table...
    <!-- auto:end:ddl -->

Supported zone ids: ``ddl``, ``sql``, ``api_objects``, ``page_objects``,
``action_words``, ``apps``, ``features``, ``assets``. Text outside the fences
is never touched, so humans and the ``maintain-index`` skill keep the manual
sections.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from tuner_testkit.catalog.build import build_catalog

FENCE_RE = re.compile(
    r"(?P<begin><!--\s*auto:begin:(?P<zone>[a-z_]+)\s*-->)\r?\n(?P<body>.*?)(?P<end><!--\s*auto:end:(?P=zone)\s*-->)",
    re.S,
)
EMPTY = "_(暂无)_"


def _table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    if not rows:
        lines.append("| " + " | ".join([EMPTY] + [""] * (len(header) - 1)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(_cell(c) for c in row) + " |")
    return "\n".join(lines)


def _cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def render_ddl(catalog: dict[str, Any]) -> str:
    rows = []
    for block in catalog["knowledge"]["ddl"]:
        rows.append([f"`{block['datasource']}`", ", ".join(f"`{t}`" for t in block["tables"]) or "", f"`{block['path']}`"])
    return _table(["datasource", "表", "路径"], rows)


def render_sql(catalog: dict[str, Any]) -> str:
    rows = [[f"`{row['name']}`", f"`{row['path']}`"] for row in catalog["knowledge"]["sql_files"]]
    return _table(["文件", "路径"], rows)


def render_assets(catalog: dict[str, Any]) -> str:
    rows = []
    for row in catalog["knowledge"]["assets"]:
        rows.append(
            [
                f"`{row['path']}`",
                row.get("category") or "",
                row.get("domain") or "",
                row.get("source") or "",
                row.get("confidence") or "",
                row.get("title") or "",
            ]
        )
    return _table(["路径", "类别", "domain", "source", "confidence", "标题"], rows)


def render_api_objects(catalog: dict[str, Any]) -> str:
    rows = [[f"`{row['method']} {row['path']}`", f"`{row['file']}`"] for row in catalog["api_objects"]]
    return _table(["method + path", "文件"], rows)


def render_page_objects(catalog: dict[str, Any]) -> str:
    rows = [[f"`{row['page_id']}`", f"`{row['path']}`"] for row in catalog["page_objects"]]
    return _table(["page", "文件"], rows)


def render_action_words(catalog: dict[str, Any]) -> str:
    rows = []
    for row in catalog["action_words"]:
        if "word_id" not in row:
            rows.append([f"_(扫描失败: {row.get('error', '')})_", "", ""])
            continue
        rows.append([f"`{row['word_id']}`", row.get("name") or "", row.get("category") or ""])
    return _table(["word_id", "名称", "类别"], rows)


def render_apps(catalog: dict[str, Any]) -> str:
    rows = []
    for row in catalog["tools"]:
        if row.get("origin") != "workspace":
            continue
        readme = f"`{row['readme_path']}`" if row.get("readme_path") else ""
        rows.append([f"`{row['tool_id']}`", f"`{' '.join(row['argv'])}`", row.get("summary") or row.get("name") or "", readme])
    return _table(["工具", "运行", "用途", "交接文档"], rows)


def render_features(catalog: dict[str, Any]) -> str:
    rows = []
    for row in catalog["tests"]["features"]:
        rows.append([f"`{row['path']}`", str(len(row["scenarios"])), ", ".join(row.get("tags") or [])])
    return _table(["feature", "场景数", "标签"], rows)


RENDERERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "ddl": render_ddl,
    "sql": render_sql,
    "assets": render_assets,
    "api_objects": render_api_objects,
    "page_objects": render_page_objects,
    "action_words": render_action_words,
    "apps": render_apps,
    "features": render_features,
}


def resolve_index_file(root: Path, explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        return path if path.is_absolute() else root / path
    project = root / "INDEX.project.md"
    return project if project.is_file() else root / "INDEX.md"


def render_text(text: str, catalog: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    """Return (new_text, zones_rendered, zones_unknown)."""
    rendered: list[str] = []
    unknown: list[str] = []

    def _sub(match: re.Match[str]) -> str:
        zone = match.group("zone")
        renderer = RENDERERS.get(zone)
        if renderer is None:
            unknown.append(zone)
            return match.group(0)
        rendered.append(zone)
        return f"{match.group('begin')}\n{renderer(catalog)}\n{match.group('end')}"

    new_text = FENCE_RE.sub(_sub, text)
    return new_text, rendered, unknown


def render_index(root: Path, explicit_file: str | None = None, *, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    path = resolve_index_file(root, explicit_file)
    if not path.is_file():
        raise FileNotFoundError(f"index file not found: {path}")
    catalog = catalog or build_catalog(root)
    original = path.read_text(encoding="utf-8")
    new_text, rendered, unknown = render_text(original, catalog)
    changed = new_text != original
    if changed:
        path.write_text(new_text, encoding="utf-8", newline="\n")
    return {"file": str(path), "zones": rendered, "unknown_zones": unknown, "changed": changed}


def check_index(root: Path, explicit_file: str | None = None, *, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    path = resolve_index_file(root, explicit_file)
    if not path.is_file():
        raise FileNotFoundError(f"index file not found: {path}")
    catalog = catalog or build_catalog(root)
    original = path.read_text(encoding="utf-8")
    new_text, rendered, unknown = render_text(original, catalog)
    stale = [
        zone
        for zone, before, after in zip(rendered, _zone_bodies(original), _zone_bodies(new_text))
        if before != after
    ]
    return {"file": str(path), "zones": rendered, "unknown_zones": unknown, "stale_zones": stale, "up_to_date": not stale}


def _zone_bodies(text: str) -> list[str]:
    return [m.group("body") for m in FENCE_RE.finditer(text) if m.group("zone") in RENDERERS]
