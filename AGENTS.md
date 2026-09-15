<!-- version: 1.4.0 -->
# AGENTS — 平台总入口（轻量 DM）

> 本文件是"repo as a platform"的**稳定世界观**：只写不常变的分层结构与角色。
> 「当前仓库有哪些具体知识与能力」这类会频繁变化的信息**不在这里**，去读
> [`INDEX.md`](INDEX.md)（平台能力地图）与 [`.cursor/REGISTRY.md`](.cursor/REGISTRY.md)（AI 组件注册表）。
> 若存在 `INDEX.project.md`（下游项目仓的业务资产地图），生成业务测试前一并阅读。
>
> 「自动学习被测系统并完成验收自动化」是 epic 下的旗舰 feature，规格见
> [`docs/spec/sut-self-learning.md`](docs/spec/sut-self-learning.md)，不是本文件的替代总纲。

## 1. 六层分层结构（职责边界）

| 层 | 目录 | 职责 | 谁运行 |
| --- | --- | --- | --- |
| 知识层 | `assets/` | 给人和 LLM 阅读、生成测试代码的基础知识（ddl / sql / usecases / domain-notes / explore / design / testreport）。见 `docs/spec/assets-knowledge-syntax.md`。 | 只读引用 |
| 运行库 | `tuner_testkit/`（PyPI：`tuner-testkit`） | 公共运行时与 CLI（db / logging / api_test / page_test / fake / recorders / dna）。SUT 用 `uv` 锁版本。 | `import tuner_testkit`；`tuner-recorder` 等 scripts |
| 组件层 | `packages/` | **本仓业务资产**（api_objects / page_objects / action_words），不是 kit 运行库。 | 被 import |
| 工具层 | `apps/` | **本仓私有**工具。公共工具在 `tuner_testkit.apps`。见 `docs/spec/apps-authoring-syntax.md`。 | `python -m apps.<name>`（仅项目工具） |
| 数据层 | `data/` | 供测试代码读取的结构化测试数据。 | 被读取 |
| 测试层 | `tests/` | 自动化测试代码（behave `features/` + `pytest/`）。 | behave / pytest |
| 文档层 | `docs/` | 仓库使用说明与规范（`docs/spec/**`）。 | 只读 |

配套：`config/`（环境/数据源）、`.cursor/`（AI 组件，见下）、`artifacts/`·`logs/`（运行产出；MCP evidence 落 `artifacts/evidence/<run_id>/`；agent 任务记录落 `artifacts/inbox/`）。SUT 登录本机文件：`data/sut-accounts.local.yaml`（gitignore）。

## 2. 三角色

- **测试工程师**：向 `assets/` 沉淀高置信度的手工经验（SQL / 测试报告 / 业务讲解）；向 `apps/` 用 packages + assets 交给 LLM 按需开发工具。
- **LLM**：读取 `assets/`、`INDEX.md`（及存在时的 `INDEX.project.md`）作为**生成依据**（防幻觉），协助工程师产出测试与工具；维护对应索引与各类资产。
- **MCP**（如 Playwright MCP）：读取被测系统页面/网络，供 LLM 探索 SUT、生成 `packages/page_objects`、冻结 `packages/api_objects`。

## 3. AI 组件即"平台后端服务"

`.cursor/**` 下的 rule / skill / agent / hook 相当于传统测试平台后端 service 里的**业务规则与处理逻辑**，需被版本化并对人类可读。

- **想知道当前有哪些规则/技能/编排/钩子、各是什么版本** → 读 [`.cursor/REGISTRY.md`](.cursor/REGISTRY.md)（由 `python -m tuner_testkit.apps.index_ai` 确定性生成）。
- **组件类型判断口诀**：能确定性脚本化就用 **hook/app**，别用 LLM；是约束就用 **rule**；是流程就用 **skill**；要串流程就用 **agent**。

## 4. 任务分诊（中立决策树，无 always-on 强制流程）

拿到任务先判断类型，再选路。**没有任何一条工作流是默认强制的**——BDD 只是能力之一。

```mermaid
flowchart TD
  Start[任务到达] --> Q{任务类型?}
  Q -->|"学习被测系统 / 探索式测试"| Learn["SUT 自学习编排\n.cursor/agents/sut-self-learning.md"]
  Q -->|"业务 UI/API 流自动化"| BDD["BDD 资产流水线（下半程）\n.cursor/agents/bdd-asset-pipeline.md"]
  Q -->|"明确要求 pytest / 性能 / DB 核对"| Pytest["pytest 路径\n复用 tuner_testkit + packages，不产出 .feature"]
  Q -->|"需要一个新的独立工具"| App["create-app skill\napps-authoring / apps-handover 规则"]
  Q -->|"缺少知识(ddl/api/用例)"| Know["先跑 kit CLI 回填 assets\n再走生成"]
  Q -->|"新建/更新项目仓"| Init["tuner-init / tuner-dna / release-template"]
  Q -->|"读/策展/索引知识"| Idx["查 INDEX.md + maintain-index skill"]
```

- **学习被测系统** → `.cursor/agents/sut-self-learning.md`（编排 explore → freeze → design；规格 `docs/spec/sut-self-learning.md`；任务 log 见 `docs/spec/agent-task-log.md`）。
- **业务 UI/API 流** → `.cursor/agents/bdd-asset-pipeline.md`（自学习的**下半程**；内部含三门禁，仅在此分支生效）。
- **明确 pytest** → 直接写 pytest，复用 `tuner_testkit` 与本仓 `packages/**` 业务资产，不要为满足分层而硬造 Gherkin。
- **造工具** → `create-app` skill；工具做好按 `apps-handover.mdc` 补交接文档。证据通道（日志/DB 日志取数）也落 `apps/`，遵守 CLI + JSON 输出约定。
- **补知识** → 用 `tuner-dump-ddl`、Playwright MCP 探索（落盘 `artifacts/evidence/`）、`tuner-recorder` / `tuner-api-recorder` / `tuner-page-recorder` 等回填，再进入生成。
- **仓库初始化/发布** → `tuner-init scaffold`（骨架 + 依赖 `tuner-testkit` + 一次 `tuner-dna sync`）+ `release-template` skill。下游升 kit：`uv add tuner-testkit==x.y.z` 然后 `tuner-dna sync`，再提交。
- **读/索引知识** → 先查 `INDEX.md`；若存在 `INDEX.project.md` 则一并查。索引维护用 `maintain-index` skill。

## 5. 全程硬约束（跨分支）

- 不得将 token / cookie / Authorization / 密码 / session 等敏感信息写入仓库（含 capture 与 api_objects）。
- 提交遵循 Conventional Commits + 六层 scope，见 `docs/spec/commit-convention.md`（`commit-msg` hook 会校验）。
- DB 只走 `tuner_testkit.db`，日志只走 `tuner_testkit.logging`（见对应 rule）。
- 密钥只放本机 `config/env_local.py`、`data/**/*.local.yaml` 或环境变量，**任何分支都不得提交**。多套 prd/uat/dev 写在 `env_local.ENVIRONMENTS` 里，用 `python -m tuner_testkit.config use <name>` 切换（或 `TUNER_ENV`）。探索账号优先 `data/sut-accounts.local.yaml`（模板 `data/sut-accounts.example.yaml`）。

## 6. 分支与下游仓

本公开仓只维护**平台**：`tuner_testkit/`、`.cursor/**`、`docs/spec/**`、`INDEX.md`。

| 分支 | 职责 | 谁改 |
| --- | --- | --- |
| `public-main` | 平台主干。框架改动只在这里提交，经 tag 发 PyPI（`tuner-testkit`）+ DNA。 | 平台 |

- **下游 SUT 测试仓**用 `tuner-init scaffold` 从空白目录新建，用 `uv add tuner-testkit==x.y.z` + `tuner-dna sync` 取平台能力。业务资产（`assets/`、objects、features、`INDEX.project.md`）只活在下游仓。
- 试用中发现框架要改：在 `public-main` 改并提交（内循环可用 `uv tool install --from <this-repo>`）；阶段收口打 tag 发 PyPI，下游再升级。
- 历史分支 `plane-dogfood` **退役**：分支式 dogfood 验不了 `tuner-init` + PyPI 全链。Plane 的业务测试仓是外部仓（如 `tuner-test-platform-testrepo`）。
