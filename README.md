# tuner-testkit

发行名 **`tuner-testkit`**，导入名 **`tuner_testkit`**。给被测系统（SUT）测试仓提供公共运行库与 CLI（db / API / Web UI / 录制 / mock），以及 Cursor/git **DNA**（rules、skills、hooks）。

业务资产（page/api objects、action words、features）留在**各项目仓**的 `packages/` 与 `tests/`，不进本包。平台发新版本后，下游用 `uv` 按需升级，不必再整树拷贝运行库。

---

## 标准作业流程

### 1. 工具域：只装核心 kit（能 `tuner-init` 即可）

`uv tool install` 和业务仓 `.venv` 是两套环境。下游在 **tool 域只装默认 wheel**，用来拿 `tuner-init` / `tuner-dna`；**不要**在 tool 域打开 `[db]` / `[api]` 等 extra。

```bash
uv tool install tuner-testkit
```

入口命令是 `tuner-init`、`tuner-dna` 等（`tuner-*`），**没有** `tuner-testkit` 这个 script。`tuner-dump-ddl`、`tuner-recorder` 等依赖 extra 的 CLI，请在业务仓用 `uv run …` 跑，走该仓 `.venv`。

### 2. 初始化测试仓

```bash
tuner-init scaffold ../my-sut-tests
cd ../my-sut-tests
uv sync
```

`scaffold` 会铺六层目录、写入依赖 `tuner-testkit[db,api]` 的 `pyproject.toml`，并执行一次 `tuner-dna sync`（把 `.cursor/`、`docs/spec/`、`tools/git-hooks/` 放进**项目树**）。可在任意目录运行，不必先有测试仓。不要用 `tuner-testkit init repo`。

`uv sync` 把 **db / api 装进业务仓 `.venv`**，不是 tool 域。已有项目仓则在该仓根目录：

```bash
uv add "tuner-testkit[db,api]>=4.0.0"
uv sync
```

Web UI / 合录等按需再加 extra：

```bash
uv add "tuner-testkit[web-ui]"
uv add "tuner-testkit[recorder]"
```

测 kit 全能力（平台狗食仓等）一次打开全部能力 extra：

```bash
uv add "tuner-testkit[all]"
uv sync
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

### 4. 获取 PyPI 上的更新

平台发新版本后，下游从 [PyPI：tuner-testkit](https://pypi.org/project/tuner-testkit/) 取 wheel，**不要**再拷本仓源码。tool 域和业务仓 `.venv` 是两份安装，**两边都要升**，再铺 DNA。

**先看当前装的是哪一版、PyPI 最新是哪一版：**

```bash
uv tool list                          # tool 域里的 tuner-testkit
cd ../my-sut-tests
uv pip show tuner-testkit             # 业务仓 .venv
```

发行说明见 [`docs/changelog/FRAMEWORK.md`](docs/changelog/FRAMEWORK.md) 与该版本的 `docs/changelog/TEMPLATE-*.md`。

**① tool 域（只升核心 CLI）**

```bash
uv tool upgrade tuner-testkit
```

升的是 `tuner-init` / `tuner-dna` 所在环境。这里仍然**不要**加 `[db]` / `[api]`。尚未 `uv tool install` 过则先执行第 1 节。

**② 业务仓 `.venv`（升运行库 + extras）**

在**项目仓根目录**改依赖并同步 lock。保留你原来打开的 extra（普通仓 `[db,api]`，狗食/全能力仓 `[all]`）：

```bash
# 钉到某一发行版（推荐，和团队 lock 一致）
uv add "tuner-testkit[db,api]==4.1.0"

# 或只抬下限，让解析器选允许范围内的最新
# uv add "tuner-testkit[db,api]>=4.1.0"

uv sync
```

已经写过 `>=4.0.0`、只想把 lock 里的 kit 升到 PyPI 最新：

```bash
uv lock --upgrade-package tuner-testkit
uv sync
```

只改 `pyproject.toml` 里的版本再 `uv lock` / `uv sync` 也可以。一个 wheel 不能「只升 web-ui、钉死旧 db」。

**③ 同步 DNA 并提交**

`uv add` / `uv sync` 只更新 site-packages 里的运行库。Cursor 读的是项目树里的 `.cursor/`、`docs/spec/`、`tools/git-hooks/`，必须再铺一层：

```bash
tuner-dna sync
tuner-dna check
git add -A && git commit
```

`tuner-dna check` 核对项目树 DNA 是否与**当前 PATH 上那份** kit 一致。建议先 `uv tool upgrade`，再 `sync`，避免 CLI 还是旧包、`.venv` 已是新包。

新仓第一次仍用第 2 节的 `tuner-init scaffold`（会写依赖并做一次 `tuner-dna sync`），不是每次发版都重新 scaffold。

`[phone-ui]` 为预留空 extra，4.0 未实现。

---

## extras

| extra | 内容 |
| --- | --- |
| （默认 wheel） | `config` / `logging`、`tuner-init`、`tuner-dna`（tool 域只装这个） |
| `[db]` | MySQL / SQL Server / PostgreSQL（装在业务仓 `.venv`） |
| `[api]` | `api_test`（HTTP 客户端） |
| `[web-ui]` | `page_test` + Playwright |
| `[phone-ui]` | 预留，无实现 |
| `[recorder]` | 合录 / 仅 UI / mitmproxy 代理 |
| `[mock]` | 按冻结的 api_objects 回放 |
| `[excel]` / `[fake]` | 表格 / 假数据 |
| `[bdd]` / `[test]` | behave / pytest |
| `[all]` | 元 extra：上述能力 extra 的并集（不含 `[dev]`） |
| `[dev]` | `tuner-testkit[all]`，给本仓 editable 开发 |

CLI 与 `python -m tuner_testkit.…` 等价，例如 `tuner-recorder`、`tuner-page-recorder`、`tuner-api-recorder`、`tuner-mock-server`。依赖 extra 的命令在业务仓用 `uv run tuner-dump-ddl` / `uv run tuner-recorder`。

---

## 安全

不得把 token、cookie、Authorization、密码、session 写入仓库（含 capture 与 api_objects）。凭证只允许运行时注入。

---

## 本仓库（平台源码）

克隆后在仓库根目录开发 kit 本身：

```powershell
uv venv
uv sync --extra all
```

`uv sync --extra dev` 与 `--extra all` 等价（`dev` 只是引用 `[all]`）。

4.1.0 发行说明见 [`docs/changelog/TEMPLATE-4.1.0.md`](docs/changelog/TEMPLATE-4.1.0.md)；3.x → 4.x 迁移见 [`TEMPLATE-4.0.0.md`](docs/changelog/TEMPLATE-4.0.0.md)。平台能力地图见 [`INDEX.md`](INDEX.md)。
