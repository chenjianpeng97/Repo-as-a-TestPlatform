# apps 工具编写规范（apps-authoring-syntax）

> `apps/` 存放**可独立运行**的测试工具（公用：`dump_ddl`、`recorder`、`index_ai`、
> `init_repo`；项目特定：造数/核对等）。本规范把 `dump_ddl` / `recorder` 的隐性约定
> 显性化，供 `apps-authoring.mdc`（创建期）与 `apps-handover.mdc`（完成期）两条规则引用。

## 1. 目录与入口

单文件工具或包均可：

```text
apps/
├── dump_ddl.py                 # 单文件：python apps/dump_ddl.py <args>
├── recorder/                   # 包：python -m apps.recorder
│   ├── __init__.py __main__.py cli.py ...
│   └── README.md               # 交接文档
├── _shared/                    # 跨工具共享(如 changelog)，不是独立工具
└── <your_tool>/                # 新工具
    ├── __init__.py __main__.py # python -m apps.<your_tool>
    ├── cli.py                  # argparse 入口
    ├── README.md               # 交接文档(见第 4 节)
    └── tests/                  # 该工具的测试
```

- 包形式必须支持 `python -m apps.<name>`（提供 `__main__.py`）。
- 需要在仓库根外可运行时，脚本顶部把 `REPO_ROOT` 注入 `sys.path`（见 `apps/dump_ddl.py`）。

## 2. 必须复用 packages（不得重造轮子）

- **DB** → `packages.db.DbClient`（多数据源，`config/env.py` 的别名）。禁止 `pymysql/pymssql.connect`、
  硬编码 DSN、SQL 字符串拼接。见 `.cursor/rules/packages-db.mdc`。
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

## 6. 测试

- 纯逻辑（归一化、解析、代码生成）应可离线单测，放 `apps/<name>/tests/`（参考 `apps/recorder/tests`）。
- 依赖真实环境的部分用参数/开关隔离，便于 CI 只跑离线单测。
