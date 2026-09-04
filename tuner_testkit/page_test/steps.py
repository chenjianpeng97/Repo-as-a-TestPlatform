"""声明式 step 原语 —— 动作序列即数据。

每个 step 是 frozen dataclass，带 ``op`` 标识与 ``to_dict()`` / ``from_dict()``
双向序列化，因此同一份动作序列既能被驱动执行、又能被平台渲染成步骤表、
又能被 page recorder 生成，对齐 ``AssertOperation`` / ``ExtractVariableOperation``
在 ``tuner_testkit.api_test`` 里「断言与提取也是数据」的做法。

值支持 ``{{param}}`` 占位（以及 ``{{env:NAME}}`` 读环境变量），运行时才代入真值，
因此**资产源码里永不出现明文凭据**，与 ``tuner_testkit.api_objects.auth`` 的
``materialize_payload`` 同一思路。
"""
from __future__ import annotations

import os
import re
from dataclasses import MISSING, dataclass, fields
from typing import Any, ClassVar, Mapping

from .errors import ElementSpecError, StepExecutionError

#: 敏感键启发式：命中则日志里只记 ``***``
SENSITIVE_RE = re.compile(
    r"(token|secret|password|passwd|pwd|session|cookie|credential)", re.IGNORECASE
)

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
_FULL_PLACEHOLDER_RE = re.compile(r"^\{\{\s*([^{}]+?)\s*\}\}$")

TEXT_OPERATORS = ("eq", "contains", "not_contains", "matches")
COUNT_OPERATORS = ("eq", "gt", "gte", "lt", "lte")
ELEMENT_STATES = ("visible", "hidden", "attached", "detached", "enabled", "disabled")
SELECT_BY = ("label", "value", "index")

#: op -> Step 子类，由 ``__init_subclass__`` 自动登记，供 :func:`step_from_dict`
STEP_TYPES: dict[str, type["Step"]] = {}


def _lookup(token: str, params: Mapping[str, Any], *, where: str) -> Any:
    token = token.strip()
    if token.lower().startswith("env:"):
        name = token[4:].strip()
        value = os.getenv(name)
        if value is None:
            raise StepExecutionError(f"{where}: 环境变量 {name} 未设置")
        return value
    if token in params:
        return params[token]
    raise StepExecutionError(
        f"{where}: 未提供参数 {{{{{token}}}}}；已提供: {sorted(params)}"
    )


def resolve_value(value: Any, params: Mapping[str, Any], *, where: str = "step") -> Any:
    """代入 ``{{param}}`` 占位符。

    整串就是一个占位符时**保留原类型**（``"{{page_size}}"`` → ``10``）；
    嵌在文本里时按字符串拼接。
    """
    if not isinstance(value, str):
        return value
    full = _FULL_PLACEHOLDER_RE.match(value.strip())
    if full:
        return _lookup(full.group(1), params, where=where)
    return _PLACEHOLDER_RE.sub(
        lambda m: str(_lookup(m.group(1), params, where=where)), value
    )


def placeholders_in(value: Any) -> tuple[str, ...]:
    """列出值里引用的占位符名（``env:`` 前缀保留），供 flow 入参完整性校验。"""
    if not isinstance(value, str):
        return ()
    return tuple(m.group(1).strip() for m in _PLACEHOLDER_RE.finditer(value))


@dataclass(frozen=True)
class RetryPolicy:
    """step 级重试。只挂在幂等的定位/点击类 step 上，提交类默认不重试。"""

    attempts: int = 1
    backoff_ms: int = 200
    #: 触发重试的失败类别："locator" | "timeout" | "assert"
    on: tuple[str, ...] = ("locator", "timeout")

    def to_dict(self) -> dict[str, Any]:
        return {"attempts": self.attempts, "backoff_ms": self.backoff_ms, "on": list(self.on)}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RetryPolicy":
        payload = dict(data)
        if "on" in payload:
            payload["on"] = tuple(payload["on"])
        return cls(**payload)


@dataclass(frozen=True)
class Step:
    """所有 step 的基类。子类只声明数据字段，执行逻辑在 ``PageDriver``。"""

    op: ClassVar[str] = ""
    #: 导航 / 交互 / 等待 / 提取 / 断言 / 组合
    category: ClassVar[str] = ""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        op = cls.__dict__.get("op", "")
        if not op:
            return
        existing = STEP_TYPES.get(op)
        if existing is not None and existing is not cls:
            raise ElementSpecError(f"step op 重复注册: {op!r}")
        STEP_TYPES[op] = cls

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"op": type(self).op}
        for f in fields(self):
            value = getattr(self, f.name)
            if value is None:
                continue
            if f.default is not MISSING and value == f.default:
                continue
            if isinstance(value, RetryPolicy):
                out[f.name] = value.to_dict()
                continue
            if isinstance(value, tuple):
                out[f.name] = list(value)
                continue
            out[f.name] = value
        return out

    def elements_used(self) -> tuple[str, ...]:
        """本 step 引用的元素名，供 flow 引用完整性校验。"""
        name = getattr(self, "element", None)
        return (str(name),) if name else ()

    def flows_used(self) -> tuple[str, ...]:
        return ()

    def values_used(self) -> tuple[Any, ...]:
        """本 step 里可能含占位符的值。"""
        return ()

    def is_secret(self) -> bool:
        """本 step 的值是否需要在日志里脱敏。"""
        return False

    def describe(self) -> str:
        payload = self.to_dict()
        payload.pop("op", None)
        if not payload:
            return type(self).op
        parts = ", ".join(f"{k}={v!r}" for k, v in payload.items())
        return f"{type(self).op}({parts})"


# ---------------------------------------------------------------------------
# 导航
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Goto(Step):
    op: ClassVar[str] = "goto"
    category: ClassVar[str] = "navigate"

    #: 缺省用 ``PageModel.url_path``；给值时也必须是无 host 的路径
    path: str | None = None

    def values_used(self) -> tuple[Any, ...]:
        return (self.path,) if self.path else ()


@dataclass(frozen=True)
class GoBack(Step):
    op: ClassVar[str] = "go_back"
    category: ClassVar[str] = "navigate"


@dataclass(frozen=True)
class Reload(Step):
    op: ClassVar[str] = "reload"
    category: ClassVar[str] = "navigate"


# ---------------------------------------------------------------------------
# 交互
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Fill(Step):
    op: ClassVar[str] = "fill"
    category: ClassVar[str] = "interact"

    element: str
    value: Any
    #: 显式声明敏感；未声明时按元素名/占位符名启发式判断
    secret: bool = False

    def values_used(self) -> tuple[Any, ...]:
        return (self.value,)

    def is_secret(self) -> bool:
        if self.secret:
            return True
        return bool(SENSITIVE_RE.search(str(self.value)) or SENSITIVE_RE.search(self.element))


@dataclass(frozen=True)
class Click(Step):
    op: ClassVar[str] = "click"
    category: ClassVar[str] = "interact"

    element: str
    retry: RetryPolicy | None = None


@dataclass(frozen=True)
class Hover(Step):
    op: ClassVar[str] = "hover"
    category: ClassVar[str] = "interact"

    element: str
    retry: RetryPolicy | None = None


@dataclass(frozen=True)
class Check(Step):
    op: ClassVar[str] = "check"
    category: ClassVar[str] = "interact"

    element: str
    checked: bool = True
    retry: RetryPolicy | None = None


@dataclass(frozen=True)
class Select(Step):
    op: ClassVar[str] = "select"
    category: ClassVar[str] = "interact"

    element: str
    option: Any
    by: str = "label"

    def __post_init__(self) -> None:
        if self.by not in SELECT_BY:
            raise ElementSpecError(f"select by 必须是 {list(SELECT_BY)}，得到 {self.by!r}")

    def values_used(self) -> tuple[Any, ...]:
        return (self.option,)


@dataclass(frozen=True)
class Press(Step):
    op: ClassVar[str] = "press"
    category: ClassVar[str] = "interact"

    element: str
    key: str


@dataclass(frozen=True)
class Upload(Step):
    op: ClassVar[str] = "upload"
    category: ClassVar[str] = "interact"

    element: str
    #: 本地文件路径，通常写成 ``{{some_file}}`` 由运行时提供；文件内容永不冻结
    file: Any

    def values_used(self) -> tuple[Any, ...]:
        return (self.file,)


# ---------------------------------------------------------------------------
# 等待（只等条件成立，禁止固定 sleep）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WaitForElement(Step):
    op: ClassVar[str] = "wait_for_element"
    category: ClassVar[str] = "wait"

    element: str
    state: str = "visible"
    timeout_ms: int | None = None
    retry: RetryPolicy | None = None

    def __post_init__(self) -> None:
        if self.state not in ELEMENT_STATES:
            raise ElementSpecError(
                f"wait state 必须是 {list(ELEMENT_STATES)}，得到 {self.state!r}"
            )


@dataclass(frozen=True)
class WaitForUrl(Step):
    op: ClassVar[str] = "wait_for_url"
    category: ClassVar[str] = "wait"

    #: 子串或正则（以 ``re:`` 前缀声明正则）
    pattern: str
    timeout_ms: int | None = None

    def values_used(self) -> tuple[Any, ...]:
        return (self.pattern,)


@dataclass(frozen=True)
class WaitForResponse(Step):
    op: ClassVar[str] = "wait_for_response"
    category: ClassVar[str] = "wait"

    #: 与业务强相关的响应路径片段（不含 host）
    path_contains: str
    status: int = 200
    timeout_ms: int | None = None

    def values_used(self) -> tuple[Any, ...]:
        return (self.path_contains,)


# ---------------------------------------------------------------------------
# 提取
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExtractText(Step):
    op: ClassVar[str] = "extract_text"
    category: ClassVar[str] = "extract"

    element: str
    variable: str


@dataclass(frozen=True)
class ExtractAttribute(Step):
    op: ClassVar[str] = "extract_attribute"
    category: ClassVar[str] = "extract"

    element: str
    attribute: str
    variable: str


@dataclass(frozen=True)
class ExtractCount(Step):
    op: ClassVar[str] = "extract_count"
    category: ClassVar[str] = "extract"

    element: str
    variable: str


# ---------------------------------------------------------------------------
# 断言（内部轮询等待，吃 Playwright auto-wait）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AssertVisible(Step):
    op: ClassVar[str] = "assert_visible"
    category: ClassVar[str] = "assert"

    element: str
    timeout_ms: int | None = None


@dataclass(frozen=True)
class AssertHidden(Step):
    op: ClassVar[str] = "assert_hidden"
    category: ClassVar[str] = "assert"

    element: str
    timeout_ms: int | None = None


@dataclass(frozen=True)
class AssertText(Step):
    op: ClassVar[str] = "assert_text"
    category: ClassVar[str] = "assert"

    element: str
    expected: Any
    operator: str = "contains"
    timeout_ms: int | None = None

    def __post_init__(self) -> None:
        if self.operator not in TEXT_OPERATORS:
            raise ElementSpecError(
                f"assert_text operator 必须是 {list(TEXT_OPERATORS)}，得到 {self.operator!r}"
            )

    def values_used(self) -> tuple[Any, ...]:
        return (self.expected,)


@dataclass(frozen=True)
class AssertUrl(Step):
    op: ClassVar[str] = "assert_url"
    category: ClassVar[str] = "assert"

    pattern: str
    timeout_ms: int | None = None

    def values_used(self) -> tuple[Any, ...]:
        return (self.pattern,)


@dataclass(frozen=True)
class AssertCount(Step):
    op: ClassVar[str] = "assert_count"
    category: ClassVar[str] = "assert"

    element: str
    expected: Any
    operator: str = "eq"

    def __post_init__(self) -> None:
        if self.operator not in COUNT_OPERATORS:
            raise ElementSpecError(
                f"assert_count operator 必须是 {list(COUNT_OPERATORS)}，得到 {self.operator!r}"
            )

    def values_used(self) -> tuple[Any, ...]:
        return (self.expected,)


# ---------------------------------------------------------------------------
# 组合
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RunFlow(Step):
    op: ClassVar[str] = "run_flow"
    category: ClassVar[str] = "compose"

    flow: str

    def flows_used(self) -> tuple[str, ...]:
        return (self.flow,)


@dataclass(frozen=True)
class Screenshot(Step):
    op: ClassVar[str] = "screenshot"
    category: ClassVar[str] = "compose"

    name: str = "step"


def step_from_dict(data: Mapping[str, Any]) -> Step:
    """按 ``op`` 反序列化 step，供平台与 page recorder 生成资产。"""
    payload = dict(data)
    op = str(payload.pop("op", "")).strip()
    cls = STEP_TYPES.get(op)
    if cls is None:
        raise ElementSpecError(f"未知 step op {op!r}；可用: {sorted(STEP_TYPES)}")
    if isinstance(payload.get("retry"), Mapping):
        payload["retry"] = RetryPolicy.from_dict(payload["retry"])
    known = {f.name for f in fields(cls)}
    unknown = [str(k) for k in payload if str(k) not in known]
    if unknown:
        raise ElementSpecError(f"step {op!r} 含未知键: {sorted(unknown)}")
    return cls(**payload)


def steps_from_dicts(items: Any) -> tuple[Step, ...]:
    return tuple(step_from_dict(item) for item in (items or ()))


def steps_to_dicts(steps: Any) -> list[dict[str, Any]]:
    return [step.to_dict() for step in (steps or ())]


__all__ = [
    "SENSITIVE_RE",
    "TEXT_OPERATORS",
    "COUNT_OPERATORS",
    "ELEMENT_STATES",
    "SELECT_BY",
    "STEP_TYPES",
    "RetryPolicy",
    "Step",
    "Goto",
    "GoBack",
    "Reload",
    "Fill",
    "Click",
    "Hover",
    "Check",
    "Select",
    "Press",
    "Upload",
    "WaitForElement",
    "WaitForUrl",
    "WaitForResponse",
    "ExtractText",
    "ExtractAttribute",
    "ExtractCount",
    "AssertVisible",
    "AssertHidden",
    "AssertText",
    "AssertUrl",
    "AssertCount",
    "RunFlow",
    "Screenshot",
    "resolve_value",
    "placeholders_in",
    "step_from_dict",
    "steps_from_dicts",
    "steps_to_dicts",
]
