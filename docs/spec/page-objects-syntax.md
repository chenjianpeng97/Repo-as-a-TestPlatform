---
name: python-playwright-page-objects
user-invocable: false
description: Python + Playwright 的 Page Object 规范（中文），用于被 behave steps 调用；强调 locator 策略、动作/断言分离、稳定性与 AI 可维护边界。
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# python-playwright-page-objects

## 目标

- **目标**：将 UI 定位与交互封装在 `packages/page_objects/`，让 steps 只表达业务意图，提升可维护性。
- **关键边界**：steps 禁止直接写 selector；selector 只能出现在 page object 内部。

## 目录与模块组织（建议）

- `packages/page_objects/`
  - `pages/`：页面级对象（如 login、home）
  - `components/`：可复用组件对象（如 table、modal、date_picker）
  - `__init__.py`：可选，统一导出入口

## 设计原则（必须遵守）

- **单一职责**：一个对象只描述一个页面或一个组件。
- **封装**：对外只暴露“业务动作”和“业务断言”，隐藏 locator/等待细节。
- **稳定性优先**：优先选择稳定 locator（见下文优先级）。
- **可审计**：当 locator 不稳定时，必须在实现中体现“风险等级与替代建议”（可通过命名/结构体现，避免在 steps 泄露细节）。

## Locator 策略（优先级与禁用项）

### 推荐优先级（从高到低）

1. **语义定位**：`get_by_role` / `get_by_label` / `get_by_text`（可结合过滤）
2. **测试标识**：`get_by_test_id`（若研发支持，最稳定）
3. **结构化 CSS**：仅当语义定位不可用
4. **XPath**：最后手段（第一期建议禁用，除非明确豁免）

### 禁止（默认）

- 绝对 XPath
- 依赖 DOM 层级的超长 selector
- `nth(0)` 这类基于索引的定位（除非列表无稳定标识且已豁免）

## 动作与断言分离

### 对外暴露的方法类型

- **动作（actions）**：`login()`、`open()`、`search()`、`submit()`…
- **断言（assertions）**：`assert_visible()`、`assert_error_message()`…

> 断言方法内部负责等待条件成立（避免 steps 写 sleep）。

## Python + Playwright Page Object 示例

> 仅示例结构与风格；真实项目可按你们的 runner/context 封装调整。

```python
from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    # Locators（只在 page object 内部出现）
    @property
    def username_input(self):
        return self.page.get_by_label("用户名")

    @property
    def password_input(self):
        return self.page.get_by_label("密码")

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="登录")

    @property
    def error_alert(self):
        return self.page.get_by_role("alert")

    # Actions
    def open(self):
        self.page.goto(f"{self.base_url}/login")

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()

    # Assertions（内部等待，不让 steps sleep）
    def assert_login_failed(self, message: str):
        expect(self.error_alert).to_be_visible()
        expect(self.error_alert).to_contain_text(message)
```

## 组件对象（Component Object）示例

当页面包含可复用控件（表格/弹窗/分页），应抽成组件对象，页面对象组合调用。

```python
from playwright.sync_api import Page, Locator, expect


class Toast:
    def __init__(self, page: Page):
        self.page = page

    @property
    def root(self) -> Locator:
        return self.page.get_by_role("status")

    def assert_success(self, message: str):
        expect(self.root).to_be_visible()
        expect(self.root).to_contain_text(message)
```

## 等待策略（必须）

- 只允许等待“条件成立”，禁止固定 sleep。
- 等待应封装在 page object 的 action/assert 内部。

## 与 steps 的契约（必须）

- steps 调用 page object 时，只能调用“动作/断言”方法。
- steps 不允许访问 page object 的 locator 属性（避免泄露实现细节）。

## AI 生成/更新 page objects 的约束

- **允许修改范围**：`packages/page_objects/` 下的页面/组件实现。
- **禁止**：在 steps 中新增 selector；禁止在 page object 中固化环境 host（只用 `base_url`/config）。
- **当 locator 不稳定时**：优先建议研发补 `data-testid`；在未补齐前，选择语义定位 + 过滤策略，避免 XPath。

## 最佳实践（补充原文中的关键知识点）

### 1) Locator 链式与过滤（提升唯一性）
> 当一个 locator 过于宽泛时，用“先缩小容器，再定位子元素”的方式提升稳定性。

```python
# 先定位到购物车容器，再定位价格单元格（示意）
cart = page.get_by_test_id("shopping-cart")
price_cell = cart.get_by_role("cell", name="价格")
```

```python
# 通过 has_text 过滤（示意）
item = page.get_by_role("listitem").filter(has_text="iPhone").first
```

### 2) 组件化与组合（Component Objects）
- 页面对象负责“页面级流程”与“业务入口”
- 组件对象负责“可复用控件”（表格、弹窗、Toast、分页、表单）
- 页面对象可以组合多个组件对象，避免在每个页面重复写同一套控件逻辑

### 3) 高层动作聚合（App Actions / Flow 层，按需）
当一个业务流程跨多个页面（例如“登录→选品→下单→支付”），建议在 `packages/page_objects/flows/`（或类似目录）提供高层动作：
- steps 调用 flow
- flow 内部组合多个 page object / component object

**约束**：flow 只做编排，不写 selector（selector 仍在 page/component objects 内）。

### 4) 等待策略（更具体的约束）
- 优先等待 UI 条件：元素可见/不可见、URL 变化、文本出现
- 需要等待接口时，优先等待“与业务强相关的响应”（例如 path 包含某段且 status=200）
- 禁止 `sleep` 与不带条件的长超时等待

### 5) 反模式（Bad examples）
- **Bad：在 steps 里拿 locator 点击**（泄露实现细节、导致维护地狱）
- **Bad：page object 暴露 locator 给 steps 使用**（同上）
- **Bad：把断言写在 steps 里到处复制**（应该下沉到 `assert_*`）
- **Bad：用 `nth()`/index 定位核心元素**（除非明确豁免且有审计）

