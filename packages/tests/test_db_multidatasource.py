"""多数据源（MySQL / SQL Server / PostgreSQL 共存）配置解析与方言分支的单元测试。

不依赖真实数据库连接：只覆盖 URL 构造、别名解析、环境变量覆盖、
标识符方言引用与 ActionWord 的 datasource 声明。
"""
from __future__ import annotations

import pytest

from config import env as env_config
from tuner_testkit.db import DEFAULT_ALIAS, ConnectionSettings, build_url, get_settings
from tuner_testkit.action_words._internal.db import insert_sql, quote_ident


_FAKE_DATABASES = {
    "main": {
        "type": "mysql",
        "host": "my.example.com",
        "port": 3306,
        "user": "u1",
        "password": "p@ss:word!",
        "database": "maindb",
    },
    "sqlserver": {
        "type": "sqlserver",
        "host": "ss.example.com",
        "port": 1433,
        "user": "u2",
        "password": "p2",
        "database": "ssdb",
    },
    "postgres": {
        "type": "postgres",
        "host": "pg.example.com",
        "port": 5432,
        "user": "u3",
        "password": "p3",
        "database": "pgdb",
    },
}


@pytest.fixture()
def fake_databases(monkeypatch):
    monkeypatch.setattr(env_config, "DATABASES", _FAKE_DATABASES)
    for var in list(__import__("os").environ):
        if var.startswith("TUNER_DB"):
            monkeypatch.delenv(var, raising=False)
    return _FAKE_DATABASES


class TestBuildUrl:
    def test_sqlserver_url(self):
        s = ConnectionSettings(
            host="h", port=1433, user="u", password="p", database="d", db_type="sqlserver"
        )
        assert build_url(s) == "mssql+pymssql://u:p@h:1433/d?charset=utf8"

    def test_mysql_url(self):
        s = ConnectionSettings(
            host="h", port=3306, user="u", password="p", database="d", db_type="mysql"
        )
        assert build_url(s) == "mysql+pymysql://u:p@h:3306/d?charset=utf8mb4"

    def test_postgres_url(self):
        s = ConnectionSettings(
            host="h", port=5432, user="u", password="p", database="d", db_type="postgres"
        )
        assert build_url(s) == "postgresql+psycopg://u:p@h:5432/d"

    def test_credentials_are_url_quoted(self):
        s = ConnectionSettings(
            host="h", port=3306, user="a@b", password="p@ss:w!", database="d", db_type="mysql"
        )
        url = build_url(s)
        assert "a%40b" in url
        assert "p%40ss%3Aw%21" in url

    def test_unknown_type_raises(self):
        s = ConnectionSettings(
            host="h", port=1, user="u", password="p", database="d", db_type="oracle"
        )
        with pytest.raises(ValueError):
            build_url(s)


class TestDialect:
    def test_sqlserver_maps_to_mssql(self):
        s = ConnectionSettings(
            host="h", port=1, user="u", password="p", database="d", db_type="sqlserver"
        )
        assert s.dialect == "mssql"

    def test_mysql_maps_to_mysql(self):
        s = ConnectionSettings(
            host="h", port=1, user="u", password="p", database="d", db_type="mysql"
        )
        assert s.dialect == "mysql"

    def test_postgres_maps_to_postgresql(self):
        s = ConnectionSettings(
            host="h", port=1, user="u", password="p", database="d", db_type="postgres"
        )
        assert s.dialect == "postgresql"

    def test_unknown_type_raises(self):
        s = ConnectionSettings(
            host="h", port=1, user="u", password="p", database="d", db_type="nope"
        )
        with pytest.raises(ValueError):
            _ = s.dialect


class TestGetSettings:
    def test_resolves_alias(self, fake_databases):
        s = get_settings("sqlserver")
        assert s.db_type == "sqlserver"
        assert s.host == "ss.example.com"
        assert s.port == 1433
        assert s.database == "ssdb"

    def test_default_alias_is_main(self, fake_databases):
        s = get_settings()
        assert s.db_type == "mysql"
        assert s.database == "maindb"
        assert DEFAULT_ALIAS == "main"

    def test_unknown_alias_raises_with_known_names(self, fake_databases):
        with pytest.raises(KeyError) as exc:
            get_settings("nonexistent")
        assert "main" in str(exc.value)

    def test_per_alias_env_override(self, fake_databases, monkeypatch):
        monkeypatch.setenv("TUNER_DB_SQLSERVER_HOST", "override.example.com")
        monkeypatch.setenv("TUNER_DB_SQLSERVER_PORT", "1434")
        s = get_settings("sqlserver")
        assert s.host == "override.example.com"
        assert s.port == 1434
        # 其他别名不受影响
        assert get_settings("main").host == "my.example.com"

    def test_legacy_env_overrides_default_alias_only(self, fake_databases, monkeypatch):
        monkeypatch.setenv("TUNER_DB_HOST", "legacy.example.com")
        assert get_settings("main").host == "legacy.example.com"
        assert get_settings("sqlserver").host == "ss.example.com"

    def test_per_alias_env_wins_over_legacy(self, fake_databases, monkeypatch):
        monkeypatch.setenv("TUNER_DB_HOST", "legacy.example.com")
        monkeypatch.setenv("TUNER_DB_MAIN_HOST", "prefixed.example.com")
        assert get_settings("main").host == "prefixed.example.com"


class TestQuoteDialect:
    def test_quote_ident_mysql_default(self):
        assert quote_ident("col") == "`col`"

    def test_quote_ident_mssql(self):
        assert quote_ident("col", "mssql") == "[col]"

    def test_quote_ident_postgresql(self):
        assert quote_ident("col", "postgresql") == '"col"'
        assert quote_ident('a"b', "postgresql") == '"a""b"'

    def test_insert_sql_mysql(self):
        assert insert_sql("t", ["a", "b"]) == "INSERT INTO `t` (`a`, `b`) VALUES (%s, %s)"

    def test_insert_sql_mssql(self):
        assert (
            insert_sql("t", ["a", "b"], "mssql")
            == "INSERT INTO [t] ([a], [b]) VALUES (%s, %s)"
        )

    def test_insert_sql_postgresql(self):
        assert (
            insert_sql("t", ["a", "b"], "postgresql")
            == 'INSERT INTO "t" ("a", "b") VALUES (%s, %s)'
        )


class TestActionWordDatasource:
    def test_default_datasource_and_describe(self):
        from tuner_testkit.action_words import ActionCategory, ActionWord

        class _Probe(ActionWord):
            """测试探针。"""

            word_id = "test.probe"
            name = "探针"
            category = ActionCategory.DB_SEED

            def run(self, params):  # pragma: no cover - not executed
                raise NotImplementedError

        assert _Probe.datasource == DEFAULT_ALIAS
        assert _Probe.describe()["datasource"] == DEFAULT_ALIAS

    def test_subclass_overrides_datasource(self):
        from tuner_testkit.action_words import ActionCategory, ActionWord

        class _SqlServerProbe(ActionWord):
            """测试探针（SQL Server 库）。"""

            word_id = "test.sqlserver_probe"
            name = "SQL Server 探针"
            category = ActionCategory.DB_SEED
            datasource = "sqlserver"

            def run(self, params):  # pragma: no cover - not executed
                raise NotImplementedError

        assert _SqlServerProbe.describe()["datasource"] == "sqlserver"
