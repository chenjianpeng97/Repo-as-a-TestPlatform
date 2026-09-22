"""CLI: sync / check / bundle tuner-testkit DNA into a project repo."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from tuner_testkit.apps.dna.paths import DNA_PATHS
from tuner_testkit.apps.dna.source import (
    DnaSourceError,
    dna_source_root,
    iter_dna_files,
    payload_package_dir,
)
from tuner_testkit.apps.dna.targets import (
    TARGET_LAYOUTS,
    diff_file_map,
    parse_targets,
    render_target,
    write_file_map,
)
from tuner_testkit.project import ProjectRootError, project_root


def _target_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    return project_root()


def _targets(args: argparse.Namespace) -> list[str]:
    return parse_targets(getattr(args, "ide", None))


def cmd_sync(args: argparse.Namespace) -> int:
    try:
        source = dna_source_root()
        dest = _target_root(args.target)
        targets = _targets(args)
    except (DnaSourceError, ProjectRootError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    for target in targets:
        files = render_target(source, target)
        copied, skipped = write_file_map(dest, files, overwrite=args.overwrite)
        print(f"dna sync[{target}]: copied={copied} skipped={skipped} dest={dest}")
    marker = dest / ".tuner-dna-version"
    marker.write_text(_kit_version() + "\n", encoding="utf-8")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    try:
        source = dna_source_root()
        dest = _target_root(args.target)
        targets = _targets(args)
    except (DnaSourceError, ProjectRootError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    drifted = False
    for target in targets:
        missing, changed = diff_file_map(dest, render_target(source, target))
        if not missing and not changed:
            print(f"DNA[{target}] matches installed kit payload.")
            continue
        drifted = True
        for rel in missing:
            print(f"  [{target}] missing: {rel}", file=sys.stderr)
        for rel in changed:
            print(f"  [{target}] changed: {rel}", file=sys.stderr)
    if drifted:
        print("Run `tuner-dna sync --overwrite [--ide <targets>]` to refresh platform DNA.", file=sys.stderr)
        return 1
    return 0


def cmd_targets(_args: argparse.Namespace) -> int:
    for name, layout in TARGET_LAYOUTS.items():
        print(f"{name:8s} skills={layout.skills_dir or '-':16s} agents={layout.agents_dir or '-':16s} "
              f"instructions={layout.instructions_file or '-':10s} {layout.note}")
    return 0


def cmd_bundle(_args: argparse.Namespace) -> int:
    """Copy DNA into tuner_testkit/apps/dna/dna_payload for wheel builds."""
    try:
        source = dna_source_root()
    except DnaSourceError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    dest = payload_package_dir()
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    count = 0
    for rel, src in iter_dna_files(source):
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        count += 1
    (dest / "MANIFEST.txt").write_text(
        json.dumps({"files": count, "paths": list(DNA_PATHS)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"bundled {count} DNA files into {dest}")
    return 0


def _kit_version() -> str:
    try:
        from tuner_testkit import __version__

        return str(__version__)
    except Exception:  # noqa: BLE001
        return "0.0.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tuner-dna",
        description="Sync AI-IDE / git DNA from tuner-testkit into a project repo (Cursor by default; --ide for others).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    ide_help = "comma-separated IDE targets: cursor (default), claude, agents, codex, all"

    p_sync = sub.add_parser("sync", help="copy / render DNA files into the project")
    p_sync.add_argument("--target", default=None, help="project root (default: cwd project)")
    p_sync.add_argument("--overwrite", action="store_true", help="overwrite differing files")
    p_sync.add_argument("--ide", default=None, help=ide_help)
    p_sync.set_defaults(func=cmd_sync)

    p_check = sub.add_parser("check", help="report DNA drift vs the kit payload")
    p_check.add_argument("--target", default=None)
    p_check.add_argument("--ide", default=None, help=ide_help)
    p_check.set_defaults(func=cmd_check)

    p_targets = sub.add_parser("targets", help="list IDE targets and where each renders")
    p_targets.set_defaults(func=cmd_targets)

    p_bundle = sub.add_parser("bundle", help="copy DNA into the wheel payload directory")
    p_bundle.set_defaults(func=cmd_bundle)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
