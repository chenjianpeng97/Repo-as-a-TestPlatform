"""CLI for init_repo: scaffold a new repo or manage the release manifest.

    python -m apps.init_repo scaffold <target> [--no-ai] [--overwrite]
    python -m apps.init_repo manifest --write [--version X.Y.Z]
    python -m apps.init_repo manifest --check
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from apps.init_repo import manifest as mf
from apps.init_repo import scaffold as sc


def _cmd_scaffold(args: argparse.Namespace) -> int:
    actions = sc.scaffold(
        pathlib.Path(args.target),
        with_ai=not args.no_ai,
        overwrite=args.overwrite,
    )
    for line in actions:
        print(line)
    print(f"\nScaffolded {len(actions)} entries into {args.target}")
    return 0


def _cmd_manifest(args: argparse.Namespace) -> int:
    if args.write:
        path = mf.write_manifest(version=args.version)
        data = mf.load_manifest() or {}
        print(
            f"Wrote {path.relative_to(mf.REPO_ROOT)} "
            f"(template_version={data.get('template_version')}, "
            f"files={len(data.get('files', {}))})"
        )
        return 0

    if args.check:
        drift = mf.check_drift()
        if drift is None:
            print("No manifest yet — run `manifest --write` first.", file=sys.stderr)
            return 1
        if not drift.any:
            print("No drift: tracked platform assets match the release manifest.")
            return 0
        print("DRIFT detected vs release_manifest.json:", file=sys.stderr)
        for kind, items in (("changed", drift.changed), ("added", drift.added), ("removed", drift.removed)):
            for it in items:
                print(f"  {kind}: {it}", file=sys.stderr)
        print(
            "\nCommon platform assets changed. Use the `release-template` skill to "
            "bump the version and refresh the manifest.",
            file=sys.stderr,
        )
        return 1

    print("nothing to do — pass --write or --check", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m apps.init_repo",
        description="Scaffold a project repo from this template, or manage the release manifest.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sc = sub.add_parser("scaffold", help="create six-layer skeleton (+ platform DNA)")
    p_sc.add_argument("target", help="target directory for the new project repo")
    p_sc.add_argument("--no-ai", action="store_true", help="do not copy .cursor/docs-spec/packages DNA")
    p_sc.add_argument("--overwrite", action="store_true", help="overwrite existing files when copying DNA")
    p_sc.set_defaults(func=_cmd_scaffold)

    p_mf = sub.add_parser("manifest", help="write or check the release manifest")
    p_mf.add_argument("--write", action="store_true", help="(re)generate release_manifest.json")
    p_mf.add_argument("--version", default=None, help="template_version to stamp (default: pyproject version)")
    p_mf.add_argument("--check", action="store_true", help="exit 1 if tracked assets drifted from the manifest")
    p_mf.set_defaults(func=_cmd_manifest)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
