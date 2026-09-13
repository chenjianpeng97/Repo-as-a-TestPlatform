# tuner-testkit 4.2.0 — SUT 自学习契约（explore-first）

本版是 **DNA + 规范** 的 MINOR：把平台从「必须先有 `.feature`」纠偏为
**explore-first 自学习**，并统一运行产物路径。无数据库驱动 / HTTP 客户端 API 断裂。

## 本版新增

- Feature 规格：`docs/spec/sut-self-learning.md`
- Design 知识草案：`docs/spec/design-knowledge-syntax.md`（v0.1，待 Plane dogfood 收敛）
- Skills：`explore-sut`、`derive-design-knowledge`、`derive-feature-sets`
- Rule：`explore-safety`
- `assets/explore/`、`assets/design/` 目录约定；`tuner-init scaffold` 会铺这两类目录

## 纠偏

- `bdd-pipeline-gates` **3.0.0**：Gate 1 = 证据门禁（探索会话也算）；Gate 3 = 只跑实际存在的 stage
- `bdd-asset-pipeline` **2.0.0**：定位为自学习**下半程**
- MCP spec：capture **必须**落盘 `artifacts/evidence/<run_id>/`
- `AGENTS.md` **1.3.0**：分诊树增加「学习被测系统」；主干改为 `public-main`；退役分支式 `plane-dogfood`

## 下游怎么用

1. tool 域：`uv tool upgrade tuner-testkit`（或 `uv tool install tuner-testkit`）
2. 业务仓：`uv add "tuner-testkit[all]==4.2.0"`（或原来的 `[db,api]`）→ `uv sync` → `tuner-dna sync`
3. 新仓：`tuner-init scaffold ../my-sut-tests`

完整步骤见根 [`README.md`](../../README.md)。
