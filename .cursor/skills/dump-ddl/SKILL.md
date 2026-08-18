---
name: dump-ddl
version: 1.0.0
description: Dumps live table DDL into assets/ddl/<datasource>/ via apps/dump_ddl.py, then updates the knowledge index from CHANGELOG. Use when the user says /dump-ddl, dump DDL, 拉取 DDL, 导出表结构, or needs schema files before writing action words / SQL.
---

# Dump DDL — 把线上/本地库表结构回填到 assets/ddl

## Scope

- **目标**：按命名数据源把基表 DDL（+ 可选示例 INSERT）写到
  `assets/ddl/<datasource>/<table>.sql`，并留下 `assets/CHANGELOG.md` 供索引增量更新。
- **写范围**：`assets/ddl/<datasource>/**`、`assets/CHANGELOG.md`；有
  `INDEX.project.md` 时更新其 §1.1，否则更新 `INDEX.md` §1.1。
- **不写**：`config/env_local.py`（gitignore，永不提交）、token/密码、平台 DNA
  （`packages/db`、`apps/dump_ddl.py`）——缺方言支持要先改 `public-main` / `github/main`。
- **必须走**：`python apps/dump_ddl.py` → `packages.db.DbClient`。禁止直连驱动、
  手写 `pg_dump` / `mysqldump` 替代、把密钥写进仓库。

## Before running

1. 读 `config/env.py` + 若存在的 `config/env_overlay.py`，确认 `DATABASES` 别名与
   `type`（`mysql` / `sqlserver` / `postgres`）。**不要把 `env_local.py` 的密码回显到对话。**
2. 本机真实连接只存在于 `config/env_local.py` 或 `ARGON_DB_<ALIAS>_*`。文件不存在则
   先让用户从 `config/env_local.py.example` 复制并填值，**不要替用户把密钥提交进 git**。
3. 缺别名时：试验田/下游仓把无密钥的 `type`/host/库名写进 `env_overlay.py`；密钥仍只放
   `env_local.py`。
4. PostgreSQL（如 Plane 本地）：容器内 hostname 是 `plane-db`，**从宿主机 dump 必须用
   `127.0.0.1:5432`**。库名/用户默认与 Plane `.env` 的 `POSTGRES_DB` / `POSTGRES_USER`
   一致；schema 默认 `public`。
5. 产出目录是 `assets/ddl/<datasource>/`。换 SUT 时不要把旧系统的表文件混进同一别名目录
   （先清该别名目录再 `--all`，或换一个 datasource 别名）。

## Steps

```
Task Progress:
- [ ] 确认 datasource 别名与 type
- [ ] 运行 dump_ddl
- [ ] 核对 CHANGELOG 新行与产出路径
- [ ] 增量更新 INDEX.project.md 或 INDEX.md §1.1
```

1. **选定数据源**
   - 用户指定了别名 → 用那个 `--datasource`。
   - 未指定 → `main`。
   - 用户指定了表名 → 传表名；否则 `--all`（排除视图）。
   - PostgreSQL 需要非 `public` schema 时加 `--schema <name>`。
   - 只要结构、不要示例 INSERT → `--no-sample`。
     **有 password / token / session / cookie 列的库必须加 `--no-sample`**（本仓禁止把这些写进
     `assets/`）。Plane 本地库一律 `--no-sample`。

2. **执行**（仓库根目录）

   ```bash
   uv run python apps/dump_ddl.py --all --datasource main --no-sample
   ```

   指定表：

   ```bash
   uv run python apps/dump_ddl.py issues cycles --datasource main --no-sample
   ```

   PostgreSQL 显式 schema：

   ```bash
   uv run python apps/dump_ddl.py --all --datasource main --schema public --no-sample
   ```

3. **留痕**：工具会 `append_entry` 到 `assets/CHANGELOG.md`。不要手改 `assets/ddl/**`
   正文；要更新就重跑本工具。

4. **索引**：读 `assets/CHANGELOG.md` **尾部新行**（表数量、datasource、schema），按
   `maintain-index` skill 更新业务索引 §1.1。有 `INDEX.project.md` 就写那里，不要把
   SUT 表清单写进平台 `INDEX.md`。

## Hard rules

- DB 只经 `packages.db.DbClient`；本 skill 只**调用** `apps/dump_ddl.py`，不在对话里
  拼 DSN、不 `psql`/`mysql` 客户端替代。
- 日志走 `packages.logging`（工具已接好）。不要 `print` 连接串。
- 不得提交 `config/env_local.py`、`.env`、密码、token。
- 平台缺 PostgreSQL / 某方言：切到 `public-main`（跟踪 `github/main`）改
  `packages/db` + `apps/dump_ddl.py`，提交后再 `git merge` 进试验田。禁止把平台改动只留在
  `plane-dogfood`。
- 覆盖式 dump 会改写同名 `.sql`；换库前确认 alias 目录不会混入另一套 SUT。

## Verify

1. `uv run python apps/dump_ddl.py --help` 能看到 `--datasource` / `--all` / `--schema`。
2. 目标 `assets/ddl/<alias>/` 出现 `.sql`；文件头含 `-- auto-generated definition`。
3. `assets/CHANGELOG.md` 末行 `tool=dump_ddl` 且 `count=` 与文件数一致。
4. 对应索引 §1.1 已登记 datasource / 路径 / 表文件数（不要把每一张表名都抄进 INDEX）。

## Output checklist

- 使用的 `--datasource` / `--schema` / `--all` 或表名列表。
- 产出目录与表文件数（来自 CHANGELOG，不逐个读 `.sql` 正文）。
- 更新了哪份 INDEX。
- 是否误把 `env_local.py` 纳入暂存区（必须否）。
