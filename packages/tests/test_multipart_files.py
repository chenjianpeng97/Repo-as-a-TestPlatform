from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest

from packages.api_test.client import ApiClient, normalize_file_input
from packages.api_test.errors import FilesPolicyError
from packages.api_test.model import APIModel


class _DummyResp:
    def __init__(self, status_code: int = 200, json_obj: Any = None, text: str = ""):
        self.status_code = status_code
        self._json_obj = json_obj
        self.text = text
        self.headers = {"Content-Type": "application/json"}
        self.content = b"{}"

    def json(self):
        if self._json_obj is None:
            raise ValueError("no json")
        return self._json_obj


def _multipart_model(**kwargs: Any) -> APIModel:
    defaults = dict(
        id="svc.POST./import@v1",
        name="import",
        description="",
        method="POST",
        path="/import",
        body_schema={"bizType": {"type": "string", "required": False}},
        files_schema={"file": {"type": "file", "required": True}},
        body_format="multipart",
        headers_policy={
            "allowlist": ["Accept", "Content-Type"],
            "forbidden": ["Authorization", "Cookie", "Set-Cookie"],
        },
        auth_policy={"required": False, "strategy": "none"},
    )
    defaults.update(kwargs)
    return APIModel(**defaults)


def test_set_files_requires_multipart():
    m = APIModel(
        id="svc.POST./x@v1",
        name="x",
        description="",
        method="POST",
        path="/x",
        body_format="json",
        headers_policy={"allowlist": ["Accept"], "forbidden": []},
        auth_policy={"required": False, "strategy": "none"},
    )
    with pytest.raises(FilesPolicyError, match="multipart"):
        m.set_files({"file": "a.xlsx"})


def test_set_files_merge_and_override():
    m = _multipart_model(files_schema={"file": {"type": "file", "required": False}, "attach": {"type": "file", "required": False}})
    inv = m.set_files({"file": "a.xlsx"}).set_files({"attach": "b.xlsx"})
    assert inv._final_files() == {"file": "a.xlsx", "attach": "b.xlsx"}
    inv2 = inv.override_files({"file": "c.xlsx"})
    assert inv2._final_files() == {"file": "c.xlsx"}


def test_required_file_missing_on_execute(monkeypatch):
    monkeypatch.setattr(
        "requests.Session.request",
        lambda self, **kwargs: _DummyResp(json_obj={"code": 200}),
        raising=True,
    )
    client = ApiClient(base_url="http://example.com")
    m = _multipart_model().bind(client)
    with pytest.raises(FilesPolicyError, match="required file"):
        m.set_json({"bizType": "1"}).execute()


def test_multipart_execute_sends_data_and_files(monkeypatch, tmp_path: Path):
    captured: Dict[str, Any] = {}
    upload = tmp_path / "import.xlsx"
    upload.write_bytes(b"PK\x03\x04demo")

    def fake_request(self, **kwargs):
        captured.update(kwargs)
        return _DummyResp(status_code=200, json_obj={"code": 200, "data": True})

    monkeypatch.setattr("requests.Session.request", fake_request, raising=True)

    client = ApiClient(base_url="http://example.com")
    m = _multipart_model().bind(client)
    resp = (
        m.set_json({"bizType": "1"})
        .set_files({"file": str(upload)})
        .set_headers({"Content-Type": "multipart/form-data", "Accept": "application/json"})
        .execute()
    )
    assert resp.ok is True
    assert captured["url"] == "http://example.com/import"
    assert captured["data"] == {"bizType": "1"}
    assert "files" in captured
    assert "file" in captured["files"]
    # requests sets multipart boundary — caller Content-Type must be stripped
    assert not any(k.lower() == "content-type" for k in (captured.get("headers") or {}))


def test_normalize_file_input_path_and_tuple(tmp_path: Path):
    p = tmp_path / "a.xlsx"
    p.write_bytes(b"abc")
    name, content, ctype = normalize_file_input(str(p), field_name="file")
    assert name == "a.xlsx"
    assert content.read() == b"abc"
    content.close()

    name2, content2, ctype2 = normalize_file_input(
        ("custom.xlsx", b"xyz", "application/octet-stream"),
        field_name="file",
    )
    assert name2 == "custom.xlsx"
    assert content2 == b"xyz"
    assert ctype2 == "application/octet-stream"
