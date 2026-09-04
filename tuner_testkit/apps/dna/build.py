"""setuptools cmdclass: copy DNA into the wheel payload (not used for editable)."""

from __future__ import annotations

from types import SimpleNamespace

from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist


def _bundle() -> None:
    from tuner_testkit.apps.dna.cli import cmd_bundle

    code = cmd_bundle(SimpleNamespace())
    if code != 0:
        raise RuntimeError("tuner-dna bundle failed; cannot build wheel without DNA payload")


class BuildPyWithDna(_build_py):
    def run(self) -> None:
        if not getattr(self, "editable_mode", False):
            _bundle()
        super().run()


class SdistWithDna(_sdist):
    def run(self) -> None:
        _bundle()
        super().run()
