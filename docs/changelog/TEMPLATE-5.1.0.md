# tuner-testkit 5.1.0 — A 收口、本地工作台、元数据约定

MINOR：无运行时 API 断裂。下游 `uv add tuner-testkit==5.1.0` 后 `tuner-dna sync` 拿新 skill / spec。

## 本版新增

- `tuner-workspace run` / `meta stamp`
- `tuner-workbench`（`[workbench]` extra，只绑 127.0.0.1）
- `docs/spec/metadata-conventions.md`、`generate-test-report` skill、apps `--json` envelope
- scaffold 带 `workbench.cmd` / `workbench.sh`

## 下游怎么用

1. `uv add "tuner-testkit[db,api]==5.1.0"`（工作台再加 `[workbench]`）→ `uv sync` → `tuner-dna sync --overwrite`
2. 轻量用户：`git pull` → `uv sync` → `uv run tuner-workbench`
