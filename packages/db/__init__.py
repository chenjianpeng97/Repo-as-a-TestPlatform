"""Generic multi-dialect DB utilities used by higher-level service layers.

The framework supports MySQL, SQL Server, and PostgreSQL side by side; named
datasources are declared in ``config.env.DATABASES`` (business alias ->
connection config incl. ``type``). Use ``DbClient.for_datasource(alias)`` to
target a specific one; ``DbClient.default()`` targets the ``"main"`` alias.

This package intentionally contains **only** generic DB concerns (connection,
parameterised execution, context management). It does not know about any
business table names, business queries, or domain entities.

``MySQLClient`` is a deprecated alias of ``DbClient`` kept for transitional
imports; new code should use ``DbClient``.
"""
from __future__ import annotations

from .client import DbClient, MySQLClient
from .connection import (
    DEFAULT_ALIAS,
    ConnectionSettings,
    build_url,
    get_default_settings,
    get_settings,
)

__all__ = [
    "DbClient",
    "MySQLClient",
    "ConnectionSettings",
    "DEFAULT_ALIAS",
    "build_url",
    "get_default_settings",
    "get_settings",
]
