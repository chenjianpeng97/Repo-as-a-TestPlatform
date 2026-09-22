"""When steps for the api stage."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from behave import when


def _run(context, argv: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["TUNER_ROOT"] = str(context.project_root)
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        argv,
        cwd=str(context.project_root),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


@when("我查看该工具的用法说明")
def step_tool_help(context):
    proc = _run(context, [sys.executable, "-m", f"apps.{context.tool_id}", "--help"])
    context.help_text = proc.stdout + proc.stderr
    context.help_code = proc.returncode
    assert proc.returncode == 0, context.help_text


@when("我生成工作区目录")
def step_catalog(context):
    proc = _run(context, [sys.executable, "-m", "tuner_testkit.workspace", "catalog", "--out", "-"])
    assert proc.returncode == 0, proc.stderr
    context.catalog = json.loads(proc.stdout)


@when('我用首行 "{header}" 提交')
def step_commit_header(context, header):
    import tempfile

    hook = Path(__file__).resolve().parents[4] / "tools" / "git-hooks" / "validate_commit_msg.py"
    spec_name = "validate_commit_msg"
    import importlib.util

    spec = importlib.util.spec_from_file_location(spec_name, hook)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as fh:
        fh.write(header + "\n")
        msg_path = fh.name
    env_files = context.staged_path
    old = os.environ.get("TUNER_COMMIT_STAGED")
    os.environ["TUNER_COMMIT_STAGED"] = env_files
    try:
        context.commit_code = mod.main([spec_name, msg_path])
    finally:
        if old is None:
            os.environ.pop("TUNER_COMMIT_STAGED", None)
        else:
            os.environ["TUNER_COMMIT_STAGED"] = old
        Path(msg_path).unlink(missing_ok=True)


@when("我查看工具目录")
def step_list_tools(context):
    resp = context.workbench.get("/api/tools")
    assert resp.status_code == 200
    context.tool_items = resp.json()["items"]
