"""Opt-in Plane mark for frozen API objects. Import-safe."""
from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")

PLANE_KIND_ATTR = "_plane_kind"


def plane_apiobject(obj: T) -> T:
    """Mark an APIModel (or similar) for Formulation API. Not runnable this phase."""
    object.__setattr__(obj, PLANE_KIND_ATTR, "api_object")
    return obj
