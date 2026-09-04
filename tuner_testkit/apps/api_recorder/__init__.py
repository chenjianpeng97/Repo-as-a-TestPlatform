"""HTTP(S) proxy that freezes traffic into route-aligned API Objects.

See ``tuner_testkit/apps/api_recorder/README.md`` and ``docs/spec/api-objects-syntax.md``.
Does not capture UI element tables — use ``python -m tuner_testkit.apps.recorder`` for 合录.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.1.0"
