from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
DOGFOOD = REPO / "dogfood"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from tuner_testkit.action_words.registry import reset_registry_for_tests
    from tuner_testkit.tools.manifest import reset_registry_for_tests as reset_tools
    from tuner_testkit.workbench.app import create_app

    reset_tools()
    reset_registry_for_tests()
    monkeypatch.setenv("TUNER_ROOT", str(DOGFOOD))
    return TestClient(create_app(root=DOGFOOD))


def test_health_and_home(client) -> None:
    assert client.get("/api/health").json()["ok"] is True
    assert client.get("/").status_code == 200


def test_api_tools_lists_sample_tool_and_seed(client) -> None:
    items = client.get("/api/tools").json()["items"]
    ids = {row["id"] for row in items}
    assert "sample_tool" in ids
    assert "db_seed.sample_seed" in ids
    sample = next(row for row in items if row["id"] == "sample_tool")
    assert "params_schema" in sample and "count" in sample["params_schema"].get("properties", {})


def test_api_tools_search(client) -> None:
    items = client.get("/api/tools", params={"q": "sample"}).json()["items"]
    assert items
    assert all("sample" in row["id"].lower() or "sample" in row["name"].lower() for row in items)


def test_api_env_lists_names_only(client) -> None:
    resp = client.get("/api/env")
    assert resp.status_code == 200
    body = resp.json()
    assert "available" in body and "active" in body and "mode" in body
    blob = str(body).lower()
    for secret in ("password", "token", "secret", "authorization", "cookie"):
        assert secret not in blob
    assert client.get("/env").status_code == 200


def test_api_run_sample_tool(client) -> None:
    resp = client.post("/api/tools/sample_tool/run", json={"params": {"count": 1, "label": "wb", "json": True}})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "succeeded"
    assert body["envelope"]["status"] == "succeeded"
