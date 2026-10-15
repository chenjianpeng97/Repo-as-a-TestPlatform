# tuner-testkit 6.2.0 — 测试单，以及用例维护一次一个提交

MINOR：新增 `maintain-testsheet`。`maintain-testcases` 升到 1.5.0。用例文件格式不变。

## 本版变更

- skill `maintain-testsheet`：一轮测试单写在 `assets/testsheet/<轮次>/testsheet.md`。选中的就绪用例原样复制到同目录 `testcase/`，测试单只链这些副本
- skill `maintain-testcases`：同一次维护只做一个 git 提交。正文每个用例文件一段，新文件写「首次创建」，已有文件写「变更原因」，供 IDE Timeline 查看
- `tuner-init scaffold` 会创建空的 `assets/testsheet/`

## 下游怎么用

1. `uv add "tuner-testkit==6.2.0"` → `uv sync` → `tuner-dna sync --overwrite`
2. 生成测试单时让 agent 使用 skill `maintain-testsheet`
