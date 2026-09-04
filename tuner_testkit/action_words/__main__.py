"""Action Words CLI — 列出 / 查看 / 一键运行 / 导出目录。

用法::

    uv run python -m tuner_testkit.action_words list
    uv run python -m tuner_testkit.action_words describe db_seed.create_example
    uv run python -m tuner_testkit.action_words run db_seed.create_example --params "{...}"
    uv run python -m tuner_testkit.action_words run db_seed.create_example --params-file p.json
    uv run python -m tuner_testkit.action_words run db_seed.create_example --example
    uv run python -m tuner_testkit.action_words catalog --out report/action_words_catalog.json

``run`` 未提供 ``--params`` 时使用 ``{}``（即全部默认值）；``--example``
使用 word 自带的 ``example_params`` 样例运行。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tuner_testkit.action_words import ActionContext, export_catalog, get, list_all


def _print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _cmd_list(_args: argparse.Namespace) -> int:
    rows = [
        {"word_id": cls.word_id, "name": cls.name, "category": str(cls.category)}
        for cls in list_all()
    ]
    _print_json(rows)
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    _print_json(get(args.word_id).describe())
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    cls = get(args.word_id)
    if args.example:
        raw = dict(cls.example_params)
    elif args.params_file:
        raw = json.loads(Path(args.params_file).read_text(encoding="utf-8"))
    else:
        raw = json.loads(args.params or "{}")

    with ActionContext(username=args.username, password=args.password) as ctx:
        try:
            result = cls(ctx).run_from_dict(raw)
        except AssertionError as exc:
            _print_json({"ok": False, "error": str(exc)})
            return 1
    _print_json(result.model_dump(mode="json"))
    return 0 if result.ok else 1


def _cmd_catalog(args: argparse.Namespace) -> int:
    catalog = export_catalog()
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"catalog written: {out} ({len(catalog)} words)")
    else:
        _print_json(catalog)
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(prog="python -m tuner_testkit.action_words")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="列出全部已注册 action words")

    p_desc = sub.add_parser("describe", help="查看某个 word 的元数据 / 入参 schema / 样例")
    p_desc.add_argument("word_id")

    p_run = sub.add_parser("run", help="一键运行某个 word")
    p_run.add_argument("word_id")
    p_run.add_argument("--params", help="JSON 入参字符串（默认 {}）")
    p_run.add_argument("--params-file", help="JSON 入参文件路径")
    p_run.add_argument("--example", action="store_true", help="使用 example_params 样例运行")
    p_run.add_argument("--username", help="接口登录用户名（覆盖环境变量/配置）")
    p_run.add_argument("--password", help="接口登录密码（覆盖环境变量/配置）")

    p_cat = sub.add_parser("catalog", help="导出全量目录 JSON（平台化数据源）")
    p_cat.add_argument("--out", help="输出文件路径；缺省打印到 stdout")

    args = parser.parse_args(argv)
    handlers = {
        "list": _cmd_list,
        "describe": _cmd_describe,
        "run": _cmd_run,
        "catalog": _cmd_catalog,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
