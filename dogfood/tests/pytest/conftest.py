"""pytest session hooks: write ``artifacts/reports/<run_id>/manifest.json`` (docs/spec/artifacts-layout.md).

Run with ``pytest tests/pytest --junitxml artifacts/reports/<run_id>/junit.xml`` to
keep the JUnit file next to the manifest; ``TUNER_REPORT_DIR`` / ``TUNER_RUN_ID``
override the run directory / id.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from tuner_testkit import artifacts
from tuner_testkit.project import ensure_project_on_path

_STATE: dict[str, object] = {"manifest": None, "counts": {"passed": 0, "failed": 0, "skipped": 0}}


def pytest_sessionstart(session: pytest.Session) -> None:
    root = ensure_project_on_path()
    producer = artifacts.default_producer(root, suite="pytest tests/pytest")
    report_dir = os.environ.get("TUNER_REPORT_DIR")
    if report_dir:
        manifest = artifacts.RunManifest(
            kind="report",
            run_id=os.environ.get("TUNER_RUN_ID") or Path(report_dir).name,
            producer=producer,
            dir=Path(report_dir),
        )
        manifest.write()
    else:
        manifest = artifacts.start_run("report", "pytest", root=root, run_id=os.environ.get("TUNER_RUN_ID"), producer=producer)
    _STATE["manifest"] = manifest


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    counts: dict[str, int] = _STATE["counts"]  # type: ignore[assignment]
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        key = "passed" if report.outcome == "passed" else "failed" if report.outcome == "failed" else "skipped"
        counts[key] += 1


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    manifest = _STATE["manifest"]
    counts: dict[str, int] = _STATE["counts"]  # type: ignore[assignment]
    if manifest is None:
        return
    manifest.finish(  # type: ignore[union-attr]
        "succeeded" if int(exitstatus) == 0 else "failed",
        exit_code=int(exitstatus),
        summary={"total": sum(counts.values()), **counts},
    )
