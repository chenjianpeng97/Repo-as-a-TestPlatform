<!-- version: 0.1.0 -->
# INDEX.project — dogfood workspace 业务资产地图

> 被测系统 = tuner-testkit 平台本身。生成任何测试/资产前先读这里；平台能力地图见仓根 `INDEX.md`。
> 标有 `auto:` 围栏的区块由 `tuner-workspace index render` 从 `artifacts/catalogs/workspace.json`
> 确定性渲染，不要手改；人工区由 `maintain-index` skill 增量维护。

## 1. 知识层（assets/）

### 1.1 DDL（自动区）

<!-- auto:begin:ddl -->
| datasource | 表 | 路径 |
| --- | --- | --- |
| _(暂无)_ |  |  |
<!-- auto:end:ddl -->

### 1.2 业务 SQL 副本（自动区）

<!-- auto:begin:sql -->
| 文件 | 路径 |
| --- | --- |
| _(暂无)_ |  |
<!-- auto:end:sql -->

### 1.3 用例 / 业务讲解 / 探索 / design / 报告（人工区）

| 路径 | domain | source | confidence | 一句话用途 |
| --- | --- | --- | --- | --- |
| `assets/domain-notes/platform/roadmap.md` | platform | plan 2026-09-22 | high | 平台路线图 A→B→C→D、版本节奏 |
| `assets/usecases/platform/qa-daily-journeys.md` | platform | plan 2026-09-22 §A7 | high | 「QA 一天」五条日常路径与判据 |
| `assets/usecases/workbench/lightweight-user.md` | workbench | plan 2026-09-22 §B | high | 低代码成员使用工作台的主流程与验收 |

## 2. 业务资产（packages/）

### 2.1 API Objects（自动区）

<!-- auto:begin:api_objects -->
| method + path | 文件 |
| --- | --- |
| _(暂无)_ |  |
<!-- auto:end:api_objects -->

### 2.2 Page Objects（自动区）

<!-- auto:begin:page_objects -->
| page | 文件 |
| --- | --- |
| _(暂无)_ |  |
<!-- auto:end:page_objects -->

### 2.3 Action Words（自动区）

<!-- auto:begin:action_words -->
| word_id | 名称 | 类别 |
| --- | --- | --- |
| `db_seed.sample_seed` | 示例造数（dry-run） | db_seed |
<!-- auto:end:action_words -->

## 3. 工具层（apps/，自动区）

<!-- auto:begin:apps -->
| 工具 | 运行 | 用途 | 交接文档 |
| --- | --- | --- | --- |
| `sample_tool` | `python -m apps.sample_tool` | 离线生成带标签的样例行；工作台表单与 QA 一天验收的 fixture。 | `apps/sample_tool/README.md` |
<!-- auto:end:apps -->

## 4. 测试层（tests/，自动区）

<!-- auto:begin:features -->
| feature | 场景数 | 标签 |
| --- | --- | --- |
| `tests/features/platform/qa_daily_journeys.feature` | 5 | platform, dogfood |
| `tests/features/workbench/knowledge_browse.feature` | 3 | workbench, dogfood |
| `tests/features/workbench/run_history.feature` | 2 | workbench, dogfood |
| `tests/features/workbench/run_tool.feature` | 4 | workbench, dogfood |
| `tests/features/workbench/tool_catalog.feature` | 3 | workbench, dogfood |
<!-- auto:end:features -->

## 5. 交付物（artifacts/）

- `artifacts/inbox/`：agent 任务记录（gitignore）。
- `artifacts/evidence/<run_id>/`：探索证据（gitignore）。
- `artifacts/catalogs/workspace.json`：`tuner-workspace catalog` 产物（gitignore）。
