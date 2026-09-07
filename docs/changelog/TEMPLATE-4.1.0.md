# tuner-testkit 4.1.0 — 元 extra `[all]` 与双域安装

4.0.x 已把运行库发到 PyPI extras。本版只增加**依赖解析**能力与下游安装约定，**无**运行库 API 变更。

## 本版新增

- **`[all]`**：元 extra，并集 `db,api,web-ui,phone-ui,excel,fake,mock,recorder,test,bdd`（不含 `[dev]`，避免循环）。
- **`[dev]`**：改为 `tuner-testkit[all]`（本仓 editable 开发别名，与 `--extra all` 等价）。

## 下游怎么用

1. **tool 域**（只要 CLI）：`uv tool install tuner-testkit`，不要加 extra。用 `tuner-init` / `tuner-dna`。
2. **普通业务仓 `.venv`**：`uv add "tuner-testkit[db,api]>=4.1.0"`（`scaffold` 仍写 `[db,api]`）。
3. **全能力 / 平台狗食仓**：`uv add "tuner-testkit[all]>=4.1.0"`。
4. **升已有仓**：`uv add "tuner-testkit[db,api]==4.1.0"`（或 `[all]`）→ `uv sync` → `tuner-dna sync` → 提交。tool 域另跑 `uv tool upgrade tuner-testkit`。

依赖 extra 的 CLI（`tuner-dump-ddl`、`tuner-recorder`）在业务仓用 `uv run …`。

完整步骤见根 [`README.md`](../../README.md) 第 4 节。从 3.x 迁 4.x 仍看 [`TEMPLATE-4.0.0.md`](TEMPLATE-4.0.0.md)。
