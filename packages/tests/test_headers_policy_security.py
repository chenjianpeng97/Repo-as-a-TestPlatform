from __future__ import annotations

import pytest

from tuner_testkit.api_test.errors import HeadersPolicyError
from tuner_testkit.api_test.model import APIModel


def test_set_headers_rejects_non_allowlisted_header():
    m = APIModel(
        id="svc.GET./x@v1",
        name="x",
        description="",
        method="GET",
        path="/x",
        headers_policy={"allowlist": ["Accept"], "forbidden": ["Authorization", "Cookie", "Set-Cookie"]},
        auth_policy={"required": False, "strategy": "none"},
    )

    with pytest.raises(HeadersPolicyError):
        m.set_headers({"X-Not-Allowed": "1"})


def test_set_headers_rejects_forbidden_header():
    m = APIModel(
        id="svc.GET./x@v1",
        name="x",
        description="",
        method="GET",
        path="/x",
        headers_policy={"allowlist": ["Accept"], "forbidden": ["Authorization", "Cookie", "Set-Cookie"]},
        auth_policy={"required": False, "strategy": "none"},
    )

    with pytest.raises(HeadersPolicyError):
        m.set_headers({"Authorization": "Bearer xxx"})

