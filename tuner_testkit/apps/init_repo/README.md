# init_repo

把 **SUT 测试仓骨架** 铺到新目录，并调用一次 `tuner-dna sync`。运行库不再整树拷贝：下游用 `uv add tuner-testkit[…]` 锁版本。

## 试用场景

- **新建项目仓**：`scaffold` 生成六层目录、薄 `packages/` 封装、`pyproject.toml` 依赖 `tuner-testkit`，并同步 Cursor/git DNA。
- **发布/漂移检测**：`manifest --check` 对照 DNA 文件哈希；配合 `release-template` skill。
- **升 DNA**：下游 `uv add tuner-testkit==x.y.z` 后执行 `tuner-dna sync`，再提交。两步缺一不可。

## 运行方式

```bash
python -m tuner_testkit.apps.init_repo scaffold ../my-new-project
# 或
tuner-init scaffold ../my-new-project

python -m tuner_testkit.apps.init_repo scaffold ../my-new-project --no-ai
python -m tuner_testkit.apps.init_repo manifest --write
python -m tuner_testkit.apps.init_repo manifest --check
```

无额外依赖（stdlib）。DNA 源：本仓 `.cursor/` / `docs/spec/` / `tools/git-hooks/`（editable）；wheel 内 `dna_payload/`（构建时 `tuner-dna bundle`）。

## 版本与漂移

- `release_manifest.json`：`template_version`（与 wheel `4.x` 对齐）+ DNA 文件 sha256。
- `tools/git-hooks/pre-push` 会在推送前跑 `manifest --check`，**仅警告不阻断**。
- 3.x = 仓内拷贝 `packages/` / `apps/` 运行库；4.x = `tuner-testkit` + `tuner-dna`。迁移说明见 `docs/changelog/TEMPLATE-4.0.0.md`。
