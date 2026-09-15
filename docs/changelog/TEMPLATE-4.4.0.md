# tuner-testkit 4.4.0 — SUT 自学习编排与任务 log

MINOR：新增编排 agent 与 inbox 约定，无运行时 API 断裂。下游 `tuner-dna sync` 即可拿到 DNA；kit 运行时与 4.3.0 兼容。

## 本版新增

- **`.cursor/agents/sut-self-learning.md`**：上半程编排（账号 → explore → evidence → freeze → design → index）
- **`artifacts/inbox/`** + `docs/spec/agent-task-log.md`：所有 agent 结束前写任务记录；自学习必须列出探索页面与本轮新增资产
- **`data/sut-accounts.example.yaml`**（scaffold）：本机副本 `data/sut-accounts.local.yaml`（gitignore）供 LLM 登录
- **`tuner-dna` wheel**：构建时始终从源树重打 `dna_payload`（旧 payload 不再短路），避免 4.4.0 工具域仍下发 4.3.0 DNA
- 规则 `agent-task-log` always-on；`explore-sut` 先读 local 账号文件

## 下游怎么用

1. 内循环：`uv tool install --from <platform-repo> --force` 后在业务仓 `tuner-dna sync`
2. 拷贝 `data/sut-accounts.example.yaml` → `data/sut-accounts.local.yaml` 填真实账号（勿提交）
3. 阶段收口才打 `v4.4.0` 发 PyPI；未发版前不要 `uv add ==4.4.0`
