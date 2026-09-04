# assets 知识层规范（assets-knowledge-syntax）

> `assets/` 是平台的**知识地基**：给人和 LLM 阅读、作为生成测试代码/工具的依据。
> 本规范定义目录分类、文件元数据、raw 与 curated 的边界，以及可追溯原则。
> 配套硬约束见 `.cursor/rules/assets-knowledge.mdc`；全局发现入口见根 `INDEX.md`。

## 1. 目录分类

```text
assets/
├── ddl/<datasource>/<table>.sql   # 工具产出(自动区): 表结构，tuner-dump-ddl / tuner_testkit.apps.dump_ddl 生成
├── sql/<name>.sql                 # 人类可读的业务 SQL 副本(packages-db.mdc 约定镜像)
├── usecases/<domain>/<name>.md    # 禅道/XMind 导出、整理后的用例
├── domain-notes/<domain>/<name>.md# 业务讲解、字段含义、权限规则等高置信度经验
├── testreport/<name>.md           # 测试报告类原始资产
└── CHANGELOG.md                   # 自动区变更流水(供 maintain-index 读取 delta)
```

- **自动区**（工具产出，可被覆盖重写）：`ddl/`、以及每次生成会追加 `CHANGELOG.md`。
  人不手改这些文件的内容语义；要更新就重跑工具。
- **人工/半自动区**（人主导，LLM 辅助）：`sql/`、`usecases/`、`domain-notes/`、`testreport/`。

## 2. 文件头元数据（front-matter）

**人工/半自动区**的 `.md` / `.sql` 文件建议在文件头写元数据，供 `INDEX.md` 索引与 LLM 判断可信度：

Markdown（YAML front-matter）：

```markdown
---
domain: authorization        # 业务域
source: zentao#1234          # 来源(禅道用例号/XMind/口述整理)
date: 2026-08-15             # 导出/整理日期
version: 1.0.0               # 该知识的版本
confidence: high             # high | medium | low —— 人工核实过的高置信度经验标 high
---
# 授权查询用例整理
...
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
- `ddl/` 由工具产出，不要求 front-matter；其可信度来自 `CHANGELOG.md` 里的生成记录。

## 3. raw 与 curated 的边界

- **raw**（原始导入物，如禅道/XMind 直出 CSV/MD）：**不得改写语义**，只允许补充元数据头与放置到正确目录。
- **curated**（加工后的知识，如整理过的 `domain-notes`、清洗过的 `usecases`）：可编辑，但必须保留 `source` 指回 raw 来源，并 bump `version`。

## 4. 可追溯原则

- 每份知识都能回答"从哪来、何时、什么版本、多可信"（即上面 4+1 个字段）。
- 更新 curated 知识 → bump `version` 并在正文追加简短变更说明。
- 自动区更新 → 由工具写 `CHANGELOG.md`（见 `apps-authoring-syntax.md` 的 changelog 约定）。

## 5. 与其它层的关系

- 造数 action word 从 `assets/ddl/<datasource>/<table>.sql` 取列名（见 `create-action-word` skill）。
- 业务 SQL 服务在 `packages/<domain>/` 实现，同时镜像人类可读副本到 `assets/sql/`（见 `packages-db.mdc`）。
- 生成任何测试/资产前，先查根 `INDEX.md` 检索相关 domain 的知识作为依据（grounding）。
