"""Action word 注册中心 — 装饰器注册、自动发现、目录导出。

``@register`` 在导入时校验模板硬约束（docstring / 元数据 / Params 类型），
更完整的规范（字段 description、example 可校验）由
``packages/tests/test_action_word_template.py`` 兜底。

``discover()`` 导入各类别子包下的全部模块，触发注册；CLI 与平台目录
导出前先调用它。
"""
from __future__ import annotations

import importlib
import pkgutil
from typing import Any, Iterable

from packages.action_words.base import ActionCategory, ActionWord

_REGISTRY: dict[str, type[ActionWord]] = {}

#: 存放 action word 实现模块的子包（按类别分目录）
_WORD_SUBPACKAGES = ("db_seed", "db_assert", "api_request", "api_assert", "ui_action", "ui_assert")


def register(cls: type[ActionWord]) -> type[ActionWord]:
    """注册一个 action word 类，同时校验模板硬约束。"""
    if not issubclass(cls, ActionWord):
        raise TypeError(f"{cls.__name__} 必须继承 ActionWord")
    word_id = getattr(cls, "word_id", None)
    if not word_id or not isinstance(word_id, str):
        raise ValueError(f"{cls.__name__} 缺少 word_id")
    if not getattr(cls, "name", None):
        raise ValueError(f"{word_id}: 缺少 name（中文业务名）")
    if not isinstance(getattr(cls, "category", None), ActionCategory):
        raise ValueError(f"{word_id}: category 必须是 ActionCategory")
    if not (cls.__doc__ or "").strip():
        raise ValueError(f"{word_id}: 必须有业务 docstring")
    if not word_id.startswith(f"{cls.category}."):
        raise ValueError(f"{word_id}: word_id 须以类别前缀开头，如 '{cls.category}.xxx'")
    existing = _REGISTRY.get(word_id)
    if existing is not None and existing is not cls:
        raise ValueError(f"word_id 重复注册: {word_id} ({existing.__name__} vs {cls.__name__})")
    _REGISTRY[word_id] = cls
    return cls


def get(word_id: str) -> type[ActionWord]:
    discover()
    cls = _REGISTRY.get(word_id)
    if cls is None:
        raise KeyError(f"未注册的 action word: {word_id}（已注册: {sorted(_REGISTRY)}）")
    return cls


def list_all() -> list[type[ActionWord]]:
    discover()
    return [_REGISTRY[k] for k in sorted(_REGISTRY)]


def iter_ids() -> Iterable[str]:
    discover()
    return sorted(_REGISTRY)


_discovered = False


def discover() -> None:
    """导入全部类别子包下的模块，触发 ``@register`` 副作用。幂等。"""
    global _discovered
    if _discovered:
        return
    _discovered = True
    import packages.action_words as root_pkg

    for sub in _WORD_SUBPACKAGES:
        try:
            pkg = importlib.import_module(f"{root_pkg.__name__}.{sub}")
        except ModuleNotFoundError:
            continue  # 预留类别（如 ui_action）尚未建目录
        for mod_info in pkgutil.iter_modules(pkg.__path__):
            importlib.import_module(f"{pkg.__name__}.{mod_info.name}")


def export_catalog() -> list[dict[str, Any]]:
    """导出全量目录（元数据 + docstring + 入参 schema + 样例），供本机 CLI。"""
    return [cls.describe() for cls in list_all()]


def reset_registry_for_tests() -> None:
    """Test helper: clear word registration so discover can run again."""
    global _discovered
    _REGISTRY.clear()
    _discovered = False
