# tuner-testkit 4.0.0 — 从仓内拷贝到 PyPI extras

3.x（冻结点 **`v3.0.0`**）把运行库放在各仓的 `packages/` / `apps/`，用 `init_repo scaffold` 整树拷贝。
4.x 发行 **`tuner-testkit`**（导入名 **`tuner_testkit`**），下游 `uv add` extras，DNA 用 **`tuner-dna sync`** 放进项目树。

## 下游迁移清单

1. **依赖**：`pyproject.toml` 增加 `tuner-testkit[db,api]==4.0.0`（Web UI 再加 `web-ui`；合录再加 `recorder`）。不要再拷 `db` / `page_test` / 公共 recorder 源码。
2. **导入**：`from packages.db import …` → `from tuner_testkit.db import …`（`page_test` / `api_test` / `logging` / `fake` / `excel` / `config` 同理）。业务资产仍在本仓 `packages/page_objects` 等。
3. **CLI**：`python -m apps.recorder` → `tuner-recorder` 或 `python -m tuner_testkit.apps.recorder`。
4. **环境变量**：`TUNER_ENV` / `TUNER_DB_<ALIAS>_*`（旧 `ARGON_*` 仍可读）。项目根可用 `TUNER_ROOT`。
5. **DNA**：`uv add tuner-testkit==4.0.0` 之后必须 `tuner-dna sync`，把 `.cursor/`、`docs/spec/`、`tools/git-hooks/` 更新进 git。Cursor 不会读 site-packages 里的 rule/skill。
6. **新建仓**：`tuner-init scaffold <dir>` 只铺骨架 + 依赖 + 一次 dna sync。

## extras

- `[web-ui]`：现有 Playwright `page_test`（不是 `[page]`）。
- `[phone-ui]`：预留空 extra，本版本无实现。
- 一个 wheel 不能「只升 web-ui、钉死旧 db」；手机栈若将来独立再拆第二个发行版。
