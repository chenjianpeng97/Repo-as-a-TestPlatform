# apps 工具编写规范（apps-authoring-syntax）

> `apps/` 存放 **SUT 私有**、可独立运行的测试工具（`python -m apps.<name>`）。
> **平台**工具在 `tuner_testkit.apps`（`tuner-recorder`、`tuner-dump-ddl` 等），不要再拷进下游 `apps/`。
> 领域动作（造数 / API / UI）留在 `packages/`（action words 经 `@register` 自动进入目录与工作台），不经 apps 冒充。
> 供 `apps-authoring.mdc`（创建期）与 `apps-handover.mdc`（完成期）引用。

## 1. 目录与入口

单文件工具或包均可：

```text
apps/                            # 仅 SUT 私有工具
├── __init__.py
└── <your_tool>/
    ├── __init__.py __main__.py
    ├── cli.py                   # argparse build_parser() + main()
    ├── tool.py                  # import-safe @tool 清单（工作台 / catalog 读取）
    ├── README.md                # 交接文档（front-matter 见 metadata-conventions）
    └── tests/

# 平台工具（已安装的 tuner-testkit，不要写进本仓 apps/）
# tuner_testkit/apps/dump_ddl.py
# tuner_testkit/apps/recorder/
# tuner_testkit/apps/dna/
```

- 包形式必须支持 `python -m apps.<name>`（提供 `__main__.py`）。仓库根须有
  `apps/__init__.py`。平台 CLI 走 `python -m tuner_testkit.apps.<name>` / `tuner-*`。
- 需要在仓库根外可运行时，用 `tuner_testkit.project.project_root()`（禁止 kit `__file__` 当 SUT 根）。

## 2. 必须复用 kit 运行库（不得重造轮子）

- **DB** → `tuner_testkit.db.DbClient`（多数据源，`config/env.py` 的别名）。禁止 `pymysql` /
  `pymssql` / `psycopg.connect`、硬编码 DSN、SQL 字符串拼接。见 `.cursor/rules/packages-db.mdc`。
- **日志** → `tuner_testkit.logging`（`log_info/log_warn/log_error/log_data_setup/...`）。禁止 `print`、
  stdlib `logging`、自建日志文件。见 `.cursor/rules/packages-logging.mdc`。
- **配置/凭据** → `config/env.py`（`tuner_testkit.config` 解析 `env_local` 命名环境；
  再叠加 `TUNER_DB_*` / `TEST_*` 环境变量），不在代码里写死。
- **HTTP/API** → 复用 `tuner_testkit.api_test` / `packages.api_objects`；表格解析用 `tuner_testkit.excel`。

## 3. 产出去向

- **原始知识回填** → `assets/`（如 DDL 落 `assets/ddl/<datasource>/`）。
- **可复用资源** → `packages/`（如抓包冻结为 `packages/api_objects/`）。
- **自动区变更留痕**：凡是覆盖式生成 `assets/**`、`packages/api_objects/**` 或
  `packages/page_objects/**` 的工具，运行结束**必须**用
  `tuner_testkit.apps._shared.changelog.append_entry(...)` 向对应区 `CHANGELOG.md`
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
- **工作台可见 vs 本地维护**：要出现在 `tuner-workspace catalog` / 工作台的工具，提供 import-safe 的
  `apps/<name>/tool.py`，用 `tuner_testkit.tools.tool` 装饰 `build_parser`（argparse → `params_schema` + `argv_plan`）。
  纯本地维护、产物直接进 git 的工具可以不写 `tool.py`，或写了但声明 `visibility="local"`。
  `tool.py` 及其 import 的模块**不得**在顶层 import DB 驱动 / 浏览器 / 代理。领域动作留在 `packages/`
  （action words 经 `@register` 自动进目录）。

## 6. 测试

- 纯逻辑（归一化、解析、代码生成）应可离线单测：可放 `packages/**/tests` 或 `apps/<name>/tests/`
  （参考 `packages/tests/test_api_objects_recording_*.py`、`tuner_testkit/apps/api_recorder/tests`）。
- 依赖真实环境的部分用参数/开关隔离，便于 CI 只跑离线单测。

## 7. `--json` 输出契约（工作台 / runner）

工作台与 `tuner-workspace run` 会把 stdout 里**最后一行 JSON 对象**当作 envelope 写入
`artifacts/runs/<run_id>/envelope.json`。约定：

```json
{
  "status": "succeeded",
  "outputs": [{"kind": "lines", "count": 2}],
  "artifacts": ["artifacts/runs/<run_id>/out.txt"],
  "log_path": null
}
```

- `status`：`succeeded` / `failed`（须与进程退出码一致：0 ↔ succeeded）。
- `outputs[]`：给人看的摘要，自由结构。
- `artifacts[]`：本次写出的文件路径（相对 workspace 根或绝对路径）。
- `log_path`：若工具自己另写了日志文件则填，否则 `null`（kit 仍会写 `stdout.log`）。
- 破坏性工具默认 dry-run；真正执行必须有显式开关。
- `create-app` 脚手架默认带 `--json` 与 `tool.py`。

