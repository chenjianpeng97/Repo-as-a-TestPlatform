from __future__ import annotations

from apps.recorder.normalize import (
    fingerprint,
    is_static_request,
    normalize_path,
    service_from_path,
)


def test_normalize_path_int_and_uuid():
    assert normalize_path("/users/123/orders") == "/users/{id}/orders"
    assert (
        normalize_path("/argon/item/550e8400-e29b-41d4-a716-446655440000/detail")
        == "/argon/item/{uuid}/detail"
    )


def test_is_static_js_css():
    assert is_static_request(path="/static/app.js")
    assert is_static_request(path="/assets/main.css")
    assert is_static_request(path="/x", content_type="application/javascript")
    assert is_static_request(path="/x", response_content_type="text/css")
    assert not is_static_request(path="/argon/mainData/getCategoryTree")


def test_fingerprint_stable():
    fp = fingerprint(
        method="get",
        normalized_path="/argon/x",
        query_keys=["b", "a"],
        body_keys_=["z", "y"],
    )
    assert fp == "GET /argon/x?a,b|y,z"


def test_fingerprint_includes_files_keys():
    fp = fingerprint(
        method="post",
        normalized_path="/import",
        query_keys=[],
        body_keys_=["bizType"],
        files_keys_=["file"],
    )
    assert fp == "POST /import?|bizType|files:file"


def test_service_from_path():
    assert service_from_path("/argon/mainData/x") == "argon"
