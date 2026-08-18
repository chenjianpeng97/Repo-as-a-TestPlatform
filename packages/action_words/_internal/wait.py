"""轮询等待 — 异步结果断言前的同步点。"""
from __future__ import annotations

import time
from typing import Any, Callable


def wait_until(
    check: Callable[[], tuple[bool, Any]],
    *,
    timeout: float = 90.0,
    interval: float = 3.0,
    desc: str = "",
) -> Any:
    """轮询 ``check`` 直到其返回 ``(True, value)``，超时抛 AssertionError。

    ``check`` 返回 ``(ok, detail)``：ok 为 False 时 detail 用于超时报错定位。
    """
    deadline = time.monotonic() + timeout
    detail: Any = None
    while True:
        ok, detail = check()
        if ok:
            return detail
        if time.monotonic() >= deadline:
            raise AssertionError(f"等待超时({timeout}s): {desc}；最后状态: {detail!r}")
        time.sleep(interval)
