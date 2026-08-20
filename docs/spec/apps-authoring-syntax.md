# apps 工具编写规范（apps-authoring-syntax）

> `apps/` 存放**可独立运行**的测试工具。分两类：
> **本地维护**（`dump_ddl`、`recorder`、`index_ai`、`init_repo`）——产物进 git，不上 Plane；
> **Plane Job 门面**（`index_platform`、`action_runner`）——`plane.py` + `@plane_app`。
> 供 `apps-authoring.mdc`（创建期）与 `apps-handover.mdc`（完成期）引用。

## 1. 目录与入口

单文件工具或包均可：

```text
apps/
├── dump_ddl.py                 # 本地维护：python apps/dump_ddl.py <args>
├── recorder/                   # 本地维护：python -m apps.recorder
├── action_runner/              # Plane 门面：plane.py + run.py
│   ├── plane.py                # import-safe；@plane_app / register_plane_app
│   ├── run.py                  # 惰性调用 packages.action_words
│   └── README.md
├── index_platform/             # Plane Sync 引导扫描（expose=False）
├── _shared/plane_app.py        # 注册器（不是独立工具）
└── <your_tool>/
    ├── __init__.py __main__.py
    ├── plane.py                # 仅当要在 Plane 跑时提供
    ├── cli.py
    ├── README.md
    └── tests/
```

- 包形式必须支持 `python -m apps.<name>`（提供 `__main__.py`）。
- 需要在仓库根外可运行时，脚本顶部把 `REPO_ROOT` 注入 `sys.path`（见 `apps/dump_ddl.py`）。

## 2. 必须复用 packages（不得重造轮子）

- **DB** → `packages.db.DbClient`（多数据源，`config/env.py` 的别名）。禁止 `pymysql` /
  `pymssql` / `psycopg.connect`、硬编码 DSN、SQL 字符串拼接。见 `.cursor/rules/packages-db.mdc`。
- **日志** → `packages.logging`（`log_info/log_warn/log_error/log_data_setup/...`）。禁止 `print`、
  stdlib `logging`、自建日志文件。见 `.cursor/rules/packages-logging.mdc`。
- **配置/凭据** → `config/env.py`（+ 环境变量覆盖），不在代码里写死。
- **HTTP/API** → 复用 `packages.api_test` / `packages.api_objects`；表格解析用 `packages.excel`。

## 3. 产出去向

- **原始知识回填** → `assets/`（如 DDL 落 `assets/ddl/<datasource>/`）。
- **可复用资源** → `packages/`（如抓包冻结为 `packages/api_objects/`）。
- **自动区变更留痕**：凡是覆盖式生成 `assets/**` 或 `packages/api_objects/**` 的工具，
  运行结束**必须**用 `apps._shared.changelog.append_entry(...)` 向对应区 `CHANGELOG.md`
  追加一行（tool / action / items / 关键字段），供 `maintain-index` 增量更新 `INDEX.md`。

## 4. 交接文档（完成期必产出）

每个工具在 `apps/<name>/README.md`（单文件工具写进 `apps/README.md` 的条目）记录：

- **需求背景**：当时为解决什么问题而造。
- **试用场景**：适用/不适用的场景，前置条件（如需要哪个数据源、是否需登录）。
- **运行方式**：完整命令（含依赖安装 extra，如 `uv sync --extra recorder`）。
- **运行示例**：一条可复制的命令 + 预期产出位置。

并在 `INDEX.md` 第 3 节登记该工具一行。

## 5. 安全与边界

- 不得写入 token / cookie / 密码 / Authorization / session 等敏感值（含产出文件与日志）。
- apps 是**独立运行**的工具，**不得被 `tests/` import**（测试复用逻辑应下沉到 `packages/`）。
- 破坏性操作（写生产库、删除文件）必须显式开关 + 默认 dry-run/只读。
- **Plane vs 本地**：只有要在 Plane 跑的工具才加 `plane.py` + `@plane_app`。
  回填 git 的工具（DDL/api_objects/REGISTRY/脚手架）不要注册。领域动作留在
  `packages/`；`apps.action_runner` 只做协议浅封装。发现器只加载 `plane.py`。

## 6. 测试

- 纯逻辑（归一化、解析、代码生成）应可离线单测，放 `apps/<name>/tests/`（参考 `apps/recorder/tests`）。
- 依赖真实环境的部分用参数/开关隔离，便于 CI 只跑离线单测。
