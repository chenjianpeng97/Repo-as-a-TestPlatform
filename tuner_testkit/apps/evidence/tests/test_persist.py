from __future__ import annotations

import json
from pathlib import Path

from tuner_testkit.apps.evidence.persist import persist, unique_routes


def test_persist_strips_cookie_and_masks_email(tmp_path: Path):
    captures = [
        {
            "method": "POST",
            "url": "http://localhost:8000/api/sign-in/",
            "headers": {"Cookie": "sessionid=secret", "content-type": "application/json"},
            "body": {"email": "dogfood@local.test", "password": "super-secret"},
            "response": {"status": 200, "headers": {"content-type": "application/json"}, "body": {"ok": True}},
        }
    ]
    payload = persist(
        run_id="20260913T000000Z-test",
        scenario_id="explore:login",
        captures=captures,
        intent="unit test",
        root=tmp_path,
    )
    network = Path(payload["dir"]) / "network.jsonl"
    row = json.loads(network.read_text(encoding="utf-8").splitlines()[0])
    headers = {k.lower(): v for k, v in row["request"]["headers"].items()}
    assert "cookie" not in headers
    assert "password" not in (row["request"]["body"] or {}) or row["request"]["body"]["password"] == "***"
    email = (row["request"]["body"] or {}).get("email", "")
    assert "dogfood@local.test" not in json.dumps(row)
    assert "***" in str(email) or email == "***"
    assert (Path(payload["dir"]) / "run_summary.md").is_file()
    assert payload["routes"][0]["method"] == "POST"


def test_persist_task_id_screenshot_log_and_api(tmp_path: Path):
    shot = tmp_path / "fail.png"
    shot.write_bytes(b"\x89PNG\r\n")
    log = tmp_path / "app.log"
    log.write_text("Authorization: Bearer super-secret-token\nlevel=info msg=ok\n", encoding="utf-8")  # fake fixture — secret-scan: allow
    api = tmp_path / "create.json"
    api.write_text('{"ok": false, "token": "raw-token"}', encoding="utf-8")  # fake fixture — secret-scan: allow
    payload = persist(
        run_id="20260924T000000Z-exec",
        scenario_id="explore:order",
        captures=[],
        intent="e2e",
        root=tmp_path,
        task_id="TASK-20260924-001",
        screenshots=[shot],
        logs=[log],
        apis=[api],
    )
    dest = Path(payload["dir"])
    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["params"]["task_id"] == "TASK-20260924-001"
    redacted = (dest / "logs" / "app.log").read_text(encoding="utf-8")
    assert "super-secret-token" not in redacted
    assert "msg=ok" in redacted
    body = json.loads((dest / "api" / "create.json").read_text(encoding="utf-8"))
    assert body["token"] == "***"
    assert (dest / "screenshots" / "fail.png").is_file()
    kinds = {item["kind"] for item in manifest["files"]}
    assert "screenshot" in kinds
    assert "log" in kinds


def test_unique_routes_dedupes():
    rows = [
        {"request": {"method": "GET", "normalized_path": "/api/x"}, "response": {"status": 200}},
        {"request": {"method": "GET", "path": "/api/x"}, "response": {"status": 200}},
        {"request": {"method": "POST", "normalized_path": "/api/x"}, "response": {"status": 201}},
    ]
    routes = unique_routes(rows)
    assert [r["method"] for r in routes] == ["GET", "POST"]
