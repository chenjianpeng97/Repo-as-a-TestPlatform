---
name: behave-step-definitions
user-invocable: false
description: Python + behave 的 Step Definitions 团队规范（中文），强调分层、复用、参数化、上下文管理与禁止内联实现细节。
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# behave-step-definitions

## 适用范围

- 本规范约束 **behave** 的 step definitions（`tests/features/{ui,api}_steps/`）。
- 当用户**明确要求用 pytest** 实现时，**不要**强制编写 behave steps；用 pytest 测试直接调用 `packages/**`（及既有 page/api objects，如适用）。

## 目标

- **目标**：让 steps 可长期维护，避免“脚本堆”；并为 AI 自动补全/复用 steps 提供明确边界。
- **硬原则**：steps 只编排业务动作与断言，具体实现必须委托给：
  - `packages/page_objects/`（UI 行为与定位）
  - `packages/api_objects/`（接口资产与执行）
  - `packages/`（通用能力：配置、报告、上下文、断言工具）

## 分层目录（建议）

- `tests/features/ui_steps/`：UI 交互相关 steps（调用 `packages/page_objects/` 或 action words）
- `tests/features/api_steps/`：API 相关 steps（优先调用 `packages/action_words/`，或直接编排 `packages/api_objects/`）

## 命名与组织

- 一个 `.py` 文件聚焦一个业务域/页面/模块（不要把全站 steps 混在一起）。
- step 函数名应体现意图：`step_login_with_username_password`
- 优先复用既有 steps；当语义高度重合时，**禁止**新增同义 steps。
- 应在`tests/features/ui_steps/`和`tests/features/api_steps/`目录下区分`given.py`,`when.py`,`then.py`三个文件，分别用于编写`given`、`when`、`then`的steps。

## 参数化规范

### 1) 字符串参数

```python
from behave import when

@when('我使用账号 "{username}" 密码 "{password}" 登录')
def step_login(context, username: str, password: str):
    context.pages.login.login(username=username, password=password)
```

### 2) DataTable 参数

```python
from behave import when

@when("我提交创建用户表单:")
def step_submit_create_user(context):
    data = context.table[0].as_dict()  # {'name': '张三', 'phone': '138...', ...}
    context.pages.user_create.submit_form(**data)
```

### 3) 多种写法兼容（建议谨慎）

同一业务动作尽量只保留一种表达方式，避免 AI/人写出多套同义句式。

## 上下文（context）使用规范

### context 的角色

- `context` 用于保存跨步骤共享的信息：token、临时变量、上一步提取的 id 等。

### 建议的命名空间

- `context.vars`：业务变量（如 `order_id`、`product_id`）
- `context.api`：最近一次 API 响应/请求摘要（可选）
- `context.pages`：页面对象容器（统一入口）

### 禁止

- 在 `context` 顶层随意塞大量 key（导致污染与冲突）
- 保存敏感信息明文（token/cookie）到可被日志输出的位置

## UI steps 的硬约束（必须遵守）

- steps 内 **禁止出现 selector/css/xpath**；只能调用 page object 的方法。
- 等待必须是“等待条件”，不能 `sleep(5)`。

示例（正确）：

```python
from behave import given, when, then

@given("打开登录页")
def step_open_login(context):
    context.pages.login.open()

@when('我使用账号 "{username}" 密码 "{password}" 登录')
def step_do_login(context, username, password):
    context.pages.login.login(username=username, password=password)

@then("我应该看到首页")
def step_assert_home(context):
    context.pages.home.assert_visible()
```

## API steps 的硬约束（必须遵守）

- steps 内 **禁止直接拼 request**（url/headers/token/body）。
- 必须通过 `packages/api_objects/` 的 `APIModel` 调用（参见 `api-objects-syntax.md`）。

示例（正确）：

```python
from behave import when, then
from packages.api_objects.argon.mainData.getCategoryTree.GET_v1 import get_category_tree_v1

@when('我查询可授权产品，分类名为 "{category_name}"')
def step_call_get_category_tree(context, category_name):
    resp = (
        get_category_tree_v1
        .set_query({"categoryName": category_name})
        .execute(auth={"bearer_token": context.vars["token"]})
    )
    context.api = {"last_response": resp}

@then("查询应成功")
def step_assert_api_ok(context):
    assert context.api["last_response"].ok is True
```

## 断言规范（Then）

- 断言应尽量集中在 page/api object 的 `assert_*` 方法，steps 做最薄的一层编排。
- 一个 Then 只断言一个核心结果；复杂断言拆分为多个 Then。

## AI 生成/更新 steps 的约束（写入边界）

- AI 允许新增/修改：
  - `tests/features/ui_steps/`
  - `tests/features/api_steps/`
- AI 禁止修改：
  - `packages/` 的公共基建（除非进入明确的“重构任务”）
- AI 新增 step 前必须先搜索是否已有可复用 step；若存在，优先复用并说明原因。

## 最佳实践（steps 编写与治理）

### 1) Step 句子要“稳定可复用”，避免同义不同写法

- **推荐**：优先选少量固定句式，覆盖 80% 场景；通过参数化扩展
- **不推荐**：为同一动作写多条近义步骤，导致维护与匹配冲突

**Good（统一句式 + 参数化）**

```python
from behave import when

@when('我创建商品 "{name}" 价格为 {price:g}')
def step_create_product(context, name: str, price: float):
    context.pages.product.create(name=name, price=price)
```

**Bad（同义泛滥）**

```python
@when('我新增一个商品叫 "{name}"')
def step_add_product_1(context, name): ...

@when('我创建一个新商品 "{name}"')
def step_add_product_2(context, name): ...
```

### 2) 使用 `step_matcher` / 类型解析（可选但强烈建议）
> 目的是减少手动转换、提升可读性与稳定性。

推荐在 steps 模块入口设置：

```python
from behave import use_step_matcher

use_step_matcher("parse")  # 支持 {var}、{num:d}、{price:g} 等
```

常用类型（示意）：
- `{count:d}`：整数
- `{price:g}`：浮点数

### 3) hooks 与 fixture（建议放在 `tests/features/environment.py`）
> 把“启动浏览器/登录/清理上下文/截图/trace”等放进 hooks，避免散落在 steps。

建议最小 hooks：
- `before_all`：初始化配置、报告器
- `before_scenario`：初始化 `context.vars/context.pages/context.api_client`（或 model 内置 client），清理残留状态
- `after_scenario`：失败自动截图/保存关键日志（注意脱敏）

### 4) UI/API 分层必须贯彻到代码结构
- UI steps：只调用 `packages/page_objects/` 的 action/assert
- API steps：只调用 `packages/api_objects/` 的 APIModel（链式 set/override 后 `execute()`）
- 公共能力：放 `packages/`，steps 不重复造轮子

### 5) 错误信息要“可定位”
- 断言失败信息必须包含：**期望值**、**实际值**、**业务上下文（关键变量）**
- API 断言不要直接打印完整响应（可能有敏感字段）；优先打印 jsonpath 对应片段（脱敏后）
