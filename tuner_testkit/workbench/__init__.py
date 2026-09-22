"""Local workbench: a 127.0.0.1 page over ``tuner-workspace catalog`` + ``run``.

Lightweight users ``git pull`` then ``uv run tuner-workbench`` to fill in tool
parameters visually. No database; repo is read-only; only ``artifacts/`` is written.
"""
from __future__ import annotations

__all__ = ["create_app"]


def create_app(*, root=None):
    from tuner_testkit.workbench.app import create_app as _create

    return _create(root=root)
