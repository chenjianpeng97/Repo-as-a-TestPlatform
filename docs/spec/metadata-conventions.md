---
name: metadata-conventions
version: 1.0.0
description: 统一 front-matter / run manifest 字段家族，供 catalog、工作台与未来企业平台解析「谁在何时创建了什么」。
---

# 元数据约定（metadata-conventions）

> C 阶段 0：企业平台**只解析 front-matter + manifest**，不读业务代码。
> 身份不要让 LLM 手填——用 `tuner-workspace meta stamp <path>` 写 `git config user.email`。

## 1. 通用字段

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `kind` | string | `app` / `action_word` / `testreport` / `inbox` / `question` / `task` / `testdesign` / `testcase` / `testcase-module` / `testcase-index` / `explore` / `design` / `usecase` / `domain-note` |
| `id` | string | 稳定标识（`tool_id` / `word_id` / 报告 slug） |
| `title` | string | 短标题 |
| `author` | email | 创建者，来自 `git config user.email` |
| `created` | date | 首次写入（ISO `YYYY-MM-DD`） |
| `updated` | date | 最近 stamp |
| `version` | string | 资产版本 |
| `tags` | list | 自由标签 |
| `sut` | string | 被测系统短名 |
| `env` | string | 命名环境（`dev` / `uat` / …） |

catalog 同时用 `git log --diff-filter=A --format=%ae -- <path>` 算首次提交者；
`author` 与之不一致时 `tuner-workspace catalog` 行上带 `author_mismatch: true`（不阻断）。

## 2. 按 kind 扩展

### `apps/<name>/README.md`（`kind: app`）

额外：`tool_id` / `summary` / `inputs` / `outputs`。

### action word

类属性 `author` / `owner`（可选）经 `describe()` 进 catalog；缺省用模块文件的 git 首次作者。
`Params` 每个字段必须有 `Field(description=...)`（表单 label）。

### 测试报告（`kind: testreport`）

落点：`assets/testreport/<sut>/<yyyy-mm>/<slug>.md`。

额外：`run_id` / `period` / `result`（`{total,passed,failed}`）/ `evidence[]` / `features[]`。
端到端执行报告再加 `task_id` / `design`（指向 `work/tasks` 与 `assets/testdesign`）。

正文固定章节：范围 / 环境 / 结果 / 缺陷 / 风险 / 证据链接。见 skill `generate-test-report`。

### inbox

沿用 `docs/spec/agent-task-log.md`，再加 `author`。

### 任务与测试设计

- `kind: task` 落在 `work/tasks/TASK-*.md`，字段见 `docs/spec/work-task.md`。
- `kind: question` 未回答落在 `artifacts/inbox/questions/Q-*.md`，回答后移到 `artifacts/inbox/archived-question/`（不入库）。
- `kind: testdesign` 落在 `assets/testdesign/<sut>/<slug>.md`，字段见 `docs/spec/test-design-syntax.md`。
- `kind: testcase` 落在 `assets/testcases/<模块>/<功能>.md`；模块说明是 `testcase-module`，总索引是 `testcase-index`。字段见 `docs/spec/testcase-syntax.md`。

### run manifest

`artifacts/runs|<reports>/<run_id>/manifest.json`：`producer.user_email` / `producer.host` /
`producer.tool_id`。见 `docs/spec/artifacts-layout.md`。

## 3. 谁来写

| 动作 | 命令 |
| --- | --- |
| 新建 app / 报告 / usecase | skill 落盘后立刻 `tuner-workspace meta stamp <path> --kind …` |
| 批量补作者 | 对缺 `author` 的 Markdown 再 stamp 一次（不覆盖已有 `created`） |
