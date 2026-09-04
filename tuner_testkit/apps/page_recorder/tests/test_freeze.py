"""freeze + codegen：live merge PageModel 源码（不启浏览器）。"""
from __future__ import annotations

import ast
from pathlib import Path

from tuner_testkit.apps.page_recorder.capture import build_capture
from tuner_testkit.apps.page_recorder.codegen import render_page_model_source
from tuner_testkit.apps.page_recorder.freeze import (
    PageObjectFreezer,
    collapse_steps,
    load_existing_model,
)
from tuner_testkit.page_test.locator import ElementSpec, LocatorSpec
from tuner_testkit.page_test.model import PageFlow, PageModel
from tuner_testkit.page_test.steps import Click, Fill, WaitForElement


def _click(*, url: str = "https://app.example/sign-in", name: str = "登录", extra=None):
    snap = {
        "tag": "button",
        "role": "button",
        "accessible_name": name,
        "test_id": "login-submit",
    }
    if extra:
        snap.update(extra)
    return build_capture({"kind": "click", "url": url, "snapshot": snap})


def _fill_password(value: str = "SuperSecret123!") :
    return build_capture(
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
            "value": value,
        }
    )


def test_collapse_consecutive_clicks_and_fills():
    steps = collapse_steps(
        (
            Click("submit_button"),
            Click("submit_button"),
            Fill("username_input", "{{username}}"),
            Fill("username_input", "{{username}}"),
            Click("other"),
        )
    )
    assert len(steps) == 3
    assert isinstance(steps[0], Click)
    assert isinstance(steps[1], Fill)
    assert steps[2].element == "other"


def test_freeze_creates_pagemodel_with_main_block(tmp_path: Path):
    freezer = PageObjectFreezer(tmp_path, app="plane", flow="login")
    cap = _click()
    assert cap is not None
    result = freezer.freeze(cap)
    assert result.action == "created"
    assert result.path.name == "sign_in.py"
    text = result.path.read_text(encoding="utf-8")
    assert "id=\"plane.sign_in@v1\"" in text or 'id="plane.sign_in@v1"' in text
    assert "url_path=" in text
    assert "example.com" not in text
    assert "if __name__ == \"__main__\":" in text
    assert "tuner_testkit.page_test.session" in text
    assert "PageModel(" in text
    ast.parse(text)
    loaded = load_existing_model(result.path)
    assert loaded is not None
    variable, model = loaded
    assert model.id == "plane.sign_in@v1"
    assert model.url_path == "/sign-in"
    assert "login" in model.flows
    assert model.flows["login"].steps
    assert variable.endswith("_page_v1")


def test_freeze_merges_locator_union_and_collapses_clicks(tmp_path: Path):
    freezer = PageObjectFreezer(tmp_path, app="plane", flow="login")
    first = _click()
    freezer.freeze(first)
    second = build_capture(
        {
            "kind": "click",
            "url": "https://app.example/sign-in",
            "snapshot": {
                "tag": "button",
                "role": "button",
                "accessible_name": "登录",
                "test_id": "login-submit",
                "id": "submit",
            },
        }
    )
    result = freezer.freeze(second)
    assert result.action == "updated"
    _variable, model = load_existing_model(result.path)
    clicks = [s for s in model.flows["login"].steps if isinstance(s, Click)]
    assert len(clicks) == 1
    button = next(el for el in model.elements.values() if "button" in el.name or el.role_hint == "button")
    strategies = {loc.strategy for loc in button.locators}
    assert "role" in strategies
    assert "test_id" in strategies
    assert "css" in strategies  # #submit


def test_password_never_written_to_source(tmp_path: Path):
    freezer = PageObjectFreezer(tmp_path, app="plane", flow="login")
    cap = _fill_password("SuperSecret123!")
    assert cap is not None
    result = freezer.freeze(cap)
    text = result.path.read_text(encoding="utf-8")
    assert "SuperSecret123!" not in text
    assert "{{password}}" in text
    _variable, model = load_existing_model(result.path)
    fill = next(s for s in model.flows["login"].steps if isinstance(s, Fill))
    assert fill.value == "{{password}}"
    assert fill.secret is True


def test_codegen_roundtrip_from_dict(tmp_path: Path):
    model = PageModel(
        id="demo.login@v1",
        name="登录页",
        description="roundtrip",
        url_path="/login",
        elements={
            "username_input": ElementSpec(
                name="username_input",
                description="用户名",
                role_hint="textbox",
                locators=(
                    LocatorSpec("label", "用户名"),
                    LocatorSpec("test_id", "login-username"),
                ),
            )
        },
        ready=(WaitForElement("username_input", state="visible"),),
        flows={
            "login": PageFlow(
                name="login",
                description="登录",
                steps=(Fill("username_input", "{{username}}"), Click("username_input")),
                example_params={"username": "demo"},
            )
        },
    )
    variable, source = render_page_model_source(model, variable="login_page_v1", replay_flow="login")
    assert variable == "login_page_v1"
    ast.parse(source)
    path = tmp_path / "login.py"
    path.write_text(source, encoding="utf-8")
    loaded = load_existing_model(path)
    assert loaded is not None
    _name, restored = loaded
    assert restored.id == model.id
    assert restored.url_path == "/login"
    assert list(restored.elements) == ["username_input"]
    assert restored.elements["username_input"].locators[0].strategy == "label"
    dumped = restored.to_dict()
    again = PageModel.from_dict(dumped)
    assert again.id == model.id
    assert again.flows["login"].steps[0].op == "fill"


def test_skip_overwrite_non_pagemodel(tmp_path: Path):
    freezer = PageObjectFreezer(tmp_path, app="plane", flow="login")
    target = tmp_path / "plane" / "sign_in.py"
    target.parent.mkdir(parents=True)
    target.write_text("class SignInPage:\n    pass\n", encoding="utf-8")
    result = freezer.freeze(_click())
    assert result.action == "skipped"
    assert "class SignInPage" in target.read_text(encoding="utf-8")


def test_ready_wait_for_first_element(tmp_path: Path):
    freezer = PageObjectFreezer(tmp_path, app="plane", flow="login")
    result = freezer.freeze(_click())
    _variable, model = load_existing_model(result.path)
    assert model.ready
    assert isinstance(model.ready[0], WaitForElement)
