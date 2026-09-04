from __future__ import annotations

import pytest

from tuner_testkit.api_mock.router import PathPattern, RouteTable, path_matches


@pytest.mark.parametrize(
    "pattern, path, expected",
    [
        ("/prod-api/foo", "/prod-api/foo", True),
        ("/prod-api/foo", "/prod-api/bar", False),
        ("/prod-api/foo", "/prod-api/foo/extra", False),
        ("/users/{id}", "/users/123", True),
        ("/users/{id}", "/users/abc", False),
        ("/users/{id}/orders", "/users/7/orders", True),
        ("/items/{uuid}", "/items/3f2504e0-4f89-11d3-9a0c-0305e82c3301", True),
        ("/items/{uuid}", "/items/123", False),
        ("/files/{name}", "/files/report.xlsx", True),
        ("prod-api/foo", "/prod-api/foo", True),
    ],
)
def test_path_matching(pattern: str, path: str, expected: bool) -> None:
    assert path_matches(pattern, path) is expected


def test_literal_pattern_reports_no_placeholders() -> None:
    assert PathPattern("/a/b").is_literal is True
    assert PathPattern("/a/{id}").is_literal is False
    assert PathPattern("/a/{id}/{uuid}").placeholder_count == 2


def test_literal_route_wins_over_placeholder() -> None:
    entries = [
        {"method": "GET", "path": "/users/{id}", "tag": "dynamic"},
        {"method": "GET", "path": "/users/me", "tag": "literal"},
    ]
    table = RouteTable(entries, method_of=lambda e: e["method"], path_of=lambda e: e["path"])

    assert table.match("GET", "/users/me")["tag"] == "literal"
    assert table.match("GET", "/users/42")["tag"] == "dynamic"


def test_fewer_placeholders_wins() -> None:
    entries = [
        {"method": "GET", "path": "/{a}/{b}", "tag": "two"},
        {"method": "GET", "path": "/fixed/{b}", "tag": "one"},
    ]
    table = RouteTable(entries, method_of=lambda e: e["method"], path_of=lambda e: e["path"])

    assert table.match("GET", "/fixed/x")["tag"] == "one"
    assert table.match("GET", "/other/x")["tag"] == "two"


def test_method_is_scoped_and_case_insensitive() -> None:
    entries = [{"method": "post", "path": "/a", "tag": "p"}]
    table = RouteTable(entries, method_of=lambda e: e["method"], path_of=lambda e: e["path"])

    assert table.match("POST", "/a")["tag"] == "p"
    assert table.match("GET", "/a") is None
    assert len(table) == 1
