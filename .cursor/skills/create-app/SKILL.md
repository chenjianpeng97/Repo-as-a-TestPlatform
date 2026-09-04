---
name: create-app
description: Scaffolds a new standalone SUT-private tool under apps/ that reuses tuner_testkit plus this repo's packages business assets, following apps-authoring-syntax.md. Use when the engineer needs an on-demand test tool (data generator, checker, exporter, capture/enrichment). Do not scaffold into tuner_testkit/apps/.
version: 1.1.0
---

# Create App — 按需开发一个独立工具

## Scope

- **目标**：把「利用 tuner_testkit + 本仓 packages/assets 按需开发一个可独立运行的 **SUT 私有**工具」落成规范资产。
- **写范围**：`apps/<name>/**`（+ 必要时 `apps/README.md`、`INDEX.md` 登记）。**不要**往 `tuner_testkit/apps/` 脚手架。
- **必须遵循**：`docs/spec/apps-authoring-syntax.md`、`.cursor/rules/apps-authoring.mdc`
  （创建期）、`.cursor/rules/apps-handover.mdc`（完成期）。

## Before creating（复用优先）

1. 看 `INDEX.md` 工具层与 `tuner_testkit.apps` 是否已有同类平台工具（`dump_ddl`、`recorder` 合录、
   `api_recorder`、`page_recorder`、`dna`、`index_ai`、`init_repo`）。能扩展 kit 就别在 SUT `apps/` 再建一份。
2. 本仓 `apps/` 是否已有同类 **项目私有** 工具。能扩展就别新建。
3. 明确工具的**输入/输出去向**：原始知识 → `assets/`；可复用资源 → `packages/`。
4. 明确要复用哪些 kit 能力：DB(`tuner_testkit.db`)、日志(`tuner_testkit.logging`)、
   配置(`config/env.py`)、HTTP(`tuner_testkit.api_test`)、表格(`tuner_testkit.excel`)。

## 脚手架结构（包形式）

```text
apps/<name>/
├── __init__.py
├── __main__.py        # from .cli import main; raise SystemExit(main())
├── cli.py             # argparse 入口，调用核心逻辑
├── <core>.py          # 纯逻辑，尽量可离线单测
├── README.md          # 交接文档(见下)
└── tests/             # 离线单测
```

单文件工具（如仅一个脚本）可直接 `apps/<name>.py`，但交接文档仍需写进 `apps/README.md`。

## Hard rules（强制）

- 支持 `python -m apps.<name>`（SUT 私有工具）；参数用 `argparse`。不要做成 `python -m tuner_testkit.apps.<name>`。
- DB 只走 `tuner_testkit.db.DbClient`；日志只走 `tuner_testkit.logging`；凭据只从 `config/env.py`
  + 环境变量取；**禁止** `print`、直连驱动、硬编码 DSN、SQL 拼接、自建日志文件。
- 覆盖式生成 `assets/**` / `packages/api_objects/**` / `packages/page_objects/**` 的工具，运行结束必须
  `tuner_testkit.apps._shared.changelog.append_entry(...)` 追加对应区 `CHANGELOG.md`。
- 不得被 `tests/` import；不得写入 token/cookie/密码等敏感值；破坏性操作默认 dry-run/只读。

## 交接文档（完成期必产出）

`apps/<name>/README.md` 写清：**需求背景 / 试用场景与前置条件 / 运行方式(含依赖 extra) /
运行示例(可复制命令 + 预期产出)**；并在 `INDEX.md` 第 3 节登记一行。

## Verify

1. `python -m apps.<name> --help` 正常输出用法。
2. 离线单测 `uv run pytest apps/<name>/tests -q`（若有）。
3. 有环境时跑一条示例命令，确认产出位置与 `CHANGELOG` 追加正确。

## Output checklist

- 新建/更新的文件清单（含入口与交接文档）。
- 复用了哪些 tuner_testkit 模块 / 本仓 packages / assets（reuse 证据）。
- 产出去向与 changelog 是否接入。
- `INDEX.md` 是否登记。
