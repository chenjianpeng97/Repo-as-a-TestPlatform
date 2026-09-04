"""locator policy 与多候选 fallback —— page_test 稳定性核心的确定性校验。"""
from __future__ import annotations

import pytest

from tuner_testkit.page_test.errors import (
    ElementNotFoundError,
    ElementSpecError,
    LocatorPolicyError,
)
from tuner_testkit.page_test.locator import (
    DEFAULT_POLICY,
    ElementSpec,
    LocatorPolicy,
    LocatorSpec,
    css_depth,
    is_absolute_xpath,
    resolve_element,
    validate_element,
    validate_elements,
)
from tuner_testkit.page_test.testing import FakePage


def _element(*locators: LocatorSpec, name: str = "target") -> ElementSpec:
    return ElementSpec(name=name, locators=locators)


# ---------------------------------------------------------------------------
# 静态 policy 校验：把规范文字变成运行时可执行的约束
# ---------------------------------------------------------------------------


def test_semantic_and_test_id_candidates_pass():
    element = _element(
        LocatorSpec("label", "用户名"),
        LocatorSpec("test_id", "login-username"),
    )
    validate_element(element, policy=DEFAULT_POLICY)


def test_absolute_xpath_is_hard_rejected():
    element = _element(
        LocatorSpec("xpath", "/html/body/div[3]/input", confidence="fragile", note="录制得到")
    )
    with pytest.raises(LocatorPolicyError, match="绝对 XPath"):
        validate_element(element, policy=DEFAULT_POLICY)


def test_relative_xpath_allowed_only_as_fragile_candidate():
    """相对 XPath 有 CSS 做不到的能力（text() / 轴向），允许但必须降权。"""
    fragile = _element(
        LocatorSpec("test_id", "row-action"),
        LocatorSpec(
            "xpath",
            "//td[text()='张三']/following-sibling::td//button",
            confidence="fragile",
            note="伪表格无 role/testid",
        ),
    )
    validate_element(fragile, policy=DEFAULT_POLICY)

    undeclared = _element(
        LocatorSpec("xpath", "//td//button"),
        LocatorSpec("test_id", "row-action"),
    )
    with pytest.raises(LocatorPolicyError, match="fragile"):
        validate_element(undeclared, policy=DEFAULT_POLICY)


def test_index_addressing_rejected_but_disambiguation_allowed():
    """``nth(i)`` 是用位置代替业务标识（寻址）；``.first`` 是消除 strict mode 冲突（消歧）。"""
    addressing = _element(LocatorSpec("css", ".row", nth=3, note="第四行"))
    with pytest.raises(LocatorPolicyError, match="索引寻址"):
        validate_element(addressing, policy=DEFAULT_POLICY)

    disambiguation = _element(LocatorSpec("role", "button", name="保存", first=True))
    validate_element(disambiguation, policy=DEFAULT_POLICY)


def test_index_addressing_can_be_exempted_per_page_with_note():
    element = _element(LocatorSpec("css", ".row", nth=3, note="列表无稳定标识，已评估"))
    validate_element(element, policy=LocatorPolicy(allow_index=True))

    without_note = _element(LocatorSpec("css", ".row", nth=3))
    with pytest.raises(LocatorPolicyError, match="note"):
        validate_element(without_note, policy=LocatorPolicy(allow_index=True))


def test_deep_dom_dependent_css_rejected():
    element = _element(LocatorSpec("css", "div > div > span > a > b > i"))
    with pytest.raises(LocatorPolicyError, match="层级"):
        validate_element(element, policy=DEFAULT_POLICY)


def test_fragile_candidate_requires_note_and_fallback():
    no_note = _element(LocatorSpec("css", ".toast", confidence="fragile"))
    with pytest.raises(LocatorPolicyError, match="note"):
        validate_element(no_note, policy=DEFAULT_POLICY)

    fragile_primary_only = _element(
        LocatorSpec("css", ".toast", confidence="fragile", note="无语义标识")
    )
    with pytest.raises(LocatorPolicyError):
        validate_element(fragile_primary_only, policy=LocatorPolicy(min_stable_candidates=0))


def test_role_locator_requires_name_or_text():
    element = _element(LocatorSpec("role", "button"))
    with pytest.raises(LocatorPolicyError, match="name"):
        validate_element(element, policy=DEFAULT_POLICY)


def test_too_many_candidates_rejected():
    element = _element(
        LocatorSpec("test_id", "a"),
        LocatorSpec("test_id", "b"),
        LocatorSpec("test_id", "c"),
        LocatorSpec("test_id", "d"),
        LocatorSpec("test_id", "e"),
    )
    with pytest.raises(LocatorPolicyError, match="fallback_max_attempts"):
        validate_element(element, policy=DEFAULT_POLICY)


def test_unknown_policy_key_rejected():
    with pytest.raises(LocatorPolicyError, match="未知键"):
        LocatorPolicy.from_mapping({"allow_xpath": True, "typo_field": 1})


def test_scope_reference_must_exist_and_not_cycle():
    dangling = {
        "cell": ElementSpec(
            name="cell", locators=(LocatorSpec("css", ".cell", scope="missing_table"),)
        )
    }
    assert any("不存在" in p for p in validate_elements(dangling))

    cyclic = {
        "a": ElementSpec(name="a", locators=(LocatorSpec("css", ".a", scope="b"),)),
        "b": ElementSpec(name="b", locators=(LocatorSpec("css", ".b", scope="a"),)),
    }
    assert any("成环" in p for p in validate_elements(cyclic))


def test_element_table_key_must_match_spec_name():
    problems = validate_elements(
        {"typo": ElementSpec(name="actual", locators=(LocatorSpec("test_id", "x"),))}
    )
    assert any("不一致" in p for p in problems)


def test_absolute_xpath_detection_and_css_depth():
    assert is_absolute_xpath("/html/body/div")
    assert is_absolute_xpath("xpath=/a/b")
    assert not is_absolute_xpath("//div[@id='x']")
    assert not is_absolute_xpath(".//td")
    assert css_depth(".a") == 1
    assert css_depth("div > span a") == 3


def test_locator_spec_roundtrip_preserves_fields():
    spec = LocatorSpec(
        "role",
        "button",
        name="保存",
        exact=True,
        has_text="草稿",
        first=True,
        scope="dialog",
        confidence="fragile",
        note="弹窗内多个同名按钮",
    )
    assert LocatorSpec.from_dict(spec.to_dict()) == spec

    element = _element(spec, LocatorSpec("test_id", "save"))
    assert ElementSpec.from_dict(element.to_dict()) == element


def test_element_spec_rejects_unknown_key():
    with pytest.raises(ElementSpecError, match="未知键"):
        ElementSpec.from_dict({"name": "x", "typo": 1})


# ---------------------------------------------------------------------------
# 运行时多候选探测：稳定性的实际收益
# ---------------------------------------------------------------------------


def test_primary_candidate_wins_when_present():
    page = FakePage()
    page.register("label=用户名")
    page.register("test_id=login-username")
    elements = {
        "username": _element(
            LocatorSpec("label", "用户名"),
            LocatorSpec("test_id", "login-username"),
            name="username",
        )
    }
    events: list = []

    resolved = resolve_element(page, "username", elements=elements, sink=events.append)

    assert resolved.index == 0
    assert not resolved.fallback_used
    assert [e.outcome for e in events] == ["primary"]


def test_falls_back_to_backup_candidate_and_emits_event():
    """首选失效时测试不该红 —— 这就是「多定位器备用」的核心收益。"""
    page = FakePage()
    page.register("test_id=login-username")  # 只注册备用候选
    elements = {
        "username": _element(
            LocatorSpec("label", "用户名"),
            LocatorSpec("test_id", "login-username"),
            name="username",
        )
    }
    events: list = []

    resolved = resolve_element(page, "username", elements=elements, sink=events.append)

    assert resolved.index == 1
    assert resolved.fallback_used
    assert resolved.spec.strategy == "test_id"
    event = events[0]
    assert event.outcome == "fallback"
    assert event.used_index == 1
    assert event.preferred.startswith("label=")
    assert len(event.candidates) == 2


def test_all_candidates_missing_raises_with_full_diagnosis():
    page = FakePage()
    elements = {
        "username": _element(
            LocatorSpec("label", "用户名"),
            LocatorSpec("test_id", "login-username"),
            name="username",
        )
    }
    events: list = []

    with pytest.raises(ElementNotFoundError) as excinfo:
        resolve_element(page, "username", elements=elements, sink=events.append)

    message = str(excinfo.value)
    assert "label='用户名'" in message
    assert "test_id='login-username'" in message
    assert events[0].outcome == "missing"


def test_scope_narrows_search_to_parent_container():
    page = FakePage()
    page.register("test_id=cart")
    page.register("test_id=cart > role=cell name=价格")
    elements = {
        "cart": _element(LocatorSpec("test_id", "cart"), name="cart"),
        "price_cell": _element(
            LocatorSpec("role", "cell", name="价格", scope="cart"), name="price_cell"
        ),
    }

    resolved = resolve_element(page, "price_cell", elements=elements)

    assert resolved.locator.key == "test_id=cart > role=cell name=价格"


def test_resolve_rejects_undeclared_element():
    with pytest.raises(ElementSpecError, match="未声明的元素"):
        resolve_element(FakePage(), "ghost", elements={})


def test_resolve_enforces_policy_at_runtime():
    page = FakePage()
    page.register("xpath=/html/body/input")
    elements = {
        "field": _element(
            LocatorSpec("xpath", "/html/body/input", confidence="fragile", note="录制"),
            name="field",
        )
    }
    with pytest.raises(LocatorPolicyError):
        resolve_element(page, "field", elements=elements)
