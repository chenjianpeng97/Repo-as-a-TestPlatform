"""Then steps for the api stage."""
from __future__ import annotations

from behave import then


@then('用法说明应列出参数 "{flag}" 与 "{other}"')
def step_help_flags(context, flag, other):
    text = context.help_text
    assert flag in text, text
    assert other in text, text


@then('工作区目录应包含工具 "{tool_id}" 及其参数结构')
def step_catalog_has_tool(context, tool_id):
    tools = context.catalog.get("tools") or []
    row = next((t for t in tools if t.get("tool_id") == tool_id), None)
    assert row is not None, f"{tool_id} not in catalog tools"
    props = (row.get("params_schema") or {}).get("properties") or {}
    assert "count" in props and "label" in props


@then('提交信息校验结果应为 "{result}"')
def step_commit_result(context, result):
    expected = 0 if result == "通过" else 1
    assert context.commit_code == expected, f"expected {result} ({expected}), got {context.commit_code}"


@then('目录应包含工具 "{tool_id}"')
def step_dir_has_tool(context, tool_id):
    ids = {row["id"] for row in context.tool_items}
    assert tool_id in ids, ids


@then('目录应包含动作词 "{word_id}"')
def step_dir_has_word(context, word_id):
    ids = {row["id"] for row in context.tool_items}
    assert word_id in ids, ids


@then("每个条目应带有名称、分组与参数结构")
def step_items_shaped(context):
    assert context.tool_items, "empty tool directory"
    for row in context.tool_items:
        assert row.get("name")
        assert row.get("group")
        assert isinstance(row.get("params_schema"), dict)
