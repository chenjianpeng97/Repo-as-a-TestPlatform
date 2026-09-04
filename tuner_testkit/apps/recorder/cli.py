"""CLI for headed 合录 (PageObject + APIObject in one Playwright session)."""

from __future__ import annotations

import argparse
import pathlib
import sys

from tuner_testkit.logging import log_info, log_warn
from tuner_testkit.project import (
    api_objects_dir,
    ensure_project_on_path,
    mocks_dir,
    page_objects_dir,
)


def _resolve_dir(passed: pathlib.Path | None, default_factory):
    if passed is not None:
        return passed.expanduser().resolve()
    ensure_project_on_path()
    return default_factory()

_LEGACY_PROXY_FLAGS = frozenset({"--port", "--listen_host", "--listen-host"})


def reject_legacy_proxy_argv(argv: list[str] | None) -> None:
    """``python -m tuner_testkit.apps.recorder`` used to be the mitmproxy proxy. Do not silently forward."""
    tokens = list(argv) if argv is not None else sys.argv[1:]
    for token in tokens:
        name = token.split("=", 1)[0]
        if name in _LEGACY_PROXY_FLAGS:
            raise SystemExit(
                "python -m tuner_testkit.apps.recorder 已改为 headed 合录（PageObject + APIObject），"
                "不再启动 mitmproxy 代理。\n"
                "请改用: python -m tuner_testkit.apps.api_recorder"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tuner_testkit.apps.recorder",
        description=(
            "Launch a headed Playwright browser and freeze PageModel + APIModel "
            "as you click, fill, and browse. Use --page-only / --api-only to freeze "
            "one side. For HTTP(S) proxy capture of non-browser clients, use "
            "python -m tuner_testkit.apps.api_recorder."
        ),
    )
    parser.add_argument(
        "--app",
        required=True,
        help="应用名，写入 id '<app>.<page_slug>@v1' 与目录 packages/page_objects/<app>/",
    )
    parser.add_argument(
        "--flow",
        default="recorded",
        help="写入的 flow 名（默认 recorded）",
    )
    parser.add_argument(
        "--url",
        default="",
        help="起始 URL；相对路径拼到 TEST_UI_BASE_URL / TEST_BASE_URL",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="进入每个新 URL 后扫描可见的 button/link/textbox 等，只扩元素表（仅冻 page 时生效）",
    )
    parser.add_argument(
        "--outputs_dir",
        type=pathlib.Path,
        default=None,
        help="Page Objects 根目录（默认: <project>/packages/page_objects）",
    )
    parser.add_argument(
        "--storage-state",
        default="",
        help="可选 Playwright storage_state JSON（已登录会话；凭据不进资产）",
    )
    parser.add_argument(
        "--include_host",
        default="",
        help="只冻结 host 包含该子串的页面与 API（可选）",
    )
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument(
        "--page-only",
        action="store_true",
        help="只冻 PageModel，不挂 API tap",
    )
    exclusive.add_argument(
        "--api-only",
        action="store_true",
        help="仍开 headed 浏览器，只冻 APIModel，不写 PageModel",
    )
    parser.add_argument(
        "--api-outputs-dir",
        type=pathlib.Path,
        default=None,
        help="API Objects 根目录（默认: <project>/packages/api_objects）",
    )
    parser.add_argument(
        "--write-mocks",
        action="store_true",
        help="冻 API 时同时把完整响应写入 data/mocks（仅 API 开启时生效）",
    )
    parser.add_argument(
        "--mocks-dir",
        type=pathlib.Path,
        default=None,
        help="Where --write-mocks saves definitions (default: <project>/data/mocks)",
    )
    parser.add_argument(
        "--mock-scenario",
        default="success",
        help="Scenario name --write-mocks writes/refreshes (default: success)",
    )
    parser.add_argument(
        "--mock-max-bytes",
        type=int,
        default=1_048_576,
        help="Skip mock writes whose JSON body exceeds this size (default: 1 MiB; 0 disables)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    reject_legacy_proxy_argv(argv)
    parser = build_parser()
    args = parser.parse_args(argv)

    from tuner_testkit.apps.page_recorder.cli import _validate_app
    from tuner_testkit.apps.page_recorder.session import PageRecorderSession, resolve_start_url

    app = _validate_app(args.app)
    flow = (args.flow or "recorded").strip() or "recorded"
    freeze_pages = not bool(args.api_only)
    freeze_apis = not bool(args.page_only)
    page_outputs = _resolve_dir(args.outputs_dir, page_objects_dir)
    api_outputs = _resolve_dir(args.api_outputs_dir, api_objects_dir)
    if freeze_pages:
        page_outputs.mkdir(parents=True, exist_ok=True)
    if freeze_apis:
        api_outputs.mkdir(parents=True, exist_ok=True)

    try:
        start_url = resolve_start_url(args.url or None)
    except SystemExit:
        raise

    tap = None
    if freeze_apis:
        from tuner_testkit.api_objects.recording import MockSampleWriter

        from tuner_testkit.apps.api_recorder.playwright_tap import PlaywrightApiTap

        mock_writer = None
        if args.write_mocks:
            mock_writer = MockSampleWriter(
                _resolve_dir(args.mocks_dir, mocks_dir),
                scenario=args.mock_scenario,
                max_bytes=args.mock_max_bytes,
                tool="recorder",
            )
        tap = PlaywrightApiTap(
            outputs_dir=api_outputs,
            include_host=args.include_host or None,
            mock_writer=mock_writer,
            tool="recorder",
        )

    def on_page_ready(page) -> None:
        if tap is not None:
            tap.attach(page)

    storage_state = (args.storage_state or "").strip() or None
    session = PageRecorderSession(
        app=app,
        flow=flow,
        outputs_dir=page_outputs,
        start_url=start_url,
        scan=bool(args.scan) and freeze_pages,
        include_host=args.include_host or None,
        storage_state=storage_state,
        freeze_pages=freeze_pages,
        on_page_ready=on_page_ready if freeze_apis else None,
    )
    try:
        session.run()
    except KeyboardInterrupt:
        log_info("recorder stopped (Ctrl+C)")
    except Exception as exc:  # noqa: BLE001
        log_warn("recorder aborted", error=str(exc))
        from tuner_testkit.page_test.errors import DriverError

        if isinstance(exc, DriverError):
            raise SystemExit(str(exc)) from exc
        raise SystemExit(f"recorder failed: {exc}") from exc
    finally:
        if tap is not None:
            tap.done()
        if freeze_pages:
            _write_page_changelog(page_outputs, app=app, items=session.freezer.touched_ids)
        if freeze_apis and tap is not None:
            from tuner_testkit.apps.api_recorder.cli import write_api_changelog

            write_api_changelog(api_outputs, tap.touched_items(), tool="recorder")

    return 0


def _write_page_changelog(outputs_dir: pathlib.Path, *, app: str, items: list[str]) -> None:
    if not items:
        return
    try:
        from tuner_testkit.apps._shared.changelog import append_entry
    except Exception as exc:  # noqa: BLE001
        log_warn("recorder page changelog skipped", error=str(exc))
        return
    append_entry(
        outputs_dir / "CHANGELOG.md",
        tool="recorder",
        action="record-pages",
        items=items,
        app=app,
        count=len(items),
    )
    log_info("recorder page changelog appended", count=len(items), app=app)


if __name__ == "__main__":
    raise SystemExit(main())
