<!-- version: 1.2.0 -->
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

### 1.1 DDL（自动区，dump_ddl 产出）

| datasource | 表 | 更新 | 备注 |
| --- | --- | --- | --- |
| _(暂无平台内置 DDL)_ | | | 运行 `python -m tuner_testkit.apps.dump_ddl --all --datasource <alias>`；MySQL / SQL Server / PostgreSQL。业务库 DDL 写 `INDEX.project.md` |

变更流水：`assets/CHANGELOG.md`

### 1.2 业务 SQL 副本（assets/sql/，人类可读镜像）

| 文件 | domain | confidence | 用途 |
| --- | --- | --- | --- |
| _(暂无)_ | | | |

### 1.3 用例 / 业务讲解 / 报告（usecases / domain-notes / testreport）

| 路径 | domain | source | confidence | 一句话用途 |
| --- | --- | --- | --- | --- |
| _(暂无)_ | | | | |

## 2. 运行库（`tuner_testkit/`，PyPI：`tuner-testkit`）与本仓资产（`packages/`）

发行名 `tuner-testkit`，导入名 `tuner_testkit`。下游用 extras 按需安装；本仓 editable 开发用 `uv sync --extra dev`。

| extra | 模块 | 用途 |
| --- | --- | --- |
| （默认） | `tuner_testkit.config` / `logging` | 命名环境解析（`TUNER_ENV` > 旧名 `ARGON_ENV` > `.active_env`）；统一日志 |
| `[db]` | `tuner_testkit.db` | 多数据源 DB |
| `[api]` | `tuner_testkit.api_test` | APIModel 运行框架 |
| `[web-ui]` | `tuner_testkit.page_test` | Web UI（Playwright）；Python 模块名仍为 `page_test` |
| `[phone-ui]` | — | **预留**，4.0 未实现 |
| `[excel]` / `[fake]` / `[mock]` | 对应模块 | 表格 / 假数据 / api_mock |
| `[recorder]` | `tuner_testkit.apps.{recorder,page_recorder,api_recorder}` | 合录 / 仅 UI / 代理 |
| （默认 wheel） | `tuner_testkit.apps.dna` / dump_ddl / init_repo | `tuner-dna`、`tuner-dump-ddl`、`tuner-init` 等 scripts；mock 运行时仍需 `[mock]` |

console_scripts：`tuner-config`、`tuner-recorder`、`tuner-dna`、`tuner-init`、`tuner-dump-ddl` 等，等价于 `python -m tuner_testkit.…`。

| 包 | 用途 | 规范 |
| --- | --- | --- |
| `tuner_testkit.config` | 解析器；读写 **SUT** `config/`（密钥不进 wheel） | `python -m tuner_testkit.config` / `tuner-config` |
| `tuner_testkit.db` | 多数据源 DB（MySQL / SQL Server / PostgreSQL） | `.cursor/rules/packages-db.mdc` |
| `tuner_testkit.logging` | 统一日志 | `.cursor/rules/packages-logging.mdc` |
| `tuner_testkit.api_test` | APIModel 运行框架 | `tuner_testkit/api_test/USAGE.md` |
| `tuner_testkit.api_mock` | 用 api_objects + `data/mocks` 起 mock server | `tuner_testkit/api_mock/README.md` |
| `tuner_testkit.page_test` | PageModel 运行框架（`[web-ui]`） | `tuner_testkit/page_test/USAGE.md` |
| `tuner_testkit.excel` / `fake` | 表格解析 / 假数据 | 对应 USAGE |
| `packages/action_words` | **本仓**业务动作；基类在 kit | `docs/spec/action-words-syntax.md` |
| `packages/api_objects` | **本仓**路由资产；冻结内核在 kit `recording/` | `docs/spec/api-objects-syntax.md` |
| `packages/page_objects` | **本仓** UI 资产 | `docs/spec/page-objects-syntax.md` |

### 2.1 已冻结的 API Objects（自动/半自动区）

| method + path | 资产文件 | 来源 | 备注 |
| --- | --- | --- | --- |
| _(暂无)_ | | | `python -m tuner_testkit.apps.recorder` / `python -m tuner_testkit.apps.api_recorder` 或 freeze-api-objects 产出 |

### 2.2 已有的 Page Objects

| page_id | 文件 | 范式 | 备注 |
| --- | --- | --- | --- |
| _(暂无)_ | | | `python -m tuner_testkit.page_test list` 列出实际发现的资产 |

## 3. 工具层（kit CLI + 本仓 `apps/`）

公共工具在 **`tuner_testkit.apps`**（`tuner-*` scripts）。本仓 `apps/` 只放 **SUT 私有**工具。规范：`docs/spec/apps-authoring-syntax.md`。

| 工具 | 运行 | 用途 | 交接文档 |
| --- | --- | --- | --- |
| `dump_ddl` | `tuner-dump-ddl` / `python -m tuner_testkit.apps.dump_ddl` | 拉取表结构到 `assets/ddl/<alias>/` | skill `/dump-ddl` |
| `recorder` | `tuner-recorder --app <app>` | headed 合录 Page + API | `tuner_testkit/apps/recorder/README.md` |
| `api_recorder` | `tuner-api-recorder` | mitmproxy 代理冻 API | `tuner_testkit/apps/api_recorder/README.md` |
| `page_recorder` | `tuner-page-recorder --app <app>` | headed 仅冻 Page | `tuner_testkit/apps/page_recorder/README.md` |
| `dna` | `tuner-dna sync` / `check` | 把 kit 所带 DNA merge 进项目 `.cursor/` / `docs/spec/` / git-hooks | `tuner-dna --help` |
| `index_ai` | `tuner-index-ai` | 生成 `.cursor/REGISTRY.md` | `tuner_testkit/apps/index_ai/README.md` |
| `init_repo` | `tuner-init scaffold <dir>` | 新仓骨架 + 一次 `dna sync`（**不再拷**运行库源码） | `tuner_testkit/apps/init_repo/README.md` |
| `index_platform` | `tuner-index-platform --out -` | Plane Sync catalog JSON | `tuner_testkit/apps/index_platform/README.md` |
| `mock_server` | `tuner-mock-server serve` | 按 `data/mocks` 回放（需 `[mock]`） | `tuner_testkit/apps/mock_server/README.md` |

## 4. 测试层（tests/）

| 类型 | 路径 | 说明 |
| --- | --- | --- |
| behave BDD | `tests/features/**` | UI/API 双 stage；见 `.cursor/agents/bdd-asset-pipeline.md` |
| pytest | `tests/pytest/**` | 性能/DB 核对等显式 pytest 套件 |

## 5. AI 组件（.cursor/）

完整注册表（含类型/触发/版本）：[`.cursor/REGISTRY.md`](.cursor/REGISTRY.md)（`python -m tuner_testkit.apps.index_ai` 生成）。
