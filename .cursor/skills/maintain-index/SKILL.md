---
name: maintain-index
description: Updates the repo-level INDEX.md (knowledge/capability map) incrementally by reading changelog deltas, not full asset bodies. Use after new assets/tools/objects are added, or when INDEX.md drifts from reality.
version: 1.1.1
---

# Maintain INDEX.md（增量、省 token）

## Scope

- **目标**：保持根 `INDEX.md`（平台能力地图）与仓库真实状态一致；若存在 `INDEX.project.md`，同步保持业务资产地图一致。
- **规范**：`.cursor/rules/index-hygiene.mdc`、`docs/spec/assets-knowledge-syntax.md`。
- **写范围**：`INDEX.md`；若 `INDEX.project.md` 存在则也可改它。AI 组件区不手写（见下）。
- **分流**：平台工具 / 公共 `packages` / AI 组件链接 → `INDEX.md`。业务 DDL / SQL / 用例 / api_objects / page_objects / features → 有 `INDEX.project.md` 就写那里，不要把 SUT 明细填进 `INDEX.md`（避免 `main` 与试验田对打）。

## 核心原则：读 delta，不全量读

- **自动区**（`assets/ddl/`、`packages/api_objects/`、`packages/page_objects/` 等）：**只读各区 `CHANGELOG` 的尾部增量**
  （`assets/CHANGELOG.md`、`packages/api_objects/CHANGELOG.md`、
  `packages/page_objects/CHANGELOG.md`），据此补/改 `INDEX.md` 条目。
  **禁止**为维护索引而逐个打开 `assets/ddl/*.sql` 正文——那是 token 浪费。
- **人工/半自动区**（`usecases` / `domain-notes` / `sql`）：读新增文件的 **front-matter 元数据头**
  （domain/source/date/version/confidence）即可登记，不必读全文。

## 步骤

1. 读取各区 `CHANGELOG` 的**新条目**（自上次索引更新之后的行）；若不确定分界，读尾部若干行。
2. 对照对应索引的现有条目，做最小 diff（有 `INDEX.project.md` 时，第 1 / 2.1 / 2.2 / 业务 tests 小节写进它；第 3 节平台工具仍写 `INDEX.md`）：
   - DDL → 第 1.1 节（datasource / 表 / 更新时间）。
   - 业务 SQL → 第 1.2 节（文件 / domain / confidence）。
   - 用例/讲解/报告 → 第 1.3 节（读 front-matter 填 domain/source/confidence/用途）。
   - api_objects / page_objects → 第 2.1 / 2.2 节。
   - 新工具 → 第 3 节。
3. **不要**把 `.cursor/**` 组件手写进 `INDEX.md`：运行 `python -m tuner_testkit.apps.index_ai` 重新生成
   `.cursor/REGISTRY.md`，`INDEX.md` 第 5 节只保留链接。
4. 只更新变化的小节，保留其余原样。

## Verify

- `INDEX.md` 中每个新条目都能在仓库找到对应文件/CHANGELOG 行。
- 未新增全量读取 `.sql` 正文（自查：只依据 CHANGELOG / front-matter 更新）。

## Output checklist

- 更新了哪些小节、新增/修改了哪些条目。
- 读取了哪些 `CHANGELOG` 的 delta（来源证据）。
- 是否重跑了 `index_ai`（若 `.cursor/**` 有变化）。
