from __future__ import annotations

import pytest

from tuner_testkit.api_test.errors import SchemaValidationError
from tuner_testkit.api_test.model import APIModel


def test_set_query_autofills_missing_schema_keys_by_default():
    m = APIModel(
        id="svc.GET./x@v1",
        name="x",
        description="",
        method="GET",
        path="/x",
        query_schema={"pageNum": {"type": "int", "required": False}},
        headers_policy={"allowlist": ["Accept"], "forbidden": ["Authorization", "Cookie", "Set-Cookie"]},
        auth_policy={"required": False, "strategy": "none"},
    )

    inv = m.set_query({"pageNum": 1, "pageSize": 10})
    # schema is updated on effective model
    eff = inv._effective_model()
    assert "pageSize" in eff.query_schema
    assert eff.query_schema["pageSize"]["required"] is False


def test_set_query_can_disable_autofill():
    m = APIModel(
        id="svc.GET./x@v1",
        name="x",
        description="",
        method="GET",
        path="/x",
        query_schema={"pageNum": {"type": "int", "required": False}},
        headers_policy={"allowlist": ["Accept"], "forbidden": ["Authorization", "Cookie", "Set-Cookie"]},
        auth_policy={"required": False, "strategy": "none"},
    )

    with pytest.raises(SchemaValidationError):
        m.set_query({"pageSize": 10}, autofill_schema=False)

