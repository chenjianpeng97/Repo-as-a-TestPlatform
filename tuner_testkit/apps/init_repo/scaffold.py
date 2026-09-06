"""Scaffold a new SUT test repo: six-layer skeleton + DNA overlay + kit dependency."""
from __future__ import annotations

import pathlib
import shutil
import textwrap

SKELETON_DIRS: tuple[str, ...] = (
    "assets/ddl",
    "assets/sql",
    "assets/usecases",
    "assets/domain-notes",
    "assets/testreport",
    "packages/action_words/db_seed",
    "packages/action_words/db_assert",
    "packages/action_words/api_request",
    "packages/action_words/api_assert",
    "packages/action_words/ui_action",
    "packages/action_words/ui_assert",
    "packages/api_objects",
    "packages/page_objects",
    "apps",
    "data/mocks",
    "tests/features/ui_steps",
    "tests/features/api_steps",
    "tests/pytest",
    "docs/spec",
    "config",
    "logs",
    "artifacts",
)

# Thin SUT files copied from this template (not the full kit runtime).
_STUB_FILES: tuple[str, ...] = (
    "config/env.py",
    "packages/__init__.py",
    "packages/page_objects/__init__.py",
    "packages/page_objects/session.py",
    "packages/page_objects/plane.py",
    "packages/api_objects/__init__.py",
    "packages/api_objects/auth.py",
    "packages/api_objects/registry.py",
    "packages/api_objects/plane.py",
    "packages/api_objects/recording/__init__.py",
    "packages/action_words/__init__.py",
    "packages/action_words/models.py",
    "packages/action_words/_internal/__init__.py",
    "packages/action_words/_internal/params.py",
    "apps/__init__.py",
    "behave.ini",
)


def _stub_root() -> pathlib.Path | None:
    """Directory that contains thin SUT stub files (``config/env.py``, …).

    Wheel installs have no template checkout beside site-packages, and
    ``project_root()`` must not be used: scaffold is how a project is created.
    """
    from tuner_testkit.project import template_source_root

    editable = template_source_root()
    if editable is not None:
        return editable
    bundled = pathlib.Path(__file__).resolve().parent / "stubs"
    if (bundled / "config" / "env.py").is_file():
        return bundled
    return None


def _copy_file(src: pathlib.Path, dst: pathlib.Path, *, overwrite: bool) -> bool:
    if dst.exists() and not overwrite:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _write_pyproject(target: pathlib.Path, *, overwrite: bool) -> bool:
    dest = target / "pyproject.toml"
    if dest.exists() and not overwrite:
        return False
    dest.write_text(
        textwrap.dedent(
            """\
            [project]
            name = "sut-test-repo"
            version = "0.1.0"
            description = "Test repo created from tuner-testkit"
            requires-python = ">=3.12"
            dependencies = [
                "tuner-testkit[db,api]>=4.0.0",
            ]

            [project.optional-dependencies]
            web-ui = ["tuner-testkit[web-ui]"]
            recorder = ["tuner-testkit[recorder]"]
            mock = ["tuner-testkit[mock]"]
            test = ["pytest>=9.0.3"]
            bdd = ["behave>=1.2.6", "playwright>=1.54.0"]
            dev = ["pytest>=9.0.3", "behave>=1.2.6", "playwright>=1.54.0"]

            [build-system]
            requires = ["setuptools>=75", "wheel"]
            build-backend = "setuptools.build_meta"

            [tool.setuptools.packages.find]
            include = ["packages*", "config*", "apps*"]

            [tool.tuner-testkit]
            page_objects = "packages/page_objects"
            api_objects = "packages/api_objects"
            mocks = "data/mocks"
            """
        ),
        encoding="utf-8",
        newline="\n",
    )
    return True


def scaffold(target: pathlib.Path, *, with_ai: bool = True, overwrite: bool = False) -> list[str]:
    actions: list[str] = []
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    src_root = _stub_root()

    for rel in SKELETON_DIRS:
        d = target / rel
        d.mkdir(parents=True, exist_ok=True)
        keep = d / ".gitkeep"
        if not any(d.iterdir()) and not keep.exists():
            keep.write_text("", encoding="utf-8")
        actions.append(f"dir  {rel}")

    if _write_pyproject(target, overwrite=overwrite):
        actions.append("write pyproject.toml")
    else:
        actions.append("skip pyproject.toml (exists)")

    if src_root is None:
        actions.append("skip stubs (not bundled in this install)")
    else:
        for rel in _STUB_FILES:
            src = src_root / rel
            if not src.exists():
                continue
            if _copy_file(src, target / rel, overwrite=overwrite):
                actions.append(f"copy {rel}")
            else:
                actions.append(f"skip {rel} (exists)")

    if with_ai:
        from types import SimpleNamespace

        from tuner_testkit.apps.dna.cli import cmd_sync

        code = cmd_sync(
            SimpleNamespace(target=str(target), overwrite=overwrite),
        )
        actions.append(f"dna sync (exit {code})")

    return actions
