## packages.page_test usage (recommended)

与 `packages.api_test` 同构的三层：**冻结的声明式资产** → **不可变链式调用** →
**执行引擎独占 IO/日志**。对位关系：

| api_test | page_test | 说明 |
| --- | --- | --- |
| `APIModel.path` | `PageModel.url_path` | 无 host，运行时注入 |
| `APIModel.body_schema` | `PageModel.inputs_schema` | 弱 schema，`set_*` 可 autofill |
| `APIModel.headers_policy` | `PageModel.locator_policy` | 把规范约束变成运行时校验 |
| `AssertOperation` | `AssertVisible` / `AssertText` / ... | 断言也是数据 |
| `ApiClient` | `PageDriver` | 独占 IO、脱敏日志 |
| `ApiResponse` | `PageResult` | 额外带 `locator_events` / `screenshot` |

### 1) 定义元素表（唯一允许出现定位器的地方）

每个元素挂**一组按优先级排序的候选**，这是稳定性的核心：首选失效时自动降级到备用，
测试不红；降级会留痕，由 `doctor` 汇总。

```python
from packages.page_test import ElementSpec, LocatorSpec

ELEMENTS = {
    "username_input": ElementSpec(
        name="username_input",
        description="登录用户名输入框",
        role_hint="textbox",
        locators=(
            LocatorSpec("label", "用户名"),               # 首选：语义定位
            LocatorSpec("test_id", "login-username"),     # 备用：测试标识
        ),
    ),
    "submit_button": ElementSpec(
        name="submit_button",
        locators=(LocatorSpec("role", "button", name="登录"),),
    ),
    "welcome_banner": ElementSpec(
        name="welcome_banner", locators=(LocatorSpec("test_id", "welcome"),)
    ),
}
```

`LocatorSpec` 支持 `scope`（先缩小容器再定位）、`has_text`（过滤）、`first`（消歧）、
`nth`（寻址，默认被 policy 禁止）、`confidence` + `note`（脆弱候选必须声明）。

### 2) 定义 PageModel 资产（在 `packages/page_objects/<app>/<page_slug>.py`）

```python
from packages.page_test import (
    AssertVisible, Click, ExtractText, Fill, PageFlow, PageModel,
    WaitForElement, WaitForUrl,
)

login_page_v1 = PageModel(
    id="example.login@v1",                 # <app>.<page_slug>@v<major>
    name="登录页",
    description="账号密码登录；前置条件：无",
    url_path="/login",                     # 无 host
    elements=ELEMENTS,
    inputs_schema={
        "username": {"type": "string", "required": True},
        "password": {"type": "string", "required": True},
    },
    ready=(WaitForElement("username_input", state="visible"),),
    extracts=(ExtractText("welcome_banner", "welcome_text"),),
    flows={
        "login": PageFlow(
            name="login",
            description="输入账号密码并提交",
            steps=(
                Fill("username_input", "{{username}}"),
                Fill("password_input", "{{password}}"),
                Click("submit_button"),
                WaitForUrl("/dashboard"),
                AssertVisible("welcome_banner"),
            ),
            example_params={"username": "demo", "password": "demo"},
        ),
    },
)
```

**凭据永不落盘**：值写 `{{password}}` 占位符，运行时从 `set_inputs` 或环境变量代入；
`Fill` 会自动识别敏感键，日志里只记 `***`。也可用 `{{env:SOME_VAR}}` 直接读环境变量。

`asserts` / `extracts` 描述**页面自身的稳定契约**，在 `open()` 时执行；flow 级断言写在
该 flow 的 steps 里（UI flow 常导航离开本页，不能像 API 那样每次都套页面断言）。

### 3) 调用：set_inputs / override_inputs 然后 open / run

```python
from packages.page_test import PageDriver

with PageDriver.launch(headless=True) as driver:
    invocation = login_page_v1.set_inputs({"username": "demo", "password": "x"})
    invocation.open(driver=driver)                 # Goto + ready + extracts + asserts
    result = invocation.run("login", driver=driver)

assert result.ok
print(result.extracted["welcome_text"], result.url)
```

`set_inputs` 浅合并、可 autofill schema；`override_inputs` 整表替换且不允许未声明的键
（与 `APIModel.set_json` / `override_json` 同一语义）。也可以 `model.bind(driver)` 之后
省掉每次传 `driver=`。

外部已有 page（behave `context.page` / pytest fixture / MCP 场景）用 `attach`：

```python
driver = PageDriver.attach(context.page)
```

### 4) 结果与定位器健康度

`PageResult` 除了 `ok` / `url` / `title` / `extracted`，还带：

- `steps`：每步的耗时、命中的候选索引、是否用了备用候选
- `locator_events`：本次运行的全部元素解析事件
- `fallbacks`：其中命中备用候选的部分——**首选定位器已失效的信号**
- `screenshot` / `failed_step` / `error`：失败诊断

断言失败抛 `PageAssertError`（同时是 `AssertionError`），诊断挂在 `exc.result` 上：

```python
try:
    login_page_v1.set_inputs({...}).run("login", driver=driver)
except PageAssertError as exc:
    print(exc.result.failed_step, exc.result.screenshot)
```

### 5) locator_policy：把规范约束变成运行时校验

```python
login_page_v1 = PageModel(
    ...,
    locator_policy={"allow_index": True, "probe_timeout_ms": 800},
)
```

默认值与含义见 `LocatorPolicy`：绝对 XPath 硬禁、相对 XPath 需声明 `fragile`、
`nth` 寻址默认禁而 `.first` 消歧允许、CSS 层级上限、稳定候选下限、**探测超时**
（多定位器机制的性能护栏，别设太大）。policy 挂在每个资产上，所以豁免是一行可审计的声明。

### 6) 复杂交互走 BasePage 逃生舱

声明式 step 序列是线性的，没有 `if` / `for`。翻页找行、条件性关弹窗、轮询状态这类场景
直接写 Python 方法，但**元素仍经 `self.el(name)` 访问**，因此照样享受 fallback 与体检。

```python
from packages.page_test import BasePage

class OrderListPage(BasePage):
    """订单列表页。前置条件：已登录。"""

    page_id = "example.order_list@v1"
    name = "订单列表页"
    url_path = "/orders"
    elements = ELEMENTS

    def find_order_across_pages(self, order_no: str, *, max_pages: int = 10) -> bool:
        for _ in range(max_pages):
            if self.el("row").locator.filter(has_text=order_no).count():
                return True
            if not self.el("next_page").locator.is_enabled():
                return False
            self.el("next_page").locator.click()
        return False
```

`BasePage` 不暴露 `self.page`；确需裸 API 走 `self.driver.raw_page`（刺眼命名便于 review）。
类范式与声明式可共存：类上也能写 `flows`，用 `self.run("<flow>")` 执行。

### 7) CLI：独立运行与体检

```bash
python -m packages.page_test list
python -m packages.page_test describe example.login@v1
python -m packages.page_test validate                       # 不启浏览器
python -m packages.page_test catalog --out report/page_objects_catalog.json
python -m packages.page_test run example.login@v1 --flow login --example --headed
python -m packages.page_test doctor example.login@v1
```

`doctor` 跨运行聚合健康事件，指出「首选定位器连续失效，实际靠备用候选兜住」这类
静默腐烂，并给出建议 patch。**它不会自动改写资产**——采纳由人或 AI 显式执行。

```
定位器体检 example.login@v1   (基于 3 次运行 / 12 个健康事件)

username_input
  [0] label='用户名'              命中 0/3    建议下移或删除
  [1] test_id='login-username'    命中 3/3    建议提升为首选
  诊断: 首选定位器连续失效，实际靠 [1] test_id='login-username' 兜住；页面文案或结构可能已改动
```

### 8) 单文件回放

`packages.page_objects.session` 集中管理凭据（对标 `api_objects.auth`），让单个资产文件
可以直接跑。在资产文件末尾加：

```python
if __name__ == "__main__":
    import sys
    from pathlib import Path

    for _root in Path(__file__).resolve().parents:
        if (_root / "pyproject.toml").is_file() and (_root / "packages").is_dir():
            if str(_root) not in sys.path:
                sys.path.insert(0, str(_root))
            break

    from packages.page_objects.session import replay_flow, report

    report(replay_flow(login_page_v1, flow="login"))
```

```bash
set TEST_UI_BASE_URL=https://your-env.example
set TEST_USERNAME=userA
set TEST_PASSWORD=...
set PAGE_TEST_HEADED=1
python packages/page_objects/example/login.py
```

### 9) 离线单测（不装 playwright）

`driver` 惰性 import playwright，`packages.page_test.testing` 提供 FakePage 替身，
所以页面资产的 flow、插值、fallback 与断言都能离线测：

```python
from packages.page_test.testing import FakePage, make_driver, patch_playwright

def test_login_flow(monkeypatch):
    patch_playwright(monkeypatch)
    page = FakePage()
    page.register("label=用户名")
    page.register("test_id=login-password")
    page.register("role=button name=登录")
    page.register("test_id=welcome", text="欢迎 demo")

    result = login_page_v1.set_inputs({"username": "demo", "password": "x"}).run(
        "login", driver=make_driver(page)
    )
    assert result.ok


def test_survives_primary_locator_rot(monkeypatch):
    """首选定位器失效时应降级而非失败。"""
    patch_playwright(monkeypatch)
    page = FakePage()
    page.register("test_id=login-username")      # 只注册备用候选
    ...
    assert result.ok and len(result.fallbacks) == 1
```

元素按 key 注册，key 与 `LocatorSpec` 一一对应：`label=用户名`、`role=button name=登录`、
`test_id=x`、`css=.y`、`xpath=//z`。**未注册的 key 视为不存在**，所以构造 fallback 场景
只需注册备用候选。

### 10) 用途边界

本地 `PageDriver` 供页面资产自检 / health check / pytest 回归 / doctor 体检。
BDD 资产生成流程中的**网络证据捕获仍必须走 Playwright MCP**（见
`.cursor/rules/bdd-pipeline-gates.mdc` Gate 1），本地驱动不得替代。
