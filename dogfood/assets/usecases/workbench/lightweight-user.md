---
domain: workbench
source: 工作台愿景评估与演进（plan 2026-09-22 §B）
date: 2026-09-22
version: 1.0.0
confidence: high
---

# 轻量用户使用工作台

## 角色

- **测开工程师**：在 workspace 里写 `apps/<name>/`（`tool.py` 暴露参数）或 `packages/action_words/db_seed/*.py`（pydantic `Params`），push 到团队仓。
- **低代码成员**：不写代码；`git pull` 后用本地工作台找到工具、填参数、运行、看产物。

## 主流程

1. `git pull` → `uv sync` → `uv run tuner-workbench`（或双击 `workbench.cmd`），浏览器打开 `http://127.0.0.1:<port>/`。
2. 首页看到工作区统计：工具 / 动作词 / 知识文件 / feature 数量、当前分支、最近的任务记录与运行。
3. 工具目录按分组列出 `apps/` 工具与动作词；可按关键字搜索；每条带名称、分组、参数结构、交接说明。
4. 打开工具详情：表单由 JSON Schema 渲染（枚举 → 下拉、布尔 → 开关、对象 → JSON 框）；破坏性工具需勾选确认，默认 dry-run。
5. 运行：页面流式显示日志与退出码；结束后给出 `artifacts/runs/<run_id>/` 的清单与产物链接。
6. 运行历史：按时间倒序回看，每条含工具、状态、开始时间、日志链接。
7. 知识浏览：只读渲染 INDEX / REGISTRY / `assets/**` front-matter / inbox。
8. 环境切换：只显示环境名（`dev` / `uat`），凭据来自本机 `config/env_local.py`，不进页面与日志。

## 验收（对应 `tests/features/workbench/*.feature`）

| feature | 场景要点 |
| --- | --- |
| `tool_catalog.feature` | 目录含 `sample_tool` 与 `db_seed.sample_seed`；搜索；详情表单与参数结构一致 |
| `run_tool.feature` | 表单参数运行成功并产出 manifest；破坏性未确认被拒；确认后 dry-run；缺必填参数被拒 |
| `run_history.feature` | 倒序历史；打开一次运行看日志与产物 |
| `knowledge_browse.feature` | 首页统计；知识元数据；环境切换不泄露凭据 |

## 边界

- 工作台只读 repo、只写 `artifacts/`、无数据库、只绑 127.0.0.1。
- 工具本身仍是 CLI：工作台只是 `python -m apps.<name>` / `tuner-action-words run` 的表单壳。

## 变更说明

- 1.0.0（2026-09-22）：首版。
