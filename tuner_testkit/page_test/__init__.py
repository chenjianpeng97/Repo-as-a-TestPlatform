"""Page test toolkit (page model + declarative steps + driver).

与 ``tuner_testkit.api_test`` 同构的三层解耦：

- **资产**：:class:`~tuner_testkit.page_test.model.PageModel` —— 冻结的声明式
  dataclass，元素表 + 声明式动作步骤，可被 page recorder 生成、被平台可视化。
- **调用**：:class:`~tuner_testkit.page_test.model.PageInvocation` —— 不可变链式
  ``set_inputs`` / ``override_inputs`` → ``open`` / ``run``。
- **执行**：:class:`~tuner_testkit.page_test.driver.PageDriver` —— 独占 Playwright IO、
  多定位器解析、脱敏日志与失败截图。

稳定性核心是 :class:`~tuner_testkit.page_test.locator.ElementSpec`：每个元素挂一组
**按优先级排序的候选定位器**，运行时顺序探测；命中备用候选会产出
:class:`~tuner_testkit.page_test.locator.LocatorEvent`，由
:mod:`~tuner_testkit.page_test.health` 聚合成 doctor 体检报告。

复杂交互走 :class:`~tuner_testkit.page_test.base.BasePage` 逃生舱：动作用 Python 方法写，
但元素声明仍在 ``elements`` 里，因此照样享受多定位器 fallback 与体检。

``driver`` 惰性 import playwright，因此 ``describe`` / ``validate`` / ``catalog``
与离线单测在没装 playwright 的环境下也能跑。用法见 ``tuner_testkit/page_test/USAGE.md``。
"""
from __future__ import annotations

from .base import PAGE_CLASSES, BasePage
from .errors import (
    DriverError,
    ElementNotFoundError,
    ElementSpecError,
    FlowNotFoundError,
    LocatorPolicyError,
    PageAssertError,
    PageTestError,
    SchemaValidationError,
    StepExecutionError,
)
from .health import (
    DoctorReport,
    HealthCollector,
    append_events,
    artifacts_dir,
    build_report,
    load_events,
)
from .harvest import (
    HarvestedElement,
    as_valid_element,
    harvest_element,
    harvest_locators,
    suggest_name,
    suggest_placeholder,
)
from .locator import (
    DEFAULT_POLICY,
    ElementSpec,
    LocatorEvent,
    LocatorPolicy,
    LocatorSpec,
    ResolvedLocator,
    resolve_element,
    validate_element,
    validate_elements,
)
from .model import (
    PageFlow,
    PageInvocation,
    PageModel,
    PageResult,
    StepOutcome,
    normalize_url_path,
)
from .steps import (
    AssertCount,
    AssertHidden,
    AssertText,
    AssertUrl,
    AssertVisible,
    Check,
    Click,
    ExtractAttribute,
    ExtractCount,
    ExtractText,
    Fill,
    GoBack,
    Goto,
    Hover,
    Press,
    Reload,
    RetryPolicy,
    RunFlow,
    Screenshot,
    Select,
    Step,
    Upload,
    WaitForElement,
    WaitForResponse,
    WaitForUrl,
    step_from_dict,
)

__all__ = [
    # locator（稳定性核心）
    "DEFAULT_POLICY",
    "ElementSpec",
    "LocatorEvent",
    "LocatorPolicy",
    "LocatorSpec",
    "ResolvedLocator",
    "resolve_element",
    "validate_element",
    "validate_elements",
    # harvest（page recorder 离线核心）
    "HarvestedElement",
    "as_valid_element",
    "harvest_element",
    "harvest_locators",
    "suggest_name",
    "suggest_placeholder",
    # model
    "PageFlow",
    "PageInvocation",
    "PageModel",
    "PageResult",
    "StepOutcome",
    "normalize_url_path",
    # base（逃生舱）
    "BasePage",
    "PAGE_CLASSES",
    # steps
    "Step",
    "RetryPolicy",
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
    "step_from_dict",
    # health（doctor 体检）
    "DoctorReport",
    "HealthCollector",
    "append_events",
    "artifacts_dir",
    "build_report",
    "load_events",
    # errors
    "DriverError",
    "ElementNotFoundError",
    "ElementSpecError",
    "FlowNotFoundError",
    "LocatorPolicyError",
    "PageAssertError",
    "PageTestError",
    "SchemaValidationError",
    "StepExecutionError",
]


def __getattr__(name: str):  # pragma: no cover - 惰性导出，避免顶层 import playwright
    """``PageDriver`` 惰性导出：没装 playwright 时 import 本包依然安全。"""
    if name == "PageDriver":
        from .driver import PageDriver

        return PageDriver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
