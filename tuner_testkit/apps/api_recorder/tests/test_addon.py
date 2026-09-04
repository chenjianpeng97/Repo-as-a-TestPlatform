"""mitmproxy addon: filter + freeze with fake flows (no live proxy)."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from tuner_testkit.apps.api_recorder.addon import ApiObjectRecorderAddon
from tuner_testkit.api_objects.recording.mocks import MockSampleWriter


def _flow(
    *,
    method: str = "POST",
    url: str = "http://example.com/prod-api/items",
    req_headers: dict | None = None,
    resp_headers: dict | None = None,
    request_content: bytes = b'{"pageNum":1}',
    response_body: dict | bytes | None = None,
    status: int = 200,
):
    if response_body is None:
        response_body = {"code": 200, "data": {"list": [{"id": i} for i in range(30)], "total": 30}}
    payload = response_body if isinstance(response_body, bytes) else json.dumps(response_body).encode("utf-8")
    request = SimpleNamespace(
        method=method,
        pretty_url=url,
        url=url,
        content=request_content,
        headers=req_headers if req_headers is not None else {"Content-Type": "application/json"},
    )
    response = SimpleNamespace(
        status_code=status,
        content=payload,
        headers=resp_headers if resp_headers is not None else {"Content-Type": "application/json"},
    )
    return SimpleNamespace(request=request, response=response)


def test_addon_writes_both_asset_and_full_mock(tmp_path: Path) -> None:
    assets = tmp_path / "api_objects"
    mocks = tmp_path / "mocks"
    addon = ApiObjectRecorderAddon(
        outputs_dir=assets,
        verbose=False,
        mock_writer=MockSampleWriter(mocks, tool="api_recorder"),
    )

    addon.response(_flow())

    asset_src = (assets / "prod-api" / "items" / "POST.v1.py").read_text(encoding="utf-8")
    assert "...(+25 more)" in asset_src
    assert "Auto-maintained by apps.api_recorder" in asset_src

    mock = json.loads((mocks / "prod-api" / "items" / "POST.v1.json").read_text(encoding="utf-8"))
    assert len(mock["scenarios"]["success"]["body"]["data"]["list"]) == 30
    assert addon.stats["mocks_written"] == 1


def test_addon_without_writer_is_unchanged(tmp_path: Path) -> None:
    addon = ApiObjectRecorderAddon(outputs_dir=tmp_path, verbose=False)

    addon.response(_flow(response_body={"code": 200, "data": []}))

    assert addon.stats["frozen"] == 1
    assert addon.stats["mocks_written"] == 0
    assert list(tmp_path.rglob("*.json")) == []


def test_mock_write_failure_does_not_break_freezing(tmp_path: Path) -> None:
    class Exploding(MockSampleWriter):
        def write(self, capture, *, version: int = 1, asset_id: str | None = None):
            raise RuntimeError("disk on fire")

    assets = tmp_path / "api_objects"
    addon = ApiObjectRecorderAddon(
        outputs_dir=assets,
        verbose=False,
        mock_writer=Exploding(tmp_path / "mocks"),
    )

    addon.response(_flow(response_body={"code": 200, "data": []}))

    assert addon.stats["frozen"] == 1
    assert addon.stats["mocks_skipped"] == 1
    assert (assets / "prod-api" / "items" / "POST.v1.py").exists()


def test_addon_skips_options_and_static_and_html(tmp_path: Path) -> None:
    addon = ApiObjectRecorderAddon(outputs_dir=tmp_path, verbose=False, include_host="example.com")

    addon.response(_flow(method="OPTIONS"))
    addon.response(_flow(method="GET", url="http://example.com/static/app.js", request_content=b""))
    addon.response(
        _flow(
            method="GET",
            url="http://example.com/",
            request_content=b"",
            resp_headers={"Content-Type": "text/html"},
            response_body=b"<html></html>",
        )
    )
    addon.response(_flow(url="http://other.example.net/api/x"))

    assert addon.stats["skipped_method"] == 1
    assert addon.stats["skipped_static"] == 2
    assert addon.stats["skipped_host"] == 1
    assert addon.stats["frozen"] == 0
    assert not any(p.name.endswith(".v1.py") for p in tmp_path.rglob("*.py"))


def test_addon_help_prog() -> None:
    from tuner_testkit.apps.api_recorder.cli import build_parser

    parser = build_parser()
    assert parser.prog == "python -m tuner_testkit.apps.api_recorder"
