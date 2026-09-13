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


def test_unique_routes_dedupes():
    rows = [
        {"request": {"method": "GET", "normalized_path": "/api/x"}, "response": {"status": 200}},
        {"request": {"method": "GET", "path": "/api/x"}, "response": {"status": 200}},
        {"request": {"method": "POST", "normalized_path": "/api/x"}, "response": {"status": 201}},
    ]
    routes = unique_routes(rows)
    assert [r["method"] for r in routes] == ["GET", "POST"]
