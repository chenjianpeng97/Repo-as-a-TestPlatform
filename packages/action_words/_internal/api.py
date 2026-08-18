"""API 辅助 — 冻结 api_objects 的动态加载与登录换 token。

登录资产模块由环境变量 ``TEST_LOGIN_API_MODULE`` /
``TEST_LOGIN_API_ATTR`` 配置（默认未设置时明确报错），避免模板硬编码
业务路由目录。含连字符的包路径（如 ``packages.api_objects.prod-api.login``）
同样经 :func:`load_api` 按名加载。
"""
from __future__ import annotations

import importlib
import os
from typing import Any


def load_api(module_path: str, attr: str) -> Any:
    """按模块路径与属性名加载一个冻结的 APIModel 资产。"""
    return getattr(importlib.import_module(module_path), attr)


def login_token(username: str, password: str) -> str:
    """调用冻结的 login 接口资产换取 bearer token。

    配置（环境变量）：
      - ``TEST_LOGIN_API_MODULE`` — 如 ``packages.api_objects.auth_api.login``
      - ``TEST_LOGIN_API_ATTR`` — 如 ``login_post_v1``（默认 ``login_post_v1``）
    """
    module = (os.getenv("TEST_LOGIN_API_MODULE") or "").strip()
    attr = (os.getenv("TEST_LOGIN_API_ATTR") or "login_post_v1").strip()
    if not module:
        raise RuntimeError(
            "未配置登录 API Object：请设置环境变量 TEST_LOGIN_API_MODULE "
            "（及可选 TEST_LOGIN_API_ATTR），指向冻结的 login 资产；"
            "或向 ActionContext 显式传入 bearer_token。"
        )
    login_model = load_api(module, attr)
    resp = login_model.set_json({"username": username, "password": password}).execute()
    token = _extract_token(resp)
    if not token:
        keys = sorted(resp.json.keys()) if isinstance(resp.json, dict) else type(resp.json)
        raise RuntimeError(f"登录响应中未找到 token（响应顶层键: {keys}）")
    return token


def _extract_token(resp: Any) -> str | None:
    payload = resp.json if isinstance(resp.json, dict) else {}
    for candidate in (payload.get("token"), payload.get("access_token")):
        if candidate:
            return str(candidate)
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("token", "access_token", "accessToken"):
            if data.get(key):
                return str(data[key])
    if isinstance(data, str) and data:
        return data
    return None
