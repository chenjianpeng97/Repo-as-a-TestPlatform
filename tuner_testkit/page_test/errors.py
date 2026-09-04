from __future__ import annotations

from typing import Any


class PageTestError(Exception):
    """page_test 异常基类。

    ``result`` 携带失败时刻的 ``PageResult``（截图路径、已执行的 step、定位器
    健康事件），让「抛异常」与「留诊断」不冲突：调用方按需读 ``exc.result``。
    """

    def __init__(self, *args: Any, result: Any = None) -> None:
        super().__init__(*args)
        self.result = result


class LocatorPolicyError(PageTestError):
    """候选定位器违反 ``LocatorPolicy``（绝对 XPath / 索引寻址 / 缺少稳定候选等）。"""


class ElementSpecError(PageTestError):
    """元素声明本身不合法（候选为空、strategy 未知、scope 引用不存在或成环）。"""


class ElementNotFoundError(PageTestError):
    """元素的全部候选定位器都未命中。"""


class SchemaValidationError(PageTestError):
    """``set_inputs`` 传入了 ``inputs_schema`` 未声明的键，且未允许 autofill。"""


class FlowNotFoundError(PageTestError):
    pass


class StepExecutionError(PageTestError):
    """step 执行期出错（非断言失败）。"""


class PageAssertError(PageTestError, AssertionError):
    """页面断言失败。

    同时继承 ``AssertionError``，让 behave / pytest 归类为断言失败而非异常，
    与 ``tuner_testkit.action_words`` 的「断言类失败抛 AssertionError」约定一致。
    """


class DriverError(PageTestError):
    """驱动不可用（playwright 未安装、页面已关闭等）。"""
