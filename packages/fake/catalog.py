"""Fake generator registry, catalog export, and batch ``run()``.

Each generator produces **one** value. ``count`` belongs to the runner so
CLI / future platform pages / business code share one contract.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

GS = "\x1d"
COUNT_MAX = 1000
_UNIQUE_ATTEMPT_FACTOR = 80


class EmptyInputs(BaseModel):
    """No generator-specific fields (``count`` / ``seed`` stay on the runner)."""

    model_config = ConfigDict(extra="forbid")


class FakeRunRequest(BaseModel):
    fake_id: str = Field(description="catalog 键，如 udi")
    count: int = Field(1, ge=1, le=COUNT_MAX, description="生成条数（runner 层）")
    inputs: dict[str, Any] = Field(default_factory=dict, description="该 fake_id 的 Inputs")
    seed: int | None = Field(None, description="可选；与 packages.fake.seed 相同")
    unique: bool = Field(True, description="批量去重")


class FakeRunResult(BaseModel):
    fake_id: str
    count: int
    values: list[Any] = Field(description="业务主数据（UDI 含真 GS 字符）")
    display_values: list[str] = Field(description="CLI/页面粘贴用（GS 已转义）")


@dataclass(frozen=True, slots=True)
class FakeSpec:
    fake_id: str
    name: str
    category: str
    inputs_model: type[BaseModel]
    func: Callable[..., Any]
    example_inputs: dict[str, Any]
    returns: str


_REGISTRY: dict[str, FakeSpec] = {}
_discovered = False


def register(
    fake_id: str,
    *,
    name: str,
    category: str,
    inputs: type[BaseModel] | None = None,
    example: dict[str, Any] | None = None,
    returns: str = "string",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register a single-value generator. ``inputs`` must not include ``count``."""

    model = inputs or EmptyInputs

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if "count" in model.model_fields:
            raise ValueError(f"{fake_id}: Inputs 禁止包含 count（条数在 runner 层）")
        existing = _REGISTRY.get(fake_id)
        if existing is not None and existing.func is not func:
            raise ValueError(f"fake_id 重复注册: {fake_id}")
        _REGISTRY[fake_id] = FakeSpec(
            fake_id=fake_id,
            name=name,
            category=category,
            inputs_model=model,
            func=func,
            example_inputs=dict(example or {}),
            returns=returns,
        )
        return func

    return decorator


def discover() -> None:
    """Import generator modules so ``@register`` runs. Idempotent."""
    global _discovered
    if _discovered:
        return
    _discovered = True
    from packages.fake import china as _china  # noqa: F401
    from packages.fake import core as _core  # noqa: F401
    from packages.fake import medical as _medical  # noqa: F401
    from packages.fake import wrappers as _wrappers  # noqa: F401


def get(fake_id: str) -> FakeSpec:
    discover()
    spec = _REGISTRY.get(fake_id)
    if spec is None:
        known = ", ".join(sorted(_REGISTRY)) or "(empty)"
        raise KeyError(f"未注册的 fake_id: {fake_id}（已注册: {known}）")
    return spec


def describe(fake_id: str) -> dict[str, Any]:
    spec = get(fake_id)
    return {
        "id": spec.fake_id,
        "name": spec.name,
        "category": spec.category,
        "params_schema": spec.inputs_model.model_json_schema(),
        "example_inputs": spec.example_inputs,
        "returns": spec.returns,
    }


def catalog() -> list[dict[str, Any]]:
    discover()
    return [describe(fake_id) for fake_id in sorted(_REGISTRY)]


def to_display(value: Any, *, gs_repr: str = "escape") -> str:
    if isinstance(value, bool):
        text = "true" if value else "false"
    elif isinstance(value, Decimal):
        text = format(value, "f")
    elif isinstance(value, datetime):
        text = value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, date):
        text = value.isoformat()
    else:
        text = str(value)
    if gs_repr == "escape":
        return text.replace(GS, "\\x1d")
    return text


def _unique_key(value: Any) -> str:
    return to_display(value, gs_repr="raw")


def run(
    fake_id: str,
    *,
    count: int = 1,
    inputs: dict[str, Any] | None = None,
    seed: int | None = None,
    unique: bool = True,
    gs_repr: str = "escape",
) -> FakeRunResult:
    req = FakeRunRequest(
        fake_id=fake_id,
        count=count,
        inputs=inputs or {},
        seed=seed,
        unique=unique,
    )
    spec = get(req.fake_id)
    if req.seed is not None:
        from packages.fake.core import seed as seed_rng

        seed_rng(req.seed)

    params = spec.inputs_model.model_validate(req.inputs)
    kwargs = params.model_dump()
    values: list[Any] = []
    seen: set[str] = set()
    attempts = 0
    limit = req.count * _UNIQUE_ATTEMPT_FACTOR
    while len(values) < req.count:
        attempts += 1
        if attempts > limit:
            raise RuntimeError(
                f"{req.fake_id}: 无法在 {limit} 次尝试内生成 {req.count} 条"
                f"{'唯一' if req.unique else ''}数据（请放宽 unique 或 inputs）"
            )
        value = spec.func(**kwargs)
        key = _unique_key(value)
        if req.unique and key in seen:
            continue
        seen.add(key)
        values.append(value)

    return FakeRunResult(
        fake_id=req.fake_id,
        count=len(values),
        values=values,
        display_values=[to_display(v, gs_repr=gs_repr) for v in values],
    )
