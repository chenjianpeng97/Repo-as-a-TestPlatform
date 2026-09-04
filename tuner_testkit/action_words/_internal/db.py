"""DB 造数共用原语 — 参数化批量 INSERT（多方言：SQL Server / MySQL / PostgreSQL）。

注入安全说明：表名与列名是各 action word 模块内代码定义的常量（固定白名单），
从不接受外部输入；只有**值**经 ``%s`` 占位符传递，因此拼接列名/占位符
不构成注入面。

方言说明：pymssql / pymysql / psycopg 参数风格同为 ``%s``，各库仅标识符引用
不同（``[name]`` / `` `name` `` / ``"name"``）；``bulk_insert`` 从
``client.dialect`` 自动选择，调用方无感。
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from tuner_testkit.db import DbClient


def quote_ident(name: str, dialect: str = "mysql") -> str:
    """Quote an identifier for the given SQL dialect."""
    if dialect == "mysql":
        return f"`{name}`"
    if dialect == "postgresql":
        return '"' + name.replace('"', '""') + '"'
    return f"[{name}]"


def insert_sql(table: str, columns: Sequence[str], dialect: str = "mysql") -> str:
    cols = ", ".join(quote_ident(c, dialect) for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    return f"INSERT INTO {quote_ident(table, dialect)} ({cols}) VALUES ({placeholders})"


def bulk_insert(
    client: DbClient,
    table: str,
    columns: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
) -> int:
    """将 ``rows`` 以参数化语句批量插入 ``table``。

    每个 row dict 必须恰好包含 ``columns`` 中的键；值按列序取出后经
    ``%s`` 占位符传递。标识符引用按 ``client.dialect`` 自动选择方言。
    """
    if not rows:
        return 0
    sql = insert_sql(table, columns, client.dialect)
    params = [tuple(row[c] for c in columns) for row in rows]
    return client.execute_many(sql, params)
