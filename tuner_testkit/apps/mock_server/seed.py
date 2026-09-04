"""Turn frozen api_objects into starter mock definitions.

``apps.recorder`` / ``apps.api_recorder`` store the real captured response as ``_RECORDED_RESPONSE``
inside each asset's ``if __name__ == "__main__":`` block. That is a function-local
value, so importing the module cannot reach it — we read it statically with
``ast`` instead, which also avoids executing the replay block.

The recorder shrinks samples before writing them (``truncate_sample``): lists
keep 5 items plus a ``"...(+N more)"`` marker, nesting deeper than 6 collapses
to ``"..."``, and strings over 240 chars are clipped. Markers are stripped here,
but the dropped data is genuinely gone — seeds are a starting point, not a
faithful replica.

Assets without a recorded sample still produce a skeleton from
``response_hints.top_level_keys`` so every route shows up in the control plane.
"""
from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tuner_testkit.api_mock.spec import DEFAULT_SCENARIO, ResponseSpec, RouteMock, mock_relpath
from packages.api_objects.registry import ApiModelRef, iter_api_models
from tuner_testkit.logging import log_info, log_warn

__all__ = ["SeedReport", "extract_recorded_response", "seed_mocks", "strip_truncation_markers"]

_LIST_MARKER_RE = re.compile(r"^\.\.\.\(\+\d+ more\)$")
_DEPTH_MARKER = "..."
_RECORDED_NAME = "_RECORDED_RESPONSE"
_VERSION_RE = re.compile(r"\.v(\d+)\.py$", re.IGNORECASE)


@dataclass
class SeedReport:
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    from_recording: int = 0
    from_hints: int = 0

    @property
    def total(self) -> int:
        return len(self.created) + len(self.skipped) + len(self.failed)


def extract_recorded_response(source: str) -> dict[str, Any] | None:
    """Statically read ``_RECORDED_RESPONSE`` from an asset's source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if _RECORDED_NAME not in names:
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, SyntaxError):
            return None
        return value if isinstance(value, dict) else None
    return None


def strip_truncation_markers(value: Any) -> Any:
    """Drop recorder truncation sentinels so mocks do not serve them as data."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            # A depth sentinel stood in for a nested structure; keep the key so
            # the response shape survives, but do not pretend "..." is a value.
            out[key] = None if item == _DEPTH_MARKER else strip_truncation_markers(item)
        return out
    if isinstance(value, list):
        return [
            strip_truncation_markers(item)
            for item in value
            if not (isinstance(item, str) and (_LIST_MARKER_RE.match(item) or item == _DEPTH_MARKER))
        ]
    return value


def _asset_version(file: str) -> int:
    match = _VERSION_RE.search(file)
    return int(match.group(1)) if match else 1


def _status_from_asserts(ref: ApiModelRef) -> int:
    for operation in ref.model.asserts or []:
        if operation.jsonpath == "$.http_status" and operation.operator == "eq":
            try:
                return int(operation.expected)
            except (TypeError, ValueError):
                continue
    return 200


def _body_from_hints(ref: ApiModelRef) -> Any:
    hints = ref.model.response_hints or {}
    keys = hints.get("top_level_keys")
    if isinstance(keys, list) and keys:
        return {str(key): None for key in keys}
    if hints.get("body") == "binary_or_non_json":
        return None
    return None


def build_route_mock(ref: ApiModelRef, recorded: dict[str, Any] | None) -> tuple[RouteMock, bool]:
    """Build a one-scenario mock. Second element is True when a recording was used."""
    version = _asset_version(ref.file)
    used_recording = False

    if recorded:
        status = int(recorded.get("http_status", 200) or 200)
        is_json = bool(recorded.get("is_json", recorded.get("json") is not None))
        body = strip_truncation_markers(recorded.get("json")) if is_json else None
        headers = {"Content-Type": "application/json"} if is_json else {}
        used_recording = True
        description = "Seeded from the recorded sample (truncated by the recorder)."
    else:
        status = _status_from_asserts(ref)
        body = _body_from_hints(ref)
        headers = {"Content-Type": "application/json"} if body is not None else {}
        description = "Skeleton from response_hints — fill in real values."

    route = RouteMock(
        method=ref.model.method,
        path=ref.model.path,
        id=ref.model.id,
        version=version,
        description=f"{ref.model.name} ({ref.file})",
        active=DEFAULT_SCENARIO,
        scenarios={
            DEFAULT_SCENARIO: ResponseSpec(
                status=status,
                headers=headers,
                body=body,
                description=description,
            )
        },
    )
    return route, used_recording


def seed_mocks(
    mocks_dir: str | Path,
    *,
    root: str | Path | None = None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> SeedReport:
    """Write ``data/mocks/**.json`` for every discovered APIModel."""
    target_dir = Path(mocks_dir)
    repo_root = Path(root) if root is not None else None
    report = SeedReport()

    for ref in iter_api_models(repo_root):
        rel = mock_relpath(ref.model.method, ref.model.path, version=_asset_version(ref.file))
        destination = target_dir / rel
        if destination.exists() and not overwrite:
            report.skipped.append(str(destination))
            continue

        source_file = (repo_root or _repo_root()) / ref.file
        try:
            recorded = extract_recorded_response(source_file.read_text(encoding="utf-8"))
        except OSError as exc:
            log_warn("asset unreadable while seeding", file=ref.file, error=str(exc))
            recorded = None

        try:
            route, used_recording = build_route_mock(ref, recorded)
        except Exception as exc:  # noqa: BLE001 -- report and continue with other assets
            log_warn("seed failed", file=ref.file, error=f"{type(exc).__name__}: {exc}")
            report.failed.append(ref.file)
            continue

        if used_recording:
            report.from_recording += 1
        else:
            report.from_hints += 1

        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                _dump(route),
                encoding="utf-8",
                newline="\n",
            )
        report.created.append(str(destination))

    log_info(
        "mock seed complete",
        created=len(report.created),
        skipped=len(report.skipped),
        failed=len(report.failed),
        dry_run=dry_run,
    )
    return report


def _dump(route: RouteMock) -> str:
    return json.dumps(route.to_json_dict(), ensure_ascii=False, indent=2) + "\n"


def _repo_root() -> Path:
    from tuner_testkit.project import project_root

    return project_root()
