# Framework changelog（公共组件变更记录）

本仓库是测试框架模板仓。从业务试验田
`C:\dev\repo\innovamed-test` 验证通过后回灌的**公共框架能力**记录于此，
便于对照来源 commit 与同步路径。

## 维护约定

- **何时写**：改动下列任一可回灌 / 已回灌路径时，同一提交必须追加条目：
  - `packages/api_test/**`
  - `packages/db/**`
  - `packages/logging/**`
  - `packages/excel/**`
  - `apps/recorder/**`
  - `apps/dump_ddl.py`
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
