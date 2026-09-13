from tuner_testkit.apps.evidence.cli import build_parser, main


def test_help_exits_zero():
    parser = build_parser()
    try:
        parser.parse_args(["--help"])
    except SystemExit as exc:
        assert exc.code == 0


def test_persist_requires_network():
    parser = build_parser()
    try:
        parser.parse_args(["persist", "--run-id", "x", "--scenario", "explore:x"])
        raised = False
    except SystemExit:
        raised = True
    assert raised


def test_main_help():
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
