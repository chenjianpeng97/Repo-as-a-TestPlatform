from __future__ import annotations

import json
from pathlib import Path

import pytest

from tuner_testkit.api_mock.errors import MockSpecError, RouteNotFoundError, ScenarioNotFoundError
from tuner_testkit.api_mock.spec import ResponseSpec, RouteMock, mock_relpath, route_key, scan_sensitive
from tuner_testkit.api_mock.store import MockStore


def _write(mocks_dir: Path, payload: dict) -> Path:
    rel = mock_relpath(payload["method"], payload["path"], version=payload.get("version", 1))
    target = mocks_dir / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return target


def _route(**overrides) -> dict:
    payload = {
        "method": "POST",
        "path": "/prod-api/items",
        "active": "success",
        "scenarios": {"success": {"status": 200, "body": {"code": 200}}},
    }
    payload.update(overrides)
    return payload


# --- spec ------------------------------------------------------------------


def test_route_key_normalises_method_and_slash() -> None:
    assert route_key("post", "prod-api/x") == "POST /prod-api/x"


def test_mock_relpath_mirrors_route_tree() -> None:
    rel = mock_relpath("post", "/prod-api/inout/report/his/queryInoutHis")
    assert rel.as_posix() == "prod-api/inout/report/his/queryInoutHis/POST.v1.json"


def test_path_must_not_contain_host() -> None:
    with pytest.raises(ValueError, match="host"):
        RouteMock(method="GET", path="http://example.com/x")


def test_active_scenario_must_exist() -> None:
    with pytest.raises(ValueError, match="active scenario"):
        RouteMock(
            method="GET",
            path="/x",
            active="nope",
            scenarios={"success": ResponseSpec()},
        )


def test_scan_sensitive_flags_real_values_but_not_placeholders() -> None:
    route = RouteMock(
        method="POST",
        path="/login",
        scenarios={
            "success": ResponseSpec(
                headers={"Set-Cookie": "session=abc123"},
                body={"token": "eyJhbGciOi", "masked": "***", "nested": {"password": "hunter2"}},
            )
        },
    )
    hits = scan_sensitive(route)

    assert "success.headers.Set-Cookie" in hits
    assert "success.body.token" in hits
    assert "success.body.nested.password" in hits
    assert not any("masked" in hit for hit in hits)


# --- store loading ---------------------------------------------------------


def test_reload_reads_definitions(tmp_path: Path) -> None:
    _write(tmp_path, _route())
    store = MockStore(tmp_path)

    assert store.reload() == 1
    assert store.get("POST", "/prod-api/items").active == "success"


def test_missing_dir_is_not_an_error(tmp_path: Path) -> None:
    store = MockStore(tmp_path / "absent")
    assert store.reload() == 0
    assert store.routes() == []


def test_invalid_definition_is_skipped_not_fatal(tmp_path: Path) -> None:
    _write(tmp_path, _route())
    broken = tmp_path / "broken" / "GET.v1.json"
    broken.parent.mkdir(parents=True)
    broken.write_text("{not json", encoding="utf-8")

    store = MockStore(tmp_path)
    assert store.reload() == 1


def test_highest_version_wins(tmp_path: Path) -> None:
    _write(tmp_path, _route(version=1, scenarios={"success": {"status": 200, "body": "v1"}}))
    _write(tmp_path, _route(version=2, scenarios={"success": {"status": 200, "body": "v2"}}))

    store = MockStore(tmp_path)
    store.reload()

    assert store.get("POST", "/prod-api/items").scenarios["success"].body == "v2"


def test_match_honours_dynamic_segments(tmp_path: Path) -> None:
    _write(tmp_path, _route(path="/users/{id}"))
    store = MockStore(tmp_path)
    store.reload()

    assert store.match("POST", "/users/42") is not None
    assert store.match("POST", "/users/abc") is None
    assert store.get("POST", "/users/42") is None  # get() is exact-only


# --- overrides and persistence ---------------------------------------------


def test_upsert_scenario_creates_route_in_memory_only(tmp_path: Path) -> None:
    store = MockStore(tmp_path)
    store.reload()

    store.upsert_scenario("POST", "/new", "success", ResponseSpec(status=201), activate=True)

    assert store.get("POST", "/new").active == "success"
    assert store.is_dirty("POST", "/new") is True
    assert list(tmp_path.rglob("*.json")) == []


def test_set_active_switches_scenario(tmp_path: Path) -> None:
    _write(
        tmp_path,
        _route(
            scenarios={
                "success": {"status": 200, "body": {"code": 200}},
                "boom": {"status": 500, "body": {"code": 500}},
            }
        ),
    )
    store = MockStore(tmp_path)
    store.reload()

    assert store.set_active("POST", "/prod-api/items", "boom").active == "boom"
    with pytest.raises(ScenarioNotFoundError):
        store.set_active("POST", "/prod-api/items", "absent")
    with pytest.raises(RouteNotFoundError):
        store.set_active("GET", "/absent", "success")


def test_persist_writes_overrides_and_clears_dirty(tmp_path: Path) -> None:
    store = MockStore(tmp_path)
    store.reload()
    store.upsert_scenario("POST", "/prod-api/items", "success", ResponseSpec(body={"code": 200}))

    written = store.persist()

    assert len(written) == 1
    assert Path(written[0]).relative_to(tmp_path).as_posix() == "prod-api/items/POST.v1.json"
    assert store.is_dirty("POST", "/prod-api/items") is False
    assert store.dirty_keys() == []
    # Survives a fresh load from disk.
    reloaded = MockStore(tmp_path)
    reloaded.reload()
    assert reloaded.get("POST", "/prod-api/items").scenarios["success"].body == {"code": 200}


def test_persist_single_route_requires_both_args(tmp_path: Path) -> None:
    store = MockStore(tmp_path)
    store.reload()
    store.upsert_scenario("POST", "/a", "success", ResponseSpec())

    with pytest.raises(ValueError, match="both method and path"):
        store.persist("POST", None)
    with pytest.raises(RouteNotFoundError):
        store.persist("GET", "/never-touched")


def test_reset_drops_overrides_but_keeps_disk(tmp_path: Path) -> None:
    _write(tmp_path, _route())
    store = MockStore(tmp_path)
    store.reload()
    store.upsert_scenario("POST", "/prod-api/items", "boom", ResponseSpec(status=500), activate=True)
    assert store.get("POST", "/prod-api/items").active == "boom"

    assert store.reset() == 1
    assert store.get("POST", "/prod-api/items").active == "success"


def test_cannot_delete_last_scenario(tmp_path: Path) -> None:
    _write(tmp_path, _route())
    store = MockStore(tmp_path)
    store.reload()

    with pytest.raises(MockSpecError, match="last scenario"):
        store.delete_scenario("POST", "/prod-api/items", "success")


def test_delete_scenario_reassigns_active(tmp_path: Path) -> None:
    _write(
        tmp_path,
        _route(
            active="boom",
            scenarios={
                "success": {"status": 200, "body": {"code": 200}},
                "boom": {"status": 500, "body": {"code": 500}},
            },
        ),
    )
    store = MockStore(tmp_path)
    store.reload()

    route = store.delete_scenario("POST", "/prod-api/items", "boom")

    assert sorted(route.scenarios) == ["success"]
    assert route.active == "success"
