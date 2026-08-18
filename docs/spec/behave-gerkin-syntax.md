---
name: behave-gherkin-syntax
user-invocable: false
description: 使用 Python + behave 编写 Gherkin feature 的团队规范（中文），包含结构、标签、参数化、数据表达与可自动化性约束。
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# behave-gherkin-syntax

## 适用范围

- 本规范约束 **behave + Gherkin** 的 `.feature` 写法。
- 当用户**明确要求用 pytest** 实现（例如性能、数据库核对等非 BDD 场景）时，**不要**为了套用本规范而强行产出 `.feature`；按 pytest 实现即可（仍可复用 `packages/**`）。

## 目标

- **目标**：让非编码测试同学也能稳定编写 `.feature`，并能被 AI/自动化框架持续维护。
- **核心原则**：feature 只描述“业务行为与期望”，不泄露实现细节（selector、接口细节、SQL 等）。

## 文件与目录约定

- feature 文件放在 `tests/features/` 下，按业务域/模块分目录（推荐）。
- steps 分层目录（示例）：
  - `tests/features/ui_steps/`：UI 层步骤定义
  - `tests/features/api_steps/`：API 层步骤定义

## Feature 文件结构（behave）

### 基本结构

```gherkin
@smoke @web
Feature: 用户登录
  为了访问系统功能
  作为一个用户
  我希望可以登录

  Background:
    Given 打开登录页

  @critical
  Scenario: 正确账号密码登录成功
    When 我使用账号 "userA" 密码 "******" 登录
    Then 我应该看到首页
```

### 规范要求

- **Feature/Scenario 标题必须可读、可搜索**：尽量包含业务名词。
- **Background 只放稳定前置**：如“打开某页面/清理浏览器状态/进入模块首页”。不要在 Background 做大量数据创建。
- **Scenario 尽量短**：推荐 5~12 步；超过 12 步优先拆分或抽象复用步骤。

## Given / When / Then 语义规范

- **Given（前置）**：系统/用户所处状态，不表达操作细节。
- **When（动作）**：用户或系统触发的动作（点击、提交、调用业务动作）。
- **Then（结果）**：可验证的结果（页面提示、状态变化、数据呈现）。

### Then 的硬约束（强制）

- **Then/And(Then)** 只允许断言，不允许出现“点击/输入/请求接口”等动作。
- 所有断言应当是**可观测**的：UI 文字、状态标签、URL/页面元素可见性、接口返回关键字段等。

## 参数化与数据表达

### 1) 直接参数（字符串/数字）

```gherkin
Scenario: 搜索商品
  When 我在搜索框输入 "iPhone"
  And 我点击搜索
  Then 列表中应包含商品 "iPhone 15"
```

### 2) DataTable（推荐用于结构化输入）

```gherkin
Scenario: 创建用户
  When 我提交创建用户表单:
    | name | phone      | role  |
    | 张三 | 13800000000 | admin |
  Then 创建应成功
```

### 3) Scenario Outline（批量数据驱动）

```gherkin
Scenario Outline: 不同角色登录
  Given 打开登录页
  When 我使用账号 "<username>" 密码 "<password>" 登录
  Then 我应该看到 "<home>" 首页入口

  Examples:
    | username | password | home     |
    | admin    | ******   | 管理后台 |
    | user     | ******   | 工作台   |
```

## 标签（Tags）规范：可筛选、可治理

> 标签用于“分组执行、隔离环境差异、标记稳定性/风险”。

### 基础标签（建议最小集合）

- `@smoke`：冒烟（本地一键跑，必须稳定）
- `@regression`：回归集
- `@critical`：关键路径
- `@slow`：慢用例（默认不跑）
- `@flaky`：已知不稳定（必须附带原因与治理计划）
- `@skip`：暂不执行（必须写明原因）

### 环境标签（可选）

- `@env_test` / `@env_uat`：明确环境适配

## 可自动化性约束（防止写出“不能稳定自动化”的 feature）

### 禁止写法（示例）

- “点击左边第二个按钮”
- “等 5 秒”
- “看到差不多就行”
- “接口返回应该正常”（没有可验证字段）

### 推荐写法（示例）

- 用语义动作：`When 我提交登录表单`
- 用可验证结果：`Then 我应该看到提示 "登录成功"`
- 若需要等待，必须表达为**条件等待**：`Then 页面应出现 "提交成功"`（由实现层等待该条件成立）

## 与实现层（steps/page/api objects）的边界

### feature 禁止包含

- UI selector、xpath、css
- 具体接口 URL/headers/token
- SQL 语句与表名

### feature 允许表达

- 业务动作（登录、创建订单、审批）
- 业务字段（名称、金额、状态）
- 期望结果（提示、状态、列表展示）

## 最佳实践（含 Good/Bad 示例，便于培训与评审）

### 1) 用“声明式”步骤表达业务意图（不要写成脚本流水账）

**Good（声明式，推荐）**

```gherkin
Given 我已登录为管理员
When 我创建一个新商品
Then 商品应出现在商品列表中
```

**Bad（命令式/过于具体，不推荐）**

```gherkin
Given 我打开 "/login"
And 我在邮箱输入框输入 "admin@test.com"
And 我在密码输入框输入 "password123"
And 我点击登录按钮
And 我等待仪表盘加载完成
When 我点击 "商品" 菜单
And 我点击 "新增"
...
```

### 2) 场景命名要有业务含义（便于检索与复用）

**Good**

```gherkin
Scenario: 登录用户可以将商品加入收藏
Scenario: 游客结算前会被提示注册
Scenario: 过期优惠码会提示明确错误原因
```

**Bad**

```gherkin
Scenario: 测试1
Scenario: 检查收藏
Scenario: 错误测试
```

### 3) 场景必须可独立运行（不依赖上一个场景）

**Good（每个场景自建前置）**

```gherkin
Scenario: 编辑已有商品
  Given 存在商品 "测试商品"
  When 我将商品名称修改为 "更新后的商品"
  Then 列表中应出现 "更新后的商品"
```

**Bad（依赖前序场景状态）**

```gherkin
Scenario: 编辑商品
  # 假设上一个场景已经创建了商品
  When 我修改商品名称
  Then 商品应更新成功
```

### 4) Background 只放“真正通用”的前置（避免过于具体）

**Good（通用前置）**

```gherkin
Background:
  Given 我已登录
```

**Bad（too specific：把大量具体数据塞进 Background）**

```gherkin
Background:
  Given 我已登录
  And 我创建了商品 "Widget"
  And 商品有 5 条评价
  And 商品正在促销
```

### 5) 用 Tags 组织用例集（behave 运行方式）

```gherkin
@e2e @checkout
Feature: 结算流程

  @smoke @critical
  Scenario: 信用卡完成结算
    ...

  @regression
  Scenario: PayPal 结算
    ...

  @slow @integration
  Scenario: 库存同步下的结算
    ...
```

> behave 运行示例（供参考，具体以你们 runner 为准）：
>
> - 只跑冒烟：`behave -t @smoke`
> - 跳过慢用例：`behave -t ~@slow`
> - 组合：`behave -t @smoke -t @critical`

### 6) 避免步骤过多（建议 3~7 步，超过 12 步必须拆分）

**Good**

```gherkin
Scenario: 加入购物车
  Given 我正在查看某个商品
  When 我将商品加入购物车
  Then 购物车应显示 1 件商品
```

**Bad（步骤太多，属于“脚本流水账”）**

```gherkin
Scenario: 完成一次购买
  Given 我已登录
  And 我在首页
  And 我搜索 "laptop"
  And 我点击第一个搜索结果
  And 我选择颜色 "silver"
  And 我选择内存 "16GB"
  And 我点击加入购物车
  And 我打开购物车
  And 我点击结算
  And 我输入收货地址
  And 我选择配送方式
  And 我输入信用卡信息
  And 我确认订单
  Then 我应看到下单成功提示
  # 太长：应拆成“选购/下单/支付”多个场景，或抽成更高层语义步骤
```
