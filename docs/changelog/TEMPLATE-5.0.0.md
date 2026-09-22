# tuner-testkit 5.0.0 — Plane Job 协议退场，工具清单与 workspace catalog 中立化

MAJOR：删除面向企业 Runner 的 Plane Job / Sync 协议（D 阶段雏形），把其中 A/B 阶段真正需要的两块能力抽成中立模块。
路线图见 `dogfood/assets/domain-notes/platform/roadmap.md`（A 本地 workspace → B 本地工作台 → C 企业信息平台 → D 云端拉取）。

## 破坏性变更

| 5.0.0 之前 | 5.0.0 |
| --- | --- |
| `tuner_testkit.apps._shared.plane_app.@plane_app`（`apps/<name>/plane.py`） | `tuner_testkit.tools.tool`（`apps/<name>/tool.py`）；字段：`tool_id / name / summary / group / module / argv / destructive / timeout / runtime / visibility / readme_path` |
| `plane_runnable` / `whitelisted` / `expose` / `result="catalog_json"` | 删除；`visibility="workbench"|"local"` 表达「是否进目录」 |
| `@plane_db_seed` 等六个 opt-in 装饰器（`tuner_testkit.action_words.plane`） | 删除；`@register` 的词全部进目录（`destructive` 按类别推断） |
| `@plane_apiobject` / `@plane_pageobject`（`packages/*/plane.py`） | 删除；catalog 静态扫描 `method/path`、`page_id` |
| `tuner-index-platform`（`tuner_testkit.apps.index_platform`，catalog v2） | `tuner-workspace catalog`（`tuner_testkit.catalog`，catalog v3，落 `artifacts/catalogs/workspace.json`） |
| 发现器只扫 `apps/*/plane.py` | 同时扫 `apps/*/tool.py` 与 kit `tuner_testkit/apps/*/tool.py`（`mock_server` 现在进目录） |

## 新增

- `tuner_testkit.tools`：`@tool` / `discover` / `export_tools` / `get_tool` / `build_argv` / `validate_params`；
  argparse 内省补全 `integer/number` 类型、`default`、`help → description`、`choices → enum`。
- `tuner_testkit.catalog`：`build_catalog(root)` v3（tools / action_words / api_objects / page_objects / knowledge assets 含 front-matter / tests / docs / artifacts inbox·runs·reports / ai_components / git）；无 PyYAML 依赖的 front-matter 读写器。
- `tuner-workspace`（`tuner_testkit.workspace`）：`catalog`、`index render|check`（`<!-- auto:begin:<zone> -->` 围栏）。
- `dogfood/`：仓内 dogfood workspace（A0），见 `dogfood/README.md`。

## 下游迁移

1. 升 kit：`uv add "tuner-testkit[db,api]==5.0.0"` → `uv sync` → `tuner-dna sync --overwrite`（rules/spec 措辞已改）。
2. 删除 `packages/action_words/plane.py`、`packages/api_objects/plane.py`、`packages/page_objects/plane.py`；
   去掉源码里的 `from ... plane import ...` 与 `@plane_*` 装饰器（`@register` 保留即可）。
3. `apps/<name>/plane.py` 改名 `tool.py`：`@plane_app(app_id=..., module=..., expose=..., result=...)` →
   `@tool(tool_id=..., name=..., module="apps.<name>", group=..., destructive=..., timeout=...)`。
4. `tuner-index-platform --out -` → `tuner-workspace catalog --out -`；消费方按 v3 结构读取（`tools[]` 键名 `tool_id`）。
5. 可选：在 `INDEX.project.md` 加 `<!-- auto:begin:apps -->` 等围栏，`tuner-workspace index render` 接管自动区。

## 验证

`uv run pytest`；`uv run --directory dogfood tuner-workspace catalog --out -`；`uv run --directory dogfood tuner-workspace index check`；
`tuner-index-ai --check`；`python -m tuner_testkit.apps.init_repo manifest --check`。
