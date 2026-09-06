"""setuptools cmdclass: copy DNA into the wheel payload (not used for editable)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist


def _repo_root() -> Path:
    # tuner_testkit/apps/dna/build.py → repository root
    return Path(__file__).resolve().parents[3]


def _ensure_src_on_path() -> None:
    # Isolated `uv build` / PEP 517 env does not install this package first.
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)


def _payload_dir() -> Path:
    return Path(__file__).resolve().parent / "dna_payload"


def _payload_ready(root: Path | None = None) -> bool:
    return ((root or _payload_dir()) / ".cursor" / "rules").is_dir()


def _bundle() -> None:
    _ensure_src_on_path()
    if _payload_ready():
        return

    from tuner_testkit.apps.dna.cli import cmd_bundle

    code = cmd_bundle(SimpleNamespace())
    if code != 0:
        raise RuntimeError("tuner-dna bundle failed; cannot build wheel without DNA payload")
    if not _payload_ready():
        raise RuntimeError("tuner-dna bundle wrote no .cursor/rules (hidden files missing)")


class BuildPyWithDna(_build_py):
    def run(self) -> None:
        if not getattr(self, "editable_mode", False):
            _bundle()
        super().run()
        self._copy_hidden_payload()

    def _copy_hidden_payload(self) -> None:
        if getattr(self, "editable_mode", False) or not self.build_lib:
            return
        _ensure_src_on_path()
        from tuner_testkit.apps.dna.source import copy_tree, payload_package_dir

        src = payload_package_dir()
        dest = Path(self.build_lib) / "tuner_testkit" / "apps" / "dna" / "dna_payload"
        if src.is_dir():
            copy_tree(src, dest)


class SdistWithDna(_sdist):
    def run(self) -> None:
        _bundle()
        super().run()

    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        # setuptools prunes ``.*`` paths; re-copy the payload including ``.cursor/``.
        _ensure_src_on_path()
        from tuner_testkit.apps.dna.source import copy_tree, payload_package_dir

        src = payload_package_dir()
        dest = Path(base_dir) / "tuner_testkit" / "apps" / "dna" / "dna_payload"
        if src.is_dir():
            copy_tree(src, dest)
