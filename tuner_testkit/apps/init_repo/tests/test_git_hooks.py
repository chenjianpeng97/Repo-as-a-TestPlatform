"""Deterministic git hooks (tools/git-hooks) — run as plain scripts."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
HOOKS = REPO_ROOT / "tools" / "git-hooks"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, HOOKS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_secret_scan_flags_values_not_words(tmp_path: Path) -> None:
    scan = _load("secret_scan")
    clean = tmp_path / "clean.py"
    clean.write_text(
        'PASSWORD = "{{password}}"\n'
        'token = os.environ["TEST_TOKEN"]\n'
        "# the password field is masked as ***\n"
        'api_key = "CHANGE_ME"\n',
        encoding="utf-8",
    )
    assert scan.scan_paths([str(clean)]) == []
    dirty = tmp_path / "dirty.yaml"
    dirty.write_text(
        "password: Sup3rSecretValue!\n"  # fake fixture — secret-scan: allow
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789\n"  # fake fixture — secret-scan: allow
        "jwt: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U\n"  # secret-scan: allow
        "allowed: Sup3rSecretValue!  # secret-scan: allow\n",
        encoding="utf-8",
    )
    findings = scan.scan_paths([str(dirty)])
    assert len(findings) == 3
    assert not any("Sup3rSecretValue!" in f for f in findings)  # masked output


def test_secret_scan_cli_uses_injected_staged_list(tmp_path: Path) -> None:
    bad = tmp_path / "config.py"
    bad.write_text('DB_PASSWORD = "p@ssw0rd-real"\n', encoding="utf-8")  # fake fixture — secret-scan: allow
    env = {**os.environ, "TUNER_COMMIT_STAGED": str(bad)}
    proc = subprocess.run([sys.executable, str(HOOKS / "secret_scan.py")], env=env, capture_output=True, text=True, cwd=str(tmp_path))
    assert proc.returncode == 1
    assert "credential-looking assignment `PASSWORD`" in proc.stderr
    assert "p@ssw0rd-real" not in proc.stderr  # never echo the secret


def test_validate_commit_msg_scope_coverage(tmp_path: Path) -> None:
    validate = _load("validate_commit_msg")
    msg = tmp_path / "msg.txt"
    msg.write_text("feat(dogfood): add sample tool\n", encoding="utf-8")
    os.environ["TUNER_COMMIT_STAGED"] = "dogfood/apps/sample_tool/cli.py"
    try:
        assert validate.main(["x", str(msg)]) == 0
        os.environ["TUNER_COMMIT_STAGED"] = "dogfood/apps/sample_tool/cli.py\ntuner_testkit/tools/manifest.py"
        assert validate.main(["x", str(msg)]) == 1  # packages layer not covered
        msg.write_text("feat(dogfood,packages): add sample tool\n", encoding="utf-8")
        assert validate.main(["x", str(msg)]) == 0
        msg.write_text("added stuff\n", encoding="utf-8")
        assert validate.main(["x", str(msg)]) == 1
    finally:
        os.environ.pop("TUNER_COMMIT_STAGED", None)
