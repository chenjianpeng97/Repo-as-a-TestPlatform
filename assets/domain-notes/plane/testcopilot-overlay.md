---
domain: testcopilot
source: C:\dev\repo\plane TESTCOPILOT.md + docs/testhub/PLAN.md + 已实现 UI（Formulation / 环境 / TestCopilot / 作业 / 配置）
date: 2026-08-18
version: 1.0.0
confidence: high
---

# TestCopilot overlay — 本 fork 已落地能力（dogfood 生成依据）

> 作者 **tuner** 在 Plane v1.4.1 上的自研层。对外产品名 **TestCopilot**。
> 测试能力的唯一真相源是绑定的 git 仓，不在 Plane 数据库、也不在工作项里。
> 本笔记只写 **当前 UI 已能看见的行为**；P3 跑测闭环、P4 recorder 等未完成能力标为暂缓。

## 两仓分工

| 仓 | 职责 |
| --- | --- |
| Plane fork | 配置绑定、按约定扫描展示、白名单作业、测程引用、失败以后才链到工作项 |
| 测试 / 规格 git 仓 | `.feature`、action words、api/page objects、DDL/SQL、`python -m apps.*` |

不要把说明书、连接密钥和跑测塞进同一个产品模块，也不要把用例正文双写进工作项。

## 项目侧栏成分（与工作项同级）

1. **Formulation** — 场景（`.feature`）、可执行 action words、API、Page objects、DDL（活文档）。
2. **环境** — SUT 连接与数据源模板（脱敏）。永不展示密码/token，永不读取本地密钥文件。
3. **TestCopilot** — 测程与报告、工具、常用 SQL、pytest 节点。
4. **作业** — 各页触发的白名单异步任务结果。
5. **配置** — 数据源登记 + 模块绑定 + 同步。

未绑定数据源时，对应产品页显示空状态引导，并提供「打开配置」入口，不报错崩溃。

## 配置（数据源 + 模块绑定）

- 可添加 **本地挂载** 数据源（本阶段主路径）；可填写名称、容器工作目录、可选宿主机路径。
- **Git URL** 类型可以保存，但克隆/fetch **尚未实现**；同步应提示本阶段请用本地挂载。
- 每个产品模块最多绑 **一条** 数据源：TestCopilot / Formulation / 环境（以及 Wiki / PRD 约定位）。
- 三条绑定可以指向同一条本地挂载（常见：测试平台仓同时满足三种约定）。
- 文件夹靠约定发现，不在配置页填写相对路径。
- 同步本地挂载时，若该源被 TestCopilot 使用，会入队白名单作业刷新目录。

## Formulation

- 绑定后按约定读取场景、action words、API objects、page objects、DDL。
- 场景页列出 Feature 名称、标签与 Scenario；可预览文件，可「在 TestCopilot 中引用」。
- Action words 可查看参数模型；真正执行需要 TestCopilot 也已绑定（执行发生在 TestCopilot 工作目录）。
- 破坏性 action word（写入被测系统）需要用户确认「我确认此操作会写入被测系统」。
- 不在 Formulation 里编辑 Gherkin，不回写 git。

## 环境

- 列出连接目标（种类 + 基址）与数据源别名/引擎/主机/库名。
- 密钥只展示 **键名**，值为脱敏后的变量；页上有「密码和 token 已脱敏」提示。

## TestCopilot

- 总览：绑定仓名称/分支/工作目录、HEAD、同步状态，以及测程 / Apps / 常用 SQL / pytest / 作业入口卡片。
- **测程**：引用 Formulation 场景（路径 + git sha），可选环境；创建后报告在关联运行之前保持为空（状态为待执行）。本阶段 **不会** 自动跑 behave。
- **工具**：展示 catalog 中已向 Plane 注册的 apps（`plane_runnable`）。本轮即
  `db_seed` / `db_assert` / `api_request` 等 action_runner 类别。`dump_ddl`、
  `index_ai`、`recorder` 是本地维护工具，不出现在可运行列表。
- **常用 SQL**：列出 `assets/sql` 索引，可筛选与预览，不是任意 SQL 控制台。
- **pytest**：只读展示收集到的节点，本阶段不在此页直接执行。

## 作业

- 需要 TestCopilot 数据源；未绑定则引导去配置。
- 无作业时显示空状态。
- 有作业时列出类型与状态；详情可见命令、退出码、标准输出/错误（日志中不得出现密钥）。
- 同一项目默认串行；已有排队/运行中作业时再触发应冲突失败（可观测错误，而不是并行再开一条）。

## 白名单（当前已实现的作业类型）

- 唯一硬编码 kind：`index_platform`（Sync，stdout catalog JSON）
- 其余 kind = catalog `tools[].app_id`（本轮：`db_seed` / `db_assert` / `api_request` / `api_assert` / `ui_action` / `ui_assert`），由测试仓 `@plane_app` 注册
- 破坏性以工具的 `destructive` 为准（造数 / API 请求 / UI 操作需确认）
- `dump_ddl` / `index_ai` / `recorder` / `init_repo` **不在** Plane Runner 白名单

## 明确暂缓（feature 里用 @skip 并写原因）

- Git URL 的 clone/fetch 同步。
- 测程关联 behave/pytest 运行并回填报告（P3）。
- 失败一键开工作项（P3）。
- recorder 常驻、任意 SQL 控制台（P4 / 明确不做）。
