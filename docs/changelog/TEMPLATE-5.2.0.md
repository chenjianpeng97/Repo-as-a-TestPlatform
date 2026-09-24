# tuner-testkit 5.2.0 — 工作任务、测试设计、证据附件

MINOR：新增 `tuner-task` 与 `tuner-evidence attach`。已有 `persist` 调用不变。下游 `uv add tuner-testkit==5.2.0` 后 `tuner-dna sync` 拿到新 spec / skill / rule。

## 本版新增

- `work/tasks/` 与 `tuner-task create|start|ask|answer|finish|validate`
- 阻塞式提问 `artifacts/inbox/questions/`；日志来源主题 `sut-log-source`（SSH 目录 / 日志接口 / Rancher / 跳过）
- `docs/spec/test-design-syntax.md`、skill `derive-test-design` 与 `run-test-execution`
- evidence run 可附带截图、脱敏日志、接口 JSON，以及 `manifest.params.task_id`

## 下游怎么用

1. `uv add "tuner-testkit==5.2.0"` → `uv sync` → `tuner-dna sync --overwrite`
2. 发布任务：`tuner-task create --type test-design --title "…"`
