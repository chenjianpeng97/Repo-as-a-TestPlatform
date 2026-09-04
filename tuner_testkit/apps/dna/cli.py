"""CLI: sync / check / bundle tuner-testkit DNA into a project repo."""

from __future__ import annotations

import argparse
import hashlib
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
from tuner_testkit.project import ProjectRootError, project_root


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _target_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    return project_root()


def cmd_sync(args: argparse.Namespace) -> int:
    try:
        source = dna_source_root()
        dest = _target_root(args.target)
    except (DnaSourceError, ProjectRootError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    copied = 0
    skipped = 0
    for rel, src in iter_dna_files(source):
        dst = dest / rel
        if dst.exists() and not args.overwrite:
            if dst.is_file() and src.read_bytes() == dst.read_bytes():
                skipped += 1
                continue
            if dst.is_file() and not args.overwrite:
                skipped += 1
                continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
        print(f"copy {rel}")
    print(f"dna sync: copied={copied} skipped={skipped} dest={dest}")
    marker = dest / ".tuner-dna-version"
    marker.write_text(_kit_version() + "\n", encoding="utf-8")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    try:
        source = dna_source_root()
        dest = _target_root(args.target)
    except (DnaSourceError, ProjectRootError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    missing: list[str] = []
    changed: list[str] = []
    for rel, src in iter_dna_files(source):
        dst = dest / rel
        if not dst.is_file():
            missing.append(rel)
            continue
        if _hash_bytes(src.read_bytes()) != _hash_bytes(dst.read_bytes()):
            changed.append(rel)
    if not missing and not changed:
        print("DNA matches installed kit payload.")
        return 0
    for rel in missing:
        print(f"  missing: {rel}", file=sys.stderr)
    for rel in changed:
        print(f"  changed: {rel}", file=sys.stderr)
    print("Run `tuner-dna sync` to refresh platform DNA.", file=sys.stderr)
    return 1


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
        description="Sync Cursor/git DNA from tuner-testkit into a project repo.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sync = sub.add_parser("sync", help="copy DNA files into the project")
    p_sync.add_argument("--target", default=None, help="project root (default: cwd project)")
    p_sync.add_argument("--overwrite", action="store_true", help="overwrite differing files")
    p_sync.set_defaults(func=cmd_sync)

    p_check = sub.add_parser("check", help="report DNA drift vs the kit payload")
    p_check.add_argument("--target", default=None)
    p_check.set_defaults(func=cmd_check)

    p_bundle = sub.add_parser("bundle", help="copy DNA into the wheel payload directory")
    p_bundle.set_defaults(func=cmd_bundle)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
