"""Deterministic workspace catalog: scan a workspace repo into one JSON document.

``build_catalog(root)`` never imports heavy runtime modules, never touches the
SUT and never writes git. Consumers: ``tuner-workspace catalog`` (CLI),
``tuner-workspace index render`` (INDEX auto zones), the local workbench, and
any future publisher.
"""
from __future__ import annotations

from tuner_testkit.catalog.build import CATALOG_VERSION, build_catalog, write_catalog
from tuner_testkit.catalog.front_matter import dump_front_matter, parse_front_matter, split_front_matter

__all__ = [
    "CATALOG_VERSION",
    "build_catalog",
    "dump_front_matter",
    "parse_front_matter",
    "split_front_matter",
    "write_catalog",
]
