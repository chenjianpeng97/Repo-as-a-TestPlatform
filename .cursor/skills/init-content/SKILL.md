---
name: init-content
version: 1.0.0
description: Audits a scaffolded test workspace and writes the missing copilot basics (SUT identity, UI/API hosts, explore account, database, source roots, log channel) into the skeleton. Use when the user invokes init-content, says 开场配置 / 初始化内容 / 配置基础信息, or has just run tuner-init scaffold.
---

# init-content — 空骨架的开场配置

把测试仓补成可检索的 copilot 起点。人提供连接和位置，本 skill 只写缺的项。
表结构用 `dump-ddl` 导出；页面、接口、design、用例库不在这里编造。

## Scope

- **目标**：检查六项基础信息，向用户收集未配置项，写到下面的路径。
- **写范围**：`assets/domain-notes/<sut>/` 三份说明、`INDEX.project.md` 人工区、gitignore 的 `config/env_local.py` 与 `data/*.local.yaml`。用户确认后才跑 `dump-ddl`。
- **不写**：密码 / token / Cookie 进 `assets/`、`INDEX*`、任务、inbox、对话总结。不 `git add`、不提交。不新建 explore、design、api/page objects、feature。

## 在哪执行

1. 目标目录要有 `INDEX.project.md` 和 `config/env.py`。没有就停，让用户先 `tuner-init scaffold <dir>`。
2. 仓库根同时有 `tuner_testkit/apps/init_repo/scaffold.py` 和 `dogfood/` 时，这里是平台仓。先问目标目录（下游仓或 `dogfood/`）。用户指定前不要在平台根写业务配置。
3. 之后的路径都相对该目标目录。重复执行本 skill：已配置的值保持不动，只补缺项；用户点名要改的项才覆盖。

## 开场检查

先读盘，再向用户展示一张表（不要附带密码、token）。状态只用：`已配置` / `未配置` / `模板占位` / `连接已写，表结构未导出`。

| 项 | 落点 |
| --- | --- |
| 被测系统 | `assets/domain-notes/<sut>/profile.md` |
| 环境与地址 | `config/env_local.py` 的 `ENVIRONMENTS.<name>`：`TEST_UI_BASE_URL`、`TEST_BASE_URL` |
| 探索账号 | `data/sut-accounts.local.yaml` |
| 数据库 | 同一环境的 `DATABASES`（类型、host、库名、账号） |
| 表结构 | `assets/ddl/<别名>/*.sql` |
| 源码位置 | `assets/domain-notes/<sut>/source-roots.md` + 本机 `data/source-roots.local.yaml` |
| 后端日志 | `assets/domain-notes/<sut>/log-source.md` |

`<sut>` 取已有 `profile.md` 的父目录名。没有 profile 时此项为未配置，其余 domain-notes 路径等用户给出系统名后再定。多份 profile 时先问本次配置哪一个。

可选材料（有则记一笔，没有不算缺）：`assets/usecases/`、其它 `assets/domain-notes/`、`assets/sql/`。

检查时可以跑 `python -m tuner_testkit.config show`（只打印环境名、URL、库别名）。

## 已配置判定

字段非空，且不是占位符，才算已配置。占位符：`CHANGE_ME`、`replace-me`、`you@example.com`、`example-app`、`待填写`、`00000000-0000-0000-0000-000000000000`、空字符串。

- 密码仍是 `CHANGE_ME` 或 `replace-me` 时，同一文件里的示例地址（`127.0.0.1:8080`、`127.0.0.1:8081`、`localhost:3000`、`localhost:8000`）和库名 `example` / `example_uat` 一律算模板占位。
- 密码已换成真实值后，上述地址算已配置。
- 状态表里密码列只写「已填」或「仍是占位」，不写原值。

## 收集

按表只问未配置项，一次问完。用户可以跳过某一项。被测系统名不能跳过，否则没有 `<sut>` 目录。

收集顺序：

1. 系统显示名、目录用的短名 `<sut>`（小写字母、数字、连字符）、一句话范围、先学的一个模块。
2. 环境名（如 `dev`）、界面 host、接口 host。两边相同就写同一个。只要 host，不要路径。
3. 探索账号：`account_id`、用户名或邮箱、密码。多租户再要工作区 slug、项目标识。
4. 业务库：别名（默认 `main`）、`mysql` / `sqlserver` / `postgres`、host、端口、库名、用户、密码。PostgreSQL 不是 `public` 时另记 schema 名。
5. 源码：后端与前端的仓库地址、分支、仓内根（如 `apps/api`）。本机已经克隆时再要绝对路径。
6. 日志通道，四选一：`ssh-dir`、`log-api`、`rancher-api`、`skip`。
   - `ssh-dir`：目录；主机、用户、密码或密钥路径进 `LOG_SOURCE`。
   - `log-api`：接口 path；令牌进 `LOG_SOURCE`。
   - `rancher-api`：命名空间、工作负载；地址和令牌进 `LOG_SOURCE`。
   - `skip`：写明本轮不做日志。
7. 是否有现成用例、字段/权限说明、业务 SQL 要放进仓库。没有就结束此项。

## 落盘

下面的代码块只说明文件形状。host、账号、邮箱、路径、密码都用用户本次给的值；没给的键不要写，也不要留下 `...`。

### 可提交的说明

三份都用下面这种头（`date` 用当天 ISO 日期）。写完后对每个新文件执行：

```bash
uv run tuner-workspace meta stamp assets/domain-notes/<sut>/<file>.md --kind domain-note
```

`profile.md` 正文写显示名、范围、先学切片。非 `public` 的 schema 写在这里，供随后的 `dump-ddl --schema`。

`source-roots.md` 用表列出端、仓库、分支、仓内根。绝对路径不写进这份文件。

`log-source.md` 写 `channel` 与不含密钥的定位（目录、path、命名空间、工作负载）。密钥句只写「见 `config/env_local.py` 的 `LOG_SOURCE`」。

`INDEX.project.md` 人工区（`<!-- auto:` 围栏外）追加一条，指向这三份说明。原来只有 `_(暂无)_` 时换成这条。不要手改围栏内的表。

用户给了现成材料时：用例放 `assets/usecases/<sut>/`，字段或权限说明放 `assets/domain-notes/<sut>/`，SQL 放 `assets/sql/`。头里的 `source` 指向用户给出的原文件名。语义按原文写入，不改写。

### 只留本机

`config/env_local.py` 不存在就新建（骨架里通常没有 example）。已存在则只补缺的环境或字段，已填值不动。模板环境（仍含 `CHANGE_ME`）在用户给出真实值后整段替换，不要留着占位环境。

```python
# 本机密钥。gitignore。勿提交。
ACTIVE_ENV = "dev"

ENVIRONMENTS = {
    "dev": {
        "DATABASES": {
            "main": {
                "type": "mysql",
                "host": "127.0.0.1",
                "port": 3306,
                "user": "app",
                "password": "...",
                "database": "app",
            },
        },
        "TEST_BASE_URL": "http://127.0.0.1:8000",
        "TEST_UI_BASE_URL": "http://127.0.0.1:3000",
        "TEST_ACCOUNT": {"username": "qa", "password": "..."},
    },
}

# 仅在日志通道需要密钥时添加。channel 与目录/path/命名空间写在 log-source.md。
# LOG_SOURCE = {"host": "...", "user": "...", "password": "..."}
```

新别名才写 `config/env_overlay.py`（类型，无密码）。`main` / `sqlserver` / `postgres` 已在 `config/env.py`。业务库类型写在 `env_local` 该项的 `type`。

写好后切换激活环境（生产类名字会打印 warning，照用户的选择执行）：

```bash
python -m tuner_testkit.config use <name>
```

`data/sut-accounts.local.yaml`：

```yaml
sut: app
ui_base_url: http://127.0.0.1:3000
api_base_url: http://127.0.0.1:8000
accounts:
  - id: qa
    email: qa@example.com
    password: "..."
    notes: ""
```

用户没给工作区 / 项目标识就不写 `workspace` 和 `project`。

`data/source-roots.local.yaml` 只在用户给了本机绝对路径时创建：

```yaml
backend: C:/dev/repo/app/apps/api
frontend: C:/dev/repo/app/apps/web
```

只有一端就只写那一端。仓库地址已记、本机还没克隆：local 文件先不造路径，收口时告诉用户克隆后再跑一次本 skill。

## 表结构

数据库已配置，且 `assets/ddl/<别名>/` 下没有 `.sql` 时，问用户是否现在导出。同意后再读并遵循 `.cursor/skills/dump-ddl/SKILL.md`。用户点名表就只导那些表；`--all` 必须得到明确同意。schema 用 profile 里记下的名字。

## 收口

1. 能跑通时执行 `uv run tuner-workspace catalog` 和 `uv run tuner-workspace index render`，让 domain-notes 进入 `INDEX.project.md` 自动区。命令失败就在总结里写出失败原因，不要假装索引已更新。
2. 用同一张状态表回复：每项是已写入、本来就有，还是用户跳过。路径用仓库相对路径。总结里不出现密码、token、Cookie。
3. 不提交。提醒用户 `config/env_local.py`、`config/.active_env`、`data/*.local.yaml` 已在 gitignore。
4. 六项里地址和账号已齐时，下一步是 `explore-sut`。源码路径已齐时，读源码走 `sut-source-to-design`。

## Hard rules

- 用户没说的 URL、主机、仓库路径、表名，保持空白，不要用示例值充数。
- 对话里复述配置时，密码和令牌用「已写入本机文件」代替。
- 日志通道未写入 `log-source.md` 之前，不要选定 SSH、日志接口或 Rancher，也不要写取日志实现。
- 不把 `env_local.py` 或 `*.local.yaml` 放进暂存区。
