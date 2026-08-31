"""Mock definition schema: what a route returns, per scenario.

The response contract lives **outside** ``APIModel`` on purpose. ``APIModel``
describes the request contract plus stable asserts; its ``response_hints`` only
carries top-level key names (see ``apps.recorder.codegen.build_response_hints``)
and its asserts are assertions, not a response definition. Keeping mock bodies
in ``data/mocks/`` therefore leaves ``packages.api_test`` untouched and keeps
scenario data out of the route assets.

One file per ``method + path``, mirroring the api_objects route tree::

    packages/api_objects/prod-api/inout/report/his/queryInoutHis/POST.v1.py
    data/mocks/prod-api/inout/report/his/queryInoutHis/POST.v1.json
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .errors import MockSpecError

__all__ = [
    "DEFAULT_SCENARIO",
    "ResponseSpec",
    "RouteMock",
    "mock_relpath",
    "route_key",
    "scan_sensitive",
]

DEFAULT_SCENARIO = "success"

# Mirrors docs/spec/api-objects-syntax.md: these must never be persisted with a
# real value. Mock data is fake by definition, but the repo-wide rule is that
# nothing resembling a credential lands in git, so persistence warns on these.
_SENSITIVE_KEY_RE = re.compile(r"(authorization|cookie|token|secret|password|session)", re.IGNORECASE)
_PLACEHOLDER_VALUES = {"", "***", "mock", "fake", "dummy", "changeme"}


class ResponseSpec(BaseModel):
    """One canned response."""

    model_config = ConfigDict(extra="forbid")

    status: int = Field(200, ge=100, le=599)
    headers: dict[str, str] = Field(default_factory=dict)
    body: Any = Field(None, description="dict/list -> JSON; str -> raw text; None -> empty")
    delay_ms: int = Field(0, ge=0, le=60_000, description="Simulated latency before responding")
    description: str | None = None

    @property
    def is_json(self) -> bool:
        return isinstance(self.body, (dict, list))


class RouteMock(BaseModel):
    """Every scenario for a single ``method + path``, plus which one is live."""

    model_config = ConfigDict(extra="forbid")

    method: str
    path: str
    scenarios: dict[str, ResponseSpec] = Field(default_factory=dict)
    active: str = DEFAULT_SCENARIO
    id: str | None = Field(None, description="Source APIModel id, when seeded from an asset")
    version: int = Field(1, ge=1, description="Matches the asset's <METHOD>.v<N> suffix")
    description: str | None = None

    @field_validator("method")
    @classmethod
    def _upper_method(cls, value: str) -> str:
        method = str(value or "").strip().upper()
        if not method.isalpha():
            raise ValueError(f"invalid HTTP method: {value!r}")
        return method

    @field_validator("path")
    @classmethod
    def _leading_slash(cls, value: str) -> str:
        path = str(value or "").strip()
        if not path:
            raise ValueError("path must not be empty")
        if "://" in path:
            raise ValueError(f"path must not contain a host: {path!r}")
        return path if path.startswith("/") else "/" + path

    @model_validator(mode="after")
    def _active_exists(self) -> "RouteMock":
        if self.scenarios and self.active not in self.scenarios:
            raise ValueError(
                f"active scenario {self.active!r} is not defined "
                f"(have: {sorted(self.scenarios)})"
            )
        return self

    @property
    def route_key(self) -> str:
        return route_key(self.method, self.path)

    def active_response(self) -> ResponseSpec | None:
        return self.scenarios.get(self.active)

    def to_json_dict(self) -> dict[str, Any]:
        """Serialise for ``data/mocks/**.json``.

        ``body`` is kept even when ``null`` — an empty response (204 and
        friends) is a real definition, not an unset field. Only optional
        metadata is dropped so files stay readable.
        """
        data = self.model_dump(mode="json")
        for key in ("id", "description"):
            if data.get(key) is None:
                data.pop(key, None)
        for scenario in data.get("scenarios", {}).values():
            if isinstance(scenario, dict) and scenario.get("description") is None:
                scenario.pop("description", None)
        return data

    @classmethod
    def from_json_dict(cls, data: Any, *, source: str = "<memory>") -> "RouteMock":
        if not isinstance(data, dict):
            raise MockSpecError(f"{source}: mock definition must be a JSON object")
        try:
            return cls.model_validate(data)
        except Exception as exc:  # noqa: BLE001 -- surface pydantic detail with the file name
            raise MockSpecError(f"{source}: {exc}") from exc


def route_key(method: str, path: str) -> str:
    """Canonical ``"METHOD /path"`` identity used across store, router, admin."""
    normalized = str(path or "/").strip()
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    return f"{str(method).strip().upper()} {normalized}"


def mock_relpath(method: str, path: str, *, version: int = 1) -> PurePosixPath:
    """Route-tree-relative location of a mock file, e.g.
    ``prod-api/inout/report/his/queryInoutHis/POST.v1.json``."""
    segments = [seg for seg in str(path or "").split("/") if seg]
    filename = f"{str(method).strip().upper()}.v{int(version)}.json"
    return PurePosixPath(*segments, filename) if segments else PurePosixPath(filename)


def scan_sensitive(route: RouteMock) -> list[str]:
    """Report header names / body keys that look like real credentials.

    Used to warn before writing to disk. Placeholder values (``***`` etc.)
    are ignored so recorder-sanitised seeds stay quiet.
    """
    hits: list[str] = []
    for name, response in route.scenarios.items():
        for header, value in response.headers.items():
            if _SENSITIVE_KEY_RE.search(header) and not _is_placeholder(value):
                hits.append(f"{name}.headers.{header}")
        hits.extend(f"{name}.body.{loc}" for loc in _scan_body(response.body))
    return hits


def _is_placeholder(value: Any) -> bool:
    return str(value).strip().lower() in _PLACEHOLDER_VALUES


def _scan_body(body: Any, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(body, dict):
        for key, value in body.items():
            loc = f"{prefix}.{key}" if prefix else str(key)
            if _SENSITIVE_KEY_RE.search(str(key)) and not isinstance(value, (dict, list)):
                if not _is_placeholder(value):
                    hits.append(loc)
                continue
            hits.extend(_scan_body(value, loc))
    elif isinstance(body, list):
        for index, item in enumerate(body):
            hits.extend(_scan_body(item, f"{prefix}[{index}]"))
    return hits
