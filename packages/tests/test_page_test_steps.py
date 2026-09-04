"""声明式 step 原语：序列化往返、参数插值与敏感值脱敏判定。"""
from __future__ import annotations

import pytest

from tuner_testkit.page_test.errors import ElementSpecError, StepExecutionError
from tuner_testkit.page_test.steps import (
    STEP_TYPES,
    AssertCount,
    AssertText,
    AssertUrl,
    AssertVisible,
    Check,
    Click,
    ExtractText,
    Fill,
    Goto,
    Press,
    RetryPolicy,
    RunFlow,
    Screenshot,
    Select,
    Upload,
    WaitForElement,
    WaitForResponse,
    WaitForUrl,
    placeholders_in,
    resolve_value,
    step_from_dict,
    steps_to_dicts,
)

SAMPLE_FLOW = (
    Goto(),
    Fill("username_input", "{{username}}"),
    Fill("password_input", "{{password}}"),
    Click("submit_button", retry=RetryPolicy(attempts=2, backoff_ms=100)),
    WaitForElement("welcome_banner", state="visible"),
    WaitForUrl("re:/dashboard"),
    WaitForResponse("/api/v1/me", status=200),
    ExtractText("welcome_banner", "welcome_text"),
    AssertText("welcome_banner", expected="{{username}}", operator="contains"),
    AssertVisible("welcome_banner"),
    AssertUrl("/dashboard"),
    AssertCount("nav_items", expected=5, operator="gte"),
    Check("remember_me", checked=False),
    Select("role_select", option="管理员", by="label"),
    Press("search_input", key="Enter"),
    Upload("attachment_input", file="{{invoice_file}}"),
    RunFlow("close_onboarding"),
    Screenshot("after_login"),
)


def test_every_step_category_is_registered():
    assert len(STEP_TYPES) == 23
    categories = {cls.category for cls in STEP_TYPES.values()}
    assert categories == {"navigate", "interact", "wait", "extract", "assert", "compose"}


def test_steps_roundtrip_through_dicts():
    """双向序列化是平台可视化与 page recorder 生成资产的前提。"""
    payload = steps_to_dicts(SAMPLE_FLOW)
    assert tuple(step_from_dict(item) for item in payload) == SAMPLE_FLOW


def test_serialized_step_carries_op_and_skips_defaults():
    payload = Fill("username_input", "{{username}}").to_dict()
    assert payload == {"op": "fill", "element": "username_input", "value": "{{username}}"}

    retry = Click("submit", retry=RetryPolicy(attempts=3)).to_dict()
    assert retry["retry"]["attempts"] == 3


def test_secret_values_are_flagged_for_log_masking():
    assert Fill("password_input", "{{password}}").is_secret()
    assert Fill("any_field", "{{token}}").is_secret()
    assert Fill("plain_field", "hello", secret=True).is_secret()
    assert not Fill("username_input", "{{username}}").is_secret()


def test_element_and_flow_references_are_discoverable():
    elements = {name for step in SAMPLE_FLOW for name in step.elements_used()}
    assert "username_input" in elements
    assert "nav_items" in elements
    flows = [name for step in SAMPLE_FLOW for name in step.flows_used()]
    assert flows == ["close_onboarding"]


def test_interpolation_preserves_type_for_whole_placeholder():
    params = {"username": "userA", "page_size": 10, "flag": True}
    assert resolve_value("{{username}}", params) == "userA"
    assert resolve_value("{{page_size}}", params) == 10
    assert resolve_value("{{flag}}", params) is True
    assert resolve_value("hi {{username}}, page {{page_size}}", params) == "hi userA, page 10"
    assert resolve_value(42, params) == 42


def test_interpolation_reads_env_placeholder(monkeypatch):
    monkeypatch.setenv("PAGE_TEST_SAMPLE_SECRET", "from-env")
    assert resolve_value("{{env:PAGE_TEST_SAMPLE_SECRET}}", {}) == "from-env"


def test_interpolation_reports_missing_param_and_env():
    with pytest.raises(StepExecutionError, match="未提供参数"):
        resolve_value("{{nope}}", {"username": "a"})
    with pytest.raises(StepExecutionError, match="环境变量"):
        resolve_value("{{env:PAGE_TEST_DEFINITELY_UNSET}}", {})


def test_placeholders_in_lists_referenced_names():
    assert placeholders_in("a{{x}}b{{env:Y}}") == ("x", "env:Y")
    assert placeholders_in(7) == ()


def test_invalid_step_arguments_rejected_at_construction():
    with pytest.raises(ElementSpecError, match="wait state"):
        WaitForElement("x", state="bogus")
    with pytest.raises(ElementSpecError, match="assert_text operator"):
        AssertText("x", expected="y", operator="bogus")
    with pytest.raises(ElementSpecError, match="assert_count operator"):
        AssertCount("x", expected=1, operator="bogus")
    with pytest.raises(ElementSpecError, match="select by"):
        Select("x", option="y", by="bogus")


def test_step_from_dict_rejects_unknown_op_and_key():
    with pytest.raises(ElementSpecError, match="未知 step op"):
        step_from_dict({"op": "teleport"})
    with pytest.raises(ElementSpecError, match="未知键"):
        step_from_dict({"op": "click", "element": "x", "bogus": 1})
