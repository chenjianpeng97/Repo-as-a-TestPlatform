from __future__ import annotations

import json
from pathlib import Path

from apps.mock_server.seed import (
    extract_recorded_response,
    seed_mocks,
    strip_truncation_markers,
)

ASSET_WITH_RECORDING = '''\
"""Auto-maintained by apps.recorder."""

from packages.api_test.model import APIModel, AssertOperation

query_items_post_v1 = APIModel(
    id="svc.POST./svc/items@v1",
    name="query items",
    description="",
    method="POST",
    path="/svc/items",
    response_hints={"top_level_keys": ["code", "data", "message"]},
    asserts=[
        AssertOperation(name="http status", jsonpath="$.http_status", operator="eq", expected=200),
    ],
)

if __name__ == "__main__":
    _RECORDED_BODY = {"pageNum": 1}
    _RECORDED_RESPONSE = {
        "http_status": 200,
        "is_json": True,
        "json": {
            "code": 200,
            "message": "SUCCESS",
            "data": {
                "list": [{"id": 1}, {"id": 2}, "...(+7 more)"],
                "deep": "...",
                "total": 9,
            },
            "token": "***",
        },
    }
    print(_RECORDED_RESPONSE)
'''

ASSET_WITHOUT_RECORDING = '''\
from packages.api_test.model import APIModel, AssertOperation

get_thing_get_v1 = APIModel(
    id="svc.GET./svc/thing@v1",
    name="get thing",
    description="",
    method="GET",
    path="/svc/thing",
    response_hints={"top_level_keys": ["code", "data"]},
    asserts=[
        AssertOperation(name="http status", jsonpath="$.http_status", operator="eq", expected=201),
    ],
)
'''


def _write_asset(root: Path, route_dir: str, filename: str, source: str) -> Path:
    target = root / "packages" / "api_objects" / route_dir / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    return target


# --- pure helpers ----------------------------------------------------------


def test_extract_reads_recorded_response_from_main_block() -> None:
    recorded = extract_recorded_response(ASSET_WITH_RECORDING)

    assert recorded is not None
    assert recorded["http_status"] == 200
    assert recorded["json"]["code"] == 200


def test_extract_returns_none_without_a_sample() -> None:
    assert extract_recorded_response(ASSET_WITHOUT_RECORDING) is None


def test_extract_survives_unparsable_source() -> None:
    assert extract_recorded_response("def broken(:\n") is None


def test_strip_removes_list_and_depth_markers() -> None:
    cleaned = strip_truncation_markers(
        {
            "list": [{"id": 1}, "...(+7 more)", "..."],
            "deep": "...",
            "kept": "real value",
            "nested": [["...(+2 more)", "x"]],
        }
    )

    assert cleaned["list"] == [{"id": 1}]
    assert cleaned["deep"] is None  # key survives so the response shape holds
    assert cleaned["kept"] == "real value"
    assert cleaned["nested"] == [["x"]]


def test_strip_leaves_ordinary_ellipsis_inside_longer_strings() -> None:
    assert strip_truncation_markers({"note": "to be continued..."})["note"] == "to be continued..."


# --- end to end ------------------------------------------------------------


def test_seed_uses_recorded_sample(tmp_path: Path) -> None:
    _write_asset(tmp_path, "svc/items", "POST.v1.py", ASSET_WITH_RECORDING)
    mocks = tmp_path / "data" / "mocks"

    report = seed_mocks(mocks, root=tmp_path)

    assert report.from_recording == 1
    assert report.from_hints == 0
    written = mocks / "svc" / "items" / "POST.v1.json"
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["id"] == "svc.POST./svc/items@v1"
    assert payload["active"] == "success"
    body = payload["scenarios"]["success"]["body"]
    assert body["data"]["list"] == [{"id": 1}, {"id": 2}]  # marker stripped
    assert body["token"] == "***"
    assert payload["scenarios"]["success"]["headers"]["Content-Type"] == "application/json"


def test_seed_falls_back_to_response_hints(tmp_path: Path) -> None:
    _write_asset(tmp_path, "svc/thing", "GET.v1.py", ASSET_WITHOUT_RECORDING)
    mocks = tmp_path / "data" / "mocks"

    report = seed_mocks(mocks, root=tmp_path)

    assert report.from_hints == 1
    payload = json.loads((mocks / "svc" / "thing" / "GET.v1.json").read_text(encoding="utf-8"))
    scenario = payload["scenarios"]["success"]
    assert scenario["body"] == {"code": None, "data": None}
    assert scenario["status"] == 201  # taken from the asset's $.http_status assert


def test_seed_skips_existing_files_unless_overwrite(tmp_path: Path) -> None:
    _write_asset(tmp_path, "svc/items", "POST.v1.py", ASSET_WITH_RECORDING)
    mocks = tmp_path / "data" / "mocks"
    seed_mocks(mocks, root=tmp_path)

    target = mocks / "svc" / "items" / "POST.v1.json"
    target.write_text('{"method":"POST","path":"/svc/items","scenarios":{}}', encoding="utf-8")

    again = seed_mocks(mocks, root=tmp_path)
    assert again.created == []
    assert len(again.skipped) == 1
    assert json.loads(target.read_text(encoding="utf-8"))["scenarios"] == {}

    forced = seed_mocks(mocks, root=tmp_path, overwrite=True)
    assert len(forced.created) == 1
    assert json.loads(target.read_text(encoding="utf-8"))["scenarios"] != {}


def test_seed_dry_run_writes_nothing(tmp_path: Path) -> None:
    _write_asset(tmp_path, "svc/items", "POST.v1.py", ASSET_WITH_RECORDING)
    mocks = tmp_path / "data" / "mocks"

    report = seed_mocks(mocks, root=tmp_path, dry_run=True)

    assert len(report.created) == 1
    assert not mocks.exists()


def test_seeded_files_load_back_into_the_store(tmp_path: Path) -> None:
    from packages.api_mock.store import MockStore

    _write_asset(tmp_path, "svc/items", "POST.v1.py", ASSET_WITH_RECORDING)
    _write_asset(tmp_path, "svc/thing", "GET.v1.py", ASSET_WITHOUT_RECORDING)
    mocks = tmp_path / "data" / "mocks"
    seed_mocks(mocks, root=tmp_path)

    store = MockStore(mocks)

    assert store.reload() == 2
    assert store.get("POST", "/svc/items") is not None
    assert store.get("GET", "/svc/thing") is not None
