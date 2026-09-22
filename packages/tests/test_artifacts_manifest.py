from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from tuner_testkit import artifacts as art
from tuner_testkit.project import reset_path_cache


def _workspace(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\nversion='0'\n", encoding="utf-8")
    (tmp_path / "packages").mkdir()
    return tmp_path


def test_new_run_id_and_mask() -> None:
    rid = art.new_run_id("Sample Tool!")
    assert rid.endswith("-sample-tool") and len(rid.split("-")[0]) == 16
    masked = art.mask_params({"count": 1, "password": "x", "nested": {"api_key": "k", "ok": 2}})
    assert masked == {"count": 1, "password": "***", "nested": {"api_key": "***", "ok": 2}}


def test_start_and_finish_run(tmp_path: Path, monkeypatch) -> None:
    reset_path_cache()
    root = _workspace(tmp_path)
    monkeypatch.delenv("TUNER_ROOT", raising=False)
    manifest = art.start_run("run", "sample_tool", root=root, params={"count": 2, "token": "t"}, run_id="r1")
    assert manifest.dir == root / "artifacts" / "runs" / "r1"
    data = json.loads(manifest.path.read_text(encoding="utf-8"))
    assert data["status"] == "running" and data["params"]["token"] == "***"
    (manifest.dir / "stdout.log").write_bytes(b"hi\n")
    manifest.finish("succeeded", exit_code=0, summary={"lines": 1})
    data = json.loads(manifest.path.read_text(encoding="utf-8"))
    assert data["status"] == "succeeded" and data["exit_code"] == 0
    assert data["files"] == [{"path": "stdout.log", "kind": "log", "bytes": 3}]
    loaded = art.RunManifest.load(manifest.dir)
    assert loaded.summary == {"lines": 1} and loaded.dir == manifest.dir


def test_behave_report_collector(tmp_path: Path, monkeypatch) -> None:
    reset_path_cache()
    root = _workspace(tmp_path)
    monkeypatch.setenv("TUNER_REPORT_DIR", str(root / "artifacts" / "reports" / "manual-run"))
    monkeypatch.delenv("TUNER_RUN_ID", raising=False)
    context = SimpleNamespace(config=SimpleNamespace(stage="api"), failed=False)
    manifest = art.report_run_begin(context, root=root)
    assert manifest.run_id == "manual-run" and manifest.producer.suite == "behave --stage api"
    feature = SimpleNamespace(name="F")
    art.report_scenario_end(context, SimpleNamespace(feature=feature, name="ok", tags=["x"], status=SimpleNamespace(name="passed"), duration=0.1))
    art.report_scenario_end(context, SimpleNamespace(feature=feature, name="bad", tags=[], status="failed", duration=0.2))
    finished = art.report_run_end(context)
    assert finished is not None and finished.status == "succeeded"  # context.failed wins over counts
    summary = json.loads((finished.dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["summary"] == {"total": 2, "passed": 1, "failed": 1, "skipped": 0, "by_status": {"passed": 1, "failed": 1}}
    assert any(f["path"] == "summary.json" for f in json.loads(finished.path.read_text(encoding="utf-8"))["files"])
