from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="needs the 'mock' extra: uv sync --extra mock")

from fastapi.testclient import TestClient  # noqa: E402

from tuner_testkit.api_mock import MockStore, create_app  # noqa: E402
from tuner_testkit.api_mock.spec import mock_relpath  # noqa: E402

ADMIN = "/__mock__"


def _write_mock(mocks_dir: Path, payload: dict) -> Path:
    rel = mock_relpath(payload["method"], payload["path"], version=payload.get("version", 1))
    target = mocks_dir / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return target


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    _write_mock(
        tmp_path,
        {
            "method": "POST",
            "path": "/prod-api/items",
            "active": "success",
            "scenarios": {
                "success": {
                    "status": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": {"code": 200, "data": {"total": 2}},
                },
                "boom": {"status": 500, "body": {"code": 500, "message": "mocked failure"}},
            },
        },
    )
    app = create_app(mocks_dir=tmp_path, load_models=False)
    return TestClient(app)


# --- serving ---------------------------------------------------------------


def test_serves_the_active_scenario(client: TestClient) -> None:
    response = client.post("/prod-api/items", json={"pageNum": 1})

    assert response.status_code == 200
    assert response.json() == {"code": 200, "data": {"total": 2}}


def test_undefined_route_returns_501_with_guidance(client: TestClient) -> None:
    response = client.get("/not-defined")

    assert response.status_code == 501
    body = response.json()
    assert body["error"] == "no_mock_definition"
    assert "GET /not-defined" in body["message"]
    assert "apps.mock_server seed" in body["hint"]


def test_method_is_part_of_the_route_identity(client: TestClient) -> None:
    assert client.get("/prod-api/items").status_code == 501


def test_admin_prefix_is_not_swallowed_by_the_catch_all(client: TestClient) -> None:
    response = client.get(f"{ADMIN}/health")

    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_string_body_is_served_as_text(tmp_path: Path) -> None:
    _write_mock(
        tmp_path,
        {
            "method": "GET",
            "path": "/plain",
            "scenarios": {"success": {"status": 200, "body": "hello", "headers": {"Content-Type": "text/csv"}}},
        },
    )
    response = TestClient(create_app(mocks_dir=tmp_path, load_models=False)).get("/plain")

    assert response.status_code == 200
    assert response.text == "hello"
    assert response.headers["content-type"].startswith("text/csv")


def test_null_body_serves_an_empty_response(tmp_path: Path) -> None:
    _write_mock(
        tmp_path,
        {"method": "DELETE", "path": "/thing/1", "scenarios": {"success": {"status": 204, "body": None}}},
    )
    response = TestClient(create_app(mocks_dir=tmp_path, load_models=False)).delete("/thing/1")

    assert response.status_code == 204
    assert response.content == b""


def test_dynamic_segments_match(tmp_path: Path) -> None:
    _write_mock(
        tmp_path,
        {"method": "GET", "path": "/users/{id}", "scenarios": {"success": {"status": 200, "body": {"ok": True}}}},
    )
    client = TestClient(create_app(mocks_dir=tmp_path, load_models=False))

    assert client.get("/users/42").status_code == 200
    assert client.get("/users/not-an-int").status_code == 501


# --- control plane ---------------------------------------------------------


def test_routes_listing_reports_mock_state(client: TestClient) -> None:
    payload = client.get(f"{ADMIN}/routes").json()

    assert payload["count"] == 1
    row = payload["routes"][0]
    assert row["key"] == "POST /prod-api/items"
    assert row["has_mock"] is True
    assert row["active"] == "success"
    assert row["scenarios"] == ["boom", "success"]
    assert row["dirty"] is False


def test_route_detail_includes_full_definition(client: TestClient) -> None:
    payload = client.get(
        f"{ADMIN}/routes/detail", params={"method": "POST", "path": "/prod-api/items"}
    ).json()

    assert payload["definition"]["scenarios"]["boom"]["status"] == 500


def test_define_scenario_takes_effect_immediately(client: TestClient) -> None:
    response = client.put(
        f"{ADMIN}/scenario",
        json={
            "method": "POST",
            "path": "/prod-api/items",
            "scenario": "empty",
            "activate": True,
            "response": {"status": 200, "body": {"code": 200, "data": {"total": 0, "list": []}}},
        },
    )

    assert response.status_code == 200
    assert response.json()["persisted"] is False
    assert client.post("/prod-api/items", json={}).json()["data"]["total"] == 0


def test_define_scenario_on_a_brand_new_route(client: TestClient) -> None:
    client.put(
        f"{ADMIN}/scenario",
        json={
            "method": "GET",
            "path": "/freshly/invented",
            "scenario": "success",
            "response": {"status": 202, "body": {"ok": True}},
        },
    )

    assert client.get("/freshly/invented").status_code == 202


def test_switch_active_scenario(client: TestClient) -> None:
    assert client.put(
        f"{ADMIN}/active",
        json={"method": "POST", "path": "/prod-api/items", "scenario": "boom"},
    ).status_code == 200

    response = client.post("/prod-api/items", json={})
    assert response.status_code == 500
    assert response.json()["message"] == "mocked failure"


def test_unknown_scenario_and_route_return_404(client: TestClient) -> None:
    missing_scenario = client.put(
        f"{ADMIN}/active", json={"method": "POST", "path": "/prod-api/items", "scenario": "nope"}
    )
    missing_route = client.put(
        f"{ADMIN}/active", json={"method": "GET", "path": "/absent", "scenario": "success"}
    )

    assert missing_scenario.status_code == 404
    assert missing_scenario.json()["error"] == "scenario_not_found"
    assert missing_route.status_code == 404
    assert missing_route.json()["error"] == "route_not_found"


def test_changes_stay_in_memory_until_persist(client: TestClient, tmp_path: Path) -> None:
    client.put(
        f"{ADMIN}/scenario",
        json={
            "method": "POST",
            "path": "/prod-api/items",
            "scenario": "slow",
            "response": {"status": 200, "body": {"code": 200}},
        },
    )
    on_disk = json.loads((tmp_path / "prod-api" / "items" / "POST.v1.json").read_text(encoding="utf-8"))
    assert "slow" not in on_disk["scenarios"]
    assert client.get(f"{ADMIN}/health").json()["pending_changes"] == ["POST /prod-api/items"]

    persisted = client.post(f"{ADMIN}/persist", json={})

    assert persisted.status_code == 200
    assert persisted.json()["count"] == 1
    after = json.loads((tmp_path / "prod-api" / "items" / "POST.v1.json").read_text(encoding="utf-8"))
    assert "slow" in after["scenarios"]
    assert client.get(f"{ADMIN}/health").json()["pending_changes"] == []


def test_reset_discards_in_memory_changes(client: TestClient) -> None:
    client.put(
        f"{ADMIN}/active", json={"method": "POST", "path": "/prod-api/items", "scenario": "boom"}
    )
    assert client.post("/prod-api/items", json={}).status_code == 500

    assert client.post(f"{ADMIN}/reset").json()["dropped_overrides"] == 1
    assert client.post("/prod-api/items", json={}).status_code == 200


def test_delete_scenario(client: TestClient) -> None:
    response = client.delete(
        f"{ADMIN}/scenario", params={"method": "POST", "path": "/prod-api/items", "scenario": "boom"}
    )

    assert response.status_code == 200
    assert response.json()["scenarios"] == ["success"]


# --- request log -----------------------------------------------------------


def test_request_log_records_matches_and_misses(client: TestClient) -> None:
    client.post("/prod-api/items", json={"pageNum": 1, "pageSize": 10})
    client.get("/nowhere")

    entries = client.get(f"{ADMIN}/requests").json()["requests"]

    assert len(entries) == 2
    matched, missed = entries
    assert matched["matched_route"] == "POST /prod-api/items"
    assert matched["scenario"] == "success"
    assert matched["status"] == 200
    assert matched["body_keys"] == ["pageNum", "pageSize"]  # keys only, never values
    assert missed["matched_route"] is None
    assert missed["status"] == 501


def test_request_log_masks_sensitive_headers(client: TestClient) -> None:
    client.post(
        "/prod-api/items",
        json={"password": "hunter2"},
        headers={"Authorization": "Bearer real-token", "X-Trace": "keep-me"},
    )

    entry = client.get(f"{ADMIN}/requests").json()["requests"][0]
    headers = {k.lower(): v for k, v in entry["headers"].items()}

    assert headers["authorization"] == "***"
    assert headers["x-trace"] == "keep-me"
    # Body values are never stored, only key names.
    assert entry["body_keys"] == ["password"]
    assert "hunter2" not in json.dumps(entry)


def test_request_log_can_be_cleared(client: TestClient) -> None:
    client.post("/prod-api/items", json={})

    assert client.delete(f"{ADMIN}/requests").json()["cleared"] == 1
    assert client.get(f"{ADMIN}/requests").json()["count"] == 0


def test_custom_admin_prefix(tmp_path: Path) -> None:
    app = create_app(mocks_dir=tmp_path, load_models=False, admin_prefix="/__ctl__")
    client = TestClient(app)

    assert client.get("/__ctl__/health").status_code == 200
    assert client.get(f"{ADMIN}/health").status_code == 501  # now just an unmocked route


def test_store_can_be_injected(tmp_path: Path) -> None:
    store = MockStore(tmp_path)
    app = create_app(store=store, load_models=False)
    client = TestClient(app)

    client.put(
        f"{ADMIN}/scenario",
        json={"method": "GET", "path": "/x", "scenario": "success", "response": {"status": 200, "body": {"a": 1}}},
    )

    assert store.get("GET", "/x") is not None
    assert client.get("/x").json() == {"a": 1}
