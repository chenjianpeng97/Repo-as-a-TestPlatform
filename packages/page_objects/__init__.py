from __future__ import annotations

try:
    from .pages import Pages
except ImportError:  # template may ship before Pages is generated
    Pages = None  # type: ignore[misc, assignment]

__all__ = ["Pages"]
