"""资产发现：两种范式统一封装、坏模块不拖垮扫描、非资产模块不入目录。"""
from __future__ import annotations

import pytest

from packages.page_test import registry
from packages.page_test.base import BasePage
from packages.page_test.errors import PageTestError
from packages.page_test.locator import ElementSpec, LocatorSpec

DECLARATIVE_ASSET = '''\
"""示例登录页（测试夹具）。"""

from packages.page_test import (
    AssertVisible,
    Click,
    ElementSpec,
    Fill,
    LocatorSpec,
    PageFlow,
    PageModel,
    WaitForElement,
)

fixture_login_page_v1 = PageModel(
    id="fixture.login@v1",
    name="示例登录页",
    description="registry 发现测试用",
    url_path="/login",
    elements={
        "username_input": ElementSpec(
            name="username_input",
            locators=(
                LocatorSpec("label", "用户名"),
                LocatorSpec("test_id", "login-username"),
            ),
        ),
        "submit_button": ElementSpec(
            name="submit_button",
            locators=(LocatorSpec("role", "button", name="登录"),),
        ),
        "welcome_banner": ElementSpec(
            name="welcome_banner", locators=(LocatorSpec("test_id", "welcome"),)
        ),
    },
    inputs_schema={"username": {"type": "string", "required": True}},
    ready=(WaitForElement("username_input", state="visible"),),
    flows={
        "login": PageFlow(
            name="login",
            steps=(
                Fill("username_input", "{{username}}"),
                Click("submit_button"),
                AssertVisible("welcome_banner"),
            ),
            example_params={"username": "demo"},
        )
    },
)
'''

CLASS_ASSET = '''\
"""示例列表页（测试夹具）。"""

from packages.page_test import BasePage, ElementSpec, LocatorSpec


class FixtureListPage(BasePage):
    """列表页夹具，验证类范式也能被发现。"""

    page_id = "fixture.list@v1"
    name = "示例列表页"
    url_path = "/items"
    elements = {
        "row": ElementSpec(name="row", locators=(LocatorSpec("test_id", "row"),)),
    }
'''

BROKEN_ASSET = "raise RuntimeError('这个模块坏了')\n"


@pytest.fixture
def asset_root(tmp_path, monkeypatch):
    root = tmp_path / "page_objects"
    root.mkdir()
    monkeypatch.setattr(registry, "page_objects_root", lambda: root)
    registry.reset_registry_for_tests()
    yield root
    registry.reset_registry_for_tests()


def test_discovers_declarative_and_class_assets(asset_root):
    (asset_root / "fixture_login.py").write_text(DECLARATIVE_ASSET, encoding="utf-8")
    (asset_root / "fixture_list.py").write_text(CLASS_ASSET, encoding="utf-8")

    assert registry.discover() == []
    assert sorted(registry.iter_ids()) == ["fixture.list@v1", "fixture.login@v1"]

    declarative = registry.get("fixture.login@v1")
    assert declarative.kind == "page_model"
    assert declarative.variable == "fixture_login_page_v1"
    assert declarative.model.url_path == "/login"

    class_based = registry.get("fixture.list@v1")
    assert class_based.kind == "page_class"
    assert class_based.page_class is not None


def test_broken_module_is_skipped_without_breaking_the_scan(asset_root):
    (asset_root / "fixture_login.py").write_text(DECLARATIVE_ASSET, encoding="utf-8")
    (asset_root / "fixture_broken.py").write_text(BROKEN_ASSET, encoding="utf-8")

    problems = registry.discover()

    assert any("fixture_broken.py" in p for p in problems)
    assert "fixture.login@v1" in registry.iter_ids()
    assert "<import>" in registry.validate_all()


def test_helper_modules_are_not_treated_as_assets(asset_root):
    (asset_root / "session.py").write_text(BROKEN_ASSET, encoding="utf-8")
    (asset_root / "plane.py").write_text(BROKEN_ASSET, encoding="utf-8")
    (asset_root / "__init__.py").write_text(BROKEN_ASSET, encoding="utf-8")

    assert registry.discover() == []
    assert list(registry.iter_ids()) == []


def test_page_classes_outside_asset_package_are_ignored(asset_root):
    """单测夹具与临时试验类不该出现在平台目录里。"""

    class LocalOnlyPage(BasePage):
        """定义在测试模块里的页面类。"""

        page_id = "local.only@v1"
        name = "本地类"
        elements = {
            "row": ElementSpec(name="row", locators=(LocatorSpec("test_id", "row"),))
        }

    registry.discover(force=True)

    assert "local.only@v1" not in registry.iter_ids()
    assert LocalOnlyPage.page_id == "local.only@v1"


def test_catalog_export_covers_both_paradigms(asset_root):
    (asset_root / "fixture_login.py").write_text(DECLARATIVE_ASSET, encoding="utf-8")
    (asset_root / "fixture_list.py").write_text(CLASS_ASSET, encoding="utf-8")

    catalog = registry.export_catalog()

    kinds = {entry["id"]: entry["kind"] for entry in catalog}
    assert kinds == {"fixture.login@v1": "page_model", "fixture.list@v1": "page_class"}
    login = next(e for e in catalog if e["id"] == "fixture.login@v1")
    assert login["module"].startswith("packages.page_objects")
    assert login["flows"][0]["name"] == "login"


def test_validate_all_reports_only_problematic_assets(asset_root):
    (asset_root / "fixture_login.py").write_text(DECLARATIVE_ASSET, encoding="utf-8")
    (asset_root / "fixture_bad.py").write_text(
        CLASS_ASSET.replace('page_id = "fixture.list@v1"', 'page_id = "BadId"').replace(
            "FixtureListPage", "FixtureBadPage"
        ),
        encoding="utf-8",
    )

    problems = registry.validate_all()

    assert "fixture.login@v1" not in problems
    assert any("page_slug" in item for items in problems.values() for item in items)


def test_get_unknown_asset_raises_with_available_ids(asset_root):
    with pytest.raises(PageTestError, match="未注册的页面资产"):
        registry.get("nope@v1")


def test_bind_returns_instance_for_class_and_bound_model_for_declarative(asset_root):
    (asset_root / "fixture_login.py").write_text(DECLARATIVE_ASSET, encoding="utf-8")
    (asset_root / "fixture_list.py").write_text(CLASS_ASSET, encoding="utf-8")
    sentinel = object()

    bound_model = registry.get("fixture.login@v1").bind(sentinel)
    assert bound_model._driver is sentinel

    instance = registry.get("fixture.list@v1").bind(sentinel)
    assert isinstance(instance, BasePage)
    assert instance.driver is sentinel
