"""PageModel 资产：静态校验、不可变调用链与平台化 describe 契约。"""
from __future__ import annotations

import pytest

from packages.page_test.errors import (
    ElementSpecError,
    FlowNotFoundError,
    SchemaValidationError,
)
from packages.page_test.locator import ElementSpec, LocatorSpec
from packages.page_test.model import (
    PageFlow,
    PageModel,
    normalize_url_path,
)
from packages.page_test.steps import (
    AssertVisible,
    Click,
    ExtractText,
    Fill,
    Goto,
    RunFlow,
    WaitForElement,
)

ELEMENTS = {
    "username_input": ElementSpec(
        name="username_input",
        description="登录用户名输入框",
        role_hint="textbox",
        locators=(
            LocatorSpec("label", "用户名"),
            LocatorSpec("test_id", "login-username"),
        ),
    ),
    "password_input": ElementSpec(
        name="password_input",
        locators=(
            LocatorSpec("label", "密码"),
            LocatorSpec("test_id", "login-password"),
        ),
    ),
    "submit_button": ElementSpec(
        name="submit_button",
        locators=(LocatorSpec("role", "button", name="登录"),),
    ),
    "welcome_banner": ElementSpec(
        name="welcome_banner",
        locators=(LocatorSpec("test_id", "welcome"),),
    ),
}


def login_model(**overrides) -> PageModel:
    payload = dict(
        id="example.login@v1",
        name="登录页",
        description="示例登录页，用于验证资产形态",
        url_path="/login",
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
                    AssertVisible("welcome_banner"),
                ),
                example_params={"username": "demo", "password": "demo"},
            )
        },
    )
    payload.update(overrides)
    return PageModel(**payload)


def test_valid_model_passes_validation():
    assert login_model().validate() == []


def test_id_must_follow_versioned_convention():
    problems = login_model(id="LoginPage").validate()
    assert any("page_slug" in p for p in problems)


def test_url_path_must_not_contain_host():
    assert any("host" in p for p in login_model(url_path="https://x.test/login").validate())
    assert any("/ 开头" in p for p in login_model(url_path="login").validate())


def test_flow_referencing_unknown_element_is_reported():
    """flow 只按名字引用元素，因此引用完整性必须能静态查出来。"""
    broken = login_model(
        flows={
            "login": PageFlow(
                name="login", steps=(Fill("ghost_input", "{{username}}"),)
            )
        }
    )
    problems = broken.validate()
    assert any("未声明的元素 'ghost_input'" in p for p in problems)


def test_flow_referencing_unknown_flow_is_reported():
    broken = login_model(
        flows={"login": PageFlow(name="login", steps=(RunFlow("nope"),))}
    )
    assert any("不存在的 flow 'nope'" in p for p in broken.validate())


def test_flow_cycle_is_reported():
    broken = login_model(
        flows={
            "a": PageFlow(name="a", steps=(RunFlow("b"),)),
            "b": PageFlow(name="b", steps=(RunFlow("a"),)),
        }
    )
    assert any("成环" in p for p in broken.validate())


def test_flow_key_must_match_name_and_have_steps():
    broken = login_model(flows={"typo": PageFlow(name="login", steps=())})
    problems = broken.validate()
    assert any("不一致" in p for p in problems)
    assert any("没有任何 step" in p for p in problems)


def test_duplicate_extract_variable_is_reported():
    broken = login_model(
        flows={
            "login": PageFlow(
                name="login", steps=(ExtractText("welcome_banner", "welcome_text"),)
            )
        }
    )
    assert any("重复定义" in p for p in broken.validate())


def test_goto_step_must_not_carry_host():
    broken = login_model(
        flows={"login": PageFlow(name="login", steps=(Goto(path="https://x.test/a"),))}
    )
    assert any("host" in p for p in broken.validate())


def test_element_policy_problems_surface_through_model():
    broken = login_model(
        elements={
            "row": ElementSpec(
                name="row", locators=(LocatorSpec("css", ".row", nth=2, note="第三行"),)
            )
        },
        ready=(),
        extracts=(),
        flows={},
    )
    assert any("索引寻址" in p for p in broken.validate())


def test_per_page_policy_can_exempt_index_addressing():
    exempted = login_model(
        elements={
            "row": ElementSpec(
                name="row",
                locators=(LocatorSpec("css", ".row", nth=2, note="列表无稳定标识"),),
            )
        },
        ready=(),
        extracts=(),
        flows={},
        locator_policy={"allow_index": True},
    )
    assert exempted.validate() == []


# ---------------------------------------------------------------------------
# 不可变调用链（对齐 APIInvocation）
# ---------------------------------------------------------------------------


def test_set_inputs_is_immutable_and_merges_shallow():
    model = login_model()
    first = model.set_inputs({"username": "a"})
    second = first.set_inputs({"password": "b"})

    assert first._final_inputs() == {"username": "a"}
    assert second._final_inputs() == {"username": "a", "password": "b"}
    assert model.inputs_schema == login_model().inputs_schema


def test_set_inputs_autofills_unknown_keys_but_override_does_not():
    model = login_model()
    filled = model.set_inputs({"extra": 1})
    assert "extra" in filled._inputs_schema

    with pytest.raises(SchemaValidationError, match="未声明的键"):
        model.set_inputs({"extra": 1}, autofill_schema=False)
    with pytest.raises(SchemaValidationError):
        model.override_inputs({"extra": 1})


def test_override_inputs_replaces_previous_set():
    model = login_model()
    invocation = model.set_inputs({"username": "a"}).override_inputs({"password": "b"})
    assert invocation._final_inputs() == {"password": "b"}


def test_run_unknown_flow_raises():
    with pytest.raises(FlowNotFoundError, match="没有 flow"):
        login_model().run("nope", driver=object())


# ---------------------------------------------------------------------------
# 平台化导出
# ---------------------------------------------------------------------------


def test_describe_exposes_elements_flows_and_policy():
    payload = login_model().describe()

    assert payload["kind"] == "page_model"
    assert payload["id"] == "example.login@v1"
    element_names = [e["name"] for e in payload["elements"]]
    assert element_names == sorted(ELEMENTS)
    username = next(e for e in payload["elements"] if e["name"] == "username_input")
    assert [locator["strategy"] for locator in username["locators"]] == ["label", "test_id"]
    assert username["role_hint"] == "textbox"

    flow = payload["flows"][0]
    assert flow["name"] == "login"
    assert [step["op"] for step in flow["steps"]] == [
        "fill",
        "fill",
        "click",
        "assert_visible",
    ]
    assert flow["example_params"] == {"username": "demo", "password": "demo"}
    assert payload["locator_policy"]["allow_absolute_xpath"] is False
    assert payload["ready"][0]["op"] == "wait_for_element"


def test_model_roundtrips_through_dicts():
    model = login_model()
    restored = PageModel.from_dict(model.to_dict())
    assert restored == model


def test_describe_payload_can_be_reloaded():
    """describe() 的产物也要能还原，平台改完流程能写回资产。"""
    model = login_model()
    restored = PageModel.from_dict(model.describe())
    assert restored.id == model.id
    assert restored.elements == model.elements
    assert restored.flows == model.flows


def test_from_dict_rejects_unknown_key():
    with pytest.raises(ElementSpecError, match="未知键"):
        PageModel.from_dict({"id": "a.b@v1", "name": "x", "bogus": 1})


def test_fingerprint_tracks_url_and_element_names():
    model = login_model()
    same = login_model(description="改了描述")
    assert model.fingerprint() == same.fingerprint()

    different = login_model(url_path="/signin")
    assert model.fingerprint() != different.fingerprint()


def test_normalize_url_path_masks_ids_and_uuids():
    assert normalize_url_path("/projects/42/issues") == "/projects/{id}/issues"
    assert (
        normalize_url_path("/x/2b6f0cc9-04b8-4f2a-9a6a-5c1c2c1b7a11")
        == "/x/{uuid}"
    )
    assert normalize_url_path("/login") == "/login"
