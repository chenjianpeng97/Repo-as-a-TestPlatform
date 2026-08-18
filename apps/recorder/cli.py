"""CLI for the API Object traffic recorder."""

from __future__ import annotations

import argparse
import asyncio
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_OUTPUTS = REPO_ROOT / "packages" / "api_objects"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m apps.recorder",
        description=(
            "Start an HTTP(S) proxy that captures non-static API traffic and "
            "auto-maintains route-aligned API Objects under packages/api_objects "
            "(see docs/spec/api-objects-syntax.md)."
        ),
    )
    p.add_argument(
        "--outputs_dir",
        type=pathlib.Path,
        default=DEFAULT_OUTPUTS,
        help=f"API Objects root directory (default: {DEFAULT_OUTPUTS})",
    )
    p.add_argument(
        "--listen_host",
        default="127.0.0.1",
        help="Proxy bind address (default: 127.0.0.1)",
    )
    p.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Proxy listen port (default: 8080)",
    )
    p.add_argument(
        "--include_host",
        default="",
        help="Only freeze flows whose host contains this substring (optional)",
    )
    p.add_argument(
        "--ssl-insecure",
        action="store_true",
        help="Do not verify upstream TLS certificates (useful for lab envs)",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Less console output",
    )
    return p


def _require_mitmproxy() -> None:
    try:
        import mitmproxy  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "mitmproxy is required for apps.recorder.\n"
            "Install with:  pip install 'mitmproxy>=10'\n"
            "Or:            pip install -e '.[recorder]'"
        ) from exc


async def _run_proxy(args: argparse.Namespace) -> None:
    from mitmproxy.options import Options
    from mitmproxy.tools.dump import DumpMaster

    from apps.recorder.addon import ApiObjectRecorderAddon

    outputs_dir = args.outputs_dir.expanduser().resolve()
    outputs_dir.mkdir(parents=True, exist_ok=True)

    addon = ApiObjectRecorderAddon(
        outputs_dir=outputs_dir,
        include_host=args.include_host or None,
        verbose=not args.quiet,
    )

    opts = Options(
        listen_host=args.listen_host,
        listen_port=args.port,
        ssl_insecure=bool(args.ssl_insecure),
    )
    master = DumpMaster(opts, with_termlog=not args.quiet, with_dumper=False)
    master.addons.add(addon)

    print(f"API Object recorder proxy listening on {args.listen_host}:{args.port}")
    print(f"Writing assets to: {outputs_dir}")
    print("Point the browser / system HTTP(S) proxy here.")
    print("Static .js/.css (and similar assets) are ignored.")
    print("For HTTPS, trust the mitmproxy CA (mitmproxy docs: about:certificates / certutil).")
    print("Ctrl+C to stop.\n")

    try:
        await master.run()
    finally:
        addon.done()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _require_mitmproxy()
    try:
        asyncio.run(_run_proxy(args))
    except KeyboardInterrupt:
        print("\nRecorder stopped.")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
