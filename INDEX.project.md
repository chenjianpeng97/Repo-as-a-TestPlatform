<!-- version: 1.0.0 -->
# INDEX.project — Plane dogfood 业务资产地图

> 只登记**被测系统 Plane**的资产。平台能力（公共 packages、apps、AI 组件）见
> [`INDEX.md`](INDEX.md)。
> 本文件只存在于 `plane-dogfood`；`main` 不包含它，因此 `main → plane-dogfood`
> 合入不会对打。
>
> Dogfood：用 Plane 可视化本测试仓，同时用本仓回归 Plane。
>
> 维护：`maintain-index` skill 在本文件存在时把 DDL / SQL / 用例 / api_objects /
> page_objects / features 写到这里。

## 1. 知识层（assets/）

规范：`docs/spec/assets-knowledge-syntax.md`。

### 1.1 DDL（自动区，apps/dump_ddl 产出）

| datasource | 表文件数 | 路径 | 备注 |
| --- | --- | --- | --- |
| _(暂无)_ | | | 运行 `python apps/dump_ddl.py <table> --datasource <alias>` 生成 |

### 1.2 业务 SQL 副本（assets/sql/）

| 文件 | 用途 |
| --- | --- |
| _(暂无)_ | |

### 1.3 用例 / 业务讲解 / 报告

| 路径 | 一句话用途 |
| --- | --- |
| _(暂无)_ | |

## 2. 组件层（业务资产）

主数据样例：需要时新增 `packages/action_words/_internal/params_project.py`（经 `params.py` 转出）。
共享模型：需要时新增 `packages/action_words/models_project.py`（经 `models.py` 转出）。

### 2.1 已冻结的 API Objects

| method + path | 资产文件 | 来源 | 备注 |
| --- | --- | --- | --- |
| _(暂无)_ | | | `python -m apps.recorder` 或 freeze-api-objects 产出 |

### 2.2 已有的 Page Objects

| 页面/组件 | 文件 | 备注 |
| --- | --- | --- |
| _(暂无)_ | | |

### 2.3 Action Words

| 类别 | 模块 | 备注 |
| --- | --- | --- |
| _(暂无)_ | | |

## 3. 试验田工具（非平台 DNA）

| 工具 | 路径 | 说明 |
| --- | --- | --- |
| _(暂无)_ | | 定型为平台能力后：在 **`main`** 实现并提交，再 merge 进本分支 |

## 4. 测试层

| 类型 | 路径 | 说明 |
| --- | --- | --- |
| _(暂无)_ | | 业务 `.feature` / pytest 落在本分支；步骤夹具仍用平台 `tests/features/*_steps` |

变更纪律见 `.cursor/rules/index-hygiene.mdc`。
