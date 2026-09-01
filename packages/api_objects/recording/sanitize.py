"""Sanitize captures so secrets never land in api_objects source."""

from __future__ import annotations

import re
from typing import Any, Mapping, Optional

FORBIDDEN_HEADER_EXACT = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "x-token",
        "proxy-authorization",
    }
)

_SENSITIVE_KEY_RE = re.compile(r"(token|secret|password|session|credential|passwd|pwd)", re.I)
_JWT_RE = re.compile(r"^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")
_LONG_TOKEN_RE = re.compile(r"^[A-Za-z0-9_\-+/=]{32,}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\+?\d{7,15}$")

HEADER_ALLOWLIST = frozenset(
    {
        "content-type",
        "accept",
        "content-language",
        "accept-language",
        "x-request-id",
    }
)


def is_forbidden_header(name: str) -> bool:
    ln = name.lower()
    if ln in FORBIDDEN_HEADER_EXACT:
        return True
    return bool(_SENSITIVE_KEY_RE.search(ln))


def mask_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool) or isinstance(value, (int, float)):
        return value
    if isinstance(value, list):
        return [mask_value(v) for v in value]
    if isinstance(value, Mapping):
        return sanitize_mapping(value)
    text = str(value)
    if _JWT_RE.match(text) or (_LONG_TOKEN_RE.match(text) and len(text) >= 32):
        if len(text) <= 12:
            return "***"
        return f"{text[:4]}***{text[-4:]}"
    if _EMAIL_RE.match(text):
        local, _, domain = text.partition("@")
        keep = local[:2] if len(local) > 2 else "*"
        return f"{keep}***@{domain}"
    if _PHONE_RE.match(text.replace("-", "").replace(" ", "")):
        digits = re.sub(r"\D", "", text)
        return f"{digits[:3]}****{digits[-2:]}" if len(digits) >= 7 else "***"
    return value


def sanitize_mapping(data: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in (data or {}).items():
        key = str(k)
        if _SENSITIVE_KEY_RE.search(key):
            out[key] = "***"
            continue
        out[key] = mask_value(v)
    return out


def sanitize_headers(headers: Optional[Mapping[str, Any]]) -> dict[str, str]:
    """Keep only allowlisted headers; drop all forbidden/sensitive keys."""
    out: dict[str, str] = {}
    for k, v in (headers or {}).items():
        if is_forbidden_header(str(k)):
            continue
        if str(k).lower() not in HEADER_ALLOWLIST:
            continue
        out[str(k)] = str(mask_value(v))
    return out


def detect_auth_strategy(headers: Optional[Mapping[str, Any]]) -> tuple[bool, str, str]:
    """Return ``(required, strategy, source)`` from raw request headers."""
    lower = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
    auth = lower.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return True, "bearer_token", "context.token"
    if "cookie" in lower and lower["cookie"].strip():
        return True, "cookie_session", "context.session"
    if any(is_forbidden_header(k) for k in lower):
        return True, "bearer_token", "context.token"
    return False, "none", "client.default"
