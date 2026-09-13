# design 知识规范（v0.1 草案）

> **状态**：v0.1 草案。待下游 dogfood（Plane）实践收敛后再升 v0.2。
> 不要把本文件当成冻结的 API。缺字段、多余字段、命名不贴，都记回本文件。
>
> 归属：`assets/design/`。总流程见 [`sut-self-learning.md`](sut-self-learning.md)。
> 与 `api-objects-syntax.md` / `page-objects-syntax.md` 平级，但是**知识**不是可执行代码。

## 1. 原则

- **来源开放**：日志、DB diff、源码、人工文档、MCP 网络均可。
- **产物收敛**：一篇文档描述 **一条业务路由** 的 DB/外部副作用，可供
  `db_assert` / action words / Then 步骤直接引用。
- **可溯源**：每条 `writes` 必须能指回 evidence 或源码位置。
- **noise 不当断言**：审计表、操作日志默认进 `noise`，禁止当业务结果断言。

## 2. 路径与命名

```text
assets/design/<app>/<route-slug>.md
```

- `<app>`：与 page_objects 的 app 分段对齐（如 `web`）。
- `<route-slug>`：由 method + normalized_path 派生，例如
  `post-api-v1-workspaces-projects-issues.md`。

一篇文档 **只描述一条路由**。同一 path 的 GET/POST 拆开。

## 3. Front-matter

```yaml
---
domain: issue
source: explore+source-code
date: 2026-09-13
version: 0.1.0
confidence: inferred          # observed | inferred | verified
evidence:
  - artifacts/evidence/20260913T133000Z-issue-create/
route: POST /api/v1/workspaces/{slug}/projects/{id}/issues/
method: POST
normalized_path: /api/v1/workspaces/{slug}/projects/{id}/issues/
api_object_ref: packages/api_objects/api/v1/workspaces/projects/issues/POST.v1.py
page_ref:
  page_id: web.project_issues@v1
  trigger: "New Issue"        # 按钮 / 控件名，可空
---
```

`confidence` 在本资产上的含义：

| 值 | 含义 |
| --- | --- |
| `observed` | DB diff / SQL 日志实测 |
| `inferred` | 源码或文档推导 |
| `verified` | 人工核实（对应 assets 的 `high`） |

## 4. 正文 schema（骨架）

```markdown
# POST /api/v1/workspaces/{slug}/projects/{id}/issues/

## writes
- issues            INSERT
  correlate: body.name → name, path.project_id → project_id
  identity: id
- issue_description INSERT
  correlate: issue_id ← issues.id

## noise
- issue_activities  INSERT   # 审计，默认不当业务断言

## reads
- states, project_members     # 只读校验，locate 可忽略

## notes
- 源码：apps/api/plane/db/models/issue.py Issue.save
```

字段约定：

- `writes[]`: `table` + `op`（INSERT/UPDATE/DELETE）+ 可选 `correlate` + 可选 `identity`
- `correlate`: `body.<field> → <column>` 或 `path.<seg> → <column>` 或
  `<column> ← <other_table>.<identity>`
- `identity`: 新行主键列名，供后续断言 locate
- `noise[]`: 每次操作都写、但不是业务结果的表
- `reads[]`: 请求过程中的只读表（权限/枚举），默认不断言

## 5. 硬约束

- 不得写入 token / cookie / 密码 / 真实邮箱（可用掩码）。
- `noise` 表不得写入 `db_assert` action words 作为业务断言。
- 没有 `evidence` 且 `source` 也不是明确的源码路径时，不得把 `confidence`
  标成 `observed`。
- 更新文档必须 bump `version`。

## 6. 实践待决（dogfood 回来改）

- 要不要按「一次用户动作」而不是「一条路由」成文（一个按钮打出多条 API）？
- `page_ref` 一个文档是否允许多个 trigger？
- `writes` 是否需要 `where` 条件模板（UPDATE 场景）？
- 要不要独立的 `externals:`（发邮件 / 写 S3 / 调 webhook）？
