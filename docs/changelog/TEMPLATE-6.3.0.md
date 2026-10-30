# tuner-testkit 6.3.0 — 测试单出 GJB438B 测试报告

MINOR：新增工具 `tuner-testreport`、extra `[report]`、skill `generate-testsheet-report`。`maintain-testsheet` 升到 1.1.0，缺陷表从四列改为七列；旧测试单用 `tuner-testreport stats --check` 能查出要迁移的地方。另含 skill `init-content`。

## 本版变更

- 工具 `tuner-testreport`（`tuner_testkit/apps/testreport`）：
  - `stats --check`：核对测试单的「共 N 条」与五个计数、缺陷表取值、本轮信息
  - `draft`：按画像 `assets/domain-notes/testreport/<sut>.md` 起草 `assets/testreport/<sut>/<yyyy-mm>/<slug>.md`，要人补的地方写 TODO
  - `render`：套 kit 自带的 GJB438B 模板出 docx 到 `artifacts/runs/`，再检查残留模板标签和第 6 章用例行数（需要 `[report]`）
  - `build-template`：把版式不同的样例报告转成自己的模板，`render --template` 使用
- skill `generate-testsheet-report` 1.1.0：从测试单到报告的完整流程。缺的信息一次问全，并向用户解释编制单位、保障机构等字段；画像里有意留空的表格写一行「/」；列出 `draft --force` 会覆盖的手工整理；渲染自检通过才算完成；收尾登记任务和索引；用例库、测试单、报告分开提交
- skill `maintain-testsheet` 1.1.0：本轮信息加「版本」；缺陷表改为 `编号 | 用例 | 现象 | 严重程度 | 类型 | 状态 | 是否阻塞后续`；计数改由 `tuner-testreport stats --check` 核对，不手算
- skill `init-content` 1.0.0：scaffold 之后补齐 SUT 身份、URL、探索账号、数据库、源码根、日志通道。`sut-self-learning` 1.0.1、`sut-source-to-design` 1.0.2 先读这些文件，没有再问
- `tuner-init scaffold` 生成的 `pyproject.toml` 带 `report = ["tuner-testkit[report]"]`
- git hooks：`secret_scan.py` 和 `validate_commit_msg.py` 改用 `git diff --cached --name-only -z` 读暂存文件。修复前，git 默认 `core.quotepath=true` 时中文路径会被转义，密钥扫描跳过这些文件、scope 校验也认不出它们；中文 Windows 上 commit-msg 校验还会因 GBK 解码失败而报错
- `AGENTS.md` 1.7.4：测试单分诊加上出报告的入口

## 下游怎么用

1. `uv add "tuner-testkit==6.3.0"` → `uv sync` → `tuner-dna sync --overwrite`
2. 要出 docx：`pyproject.toml` 加 `report = ["tuner-testkit[report]"]`（新 scaffold 已带），再 `uv sync --inexact --extra report`
3. 已有测试单先跑 `uv run tuner-testreport stats assets/testsheet/<轮次> --check`，按输出把缺陷表迁到七列
4. 仓里已有私有 `apps/testreport` 的，可以删掉改用 `tuner-testreport`；画像与报告 Markdown 格式不变
