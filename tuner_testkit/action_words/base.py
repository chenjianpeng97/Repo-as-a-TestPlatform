"""Action Word 基类与统一数据契约。

Action Word 是本仓库测试资产的最小可复用业务动作单元，按类别覆盖
DB 造数 / DB 断言 / 接口请求 / 接口断言 / 页面操作 / 页面断言六类工作。
每个 action word 独立可运行（CLI 一键执行），也可被 behave 步骤或 pytest
直接调用。

模板规范（平台化契约，违反会被 registry 注册与模板一致性测试拦截）：

- 子类必须有业务 docstring（描述业务含义、前置条件、副作用）；
- 类元数据 ``word_id`` / ``name`` / ``category`` 必填；
- 内嵌 ``Params``（pydantic BaseModel）：每个字段必须有类型声明与
  ``Field(description=...)``，供平台以可视化表单展示；
- ``example_params``：一份能通过 ``Params`` 校验、可直接运行的入参样例；
- ``run(params)`` 为唯一执行入口；断言类 word 失败时抛 ``AssertionError``，
  成功返回 ``Result``（含 ``detail`` 细节与造数类的 ``cleanup`` 清理登记）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, ClassVar, Mapping

from pydantic import BaseModel, ConfigDict, Field

from tuner_testkit.action_words.context import ActionContext
from tuner_testkit.db import DEFAULT_ALIAS, DbClient


class ActionCategory(StrEnum):
    """Action word 的工作类别（平台侧用于分组展示与运行策略）。"""

    DB_SEED = "db_seed"          # DB 造数
    DB_ASSERT = "db_assert"      # DB 断言
    API_REQUEST = "api_request"  # 接口请求 / 编排
    API_ASSERT = "api_assert"    # 接口断言
    UI_ACTION = "ui_action"      # 页面操作（预留）
    UI_ASSERT = "ui_assert"      # 页面断言（预留）


class TableRows(BaseModel):
    """一张表上本次动作产生的行 id，供调用方注册清理夹具后精确删除。"""

    table: str = Field(description="表名")
    ids: list[int] = Field(default_factory=list, description="行主键 id 列表")


class ActionResult(BaseModel):
    """所有 action word 的统一返回基类。

    子类可以增加强类型的业务字段（如 ``invoice_nos``）；``detail`` 存放
    人类可读的执行摘要，``cleanup`` 仅造数类 word 填写。
    """

    ok: bool = Field(True, description="动作是否成功")
    detail: dict[str, Any] = Field(
        default_factory=dict, description="人类可读的执行细节 / 摘要"
    )
    cleanup: list[TableRows] = Field(
        default_factory=list,
        description="造数产生的行按表登记，供测试夹具在场景结束后精确删除",
    )


class ActionWord(ABC):
    """所有 action word 的抽象基类。见模块 docstring 的模板规范。"""

    # ---- 类元数据（平台目录 / registry 索引） ----
    word_id: ClassVar[str]
    name: ClassVar[str]
    category: ClassVar[ActionCategory]
    tags: ClassVar[tuple[str, ...]] = ()
    #: 依赖的环境资源："db" / "api"；ActionContext 按需惰性初始化
    requires: ClassVar[frozenset[str]] = frozenset()
    #: 目标数据源别名（config/env.py 的 ``DATABASES`` 键）。框架支持
    #: MySQL / SQL Server / PostgreSQL 共存，DB 类 word 在此显式声明去影响哪个库
    #: （如主业务在 "main"、第二库在 "sqlserver" / "postgres"），
    #: 数据库具体类型只写在配置里。
    datasource: ClassVar[str] = DEFAULT_ALIAS
    #: 可直接运行的入参样例（必须能通过 Params 校验）
    example_params: ClassVar[dict[str, Any]] = {}

    class Params(BaseModel):
        """入参契约；子类内嵌覆盖。未知键一律拒绝，避免拼写错误静默生效。"""

        model_config = ConfigDict(extra="forbid")

    class Result(ActionResult):
        pass

    def __init__(self, ctx: ActionContext | None = None) -> None:
        self.ctx = ctx if ctx is not None else ActionContext()

    @property
    def db(self) -> DbClient:
        """本 word 声明的目标数据源连接（``ctx.get_db(cls.datasource)``）。"""
        return self.ctx.get_db(type(self).datasource)

    @abstractmethod
    def run(self, params: Params) -> ActionResult:
        """执行动作。断言类失败抛 ``AssertionError``，其余异常按原样上抛。"""

    def run_from_dict(self, raw: Mapping[str, Any] | None = None) -> ActionResult:
        """统一接入点：dict 入参 → pydantic 校验 → :meth:`run`。

        behave 步骤、pytest、CLI、未来平台的在线执行都走这一入口。
        """
        params = self.Params.model_validate(dict(raw or {}))
        return self.run(params)

    # ---- 平台化导出 ----

    @classmethod
    def params_schema(cls) -> dict[str, Any]:
        """入参 JSON Schema（供平台渲染表单）。"""
        return cls.Params.model_json_schema()

    @classmethod
    def describe(cls) -> dict[str, Any]:
        """目录条目：元数据 + docstring + 入参 schema + 样例。"""
        return {
            "word_id": cls.word_id,
            "name": cls.name,
            "category": str(cls.category),
            "tags": list(cls.tags),
            "requires": sorted(cls.requires),
            "datasource": cls.datasource,
            "doc": (cls.__doc__ or "").strip(),
            "params_schema": cls.params_schema(),
            "example_params": cls.example_params,
        }
