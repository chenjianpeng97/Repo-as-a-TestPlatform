<!-- version: 1.1.0 -->
# INDEX — 仓库知识 / 能力地图

> 平台的**当前状态与能力**总览。LLM 生成任何测试/工具前先来这里检索依据（grounding）；
> 人类工程师用它一眼看全"这个仓库现在有哪些知识、工具、资产、AI 组件"。
> 稳定的分层世界观见 [`AGENTS.md`](AGENTS.md)；AI 组件明细见 [`.cursor/REGISTRY.md`](.cursor/REGISTRY.md)。
>
> 本文件只登记**平台**能力。若存在 `INDEX.project.md`（试验田 / 下游项目仓），那是被测系统的业务资产地图，生成业务测试前一并阅读。
>
> 维护方式：**人工/半自动区**由 `maintain-index` skill 增量更新（读各区 `CHANGELOG` 的 delta，不全量读正文）；
> **自动区**由生成工具写 `CHANGELOG`。变更纪律见 `.cursor/rules/index-hygiene.mdc`。

## 1. 知识层（assets/）

规范：`docs/spec/assets-knowledge-syntax.md`。字段：domain / source / date / version / confidence。

### 1.1 DDL（自动区，apps/dump_ddl 产出）

| datasource | 表 | 更新 | 备注 |
| --- | --- | --- | --- |
| _(暂无平台内置 DDL)_ | | | 运行 `python apps/dump_ddl.py --all --datasource <alias>`；MySQL / SQL Server / PostgreSQL。业务库 DDL 写 `INDEX.project.md` |

变更流水：`assets/CHANGELOG.md`

### 1.2 业务 SQL 副本（assets/sql/，人类可读镜像）

| 文件 | domain | confidence | 用途 |
| --- | --- | --- | --- |
| _(暂无)_ | | | |

### 1.3 用例 / 业务讲解 / 报告（usecases / domain-notes / testreport）

| 路径 | domain | source | confidence | 一句话用途 |
| --- | --- | --- | --- | --- |
| _(暂无)_ | | | | |

## 2. 组件层（packages/）

| 包 | 用途 | 规范 |
| --- | --- | --- |
| `packages/config` | 命名环境解析与切换（`ENVIRONMENTS` + `.active_env` / `ARGON_ENV`）；API base URL | `python -m packages.config` |
| `packages/db` | 多数据源 DB 访问（MySQL / SQL Server / PostgreSQL） | `.cursor/rules/packages-db.mdc` |
| `packages/logging` | 统一日志 | `.cursor/rules/packages-logging.mdc`，`packages/logging/README.md` |
| `packages/api_test` | APIModel 运行框架 | `packages/api_test/USAGE.md` |
| `packages/excel` | xlsx/CSV 解析 | — |
| `packages/fake` | 假数据（UDI/USCC/Faker zh_CN）；`run`/`catalog` CLI | `packages/fake/USAGE.md`，`.cursor/rules/packages-fake.mdc` |
| `packages/action_words` | 业务动作层 | `docs/spec/action-words-syntax.md` |
| `packages/api_objects` | 路由对齐 API 资产 | `docs/spec/api-objects-syntax.md` |
| `packages/page_objects` | UI 资产 | `docs/spec/page-objects-syntax.md` |

### 2.1 已冻结的 API Objects（自动/半自动区）

| method + path | 资产文件 | 来源 | 备注 |
| --- | --- | --- | --- |
| _(暂无)_ | | | `python -m apps.recorder` 或 freeze-api-objects 产出 |

### 2.2 已有的 Page Objects

| 页面/组件 | 文件 | 备注 |
| --- | --- | --- |
| _(暂无)_ | | |

## 3. 工具层（apps/）

规范：`docs/spec/apps-authoring-syntax.md`。

| 工具 | 运行 | 用途 | 交接文档 |
| --- | --- | --- | --- |
| `dump_ddl` | `python apps/dump_ddl.py <table> --datasource <alias>` 或 `--all` | **本地**拉取表结构到 `assets/ddl/<alias>/`（不上 Plane） | `apps/README.md`；skill `/dump-ddl` |
| `recorder` | `python -m apps.recorder` | **本地**代理抓包生成 `packages/api_objects`（不上 Plane） | `apps/recorder/README.md` |
| `index_ai` | `python -m apps.index_ai` | **本地**扫描 `.cursor/**` 生成 `.cursor/REGISTRY.md`（不上 Plane） | `apps/index_ai/README.md` |
| `init_repo` | `python -m apps.init_repo --help` | **本地**生成/更新项目仓骨架（不上 Plane） | `apps/init_repo/README.md` |
| `index_platform` | `python -m apps.index_platform --out -` | **Plane Sync** 扫描 catalog JSON（不写 git） | `apps/index_platform/README.md` |

## 4. 测试层（tests/）

| 类型 | 路径 | 说明 |
| --- | --- | --- |
| behave BDD | `tests/features/**` | UI/API 双 stage；见 `.cursor/agents/bdd-asset-pipeline.md` |
| pytest | `tests/pytest/**` | 性能/DB 核对等显式 pytest 套件 |

## 5. AI 组件（.cursor/）

完整注册表（含类型/触发/版本）：[`.cursor/REGISTRY.md`](.cursor/REGISTRY.md)（`python -m apps.index_ai` 生成）。
