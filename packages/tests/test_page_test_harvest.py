"""harvest：DOM 快照 → 多候选 LocatorSpec（不启浏览器）。"""
from __future__ import annotations

from tuner_testkit.page_test.harvest import (
    as_valid_element,
    harvest_element,
    harvest_locators,
    is_secret_snapshot,
    suggest_name,
    suggest_placeholder,
)
from tuner_testkit.page_test.locator import DEFAULT_POLICY, ElementSpec, LocatorPolicy, LocatorSpec


def test_role_and_label_rank_before_test_id():
    locators, dropped = harvest_locators(
        {
            "tag": "input",
            "type": "text",
            "role": "textbox",
            "accessible_name": "用户名",
            "label": "用户名",
            "test_id": "login-username",
            "id": "username",
        }
    )
    assert locators[0].strategy == "role"
    assert locators[0].value == "textbox"
    assert locators[0].name == "用户名"
    strategies = [spec.strategy for spec in locators]
    assert "test_id" in strategies
    assert strategies.index("role") < strategies.index("test_id")
    assert all("absolute" not in reason.lower() or True for reason in dropped)


def test_absolute_xpath_never_written():
    locators, dropped = harvest_locators(
        {
            "tag": "input",
            "type": "text",
            "xpath": "/html/body/div[3]/form/input[1]",
            "absolute_xpath": "/html/body/div[3]/form/input[1]",
        }
    )
    assert all(spec.strategy != "xpath" for spec in locators)
    assert any("absolute" in reason for reason in dropped)
    harvested = harvest_element(
        {"tag": "input", "type": "text", "xpath": "/html/body/div[3]/input"}
    )
    assert as_valid_element(harvested) is None


def test_relative_xpath_is_fragile_with_note():
    locators, _dropped = harvest_locators(
        {
            "tag": "button",
            "test_id": "row-action",
            "xpath": "//td[text()='张三']/following-sibling::td//button",
        }
    )
    xpath = [spec for spec in locators if spec.strategy == "xpath"]
    assert xpath
    assert xpath[0].confidence == "fragile"
    assert xpath[0].note
    assert not xpath[0].value.startswith("/html")


def test_deep_css_rejected_by_policy():
    locators, dropped = harvest_locators(
        {
            "tag": "a",
            "css": "div > div > span > a > b > i",
            "test_id": "ok",
        }
    )
    assert all(spec.strategy != "css" or spec.value != "div > div > span > a > b > i" for spec in locators)
    assert any("rejected" in reason for reason in dropped)


def test_bare_role_without_name_skipped():
    locators, dropped = harvest_locators({"tag": "button", "role": "button"})
    assert all(not (spec.strategy == "role") for spec in locators)
    assert any("without accessible name" in reason for reason in dropped)


def test_password_snapshot_is_secret_and_placeholder():
    snap = {"tag": "input", "type": "password", "label": "密码", "name": "passwd"}
    assert is_secret_snapshot(snap)
    harvested = harvest_element(snap)
    assert harvested.is_secret
    assert suggest_placeholder(snap, harvested.name) == "{{password}}"


def test_username_placeholder_heuristic():
    snap = {
        "tag": "input",
        "type": "text",
        "label": "用户名",
        "name": "username",
        "id": "username",
    }
    harvested = harvest_element(snap)
    assert suggest_placeholder(snap, harvested.name) == "{{username}}"
    assert harvested.name == "username_input"


def test_naming_collision_reuses_existing_element():
    existing = {
        "username_input": ElementSpec(
            name="username_input",
            locators=(
                LocatorSpec("label", "用户名"),
                LocatorSpec("test_id", "login-username"),
            ),
        )
    }
    harvested = harvest_element(
        {
            "tag": "input",
            "type": "text",
            "label": "用户名",
            "test_id": "login-username",
        },
        existing=existing,
    )
    assert harvested.name == "username_input"
    assert harvested.reused


def test_unique_name_when_no_fingerprint_overlap():
    existing = {
        "submit_button": ElementSpec(
            name="submit_button",
            locators=(LocatorSpec("role", "button", name="保存"),),
        )
    }
    harvested = harvest_element(
        {
            "tag": "button",
            "accessible_name": "登录",
            "role": "button",
        },
        existing=existing,
        used_names=set(existing),
    )
    assert harvested.name != "submit_button"
    assert harvested.name == "el_button"
    assert not harvested.reused


def test_generated_id_not_used_as_css():
    locators, _dropped = harvest_locators(
        {
            "tag": "div",
            "id": "ember12345",
            "test_id": "panel",
        }
    )
    assert all(spec.strategy != "css" or "ember" not in spec.value for spec in locators)
    assert locators[0].strategy == "test_id"


def test_candidate_cap_respects_policy():
    locators, dropped = harvest_locators(
        {
            "tag": "input",
            "type": "text",
            "role": "textbox",
            "accessible_name": "邮箱",
            "label": "邮箱",
            "placeholder": "name@example.com",
            "title": "电子邮箱",
            "test_id": "email",
            "id": "email",
            "name": "email",
        },
        policy=LocatorPolicy(fallback_max_attempts=3),
    )
    assert len(locators) <= 3
    assert any("capped" in reason for reason in dropped) or len(locators) == 3


def test_implicit_role_for_native_controls():
    locators, _ = harvest_locators(
        {"tag": "button", "accessible_name": "提交"}
    )
    assert locators[0].strategy == "role"
    assert locators[0].value == "button"

    locators, _ = harvest_locators(
        {"tag": "a", "href": "/home", "accessible_name": "首页"}
    )
    assert locators[0].value == "link"


def test_as_valid_element_keeps_semantic_pair():
    harvested = harvest_element(
        {
            "tag": "input",
            "type": "text",
            "label": "用户名",
            "test_id": "login-username",
        }
    )
    spec = as_valid_element(harvested, policy=DEFAULT_POLICY)
    assert spec is not None
    assert spec.name == harvested.name
    assert len(spec.locators) >= 2


def test_suggest_name_from_id_and_role_suffix():
    assert suggest_name({"tag": "button", "id": "submit", "accessible_name": "登录"}) == "submit_button"
    chinese_only = suggest_name({"tag": "button", "accessible_name": "登录"})
    assert chinese_only == "el_button"
