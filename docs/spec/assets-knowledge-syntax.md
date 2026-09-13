# assets 知识层规范（assets-knowledge-syntax）

> `assets/` 是平台的**知识地基**：给人和 LLM 阅读、作为生成测试代码/工具的依据。
> 本规范定义目录分类、文件元数据、raw 与 curated 的边界，以及可追溯原则。
> 配套硬约束见 `.cursor/rules/assets-knowledge.mdc`；全局发现入口见根 `INDEX.md`。
> SUT 自学习如何消费这些知识见 `docs/spec/sut-self-learning.md`；
> `design/` 的正文 schema 见 `docs/spec/design-knowledge-syntax.md`。

## 1. 目录分类

```text
assets/
├── ddl/<datasource>/<table>.sql   # 工具产出(自动区): 表结构，tuner-dump-ddl 生成
├── sql/<name>.sql                 # 人类可读的业务 SQL 副本
├── usecases/<domain>/<name>.md    # 禅道/XMind 导出、整理后的用例
├── domain-notes/<domain>/<name>.md# 业务讲解、字段含义、权限规则、环境约束
├── explore/<app>/<name>.md        # 探索式测试产出的能力清单 / 站点地图（半自动）
├── design/<app>/<route-slug>.md   # API↔DB effects 收敛知识（见 design-knowledge-syntax）
├── testreport/<name>.md           # 测试报告类原始资产
└── CHANGELOG.md                   # 自动区变更流水(供 maintain-index 读取 delta)
```

- **自动区**（工具产出，可被覆盖重写）：`ddl/`、以及每次生成会追加 `CHANGELOG.md`。
  人不手改这些文件的内容语义；要更新就重跑工具。
- **人工/半自动区**：`sql/`、`usecases/`、`domain-notes/`、`explore/`、`design/`、`testreport/`。
- `apidoc/` **不单列**：人工导入的接口说明放 `domain-notes/` 或 `usecases/`；
  运行时冻结的契约在 `packages/api_objects/`。是否再拆目录留给下游实践决定。

## 2. 文件头元数据（front-matter）

**人工/半自动区**的 `.md` / `.sql` 文件建议在文件头写元数据：

Markdown（YAML front-matter）：

```markdown
---
domain: authorization
source: zentao#1234
date: 2026-08-15
version: 1.0.0
confidence: high
evidence: []          # 可选：artifacts/evidence/<run_id> 列表（explore/design 建议填）
---
```

SQL（顶部行注释，等价字段）：

```sql
-- domain: authorization
-- source: 手工核对(生产只读库)
-- date: 2026-08-15
-- version: 1.0.0
-- confidence: high
SELECT ...
```

- `confidence` 是 LLM 的**采信优先级**信号：`high` 的人工经验优先于自动推断。
- `ddl/` 由工具产出，不要求 front-matter；其可信度来自 `CHANGELOG.md`。
- `explore/` 与 `design/` 应填 `evidence`，把知识指回一次 MCP/工具运行。

## 3. raw 与 curated 的边界

- **raw**（原始导入物，如禅道/XMind 直出 CSV/MD）：**不得改写语义**，只允许补充元数据头与放置到正确目录。
- **curated**（加工后的知识）：可编辑，但必须保留 `source` 指回 raw 来源，并 bump `version`。

## 4. 可追溯原则

- 每份知识都能回答"从哪来、何时、什么版本、多可信"。
- 更新 curated 知识 → bump `version` 并在正文追加简短变更说明。
- 自动区更新 → 由工具写 `CHANGELOG.md`。

## 5. 与其它层的关系

- 造数 action word 从 `assets/ddl/<datasource>/<table>.sql` 取列名。
- 业务 SQL 服务在 `packages/<domain>/` 实现，同时镜像人类可读副本到 `assets/sql/`。
- 探索会话产出能力清单 → `assets/explore/`；effects 知识 → `assets/design/`。
- 生成任何测试/资产前，先查根 `INDEX.md`（及存在时的 `INDEX.project.md`）。
