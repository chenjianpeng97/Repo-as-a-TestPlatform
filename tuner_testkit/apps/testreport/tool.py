"""Import-safe workbench/catalog manifest. Do not import docxtpl / python-docx here."""
from __future__ import annotations

import argparse

from tuner_testkit.tools import tool


@tool(
    tool_id="testreport",
    name="测试单出 GJB438B 测试报告",
    summary="测试单计数与一致性检查，按画像起草报告 Markdown，再套 GJB438B Word 模板出 docx。",
    group="report",
    module="tuner_testkit.apps.testreport",
    argv=["python", "-m", "tuner_testkit.apps.testreport"],
    destructive=False,
    timeout=300,
    readme_path="tuner_testkit/apps/testreport/README.md",
)
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tuner-testreport",
        description="测试单计数与检查 / 起草报告 Markdown / 渲染 docx",
    )
    parser.add_argument("cmd", choices=("stats", "draft", "render", "build-template"), help="子命令")
    parser.add_argument("target", nargs="+", help="stats/draft：测试单目录；render：报告 md；build-template：样例 docx")
    parser.add_argument("--check", action="store_true", help="stats：只输出问题与计数")
    parser.add_argument("--sut", default="", help="draft：被测系统短名")
    parser.add_argument("--slug", default="", help="draft：报告 id")
    parser.add_argument("--task", default="", help="draft：task_id")
    parser.add_argument("--force", action="store_true", help="draft：覆盖已存在的报告")
    return parser
