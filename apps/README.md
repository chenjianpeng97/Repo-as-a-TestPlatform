# README

本目录只放 **本仓私有** 工具（`python -m apps.<name>`）。

公共 CLI 已迁入 PyPI 包 `tuner-testkit`（导入名 `tuner_testkit`）：

| 命令 | 等价模块 |
| --- | --- |
| `tuner-dump-ddl` | `python -m tuner_testkit.apps.dump_ddl` |
| `tuner-recorder` | `python -m tuner_testkit.apps.recorder` |
| `tuner-api-recorder` | `python -m tuner_testkit.apps.api_recorder` |
| `tuner-page-recorder` | `python -m tuner_testkit.apps.page_recorder` |
| `tuner-dna` | `python -m tuner_testkit.apps.dna` |
| `tuner-init` | `python -m tuner_testkit.apps.init_repo` |
| `tuner-mock-server` | `python -m tuner_testkit.apps.mock_server` |
| `tuner-index-ai` | `python -m tuner_testkit.apps.index_ai` |

交接文档在 `tuner_testkit/apps/<name>/README.md`。新建 **项目专用** 工具仍用 `create-app` skill，写在本目录。
