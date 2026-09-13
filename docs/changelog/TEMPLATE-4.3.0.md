# tuner-testkit 4.3.0 — dogfood 回流（evidence CLI + path 插值）

Plane 下游仓 `tuner-test-platform-testrepo` 走完 workspace→project→issue 切片后的 MINOR。
无 API 客户端断裂：旧资产仍用具体 path；新 slug 占位走 `set_path`。

## 本版新增

- **`tuner-evidence`**：`persist` / `routes`，把 MCP 网络 dump 脱敏写入 `artifacts/evidence/<run_id>/`，stdout JSON
- **`APIModel.set_path`**：替换 `{workspace_slug}` / `{project_id}` 等文档占位
- **PageModel `url_path` 插值**：`open()` 的 Goto 会对 `{{param}}` 做 `set_inputs` 替换
- **scaffold**：写入 `.python-version`（3.12），`requires-python = ">=3.12,<3.14"`
- **named env**：`TEST_UI_BASE_URL` 进入 `apply_profile`（4.2.0 漏了，双 URL SUT 切环境会丢 UI host）
- Skills：`analyze-mcp-network`；agent：`sut-source-to-design`
- design schema **仍为 v0.1**；Plane 切片缺口记在 `design-knowledge-syntax.md` §6

## 下游怎么用

1. tool 域：`uv tool upgrade tuner-testkit`（或 `uv tool install tuner-testkit==4.3.0 --force`）
2. 业务仓：`uv add "tuner-testkit[all]==4.3.0"` → `uv sync` → `tuner-dna sync`
3. 探索会话结束：`tuner-evidence persist --run-id … --scenario explore:… --network captures.jsonl`
