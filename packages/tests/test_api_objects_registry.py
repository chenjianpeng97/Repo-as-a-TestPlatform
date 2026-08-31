from __future__ import annotations

from pathlib import Path

from packages.api_objects.registry import find_api_model, iter_api_models

ASSET = '''\
"""Test asset."""

from packages.api_test.model import APIModel, AssertOperation

{var} = APIModel(
    id="{ident}",
    name="{name}",
    description="",
    method="{method}",
    path="{path}",
    asserts=[
        AssertOperation(name="http status", jsonpath="$.http_status", operator="eq", expected=200),
    ],
)
'''


def _asset(root: Path, route_dir: str, filename: str, **fields) -> Path:
    target = root / "packages" / "api_objects" / route_dir / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(ASSET.format(**fields), encoding="utf-8")
    return target


def test_discovers_assets_in_route_tree(tmp_path: Path) -> None:
    _asset(
        tmp_path,
        "prod-api/inout/queryItems",
        "POST.v1.py",
        var="query_items_post_v1",
        ident="prod-api.POST./prod-api/inout/queryItems@v1",
        name="query items",
        method="POST",
        path="/prod-api/inout/queryItems",
    )

    refs = iter_api_models(tmp_path)

    assert len(refs) == 1
    assert refs[0].route_key == "POST /prod-api/inout/queryItems"
    assert refs[0].var_name == "query_items_post_v1"
    assert refs[0].file == "packages/api_objects/prod-api/inout/queryItems/POST.v1.py"


def test_route_dirs_that_are_not_python_identifiers_still_load(tmp_path: Path) -> None:
    """``prod-api`` / ``my-service`` are valid URL segments but invalid module names.

    Dotted-import discovery skips them silently; loading by file location must not.
    """
    _asset(
        tmp_path,
        "my-service/v2.1/get-thing",
        "GET.v1.py",
        var="get_thing_get_v1",
        ident="my-service.GET./my-service/get-thing@v1",
        name="get thing",
        method="GET",
        path="/my-service/get-thing",
    )

    refs = iter_api_models(tmp_path)

    assert [ref.route_key for ref in refs] == ["GET /my-service/get-thing"]


def test_init_and_test_files_are_skipped(tmp_path: Path) -> None:
    base = tmp_path / "packages" / "api_objects" / "svc" / "thing"
    base.mkdir(parents=True)
    (base / "GET.v1.py").write_text(
        ASSET.format(
            var="thing_get_v1",
            ident="svc.GET./svc/thing@v1",
            name="thing",
            method="GET",
            path="/svc/thing",
        ),
        encoding="utf-8",
    )
    # Leaf __init__.py re-exports the asset; scanning it would double-count.
    (base / "__init__.py").write_text(
        "from importlib.machinery import SourceFileLoader\n"
        "import pathlib\n"
        "thing_get_v1 = SourceFileLoader('m', str(pathlib.Path(__file__).parent / 'GET.v1.py'))"
        ".load_module().thing_get_v1\n",
        encoding="utf-8",
    )
    (base / "test_thing.py").write_text(
        ASSET.format(
            var="should_be_ignored",
            ident="svc.GET./svc/ignored@v1",
            name="ignored",
            method="GET",
            path="/svc/ignored",
        ),
        encoding="utf-8",
    )

    refs = iter_api_models(tmp_path)

    assert [ref.route_key for ref in refs] == ["GET /svc/thing"]


def test_broken_asset_does_not_abort_the_scan(tmp_path: Path) -> None:
    _asset(
        tmp_path,
        "svc/good",
        "GET.v1.py",
        var="good_get_v1",
        ident="svc.GET./svc/good@v1",
        name="good",
        method="GET",
        path="/svc/good",
    )
    broken = tmp_path / "packages" / "api_objects" / "svc" / "bad" / "GET.v1.py"
    broken.parent.mkdir(parents=True)
    broken.write_text("raise RuntimeError('boom at import time')\n", encoding="utf-8")

    refs = iter_api_models(tmp_path)

    assert [ref.route_key for ref in refs] == ["GET /svc/good"]


def test_missing_package_dir_returns_empty(tmp_path: Path) -> None:
    assert iter_api_models(tmp_path) == []


def test_find_api_model_matches_exact_method_and_path(tmp_path: Path) -> None:
    _asset(
        tmp_path,
        "svc/thing",
        "POST.v1.py",
        var="thing_post_v1",
        ident="svc.POST./svc/thing@v1",
        name="thing",
        method="POST",
        path="/svc/thing",
    )

    assert find_api_model("POST", "/svc/thing", root=tmp_path) is not None
    assert find_api_model("GET", "/svc/thing", root=tmp_path) is None
