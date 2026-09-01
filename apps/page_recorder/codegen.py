"""Render declarative ``PageModel`` Python source (no BasePage)."""
from __future__ import annotations

import json
import re
from typing import Any, Mapping

from packages.page_objects.session import MAIN_BLOCK_TEMPLATE
from packages.page_test.locator import ElementSpec, LocatorSpec
from packages.page_test.model import PageFlow, PageModel
from packages.page_test.steps import Step

_IDENT_RE = re.compile(r"[^a-z0-9_]+")


def _py_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _py_bool(value: bool) -> str:
    return "True" if value else "False"


def asset_variable(page_slug: str, major: int = 1) -> str:
    slug = _IDENT_RE.sub("_", (page_slug or "page").lower()).strip("_") or "page"
    if slug[0].isdigit():
        slug = "p_" + slug
    return f"{slug}_page_v{major}"


def _render_locator(spec: LocatorSpec) -> str:
    parts = [_py_str(spec.strategy), _py_str(spec.value)]
    if spec.name is not None:
        parts.append(f"name={_py_str(spec.name)}")
    if spec.exact is not None:
        parts.append(f"exact={_py_bool(spec.exact)}")
    if spec.has_text is not None:
        parts.append(f"has_text={_py_str(spec.has_text)}")
    if spec.nth is not None:
        parts.append(f"nth={spec.nth}")
    if spec.first:
        parts.append("first=True")
    if spec.scope:
        parts.append(f"scope={_py_str(spec.scope)}")
    if spec.confidence != "stable":
        parts.append(f"confidence={_py_str(spec.confidence)}")
    if spec.note:
        parts.append(f"note={_py_str(spec.note)}")
    return f"LocatorSpec({', '.join(parts)})"


def _render_element(spec: ElementSpec) -> str:
    loc_lines = ",\n            ".join(_render_locator(loc) for loc in spec.locators)
    loc_block = f"(\n            {loc_lines},\n        )" if spec.locators else "()"
    fields = [
        f"name={_py_str(spec.name)}",
        f"description={_py_str(spec.description)}" if spec.description else "",
        f"role_hint={_py_str(spec.role_hint)}" if spec.role_hint else "",
        f"locators={loc_block}",
    ]
    if not spec.required:
        fields.append("required=False")
    inner = ",\n        ".join(f for f in fields if f)
    return f"ElementSpec(\n        {inner},\n    )"


def _render_step(step: Step) -> str:
    payload = step.to_dict()
    op = type(step).__name__
    payload.pop("op", None)
    positional: list[str] = []
    keywords: list[str] = []
    # Common shapes: element first, then value/option/key/pattern
    if "element" in payload:
        positional.append(_py_str(str(payload.pop("element"))))
    if "value" in payload:
        value = payload.pop("value")
        positional.append(_py_str(value) if isinstance(value, str) else repr(value))
    if "option" in payload:
        option = payload.pop("option")
        positional.append(_py_str(option) if isinstance(option, str) else repr(option))
    if "key" in payload:
        positional.append(_py_str(str(payload.pop("key"))))
    if "pattern" in payload:
        positional.append(_py_str(str(payload.pop("pattern"))))
    if "path" in payload and payload["path"] is not None:
        keywords.append(f"path={_py_str(str(payload.pop('path')))}")
    if "path_contains" in payload:
        keywords.append(f"path_contains={_py_str(str(payload.pop('path_contains')))}")
    if "variable" in payload:
        keywords.append(f"variable={_py_str(str(payload.pop('variable')))}")
    if "attribute" in payload:
        keywords.append(f"attribute={_py_str(str(payload.pop('attribute')))}")
    if "expected" in payload:
        expected = payload.pop("expected")
        keywords.append(
            f"expected={_py_str(expected) if isinstance(expected, str) else repr(expected)}"
        )
    for key, value in payload.items():
        if value is None:
            continue
        if isinstance(value, bool):
            # omit defaults already dropped by to_dict
            keywords.append(f"{key}={_py_bool(value)}")
        elif isinstance(value, (int, float)):
            keywords.append(f"{key}={value!r}")
        elif isinstance(value, str):
            keywords.append(f"{key}={_py_str(value)}")
        else:
            keywords.append(f"{key}={value!r}")
    args = ", ".join([*positional, *keywords])
    return f"{op}({args})"


def _render_steps(steps: tuple[Step, ...], *, indent: int = 8) -> str:
    pad = " " * indent
    if not steps:
        return "()"
    lines = ",\n".join(f"{pad}{_render_step(step)}" for step in steps)
    return f"(\n{lines},\n{' ' * (indent - 4)})"


def _render_schema(schema: Mapping[str, Any], *, indent: int = 4) -> str:
    if not schema:
        return "{}"
    pad = " " * indent
    inner_pad = " " * (indent + 4)
    lines = ["{"]
    for key, value in schema.items():
        if isinstance(value, Mapping):
            items = ", ".join(
                f"{_py_str(str(k))}: {json.dumps(v, ensure_ascii=False) if isinstance(v, str) else repr(v)}"
                for k, v in value.items()
            )
            lines.append(f"{inner_pad}{_py_str(str(key))}: {{{items}}},")
        else:
            lines.append(f"{inner_pad}{_py_str(str(key))}: {value!r},")
    lines.append(f"{pad}}}")
    return "\n".join(lines)


def _render_flow(flow: PageFlow) -> str:
    parts = [
        f"name={_py_str(flow.name)}",
        f"description={_py_str(flow.description)}" if flow.description else "",
        f"params_schema={_render_schema(flow.params_schema, indent=12)}"
        if flow.params_schema
        else "",
        f"steps={_render_steps(flow.steps, indent=12)}",
        f"example_params={_render_schema(flow.example_params, indent=12)}"
        if flow.example_params
        else "",
    ]
    inner = ",\n            ".join(p for p in parts if p)
    return f"PageFlow(\n            {inner},\n        )"


def _collect_imports(model: PageModel) -> list[str]:
    names = {
        "ElementSpec",
        "LocatorSpec",
        "PageModel",
    }
    if model.flows:
        names.add("PageFlow")
    for steps in (model.ready, model.asserts, model.extracts):
        for step in steps:
            names.add(type(step).__name__)
    for flow in model.flows.values():
        for step in flow.steps:
            names.add(type(step).__name__)
    return sorted(names)


def render_page_model_source(
    model: PageModel,
    *,
    variable: str | None = None,
    replay_flow: str | None = None,
) -> tuple[str, str]:
    """Return ``(variable_name, python_source)``."""
    slug = model.id.split("@", 1)[0].rsplit(".", 1)[-1] if model.id else "page"
    var = variable or asset_variable(slug)
    flow_name = replay_flow
    if flow_name is None:
        flow_name = next(iter(model.flows), None)

    imports = _collect_imports(model)
    import_block = "from packages.page_test import (\n    " + ",\n    ".join(imports) + ",\n)"

    el_items = []
    for name, spec in model.elements.items():
        el_items.append(f"        {_py_str(name)}: {_render_element(spec)},")
    elements_src = "{\n" + "\n".join(el_items) + "\n    }" if el_items else "{}"

    flow_items = []
    for name, flow in model.flows.items():
        flow_items.append(f"        {_py_str(name)}: {_render_flow(flow)},")
    flows_src = "{\n" + "\n".join(flow_items) + "\n    }" if flow_items else "{}"

    ready_src = _render_steps(model.ready, indent=8)
    policy_line = ""
    if model.locator_policy:
        policy_line = f"    locator_policy={_render_schema(model.locator_policy)},\n"
    auth_line = ""
    if model.auth_policy:
        auth_line = f"    auth_policy={_render_schema(model.auth_policy)},\n"
    inputs_line = ""
    if model.inputs_schema:
        inputs_line = f"    inputs_schema={_render_schema(model.inputs_schema)},\n"

    description = model.description or (
        "Recorded by apps.page_recorder.\n"
        "notes:\n"
        "  - locators harvested from live DOM; review fragile candidates\n"
        "  - secrets replaced with {{placeholders}}; never committed"
    )

    main_block = MAIN_BLOCK_TEMPLATE.format(variable=var, flow=flow_name)

    source = f'''\
"""Auto-maintained by apps.page_recorder — do not commit secrets."""

{import_block}

{var} = PageModel(
    id={_py_str(model.id)},
    name={_py_str(model.name)},
    description={_py_str(description)},
    url_path={_py_str(model.url_path)},
    elements={elements_src},
{inputs_line}    ready={ready_src},
    flows={flows_src},
{policy_line}{auth_line})
{main_block}'''
    return var, source


__all__ = ["asset_variable", "render_page_model_source"]
