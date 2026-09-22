#!/usr/bin/env python
"""Deterministic secret scan for staged files (pre-commit) — AGENTS.md §5 hard constraint.

Looks for **values** that look like credentials, not for the words themselves:
bearer/basic auth headers, JWTs, private key blocks, cookie headers, cloud
access keys, and ``password = <8+ chars>`` style assignments whose value is not
an obvious placeholder (``{{password}}``, ``***``, ``CHANGE_ME``, ``replace-me``,
``<...>``, ``$VAR``).

Usage::

    python tools/git-hooks/secret_scan.py            # scan staged files
    python tools/git-hooks/secret_scan.py path ...   # scan given files

``TUNER_COMMIT_STAGED`` (newline-separated paths) replaces ``git diff --cached``
for tests. A line ending with ``secret-scan: allow`` is skipped. Findings are
printed masked (never the secret itself). Exit 0 = clean, 1 = findings.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

STAGED_ENV = "TUNER_COMMIT_STAGED"
ALLOW_MARKER = "secret-scan: allow"
MAX_BYTES = 2_000_000
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".whl", ".pyc", ".lock", ".ico", ".woff", ".woff2"}
SKIP_NAMES = {"uv.lock", "secret_scan.py"}
PLACEHOLDER_RE = re.compile(
    r"^(\{\{.*\}\}|\*+|<[^>]*>|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|CHANGE_?ME|changeme|replace-me|replace_me|xxx+|your[-_][a-z_]+|placeholder|none|null|true|false|dummy|example)$",
    re.I,
)

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bearer/basic auth header", re.compile(r"(?i)authorization\s*[:=]\s*[\"']?(bearer|basic)\s+[A-Za-z0-9._\-+/=]{16,}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("aws access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("cookie header", re.compile(r"(?i)\b(set-cookie|cookie)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]+=[^;\s\"']{12,}")),
    ("slack/github/openai token", re.compile(r"\b(xox[abpr]-[A-Za-z0-9-]{10,}|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,})\b")),
]
# Credential-looking assignments. In code files only *quoted string literals* count
# (`password = args.password` / `token: str` are code, not secrets); in config-like
# files (yaml / json / ini / env / toml …) unquoted values count too. Markdown is prose
# and only gets the high-signal PATTERNS above.
_KEY = r"(?:^|[^A-Za-z0-9])[A-Za-z0-9_-]*(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|client[_-]?secret)[A-Za-z0-9_-]*"
ASSIGNMENT_QUOTED_RE = re.compile(rf"(?i){_KEY}\s*[:=]\s*[\"'](?P<value>[^\"']{{8,}})[\"']")
ASSIGNMENT_ANY_RE = re.compile(rf"(?i){_KEY}\s*[:=]\s*[\"']?(?P<value>[^\s\"',;#]{{8,}})")
CONFIG_SUFFIXES = {".yaml", ".yml", ".json", ".ini", ".env", ".toml", ".cfg", ".conf", ".properties", ".txt", ".jsonl"}
PROSE_SUFFIXES = {".md", ".rst", ".mdc"}


def _staged_files() -> list[str]:
    injected = os.environ.get(STAGED_ENV)
    if injected is not None:
        return [line.strip() for line in injected.splitlines() if line.strip()]
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def _should_skip(path: Path) -> bool:
    return path.suffix.lower() in SKIP_SUFFIXES or path.name in SKIP_NAMES


def _mask(text: str) -> str:
    return text[:4] + "…" if len(text) > 4 else "…"


def scan_text(text: str, rel: str) -> list[str]:
    findings: list[str] = []
    suffix = Path(rel).suffix.lower()
    if suffix in PROSE_SUFFIXES or (suffix == "" and Path(rel).name.startswith(".")):
        assignment_re: re.Pattern[str] | None = None
    elif suffix in CONFIG_SUFFIXES or Path(rel).name.startswith(".env"):
        assignment_re = ASSIGNMENT_ANY_RE
    else:
        assignment_re = ASSIGNMENT_QUOTED_RE
    for lineno, line in enumerate(text.splitlines(), start=1):
        if ALLOW_MARKER in line:
            continue
        for label, pattern in PATTERNS:
            match = pattern.search(line)
            if match:
                findings.append(f"{rel}:{lineno}: {label} ({_mask(match.group(0))})")
                break
        else:
            if assignment_re is None:
                continue
            match = assignment_re.search(line)
            if match:
                value = match.group("value").strip()
                if not PLACEHOLDER_RE.match(value) and not value.startswith(("{{", "${", "os.environ", "env(", "getenv")):
                    findings.append(f"{rel}:{lineno}: credential-looking assignment `{match.group(1)}` ({_mask(value)})")
    return findings


def scan_paths(paths: list[str]) -> list[str]:
    findings: list[str] = []
    for rel in paths:
        path = Path(rel)
        if not path.is_file() or _should_skip(path):
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:8000]:
            continue  # binary
        findings.extend(scan_text(raw.decode("utf-8", errors="replace"), rel.replace("\\", "/")))
    return findings


def main(argv: list[str]) -> int:
    paths = argv[1:] or _staged_files()
    findings = scan_paths(paths)
    if not findings:
        return 0
    print("[x] secret-scan: possible credentials in staged files (values masked):", file=sys.stderr)
    for item in findings:
        print(f"  {item}", file=sys.stderr)
    print(
        "  Move the value to config/env_local.py / *.local.yaml / environment variables, or append "
        f"`# {ALLOW_MARKER}` to a line that is a documented placeholder.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
