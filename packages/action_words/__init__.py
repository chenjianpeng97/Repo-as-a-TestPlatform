"""Action Words — 统一管理自动化测试资产的最小业务动作层。

设计目标（见 docs/spec/action-words-syntax.md）：

- 每个 action word 是一个独立可运行的业务动作（DB 造数 / DB 断言 /
  接口请求 / 接口断言 / 页面操作 / 页面断言），入参经 pydantic 强类型
  声明并带样例，可 CLI 一键执行，也可被 behave / pytest 步骤直接调用；
- 接口类 word 只做冻结 ``packages/api_objects`` 资产的引用与编排，
  不重复定义请求契约；
- DB 类 word 统一走 ``packages.db.DbClient``（经类元数据 ``datasource``
  声明目标库），造数结果按表登记 ``cleanup``，供测试夹具精确清理。

CLI::

    uv run python -m packages.action_words list
    uv run python -m packages.action_words describe <word_id>
    uv run python -m packages.action_words run <word_id> --params '{...}'
    uv run python -m packages.action_words catalog --out report/action_words_catalog.json
"""
from __future__ import annotations

from packages.action_words.base import (
    ActionCategory,
    ActionResult,
    ActionWord,
    TableRows,
)
from packages.action_words.context import ActionContext
from packages.action_words.registry import (
    discover,
    export_catalog,
    get,
    list_all,
    register,
)

__all__ = [
    "ActionCategory",
    "ActionContext",
    "ActionResult",
    "ActionWord",
    "TableRows",
    "discover",
    "export_catalog",
    "get",
    "list_all",
    "register",
]
