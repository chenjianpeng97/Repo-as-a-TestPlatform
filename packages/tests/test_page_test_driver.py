"""执行引擎端到端 —— 全程离线（不装 playwright、不起浏览器）。

用 ``tuner_testkit.page_test.testing`` 的 FakePage 替身验证 step 分派、参数插值、
多定位器 fallback、断言、提取与日志脱敏。这也顺带证明 driver 的惰性 import
设计成立：没有 playwright 也能测页面资产。
"""
from __future__ import annotations

import pytest

from tuner_testkit.page_test.errors import ElementNotFoundError, PageAssertError
from tuner_testkit.page_test.locator import ElementSpec, LocatorSpec
from tuner_testkit.page_test.model import PageFlow, PageModel
from tuner_testkit.page_test.steps import (
    AssertCount,
    AssertHidden,
    AssertText,
    AssertUrl,
    AssertVisible,
    Check,
    Click,
    ExtractCount,
    ExtractText,
    Fill,
    Press,
    RetryPolicy,
    RunFlow,
    Select,
    Upload,
    WaitForElement,
    WaitForResponse,
    WaitForUrl,
)
from tuner_testkit.page_test.testing import FakePage, make_driver, patch_playwright

ELEMENTS = {
    "username_input": ElementSpec(
        name="username_input",
        locators=(LocatorSpec("label", "用户名"), LocatorSpec("test_id", "login-username")),
    ),
    "password_input": ElementSpec(
        name="password_input", locators=(LocatorSpec("test_id", "login-password"),)
    ),
    "submit_button": ElementSpec(
        name="submit_button", locators=(LocatorSpec("role", "button", name="登录"),)
    ),
    "welcome_banner": ElementSpec(
        name="welcome_banner", locators=(LocatorSpec("test_id", "welcome"),)
    ),
    "error_alert": ElementSpec(
        name="error_alert", locators=(LocatorSpec("role", "alert", name="错误"),)
    ),
    "nav_items": ElementSpec(name="nav_items", locators=(LocatorSpec("test_id", "nav-item"),)),
}


def build_model(**overrides) -> PageModel:
    payload = dict(
        id="example.login@v1",
        name="登录页",
        description="离线执行验证用",
        url_path="/login",
        elements=ELEMENTS,
        flows={
            "login": PageFlow(
                name="login",
                steps=(
                    Fill("username_input", "{{username}}"),
                    Fill("password_input", "{{password}}"),
                    Click("submit_button"),
                    WaitForElement("welcome_banner", state="visible"),
                    ExtractText("welcome_banner", "welcome_text"),
                    AssertText("welcome_banner", expected="{{username}}"),
                ),
                example_params={"username": "demo", "password": "secret"},
            )
        },
    )
    payload.update(overrides)
    return PageModel(**payload)


@pytest.fixture
def page() -> FakePage:
    fake = FakePage()
    fake.register("label=用户名")
    fake.register("test_id=login-password")
    fake.register("role=button name=登录")
    fake.register("test_id=welcome", text="欢迎 demo")
    fake.register("test_id=nav-item", count=5)
    return fake


@pytest.fixture(autouse=True)
def _playwright_stub(monkeypatch):
    patch_playwright(monkeypatch)


def test_open_navigates_and_waits_for_ready(page):
    model = build_model(ready=(WaitForElement("username_input", state="visible"),))
    driver = make_driver(page)

    result = model.open(driver=driver)

    assert result.ok
    assert page.navigations == ["http://localhost/login"]
    assert [outcome.op for outcome in result.steps] == ["goto", "wait_for_element"]


def test_flow_fills_clicks_extracts_and_asserts(page):
    model = build_model()
    driver = make_driver(page)

    result = model.set_inputs({"username": "demo", "password": "secret"}).run(
        "login", driver=driver
    )

    assert result.ok
    assert page.filled["label=用户名"] == "demo"
    assert page.filled["test_id=login-password"] == "secret"
    assert ("click", "role=button name=登录", None) in page.actions
    assert result.extracted["welcome_text"] == "欢迎 demo"
    assert all(outcome.ok for outcome in result.steps)


def test_extracted_variable_is_usable_by_later_steps(page):
    model = build_model(
        flows={
            "check": PageFlow(
                name="check",
                steps=(
                    ExtractText("welcome_banner", "banner_text"),
                    AssertText("welcome_banner", expected="{{banner_text}}", operator="eq"),
                    ExtractCount("nav_items", "nav_total"),
                    AssertCount("nav_items", expected="{{nav_total}}", operator="eq"),
                ),
            )
        }
    )
    result = build_model_run(model, page, "check")
    assert result.extracted == {"banner_text": "欢迎 demo", "nav_total": 5}


def build_model_run(model: PageModel, page: FakePage, flow: str, **params):
    return model.set_inputs(params).run(flow, driver=make_driver(page))


def test_fallback_keeps_flow_green_and_is_reported(page):
    """首选定位器失效时 flow 照常通过，但降级必须留痕、可被 doctor 看见。"""
    page.unregister("label=用户名")
    page.register("test_id=login-username")
    model = build_model()

    result = model.set_inputs({"username": "demo", "password": "secret"}).run(
        "login", driver=make_driver(page)
    )

    assert result.ok
    assert page.filled["test_id=login-username"] == "demo"
    assert len(result.fallbacks) == 1
    event = result.fallbacks[0]
    assert event.element == "username_input"
    assert event.used_index == 1
    fill_outcome = result.steps[0]
    assert fill_outcome.fallback_used
    assert fill_outcome.locator_index == 1


def test_repeated_resolution_reuses_hint_but_keeps_real_indexes(page):
    """失效首选每次都等满探测超时，所以队首提示是必要的优化。

    但提示不能掩盖 doctor 需要的信号：``used_index`` 必须仍是真实候选下标，
    每次降级都要留一条事件。
    """
    page.unregister("label=用户名")
    page.register("test_id=login-username")
    model = build_model(
        flows={
            "check": PageFlow(
                name="check",
                steps=(
                    Fill("username_input", "a"),
                    Fill("username_input", "b"),
                    Fill("username_input", "c"),
                ),
            )
        }
    )
    driver = make_driver(page)

    result = model.run("check", driver=driver)

    assert result.ok
    assert page.filled["test_id=login-username"] == "c"
    assert len(result.fallbacks) == 3
    assert {event.used_index for event in result.fallbacks} == {1}
    assert all(outcome.locator_index == 1 for outcome in result.steps)


def test_fallback_is_logged_once_per_run(page, monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(
        "tuner_testkit.page_test.driver.log_ui_action",
        lambda action, **fields: calls.append(action),
    )
    page.unregister("label=用户名")
    page.register("test_id=login-username")
    model = build_model(
        flows={
            "check": PageFlow(
                name="check",
                steps=(Fill("username_input", "a"), Fill("username_input", "b")),
            )
        }
    )

    model.run("check", driver=make_driver(page))

    assert calls.count("locator_fallback") == 1


def test_hints_reset_between_runs_so_recovered_primary_is_noticed(page):
    """首选修好之后，下一次运行必须重新从首选开始探测。"""
    page.unregister("label=用户名")
    page.register("test_id=login-username")
    model = build_model(
        flows={"check": PageFlow(name="check", steps=(Fill("username_input", "a"),))}
    )
    driver = make_driver(page)

    first = model.run("check", driver=driver)
    assert first.steps[0].locator_index == 1

    page.register("label=用户名")  # 研发把 label 补回来了
    second = model.run("check", driver=driver)

    assert second.steps[0].locator_index == 0
    assert second.fallbacks == ()


def test_missing_element_fails_with_diagnosis_attached(page):
    page.unregister("label=用户名")
    model = build_model()

    with pytest.raises(ElementNotFoundError) as excinfo:
        model.set_inputs({"username": "demo", "password": "x"}).run(
            "login", driver=make_driver(page)
        )

    result = excinfo.value.result
    assert result is not None
    assert not result.ok
    assert result.steps[-1].op == "fill"
    assert not result.steps[-1].ok
    assert "login-username" in result.steps[-1].error


def test_failed_assertion_raises_page_assert_error_with_result(page):
    model = build_model()

    with pytest.raises(PageAssertError) as excinfo:
        model.set_inputs({"username": "someone-else", "password": "x"}).run(
            "login", driver=make_driver(page)
        )

    assert isinstance(excinfo.value, AssertionError)
    result = excinfo.value.result
    assert result is not None and not result.ok
    assert result.failed_step.startswith("assert_text")
    assert "欢迎 demo" in result.error


def test_assert_hidden_passes_when_element_absent(page):
    model = build_model(
        flows={"check": PageFlow(name="check", steps=(AssertHidden("error_alert"),))}
    )
    assert build_model_run(model, page, "check").ok


def test_assert_visible_fails_when_element_present_but_invisible(page):
    page.register("role=alert name=错误", visible=False)
    model = build_model(
        flows={"check": PageFlow(name="check", steps=(AssertVisible("error_alert"),))}
    )
    with pytest.raises(PageAssertError):
        build_model_run(model, page, "check")


def test_secret_values_are_masked_in_logs(page, monkeypatch):
    calls: list[tuple[str, dict]] = []
    monkeypatch.setattr(
        "tuner_testkit.page_test.driver.log_ui_action",
        lambda action, **fields: calls.append((action, fields)),
    )
    model = build_model()

    model.set_inputs({"username": "demo", "password": "super-secret"}).run(
        "login", driver=make_driver(page)
    )

    fills = {fields["target"]: fields["value"] for action, fields in calls if action == "fill"}
    assert fills["username_input"] == "demo"
    assert fills["password_input"] == "***"
    assert "super-secret" not in repr(calls)


def test_wait_for_response_matches_buffered_response(page):
    model = build_model(
        flows={
            "check": PageFlow(
                name="check", steps=(WaitForResponse("/api/v1/me", status=200),)
            )
        }
    )
    driver = make_driver(page)
    page.emit_response("http://localhost/api/v1/me", 200)

    assert model.run("check", driver=driver).ok


def test_wait_for_response_times_out_without_match(page):
    from tuner_testkit.page_test.errors import StepExecutionError

    model = build_model(
        flows={
            "check": PageFlow(
                name="check",
                steps=(WaitForResponse("/api/v1/me", status=200, timeout_ms=10),),
            )
        }
    )
    with pytest.raises(StepExecutionError, match="等待响应超时"):
        model.run("check", driver=make_driver(page))


def test_wait_for_url_and_assert_url_use_substring_or_regex(page):
    page.url = "http://localhost/dashboard?tab=1"
    model = build_model(
        flows={
            "check": PageFlow(
                name="check",
                steps=(WaitForUrl("/dashboard"), AssertUrl("re:dashboard\\?tab=\\d")),
            )
        }
    )
    assert build_model_run(model, page, "check").ok


def test_interaction_steps_dispatch_to_locator_actions(page):
    page.register("test_id=remember", enabled=True)
    page.register("test_id=role-select", options=["管理员"])
    page.register("test_id=search")
    page.register("test_id=attachment")
    elements = dict(ELEMENTS)
    elements.update(
        {
            "remember_me": ElementSpec(
                name="remember_me", locators=(LocatorSpec("test_id", "remember"),)
            ),
            "role_select": ElementSpec(
                name="role_select", locators=(LocatorSpec("test_id", "role-select"),)
            ),
            "search_input": ElementSpec(
                name="search_input", locators=(LocatorSpec("test_id", "search"),)
            ),
            "attachment_input": ElementSpec(
                name="attachment_input", locators=(LocatorSpec("test_id", "attachment"),)
            ),
        }
    )
    model = build_model(
        elements=elements,
        flows={
            "check": PageFlow(
                name="check",
                steps=(
                    Check("remember_me", checked=False),
                    Select("role_select", option="管理员"),
                    Press("search_input", key="Enter"),
                    Upload("attachment_input", file="{{invoice}}"),
                ),
            )
        },
    )

    result = build_model_run(model, page, "check", invoice="C:/tmp/invoice.xlsx")

    assert result.ok
    kinds = {action for action, _, _ in page.actions}
    assert kinds == {"check", "select", "press", "upload"}
    assert ("check", "test_id=remember", False) in page.actions
    assert ("upload", "test_id=attachment", "C:/tmp/invoice.xlsx") in page.actions


def test_run_flow_step_executes_nested_flow(page):
    model = build_model(
        flows={
            "outer": PageFlow(name="outer", steps=(RunFlow("inner"), AssertVisible("welcome_banner"))),
            "inner": PageFlow(name="inner", steps=(Click("submit_button"),)),
        }
    )

    result = build_model_run(model, page, "outer")

    assert result.ok
    assert [outcome.op for outcome in result.steps] == ["click", "assert_visible"]


def test_retry_recovers_when_element_appears_late(page):
    page.unregister("role=button name=登录")
    model = build_model(
        flows={
            "check": PageFlow(
                name="check",
                steps=(
                    Click("submit_button", retry=RetryPolicy(attempts=3, backoff_ms=1)),
                ),
            )
        }
    )
    driver = make_driver(page)

    original = driver._pause
    attempts = {"n": 0}

    def pause_then_appear(milliseconds: int) -> None:
        attempts["n"] += 1
        if attempts["n"] == 1:
            page.register("role=button name=登录")
        original(milliseconds)

    driver._pause = pause_then_appear  # type: ignore[method-assign]

    result = model.run("check", driver=driver)

    assert result.ok
    assert attempts["n"] == 1


def test_each_run_archives_only_its_own_events(page, tmp_path, monkeypatch):
    """否则 doctor 的命中率会被重复计数污染，fallbacks 也会把历史降级算进来。"""
    monkeypatch.setenv("PAGE_TEST_ARTIFACTS_DIR", str(tmp_path / "page_test"))
    from tuner_testkit.page_test.health import load_events

    model = build_model(
        flows={"check": PageFlow(name="check", steps=(Fill("username_input", "a"),))}
    )
    driver = make_driver(page, persist_health=True)

    first = model.run("check", driver=driver)
    second = model.run("check", driver=driver)

    assert len(first.locator_events) == 1
    assert len(second.locator_events) == 1

    events, runs = load_events("example.login@v1")
    assert len(events) == 2
    assert runs == 2


def test_close_archives_events_from_python_actions(page, tmp_path, monkeypatch):
    """类范式的自定义动作不走 execute，事件要在 close 时补归档。"""
    monkeypatch.setenv("PAGE_TEST_ARTIFACTS_DIR", str(tmp_path / "page_test"))
    from tuner_testkit.page_test.health import load_events

    driver = make_driver(page, persist_health=True)
    driver.resolve("username_input", elements=ELEMENTS, page_id="example.login@v1")
    driver.close()

    events, runs = load_events("example.login@v1")
    assert len(events) == 1
    assert runs == 1


def test_bind_driver_allows_calling_without_explicit_driver(page):
    driver = make_driver(page)
    model = build_model().bind(driver)

    assert model.open().ok


def test_driver_without_binding_reports_clear_error():
    from tuner_testkit.page_test.errors import DriverError

    with pytest.raises(DriverError, match="PageDriver"):
        build_model().open()
