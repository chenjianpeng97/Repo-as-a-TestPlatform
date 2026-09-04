"""DOM 快照 → 按 locator_policy 排序的多候选 ``LocatorSpec``。

供 ``apps.page_recorder`` 在 headed 浏览器里把人工点击冻成 ``PageModel``；
本模块**不启浏览器**，单测直接喂 dict。绝对 XPath 在这里就被丢掉，不会进入资产。

快照是 JSON-able dict（由页面脚本采集），约定键：

``tag`` / ``type`` / ``role`` / ``accessible_name`` / ``label`` / ``placeholder`` /
``title`` / ``alt`` / ``test_id`` / ``id`` / ``name`` / ``classes`` / ``text`` /
``checked`` / ``href`` / ``xpath`` / ``css`` / ``parent_scope`` / ``parent_test_id``
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from .locator import (
    DEFAULT_POLICY,
    ElementSpec,
    LocatorPolicy,
    LocatorSpec,
    is_absolute_xpath,
    validate_element,
    validate_locator,
)
from .errors import ElementSpecError, LocatorPolicyError
from .steps import SENSITIVE_RE

#: HTML 标签/type → ARIA 隐式 role（HTML-AAM 的常用子集）
_TAG_ROLES: dict[str, str] = {
    "button": "button",
    "a": "link",
    "textarea": "textbox",
    "select": "combobox",
    "option": "option",
    "img": "img",
    "nav": "navigation",
    "main": "main",
    "dialog": "dialog",
    "td": "cell",
    "th": "columnheader",
    "tr": "row",
    "li": "listitem",
    "ul": "list",
    "ol": "list",
    "h1": "heading",
    "h2": "heading",
    "h3": "heading",
    "h4": "heading",
    "h5": "heading",
    "h6": "heading",
}

_INPUT_ROLES: dict[str, str] = {
    "button": "button",
    "submit": "button",
    "reset": "button",
    "image": "button",
    "checkbox": "checkbox",
    "radio": "radio",
    "text": "textbox",
    "email": "textbox",
    "tel": "textbox",
    "url": "textbox",
    "password": "textbox",
    "search": "searchbox",
    "number": "spinbutton",
    "file": "button",
}

#: role_hint → 元素名后缀
_ROLE_SUFFIX: dict[str, str] = {
    "textbox": "input",
    "searchbox": "input",
    "spinbutton": "input",
    "button": "button",
    "link": "link",
    "checkbox": "checkbox",
    "radio": "radio",
    "combobox": "select",
    "listbox": "select",
    "option": "option",
    "img": "image",
    "heading": "heading",
    "cell": "cell",
    "row": "row",
    "tab": "tab",
    "menuitem": "menuitem",
    "switch": "switch",
    "dialog": "dialog",
    "navigation": "nav",
}

_RESERVED_NAMES = frozenset(
    {
        "open",
        "run",
        "id",
        "name",
        "elements",
        "flows",
        "page",
        "self",
        "model",
        "driver",
    }
)

_GENERATED_CLASS_RE = re.compile(
    r"^(css-|sc-|mui[a-z]*-|makestyles-|jss\d+|_[a-zA-Z0-9]{6,})",
    re.I,
)
_HASH_ID_RE = re.compile(
    r"^(ember\d+|react-aria-[\w-]+|[0-9a-f]{8,}|[a-z]?\d{6,})$",
    re.I,
)
_USER_RE = re.compile(r"(user(name)?|login|email|account|账号|用户)", re.I)
_SLUG_RE = re.compile(r"[^a-z0-9]+")
_XPATH_NOTE = "harvested relative xpath; prefer role/test_id (absolute xpath is never written)"


def _s(snapshot: Mapping[str, Any], key: str) -> str:
    value = snapshot.get(key)
    if value is None:
        return ""
    return str(value).strip()


def implicit_role(snapshot: Mapping[str, Any]) -> str:
    """显式 ``role`` 优先，否则按标签/type 推断隐式 ARIA role。"""
    explicit = _s(snapshot, "role").lower()
    if explicit and explicit not in ("none", "presentation", "generic"):
        return explicit
    tag = _s(snapshot, "tag").lower()
    if tag == "input":
        input_type = _s(snapshot, "type").lower() or "text"
        return _INPUT_ROLES.get(input_type, "textbox")
    if tag == "a" and not _s(snapshot, "href"):
        return ""
    return _TAG_ROLES.get(tag, "")


def role_hint_of(snapshot: Mapping[str, Any]) -> str:
    return implicit_role(snapshot) or _s(snapshot, "tag").lower() or "element"


def is_secret_snapshot(snapshot: Mapping[str, Any], *extra: str) -> bool:
    """密码框或键名命中敏感启发式。"""
    if _s(snapshot, "type").lower() == "password":
        return True
    if snapshot.get("is_password") is True:
        return True
    blob = " ".join(
        filter(
            None,
            (
                _s(snapshot, "name"),
                _s(snapshot, "id"),
                _s(snapshot, "test_id"),
                _s(snapshot, "label"),
                _s(snapshot, "accessible_name"),
                _s(snapshot, "placeholder"),
                *extra,
            ),
        )
    )
    return bool(SENSITIVE_RE.search(blob))


def locator_fingerprint(spec: LocatorSpec) -> tuple[str, str, str, str]:
    """去重键：策略 + 值 + 可访问名 + has_text。"""
    return (spec.strategy, spec.value, spec.name or "", spec.has_text or "")


def _looks_generated_id(value: str) -> bool:
    if not value or len(value) > 64:
        return True
    return bool(_HASH_ID_RE.match(value))


def _looks_generated_class(value: str) -> bool:
    if not value or len(value) > 48:
        return True
    if _GENERATED_CLASS_RE.match(value):
        return True
    # 单段哈希 class（emotion 无前缀的短哈希）
    if re.fullmatch(r"[a-z]{5,8}\d{1,4}", value, re.I):
        return True
    return False


def _css_escape_ident(value: str) -> str | None:
    if re.fullmatch(r"[a-zA-Z_][\w-]*", value):
        return value
    return None


def _try_locator(spec: LocatorSpec, *, policy: LocatorPolicy) -> LocatorSpec | None:
    try:
        validate_locator(spec, policy=policy)
    except (LocatorPolicyError, ElementSpecError):
        return None
    return spec


def _dedupe(specs: Sequence[LocatorSpec]) -> list[LocatorSpec]:
    seen: set[tuple[str, str, str, str]] = set()
    out: list[LocatorSpec] = []
    for spec in specs:
        key = locator_fingerprint(spec)
        if key in seen:
            continue
        seen.add(key)
        out.append(spec)
    return out


def _scope_name(
    snapshot: Mapping[str, Any],
    existing: Mapping[str, ElementSpec] | None,
) -> str | None:
    if not existing:
        return None
    declared = _s(snapshot, "parent_scope")
    if declared and declared in existing:
        return declared
    parent_test_id = _s(snapshot, "parent_test_id")
    if not parent_test_id:
        return None
    for name, element in existing.items():
        for loc in element.locators:
            if loc.strategy == "test_id" and loc.value == parent_test_id:
                return name
    return None


def harvest_locators(
    snapshot: Mapping[str, Any],
    *,
    policy: LocatorPolicy | None = None,
    existing: Mapping[str, ElementSpec] | None = None,
) -> tuple[tuple[LocatorSpec, ...], tuple[str, ...]]:
    """按规范优先级产出候选；返回 ``(accepted, dropped_reasons)``。

    顺序：role+name → label/placeholder/title/alt → test_id → 短 CSS → 相对 XPath。
    绝对 XPath、超长 CSS、无 name 的裸 role、无 note 的 fragile 都进 ``dropped``。
    """
    policy = policy or DEFAULT_POLICY
    dropped: list[str] = []
    candidates: list[LocatorSpec] = []
    scope = _scope_name(snapshot, existing)

    def accept(spec: LocatorSpec) -> None:
        ok = _try_locator(spec, policy=policy)
        if ok is None:
            dropped.append(f"rejected {spec.signature()}")
            return
        candidates.append(ok)

    role = implicit_role(snapshot)
    accessible = _s(snapshot, "accessible_name") or _s(snapshot, "label")
    if role and accessible:
        accept(LocatorSpec("role", role, name=accessible))
    elif role and not accessible:
        dropped.append(f"skipped role={role!r} without accessible name")

    label = _s(snapshot, "label")
    if label:
        accept(LocatorSpec("label", label))

    placeholder = _s(snapshot, "placeholder")
    if placeholder:
        accept(LocatorSpec("placeholder", placeholder))

    title = _s(snapshot, "title")
    if title:
        accept(LocatorSpec("title", title))

    alt = _s(snapshot, "alt")
    if alt:
        accept(LocatorSpec("alt_text", alt))

    # 纯 get_by_text 不作候选：多语言会全线失效。文本只作为 role 的 name。

    test_id = _s(snapshot, "test_id")
    if test_id:
        accept(LocatorSpec("test_id", test_id))

    html_id = _s(snapshot, "id")
    css_emitted = False
    if html_id and not _looks_generated_id(html_id):
        ident = _css_escape_ident(html_id)
        if ident:
            spec = LocatorSpec("css", f"#{ident}", scope=scope)
            accept(spec)
            css_emitted = True

    html_name = _s(snapshot, "name")
    tag = _s(snapshot, "tag").lower() or "*"
    if html_name and re.fullmatch(r"[\w.:-]+", html_name):
        accept(LocatorSpec("css", f'{tag}[name="{html_name}"]', scope=scope))
        css_emitted = True

    provided_css = _s(snapshot, "css")
    if provided_css and not provided_css.lower().startswith(("html", "body", "/")):
        accept(LocatorSpec("css", provided_css, scope=scope))
        css_emitted = True

    if not css_emitted:
        classes = snapshot.get("classes") or ()
        if isinstance(classes, str):
            classes = classes.split()
        semantic = [
            c for c in classes if isinstance(c, str) and not _looks_generated_class(c) and len(c) >= 3
        ]
        if semantic and _css_escape_ident(semantic[0]) and tag != "*":
            cls = _css_escape_ident(semantic[0])
            accept(LocatorSpec("css", f"{tag}.{cls}", scope=scope, confidence="fragile", note="class selector harvested; prefer role/test_id"))

    xpath = _s(snapshot, "xpath") or _s(snapshot, "absolute_xpath")
    if xpath:
        if is_absolute_xpath(xpath):
            dropped.append(f"absolute xpath discarded: {xpath}")
        else:
            accept(
                LocatorSpec(
                    "xpath",
                    xpath,
                    scope=scope,
                    confidence="fragile",
                    note=_XPATH_NOTE,
                )
            )
    elif html_name and len(candidates) < 2:
        accept(
            LocatorSpec(
                "xpath",
                f"//{tag}[@name={html_name!r}]",
                scope=scope,
                confidence="fragile",
                note=_XPATH_NOTE,
            )
        )

    unique = _dedupe(candidates)
    capped = unique[: policy.fallback_max_attempts]
    if len(unique) > len(capped):
        dropped.append(
            f"capped at fallback_max_attempts={policy.fallback_max_attempts}"
        )
    return tuple(capped), tuple(dropped)


def _ascii_slug(text: str, *, max_len: int = 40) -> str:
    lowered = text.strip().lower()
    slug = _SLUG_RE.sub("_", lowered).strip("_")
    return slug[:max_len]


def suggest_name(
    snapshot: Mapping[str, Any],
    *,
    used_names: set[str] | None = None,
) -> str:
    """启发式元素名：``username_input`` / ``submit_button``。"""
    suffix = _ROLE_SUFFIX.get(role_hint_of(snapshot), "el")
    for key in ("test_id", "name", "id", "accessible_name", "label", "placeholder"):
        slug = _ascii_slug(_s(snapshot, key))
        if slug and slug[0].isalpha() and not _looks_generated_id(_s(snapshot, key) if key in ("id", "test_id") else slug):
            base = slug
            break
    else:
        base = ""

    if base in _RESERVED_NAMES:
        base = f"el_{base}"
    if base and base[0].isdigit():
        base = f"el_{base}"

    if not base:
        name = f"el_{suffix}"
    elif base == suffix or base.endswith(f"_{suffix}"):
        name = base
    else:
        name = f"{base}_{suffix}"

    used = used_names or set()
    if name not in used:
        return name
    index = 2
    while f"{name}_{index}" in used:
        index += 1
    return f"{name}_{index}"


def suggest_placeholder(snapshot: Mapping[str, Any], element_name: str = "") -> str:
    """Fill 值占位符。密码/敏感键 → ``{{password}}``；用户名启发式 → ``{{username}}``。"""
    if is_secret_snapshot(snapshot, element_name):
        return "{{password}}"
    blob = " ".join(filter(None, (element_name, _s(snapshot, "name"), _s(snapshot, "id"), _s(snapshot, "test_id"), _s(snapshot, "label"), _s(snapshot, "accessible_name"))))
    if _USER_RE.search(blob):
        return "{{username}}"
    param = element_name
    for ending in ("_input", "_select", "_checkbox", "_radio", "_button"):
        if param.endswith(ending):
            param = param[: -len(ending)]
            break
    param = _ascii_slug(param) or "value"
    if param[0].isdigit():
        param = f"v_{param}"
    return "{{" + param + "}}"


def match_existing_name(
    locators: Sequence[LocatorSpec],
    existing: Mapping[str, ElementSpec] | None,
) -> str | None:
    """定位器指纹有交集则复用已有元素名。"""
    if not existing or not locators:
        return None
    incoming = {locator_fingerprint(spec) for spec in locators}
    best_name: str | None = None
    best_overlap = 0
    for name, element in existing.items():
        overlap = incoming & {locator_fingerprint(spec) for spec in element.locators}
        if len(overlap) > best_overlap:
            best_overlap = len(overlap)
            best_name = name
    return best_name if best_overlap else None


@dataclass(frozen=True)
class HarvestedElement:
    """一次采集的元素：建议名 + 已过 policy 的候选。"""

    name: str
    locators: tuple[LocatorSpec, ...]
    description: str = ""
    role_hint: str = ""
    dropped: tuple[str, ...] = ()
    is_secret: bool = False
    reused: bool = False

    def to_element_spec(self) -> ElementSpec:
        return ElementSpec(
            name=self.name,
            description=self.description,
            role_hint=self.role_hint,
            locators=self.locators,
        )


def harvest_element(
    snapshot: Mapping[str, Any],
    *,
    policy: LocatorPolicy | None = None,
    existing: Mapping[str, ElementSpec] | None = None,
    used_names: set[str] | None = None,
) -> HarvestedElement:
    """快照 → 命名后的 ``HarvestedElement``。指纹撞上已有元素则复用名字。"""
    policy = policy or DEFAULT_POLICY
    locators, dropped = harvest_locators(snapshot, policy=policy, existing=existing)
    reused_name = match_existing_name(locators, existing)
    used = set(used_names or ())
    if existing:
        used.update(existing)
    if reused_name:
        name = reused_name
        reused = True
    else:
        name = suggest_name(snapshot, used_names=used)
        reused = False

    accessible = _s(snapshot, "accessible_name") or _s(snapshot, "label") or _s(snapshot, "placeholder")
    role_hint = role_hint_of(snapshot)
    description = accessible or f"harvested {role_hint}"
    return HarvestedElement(
        name=name,
        locators=locators,
        description=description[:120],
        role_hint=role_hint,
        dropped=dropped,
        is_secret=is_secret_snapshot(snapshot, name),
        reused=reused,
    )


def as_valid_element(
    harvested: HarvestedElement,
    *,
    policy: LocatorPolicy | None = None,
) -> ElementSpec | None:
    """过不了 ``validate_element`` 的候选整组丢掉（freeze 时 log_warn）。"""
    policy = policy or DEFAULT_POLICY
    if not harvested.locators:
        return None
    spec = harvested.to_element_spec()
    try:
        validate_element(spec, policy=policy)
        return spec
    except (LocatorPolicyError, ElementSpecError):
        stables = tuple(loc for loc in spec.locators if loc.confidence == "stable")
        if not stables:
            return None
        trimmed = replace(spec, locators=stables)
        try:
            validate_element(trimmed, policy=policy)
            return trimmed
        except (LocatorPolicyError, ElementSpecError):
            return None


__all__ = [
    "HarvestedElement",
    "as_valid_element",
    "harvest_element",
    "harvest_locators",
    "implicit_role",
    "is_secret_snapshot",
    "locator_fingerprint",
    "match_existing_name",
    "role_hint_of",
    "suggest_name",
    "suggest_placeholder",
]
