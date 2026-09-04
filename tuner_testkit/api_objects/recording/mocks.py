"""Write the **untruncated** response sample as a mock definition.

The asset file's ``_RECORDED_RESPONSE`` is deliberately shrunk by
``codegen.truncate_sample`` (5 list items, depth 6, 240-char strings) — Python
source has to stay readable and diffable. That makes it a poor source for
``apps.mock_server``: seeding from it yields 5-row lists and ``null`` holes
where nested structures were cut.

``Capture.response_body`` still holds the **whole** sanitized body at freeze
time, so this writer saves it verbatim to ``data/mocks/**.json`` alongside the
asset. Same route tree, same ``v<N>`` suffix::

    packages/api_objects/prod-api/inout/report/his/queryInoutHis/POST.v1.py
    data/mocks/          prod-api/inout/report/his/queryInoutHis/POST.v1.json

Safety note: the body written here went through ``sanitize.sanitize_mapping``
in ``build_capture`` — credential-shaped keys are already ``***`` and JWTs /
emails / phone numbers are masked. This writer adds no new exposure, but it
does persist *more rows* of real business data than the asset does, so treat
``data/mocks/`` with the same care as any other captured artifact.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tuner_testkit.api_mock.spec import DEFAULT_SCENARIO, ResponseSpec, RouteMock, mock_relpath
from tuner_testkit.api_mock.errors import MockSpecError

from .capture import Capture
from .normalize import DEFAULT_TOOL

__all__ = ["DEFAULT_MAX_BYTES", "MockSampleWriter", "MockWriteResult"]

DEFAULT_MAX_BYTES = 1_048_576  # 1 MiB of JSON per route; guards against huge captures


@dataclass(frozen=True)
class MockWriteResult:
    action: str  # "created" | "updated" | "skipped"
    path: Path
    detail: str = ""


class MockSampleWriter:
    """Persist full response samples next to the frozen assets."""

    def __init__(
        self,
        mocks_dir: Path,
        *,
        scenario: str = DEFAULT_SCENARIO,
        max_bytes: int = DEFAULT_MAX_BYTES,
        tool: str = DEFAULT_TOOL,
    ) -> None:
        self.mocks_dir = Path(mocks_dir).resolve()
        self.scenario = scenario or DEFAULT_SCENARIO
        self.max_bytes = int(max_bytes)
        self.tool = (tool or DEFAULT_TOOL).strip() or DEFAULT_TOOL
        self.mocks_dir.mkdir(parents=True, exist_ok=True)

    def write(self, capture: Capture, *, version: int = 1, asset_id: str | None = None) -> MockWriteResult:
        target = self.mocks_dir / mock_relpath(
            capture.method, capture.normalized_path, version=max(1, version)
        )

        body = capture.response_body if capture.response_is_json else None
        if body is not None and self.max_bytes > 0:
            size = len(json.dumps(body, ensure_ascii=False).encode("utf-8"))
            if size > self.max_bytes:
                return MockWriteResult(
                    action="skipped",
                    path=target,
                    detail=f"response {size} bytes exceeds --mock-max-bytes {self.max_bytes}",
                )

        response = ResponseSpec(
            status=capture.response_status,
            headers=self._response_headers(capture),
            body=body,
            description=(
                f"Full sample recorded by apps.{self.tool} at "
                f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}"
                + ("" if capture.response_is_json else " (non-JSON response: body not captured)")
            ),
        )

        existing = self._load(target)
        if existing is None:
            route = RouteMock(
                method=capture.method,
                path=capture.normalized_path,
                id=asset_id,
                version=max(1, version),
                description=f"Recorded by apps.{self.tool} from {capture.method} {capture.path}",
                active=self.scenario,
                scenarios={self.scenario: response},
            )
            self._dump(target, route)
            return MockWriteResult(action="created", path=target, detail=f"scenario {self.scenario!r}")

        # Refresh only our scenario; hand-authored ones (empty / boom / ...) and
        # whichever scenario the user left active must survive a re-record.
        scenarios = {**existing.scenarios, self.scenario: response}
        active = existing.active if existing.active in scenarios else self.scenario
        route = existing.model_copy(
            update={
                "scenarios": scenarios,
                "active": active,
                "id": existing.id or asset_id,
            }
        )
        self._dump(target, route)
        detail = f"scenario {self.scenario!r} refreshed"
        if active != self.scenario:
            detail += f"; active stays {active!r}"
        return MockWriteResult(action="updated", path=target, detail=detail)

    @staticmethod
    def _response_headers(capture: Capture) -> dict[str, str]:
        """Only Content-Type. Replaying Content-Length / Transfer-Encoding from a
        different body would desync the client."""
        for key, value in (capture.response_headers or {}).items():
            if str(key).lower() == "content-type":
                return {"Content-Type": str(value)}
        return {"Content-Type": "application/json"} if capture.response_is_json else {}

    @staticmethod
    def _load(target: Path) -> RouteMock | None:
        if not target.is_file():
            return None
        try:
            return RouteMock.from_json_dict(
                json.loads(target.read_text(encoding="utf-8")), source=str(target)
            )
        except (OSError, json.JSONDecodeError, MockSpecError):
            # Unreadable or hand-edited beyond parsing: start over rather than lose the capture.
            return None

    @staticmethod
    def _dump(target: Path, route: RouteMock) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(route.to_json_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
