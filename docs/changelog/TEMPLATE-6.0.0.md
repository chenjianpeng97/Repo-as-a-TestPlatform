# tuner-testkit 6.0.0 — 一条用例一个文件

MAJOR：功能用例集的目录约定变了。5.3.0 的「一个功能一个 Markdown、四级标题、`User-Login0001`」不再新发。

## 本版变更

- 一条用例一个文件：`assets/testcases/<模块>/<套件>/<用例ID>.md`
- 套件说明在 `<套件>/README.md`（`kind: testcase-suite`）
- 用例 ID 为 `<id_prefix>-<slug>`，例如 `User-Login-valid-credentials`
- 步骤对齐 TestLink：`## 步骤` 下 `### 1`，每步 `- 操作：` 与 `- 预期：`
- skill `maintain-testcases` 与 rule `testcases` 升到 1.3.0
- `python -m tuner_testkit.testcases` 按新目录校验

## 已有 5.3 用例的仓

把每个 `#### <前缀><序号>` 拆成独立文件，换成带 slug 的新 ID。旧序号留在当时的报告里，不回写。新 ID 的备注可写 `曾用：<旧 ID>`。

## 下游怎么用

1. `uv add "tuner-testkit==6.0.0"` → `uv sync` → `tuner-dna sync --overwrite`
2. 让 agent 使用 skill `maintain-testcases` 编写 `assets/testcases/<模块>/<套件>/<用例ID>.md`
