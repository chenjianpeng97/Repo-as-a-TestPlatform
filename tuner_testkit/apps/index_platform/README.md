# index_platform

Plane Sync 的引导扫描：把测试仓约定资产打成一份 JSON catalog（stdout），
**不写 git、不连 SUT**。TestCopilot 把 stdout 存进 ``CatalogSnapshot``。

## 需求背景

Plane API 容器禁止任意 subprocess / git。需要测试仓自己描述：有哪些
``@plane_app`` 工具、有哪些 **opt-in** 的 ``@plane_*`` action words / API /
Page、以及 feature / pytest / DDL 等索引。

## 试用场景

- **适用**：配置页 Sync；Plane 唯一硬编码 Job kind ``index_platform``。
- **不适用**：在本机维护 INDEX.md（用 ``maintain-index`` / ``apps.index_ai``）。
- 前置：在仓库根运行（或 Plane Runner workdir 即仓根）。

## 运行方式

```bash
python -m tuner_testkit.apps.index_platform --out -
```

``--out -`` 打印到 stdout（Plane 使用）。也可 ``--out report/catalog.json``。

## 运行示例

```bash
python -m tuner_testkit.apps.index_platform --out - | python -c "import json,sys; d=json.load(sys.stdin); print(sorted(t['app_id'] for t in d['tools']))"
```

预期 ``tools`` **不含** ``dump_ddl`` / ``recorder`` / ``db_seed`` 伪 app。
``components.action_words`` 仅带 ``@plane_db_seed`` 等标记的词条；未装饰的
``context.py`` / ``__main__.py`` 不会出现。
