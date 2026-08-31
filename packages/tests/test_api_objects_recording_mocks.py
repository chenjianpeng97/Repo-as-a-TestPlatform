from __future__ import annotations

import json
from pathlib import Path

from packages.api_objects.recording.capture import build_capture
from packages.api_objects.recording.codegen import truncate_sample
from packages.api_objects.recording.mocks import MockSampleWriter


def _capture(
    *,
    url: str = "http://example.com/prod-api/items",
    method: str = "POST",
    response: dict | bytes | None = None,
    status: int = 200,
    content_type: str = "application/json",
):
    if response is None:
        response = {"code": 200, "message": "SUCCESS", "data": {"list": [], "total": 0}}
    content = response if isinstance(response, bytes) else json.dumps(response).encode("utf-8")
    return build_capture(
        method=method,
        url=url,
        request_headers={"Content-Type": "application/json", "Authorization": "Bearer SECRET1234567890abcdefghijklmn"},
        request_content=b'{"pageNum":1}',
        response_status=status,
        response_headers={"Content-Type": content_type},
        response_content=content,
    )


def _big_list_response(rows: int = 40) -> dict:
    return {
        "code": 200,
        "message": "SUCCESS",
        "data": {
            "total": rows,
            "list": [{"id": i, "name": f"row-{i}"} for i in range(rows)],
        },
    }


# --- the whole point: no truncation --------------------------------------


def test_full_sample_keeps_every_row(tmp_path: Path) -> None:
    """The asset keeps 5 rows + a marker; the mock definition keeps all 40."""
    capture = _capture(response=_big_list_response(40))
    writer = MockSampleWriter(tmp_path)

    result = writer.write(capture)

    payload = json.loads(Path(result.path).read_text(encoding="utf-8"))
    rows = payload["scenarios"]["success"]["body"]["data"]["list"]
    assert len(rows) == 40
    assert rows[-1] == {"id": 39, "name": "row-39"}
    assert not any(isinstance(r, str) for r in rows)

    # Contrast with what the asset file would have stored.
    truncated = truncate_sample(capture.response_body)["data"]["list"]
    assert len(truncated) == 6
    assert truncated[-1] == "...(+35 more)"


def test_deep_nesting_survives(tmp_path: Path) -> None:
    deep = {"l1": {"l2": {"l3": {"l4": {"l5": {"l6": {"l7": "bottom"}}}}}}}
    capture = _capture(response={"code": 200, "data": deep})

    MockSampleWriter(tmp_path).write(capture)

    payload = json.loads(next(tmp_path.rglob("*.json")).read_text(encoding="utf-8"))
    body = payload["scenarios"]["success"]["body"]
    assert body["data"]["l1"]["l2"]["l3"]["l4"]["l5"]["l6"]["l7"] == "bottom"
    # The asset version collapses at depth 6.
    assert truncate_sample(capture.response_body)["data"]["l1"]["l2"]["l3"]["l4"]["l5"] == "..."


def test_long_strings_are_not_clipped(tmp_path: Path) -> None:
    long_text = "订单备注 " * 200  # spaces/CJK so sanitize does not read it as a token
    capture = _capture(response={"code": 200, "data": long_text})

    MockSampleWriter(tmp_path).write(capture)

    payload = json.loads(next(tmp_path.rglob("*.json")).read_text(encoding="utf-8"))
    assert payload["scenarios"]["success"]["body"]["data"] == long_text
    assert len(long_text) > 240  # the asset copy would have been clipped here
    assert truncate_sample(capture.response_body)["data"].endswith("...")


def test_token_shaped_strings_stay_masked(tmp_path: Path) -> None:
    """Pre-existing sanitize behaviour, inherited on purpose.

    A long alphanumeric run is treated as a credential by
    ``sanitize.mask_value`` before the capture is ever built, so business data
    that happens to look like a token (base64 blobs, long opaque ids) arrives
    here already masked. Recording full samples must not undo that.
    """
    capture = _capture(response={"code": 200, "data": "A1b2C3d4" * 8})

    MockSampleWriter(tmp_path).write(capture)

    payload = json.loads(next(tmp_path.rglob("*.json")).read_text(encoding="utf-8"))
    assert payload["scenarios"]["success"]["body"]["data"] == "A1b2***C3d4"


# --- layout and metadata ---------------------------------------------------


def test_path_mirrors_the_asset_route_tree(tmp_path: Path) -> None:
    capture = _capture(url="http://example.com/prod-api/inout/report/his/queryInoutHis")

    result = MockSampleWriter(tmp_path).write(capture, version=1)

    rel = result.path.relative_to(tmp_path).as_posix()
    assert rel == "prod-api/inout/report/his/queryInoutHis/POST.v1.json"


def test_version_follows_the_asset(tmp_path: Path) -> None:
    result = MockSampleWriter(tmp_path).write(_capture(), version=2)

    assert result.path.name == "POST.v2.json"
    assert json.loads(result.path.read_text(encoding="utf-8"))["version"] == 2


def test_dynamic_segments_are_normalised(tmp_path: Path) -> None:
    capture = _capture(url="http://example.com/prod-api/users/42/profile", method="POST")

    result = MockSampleWriter(tmp_path).write(capture)

    payload = json.loads(result.path.read_text(encoding="utf-8"))
    assert payload["path"] == "/prod-api/users/{id}/profile"
    assert result.path.relative_to(tmp_path).as_posix() == "prod-api/users/{id}/profile/POST.v1.json"


def test_only_content_type_header_is_kept(tmp_path: Path) -> None:
    """Replaying a recorded Content-Length against a different body breaks clients."""
    capture = build_capture(
        method="GET",
        url="http://example.com/x",
        request_headers={},
        request_content=b"",
        response_status=200,
        response_headers={
            "Content-Type": "application/json",
            "Content-Length": "12345",
            "Transfer-Encoding": "chunked",
            "Set-Cookie": "session=abc",
        },
        response_content=b'{"code":200}',
    )

    MockSampleWriter(tmp_path).write(capture)

    headers = json.loads(next(tmp_path.rglob("*.json")).read_text(encoding="utf-8"))["scenarios"]["success"]["headers"]
    assert headers == {"Content-Type": "application/json"}


def test_sanitisation_carries_over(tmp_path: Path) -> None:
    capture = _capture(
        response={"code": 200, "token": "eyJhbGciOiJIUzI1NiJ9.payload.sig", "data": {"password": "hunter2"}}
    )

    MockSampleWriter(tmp_path).write(capture)

    text = next(tmp_path.rglob("*.json")).read_text(encoding="utf-8")
    assert "hunter2" not in text
    assert "SECRET1234567890" not in text
    body = json.loads(text)["scenarios"]["success"]["body"]
    assert body["token"] == "***"
    assert body["data"]["password"] == "***"


def test_non_json_response_records_status_only(tmp_path: Path) -> None:
    capture = _capture(response=b"\x00\x01binary", content_type="application/octet-stream", status=200)

    result = MockSampleWriter(tmp_path).write(capture)

    scenario = json.loads(result.path.read_text(encoding="utf-8"))["scenarios"]["success"]
    assert scenario["body"] is None
    assert scenario["status"] == 200
    assert "non-JSON" in scenario["description"]


def test_error_status_is_preserved(tmp_path: Path) -> None:
    capture = _capture(response={"code": 500, "message": "boom"}, status=500)

    result = MockSampleWriter(tmp_path).write(capture)

    assert json.loads(result.path.read_text(encoding="utf-8"))["scenarios"]["success"]["status"] == 500


# --- re-recording ----------------------------------------------------------


def test_rerecording_refreshes_only_its_own_scenario(tmp_path: Path) -> None:
    writer = MockSampleWriter(tmp_path)
    result = writer.write(_capture(response=_big_list_response(3)))

    # A human adds a scenario and switches to it.
    payload = json.loads(result.path.read_text(encoding="utf-8"))
    payload["scenarios"]["boom"] = {"status": 500, "body": {"code": 500}}
    payload["active"] = "boom"
    result.path.write_text(json.dumps(payload), encoding="utf-8")

    again = writer.write(_capture(response=_big_list_response(9)))

    assert again.action == "updated"
    after = json.loads(result.path.read_text(encoding="utf-8"))
    assert after["scenarios"]["boom"] == {"status": 500, "headers": {}, "body": {"code": 500}, "delay_ms": 0}
    assert after["active"] == "boom"  # user's choice is not overridden
    assert len(after["scenarios"]["success"]["body"]["data"]["list"]) == 9  # refreshed


def test_custom_scenario_name_leaves_success_alone(tmp_path: Path) -> None:
    MockSampleWriter(tmp_path, scenario="success").write(_capture(response={"code": 200, "data": "hand-tuned"}))
    MockSampleWriter(tmp_path, scenario="recorded").write(_capture(response=_big_list_response(4)))

    payload = json.loads(next(tmp_path.rglob("*.json")).read_text(encoding="utf-8"))

    assert payload["scenarios"]["success"]["body"]["data"] == "hand-tuned"
    assert len(payload["scenarios"]["recorded"]["body"]["data"]["list"]) == 4
    assert payload["active"] == "success"


def test_corrupt_file_is_rebuilt_rather_than_losing_the_capture(tmp_path: Path) -> None:
    writer = MockSampleWriter(tmp_path)
    result = writer.write(_capture())
    result.path.write_text("{ not json", encoding="utf-8")

    again = writer.write(_capture(response=_big_list_response(2)))

    assert again.action == "created"
    assert len(json.loads(result.path.read_text(encoding="utf-8"))["scenarios"]["success"]["body"]["data"]["list"]) == 2


def test_oversized_response_is_skipped(tmp_path: Path) -> None:
    writer = MockSampleWriter(tmp_path, max_bytes=500)

    result = writer.write(_capture(response=_big_list_response(200)))

    assert result.action == "skipped"
    assert "exceeds --mock-max-bytes" in result.detail
    assert list(tmp_path.rglob("*.json")) == []


def test_max_bytes_zero_disables_the_guard(tmp_path: Path) -> None:
    writer = MockSampleWriter(tmp_path, max_bytes=0)

    assert writer.write(_capture(response=_big_list_response(200))).action == "created"


def test_seeded_mocks_load_into_the_store(tmp_path: Path) -> None:
    from packages.api_mock.store import MockStore

    writer = MockSampleWriter(tmp_path)
    writer.write(_capture(url="http://example.com/a/b", response=_big_list_response(12)))
    writer.write(_capture(url="http://example.com/c/d", method="GET"))

    store = MockStore(tmp_path)

    assert store.reload() == 2
    route = store.get("POST", "/a/b")
    assert len(route.active_response().body["data"]["list"]) == 12
