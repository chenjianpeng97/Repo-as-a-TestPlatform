# README

## 目录说明

- 此文件夹存放可独立运行的常用工具

## 已有工具简要功能与说明


- dump_ddl: 按命名数据源拉取表结构到 `assets/ddl/<别名>/<table>.sql`
  - 数据源：`config/env.py` → `DATABASES`（业务别名 → 连接配置，含 `type`: `mysql` / `sqlserver`）；默认别名 `main`
  - 输出按别名分子目录，例如 `assets/ddl/main/`、`assets/ddl/sqlserver/`，便于 MySQL / SQL Server 共存
  - 运行示例：
    - `python apps/dump_ddl.py some_table`（默认 `main`）
    - `python apps/dump_ddl.py --all`（当前数据源 schema 下全部基表）
    - `python apps/dump_ddl.py --all --datasource sqlserver`（指定别名）
    - `python apps/dump_ddl.py some_table --datasource sqlserver --no-sample`
- （已迁移）data_factory 造数工厂已重构为 `packages/action_words` 下的 db_seed 类 action words，
  独立运行入口见 `python -m packages.action_words --help`
- recorder/: 终端 HTTP(S) 代理抓包，按 api-objects-syntax 自动维护 packages/api_objects（跳过 .js/.css）
  - 运行：`python -m apps.recorder`（默认输出到仓库 `packages/api_objects`）
  - 自定义：`python -m apps.recorder --outputs_dir <path>`
  - 依赖：`pip install -e ".[recorder]"` 或 `uv sync --extra recorder`
  - 资产 `__main__` 可回放录制样本；鉴权统一见 `packages/api_objects/auth.py`
