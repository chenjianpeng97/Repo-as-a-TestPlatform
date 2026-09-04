"""Live-merge captures into ``packages/page_objects/<app>/<page_slug>.py``."""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Mapping

from tuner_testkit.logging import log_info, log_warn
from tuner_testkit.page_test.harvest import (
    HarvestedElement,
    as_valid_element,
    locator_fingerprint,
)
from tuner_testkit.page_test.locator import ElementSpec, LocatorPolicy, LocatorSpec
from tuner_testkit.page_test.model import PageFlow, PageModel
from tuner_testkit.page_test.steps import (
    Click,
    Fill,
    Step,
    WaitForElement,
    placeholders_in,
)

from .capture import Capture, page_slug_from_path
from .codegen import asset_variable, render_page_model_source

_SKIP_OVERWRITE = frozenset({"session.py", "plane.py", "pages.py", "__init__.py"})


@dataclass(frozen=True)
class FreezeResult:
    action: str  # "created" | "updated" | "skipped"
    path: Path
    page_id: str
    detail: str = ""


def ensure_app_package(outputs_dir: Path, app: str) -> Path:
    """Create ``outputs_dir/<app>/__init__.py`` without touching the assets root init."""
    outputs_dir.mkdir(parents=True, exist_ok=True)
    app_dir = outputs_dir / app
    app_dir.mkdir(parents=True, exist_ok=True)
    init = app_dir / "__init__.py"
    if not init.exists():
        init.write_text("", encoding="utf-8")
    return app_dir


def asset_path(outputs_dir: Path, app: str, page_slug: str) -> Path:
    return ensure_app_package(outputs_dir, app) / f"{page_slug}.py"


def load_existing_model(path: Path) -> tuple[str, PageModel] | None:
    """Import a declarative ``PageModel`` from an asset file. BasePage-only files → None."""
    if not path.is_file():
        return None
    module_name = f"page_recorder_existing_{path.stem}_{id(path)}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 — unreadable / class-only assets
        log_warn("page_recorder skip unreadable asset", path=str(path), error=str(exc))
        sys.modules.pop(module_name, None)
        return None
    found: list[tuple[str, PageModel]] = []
    for name, value in vars(module).items():
        if isinstance(value, PageModel):
            found.append((name, value))
    sys.modules.pop(module_name, None)
    if not found:
        return None
    return found[0]


def merge_locators(
    existing: tuple[LocatorSpec, ...],
    incoming: tuple[LocatorSpec, ...],
    *,
    max_n: int,
) -> tuple[LocatorSpec, ...]:
    """并集：保留原顺序，不把命中候选提升为首选（自愈级别三禁止）。"""
    seen = {locator_fingerprint(spec) for spec in existing}
    out = list(existing)
    for spec in incoming:
        key = locator_fingerprint(spec)
        if key in seen:
            continue
        seen.add(key)
        out.append(spec)
        if len(out) >= max_n:
            break
    return tuple(out[:max_n])


def _same_collapsible(left: Step, right: Step) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, Click) and isinstance(right, Click):
        return left.element == right.element
    if isinstance(left, Fill) and isinstance(right, Fill):
        return left.element == right.element
    return False


def collapse_steps(steps: Iterable[Step]) -> tuple[Step, ...]:
    """同一按钮连点压成一次 Click；同一输入框连续 Fill 只留最后一次。"""
    out: list[Step] = []
    for step in steps:
        if out and _same_collapsible(out[-1], step):
            if isinstance(step, Fill):
                out[-1] = step
            continue
        out.append(step)
    return tuple(out)


def _filter_step_refs(steps: tuple[Step, ...], elements: Mapping[str, ElementSpec]) -> tuple[Step, ...]:
    kept: list[Step] = []
    for step in steps:
        missing = [name for name in step.elements_used() if name not in elements]
        if missing:
            log_warn("page_recorder drop step, missing element", op=step.op, missing=missing)
            continue
        kept.append(step)
    return tuple(kept)


def _inputs_from_steps(steps: Iterable[Step], existing: Mapping[str, Any] | None = None) -> dict[str, Any]:
    schema = {str(k): dict(v) if isinstance(v, Mapping) else v for k, v in (existing or {}).items()}
    for step in steps:
        for value in step.values_used():
            for token in placeholders_in(value):
                if token.lower().startswith("env:"):
                    continue
                if token not in schema:
                    schema[token] = {"type": "string", "required": False, "note": "recorded by page_recorder"}
    return schema


def _example_params(schema: Mapping[str, Any], existing: Mapping[str, Any] | None = None) -> dict[str, Any]:
    out = dict(existing or {})
    for key in schema:
        if key in out:
            continue
        if key in {"username", "password"} or "password" in key.lower() or "token" in key.lower():
            out[key] = "demo"
        else:
            out[key] = "recorded"
    return out


def _sanitize_elements(
    elements: Mapping[str, ElementSpec],
    *,
    policy: LocatorPolicy,
) -> dict[str, ElementSpec]:
    out: dict[str, ElementSpec] = {}
    for name, spec in elements.items():
        harvested = HarvestedElement(
            name=name,
            locators=spec.locators,
            description=spec.description,
            role_hint=spec.role_hint,
        )
        valid = as_valid_element(harvested, policy=policy)
        if valid is None:
            log_warn("page_recorder drop element (policy)", name=name)
            continue
        out[name] = replace(
            valid,
            name=name,
            description=spec.description or valid.description,
            role_hint=spec.role_hint or valid.role_hint,
            required=spec.required,
        )
    return out


def new_page_model(
    *,
    app: str,
    capture: Capture,
    flow_name: str,
) -> PageModel:
    slug = capture.page_slug or page_slug_from_path(capture.url_path)
    page_id = f"{app}.{slug}@v1"
    title = slug.replace("_", " ")
    return PageModel(
        id=page_id,
        name=title,
        description=(
            "Recorded by apps.page_recorder.\n"
            "notes:\n"
            "  - locators harvested from live DOM; review fragile candidates\n"
            "  - secrets replaced with placeholders; never committed"
        ),
        url_path=capture.url_path or "/",
        elements={},
        flows={},
    )


def merge_capture_into_model(
    model: PageModel,
    capture: Capture,
    *,
    flow_name: str,
) -> PageModel:
    policy = model.policy()
    elements = dict(model.elements)

    if capture.element is not None:
        incoming = as_valid_element(capture.element, policy=policy)
        if incoming is None:
            log_warn(
                "page_recorder skip element (policy)",
                name=capture.element.name,
                dropped=list(capture.element.dropped),
            )
        else:
            name = capture.element.name
            if name in elements:
                merged_locs = merge_locators(
                    elements[name].locators,
                    incoming.locators,
                    max_n=policy.fallback_max_attempts,
                )
                prev = elements[name]
                elements[name] = replace(
                    prev,
                    locators=merged_locs,
                    description=prev.description or incoming.description,
                    role_hint=prev.role_hint or incoming.role_hint,
                )
            else:
                elements[name] = replace(incoming, name=name)

    elements = _sanitize_elements(elements, policy=policy)

    flows = dict(model.flows)
    if capture.step is not None:
        flow = flows.get(flow_name) or PageFlow(
            name=flow_name,
            description="Recorded by apps.page_recorder",
        )
        steps = collapse_steps((*flow.steps, capture.step))
        steps = _filter_step_refs(steps, elements)
        schema = _inputs_from_steps(steps, flow.params_schema)
        flows[flow_name] = replace(
            flow,
            name=flow_name,
            steps=steps,
            params_schema=schema,
            example_params=_example_params(schema, flow.example_params),
        )

    # drop empty flows so validate 不会报「没有任何 step」
    flows = {k: v for k, v in flows.items() if v.steps}

    ready = model.ready
    if not ready:
        first = next(iter(elements), None)
        if first:
            ready = (WaitForElement(first, state="visible"),)

    inputs = _inputs_from_steps(
        (
            *(ready or ()),
            *(step for flow in flows.values() for step in flow.steps),
        ),
        model.inputs_schema,
    )
    return replace(
        model,
        elements=elements,
        flows=flows,
        ready=ready,
        inputs_schema=inputs,
        url_path=model.url_path or capture.url_path or "/",
    )


class PageObjectFreezer:
    """Create/update page assets under ``outputs_dir/<app>/``."""

    def __init__(self, outputs_dir: Path, *, app: str, flow: str = "recorded") -> None:
        self.outputs_dir = outputs_dir.resolve()
        self.app = app
        self.flow = flow
        self._cache: dict[Path, tuple[str, PageModel]] = {}
        self.results: list[FreezeResult] = []
        self.touched_ids: list[str] = []

    def freeze(self, capture: Capture) -> FreezeResult:
        slug = capture.page_slug or page_slug_from_path(capture.url_path)
        path = asset_path(self.outputs_dir, self.app, slug)
        if path.name in _SKIP_OVERWRITE:
            return FreezeResult(action="skipped", path=path, page_id="", detail="reserved name")

        loaded = self._cache.get(path)
        if loaded is None:
            loaded = load_existing_model(path)

        created = loaded is None
        if loaded is None:
            if path.exists():
                # 已有文件但不是 PageModel（例如 BasePage）——不覆盖
                log_warn("page_recorder skip non-PageModel asset", path=str(path))
                result = FreezeResult(
                    action="skipped",
                    path=path,
                    page_id="",
                    detail="existing file is not a PageModel",
                )
                self.results.append(result)
                return result
            variable = asset_variable(slug)
            model = new_page_model(app=self.app, capture=capture, flow_name=self.flow)
        else:
            variable, model = loaded

        merged = merge_capture_into_model(model, capture, flow_name=self.flow)
        problems = merged.validate()
        if problems:
            # 再滤一遍元素后复检；仍失败则丢掉过不了的候选元素
            merged = replace(
                merged,
                elements=_sanitize_elements(merged.elements, policy=merged.policy()),
            )
            merged = replace(
                merged,
                ready=_filter_step_refs(merged.ready, merged.elements),
                flows={
                    k: replace(v, steps=_filter_step_refs(v.steps, merged.elements))
                    for k, v in merged.flows.items()
                    if _filter_step_refs(v.steps, merged.elements)
                },
            )
            leftover = merged.validate()
            if leftover:
                log_warn("page_recorder validate warnings", page_id=merged.id, problems=leftover)

        var, source = render_page_model_source(
            merged,
            variable=variable,
            replay_flow=self.flow if self.flow in merged.flows else None,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8", newline="\n")
        self._cache[path] = (var, merged)

        added = []
        if capture.element is not None:
            added.append(f"+{capture.element.name}")
        if capture.step is not None:
            added.append(capture.step.op + (f" {capture.step.elements_used()[0]}" if capture.step.elements_used() else ""))
        detail = " ".join(added).strip()
        result = FreezeResult(
            action="created" if created else "updated",
            path=path,
            page_id=merged.id,
            detail=detail,
        )
        self.results.append(result)
        if merged.id not in self.touched_ids:
            self.touched_ids.append(merged.id)
        log_info(
            f"[page_recorder] merged {merged.id} {detail}".rstrip(),
            action=result.action,
            path=str(path),
        )
        return result

    def current_elements(self, url_path: str) -> dict[str, ElementSpec]:
        slug = page_slug_from_path(url_path)
        path = asset_path(self.outputs_dir, self.app, slug)
        cached = self._cache.get(path)
        if cached:
            return dict(cached[1].elements)
        loaded = load_existing_model(path)
        if loaded:
            self._cache[path] = loaded
            return dict(loaded[1].elements)
        return {}
