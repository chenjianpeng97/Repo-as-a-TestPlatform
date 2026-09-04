"""离线测试替身 —— 不装 playwright、不起浏览器也能测页面资产。

给 ``PageDriver`` 喂一个 :class:`FakePage`，就能验证 flow 的 step 序列、参数插值、
多定位器 fallback、断言与提取，全程无浏览器。下游项目仓给自己的 page object
写单测时可以直接复用本模块。

元素按 **key** 注册，key 与 ``LocatorSpec`` 的构造方式一一对应::

    page = FakePage()
    page.register("label=用户名", text="")             # get_by_label("用户名")
    page.register("role=button name=登录")             # get_by_role("button", name="登录")
    page.register("test_id=login-username")            # get_by_test_id("login-username")
    page.register("css=.toast", text="登录成功")        # locator(".toast")

**未注册的 key 视为不存在**，因此「首选候选失效、备用候选命中」这种 fallback
场景只需注册备用候选即可。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Callable


class FakeTimeoutError(Exception):
    """对应 playwright 的 TimeoutError：探测/等待超时。"""


@dataclass
class FakeElement:
    """一个已注册元素的状态。"""

    exists: bool = True
    visible: bool = True
    enabled: bool = True
    text: str = ""
    count: int = 1
    attributes: dict[str, str] = field(default_factory=dict)
    options: list[str] = field(default_factory=list)


class FakeLocator:
    """模拟 Playwright Locator 的最小子集。"""

    def __init__(self, page: "FakePage", key: str) -> None:
        self._page = page
        self.key = key

    # -- 链式收窄 ----------------------------------------------------
    # first / nth 故意不改变 key：driver 探测阶段统一加 .first，若改 key 就得
    # 为同一个元素注册两遍，与真实语义无关的负担。

    @property
    def first(self) -> "FakeLocator":
        return self

    def nth(self, index: int) -> "FakeLocator":
        return self

    def filter(self, has_text: str | None = None, **_: Any) -> "FakeLocator":
        if has_text is None:
            return self
        return FakeLocator(self._page, f"{self.key} [has_text={has_text}]")

    def get_by_role(self, role: str, *, name: str | None = None, **_: Any) -> "FakeLocator":
        suffix = f"role={role}" + (f" name={name}" if name is not None else "")
        return FakeLocator(self._page, f"{self.key} > {suffix}")

    def get_by_test_id(self, value: str) -> "FakeLocator":
        return FakeLocator(self._page, f"{self.key} > test_id={value}")

    def get_by_label(self, value: str, **_: Any) -> "FakeLocator":
        return FakeLocator(self._page, f"{self.key} > label={value}")

    def get_by_text(self, value: str, **_: Any) -> "FakeLocator":
        return FakeLocator(self._page, f"{self.key} > text={value}")

    def get_by_placeholder(self, value: str, **_: Any) -> "FakeLocator":
        return FakeLocator(self._page, f"{self.key} > placeholder={value}")

    def get_by_title(self, value: str, **_: Any) -> "FakeLocator":
        return FakeLocator(self._page, f"{self.key} > title={value}")

    def get_by_alt_text(self, value: str, **_: Any) -> "FakeLocator":
        return FakeLocator(self._page, f"{self.key} > alt_text={value}")

    def locator(self, selector: str) -> "FakeLocator":
        return FakeLocator(self._page, f"{self.key} > {_selector_key(selector)}")

    # -- 状态 --------------------------------------------------------

    @property
    def element(self) -> FakeElement | None:
        return self._page.elements.get(self.key)

    def _require(self, action: str) -> FakeElement:
        element = self.element
        if element is None or not element.exists:
            raise FakeTimeoutError(f"{action}: 元素不存在 ({self.key})")
        return element

    def wait_for(self, *, state: str = "visible", timeout: float | None = None) -> None:
        element = self.element
        present = element is not None and element.exists
        if state == "detached":
            if present:
                raise FakeTimeoutError(f"wait_for(detached) 失败 ({self.key})")
            return
        if state == "hidden":
            if present and element is not None and element.visible:
                raise FakeTimeoutError(f"wait_for(hidden) 失败 ({self.key})")
            return
        if not present:
            raise FakeTimeoutError(f"wait_for({state}) 失败: 不存在 ({self.key})")
        if state == "visible" and element is not None and not element.visible:
            raise FakeTimeoutError(f"wait_for(visible) 失败: 不可见 ({self.key})")

    def count(self) -> int:
        element = self.element
        if element is None or not element.exists:
            return 0
        return element.count

    def is_visible(self) -> bool:
        element = self.element
        return bool(element and element.exists and element.visible)

    def is_enabled(self) -> bool:
        element = self.element
        return bool(element and element.exists and element.enabled)

    def inner_text(self, timeout: float | None = None) -> str:
        return self._require("inner_text").text

    def text_content(self, timeout: float | None = None) -> str:
        return self._require("text_content").text

    def get_attribute(self, name: str, timeout: float | None = None) -> str | None:
        return self._require("get_attribute").attributes.get(name)

    # -- 动作 --------------------------------------------------------

    def fill(self, value: str, timeout: float | None = None) -> None:
        self._require("fill")
        self._page.filled[self.key] = value
        self._page.actions.append(("fill", self.key, value))

    def click(self, timeout: float | None = None) -> None:
        self._require("click")
        self._page.actions.append(("click", self.key, None))

    def hover(self, timeout: float | None = None) -> None:
        self._require("hover")
        self._page.actions.append(("hover", self.key, None))

    def check(self, timeout: float | None = None) -> None:
        self._require("check")
        self._page.actions.append(("check", self.key, True))

    def uncheck(self, timeout: float | None = None) -> None:
        self._require("uncheck")
        self._page.actions.append(("check", self.key, False))

    def press(self, key: str, timeout: float | None = None) -> None:
        self._require("press")
        self._page.actions.append(("press", self.key, key))

    def select_option(self, timeout: float | None = None, **kwargs: Any) -> None:
        self._require("select_option")
        self._page.actions.append(("select", self.key, kwargs))

    def set_input_files(self, files: Any, timeout: float | None = None) -> None:
        self._require("set_input_files")
        self._page.actions.append(("upload", self.key, files))


def _selector_key(selector: str) -> str:
    if selector.lower().startswith("xpath="):
        return f"xpath={selector[len('xpath='):]}"
    return f"css={selector}"


class FakePage:
    """模拟 Playwright Page 的最小子集。"""

    def __init__(self, *, url: str = "http://localhost/", title: str = "fake") -> None:
        self.elements: dict[str, FakeElement] = {}
        self.url = url
        self._title = title
        self.navigations: list[str] = []
        self.actions: list[tuple[str, str, Any]] = []
        self.filled: dict[str, str] = {}
        self.screenshots: list[str] = []
        self.waited_ms = 0
        self._handlers: dict[str, list[Callable[[Any], None]]] = {}

    # -- 注册 --------------------------------------------------------

    def register(self, key: str, **kwargs: Any) -> FakeElement:
        element = FakeElement(**kwargs)
        self.elements[key] = element
        return element

    def unregister(self, key: str) -> None:
        self.elements.pop(key, None)

    # -- 定位 --------------------------------------------------------

    def get_by_role(self, role: str, *, name: str | None = None, **_: Any) -> FakeLocator:
        key = f"role={role}" + (f" name={name}" if name is not None else "")
        return FakeLocator(self, key)

    def get_by_test_id(self, value: str) -> FakeLocator:
        return FakeLocator(self, f"test_id={value}")

    def get_by_label(self, value: str, **_: Any) -> FakeLocator:
        return FakeLocator(self, f"label={value}")

    def get_by_text(self, value: str, **_: Any) -> FakeLocator:
        return FakeLocator(self, f"text={value}")

    def get_by_placeholder(self, value: str, **_: Any) -> FakeLocator:
        return FakeLocator(self, f"placeholder={value}")

    def get_by_title(self, value: str, **_: Any) -> FakeLocator:
        return FakeLocator(self, f"title={value}")

    def get_by_alt_text(self, value: str, **_: Any) -> FakeLocator:
        return FakeLocator(self, f"alt_text={value}")

    def locator(self, selector: str) -> FakeLocator:
        return FakeLocator(self, _selector_key(selector))

    # -- 导航与杂项 ---------------------------------------------------

    def goto(self, url: str, timeout: float | None = None, **_: Any) -> None:
        self.url = url
        self.navigations.append(url)

    def go_back(self, timeout: float | None = None) -> None:
        self.navigations.append("<back>")

    def reload(self, timeout: float | None = None) -> None:
        self.navigations.append("<reload>")

    def title(self) -> str:
        return self._title

    def wait_for_timeout(self, milliseconds: float) -> None:
        self.waited_ms += int(milliseconds)

    def wait_for_url(self, pattern: Any, timeout: float | None = None) -> None:
        if not _matches(pattern, self.url):
            raise FakeTimeoutError(f"wait_for_url 失败: {self.url!r} 不匹配 {pattern!r}")

    def screenshot(self, path: str | None = None, **_: Any) -> bytes:
        if path:
            self.screenshots.append(str(path))
        return b""

    def on(self, event: str, handler: Callable[[Any], None]) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit_response(self, url: str, status: int = 200) -> None:
        """触发一个响应事件，供 ``WaitForResponse`` 命中。"""
        response = SimpleNamespace(url=url, status=status)
        for handler in self._handlers.get("response", []):
            handler(response)


def _matches(pattern: Any, value: str) -> bool:
    if isinstance(pattern, re.Pattern):
        return bool(pattern.search(value))
    return str(pattern) == value


class _LocatorAssertions:
    def __init__(self, locator: FakeLocator) -> None:
        self._locator = locator

    def _element(self) -> FakeElement | None:
        return self._locator.element

    def to_be_visible(self, timeout: float | None = None) -> None:
        if not self._locator.is_visible():
            raise AssertionError(f"expected visible: {self._locator.key}")

    def to_be_hidden(self, timeout: float | None = None) -> None:
        if self._locator.is_visible():
            raise AssertionError(f"expected hidden: {self._locator.key}")

    def to_be_enabled(self, timeout: float | None = None) -> None:
        if not self._locator.is_enabled():
            raise AssertionError(f"expected enabled: {self._locator.key}")

    def to_be_disabled(self, timeout: float | None = None) -> None:
        if self._locator.is_enabled():
            raise AssertionError(f"expected disabled: {self._locator.key}")

    def to_have_text(self, expected: Any, timeout: float | None = None) -> None:
        actual = self._locator.inner_text()
        if isinstance(expected, re.Pattern):
            if not expected.search(actual):
                raise AssertionError(f"expected text matching {expected!r}, got {actual!r}")
            return
        if actual != expected:
            raise AssertionError(f"expected text {expected!r}, got {actual!r}")

    def to_contain_text(self, expected: Any, timeout: float | None = None) -> None:
        actual = self._locator.inner_text()
        if str(expected) not in actual:
            raise AssertionError(f"expected {actual!r} to contain {expected!r}")

    def not_to_contain_text(self, expected: Any, timeout: float | None = None) -> None:
        actual = self._locator.inner_text()
        if str(expected) in actual:
            raise AssertionError(f"expected {actual!r} not to contain {expected!r}")

    def to_have_count(self, expected: int, timeout: float | None = None) -> None:
        actual = self._locator.count()
        if actual != expected:
            raise AssertionError(f"expected count {expected}, got {actual}")


class _PageAssertions:
    def __init__(self, page: FakePage) -> None:
        self._page = page

    def to_have_url(self, pattern: Any, timeout: float | None = None) -> None:
        if not _matches(pattern, self._page.url):
            raise AssertionError(f"expected url matching {pattern!r}, got {self._page.url!r}")


def fake_expect(target: Any) -> Any:
    if isinstance(target, FakeLocator):
        return _LocatorAssertions(target)
    return _PageAssertions(target)


def fake_playwright_api() -> SimpleNamespace:
    """替代 ``driver._import_playwright()`` 的返回值。"""
    return SimpleNamespace(expect=fake_expect, TimeoutError=FakeTimeoutError)


def make_driver(page: FakePage | None = None, **kwargs: Any) -> Any:
    """构造一个绑定 :class:`FakePage` 的 ``PageDriver``（不落盘健康事件）。"""
    from .driver import PageDriver

    page = page or FakePage()
    kwargs.setdefault("base_url", "http://localhost")
    kwargs.setdefault("persist_health", False)
    kwargs.setdefault("screenshot_on_failure", False)
    driver = PageDriver(page=page, **kwargs)
    driver._install_response_recorder()
    return driver


def patch_playwright(monkeypatch: Any) -> None:
    """把 driver 的 playwright import 换成本模块的替身。"""
    from . import driver as driver_module

    monkeypatch.setattr(driver_module, "_import_playwright", fake_playwright_api)


__all__ = [
    "FakeElement",
    "FakeLocator",
    "FakePage",
    "FakeTimeoutError",
    "fake_expect",
    "fake_playwright_api",
    "make_driver",
    "patch_playwright",
]
