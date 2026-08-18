---
name: bdd-run-gherkin-in-playwrightMCP
user-invocable: false
description: Spec for running Gherkin scenarios via Playwright MCP, capturing network context, and freezing it into route-aligned API Objects safely (sanitize, dedupe, versioning).
---

# behave-run-gherkin-in-playwrightMCP

## 适用范围

- 本规范服务于 **behave/Gherkin → Playwright MCP → API Object freeze** 路径。
- 当用户**明确要求用 pytest** 且无需从 `.feature` 抓网沉淀时，**不要**强制走本 Run→Capture→Freeze 流程。

## 目标

- **目标**：让 AI 能通过 Playwright MCP 执行 `.feature` 场景，并将执行过程中的网络请求/响应上下文（Capture）结构化保留，进而稳定生成/更新 `packages/api_objects/` 资产。
- **第一期范围**：
  - 只做“可跑通 + 可抓取 + 可沉淀 API 资产”
  - **暂不做 DB 造数**（后续另立规范）

## 总体流程（Run → Capture → Freeze）

```text
feature/scenario
  ↓
Playwright MCP 运行（UI 操作 + 断言）
  ↓
Network Capture（请求/响应脱敏后结构化记录）
  ↓
Fingerprint 匹配已有 api_objects
  ↓
生成/更新 APIModel（只补稳定契约、稳定断言、稳定提取）
```

## Capture 规范（结构化输出）

> Capture 是“证据”，用于让 AI 可复盘、可去重、可审计。

### 1) Capture 最小字段

- `scenario_id`: string（如 `tests/features/xxx.feature::Scenario:yyy`）
- `run_id`: string（一次运行的唯一标识）
- `timestamp`: ISO string
- `request`:
  - `method`
  - `url`（完整 url，仅用于解析；落盘时会拆出 host/path/query）
  - `host`
  - `path`
  - `query`: dict（key/value；value 会脱敏）
  - `headers`: dict（已脱敏，且会过滤 forbidden keys）
  - `body`: object|string|null（已脱敏）
- `response`:
  - `status`
  - `headers`（脱敏）
  - `body_sample`（脱敏；允许截断）
- `timing`（可选）：耗时等

### 2) 脱敏（Sanitize）硬规则

#### 禁止落盘的 header key（大小写不敏感）

- `Authorization`
- `Cookie` / `Set-Cookie`
- `X-Token` / `*token*`
- `*secret*` / `*password*` / `*session*`

#### 值脱敏（适用于 query/body/response_sample）

- 长 token/疑似 JWT：只保留前后各 4-6 位，中间掩码
- 手机/邮箱/证件：按规则掩码（保留可定位的部分）
- 任何可能的私钥/签名：全部替换为 `***`

> 规则目的：即使 Capture 被误提交仓库，也不会泄露凭证。

## 从 Capture 冻结为 API Object（Freeze to Asset）

### 1) 归一化（Normalization）

从 Capture 计算：

- `method`
- `normalized_path`（动态段归一：数字/uuid 等）
- `query_keys`（只取 key）
- `body_keys`（只取 key；json body 才可取）
- `content_type`

### 2) 指纹（Fingerprint）

用于匹配已有资产：

- `fingerprint = method + normalized_path + sorted(query_keys) + sorted(body_keys)`

### 3) 匹配策略

- **命中**：更新既有 APIModel（v1 内兼容补全）
  - 补全 `query_schema/body_schema`（新增可选字段）
  - 补全稳定断言（如 `$.code == 200`、字段存在）
  - 增加稳定提取（仅当 steps/场景需要）
- **未命中**：创建新 APIModel（`v1`）

## APIModel 运行时调用约定（set/override/execute）

> 统一约定：steps 不使用 executor；而是通过 `APIModel.set_*` / `APIModel.override_*` 调整运行时参数后，用 `APIModel.execute()` 触发执行。

- 小改动：`model.set_query(...)` / `model.set_json(...)`（merge-set；允许补齐 schema 的可选字段）
- 大改动：`model.override_json(...)`（override-rebuild；整段替换）

### 4) 版本策略（何时 v2）

触发 v2 的典型信号：

- 同 fingerprint 的响应结构发生不兼容变化（关键字段缺失/改名）
- 必填参数发生变化导致既有 steps 不兼容

第一期建议：除非明确不兼容，不自动升 v2；只输出“建议升 v2”的评审意见。

## 冻结时的“禁止/必须”列表（约束 AI 的写入范围）

### 禁止

- 在 `packages/api_objects/` 中写入任何真实 token/cookie
- 把 host 写入 APIModel 的 `path/url`
- 把 Referer/User-Agent 这类噪声 header 当成契约固化
- 把场景常量断言写入 APIModel（例如某个 BU 名称）

### 必须

- 新建前必须做 fingerprint 匹配，避免重复资产
- APIModel 必须声明 `auth_policy` 与 `headers_policy`
- asserts/extracts 必须按“稳定/场景”分层

## 冲突与重复资产处理（第一期策略）

当发现重复 APIModel（同 method/path，但 query/body keys 不同）：

- **优先合并**到同一资产（v1）：
  - 将字段标记为可选
  - 用 description 记录差异来源（哪些场景用到哪些字段）
- 无法兼容时：
  - 输出“建议升 v2 / 拆分为 v2”的结论
  - 第一阶段不自动重构旧资产

## 建议的运行产物（便于调试与复盘）

> 第一阶段可以先不落盘，只要求输出结构化摘要；后续再落盘到 `raw/` 或 `testcase/`。

- `run_summary`（文本）：
  - 场景列表、通过/失败、失败分类（UI/接口/环境）
  - 捕获到的路由列表（method/path）
  - 本次生成/更新的 api_objects 列表
- `capture_bundle`（结构化）：
  - 每个路由 1 份脱敏 capture（或按场景聚合）

## 失败分类（用于后续 triage 自动化）

- **UI 失败**：元素不可见/定位不稳定/页面跳转异常
- **API 失败**：HTTP 非 2xx、业务码非 200、返回缺字段
- **环境失败**：域名不可达、证书/代理、登录态失效
- **脚本失败**：步骤定义缺失、参数绑定错误
