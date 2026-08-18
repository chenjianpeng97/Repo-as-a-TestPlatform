from __future__ import annotations

import os


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

