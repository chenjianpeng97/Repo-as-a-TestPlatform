"""PageModel 资产与不可变调用链 —— 对齐 ``packages.api_test.model``。

字段分组与 ``APIModel`` 一一对位：Identity（``url_path`` 无 host，host 运行时注入）、
Contract（``inputs_schema`` 对位 ``body_schema``、``locator_policy`` 对位
``headers_policy``）、Operations（``asserts`` / ``extracts`` 都是数据）、
Runtime binding（``bind()`` 注入 driver）。

``asserts`` / ``extracts`` 描述**页面自身的稳定契约**，在 ``open()`` 时执行；
flow 级别的断言写在该 flow 的 steps 里 —— 因为 UI flow 常常导航离开本页，
不能像 API 那样每次调用后都套同一组页面断言。
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, replace
from typing import Any, Mapping, MutableMapping

from .errors import (
    DriverError,
    ElementSpecError,
    FlowNotFoundError,
    LocatorPolicyError,
    SchemaValidationError,
)
from .locator import (
    DEFAULT_POLICY,
    ElementSpec,
    LocatorEvent,
    LocatorPolicy,
    validate_elements,
)
from .steps import Goto, Step, steps_from_dicts, steps_to_dicts

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.\-]*@v\d+$")
_NUM_SEG_RE = re.compile(r"^\d+$")
_UUID_SEG_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def normalize_url_path(path: str) -> str:
    """把 ``/projects/42/issues/<uuid>`` 归一为 ``/projects/{id}/issues/{uuid}``。

    与 ``packages.api_objects.recording.normalize_path`` 对 API path 的归一同构，供 fingerprint 去重使用。
    """
    segments = []
    for segment in (path or "/").split("/"):
        if not segment:
            segments.append(segment)
        elif _NUM_SEG_RE.match(segment):
            segments.append("{id}")
        elif _UUID_SEG_RE.match(segment):
            segments.append("{uuid}")
        else:
            segments.append(segment)
    return "/".join(segments) or "/"


def _merge_shallow(
    base: Mapping[str, Any] | None, patch: Mapping[str, Any] | None
) -> dict[str, Any]:
    out: dict[str, Any] = dict(base or {})
    if patch:
        out.update(patch)
    return out


def _validate_keys_or_autofill(
    *,
    schema: MutableMapping[str, Any],
    values: Mapping[str, Any],
    allow_autofill: bool,
    schema_name: str,
) -> None:
    missing = [k for k in values if k not in schema]
    if not missing:
        return
    if not allow_autofill:
        raise SchemaValidationError(f"{schema_name} 含未声明的键: {missing}")
    for key in missing:
        schema[key] = {"type": "any", "required": False, "note": "autofilled by set_inputs"}


@dataclass(frozen=True)
class PageFlow:
    """一个业务动作：有序 step 序列 + 平台渲染表单与一键运行所需的元数据。"""

    name: str
    description: str = ""
    #: 供平台渲染表单（弱 schema，与 inputs_schema 同风格）
    params_schema: Mapping[str, Any] = field(default_factory=dict)
    steps: tuple[Step, ...] = ()
    #: 可直接运行的入参样例，对齐 ``ActionWord.example_params``（CLI ``--example``）
    example_params: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "params_schema": dict(self.params_schema),
            "steps": steps_to_dicts(self.steps),
            "example_params": dict(self.example_params),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PageFlow":
        payload = dict(data)
        steps = payload.pop("steps", ())
        known = {f for f in cls.__dataclass_fields__}
        unknown = [str(k) for k in payload if str(k) not in known]
        if unknown:
            raise ElementSpecError(f"PageFlow 含未知键: {sorted(unknown)}")
        return cls(**{str(k): v for k, v in payload.items()}, steps=steps_from_dicts(steps))


@dataclass(frozen=True)
class StepOutcome:
    """单个 step 的执行留痕，含命中的候选索引（定位器健康度的原始数据）。"""

    index: int
    op: str
    summary: str
    ok: bool
    elapsed_ms: int = 0
    element: str = ""
    locator_index: int = -1
    fallback_used: bool = False
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "op": self.op,
            "summary": self.summary,
            "ok": self.ok,
            "elapsed_ms": self.elapsed_ms,
            "element": self.element,
            "locator_index": self.locator_index,
            "fallback_used": self.fallback_used,
            "error": self.error,
        }


@dataclass(frozen=True)
class PageResult:
    """执行结果，对齐 ``ApiResponse`` 并补上 UI 特有的可观测字段。"""

    ok: bool
    page_id: str
    flow: str
    url: str = ""
    title: str = ""
    extracted: dict[str, Any] = field(default_factory=dict)
    steps: tuple[StepOutcome, ...] = ()
    locator_events: tuple[LocatorEvent, ...] = ()
    screenshot: str = ""
    failed_step: str = ""
    error: str = ""

    @property
    def fallbacks(self) -> tuple[LocatorEvent, ...]:
        """本次运行中命中备用候选的事件（首选定位器已失效的信号）。"""
        return tuple(e for e in self.locator_events if e.outcome == "fallback")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "page_id": self.page_id,
            "flow": self.flow,
            "url": self.url,
            "title": self.title,
            "extracted": dict(self.extracted),
            "steps": [s.to_dict() for s in self.steps],
            "locator_events": [e.to_dict() for e in self.locator_events],
            "screenshot": self.screenshot,
            "failed_step": self.failed_step,
            "error": self.error,
        }


@dataclass(frozen=True)
class PageModel:
    """冻结的声明式页面资产。"""

    # ---- Identity ----
    id: str
    name: str
    description: str = ""
    #: 无 host 的路径；host 由 ``packages.config.get_ui_base_url()`` 运行时注入
    url_path: str = "/"

    # ---- Contract ----
    #: 唯一允许出现定位器的地方
    elements: Mapping[str, ElementSpec] = field(default_factory=dict)
    inputs_schema: Mapping[str, Any] = field(default_factory=dict)
    flows: Mapping[str, PageFlow] = field(default_factory=dict)
    #: ``open()`` 后的就绪等待条件（等条件成立，不是 sleep）
    ready: tuple[Step, ...] = ()
    locator_policy: Mapping[str, Any] = field(default_factory=dict)
    #: 只声明鉴权策略（storage_state / 前置登录 flow）；凭据永不落盘
    auth_policy: Mapping[str, Any] = field(default_factory=dict)

    # ---- Operations ----
    asserts: tuple[Step, ...] = ()
    extracts: tuple[Step, ...] = ()

    # ---- Runtime binding ----
    _driver: Any = field(default=None, repr=False, compare=False)

    # -- 运行时绑定 -----------------------------------------------------

    def bind(self, driver: Any) -> "PageModel":
        return replace(self, _driver=driver)

    def policy(self) -> LocatorPolicy:
        return LocatorPolicy.from_mapping(self.locator_policy)

    # -- 不可变调用链入口（对齐 APIModel.set_*） -------------------------

    def set_inputs(
        self, values: Mapping[str, Any] | None = None, *, autofill_schema: bool = True
    ) -> "PageInvocation":
        return PageInvocation(self).set_inputs(values, autofill_schema=autofill_schema)

    def override_inputs(self, values: Mapping[str, Any] | None = None) -> "PageInvocation":
        return PageInvocation(self).override_inputs(values)

    def open(self, *, driver: Any = None, timeout_ms: int | None = None) -> PageResult:
        return PageInvocation(self).open(driver=driver, timeout_ms=timeout_ms)

    def run(
        self,
        flow: str,
        *,
        params: Mapping[str, Any] | None = None,
        driver: Any = None,
        timeout_ms: int | None = None,
    ) -> PageResult:
        return PageInvocation(self).run(
            flow, params=params, driver=driver, timeout_ms=timeout_ms
        )

    # -- 平台化导出 -----------------------------------------------------

    def fingerprint(self) -> str:
        """归一 url_path + 元素名集合，供 page recorder 去重。"""
        raw = f"{normalize_url_path(self.url_path)}|{','.join(sorted(self.elements))}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]

    def describe(self) -> dict[str, Any]:
        """目录条目：元素表 + 流程步骤表 + 策略，供平台解析与可视化。"""
        return {
            "kind": "page_model",
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "url_path": self.url_path,
            "normalized_url_path": normalize_url_path(self.url_path),
            "fingerprint": self.fingerprint(),
            "elements": [self.elements[k].to_dict() for k in sorted(self.elements)],
            "inputs_schema": dict(self.inputs_schema),
            "flows": [self.flows[k].to_dict() for k in sorted(self.flows)],
            "ready": steps_to_dicts(self.ready),
            "asserts": steps_to_dicts(self.asserts),
            "extracts": steps_to_dicts(self.extracts),
            "locator_policy": self.policy().to_dict(),
            "auth_policy": dict(self.auth_policy),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "url_path": self.url_path,
            "elements": {k: v.to_dict() for k, v in self.elements.items()},
            "inputs_schema": dict(self.inputs_schema),
            "flows": {k: v.to_dict() for k, v in self.flows.items()},
            "ready": steps_to_dicts(self.ready),
            "asserts": steps_to_dicts(self.asserts),
            "extracts": steps_to_dicts(self.extracts),
            "locator_policy": dict(self.locator_policy),
            "auth_policy": dict(self.auth_policy),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PageModel":
        payload = dict(data)
        payload.pop("kind", None)
        payload.pop("fingerprint", None)
        payload.pop("normalized_url_path", None)
        elements = payload.pop("elements", {}) or {}
        flows = payload.pop("flows", {}) or {}
        for key in ("ready", "asserts", "extracts"):
            if key in payload:
                payload[key] = steps_from_dicts(payload[key])
        known = {f for f in cls.__dataclass_fields__ if not f.startswith("_")}
        unknown = [str(k) for k in payload if str(k) not in known]
        if unknown:
            raise ElementSpecError(f"PageModel 含未知键: {sorted(unknown)}")

        if isinstance(elements, Mapping):
            element_specs = {
                str(k): ElementSpec.from_dict(v) for k, v in elements.items()
            }
        else:
            parsed = [ElementSpec.from_dict(v) for v in elements]
            element_specs = {spec.name: spec for spec in parsed}

        if isinstance(flows, Mapping):
            flow_objs = {str(k): PageFlow.from_dict(v) for k, v in flows.items()}
        else:
            parsed_flows = [PageFlow.from_dict(v) for v in flows]
            flow_objs = {flow.name: flow for flow in parsed_flows}

        return cls(
            **{str(k): v for k, v in payload.items()},
            elements=element_specs,
            flows=flow_objs,
        )

    # -- 静态校验（无需浏览器） -------------------------------------------

    def validate(self) -> list[str]:
        """返回问题清单（空表示通过）。CLI ``validate`` 与离线单测走这条。"""
        problems: list[str] = []

        if not _ID_RE.match(self.id or ""):
            problems.append(
                f"id {self.id!r} 不符合 '<app>.<page_slug>@v<major>' 约定"
            )
        if not self.name.strip():
            problems.append("name（业务名）不能为空")
        if "://" in self.url_path or self.url_path.startswith("//"):
            problems.append(f"url_path {self.url_path!r} 不得包含 host")
        elif not self.url_path.startswith("/"):
            problems.append(f"url_path {self.url_path!r} 必须以 / 开头")

        try:
            policy = self.policy()
        except LocatorPolicyError as exc:
            problems.append(str(exc))
            policy = DEFAULT_POLICY

        problems.extend(validate_elements(self.elements, policy=policy))

        for key, flow in self.flows.items():
            if key != flow.name:
                problems.append(f"flows 键 {key!r} 与 PageFlow.name {flow.name!r} 不一致")
            if not flow.steps:
                problems.append(f"flow {key!r} 没有任何 step")
            problems.extend(self._check_step_refs(flow.steps, where=f"flow {key!r}"))

        problems.extend(self._check_step_refs(self.ready, where="ready"))
        problems.extend(self._check_step_refs(self.asserts, where="asserts"))
        problems.extend(self._check_step_refs(self.extracts, where="extracts"))
        problems.extend(self._check_flow_cycles())

        variables: dict[str, str] = {}
        for source, steps in (("extracts", self.extracts), *(
            (f"flow {k!r}", v.steps) for k, v in self.flows.items()
        )):
            for step in steps:
                variable = getattr(step, "variable", None)
                if not variable:
                    continue
                if variable in variables:
                    problems.append(
                        f"提取变量 {variable!r} 在 {variables[variable]} 与 {source} 重复定义"
                    )
                else:
                    variables[str(variable)] = source

        return problems

    def _check_step_refs(self, steps: tuple[Step, ...], *, where: str) -> list[str]:
        problems: list[str] = []
        for index, step in enumerate(steps):
            for name in step.elements_used():
                if name not in self.elements:
                    problems.append(
                        f"{where} 第 {index} 步 {step.op} 引用了未声明的元素 {name!r}"
                    )
            for name in step.flows_used():
                if name not in self.flows:
                    problems.append(
                        f"{where} 第 {index} 步 {step.op} 引用了不存在的 flow {name!r}"
                    )
            if isinstance(step, Goto) and step.path and (
                "://" in step.path or step.path.startswith("//")
            ):
                problems.append(f"{where} 第 {index} 步 goto 的 path 不得包含 host")
        return problems

    def _check_flow_cycles(self) -> list[str]:
        problems: list[str] = []

        def walk(name: str, seen: tuple[str, ...]) -> None:
            if name in seen:
                problems.append(f"flow 调用成环: {' -> '.join([*seen, name])}")
                return
            flow = self.flows.get(name)
            if flow is None:
                return
            for step in flow.steps:
                for child in step.flows_used():
                    walk(child, (*seen, name))

        for key in self.flows:
            walk(key, ())
        return problems


@dataclass(frozen=True)
class PageInvocation:
    """不可变调用链，对齐 ``APIInvocation``：每次 set/override 返回新实例。"""

    model: PageModel

    _set_inputs: dict[str, Any] = field(default_factory=dict)
    _override_inputs: dict[str, Any] | None = None
    _inputs_schema: dict[str, Any] | None = None

    def set_inputs(
        self, values: Mapping[str, Any] | None = None, *, autofill_schema: bool = True
    ) -> "PageInvocation":
        values = dict(values or {})
        schema = dict(
            self._inputs_schema
            if self._inputs_schema is not None
            else self.model.inputs_schema
        )
        _validate_keys_or_autofill(
            schema=schema,
            values=values,
            allow_autofill=autofill_schema,
            schema_name="inputs_schema",
        )
        return replace(
            self,
            _set_inputs=_merge_shallow(self._set_inputs, values),
            _inputs_schema=schema,
        )

    def override_inputs(self, values: Mapping[str, Any] | None = None) -> "PageInvocation":
        values = dict(values or {})
        schema = dict(
            self._inputs_schema
            if self._inputs_schema is not None
            else self.model.inputs_schema
        )
        _validate_keys_or_autofill(
            schema=schema,
            values=values,
            allow_autofill=False,
            schema_name="inputs_schema",
        )
        return replace(self, _override_inputs=values, _set_inputs={}, _inputs_schema=schema)

    def _final_inputs(self) -> dict[str, Any]:
        base = self._override_inputs if self._override_inputs is not None else {}
        return _merge_shallow(base, self._set_inputs)

    def _effective_model(self) -> PageModel:
        if self._inputs_schema is None:
            return self.model
        return replace(self.model, inputs_schema=self._inputs_schema)

    def _resolve_driver(self, driver: Any) -> Any:
        use_driver = driver or self.model._driver
        if use_driver is None:
            raise DriverError(
                "没有可用的 PageDriver：用 model.bind(driver)、传 driver=，"
                "或用 PageDriver.launch() / PageDriver.attach(page)"
            )
        return use_driver

    def open(self, *, driver: Any = None, timeout_ms: int | None = None) -> PageResult:
        """导航到页面，等就绪条件成立，然后执行页面级 extracts + asserts。"""
        model = self._effective_model()
        steps = (Goto(), *model.ready, *model.extracts, *model.asserts)
        return self._resolve_driver(driver).execute(
            model,
            steps=steps,
            flow="open",
            params=self._final_inputs(),
            timeout_ms=timeout_ms,
        )

    def run(
        self,
        flow: str,
        *,
        params: Mapping[str, Any] | None = None,
        driver: Any = None,
        timeout_ms: int | None = None,
    ) -> PageResult:
        model = self._effective_model()
        flow_obj = model.flows.get(flow)
        if flow_obj is None:
            raise FlowNotFoundError(
                f"页面 {model.id} 没有 flow {flow!r}；可用: {sorted(model.flows)}"
            )
        merged = _merge_shallow(self._final_inputs(), params)
        return self._resolve_driver(driver).execute(
            model,
            steps=flow_obj.steps,
            flow=flow,
            params=merged,
            timeout_ms=timeout_ms,
        )


__all__ = [
    "PageFlow",
    "PageInvocation",
    "PageModel",
    "PageResult",
    "StepOutcome",
    "normalize_url_path",
]
