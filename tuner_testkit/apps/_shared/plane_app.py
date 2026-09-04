"""Plane Job registration: @plane_app, discover, export_tools.

Only packages that ship ``apps/<name>/plane.py`` are discovered. Domain
packages and local-only CLIs (dump_ddl, recorder, init_repo, index_ai) stay
out of the registry. ``plane.py`` must be import-safe (no DB / mitmproxy).
"""
from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Literal

APP_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ParserFactory = Callable[[], argparse.ArgumentParser]
ResultKind = Literal["logs", "catalog_json"]
RuntimeKind = Literal["job", "long_lived"]
ArgvPlanKind = Literal["option", "store_true", "store_false", "positional", "json_option"]

_REGISTRY: dict[str, "PlaneAppSpec"] = {}
_discovered = False


@dataclass
class PlaneAppSpec:
    app_id: str
    name: str
    module: str
    argv: list[str]
    destructive: bool
    timeout: int
    result: ResultKind
    runtime: RuntimeKind
    expose: bool
    readme_path: str | None
    parser_factory: ParserFactory
    json_params: tuple[str, ...] = ()
    hide_params: tuple[str, ...] = ()
    word_id_pattern: str | None = None
    schema_overlay: dict[str, Any] | None = None
    params_schema: dict[str, Any] = field(default_factory=dict)
    argv_plan: list[dict[str, Any]] = field(default_factory=list)

    def refresh_from_parser(self) -> None:
        parser = self.parser_factory()
        self.argv_plan, self.params_schema = _plan_and_schema(
            parser,
            json_params=self.json_params,
            hide_params=self.hide_params,
            word_id_pattern=self.word_id_pattern,
            schema_overlay=self.schema_overlay,
        )


def plane_app(
    *,
    app_id: str,
    name: str,
    module: str,
    argv: list[str] | None = None,
    destructive: bool = False,
    timeout: int = 180,
    result: ResultKind = "logs",
    runtime: RuntimeKind = "job",
    expose: bool = True,
    readme_path: str | None = None,
    json_params: Iterable[str] = (),
    hide_params: Iterable[str] = (),
    word_id_pattern: str | None = None,
    schema_overlay: dict[str, Any] | None = None,
) -> Callable[[ParserFactory], ParserFactory]:
    """Register a Plane-runnable CLI. Decorate an import-safe ``build_parser``."""

    def decorator(factory: ParserFactory) -> ParserFactory:
        spec = register_plane_app(
            factory,
            app_id=app_id,
            name=name,
            module=module,
            argv=argv,
            destructive=destructive,
            timeout=timeout,
            result=result,
            runtime=runtime,
            expose=expose,
            readme_path=readme_path,
            json_params=json_params,
            hide_params=hide_params,
            word_id_pattern=word_id_pattern,
            schema_overlay=schema_overlay,
        )
        factory._plane_app_id = spec.app_id  # type: ignore[attr-defined]
        return factory

    return decorator


def register_plane_app(
    factory: ParserFactory,
    *,
    app_id: str,
    name: str,
    module: str,
    argv: list[str] | None = None,
    destructive: bool = False,
    timeout: int = 180,
    result: ResultKind = "logs",
    runtime: RuntimeKind = "job",
    expose: bool = True,
    readme_path: str | None = None,
    json_params: Iterable[str] = (),
    hide_params: Iterable[str] = (),
    word_id_pattern: str | None = None,
    schema_overlay: dict[str, Any] | None = None,
) -> PlaneAppSpec:
    if not APP_ID_RE.fullmatch(app_id):
        raise ValueError(f"invalid plane app_id: {app_id!r}")
    if not module.startswith("apps.") or ".." in module:
        raise ValueError(f"invalid plane module: {module!r}")
    prefix = list(argv) if argv is not None else ["python", "-m", module]
    spec = PlaneAppSpec(
        app_id=app_id,
        name=name,
        module=module,
        argv=prefix,
        destructive=destructive,
        timeout=int(timeout),
        result=result,
        runtime=runtime,
        expose=expose,
        readme_path=readme_path,
        parser_factory=factory,
        json_params=tuple(json_params),
        hide_params=tuple(hide_params),
        word_id_pattern=word_id_pattern,
        schema_overlay=schema_overlay,
    )
    spec.refresh_from_parser()
    # Overwrite: importlib.reload after reset creates a new factory object.
    _REGISTRY[app_id] = spec
    return spec


def discover(repo_root: str | Path | None = None) -> None:
    """Import every ``apps/<name>/plane.py``. Idempotent."""
    global _discovered
    if _discovered:
        return
    _discovered = True
    root = Path(repo_root) if repo_root is not None else _repo_root()
    apps_dir = root / "apps"
    if not apps_dir.is_dir():
        return
    for child in sorted(apps_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        if not (child / "plane.py").is_file():
            continue
        mod_name = f"apps.{child.name}.plane"
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
        else:
            importlib.import_module(mod_name)


def export_tools(repo_root: str | Path | None = None) -> list[dict[str, Any]]:
    """Catalog ``tools[]`` entries with ``plane_runnable`` (expose=True)."""
    discover(repo_root)
    rows: list[dict[str, Any]] = []
    for spec in sorted(_REGISTRY.values(), key=lambda item: item.app_id):
        if not spec.expose:
            continue
        rows.append(spec_to_tool(spec))
    return rows


def spec_to_tool(spec: PlaneAppSpec) -> dict[str, Any]:
    runnable = bool(spec.expose and spec.runtime == "job")
    return {
        "app_id": spec.app_id,
        "name": spec.name,
        "module": spec.module,
        "argv": list(spec.argv),
        "params_schema": spec.params_schema,
        "argv_plan": list(spec.argv_plan),
        "destructive": spec.destructive,
        "timeout": spec.timeout,
        "result": spec.result,
        "runtime": spec.runtime,
        "plane_runnable": runnable,
        "whitelisted": runnable,
        "readme_path": spec.readme_path,
    }


def reset_registry_for_tests() -> None:
    """Test helper: clear registration so discover can run again."""
    global _discovered
    _REGISTRY.clear()
    _discovered = False


def dump_manifest(app_id: str) -> str:
    spec = _REGISTRY.get(app_id)
    if spec is None:
        raise KeyError(app_id)
    return json.dumps(spec_to_tool(spec), ensure_ascii=False, indent=2)


def _repo_root() -> Path:
    from tuner_testkit.project import project_root

    return project_root()


def _plan_and_schema(
    parser: argparse.ArgumentParser,
    *,
    json_params: tuple[str, ...],
    hide_params: tuple[str, ...],
    word_id_pattern: str | None,
    schema_overlay: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    json_set = set(json_params)
    hide_set = set(hide_params) | {"help"}
    plan: list[dict[str, Any]] = []
    properties: dict[str, Any] = {}
    required: list[str] = []

    for action in parser._actions:  # noqa: SLF001 — argparse has no public action list
        dest = getattr(action, "dest", None)
        if not dest or dest in hide_set:
            continue
        option_strings = list(getattr(action, "option_strings", []) or [])
        flag = option_strings[0] if option_strings else None
        const_nargs = getattr(argparse, "OPTIONAL", "?")

        if dest in json_set:
            step: dict[str, Any] = {"key": dest, "kind": "json_option", "flag": flag or f"--{dest.replace('_', '-')}"}
            plan.append(step)
            properties[dest] = {"type": "object"}
            continue

        action_type = type(action).__name__
        if action_type == "_StoreTrueAction" or getattr(action, "const", None) is True and getattr(action, "nargs", None) == 0:
            plan.append({"key": dest, "kind": "store_true", "flag": flag or f"--{dest.replace('_', '-')}"})
            properties[dest] = {"type": "boolean", "default": False}
            continue
        if action_type == "_StoreFalseAction":
            plan.append({"key": dest, "kind": "store_false", "flag": flag or f"--{dest.replace('_', '-')}"})
            properties[dest] = {"type": "boolean", "default": True}
            continue

        nargs = getattr(action, "nargs", None)
        if flag is None:
            variadic = nargs in ("*", "+", argparse.REMAINDER)
            plan.append({"key": dest, "kind": "positional", "variadic": variadic})
            if variadic:
                properties[dest] = {"type": "array", "items": {"type": "string"}}
            else:
                prop: dict[str, Any] = {"type": "string"}
                if dest == "word_id" and word_id_pattern:
                    prop["pattern"] = word_id_pattern
                properties[dest] = prop
            if getattr(action, "required", True) and nargs not in ("*", const_nargs, "?"):
                required.append(dest)
            elif nargs == "+":
                required.append(dest)
            continue

        plan.append({"key": dest, "kind": "option", "flag": flag})
        prop = {"type": "string"}
        if dest == "word_id" and word_id_pattern:
            prop["pattern"] = word_id_pattern
        if getattr(action, "choices", None):
            prop["enum"] = list(action.choices)
        properties[dest] = prop
        if getattr(action, "required", False):
            required.append(dest)

    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = required
    if schema_overlay:
        schema = {**schema, **schema_overlay}
        if "properties" in schema_overlay:
            schema["properties"] = {**properties, **schema_overlay["properties"]}
    return plan, schema
