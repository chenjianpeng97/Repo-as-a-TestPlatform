"""Page Test CLI —— 列出 / 查看 / 校验 / 一键运行 / 导出目录 / 定位器体检。

用法::

    uv run python -m tuner_testkit.page_test list
    uv run python -m tuner_testkit.page_test describe plane.login@v1
    uv run python -m tuner_testkit.page_test validate
    uv run python -m tuner_testkit.page_test catalog --out report/page_objects_catalog.json
    uv run python -m tuner_testkit.page_test run plane.login@v1 --flow login --example --headed
    uv run python -m tuner_testkit.page_test doctor plane.login@v1

``list`` / ``describe`` / ``validate`` / ``catalog`` / ``doctor`` **不启浏览器**，
因此没装 playwright 也能跑；只有 ``run`` 需要 ``uv sync --extra bdd``。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .health import SEVERITY_ERROR, build_report, load_events
from .registry import export_catalog, get, list_all, validate_all


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _load_params(args: argparse.Namespace, *, example: dict[str, Any]) -> dict[str, Any]:
    if getattr(args, "example", False):
        return dict(example)
    if getattr(args, "params_file", None):
        return json.loads(Path(args.params_file).read_text(encoding="utf-8"))
    return json.loads(getattr(args, "params", None) or "{}")


def _cmd_list(_args: argparse.Namespace) -> int:
    rows = [
        {
            "page_id": asset.page_id,
            "name": asset.model.name,
            "kind": asset.kind,
            "url_path": asset.model.url_path,
            "elements": len(asset.model.elements),
            "flows": sorted(asset.model.flows),
            "module": asset.module,
        }
        for asset in list_all()
    ]
    _print_json(rows)
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    _print_json(get(args.page_id).describe())
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    if args.page_id:
        problems = {args.page_id: get(args.page_id).validate()}
        problems = {k: v for k, v in problems.items() if v}
    else:
        problems = validate_all()
    if not problems:
        count = 1 if args.page_id else len(list_all())
        print(f"OK: {count} 个页面资产通过校验")
        return 0
    for page_id, found in problems.items():
        print(f"{page_id}:")
        for item in found:
            print(f"  - {item}")
    return 1


def _cmd_catalog(args: argparse.Namespace) -> int:
    catalog = export_catalog()
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"catalog written: {out} ({len(catalog)} pages)")
    else:
        _print_json(catalog)
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    asset = get(args.page_id)
    events, runs = load_events(args.page_id)
    report = build_report(
        args.page_id, events=events, elements=asset.model.elements, runs=runs
    )
    if args.json:
        _print_json(report.to_dict())
    else:
        print(report.render())
        patch = report.suggested_patch()
        if patch:
            print("建议 patch（不会自动改写资产，请人工或 AI 在有证据前提下采纳）:")
            for item in patch:
                print(f"  - {item}")
    return 1 if report.severity == SEVERITY_ERROR else 0


def _cmd_run(args: argparse.Namespace) -> int:
    from .driver import PageDriver
    from .errors import PageTestError

    asset = get(args.page_id)
    model = asset.model
    flow = args.flow
    if args.no_open and not flow:
        print("--no-open 时必须同时指定 --flow", file=sys.stderr)
        return 1
    example: dict[str, Any] = {}
    if flow:
        flow_obj = model.flows.get(flow)
        if flow_obj is None:
            print(
                f"页面 {model.id} 没有 flow {flow!r}；可用: {sorted(model.flows)}",
                file=sys.stderr,
            )
            return 1
        example = dict(flow_obj.example_params)
    params = _load_params(args, example=example)

    try:
        with PageDriver.launch(
            headless=not args.headed,
            base_url=args.base_url,
            slow_mo=args.slow_mo,
        ) as driver:
            invocation = model.set_inputs(params)
            result = (
                invocation.open(driver=driver, timeout_ms=args.timeout_ms)
                if not args.no_open
                else None
            )
            if flow:
                result = invocation.run(
                    flow, driver=driver, timeout_ms=args.timeout_ms
                )
    except PageTestError as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        if getattr(exc, "result", None) is not None:
            _print_json(exc.result.to_dict())
        return 1

    if result is None:  # pragma: no cover - 参数组合已在前面拦截
        print("没有可执行的动作", file=sys.stderr)
        return 1

    _print_json(result.to_dict())
    if result.fallbacks:
        print(
            f"注意: {len(result.fallbacks)} 次命中备用定位器，跑 "
            f"`python -m tuner_testkit.page_test doctor {model.id}` 查看体检报告",
            file=sys.stderr,
        )
    return 0 if result.ok else 1


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(prog="python -m tuner_testkit.page_test")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="列出全部已发现的页面资产")

    p_desc = sub.add_parser("describe", help="查看元素表 / 流程步骤 / 入参 schema")
    p_desc.add_argument("page_id")

    p_val = sub.add_parser("validate", help="静态校验（policy / 元素引用完整性），不启浏览器")
    p_val.add_argument("page_id", nargs="?", help="缺省校验全部")

    p_cat = sub.add_parser("catalog", help="导出全量目录 JSON（平台化数据源）")
    p_cat.add_argument("--out", help="输出文件路径；缺省打印到 stdout")

    p_doc = sub.add_parser("doctor", help="定位器健康度体检 + 建议 patch")
    p_doc.add_argument("page_id")
    p_doc.add_argument("--json", action="store_true", help="输出结构化 JSON")

    p_run = sub.add_parser("run", help="启浏览器执行 open / flow")
    p_run.add_argument("page_id")
    p_run.add_argument("--flow", help="要执行的 flow 名；缺省只 open")
    p_run.add_argument("--params", help="JSON 入参字符串（默认 {}）")
    p_run.add_argument("--params-file", help="JSON 入参文件路径")
    p_run.add_argument("--example", action="store_true", help="用 flow 的 example_params 运行")
    p_run.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    p_run.add_argument("--base-url", help="覆盖 UI base_url")
    p_run.add_argument("--slow-mo", type=float, default=0, help="每步放慢毫秒数（调试用）")
    p_run.add_argument("--timeout-ms", type=int, default=None, help="等待/断言超时")
    p_run.add_argument("--no-open", action="store_true", help="不先执行 open，直接跑 flow")

    args = parser.parse_args(argv)
    handlers = {
        "list": _cmd_list,
        "describe": _cmd_describe,
        "validate": _cmd_validate,
        "catalog": _cmd_catalog,
        "doctor": _cmd_doctor,
        "run": _cmd_run,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
