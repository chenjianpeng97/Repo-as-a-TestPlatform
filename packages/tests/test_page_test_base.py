"""BasePage 逃生舱：Python 方法写复杂交互，元素层仍是声明式。"""
from __future__ import annotations

import pytest
from pydantic import Field

from tuner_testkit.page_test.base import BasePage
from tuner_testkit.page_test.locator import ElementSpec, LocatorSpec
from tuner_testkit.page_test.model import PageFlow
from tuner_testkit.page_test.steps import AssertVisible, Click, WaitForElement
from tuner_testkit.page_test.testing import FakePage, make_driver, patch_playwright


class OrderListPage(BasePage):
    """订单列表页。用于验证「声明式 step 表达不了的循环」走 Python 方法。

    前置条件：已登录且有列表查看权限。
    """

    page_id = "example.order_list@v1"
    name = "订单列表页"
    url_path = "/orders"
    tags = ("example",)
    elements = {
        "row": ElementSpec(
            name="row",
            role_hint="row",
            locators=(LocatorSpec("test_id", "order-row"),),
        ),
        "next_page": ElementSpec(
            name="next_page",
            locators=(LocatorSpec("role", "button", name="下一页"),),
        ),
        "empty_hint": ElementSpec(
            name="empty_hint", locators=(LocatorSpec("test_id", "empty"),)
        ),
    }
    flows = {
        "go_next_page": PageFlow(
            name="go_next_page",
            steps=(Click("next_page"), WaitForElement("row", state="visible")),
        )
    }
    ready = (WaitForElement("row", state="visible"),)
    asserts = (AssertVisible("row"),)
    example_params = {"keyword": "INV"}

    class Params(BasePage.Params):
        keyword: str = Field("", description="订单号关键字")

    def find_order_across_pages(self, order_no: str, *, max_pages: int = 10) -> bool:
        """翻页查找订单号 —— 声明式 step 序列表达不了的循环。"""
        for _ in range(max_pages):
            if self.el("row").locator.filter(has_text=order_no).count():
                return True
            if not self.el("next_page").locator.is_enabled():
                return False
            self.el("next_page").locator.click()
        return False

    def assert_not_empty(self) -> None:
        """业务断言：列表非空。"""
        if not self.el("row").locator.count():
            raise AssertionError("订单列表为空")


@pytest.fixture(autouse=True)
def _playwright_stub(monkeypatch):
    patch_playwright(monkeypatch)


@pytest.fixture
def page() -> FakePage:
    fake = FakePage()
    fake.register("test_id=order-row", count=2, text="INV-001")
    fake.register("test_id=order-row [has_text=INV-001]", count=1)
    fake.register("role=button name=下一页", enabled=True)
    return fake


def test_subclass_is_auto_registered_for_discovery():
    from tuner_testkit.page_test.base import PAGE_CLASSES

    assert PAGE_CLASSES["example.order_list@v1"] is OrderListPage


def test_class_validates_against_page_model_rules():
    assert OrderListPage.validate() == []


def test_as_model_shares_the_same_element_declaration():
    model = OrderListPage.as_model()

    assert model.id == "example.order_list@v1"
    assert model.elements == OrderListPage.elements
    assert model.url_path == "/orders"
    assert "go_next_page" in model.flows
    assert model.description.startswith("订单列表页")


def test_describe_marks_python_actions_instead_of_step_graph():
    """平台「流程」栏对类范式展示自定义方法，元素表照样可视化。"""
    payload = OrderListPage.describe()

    assert payload["kind"] == "page_class"
    assert payload["class"] == "OrderListPage"
    assert [element["name"] for element in payload["elements"]] == [
        "empty_hint",
        "next_page",
        "row",
    ]

    actions = {item["name"]: item for item in payload["python_actions"]}
    assert set(actions) == {"find_order_across_pages", "assert_not_empty"}
    assert actions["find_order_across_pages"]["kind"] == "action"
    assert actions["assert_not_empty"]["kind"] == "assert"
    assert "order_no" in actions["find_order_across_pages"]["signature"]
    assert actions["find_order_across_pages"]["doc"].startswith("翻页查找订单号")

    assert payload["params_schema"]["properties"]["keyword"]["description"] == "订单号关键字"
    assert payload["example_params"] == {"keyword": "INV"}


def test_el_is_the_only_element_entry_and_uses_fallback(page):
    page.unregister("test_id=order-row")
    page.register("css=.order-row", count=1)
    driver = make_driver(page)

    class Fallbacky(OrderListPage):
        page_id = "example.order_list_fallback@v1"
        elements = {
            "row": ElementSpec(
                name="row",
                locators=(
                    LocatorSpec("test_id", "order-row"),
                    LocatorSpec("css", ".order-row"),
                ),
            )
        }

    resolved = Fallbacky(driver).el("row")

    assert resolved.index == 1
    assert resolved.fallback_used
    assert driver.collector.snapshot()[0].outcome == "fallback"


def test_python_action_loops_over_pages(page):
    order_page = OrderListPage(make_driver(page))

    assert order_page.find_order_across_pages("INV-001") is True


def test_python_action_stops_when_pagination_exhausted(page):
    page.register("test_id=order-row [has_text=INV-999]", exists=False, count=0)
    page.register("role=button name=下一页", enabled=False)
    order_page = OrderListPage(make_driver(page))

    assert order_page.find_order_across_pages("INV-999") is False


def test_call_dispatches_public_actions_only(page):
    order_page = OrderListPage(make_driver(page))

    assert order_page.call("find_order_across_pages", order_no="INV-001") is True

    from tuner_testkit.page_test.errors import ElementSpecError

    with pytest.raises(ElementSpecError):
        order_page.call("el", name="row")
    with pytest.raises(ElementSpecError):
        order_page.call("_driver")


def test_declarative_flow_still_runs_from_a_class_page(page):
    order_page = OrderListPage(make_driver(page))

    result = order_page.run("go_next_page")

    assert result.ok
    assert ("click", "role=button name=下一页", None) in page.actions


def test_open_uses_ready_and_page_level_asserts(page):
    order_page = OrderListPage(make_driver(page))

    result = order_page.open()

    assert result.ok
    assert [outcome.op for outcome in result.steps] == [
        "goto",
        "wait_for_element",
        "assert_visible",
    ]
    assert page.navigations == ["http://localhost/orders"]


def test_missing_docstring_and_elements_are_reported():
    class Bare(BasePage):
        page_id = "example.bare@v1"
        name = "空页面"

    problems = Bare.validate()
    assert any("docstring" in p for p in problems)
    assert any("没有声明任何元素" in p for p in problems)


def test_example_params_must_satisfy_params_model():
    class BadExample(BasePage):
        """带有不合法样例入参的页面。"""

        page_id = "example.bad@v1"
        name = "坏样例"
        elements = {
            "row": ElementSpec(name="row", locators=(LocatorSpec("test_id", "row"),))
        }
        example_params = {"unknown_field": 1}

    assert any("example_params" in p for p in BadExample.validate())
