<!-- version: 0.1.0 -->
# INDEX.project — 业务资产地图

> 本仓的被测系统（SUT）业务资产地图。生成任何测试/资产前先读这里；平台能力地图见 `INDEX.md`（kit）。
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

### 1.3 用例 / 业务讲解 / 探索 / design / 报告（自动区：路径与元数据；用途一句话写在下方人工区）

<!-- auto:begin:assets -->
| 路径 | 类别 | domain | source | confidence | 标题 |
| --- | --- | --- | --- | --- | --- |
| _(暂无)_ |  |  |  |  |  |
<!-- auto:end:assets -->

人工区（用途 / 采信说明）：

- _(暂无)_

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
| _(暂无)_ |  |  |
<!-- auto:end:action_words -->

## 3. 工具层（apps/，自动区）

<!-- auto:begin:apps -->
| 工具 | 运行 | 用途 | 交接文档 |
| --- | --- | --- | --- |
| _(暂无)_ |  |  |  |
<!-- auto:end:apps -->

## 4. 测试层（tests/，自动区）

<!-- auto:begin:features -->
| feature | 场景数 | 标签 |
| --- | --- | --- |
| _(暂无)_ |  |  |
<!-- auto:end:features -->

## 5. 交付物（artifacts/）

见 `docs/spec/artifacts-layout.md`：`evidence/`、`inbox/`、`runs/`、`reports/`、`catalogs/`、`exports/`（均 gitignore）。
