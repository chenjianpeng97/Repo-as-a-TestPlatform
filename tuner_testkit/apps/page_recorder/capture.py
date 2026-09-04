"""一次用户事件 → 脱敏后的 Capture（真值不进对象）。"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urlsplit

from tuner_testkit.page_test.harvest import (
    HarvestedElement,
    harvest_element,
    suggest_placeholder,
)
from tuner_testkit.page_test.locator import ElementSpec, LocatorPolicy
from tuner_testkit.page_test.model import normalize_url_path
from tuner_testkit.page_test.steps import (
    Check,
    Click,
    Fill,
    Press,
    Select,
    Step,
    WaitForUrl,
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_CLICKABLE_INPUT = frozenset({"button", "submit", "reset", "image", "file"})


@dataclass(frozen=True)
class Capture:
    """直播冻结的一条记录。``step`` 为 None 表示只扩元素表（``--scan``）。"""

    url_path: str
    host: str
    event: str
    page_slug: str
    element: HarvestedElement | None = None
    step: Step | None = None


def url_path_from_url(url: str) -> str:
    """``https://host/projects/42/issues`` → ``/projects/{id}/issues``。"""
    parts = urlsplit(url or "")
    path = parts.path or "/"
    if not path.startswith("/"):
        path = "/" + path
    return normalize_url_path(path)


def host_from_url(url: str) -> str:
    return (urlsplit(url or "").netloc or "").lower()


def page_slug_from_path(url_path: str) -> str:
    """``/sign-in`` → ``sign_in``；``/`` → ``home``。"""
    segs = []
    for segment in (url_path or "/").split("/"):
        if not segment:
            continue
        cleaned = segment.replace("{", "").replace("}", "")
        cleaned = _SLUG_RE.sub("_", cleaned.lower()).strip("_")
        if cleaned:
            segs.append(cleaned)
    slug = "_".join(segs)[:60] or "home"
    if slug[0].isdigit():
        slug = "p_" + slug
    return slug


def _tag(snapshot: Mapping[str, Any]) -> str:
    return str(snapshot.get("tag") or "").strip().lower()


def _input_type(snapshot: Mapping[str, Any]) -> str:
    return str(snapshot.get("type") or "").strip().lower()


def _skip_click(snapshot: Mapping[str, Any]) -> bool:
    tag = _tag(snapshot)
    if tag in {"textarea", "select", "option"}:
        return True
    if tag == "input" and _input_type(snapshot) not in _CLICKABLE_INPUT:
        return True
    return False


def step_from_event(
    *,
    kind: str,
    snapshot: Mapping[str, Any],
    harvested: HarvestedElement,
    extra: Mapping[str, Any] | None = None,
    url_path: str = "",
) -> Step | None:
    """把页面事件编成声明式 step；Fill 值当场换成占位符。"""
    extra = extra or {}
    name = harvested.name
    kind = (kind or "").strip().lower()

    if kind in {"scan", "harvest"}:
        return None
    if kind == "navigate":
        pattern = str(extra.get("pattern") or url_path or "")
        if not pattern:
            return None
        return WaitForUrl(pattern)
    if kind == "press":
        key = str(extra.get("key") or "Enter")
        return Press(name, key)
    if kind == "click":
        if _skip_click(snapshot):
            return None
        return Click(name)

    if kind in {"change", "input", "fill"}:
        tag = _tag(snapshot)
        input_type = _input_type(snapshot)
        if tag == "select" or harvested.role_hint in {"combobox", "listbox"}:
            option = extra.get("select_label") or extra.get("select_value") or extra.get("value")
            placeholder = suggest_placeholder(snapshot, name)
            # 选项文案本身不是密码；占位符仍避免把真实选项冻进源码
            _ = option
            return Select(name, placeholder, by="label")
        if tag == "input" and input_type in {"checkbox", "radio"}:
            checked = extra.get("checked")
            if checked is None:
                checked = snapshot.get("checked")
            return Check(name, checked=bool(checked if checked is not None else True))
        placeholder = suggest_placeholder(snapshot, name)
        return Fill(name, placeholder, secret=harvested.is_secret)

    if kind == "check":
        return Check(name, checked=bool(extra.get("checked", True)))
    if kind == "select":
        return Select(name, suggest_placeholder(snapshot, name), by="label")
    if kind == "submit":
        if _skip_click(snapshot):
            return None
        return Click(name)
    return None


def build_capture(
    payload: Mapping[str, Any],
    *,
    existing: Mapping[str, ElementSpec] | None = None,
    used_names: set[str] | None = None,
    policy: LocatorPolicy | None = None,
    url: str | None = None,
) -> Capture | None:
    """页面 binding 送来的 payload → 脱敏 Capture。无法收获定位器时返回 None。"""
    kind = str(payload.get("kind") or payload.get("event") or "").strip().lower()
    page_url = str(url or payload.get("url") or "")
    url_path = url_path_from_url(page_url)
    host = host_from_url(page_url)
    slug = page_slug_from_path(url_path)

    extra = {
        k: payload.get(k)
        for k in ("value", "checked", "select_label", "select_value", "key", "pattern")
        if payload.get(k) is not None
    }

    if kind == "navigate":
        pattern = str(payload.get("pattern") or url_path)
        return Capture(
            url_path=url_path,
            host=host,
            event="navigate",
            page_slug=slug,
            step=WaitForUrl(pattern) if pattern else None,
        )

    snapshot = payload.get("snapshot") or {}
    if not isinstance(snapshot, Mapping):
        snapshot = {}
    if not snapshot:
        return None

    harvested = harvest_element(
        snapshot,
        policy=policy,
        existing=existing,
        used_names=used_names,
    )
    if not harvested.locators:
        return None

    step = step_from_event(
        kind=kind,
        snapshot=snapshot,
        harvested=harvested,
        extra=extra,
        url_path=url_path,
    )
    event = kind or "scan"
    return Capture(
        url_path=url_path,
        host=host,
        event=event,
        page_slug=slug,
        element=harvested,
        step=step,
    )


__all__ = [
    "Capture",
    "build_capture",
    "host_from_url",
    "page_slug_from_path",
    "step_from_event",
    "url_path_from_url",
]
