"""Enumerate every frozen :class:`APIModel` under ``packages/api_objects``.

Existing discovery paths are not usable for a route table: ``scan_api_objects``
(``apps.index_platform``) only regex-greps ``method=`` / ``path=`` and never
materialises the object, and ``collect_plane_api_objects`` only returns assets
carrying an opt-in ``@plane_apiobject`` mark.

Assets live in a route-shaped tree whose directory names mirror URL segments
(``packages/api_objects/prod-api/inout/...``). Those segments are frequently
**not** valid Python identifiers, so loading by dotted module name silently
skips them. Everything here loads by file location instead.

Import-safe: no HTTP, no DB. A single unloadable asset is warned about and
skipped rather than failing the whole scan.
"""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

from packages.api_test.model import APIModel
from packages.logging import log_warn

__all__ = ["ApiModelRef", "find_api_model", "iter_api_models"]

_SKIP_DIR_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache"}
# Leaf ``__init__.py`` files only re-export the sibling ``<METHOD>.v<N>.py``
# asset (see docs/spec/api-objects-syntax.md), so scanning them would load the
# same model twice under a second path.
_SKIP_FILE_NAMES = {"__init__.py", "conftest.py"}


@dataclass(frozen=True)
class ApiModelRef:
    """A discovered asset: the model plus where it came from."""

    model: APIModel
    file: str
    """Repo-relative posix path of the defining file."""

    var_name: str
    """Module-level variable the model is bound to."""

    @property
    def route_key(self) -> str:
        return f"{self.model.method.upper()} {self.model.path}"


def iter_api_models(root: str | Path | None = None) -> list[ApiModelRef]:
    """Load and return every ``APIModel`` defined under ``packages/api_objects``.

    Results are sorted by file path then variable name so callers (route
    tables, catalogs, seeds) see a deterministic order.
    """
    repo_root = Path(root) if root is not None else _repo_root()
    base = repo_root / "packages" / "api_objects"
    if not base.is_dir():
        return []

    found: list[ApiModelRef] = []
    seen: set[int] = set()
    for path in sorted(base.rglob("*.py")):
        if not _is_candidate(path, base):
            continue
        module = _load_module(path)
        if module is None:
            continue
        for var_name, value in vars(module).items():
            if var_name.startswith("_") or not isinstance(value, APIModel):
                continue
            if id(value) in seen:
                continue
            seen.add(id(value))
            found.append(
                ApiModelRef(
                    model=value,
                    file=path.relative_to(repo_root).as_posix(),
                    var_name=var_name,
                )
            )
    found.sort(key=lambda ref: (ref.file, ref.var_name))
    return found


def find_api_model(
    method: str,
    path: str,
    *,
    root: str | Path | None = None,
) -> ApiModelRef | None:
    """Exact ``method + path`` lookup. No dynamic-segment matching."""
    wanted = f"{method.upper()} {path}"
    for ref in iter_api_models(root):
        if ref.route_key == wanted:
            return ref
    return None


def _is_candidate(path: Path, base: Path) -> bool:
    if path.name in _SKIP_FILE_NAMES or path.name.startswith("test_"):
        return False
    rel_parts = path.relative_to(base).parts
    return not any(part in _SKIP_DIR_PARTS or part.startswith(".") for part in rel_parts)


def _load_module(path: Path):
    """Import a single asset file by location, reusing an existing module."""
    resolved = path.resolve()
    for module in list(sys.modules.values()):
        module_file = getattr(module, "__file__", None)
        if not module_file:
            continue
        try:
            if Path(module_file).resolve() == resolved:
                return module
        except (OSError, ValueError):
            # Namespace packages and frozen modules can carry unusable __file__.
            continue

    # Synthetic name: route directories such as ``prod-api`` are not valid
    # identifiers, so a dotted import name would not resolve.
    mod_name = f"_api_objects_scan_{abs(hash(str(resolved)))}"
    spec = importlib.util.spec_from_file_location(mod_name, resolved)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 -- one broken asset must not stop the scan
        sys.modules.pop(mod_name, None)
        log_warn("api_objects asset failed to import", file=str(path), error=f"{type(exc).__name__}: {exc}")
        return None
    return module


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file() and (parent / "packages").is_dir():
            return parent
    return here.parents[2]
