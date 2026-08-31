# Framework changelog（公共组件变更记录）

本仓库是测试框架模板仓。从业务试验田
`C:\dev\repo\innovamed-test` 验证通过后回灌的**公共框架能力**记录于此，
便于对照来源 commit 与同步路径。

## 维护约定

- **何时写**：改动下列任一可回灌 / 已回灌路径时，同一提交必须追加条目：
  - `packages/api_test/**`
  - `packages/page_test/**`
  - `packages/page_objects/session.py`（凭据与回放接缝，非业务资产）
  - `packages/db/**`
  - `packages/config.py`
  - `packages/logging/**`
  - `packages/excel/**`
  - `packages/fake/**`
  - `apps/recorder/**`
  - `apps/dump_ddl.py`
  - `apps/_shared/**`
  - `apps/index_platform/**`
  - `docs/spec/**`（框架规范）
  - `.cursor/skills/**` / `.cursor/rules/**`
  - 本文件 `docs/changelog/FRAMEWORK.md`
- **不写**：业务资产（具体 `packages/api_objects/<业务路由>/...`）、业务 `action_words`、业务 feature/场景。
- **commit**：提交产生后用 `git rev-parse HEAD`（或 short hash）回填；未提交前写 `TBD`。
- **来源**：条目可注明试验田来源 hash，便于追溯。

## 条目模板

```markdown
## YYYY-MM-DD — <short-title>

- **commit**: `<hash>`
- **来源**: `innovamed-test@<hash>`（可选）
- **目的**: …
- **路径**:
  - `…`
- **不在同步范围**: …
- **验证**: …
```

---

## 2026-08-31 — api_objects 可回放为 mock server（packages.api_mock / apps.mock_server）

- **commit**: `ca0ebc6`
- **目的**: 让冻结的 `APIModel` 资产能直接起一个可在运行时改返回值的 mock 服务，
  供后端未就绪 / 造异常分支 / 测试平台按需定义响应时使用。
  `APIModel` 只描述请求契约（`response_hints` 仅有顶层键名、状态码只藏在 asserts 里、
  真实样例 `_RECORDED_RESPONSE` 在 `__main__` 块内 import 不到），
  因此**响应契约外置**到 `data/mocks/**.json`，按路由树与资产一一对照，
  `packages/api_test` 与 `apps/recorder` 均未改动。
- **路径**:
  - `packages/api_mock/**`（`spec` 定义 / `store` 磁盘+内存覆盖 / `router` 占位符匹配 / `app` FastAPI）
  - `packages/api_objects/registry.py`（`iter_api_models()`：按文件位置加载，
    修正了按点分模块名发现会跳过 `prod-api` 这类非标识符路由目录的问题）
  - `apps/mock_server/**`（`serve` / `seed` / `routes`；`plane.py` 用 `runtime="long_lived"`
    登记为常驻服务，是本仓第一个使用该 runtime 的 app）
  - `apps/recorder/**`（新增 `--write-mocks`：抓包时把**完整**响应另存为 mock 定义。
    资产里的 `_RECORDED_RESPONSE` 仍按 `truncate_sample` 截断以保证源码可读，
    完整体走 `data/mocks/`，两者同路由树同 `v<N>`；`mocks.py` + `FreezeResult.major`）
  - `apps/init_repo/manifest.py`（`PLATFORM_PATHS` 追加 `apps/mock_server`）
  - `pyproject.toml`（新增 `mock` extra：fastapi / uvicorn / httpx）
  - `packages/tests/test_api_mock_*.py`、`test_api_objects_registry.py`、`test_mock_server_seed.py`、
    `apps/recorder/tests/test_mock_samples.py`
- **不在同步范围**: `data/mocks/**`（项目业务资产，不随平台 DNA 分发）
- **验证**: `uv run --extra test --extra mock pytest packages/tests apps -q`（+88 用例）；
  真实起服后用未改动的 `APIModel` 经 `TEST_BASE_URL` 打通并通过断言/提取；
  `--write-mocks` 抓 137 行响应后由 mock server 原样回放（资产侧仍为 5 行 + 截断标记，凭证仍掩码）；
  `python -m apps.index_platform --out -` 可见 `mock_server`（`plane_runnable=false`）；模板版本 2.5.0

## 2026-08-31 — packages.fake 公共造数包

- **commit**: `22ca2c8`
- **目的**: 提供可 seed 的假数据生成器（医疗 UDI/社信码自研 + Faker zh_CN 包装），CLI/`run`/`catalog` 与业务单值函数共用契约，供测试员手工造数与后续平台 Fake 页。
- **路径**:
  - `packages/fake/**`
  - `packages/tests/test_fake_*.py`
  - `packages/action_words/_internal/generators.py`（re-export）
  - `pyproject.toml` / `uv.lock`（`faker`）
  - `.cursor/rules/packages-fake.mdc`
  - `.cursor/rules/bdd-asset-layering.mdc`
  - `.cursor/skills/create-action-word/SKILL.md`
  - `INDEX.md` / `AGENTS.md` / `docs/spec/action-words-syntax.md`
- **不在同步范围**: jafron 业务 db_seed 换 import（后续合并后再改）
- **验证**: `uv run --extra test pytest packages/tests/test_fake_medical.py packages/tests/test_fake_china.py packages/tests/test_fake_core.py packages/tests/test_fake_cli.py -q`；`python -m packages.fake list`

## 2026-08-29 — page_test 运行库：PageModel 资产 + 多定位器备用 + doctor 体检

- **commit**: `a0193d9`
- **目的**: 把 Page Object 从「手写 class + `@property` locator」升级为与 `packages.api_test`
  同构的运行库：`PageModel`（元素表 + 声明式 flow）对位 `APIModel`、`PageDriver` 对位
  `ApiClient`。三个可落地的收益：
  1. **稳定性**：每个元素挂一组按优先级排序的候选定位器，运行时顺序探测；首选失效时
     自动降级（测试不红），并产出健康事件避免资产静默腐烂。`locator_policy` 把
     `page-objects-syntax.md` 的 locator 约束变成运行时可执行的校验（对位
     `headers_policy` 拦截敏感请求头）。
  2. **独立运行**：`python -m packages.page_test run/list/describe/validate/catalog/doctor`，
     以及资产文件 `__main__` 单文件回放（对位 api_objects 的 `auth.replay_execute`）。
  3. **平台化 / recorder 接缝**：`describe()` 导出元素表 + 流程步骤表，step 与
     `LocatorSpec` 双向 `to_dict()` / `from_dict()`，`fingerprint()` 供去重。
  复杂交互走 `BasePage` 逃生舱：动作写 Python 方法，元素声明不变，因此照样享受
  fallback、可视化与体检。自愈只做级别一（运行时降级）与级别二（doctor 审计），
  **不做**级别三（自动改写资产源码）。
- **路径**:
  - `packages/page_test/**`（`locator` / `steps` / `model` / `driver` / `base` / `health`
    / `registry` / `errors` / `testing` / `__main__` / `USAGE.md`）
  - `packages/page_objects/session.py`（凭据与单文件回放接缝）、`packages/page_objects/__init__.py`
  - `packages/config.py`（新增 `get_ui_base_url()`：`TEST_UI_BASE_URL` → `config.env` → 回落 API host）
  - `packages/tests/test_page_test_{locator,steps,model,driver,health,base,registry}.py`、
    `packages/tests/test_page_objects_session.py`
  - `docs/spec/page-objects-syntax.md`（改写：元素声明表 / 多定位器 / 两种范式 / 独立运行；
    并修订 locator 策略——绝对 XPath 保留硬禁、相对 XPath 放宽为降权候选、索引定位区分
    「消歧」与「寻址」、纯文本定位降档、修正 test_id 优先级的措辞矛盾）
  - `.cursor/rules/packages-page-test.mdc`（新增）
  - `.cursor/skills/maintain-page-objects/SKILL.md`（2.0.0）
  - `pyproject.toml`（version bump）、`INDEX.md` §2 / §2.2
  - `docs/changelog/FRAMEWORK.md`（本条目）
- **不在同步范围**: 具体业务页面资产（`packages/page_objects/<app>/...`）、`apps/page_recorder`
  （后续独立任务，本期只留 codegen 接缝与命名约定）、`Pages` 容器与 `context.pages` 注册
  （第二阶段，本期只提供 `PageDriver.attach(page)` 接缝）
- **验证**: `uv run --extra test pytest packages/tests -q`（全程离线：`driver` 惰性 import
  playwright，`packages.page_test.testing` 提供 FakePage 替身）；
  `uv run python -m packages.page_test validate`

## 2026-08-24 — 本机多套环境一键切换（packages.config）

- **commit**: `1acea69`
- **目的**: 在 gitignore 的 `env_local.ENVIRONMENTS` 维护 prd/uat/dev 等目录，用 `.active_env` / `ARGON_ENV` 激活一套，避免注释切换。
- **路径**:
  - `packages/config.py`
  - `config/env.py` / `config/env_local.py.example`
  - `packages/tests/test_config_env_profiles.py`
  - `apps/init_repo/manifest.py`（manifest 排除 `env_local.py` / `.active_env`）
- **不在同步范围**: `config/env_local.py`、`config/.active_env`（本机密钥与激活指针）
- **验证**: `uv run --extra test pytest packages/tests/test_config_env_profiles.py -q`；模板版本 2.4.0

## 2026-08-19 — 细分 @plane_* 资产注册，Formulation 不再文件扫描

- **commit**: `a1f75b5`
- **来源**: `plane-dogfood@e04974d`
- **目的**: 能在 Plane 上架的 action words / API / Page 必须 opt-in；执行走 `python -m packages.action_words`，不再把 packages 伪装成 `apps.action_runner`。
- **路径**:
  - `packages/action_words/plane.py`
  - `packages/api_objects/plane.py`
  - `packages/page_objects/plane.py`
  - `apps/_shared/plane_asset.py` / `apps/_shared/plane.py`
  - `apps/index_platform/build.py`
  - 删除 `apps/action_runner/**`
  - `docs/spec/action-words-syntax.md` / `docs/spec/apps-authoring-syntax.md`
  - `.cursor/rules/apps-authoring.mdc` / `.cursor/rules/bdd-asset-layering.mdc`
  - `INDEX.md` / `apps/README.md`
  - `pyproject.toml`（version 2.3.0）
  - `docs/changelog/FRAMEWORK.md`（本条目）
- **不在同步范围**: 业务 action words 实现、具体 `.feature`
- **验证**: `pytest apps/_shared/tests apps/index_platform/tests -q`；catalog `tools` 不含 `db_seed`；`components.action_words` 不含 `context`

## 2026-08-19 — apps 作为常规包，保证 python -m 可导入

- **commit**: `20cbc19`
- **来源**: `plane-dogfood@64bf0be`
- **目的**: 补 `apps/__init__.py`，避免 uv 安装后 `python -m apps.index_platform` 找不到模块。mitmproxy 移到 `recorder` extra，Runner 的 `uv sync --no-dev` 不再拉 cryptography。
- **路径**:
  - `apps/__init__.py`
  - `pyproject.toml`（`namespaces = true`；mitmproxy 仅 recorder extra）
  - `uv.lock`
  - `apps/init_repo/manifest.py`
  - `docs/spec/apps-authoring-syntax.md`
  - `.cursor/rules/apps-authoring.mdc`
  - `docs/changelog/FRAMEWORK.md`（本条目）
- **不在同步范围**: 业务 action words、具体 `.feature`
- **验证**: `python -m apps.index_platform --out -` 在干净 venv 中可启动

## 2026-08-19 — Plane Job 协议：@plane_app + action_runner + index_platform

- **commit**: `02dc0f8`
- **来源**: `plane-dogfood@03c3bc2`
- **目的**: 本地维护工具（dump_ddl / recorder / init_repo / index_ai）不上 Plane；造数/API 动作经 `apps.action_runner` 浅封装 `packages.action_words`；Sync 用 `apps.index_platform` 导出 catalog。BDD/pytest 仍只引用 packages。
- **路径**:
  - `apps/_shared/plane_app.py`
  - `apps/action_runner/**`
  - `apps/index_platform/**`
  - `apps/init_repo/manifest.py`（PLATFORM_PATHS）
  - `docs/spec/apps-authoring-syntax.md` / `docs/spec/action-words-syntax.md`
  - `.cursor/rules/apps-authoring.mdc` / `.cursor/rules/bdd-asset-layering.mdc`
  - `INDEX.md` / `apps/README.md`
  - `pyproject.toml`（version 2.2.0）
  - `docs/changelog/FRAMEWORK.md`（本条目）
- **不在同步范围**: 业务 action words 实现、具体 `.feature`
- **验证**: `uv run pytest apps/action_runner/tests apps/index_platform/tests -q`；`python -m apps.index_platform --out -` 的 tools 含 `db_seed` 不含 `dump_ddl`

## 2026-08-18 — dump_ddl 样例 INSERT 剔除密钥列并限制体积

- **commit**: `72e2a7d`
- **目的**: 恢复默认「注释掉的最新一行 INSERT」，同时避免 password/token/session 与超长 stdout 进入 `assets/ddl`。
- **路径**:
  - `apps/dump_ddl.py`
  - `.cursor/skills/dump-ddl/SKILL.md`
  - `apps/README.md`
  - `docs/changelog/FRAMEWORK.md`（本条目）
- **不在同步范围**: 业务 `assets/ddl` 正文
- **验证**: `python apps/dump_ddl.py --all --datasource main` 后 `.sql` 末尾有 `-- INSERT` 或省略说明，且不含 `password`/`token` 字面量

## 2026-08-18 — PostgreSQL 数据源 + dump_ddl pg_catalog + /dump-ddl skill

- **commit**: `48eb39d`
- **目的**: 让平台能对接 Plane 等 PostgreSQL 库：`packages.db` 增加 `type: postgres`（psycopg3）；`dump_ddl` 从 `pg_catalog` 导出 DDL；新增 on-demand skill `/dump-ddl` 固化「配 env → 拉表结构 → 更新索引」流程。
- **路径**:
  - `packages/db/**`（`connection` / `client` / `__init__`）
  - `packages/action_words/_internal/db.py` / `base.py`
  - `packages/tests/test_db_multidatasource.py`
  - `apps/dump_ddl.py` / `apps/README.md`
  - `config/env.py` / `config/env_local.py.example`
  - `pyproject.toml`（`psycopg[binary]>=3.2`，version 2.1.0）
  - `.cursor/rules/packages-db.mdc`
  - `.cursor/skills/dump-ddl/SKILL.md`
  - `.cursor/skills/create-action-word/SKILL.md`
  - `docs/spec/action-words-syntax.md` / `docs/spec/apps-authoring-syntax.md`
  - `INDEX.md`
  - `docs/changelog/FRAMEWORK.md`（本条目）
- **不在同步范围**: 业务 `assets/ddl` 内容、`config/env_local.py`、`config/env_overlay.py`（试验田覆盖）
- **验证**: `uv run pytest packages/tests/test_db_multidatasource.py -q`；有 Plane 本地库时 `python apps/dump_ddl.py --all --datasource main`

## 2026-08-14 — 多数据源 SQLAlchemy（packages.db + dump_ddl + action word datasource）

- **commit**: `642abf7`
- **来源**: `innovamed-test@f2ccb95`
- **目的**: 引入 SQLAlchemy 引擎内核与命名数据源（`DATABASES` 别名），使测试框架可同时对接 MySQL / SQL Server；action word 类元数据 `datasource` 显式声明目标库；`dump_ddl` 双方言导出到 `assets/ddl/<别名>/`。
- **路径**:
  - `packages/db/**`（`DbClient` / `connection` / `__init__`）
  - `packages/action_words/base.py` / `context.py` / `_internal/db.py` / `__init__.py`
  - `apps/dump_ddl.py` / `apps/README.md`
  - `packages/tests/test_db_multidatasource.py`
  - `config/env.py`（仅 `DATABASES` 结构与占位示例；真实连接信息不入模板）
  - `docs/spec/action-words-syntax.md`
  - `.cursor/rules/packages-db.mdc`
  - `.cursor/skills/create-action-word/SKILL.md`
  - `pyproject.toml`（`sqlalchemy>=2.0`、`pymssql>=2.3.0`）
  - `docs/changelog/FRAMEWORK.md`（本条目）
- **不在同步范围**: 业务 action_words、具体连接凭据、业务 `assets/ddl` 内容
- **验证**: `uv run pytest packages/tests/test_db_multidatasource.py packages/tests/test_action_word_template.py -q`

## 2026-08-14 — APIModel multipart + recorder 冻结 Excel 上传

- **commit**: `3e0c74a`
- **来源**: `innovamed-test@fae6d0f`
- **目的**: APIModel 支持 `body_format=multipart` / `set_files`；recorder 正确解析并冻结 multipart（仅字段名，不写文件内容），形成「捕获 → 冻结 → 调用」闭环，便于 Excel 导入类接口自动化。
- **路径**:
  - `packages/api_test/**`（`model.py` / `client.py` / `errors.py` / `USAGE.md`）
  - `packages/api_objects/auth.py`（`replay_execute(..., files=)`）
  - `packages/tests/test_multipart_files.py`
  - `apps/recorder/**`（`capture` / `normalize` / `codegen` / `freeze` / README / tests）
  - `docs/spec/api-objects-syntax.md`
  - `.cursor/skills/freeze-api-objects/SKILL.md`
  - `docs/changelog/FRAMEWORK.md`（本文件）
- **不在同步范围**: 具体业务 `api_objects` 路由资产、业务 action_words / features
- **验证**: `uv run pytest packages/tests/test_multipart_files.py apps/recorder/tests -q`
