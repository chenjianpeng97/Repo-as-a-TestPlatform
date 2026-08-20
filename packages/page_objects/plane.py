"""Opt-in Plane mark for page-object classes. Import-safe."""
from __future__ import annotations

from typing import TypeVar

F = TypeVar("F", bound=type)

PLANE_KIND_ATTR = "_plane_kind"


def plane_pageobject(cls: F) -> F:
    """Mark a page-object class for Formulation Page. Not runnable this phase."""
    setattr(cls, PLANE_KIND_ATTR, "page_object")
    return cls
