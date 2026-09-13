# evidence

把 Playwright MCP（或其它网络 dump）**脱敏后落盘**到 `artifacts/evidence/<run_id>/`，
并往 stdout 打一份 JSON（路由列表），方便 LLM 接着 freeze / derive-design。

## 需求背景

4.2.0 契约要求 capture **必须**落盘，但当时只活在 LLM 上下文里。Plane dogfood
证明：没有带时间戳的 `network.jsonl`，就无法把 API 与 DB 写入做时间窗关联。

## 试用场景

- explore-first 会话结束后，把 MCP `browser_network_request` 整理成 JSONL 再 persist。
- `routes` 子命令列出 method + normalized_path，交给 `freeze-api-objects`。
- **不做**：冻结 APIModel（那是 freeze-api-objects）；不启浏览器。

## 运行方式

无 extra（stdlib + 已有 `tuner_testkit.api_objects.recording` 脱敏器）。

```bash
uv run python -m tuner_testkit.apps.evidence persist \
  --run-id 20260913T134137Z-issue-slice \
  --scenario explore:workspace-project-issue \
  --network captures.jsonl \
  --intent "create throwaway work item"

uv run python -m tuner_testkit.apps.evidence routes --run-id 20260913T134137Z-issue-slice
# 或
tuner-evidence persist --run-id ... --scenario explore:x --network captures.jsonl
```

## 运行示例

输入 JSONL 每行一个对象，至少含 `method` + `url`（或 `request.path`/`host`），可选 body/headers/response。

产出：

- `artifacts/evidence/<run_id>/network.jsonl`（脱敏）
- `artifacts/evidence/<run_id>/run_summary.md`
- stdout JSON：`{run_id, dir, routes, count, sanitizer}`
