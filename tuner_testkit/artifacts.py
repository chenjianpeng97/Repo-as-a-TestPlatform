"""Run-level artifacts: ``artifacts/<kind>/<run_id>/manifest.json`` (docs/spec/artifacts-layout.md).

Two audiences:

* tool runners (``tuner-workspace run``, the workbench) — :func:`start_run` /
  :meth:`RunManifest.finish`;
* behave ``*_environment.py`` hooks — :func:`report_run_begin` /
  :func:`report_scenario_end` / :func:`report_run_end` collect a
  ``summary.json`` under ``artifacts/reports/<run_id>/`` and write the manifest.

Sensitive parameter values (``*password*``, ``*token*`` …) are masked before
they hit disk.
"""
from __future__ import annotations

import json
import os
import platform
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

MANIFEST_VERSION = 1
MANIFEST_NAME = "manifest.json"
RunKind = Literal["run", "report", "evidence"]
RunStatus = Literal["running", "succeeded", "failed", "cancelled"]
SENSITIVE_KEY_RE = re.compile(r"(password|passwd|token|secret|cookie|authorization|session|api[_-]?key)", re.I)
SLUG_RE = re.compile(r"[^a-z0-9]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(text: str) -> str:
    slug = SLUG_RE.sub("-", text.lower()).strip("-")
    return slug[:48] or "run"


def new_run_id(slug: str, *, now: datetime | None = None) -> str:
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{slugify(slug)}"


def mask_params(params: dict[str, Any] | None) -> dict[str, Any]:
    """Replace values of sensitive keys with ``***`` (recursively)."""
    if not params:
        return {}
    out: dict[str, Any] = {}
    for key, value in params.items():
        if SENSITIVE_KEY_RE.search(str(key)):
            out[key] = "***"
        elif isinstance(value, dict):
            out[key] = mask_params(value)
        else:
            out[key] = value
    return out


class ManifestFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(description="relative to the run directory")
    kind: str = Field("other", description="log / report / envelope / screenshot / json / other")
    bytes: int = Field(0, ge=0)


class Producer(BaseModel):
    model_config = ConfigDict(extra="allow")

    tool_id: str | None = None
    suite: str | None = None
    argv: list[str] = Field(default_factory=list)
    user_email: str | None = None
    host: str | None = None
    kit_version: str | None = None


class RunManifest(BaseModel):
    """The on-disk contract; ``dir`` is runtime-only (excluded from JSON)."""

    model_config = ConfigDict(extra="forbid")

    manifest_version: int = MANIFEST_VERSION
    kind: RunKind = "run"
    run_id: str
    producer: Producer = Field(default_factory=Producer)
    params: dict[str, Any] = Field(default_factory=dict)
    started: str = Field(default_factory=utc_now)
    ended: str | None = None
    status: RunStatus = "running"
    exit_code: int | None = None
    files: list[ManifestFile] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    dir: Path | None = Field(default=None, exclude=True)

    # ---- persistence -----------------------------------------------------
    @property
    def path(self) -> Path:
        if self.dir is None:
            raise ValueError("manifest has no directory; call start_run() or set .dir")
        return self.dir / MANIFEST_NAME

    def write(self) -> Path:
        self.params = mask_params(self.params)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return self.path

    def refresh_files(self) -> None:
        """Re-list files in the run dir (excluding the manifest itself)."""
        if self.dir is None or not self.dir.is_dir():
            return
        rows: list[ManifestFile] = []
        for path in sorted(self.dir.rglob("*")):
            if not path.is_file() or path.name == MANIFEST_NAME:
                continue
            rel = path.relative_to(self.dir).as_posix()
            rows.append(ManifestFile(path=rel, kind=_guess_kind(rel), bytes=path.stat().st_size))
        self.files = rows

    def finish(self, status: RunStatus, *, exit_code: int | None = None, summary: dict[str, Any] | None = None) -> Path:
        self.status = status
        self.exit_code = exit_code
        self.ended = utc_now()
        if summary is not None:
            self.summary = summary
        self.refresh_files()
        return self.write()

    @classmethod
    def load(cls, run_dir: Path) -> "RunManifest":
        data = json.loads((run_dir / MANIFEST_NAME).read_text(encoding="utf-8"))
        manifest = cls.model_validate(data)
        manifest.dir = run_dir
        return manifest


def _guess_kind(rel: str) -> str:
    lower = rel.lower()
    if lower.endswith((".log", ".txt")):
        return "log"
    if lower.endswith((".html", ".xml", ".junit")) or "report" in lower:
        return "report"
    if lower.endswith("envelope.json"):
        return "envelope"
    if lower.endswith((".png", ".jpg", ".jpeg")):
        return "screenshot"
    if lower.endswith((".json", ".jsonl")):
        return "json"
    return "other"


def default_producer(root: Path | None, **extra: Any) -> Producer:
    from tuner_testkit.catalog.scan import git_config_value

    try:
        from importlib.metadata import version

        kit_version: str | None = version("tuner-testkit")
    except Exception:  # noqa: BLE001
        kit_version = None
    email = git_config_value(root, "user.email") if root is not None else None
    return Producer(user_email=email, host=platform.node() or None, kit_version=kit_version, **extra)


def start_run(
    kind: RunKind,
    slug: str,
    *,
    root: Path | None = None,
    run_id: str | None = None,
    producer: Producer | None = None,
    params: dict[str, Any] | None = None,
    base_dir: Path | None = None,
) -> RunManifest:
    """Create ``artifacts/<kind>s/<run_id>/`` and write a ``running`` manifest."""
    from tuner_testkit.project import artifacts_dir, project_root

    repo = Path(root).resolve() if root is not None else project_root()
    if base_dir is None:
        area = {"run": "runs", "report": "reports", "evidence": "evidence"}[kind]
        old_root = os.environ.get("TUNER_ROOT")
        os.environ["TUNER_ROOT"] = str(repo)
        try:
            base_dir = artifacts_dir(area)
        finally:
            if old_root is None:
                os.environ.pop("TUNER_ROOT", None)
            else:
                os.environ["TUNER_ROOT"] = old_root
    rid = run_id or new_run_id(slug)
    manifest = RunManifest(
        kind=kind,
        run_id=rid,
        producer=producer or default_producer(repo),
        params=mask_params(params),
        dir=base_dir / rid,
    )
    manifest.write()
    return manifest


# ---------------------------------------------------------------------------
# behave report collector (call from tests/features/<stage>_environment.py)
# ---------------------------------------------------------------------------
def report_run_begin(context: Any, *, root: Path | None = None) -> RunManifest:
    """Start ``artifacts/reports/<run_id>/`` for a behave run and attach it to ``context.report_manifest``.

    Honours ``TUNER_REPORT_DIR`` (use that directory as the run dir) and ``TUNER_RUN_ID``.
    """
    stage = (getattr(getattr(context, "config", None), "stage", None) or "run").strip() or "run"
    report_dir = os.environ.get("TUNER_REPORT_DIR")
    run_id = os.environ.get("TUNER_RUN_ID")
    if report_dir:
        base = Path(report_dir)
        manifest = RunManifest(
            kind="report",
            run_id=run_id or base.name,
            producer=default_producer(root, suite=f"behave --stage {stage}"),
            dir=base,
        )
        manifest.write()
    else:
        manifest = start_run("report", f"behave-{stage}", root=root, run_id=run_id, producer=default_producer(root, suite=f"behave --stage {stage}"))
    context.report_manifest = manifest
    context.report_rows = []
    return manifest


def report_scenario_end(context: Any, scenario: Any) -> None:
    rows = getattr(context, "report_rows", None)
    if rows is None:
        return
    feature = getattr(scenario, "feature", None)
    status = getattr(scenario, "status", None)
    rows.append(
        {
            "feature": getattr(feature, "name", "") if feature else "",
            "scenario": getattr(scenario, "name", ""),
            "tags": list(getattr(scenario, "tags", []) or []),
            "status": str(getattr(status, "name", status) or "unknown").lower(),
            "duration": round(float(getattr(scenario, "duration", 0.0) or 0.0), 3),
        }
    )


def report_run_end(context: Any) -> RunManifest | None:
    manifest: RunManifest | None = getattr(context, "report_manifest", None)
    if manifest is None or manifest.dir is None:
        return None
    rows: list[dict[str, Any]] = getattr(context, "report_rows", []) or []
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    summary = {
        "total": len(rows),
        "passed": counts.get("passed", 0),
        "failed": counts.get("failed", 0) + counts.get("error", 0),
        "skipped": counts.get("skipped", 0) + counts.get("untested", 0),
        "by_status": counts,
    }
    (manifest.dir / "summary.json").write_text(
        json.dumps({"run_id": manifest.run_id, "summary": summary, "scenarios": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    failed = getattr(context, "failed", None)
    if failed is None:
        failed = summary["failed"] > 0
    manifest.finish("failed" if failed else "succeeded", exit_code=1 if failed else 0, summary=summary)
    return manifest
