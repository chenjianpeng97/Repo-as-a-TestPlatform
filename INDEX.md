<!-- version: 1.6.0 -->
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
SUT 自学习：`docs/spec/sut-self-learning.md`（编排 `.cursor/agents/sut-self-learning.md`）。
design schema（v0.1 草案）：`docs/spec/design-knowledge-syntax.md`。
agent 任务 log：`docs/spec/agent-task-log.md` → `artifacts/inbox/`。
入库任务与人类提问：`docs/spec/work-task.md` → `work/tasks/`、`artifacts/inbox/questions/`（已回答在 `archived-question/`）。
测试设计：`docs/spec/test-design-syntax.md` → `assets/testdesign/`。
功能用例集：`docs/spec/testcase-syntax.md` → `assets/testcases/<模块>/<功能>.md`（skill `maintain-testcases`）。
交付物目录与 run manifest：`docs/spec/artifacts-layout.md`（`artifacts/{evidence,inbox,runs,reports,catalogs,exports,playwright}`；`tuner_testkit.artifacts`）。
探索账号模板：scaffold 写入 `data/sut-accounts.example.yaml`；本机副本 `data/sut-accounts.local.yaml`（gitignore）。

### 1.1 DDL（自动区，dump_ddl 产出）

| datasource | 表 | 更新 | 备注 |
| --- | --- | --- | --- |
| _(暂无平台内置 DDL)_ | | | 运行 `python -m tuner_testkit.apps.dump_ddl --all --datasource <alias>`；MySQL / SQL Server / PostgreSQL。业务库 DDL 写 `INDEX.project.md` |

变更流水：`assets/CHANGELOG.md`

### 1.2 业务 SQL 副本（assets/sql/，人类可读镜像）

| 文件 | domain | confidence | 用途 |
| --- | --- | --- | --- |
| _(暂无)_ | | | |

### 1.3 用例 / 业务讲解 / 报告 / 探索 / design

| 路径 | domain | source | confidence | 一句话用途 |
| --- | --- | --- | --- | --- |
| `assets/testcases/README.md` | testcases | testcase-syntax | high | 功能用例集的模块总索引；业务模块写在下游仓或 dogfood |
| _(暂无平台内置业务知识)_ | | | | 业务仓写 `INDEX.project.md`。平台约定目录：`usecases/` `domain-notes/` `explore/` `design/` `testdesign/` `testcases/` `testreport/` |

## 2. 运行库（`tuner_testkit/`，PyPI：`tuner-testkit`）与本仓资产（`packages/`）

发行名 `tuner-testkit`，导入名 `tuner_testkit`。tool 域只装默认 wheel（`uv tool install tuner-testkit`，能 `tuner-init` 即可）；`[db]` / `[api]` 等 extra 装在业务仓 `.venv`。本仓 editable 开发用 `uv sync --extra all`（`[dev]` 引用 `[all]`）。标准作业流程见根 [`README.md`](README.md)（即 PyPI 项目说明）。

| extra | 模块 | 用途 |
| --- | --- | --- |
| （默认） | `tuner_testkit.config` / `logging` | 命名环境解析（`TUNER_ENV` > `.active_env`）；统一日志 |
| `[db]` | `tuner_testkit.db` | 多数据源 DB |
| `[api]` | `tuner_testkit.api_test` | APIModel 运行框架 |
| `[web-ui]` | `tuner_testkit.page_test` | Web UI（Playwright）；Python 模块名仍为 `page_test` |
| `[phone-ui]` | — | **预留**，4.0 未实现 |
| `[excel]` / `[fake]` / `[mock]` | 对应模块 | 表格 / 假数据 / api_mock |
| `[workbench]` | `tuner_testkit.workbench` | 本机工作台（复用 `[mock]` 的 fastapi/uvicorn + jinja2） |
| `[recorder]` | `tuner_testkit.apps.{recorder,page_recorder,api_recorder}` | 合录 / 仅 UI / 代理 |
| `[all]` | 元 extra | 能力 extra 并集（含 `workbench`） |
| `[dev]` | 引用 `[all]` | 本仓 editable 开发别名 |
| （默认 wheel） | `tuner_testkit.apps.dna` / dump_ddl / init_repo | `tuner-init` / `tuner-dna` 可在 tool 域裸装使用；`tuner-dump-ddl` 等需业务仓 `[db]` 后 `uv run` |

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
| `packages/action_words` | **本仓**业务动作；基类在 kit。`discover` / 工作台扫描类别子包**含子目录**（如 `db_seed/audit/*.py`） | `docs/spec/action-words-syntax.md` |
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

## 3. 工具层（kit CLI + workspace `apps/`）

公共工具在 **`tuner_testkit.apps`**（`tuner-*` scripts）。workspace 的 `apps/` 只放 **SUT 私有**工具（本仓示范见 `dogfood/apps/`）。规范：`docs/spec/apps-authoring-syntax.md`。

| 工具 | 运行 | 用途 | 交接文档 |
| --- | --- | --- | --- |
| `dump_ddl` | `tuner-dump-ddl` / `python -m tuner_testkit.apps.dump_ddl` | 拉取表结构到 `assets/ddl/<alias>/` | skill `/dump-ddl` |
| `recorder` | `tuner-recorder --app <app>` | headed 合录 Page + API | `tuner_testkit/apps/recorder/README.md` |
| `api_recorder` | `tuner-api-recorder` | mitmproxy 代理冻 API | `tuner_testkit/apps/api_recorder/README.md` |
| `page_recorder` | `tuner-page-recorder --app <app>` | headed 仅冻 Page | `tuner_testkit/apps/page_recorder/README.md` |
| `dna` | `tuner-dna sync` / `check` / `targets`（`--ide cursor,claude,agents,codex,all`） | 把 kit 所带 DNA merge 进项目 `.cursor/` / `docs/spec/` / git-hooks；`--ide` 渲染到 `.claude/`、`.agents/`、`CLAUDE.md` | `tuner-dna --help` |
| `index_ai` | `tuner-index-ai` | 生成 `.cursor/REGISTRY.md` | `tuner_testkit/apps/index_ai/README.md` |
| `init_repo` | `tuner-init scaffold <dir>` | 任意目录铺新仓骨架 + 一次 `dna sync`（wheel 带 `stubs/`；**不再拷**运行库源码） | `tuner_testkit/apps/init_repo/README.md` |
| `workspace` | `tuner-workspace catalog` / `index render\|check` / `run` / `meta stamp` | 确定性 workspace catalog（`artifacts/catalogs/workspace.json`）、INDEX 自动区渲染、按清单运行工具、front-matter 署名 | `tuner_testkit/workspace/README.md` |
| `workbench` | `tuner-workbench` | 本机 127.0.0.1 工作台：目录切片（`@tool` / kit `@register`，含 `db_seed/<域>/*.py`）/ `db_seed` 特化页 / 表单运行 / 运行历史 / AI 组件 / 知识浏览（`[workbench]` extra） | `tuner_testkit/workbench/README.md` |
| `tools`（库） | `from tuner_testkit.tools import tool` | `apps/<name>/tool.py` 的 `@tool` 清单：argparse → `params_schema` + `argv_plan`，供 catalog / 工作台 / 运行器 | `docs/spec/apps-authoring-syntax.md` §5 |
| `mock_server` | `tuner-mock-server serve` | 按 `data/mocks` 回放（需 `[mock]`） | `tuner_testkit/apps/mock_server/README.md` |
| `evidence` | `tuner-evidence persist` / `attach` / `routes` | MCP/网络 dump 脱敏落盘 `artifacts/evidence/<run_id>/`，并可挂上截图、脱敏日志、接口 JSON 与 `task_id` | `tuner_testkit/apps/evidence/README.md` |
| `task` | `tuner-task create` / `ask` / `answer` / `finish` | 入库任务 `work/tasks/`；缺人答的通道写入 `artifacts/inbox/questions/` 并阻塞任务 | `tuner_testkit/apps/task/README.md` |

## 4. 测试层（tests/）

| 类型 | 路径 | 说明 |
| --- | --- | --- |
| behave BDD | workspace `tests/features/**`（本仓示范 `dogfood/tests/features/`） | UI/API 双 stage；探索编排 `.cursor/agents/sut-self-learning.md`；下半程 `.cursor/agents/bdd-asset-pipeline.md` |
| pytest | workspace `tests/pytest/**` | 性能/DB 核对等显式 pytest 套件 |
| kit 回归 | `packages/tests/**`、`tuner_testkit/**/tests/**` | 平台运行库单测（`uv run pytest`） |

## 5. AI 组件（.cursor/）

完整注册表（含类型/触发/版本）：[`.cursor/REGISTRY.md`](.cursor/REGISTRY.md)（`python -m tuner_testkit.apps.index_ai` 生成）。
工作台只读浏览：`uv run tuner-workbench` → `/ai`（与 REGISTRY 同一套扫描）。

## 6. dogfood（`dogfood/`）

用本仓 `tuner-init scaffold dogfood --no-ai` 生成的 workspace，被测系统是平台本身；uv workspace 成员，与平台共用 `.venv`。

| 内容 | 路径 |
| --- | --- |
| 业务资产地图 | [`dogfood/INDEX.project.md`](dogfood/INDEX.project.md) |
| 平台路线图（A→B→C→D） | `dogfood/assets/domain-notes/platform/roadmap.md` |
| 「QA 一天」验收剧本 / 轻量用户场景 | `dogfood/assets/usecases/platform/qa-daily-journeys.md`、`dogfood/assets/usecases/workbench/lightweight-user.md` |
| 活文档（behave） | `dogfood/tests/features/platform/*.feature`、`dogfood/tests/features/workbench/*.feature`（未落地场景 `@wip`） |
| fixture | `dogfood/apps/sample_tool/`、`dogfood/packages/action_words/db_seed/sample_seed.py` |

运行：`uv run --directory dogfood behave --stage api --tags "@offline" --tags "~@wip"`。提交 scope 用 `dogfood`。
