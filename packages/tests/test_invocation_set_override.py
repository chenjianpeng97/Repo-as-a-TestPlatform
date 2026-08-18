from __future__ import annotations

from packages.api_test.model import APIModel


def test_set_query_merges_and_overrides_values():
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

    inv = m.set_query({"pageNum": 2}).set_query({"pageNum": 3})
    assert inv._final_query()["pageNum"] == 3


def test_override_json_rebuild_ignores_set_json_for_non_dict_override():
    m = APIModel(
        id="svc.POST./x@v1",
        name="x",
        description="",
        method="POST",
        path="/x",
        body_schema={"a": {"type": "int", "required": False}},
        headers_policy={"allowlist": ["Accept"], "forbidden": ["Authorization", "Cookie", "Set-Cookie"]},
        auth_policy={"required": False, "strategy": "none"},
    )

    inv = m.set_json({"a": 1}).override_json("raw-body").set_json({"a": 2})
    assert inv._final_json() == "raw-body"

