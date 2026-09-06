# tuner-testkit

发行名 **`tuner-testkit`**，导入名 **`tuner_testkit`**。给被测系统（SUT）测试仓提供公共运行库与 CLI（db / API / Web UI / 录制 / mock），以及 Cursor/git **DNA**（rules、skills、hooks）。

业务资产（page/api objects、action words、features）留在**各项目仓**的 `packages/` 与 `tests/`，不进本包。平台发新版本后，下游用 `uv` 按需升级，不必再整树拷贝运行库。

---

## 标准作业流程

### 1. 安装 `tuner-testkit`

还没有任何项目仓时，先把 CLI 装到工具环境：

```bash
uv tool install "tuner-testkit[db,api]"
```

需要 headed 录制或 Playwright 时加上对应 extra（见下方 extras）。已有项目仓则在该仓根目录：

```bash
uv add "tuner-testkit[db,api]>=4.0.0"
uv sync
```

入口命令是 `tuner-init`、`tuner-dna`、`tuner-recorder` 等（`tuner-*`），**没有** `tuner-testkit` 这个 script。

### 2. 初始化测试仓

```bash
tuner-init scaffold ../my-sut-tests
cd ../my-sut-tests
uv sync
```

`scaffold` 会铺六层目录、写入依赖 `tuner-testkit` 的 `pyproject.toml`，并执行一次 `tuner-dna sync`（把 `.cursor/`、`docs/spec/`、`tools/git-hooks/` 放进**项目树**）。可在任意目录运行，不必先有测试仓。不要用 `tuner-testkit init repo`。

Web UI / 合录按需再加 extra：

```bash
uv add "tuner-testkit[web-ui]"
uv add "tuner-testkit[recorder]"
```

### 3. 开始写业务

在**项目仓**里写，不要改 site-packages 里的 kit：

| 你写什么 | 放哪里 |
| --- | --- |
| 页面 / 接口资产 | `packages/page_objects/`、`packages/api_objects/` |
| 业务动作 | `packages/action_words/` |
| BDD / pytest | `tests/features/`、`tests/pytest/` |
| 知识（DDL、用例） | `assets/` |
| 本仓私有工具 | `apps/`（`python -m apps.<name>`） |

代码里 `from tuner_testkit.db import …` / `from tuner_testkit.page_test import …`。密钥只放本机 `config/env_local.py` 或环境变量（`TUNER_ENV`、`TUNER_DB_<ALIAS>_*`），**不要提交**。

录制产物同样写到项目仓 `packages/`，不会写进 venv。

### 4. 升级已发布的 kit

平台把新版本推上 PyPI 之后，在项目仓改依赖并同步 DNA——**两步都要做**：

```bash
# 改版本：直接改 pyproject.toml，或
uv add "tuner-testkit[db,api]==4.1.0"
uv sync

# Cursor 不会读 site-packages 里的 rule/skill，必须再铺进本仓并提交
tuner-dna sync
git add -A && git commit
```

只跑 `uv add` / `uv sync` 只会更新运行库与 CLI；AI 约束和 git hooks 仍停留在旧 DNA。检查是否与当前安装的 kit 一致：

```bash
tuner-dna check
```

一个 wheel 不能「只升 web-ui、钉死旧 db」。`[phone-ui]` 为预留空 extra，4.0 未实现。

---

## extras

| extra | 内容 |
| --- | --- |
| （默认 wheel） | `config` / `logging`、`tuner-init`、`tuner-dna`、`tuner-dump-ddl` 等 |
| `[db]` | MySQL / SQL Server / PostgreSQL |
| `[api]` | `api_test`（HTTP 客户端） |
| `[web-ui]` | `page_test` + Playwright |
| `[phone-ui]` | 预留，无实现 |
| `[recorder]` | 合录 / 仅 UI / mitmproxy 代理 |
| `[mock]` | 按冻结的 api_objects 回放 |
| `[excel]` / `[fake]` | 表格 / 假数据 |
| `[bdd]` / `[test]` / `[dev]` | behave / pytest / 开发全集 |

CLI 与 `python -m tuner_testkit.…` 等价，例如 `tuner-recorder`、`tuner-page-recorder`、`tuner-api-recorder`、`tuner-mock-server`。

---

## 安全

不得把 token、cookie、Authorization、密码、session 写入仓库（含 capture 与 api_objects）。凭证只允许运行时注入。

---

## 本仓库（平台源码）

克隆后在仓库根目录开发 kit 本身：

```powershell
uv venv
uv sync --extra dev
```

下游迁移清单见 [`docs/changelog/TEMPLATE-4.0.0.md`](docs/changelog/TEMPLATE-4.0.0.md)。平台能力地图见 [`INDEX.md`](INDEX.md)。
