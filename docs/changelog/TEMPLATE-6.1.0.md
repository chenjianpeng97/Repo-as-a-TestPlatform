# tuner-testkit 6.1.0 — scaffold 可以指定项目名

MINOR：新建业务仓的文件夹名和 `pyproject.toml` 项目名可以分开指定。已有仓不用改。

## 本版变更

- `tuner-init scaffold <目录>` 的目录最后一段就是生成的文件夹名
- `pyproject.toml` 的 `name` 默认由文件夹名规范化而来（`Balance` → `balance`）
- `--name <项目名>` 覆盖这个项目名，例如 `tuner-init scaffold ../clients/acme --name acme-billing`
- 新仓依赖从写死的 `tuner-testkit[db,api]>=4.3.0` 改为 `>=` 执行 scaffold 的 kit 版本

## 下游怎么用

1. tool 域：`uv tool upgrade tuner-testkit`（或 `uv tool install "tuner-testkit==6.1.0"`）
2. 新仓：`tuner-init scaffold ../balance`，然后在该目录 `uv sync`
3. 已有仓要升到本版：`uv add "tuner-testkit[db,api]==6.1.0"` → `uv sync` → `tuner-dna sync --overwrite`
