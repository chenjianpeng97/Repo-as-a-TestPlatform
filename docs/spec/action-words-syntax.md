---
name: action-words-syntax
user-invocable: false
description: Action Words spec for unified test-asset management. Covers the base-class contract, Pydantic params template, cleanup registration, CLI standalone execution, and how BDD/pytest layers consume action words.
---

# action-words-syntax

## 目标与边界

- **目标**：把测试资产收敛为**最小可复用业务动作单元**（action word），统一管理
  DB 造数 / DB 断言 / 接口请求 / 接口断言 / 页面操作 / 页面断言六类工作，做到：
  - 每个 word **独立可运行**（CLI 一键执行），也可被 behave 步骤或 pytest 直接调用；
  - 入参/出参有**统一数据契约**（pydantic v2），可导出 JSON Schema 供 Plane
    Formulation 做可视化表单与一键执行；
  - 造数产生的行**按表登记 cleanup**，测试夹具场景后精确删除。
- **边界**：
  - action word 是**业务动作**，不是技术封装——`packages/db`、`packages/api_test`、
    `packages/api_objects` 这类基础设施不属于 action word；
  - API 类 word **只编排冻结的 API Objects**（`packages/api_objects/**`），不得
    手写 request 契约（与 `api-objects-syntax` 的边界一致）；
  - behave 步骤层只做「DataTable / 别名 → word 入参」翻译，不写执行逻辑。

## 目录结构

```
packages/action_words/
├── __init__.py          # 导出 ActionWord / ActionResult / register 等
├── __main__.py          # CLI：list / describe / run / catalog
├── base.py              # ActionCategory / TableRows / ActionResult / ActionWord
├── context.py           # ActionContext：DB 连接 + API token 惰性初始化
├── registry.py          # @register / discover / get / list_all / export_catalog
├── models.py            # 跨 word 共享的业务模型（如 ProductLine）
├── _internal/           # 内部工具（ids/generators/params/db/api/wait），不对外
├── db_seed/             # 每个造数 word 一个模块
├── db_assert/
├── api_request/
├── api_assert/
├── ui_action/           # 预留
└── ui_assert/           # 预留
```

- **一个模块一组强相关 word**：默认一个模块一个 word；同一聚合的多个 word
  （如 `create_invoice_relation` 与 `link_invoice_to_uninvoiced`）可同模块。
- 新增类别子包后无需注册：`registry.discover()` 会自动扫描
  `_WORD_SUBPACKAGES` 中列出的子包。

## 类模板（强制）

违反以下任一条会被 `@register`（导入期）或
`packages/tests/test_action_word_template.py`（回归期）拦截：

```python
@register
class CreateInOut(ActionWord):
    """经销商销售出库造数。

    <业务含义> + <前置条件> + <副作用（含 cleanup 说明）>，>= 20 字。
    """

    word_id = "db_seed.create_inout"        # 必须 "<category>.<snake_name>"
    name = "经销商销售出库造数"               # 中文业务名（平台目录展示）
    category = ActionCategory.DB_SEED
    tags = ("发票审计", "出入库")             # 业务域标签，便于目录过滤
    requires = frozenset({"db"})            # 依赖资源："db" / "api"
    datasource = "main"                     # 目标数据源别名（config/env.py DATABASES 键）
    example_params = {...}                  # 必须能通过 Params 校验

    Params = InOutParams                    # pydantic BaseModel，见下

    class Result(ActionResult):
        doc_nos: list[str] = Field(default_factory=list, description="出库单号")

    def run(self, params: InOutParams) -> "CreateInOut.Result":
        ...
```

### Params 规范

- pydantic v2 `BaseModel`，`model_config = ConfigDict(extra="forbid")`；
- **每个字段**必须有类型标注 + `Field(description="中文说明")`（平台表单依赖）；
- 有业务默认值的给默认值（默认值与真实主数据样例同源，见 `_internal/params.py`）；
- 跨 word 复用的结构放 `models.py`（如 `ProductLine`）；
- 组合校验用 `@model_validator`（如「count > 1 时不可指定 doc_no」）。

### Result 与 cleanup 规范

- 继承 `ActionResult`，业务字段同样必须带 `description`；
- **造数类 word 必须填 `cleanup`**：`list[TableRows]`，逐表登记本次插入的行 id；
- `detail` 放人类可读摘要（行数统计等）；
- 断言类 word 失败**抛 `AssertionError`**（带定位信息），不要返回 `ok=False`。

### 执行入口

- `run(params)` 是唯一业务入口；`run_from_dict(dict)` 是统一接入点
  （behave / pytest / CLI / 平台在线执行都走它）；
- **数据源声明**：框架支持 MySQL / SQL Server / PostgreSQL 共存。DB 类 word 通过类
  元数据 `datasource = "<别名>"` **显式声明去影响哪个库**（别名即
  `config/env.py` 的 `DATABASES` 键，数据库具体类型只写在配置里）；默认
  `"main"`。word 内经 `self.db` 取连接（等价
  `self.ctx.get_db(cls.datasource)`），**不要**在 word 内自建连接，也不要
  把连接细节写进业务代码。
- 造数落库用 `_internal/db.bulk_insert`（标识符引用按 `client.dialect`
  自动选方言：`[ident]` / `` `ident` `` / `"ident"`；值一律 `%s`）；业务 SQL 按目标库
  写对应方言——MySQL 用 `LIMIT n`、`NOW()`；SQL Server 用 `SELECT TOP n`、`GETDATE()`；
  PostgreSQL 用 `LIMIT n`、`NOW()` / `CURRENT_TIMESTAMP`、`ON CONFLICT`。
- 通过 `self.ctx`（`ActionContext`）取资源：`self.db` / `ctx.get_db(alias)`、
  `ctx.api_token`（惰性登录并缓存）；**不要**在 word 内自建连接。

## 分类约定

| 类别 | 职责 | 约定 |
| --- | --- | --- |
| `db_seed` | 直接落库造数 | 纯构建函数（`build_*_rows`，无 DB）与落库分离，便于离线单测；行 id 全部登记 cleanup；类上 `datasource` 声明目标库，走 `self.db` + `bulk_insert`；文件末尾必须提供 `if __name__ == "__main__"` 手工改参入口（显式列出关键字段，`python -m` 可独立运行） |
| `db_assert` | 对无接口层展示的表断言 | 异步数据内置 `wait_until` 轮询同步点；超时/不符抛 AssertionError |
| `api_request` | 调接口 / 编排定时任务 | 只 `load_api` 加载冻结的 API Objects；token 走 `ctx.api_token` |
| `api_assert` | 经接口读取状态并断言 | 同 db_assert 的轮询与抛错约定 |
| `ui_action` / `ui_assert` | 页面操作 / 断言（预留） | 落地时应编排 `packages/page_objects`，不得在 word 内写选择器 |

## CLI（独立执行）

```
uv run python -m packages.action_words list                 # 目录（word_id/name/category）
uv run python -m packages.action_words describe <word_id>   # 元数据 + 入参 schema + 样例
uv run python -m packages.action_words run <word_id> [--params '<json>' | --params-file f.json | --example]
uv run python -m packages.action_words catalog [-o out.json] # 全量目录 JSON（平台消费）
```

- `run` 输出 `Result` 的 JSON（含 cleanup 登记），退出码 0/1 对应成功/失败；
- 手工造数后需要清理时，按输出的 cleanup 逐表 `DELETE ... WHERE id IN (...)`。
- `catalog` 供本机 / `apps.index_platform` 调用 `export_catalog()` 同源数据；**Plane Job 不跑本 CLI**。

## 与 BDD / pytest 的集成

- **behave**：`api_environment.before_scenario` 建 `context.actions = ActionContext(db=context.db, ...)`；
  步骤内 `Word(context.actions).run(Word.Params(...))`；造数结果统一经
  `tests/features/api_steps/support.register_cleanup(context, result)` 登记，
  `after_scenario` 按表删除。别名解析（`prd1`/`经销商D`/`inv1`）留在步骤层。
- **pytest**：直接 `with ActionContext() as ctx: Word(ctx).run(...)`；
  纯构建函数（`build_*_rows` / `build_links`）可离线断言列集与关联键。
- **禁止**：`tests/**` import `apps.*` 或调用 `python -m apps.action_runner`。
  Plane 作业走 `apps.action_runner`（协议浅封装）；组合层永远是本包。

## 与 Plane（TestCopilot）

- 词条目录：`apps.index_platform` 调用 `export_catalog()` 写入 catalog
  `components.action_words`（Formulation 列表 + 每词 schema）。
- 运行：`python -m apps.action_runner run --expect-category <category> <word_id>`。
  包内 **零 Plane 知识**（无 `@plane_app`、无 argv_plan）。


## 敏感信息

- 凭据优先级：显式入参 > `TEST_USERNAME/TEST_PASSWORD` 环境变量 > `config/.env`；
- **不得**在 word 源码、example_params、日志中硬编码 token / 密码 / Cookie。

## 新增 word 检查清单

1. 选类别与 `word_id`（`<category>.<snake_name>`），先跑
   `python -m packages.action_words list` 确认无重复/无既有可复用 word；
2. **确定目标数据源**：业务数据长期存在哪个库就声明哪个别名
   （`datasource = "main"` / `"sqlserver"` / ...，见 `config/env.py` DATABASES）；
3. 造数类先写纯构建函数 + 列名元组（列名以 `assets/ddl/<别名>/*.sql` 为准，注意
   generated column 不能出现在插入列表）；
4. 按模板写 Params / Result / run / example_params，`@register` 注册；
5. `uv run pytest packages/tests/test_action_word_template.py` 通过；
6. `python -m packages.action_words run <word_id> --example` 冒烟（需要环境时）；
7. 若供 behave 使用，在步骤层接线并跑 `behave --stage api --dry-run`。
