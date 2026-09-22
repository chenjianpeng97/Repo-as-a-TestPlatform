from apps.sample_tool.cli import build_parser, main
from apps.sample_tool.core import build_lines


def test_build_lines_plain_and_upper() -> None:
    assert build_lines(2, "demo") == ["demo-001", "demo-002"]
    assert build_lines(1, "demo", "upper") == ["DEMO-001"]


def test_parser_lists_expected_options() -> None:
    usage = build_parser().format_help()
    for flag in ("--count", "--label", "--style", "--dry-run", "--json"):
        assert flag in usage


def test_main_json_envelope(capsys) -> None:
    assert main(["--count", "2", "--label", "x", "--json"]) == 0
    out = capsys.readouterr().out.strip().splitlines()[-1]
    assert '"status": "succeeded"' in out
    assert '"count": 2' in out
