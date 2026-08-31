"""UI 页面资产层。

两种范式共存，都由 ``packages.page_test`` 驱动：

- **声明式**：模块级 ``PageModel``（元素表 + 声明式 flow），page recorder 的生成目标。
- **类范式**：``BasePage`` 子类逃生舱，复杂交互写 Python 方法，元素声明照旧。

资产按路由分目录：``packages/page_objects/<app>/<page_slug>.py``。凭据与单文件
回放走 :mod:`packages.page_objects.session`（对标 ``api_objects.auth``）。
用 ``python -m packages.page_test list`` 查看当前已发现的资产。
"""
from __future__ import annotations

try:
    from .pages import Pages
except ImportError:  # template may ship before Pages is generated
    Pages = None  # type: ignore[misc, assignment]

__all__ = ["Pages"]
