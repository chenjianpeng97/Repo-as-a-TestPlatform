# README

## 目录说明

- 此文件夹存放可独立运行的常用工具。
- **本地维护（不上 Plane）**：`dump_ddl`、`recorder`（合录）、`api_recorder`（代理）、`page_recorder`、`index_ai`、`init_repo` —— 产物进 git。
- **Plane Job**：`index_platform`（Sync 扫描）。造数 / API / UI 用 packages 上的 `@plane_*`，不要再做成 apps。
  BDD/pytest 请引用 packages，不要 import apps。

## 已有工具简要功能与说明


- dump_ddl: 按命名数据源拉取表结构到 `assets/ddl/<别名>/<table>.sql`
  - 数据源：`config/env.py` → `DATABASES`（业务别名 → 连接配置，含 `type`: `mysql` / `sqlserver` / `postgres`）；默认别名 `main`
  - 输出按别名分子目录，例如 `assets/ddl/main/`、`assets/ddl/sqlserver/`、`assets/ddl/postgres/`
  - PostgreSQL 默认 schema 为 `public`（`--schema` 可改）；从 Docker 宿主机连接 Plane 用 `127.0.0.1:5432`，不要用容器名 `plane-db`
  - 运行示例：
    - `python apps/dump_ddl.py some_table`（默认 `main`）
    - `python apps/dump_ddl.py --all`（当前数据源 schema 下全部基表）
    - `python apps/dump_ddl.py --all --datasource sqlserver`（指定别名）
    - `python apps/dump_ddl.py --all --datasource postgres --schema public`
    - `python apps/dump_ddl.py some_table --datasource sqlserver --no-sample`
  - 默认在每个 `.sql` 末尾追加**注释掉的最新一行 INSERT**（造数参考）。工具会剔除
    `password` / `token` / `session_*` 等密钥列，过长行改为省略说明。只要结构时加 `--no-sample`
- （已迁移）data_factory 造数工厂已重构为 `packages/action_words` 下的 db_seed 类 action words，
  独立运行入口见 `python -m packages.action_words --help`
- index_platform: Plane Sync 引导扫描，`python -m apps.index_platform --out -`（不写 git）。交接：`apps/index_platform/README.md`
- recorder/: headed 合录，同一浏览器会话默认同时冻 PageModel + APIModel（`--page-only` / `--api-only`）
  - 运行：`python -m apps.recorder --app <app> --url /sign-in`
  - 依赖：`uv sync --extra bdd` 后 `uv run playwright install chromium`
  - 交接：`apps/recorder/README.md`。旧 mitmproxy 入口已迁到 `apps.api_recorder`（收到 `--port` 会报错提示）
- api_recorder/: 终端 HTTP(S) 代理抓包，只冻 packages/api_objects（不含 UI 元素表）
  - 运行：`python -m apps.api_recorder`（默认输出到仓库 `packages/api_objects`）
  - 自定义：`python -m apps.api_recorder --outputs_dir <path>`
  - 依赖：`pip install -e ".[recorder]"` 或 `uv sync --extra recorder`（extra 名仍为 recorder）
  - 资产 `__main__` 可回放录制样本；鉴权统一见 `packages/api_objects/auth.py`
- page_recorder/: headed 浏览器手点冻结 PageModel 到 packages/page_objects（仅 UI；合录请用 recorder）
  - 运行：`python -m apps.page_recorder --app <app> --flow login --url /sign-in`
  - 依赖：`uv sync --extra bdd` 后 `uv run playwright install chromium`
  - 交接：`apps/page_recorder/README.md`；回放见 `packages.page_objects.session`
