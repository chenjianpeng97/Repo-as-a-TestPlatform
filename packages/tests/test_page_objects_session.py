"""单文件回放接缝：凭据从环境变量注入，资产源码里只留占位符。"""
from __future__ import annotations

import pytest

from packages.page_objects import session
from packages.page_test.base import BasePage
from packages.page_test.locator import ElementSpec, LocatorSpec
from packages.page_test.model import PageFlow, PageModel
from packages.page_test.steps import AssertVisible, Click, Fill, WaitForElement
from packages.page_test.testing import FakePage, make_driver, patch_playwright

LOGIN_PAGE = PageModel(
    id="fixture.session_login@v1",
    name="示例登录页",
    description="验证 session.replay_flow 的组装",
    url_path="/login",
    elements={
        "username_input": ElementSpec(
            name="username_input", locators=(LocatorSpec("test_id", "username"),)
        ),
        "password_input": ElementSpec(
            name="password_input", locators=(LocatorSpec("test_id", "password"),)
        ),
        "submit_button": ElementSpec(
            name="submit_button", locators=(LocatorSpec("role", "button", name="登录"),)
        ),
        "welcome_banner": ElementSpec(
            name="welcome_banner", locators=(LocatorSpec("test_id", "welcome"),)
        ),
    },
    ready=(WaitForElement("username_input", state="visible"),),
    flows={
        "login": PageFlow(
            name="login",
            steps=(
                Fill("username_input", "{{username}}"),
                Fill("password_input", "{{password}}"),
                Click("submit_button"),
                AssertVisible("welcome_banner"),
            ),
            example_params={"username": "demo", "password": "demo"},
        )
    },
)


@pytest.fixture
def page() -> FakePage:
    fake = FakePage()
    fake.register("test_id=username")
    fake.register("test_id=password")
    fake.register("role=button name=登录")
    fake.register("test_id=welcome", text="欢迎")
    return fake


@pytest.fixture
def stub_launch(monkeypatch, page):
    """把 launch_driver 换成 FakePage 驱动，避免真起浏览器。"""
    patch_playwright(monkeypatch)
    driver = make_driver(page)
    monkeypatch.setattr(session, "launch_driver", lambda **_: driver)
    return driver


def test_credentials_come_from_env_only(monkeypatch):
    monkeypatch.delenv("TEST_USERNAME", raising=False)
    monkeypatch.delenv("TEST_PASSWORD", raising=False)
    assert session.get_ui_credentials() == {}

    monkeypatch.setenv("TEST_USERNAME", "userA")
    monkeypatch.setenv("TEST_PASSWORD", "p@ss")
    assert session.get_ui_credentials() == {"username": "userA", "password": "p@ss"}


def test_require_credentials_fails_loudly_when_unset(monkeypatch):
    monkeypatch.delenv("TEST_USERNAME", raising=False)
    monkeypatch.delenv("TEST_PASSWORD", raising=False)
    with pytest.raises(SystemExit, match="TEST_USERNAME"):
        session.require_ui_credentials()


def test_replay_flow_injects_env_credentials_into_placeholders(
    monkeypatch, stub_launch, page
):
    """资产里写 {{username}} / {{password}}，真值运行时才从环境变量来。"""
    monkeypatch.setenv("TEST_USERNAME", "userA")
    monkeypatch.setenv("TEST_PASSWORD", "p@ss")

    result = session.replay_flow(LOGIN_PAGE, flow="login")

    assert result.ok
    assert page.filled["test_id=username"] == "userA"
    assert page.filled["test_id=password"] == "p@ss"
    assert page.navigations == ["http://localhost/login"]


def test_replay_flow_explicit_params_win_over_env(monkeypatch, stub_launch, page):
    monkeypatch.setenv("TEST_USERNAME", "from-env")
    monkeypatch.setenv("TEST_PASSWORD", "p@ss")

    session.replay_flow(LOGIN_PAGE, flow="login", params={"username": "explicit"})

    assert page.filled["test_id=username"] == "explicit"


def test_replay_flow_requires_flow_when_not_opening(monkeypatch, stub_launch):
    monkeypatch.setenv("TEST_USERNAME", "a")
    monkeypatch.setenv("TEST_PASSWORD", "b")
    with pytest.raises(ValueError, match="必须提供 flow"):
        session.replay_flow(LOGIN_PAGE, open_first=False)


def test_as_page_model_accepts_model_and_class():
    assert session.as_page_model(LOGIN_PAGE) is LOGIN_PAGE

    class ClassPage(BasePage):
        """类范式页面。"""

        page_id = "fixture.session_class@v1"
        name = "类页面"
        url_path = "/items"
        elements = {
            "row": ElementSpec(name="row", locators=(LocatorSpec("test_id", "row"),))
        }

    assert session.as_page_model(ClassPage).id == "fixture.session_class@v1"

    with pytest.raises(TypeError):
        session.as_page_model("not-an-asset")


def test_bootstrap_repo_path_points_at_repo_root():
    root = session.bootstrap_repo_path()
    assert (root / "pyproject.toml").is_file()
    assert (root / "packages").is_dir()


def test_main_block_template_is_formattable():
    rendered = session.MAIN_BLOCK_TEMPLATE.format(
        variable="fixture_login_page_v1", flow="login"
    )
    assert "replay_flow(fixture_login_page_v1, flow='login')" in rendered
    assert "__main__" in rendered


def test_report_prints_outcome_and_warns_on_fallback(capsys, stub_launch, monkeypatch):
    monkeypatch.setenv("TEST_USERNAME", "a")
    monkeypatch.setenv("TEST_PASSWORD", "b")
    result = session.replay_flow(LOGIN_PAGE, flow="login")

    session.report(result)

    out = capsys.readouterr().out
    assert "OK" in out
    assert "fixture.session_login@v1" in out
