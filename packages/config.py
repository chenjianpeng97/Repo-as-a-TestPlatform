"""Runtime config helpers: named env profiles + API base URL.

Named environments live in gitignored ``config/env_local.py`` as ``ENVIRONMENTS``.
The active name is resolved (first hit wins) from:

1. ``ARGON_ENV`` (process / CI, does not change the repo pointer)
2. ``config/.active_env`` (repo-global pointer; gitignore)
3. ``env_local.ACTIVE_ENV`` (default before the first ``use``)
4. the sole key, if ``ENVIRONMENTS`` has exactly one entry

``python -m packages.config show`` / ``use <name>`` switches the pointer.
Callers still read the merged view on ``config.env``; this module must not
import ``config.env`` at module level (``config.env`` calls into here while
it is still loading).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ARGON_ENV_VAR = "ARGON_ENV"
_PROD_LIKE = frozenset({"prd", "prod", "production"})
_UNSET: Any = object()


class EnvProfileError(RuntimeError):
    """Named-environment catalog is missing, empty, or the active name is invalid."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def active_env_path() -> Path:
    return repo_root() / "config" / ".active_env"


def read_active_env_file(path: Path | None = None) -> str | None:
    p = path or active_env_path()
    try:
        raw = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError:
        return None
    for line in raw.splitlines():
        text = line.strip()
        if text and not text.startswith("#"):
            return text
    return None


def write_active_env(name: str, path: Path | None = None) -> Path:
    chosen = name.strip()
    if not chosen:
        raise EnvProfileError("环境名不能为空")
    p = path or active_env_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(chosen + "\n", encoding="utf-8")
    return p


def environments_of(source: Any) -> dict[str, Any] | None:
    extra = getattr(source, "ENVIRONMENTS", None)
    if isinstance(extra, dict) and extra:
        return extra
    return None


def resolve_active_name(
    *,
    available: Sequence[str],
    module_default: str | None = None,
    environ: Mapping[str, str] | None = None,
    active_file_text: str | None = None,
) -> str:
    names = [str(n) for n in available if str(n).strip()]
    if not names:
        raise EnvProfileError("ENVIRONMENTS 为空")
    known = set(names)
    env_map = os.environ if environ is None else environ

    def _take(raw: str | None) -> str:
        return (raw or "").strip()

    candidates = (
        _take(env_map.get(ARGON_ENV_VAR) if hasattr(env_map, "get") else None),
        _take(active_file_text),
        _take(module_default),
    )
    for chosen in candidates:
        if not chosen:
            continue
        if chosen not in known:
            raise EnvProfileError(
                f"未知环境 {chosen!r}；可用: {sorted(known)}"
            )
        return chosen
    if len(names) == 1:
        return names[0]
    raise EnvProfileError(
        "未选择环境：设置 ARGON_ENV、执行 python -m packages.config use <name>，"
        f"或在 env_local.py 设置 ACTIVE_ENV。可用: {sorted(known)}"
    )


def _merge_databases_into(target_db: dict[str, Any], overlay: Mapping[str, Any]) -> None:
    for alias, cfg in overlay.items():
        if not isinstance(cfg, dict):
            continue
        if alias in target_db:
            target_db[alias] = {**target_db[alias], **cfg}
        else:
            target_db[alias] = dict(cfg)


def apply_profile(target: Any, profile: Mapping[str, Any]) -> None:
    extra = profile.get("DATABASES")
    if isinstance(extra, dict):
        databases = getattr(target, "DATABASES", None)
        if not isinstance(databases, dict):
            target.DATABASES = {}
            databases = target.DATABASES
        _merge_databases_into(databases, extra)
    url = profile.get("TEST_BASE_URL")
    if url:
        target.TEST_BASE_URL = str(url)
    account = profile.get("TEST_ACCOUNT")
    if account:
        target.TEST_ACCOUNT = account


def apply_selected_environment(
    target: Any,
    source: Any,
    *,
    environ: Mapping[str, str] | None = None,
    active_file_path: Path | None = None,
    active_file_text: Any = _UNSET,
) -> str | None:
    """Merge the active named profile from ``source`` onto ``target``.

    Returns the applied name, or ``None`` when ``source`` has no non-empty
    ``ENVIRONMENTS`` (caller should fall back to a flat overlay).
    """

    envs = environments_of(source)
    if envs is None:
        return None
    if active_file_text is _UNSET:
        file_text = read_active_env_file(active_file_path)
    else:
        file_text = active_file_text  # type: ignore[assignment]
    default = getattr(source, "ACTIVE_ENV", None)
    name = resolve_active_name(
        available=list(envs),
        module_default=str(default) if default else None,
        environ=environ,
        active_file_text=file_text,
    )
    profile = envs[name]
    if not isinstance(profile, dict):
        raise EnvProfileError(f"环境 {name!r} 必须是 dict，实际为 {type(profile).__name__}")
    apply_profile(target, profile)
    target.ACTIVE_ENV = name
    return name


def load_env_local() -> Any | None:
    try:
        return __import__("config.env_local", fromlist=["*"])
    except ImportError:
        return None


def get_active_env_name() -> str | None:
    from config import env as env_config

    name = getattr(env_config, "ACTIVE_ENV", None)
    return str(name) if name else None


def get_test_base_url() -> str:
    """Base URL for API execution (host only).

    APIModel assets must store only path (no host). The host is injected at runtime.
    """

    base_url = (os.getenv("TEST_BASE_URL") or "").strip()
    if not base_url:
        from config import env as env_config

        base_url = str(getattr(env_config, "TEST_BASE_URL", "") or "").strip()
    if not base_url:
        # Keep a safe default for local development; tests should override as needed.
        return "http://localhost"
    return base_url.rstrip("/")


def get_ui_base_url() -> str:
    """Base URL for UI execution (host only).

    PageModel assets store only ``url_path`` (no host); the host is injected at
    runtime by ``packages.page_test.driver.PageDriver``. Falls back to the API
    host when the SUT serves UI and API from the same origin.
    """

    base_url = (os.getenv("TEST_UI_BASE_URL") or "").strip()
    if not base_url:
        from config import env as env_config

        base_url = str(getattr(env_config, "TEST_UI_BASE_URL", "") or "").strip()
    if not base_url:
        return get_test_base_url()
    return base_url.rstrip("/")


def _print_profile_summary(name: str, profile: Mapping[str, Any]) -> None:
    url = profile.get("TEST_BASE_URL") or ""
    databases = profile.get("DATABASES") if isinstance(profile.get("DATABASES"), dict) else {}
    aliases = ", ".join(sorted(str(k) for k in databases)) or "(none)"
    print(f"active: {name}")
    print(f"TEST_BASE_URL: {url}")
    print(f"DATABASES aliases: {aliases}")


def _cmd_show(_args: argparse.Namespace) -> int:
    local = load_env_local()
    if local is None:
        print(
            "no config/env_local.py — copy config/env_local.py.example and fill values",
            file=sys.stderr,
        )
        return 1
    envs = environments_of(local)
    if envs is None:
        print("mode: flat (no ENVIRONMENTS)")
        url = getattr(local, "TEST_BASE_URL", "") or ""
        print(f"TEST_BASE_URL: {url}")
        aliases = getattr(local, "DATABASES", None) or {}
        if isinstance(aliases, dict) and aliases:
            print(f"DATABASES aliases: {', '.join(sorted(aliases))}")
        return 0
    try:
        active = resolve_active_name(
            available=list(envs),
            module_default=str(getattr(local, "ACTIVE_ENV", None) or "") or None,
            active_file_text=read_active_env_file(),
        )
    except EnvProfileError as exc:
        print(str(exc), file=sys.stderr)
        print("available: " + ", ".join(sorted(envs)))
        return 1
    print("available:")
    for name in sorted(envs):
        marker = "*" if name == active else " "
        profile = envs[name] if isinstance(envs[name], dict) else {}
        url = profile.get("TEST_BASE_URL") or ""
        print(f"  {marker} {name}  {url}")
    profile = envs[active] if isinstance(envs[active], dict) else {}
    _print_profile_summary(active, profile)
    return 0


def _cmd_use(args: argparse.Namespace) -> int:
    local = load_env_local()
    if local is None:
        print(
            "no config/env_local.py — copy config/env_local.py.example and fill values",
            file=sys.stderr,
        )
        return 1
    envs = environments_of(local)
    if envs is None:
        print(
            "env_local.py 没有 ENVIRONMENTS；无法按名字切换。"
            "请把各套环境收进 ENVIRONMENTS 后再 use。",
            file=sys.stderr,
        )
        return 1
    name = (args.name or "").strip()
    if name not in envs:
        print(f"未知环境 {name!r}；可用: {sorted(envs)}", file=sys.stderr)
        return 1
    if name.lower() in _PROD_LIKE:
        print(f"warning: activating {name!r} (production-like)", file=sys.stderr)
    path = write_active_env(name)
    profile = envs[name] if isinstance(envs[name], dict) else {}
    _print_profile_summary(name, profile)
    print(f"wrote {path} (new processes will pick this up)")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        prog="python -m packages.config",
        description="List or switch the active local named environment (env_local ENVIRONMENTS).",
    )
    sub = parser.add_subparsers(dest="cmd")

    p_show = sub.add_parser("show", help="list named environments and the active one")
    p_show.set_defaults(func=_cmd_show)

    p_use = sub.add_parser("use", help="write config/.active_env (repo-global switch)")
    p_use.add_argument("name", help="environment name defined in env_local.ENVIRONMENTS")
    p_use.set_defaults(func=_cmd_use)

    args = parser.parse_args(argv)
    if not args.cmd:
        return _cmd_show(args)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
