"""Named-datasource settings and SQLAlchemy engine factory.

The framework supports MySQL, SQL Server, and PostgreSQL side by side. Each
logical datasource is declared in ``config.env.DATABASES`` under a business
alias (e.g. ``"main"`` for the primary store, ``"sqlserver"`` / ``"postgres"``
for additional stores); the concrete engine type lives only in that config.

Credentials resolution precedence (first wins):
    1. Explicit ``ConnectionSettings`` instance passed by the caller
    2. Per-alias environment variables ``TUNER_DB_<ALIAS>_HOST`` / ``_PORT`` /
       ``_USER`` / ``_PASSWORD`` / ``_NAME`` (legacy ``ARGON_DB_*`` still accepted)
    3. Legacy unprefixed variables (``TUNER_DB_HOST`` / ``ARGON_DB_HOST`` / ...)
       — apply to the default ``"main"`` alias only
    4. ``config.env.DATABASES[alias]`` in the SUT project
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote_plus

DEFAULT_ALIAS = "main"

#: db_type -> SQLAlchemy dialect name (also used for SQL-dialect branching)
_DB_TYPE_TO_DIALECT = {
    "sqlserver": "mssql",
    "mysql": "mysql",
    "postgres": "postgresql",
}


@dataclass(frozen=True)
class ConnectionSettings:
    host: str
    port: int
    user: str
    password: str
    database: str
    db_type: str = "mysql"
    connect_timeout: int = 15
    login_timeout: int = 15
    autocommit: bool = True

    @property
    def dialect(self) -> str:
        """SQLAlchemy dialect name (``mssql`` / ``mysql`` / ``postgresql``)."""
        try:
            return _DB_TYPE_TO_DIALECT[self.db_type]
        except KeyError:
            raise ValueError(
                f"未知数据库类型 {self.db_type!r}；支持: {sorted(_DB_TYPE_TO_DIALECT)}"
            ) from None


def _env_or(default: str, *names: str) -> str:
    for n in names:
        v = os.environ.get(n)
        if v:
            return v.strip()
    return default


def get_settings(alias: str = DEFAULT_ALIAS) -> ConnectionSettings:
    """Resolve ``ConnectionSettings`` for a named datasource alias."""
    from tuner_testkit.config import load_project_env

    env_config = load_project_env()
    databases: dict = getattr(env_config, "DATABASES", None) or {}
    if alias not in databases:
        raise KeyError(
            f"未知数据源别名 {alias!r}；请在 config/env.py 的 DATABASES 中定义。"
            f"已知别名: {sorted(databases)}"
        )
    base = dict(databases[alias])
    prefix = f"TUNER_DB_{alias.upper()}_"
    legacy_prefix = f"ARGON_DB_{alias.upper()}_"
    legacy = alias == DEFAULT_ALIAS
    extra_host = ("TUNER_DB_HOST", "ARGON_DB_HOST") if legacy else ()
    extra_port = ("TUNER_DB_PORT", "ARGON_DB_PORT") if legacy else ()
    extra_user = ("TUNER_DB_USER", "ARGON_DB_USER") if legacy else ()
    extra_password = ("TUNER_DB_PASSWORD", "ARGON_DB_PASSWORD") if legacy else ()
    extra_name = ("TUNER_DB_NAME", "ARGON_DB_NAME") if legacy else ()
    host = _env_or(str(base["host"]), prefix + "HOST", legacy_prefix + "HOST", *extra_host)
    port_str = _env_or(str(base["port"]), prefix + "PORT", legacy_prefix + "PORT", *extra_port)
    user = _env_or(str(base["user"]), prefix + "USER", legacy_prefix + "USER", *extra_user)
    password = _env_or(
        str(base["password"]),
        prefix + "PASSWORD",
        legacy_prefix + "PASSWORD",
        *extra_password,
    )
    database = _env_or(
        str(base["database"]), prefix + "NAME", legacy_prefix + "NAME", *extra_name
    )
    return ConnectionSettings(
        host=host,
        port=int(port_str),
        user=user,
        password=password,
        database=database,
        db_type=str(base.get("type", "mysql")),
    )


def get_default_settings() -> ConnectionSettings:
    return get_settings(DEFAULT_ALIAS)


def build_url(settings: ConnectionSettings) -> str:
    """Build the SQLAlchemy URL for a datasource (type -> driver mapping)."""
    user = quote_plus(settings.user or "")
    password = quote_plus(settings.password or "")
    host = settings.host
    port = settings.port
    name = settings.database
    if settings.db_type == "sqlserver":
        return f"mssql+pymssql://{user}:{password}@{host}:{port}/{name}?charset=utf8"
    if settings.db_type == "mysql":
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"
    if settings.db_type == "postgres":
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"
    raise ValueError(
        f"暂不支持该数据库类型：{settings.db_type!r}（支持 sqlserver / mysql / postgres）"
    )


def create_engine_for(settings: ConnectionSettings):
    """Create a pooled SQLAlchemy engine for the given settings.

    ``pool_pre_ping`` replaces the previous manual ``SELECT 1`` liveness check;
    ``pool_recycle`` guards against server-side idle disconnects.
    """
    from sqlalchemy import create_engine

    connect_args: dict = {}
    if settings.db_type == "sqlserver":
        connect_args = {
            "login_timeout": settings.login_timeout,
            "timeout": settings.connect_timeout,
        }
    elif settings.db_type in ("mysql", "postgres"):
        connect_args = {"connect_timeout": settings.connect_timeout}
    return create_engine(
        build_url(settings),
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args=connect_args,
    )
