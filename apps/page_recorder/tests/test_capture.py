"""capture：事件 → 脱敏 Capture（不启浏览器）。"""
from __future__ import annotations

from apps.page_recorder.capture import (
    build_capture,
    page_slug_from_path,
    url_path_from_url,
)
from packages.page_test.steps import Check, Click, Fill, Select


def test_url_path_strips_host_and_normalizes_id():
    assert url_path_from_url("https://app.example/projects/42/issues") == "/projects/{id}/issues"
    assert "example" not in url_path_from_url("https://app.example/sign-in")
    assert page_slug_from_path("/sign-in") == "sign_in"
    assert page_slug_from_path("/") == "home"


def test_password_fill_is_placeholder_never_raw_value():
    capture = build_capture(
        {
            "kind": "change",
            "url": "https://app.example/sign-in",
            "snapshot": {
                "tag": "input",
                "type": "password",
                "label": "密码",
                "name": "password",
                "test_id": "login-password",
            },
            "value": "SuperSecret123!",
        }
    )
    assert capture is not None
    assert isinstance(capture.step, Fill)
    assert capture.step.value == "{{password}}"
    assert capture.step.secret is True
    assert capture.element is not None
    assert capture.element.is_secret
    assert "SuperSecret" not in repr(capture)


def test_username_fill_placeholder():
    capture = build_capture(
        {
            "kind": "change",
            "url": "https://app.example/sign-in",
            "snapshot": {
                "tag": "input",
                "type": "text",
                "label": "用户名",
                "name": "username",
                "id": "username",
                "test_id": "login-username",
            },
            "value": "alice",
        }
    )
    assert capture is not None
    assert isinstance(capture.step, Fill)
    assert capture.step.value == "{{username}}"
    assert "alice" not in repr(capture.step)


def test_click_on_textbox_is_ignored_as_step():
    capture = build_capture(
        {
            "kind": "click",
            "url": "https://app.example/sign-in",
            "snapshot": {
                "tag": "input",
                "type": "text",
                "label": "用户名",
                "test_id": "login-username",
            },
        }
    )
    assert capture is not None
    assert capture.step is None
    assert capture.element is not None


def test_click_button_becomes_click_step():
    capture = build_capture(
        {
            "kind": "click",
            "url": "https://app.example/sign-in",
            "snapshot": {
                "tag": "button",
                "role": "button",
                "accessible_name": "登录",
                "test_id": "login-submit",
            },
        }
    )
    assert capture is not None
    assert isinstance(capture.step, Click)
    assert capture.url_path == "/sign-in"
    assert capture.page_slug == "sign_in"


def test_checkbox_change_is_check_step():
    capture = build_capture(
        {
            "kind": "change",
            "url": "https://app.example/settings",
            "snapshot": {
                "tag": "input",
                "type": "checkbox",
                "label": "记住我",
                "test_id": "remember",
            },
            "checked": False,
        }
    )
    assert capture is not None
    assert isinstance(capture.step, Check)
    assert capture.step.checked is False


def test_select_uses_placeholder_not_option_text():
    capture = build_capture(
        {
            "kind": "change",
            "url": "https://app.example/settings",
            "snapshot": {
                "tag": "select",
                "label": "国家",
                "name": "country",
                "test_id": "country",
            },
            "select_label": "China",
            "select_value": "CN",
        }
    )
    assert capture is not None
    assert isinstance(capture.step, Select)
    assert capture.step.option == "{{country}}"
    assert "China" not in str(capture.step.option)


def test_scan_has_element_but_no_step():
    capture = build_capture(
        {
            "kind": "scan",
            "url": "https://app.example/home",
            "snapshot": {
                "tag": "a",
                "href": "/projects",
                "accessible_name": "项目",
                "role": "link",
            },
        }
    )
    assert capture is not None
    assert capture.step is None
    assert capture.element is not None


def test_absolute_xpath_only_snapshot_yields_nothing():
    capture = build_capture(
        {
            "kind": "click",
            "url": "https://app.example/x",
            "snapshot": {
                "tag": "div",
                "xpath": "/html/body/div[1]/div[2]",
            },
        }
    )
    assert capture is None
