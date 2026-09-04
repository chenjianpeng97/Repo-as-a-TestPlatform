from __future__ import annotations

from typing import Any, Dict

import pytest

from tuner_testkit.api_test.client import ApiClient
from tuner_testkit.api_test.model import APIModel


class _DummyResp:
    def __init__(self, status_code: int = 200, json_obj: Any = None, text: str = ""):
        self.status_code = status_code
        self._json_obj = json_obj
        self.text = text
        self.headers = {"Content-Type": "application/json"}

    def json(self):
        if self._json_obj is None:
            raise ValueError("no json")
        return self._json_obj


def test_execute_builds_url_params_headers_and_auth(monkeypatch):
    captured: Dict[str, Any] = {}

    def fake_request(self, **kwargs):
        captured.update(kwargs)
        return _DummyResp(status_code=200, json_obj={"code": 200, "data": {"x": 1}})

    monkeypatch.setattr("requests.Session.request", fake_request, raising=True)

    client = ApiClient(base_url="http://example.com")
    m = APIModel(
        id="svc.GET./x@v1",
        name="x",
        description="",
        method="GET",
        path="/x",
        query_schema={"q": {"type": "string", "required": False}},
        headers_policy={"allowlist": ["Accept"], "forbidden": ["Authorization", "Cookie", "Set-Cookie"]},
        auth_policy={"required": True, "strategy": "bearer_token", "source": "client.default"},
    ).bind(client)

    resp = m.set_query({"q": "abc"}).set_headers({"Accept": "application/json"}).execute(auth={"bearer_token": "t123"})

    assert resp.ok is True
    assert captured["url"] == "http://example.com/x"
    assert captured["params"] == {"q": "abc"}
    assert captured["headers"]["Accept"] == "application/json"
    assert captured["headers"]["Authorization"] == "Bearer t123"

