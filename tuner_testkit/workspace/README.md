# workspace（`tuner-workspace`）

确定性的 workspace 操作 CLI：不连 SUT、不写 git、只读 repo，产物落 `artifacts/`。

## 需求背景

工作台、INDEX 自动区、企业平台同步都需要同一份「这个 workspace 里有什么」的机器可读描述。
5.0.0 之前它以 `tuner-index-platform`（Plane Sync catalog）存在，绑定企业 Runner 语义；现在中立化为
`tuner_testkit.catalog`（扫描）+ `tuner_testkit.tools`（`@tool` 清单），本 CLI 是它们的入口。

## 试用场景

- 适用：刷新 `artifacts/catalogs/workspace.json`；渲染 / 校验 `INDEX.project.md` 自动区；在命令行按清单运行工具或动作词；给 Markdown 写 `author/created/updated`。
- 不适用：维护 `.cursor/REGISTRY.md`（用 `tuner-index-ai`）；探索 SUT（用 Playwright MCP + `tuner-evidence`）。
- 前置：在 workspace 根（或 `--root`）运行；`run` 需要该工具的依赖已装进 `.venv`。

## 运行方式

```bash
uv run tuner-workspace catalog                       # → artifacts/catalogs/workspace.json
uv run tuner-workspace catalog --out -               # 打印到 stdout
uv run tuner-workspace index render                  # 渲染 INDEX.project.md（无则 INDEX.md）的 auto 围栏
uv run tuner-workspace index check                   # 自动区过期则 exit 1（进 CI）
uv run tuner-workspace run sample_tool --params '{"count": 2, "label": "demo"}'
uv run tuner-workspace run db_seed.sample_seed --params '{"count": 2}' --confirm
uv run tuner-workspace meta stamp apps/sample_tool/README.md --kind app
```

## 运行示例

```bash
uv run --directory dogfood tuner-workspace catalog --out -
```

预期：一行 JSON，`catalog_version: 3`，`tools[]` 含 `sample_tool`（origin=workspace）与 `mock_server`（origin=kit），
`action_words[]` 含 `db_seed.sample_seed`，`counts.features == 5`。

## catalog 结构（v3）

| 键 | 内容 |
| --- | --- |
| `git` | branch / sha / user_email / user_name |
| `counts` | tools / action_words / api_objects / page_objects / ddl_tables / assets / features / scenarios / docs / inbox / runs / reports / evidence_runs / ai_components |
| `tools[]` | `@tool` 清单：tool_id / name / group / origin / argv / params_schema / argv_plan / destructive / timeout / runtime / visibility / readme_path / author |
| `action_words[]` | `describe()` + destructive / argv / module |
| `api_objects[]` / `page_objects[]` | 静态扫描（method+path / page_id） |
| `knowledge` | ddl / sql_files / assets（front-matter：domain / source / confidence / author …） |
| `tests` | features（含 scenarios 与 tags）/ pytest_nodes |
| `artifacts` | inbox（状态统计 + 最近）/ runs / reports（`manifest.json` 摘要）/ evidence_runs |
| `ai_components` | `.cursor/` 下 rules / skills / agents / hooks 计数 |
