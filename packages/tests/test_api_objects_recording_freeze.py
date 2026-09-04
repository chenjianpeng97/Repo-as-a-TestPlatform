from __future__ import annotations

from pathlib import Path

from tuner_testkit.api_objects.recording.capture import build_capture
from tuner_testkit.api_objects.recording.freeze import ApiObjectFreezer, parse_existing_asset


def _cap(*, url: str, method: str = "GET", query_body: bytes = b"", resp: bytes = b'{"code":200,"data":[]}'):
    return build_capture(
        method=method,
        url=url,
        request_headers={"Accept": "application/json", "Authorization": "Bearer SECRETTOKEN1234567890"},
        request_content=query_body,
        response_status=200,
        response_headers={"Content-Type": "application/json"},
        response_content=resp,
    )


def test_freeze_creates_route_tree(tmp_path: Path):
    freezer = ApiObjectFreezer(tmp_path)
    cap = _cap(url="http://example.com/api/users/list?categoryName=foo")
    result = freezer.freeze(cap)
    assert result.action == "created"
    assert result.path.name == "GET.v1.py"
    text = result.path.read_text(encoding="utf-8")
    assert "SECRETTOKEN" not in text
    assert "Bearer " not in text
    assert '"forbidden": ["Authorization", "Cookie", "Set-Cookie"]' in text
    assert 'path="/api/users/list"' in text
    assert "categoryName" in text
    assert 'if __name__ == "__main__":' in text
    assert "_RECORDED_QUERY" in text
    assert "_RECORDED_RESPONSE" in text
    assert "tuner_testkit.api_objects.auth" in text
    assert 'categoryName": "foo"' in text or '"categoryName": "foo"' in text
    assert (tmp_path / "api" / "users" / "list" / "__init__.py").exists()
    assert (tmp_path / "auth.py").exists()


def test_freeze_merges_schema_on_second_hit(tmp_path: Path):
    freezer = ApiObjectFreezer(tmp_path)
    freezer.freeze(_cap(url="http://example.com/api/x?a=1"))
    r2 = freezer.freeze(_cap(url="http://example.com/api/x?a=1&b=2"))
    assert r2.action == "updated"
    parsed = parse_existing_asset(r2.path)
    assert "a" in parsed["query_schema"]
    assert "b" in parsed["query_schema"]


def test_freeze_normalizes_id_segment(tmp_path: Path):
    freezer = ApiObjectFreezer(tmp_path)
    r = freezer.freeze(_cap(url="http://example.com/api/users/42/profile"))
    assert r.normalized_path == "/api/users/{id}/profile"
    assert (tmp_path / "api" / "users" / "{id}" / "profile" / "GET.v1.py").exists()


def test_freeze_form_body_format(tmp_path: Path):
    freezer = ApiObjectFreezer(tmp_path)
    cap = build_capture(
        method="POST",
        url="http://example.com/api/export",
        request_headers={"Content-Type": "application/x-www-form-urlencoded"},
        request_content=b"pageNum=1&pageSize=10",
        response_status=200,
        response_headers={"Content-Type": "application/octet-stream"},
        response_content=b"\x00\x01binary",
    )
    r = freezer.freeze(cap)
    text = r.path.read_text(encoding="utf-8")
    assert 'body_format="form"' in text
    assert "resp.content" in text


def test_freeze_stamps_tool_and_recording_export_marker(tmp_path: Path):
    freezer = ApiObjectFreezer(tmp_path, tool="api_recorder")
    result = freezer.freeze(_cap(url="http://example.com/svc/ping"))
    text = result.path.read_text(encoding="utf-8")
    assert "Auto-maintained by apps.api_recorder" in text
    init = result.path.parent.joinpath("__init__.py").read_text(encoding="utf-8")
    assert "# --- recording export: GET.v1.py ---" in init
    assert "apps.recorder export" not in init
