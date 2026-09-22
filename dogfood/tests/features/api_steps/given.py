"""Given steps for the api stage (CLI + workbench HTTP)."""
from __future__ import annotations

from behave import given


@given('工作区已有私有工具 "{tool_id}"')
def step_workspace_has_tool(context, tool_id):
    root = context.project_root
    assert (root / "apps" / tool_id / "cli.py").is_file(), f"missing apps/{tool_id}/cli.py"
    context.tool_id = tool_id


@given('暂存了 "{path}" 的改动')
def step_staged_path(context, path):
    context.staged_path = path


@given("工作台已在本机启动")
def step_workbench_up(context):
    from fastapi.testclient import TestClient

    from tuner_testkit.workbench.app import create_app

    context.workbench = TestClient(create_app(root=context.project_root))
    health = context.workbench.get("/api/health")
    assert health.status_code == 200 and health.json().get("ok") is True
