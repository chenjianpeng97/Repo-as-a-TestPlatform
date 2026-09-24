# tuner-testkit 5.3.0 — 功能用例集

MINOR：新增 `assets/testcases/` 的目录、四级标题和 `CASE` ID 规范。不改变 `tuner-task`、测试设计或 behave 路径。

## 本版新增

- `docs/spec/testcase-syntax.md`：`assets/testcases/<模块>/<功能>.md`，模块 README，总索引。用例 ID 为功能缩写加 4 位序号，如 `User-Login0001`
- skill `maintain-testcases` 与 rule `testcases`
- `python -m tuner_testkit.testcases` 检查标题层级、步骤/预期和 ID 唯一
- `tuner-init scaffold` 会创建空的 `assets/testcases/`

## 下游怎么用

1. `uv add "tuner-testkit==5.3.0"` → `uv sync` → `tuner-dna sync --overwrite`
2. 让 agent 使用 skill `maintain-testcases` 编写 `assets/testcases/<模块>/<功能>.md`
