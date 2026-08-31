"""packages.fake CLI — list / describe / run / catalog.

用法::

    uv run python -m packages.fake list
    uv run python -m packages.fake describe udi
    uv run python -m packages.fake run udi --count 10 --set with_gs=true
    uv run python -m packages.fake run uscc --count 5 --seed 1
    uv run python -m packages.fake catalog --out -
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from packages.fake.catalog import catalog, describe, get, run


def _print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _parse_set_value(raw: str) -> Any:
    lowered = raw.lower()
    if lowered in {"true", "yes", "on"}:
        return True
    if lowered in {"false", "no", "off"}:
        return False
    if lowered in {"null", "none"}:
        return None
    if raw.isdigit() or (raw.startswith("-") and raw[1:].isdigit()):
        return int(raw)
    try:
        return float(raw)
    except ValueError:
        return raw


def _merge_inputs(params: dict[str, Any], sets: list[str]) -> dict[str, Any]:
    merged = dict(params)
    for item in sets:
        if "=" not in item:
            raise SystemExit(f"--set 需要 k=v，收到: {item}")
        key, value = item.split("=", 1)
        merged[key.strip()] = _parse_set_value(value)
    return merged


def _cmd_list(_args: argparse.Namespace) -> int:
    rows = [
        {"id": item["id"], "name": item["name"], "category": item["category"]}
        for item in catalog()
    ]
    _print_json(rows)
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    _print_json(describe(args.fake_id))
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    get(args.fake_id)  # fail fast with KeyError
    if args.params_file:
        raw = json.loads(Path(args.params_file).read_text(encoding="utf-8"))
    else:
        raw = json.loads(args.params or "{}")
    if not isinstance(raw, dict):
        raise SystemExit("--params 必须是 JSON object")
    inputs = _merge_inputs(raw, args.set or [])
    try:
        result = run(
            args.fake_id,
            count=args.count,
            inputs=inputs,
            seed=args.seed,
            unique=args.unique,
            gs_repr=args.gs_repr,
        )
    except (KeyError, ValueError, RuntimeError) as exc:
        _print_json({"ok": False, "error": str(exc)})
        return 1

    if args.format == "json":
        _print_json(result.model_dump(mode="json"))
        return 0
    for line in result.display_values:
        print(line)
    return 0


def _cmd_catalog(args: argparse.Namespace) -> int:
    data = catalog()
    if args.out and args.out != "-":
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"catalog written: {out} ({len(data)} generators)")
    else:
        _print_json(data)
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(prog="python -m packages.fake")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="列出全部已注册生成器")

    p_desc = sub.add_parser("describe", help="查看某个生成器的 schema / 样例")
    p_desc.add_argument("fake_id")

    p_run = sub.add_parser("run", help="生成 count 条假数据")
    p_run.add_argument("fake_id")
    p_run.add_argument("--count", type=int, default=1, help="条数（默认 1，最大 1000）")
    p_run.add_argument("--params", help="JSON Inputs 对象（默认 {}）")
    p_run.add_argument("--params-file", help="JSON Inputs 文件")
    p_run.add_argument("--set", action="append", dest="set", help="k=v，可重复；覆盖 --params")
    p_run.add_argument("--seed", type=int, default=None, help="可复现种子")
    p_run.add_argument(
        "--unique",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="批量去重（默认开；--no-unique 关闭）",
    )
    p_run.add_argument("--format", choices=("lines", "json"), default="lines")
    p_run.add_argument(
        "--gs-repr",
        choices=("escape", "raw"),
        default="escape",
        help="UDI 的 GS 显示：escape 写成 \\x1d；raw 输出真字节",
    )

    p_cat = sub.add_parser("catalog", help="导出全量目录 JSON（平台化数据源）")
    p_cat.add_argument("--out", help="输出文件；缺省或 - 打印到 stdout")

    args = parser.parse_args(argv)
    handlers = {
        "list": _cmd_list,
        "describe": _cmd_describe,
        "run": _cmd_run,
        "catalog": _cmd_catalog,
    }
    try:
        return handlers[args.command](args)
    except KeyError as exc:
        _print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
