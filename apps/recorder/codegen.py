"""Render APIModel Python source (route-aligned, sanitized)."""

from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from .capture import Capture
from .normalize import asset_var_name, service_from_path

_MAX_LIST_ITEMS = 5
_MAX_STR_LEN = 240
_MAX_DEPTH = 6


def _py_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _py_repr(value: Any, *, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(value, Mapping):
        if not value:
            return "{}"
        lines = ["{"]
        for k, v in value.items():
            lines.append(f"{pad}    {_py_str(str(k))}: {_py_repr(v, indent=indent + 4)},")
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    if isinstance(value, bool):
        return "True" if value else "False"
    if value is None:
        return "None"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return _py_str(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if not value:
            return "[]"
        items = ",\n".join(f"{pad}    {_py_repr(v, indent=indent + 4)}" for v in value)
        return f"[\n{items},\n{pad}]"
    return _py_str(str(value))


def truncate_sample(value: Any, *, depth: int = 0) -> Any:
    """Keep recorded response samples small enough for source files."""
    if depth >= _MAX_DEPTH:
        return "..."
    if isinstance(value, Mapping):
        return {str(k): truncate_sample(v, depth=depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        head = [truncate_sample(v, depth=depth + 1) for v in value[:_MAX_LIST_ITEMS]]
        if len(value) > _MAX_LIST_ITEMS:
            head.append(f"...(+{len(value) - _MAX_LIST_ITEMS} more)")
        return head
    if isinstance(value, str) and len(value) > _MAX_STR_LEN:
        return value[:_MAX_STR_LEN] + "..."
    return value


def _merge_schema(base: Mapping[str, Any], extra: Mapping[str, Any]) -> dict[str, Any]:
    out = {str(k): dict(v) if isinstance(v, Mapping) else v for k, v in base.items()}
    for k, v in extra.items():
        key = str(k)
        if key not in out:
            out[key] = dict(v) if isinstance(v, Mapping) else v
            continue
        if isinstance(out[key], Mapping) and isinstance(v, Mapping):
            merged = dict(out[key])
            if merged.get("type") in (None, "any") and v.get("type"):
                merged["type"] = v["type"]
            out[key] = merged
    return out


def build_assert_ops(capture: Capture) -> list[dict[str, Any]]:
    ops: list[dict[str, Any]] = [
        {
            "name": "http status",
            "jsonpath": "$.http_status",
            "operator": "eq",
            "expected": 200 if 200 <= capture.response_status < 300 else capture.response_status,
        }
    ]
    if capture.response_is_json and isinstance(capture.response_body, Mapping):
        if "code" in capture.response_body:
            code = capture.response_body.get("code")
            if isinstance(code, int):
                ops.append(
                    {
                        "name": "业务码",
                        "jsonpath": "$.code",
                        "operator": "eq",
                        "expected": code,
                    }
                )
        if "data" in capture.response_body:
            ops.append(
                {
                    "name": "data存在",
                    "jsonpath": "$.data",
                    "operator": "exists",
                    "expected": True,
                }
            )
    return ops


def build_extract_ops(capture: Capture) -> list[dict[str, Any]]:
    if not (capture.response_is_json and isinstance(capture.response_body, Mapping)):
        return []
    if "data" not in capture.response_body:
        return []
    return [
        {
            "name": "提取data",
            "jsonpath": "$.data",
            "variable_name": "data",
        }
    ]


def build_response_hints(capture: Capture) -> dict[str, Any]:
    if capture.response_is_json and isinstance(capture.response_body, Mapping):
        return {"top_level_keys": sorted(str(k) for k in capture.response_body.keys())}
    if not capture.response_is_json:
        return {"body": "binary_or_non_json", "note": "use resp.content after execute()"}
    return {}


def recorded_response_dict(capture: Capture) -> dict[str, Any]:
    if capture.response_is_json and capture.response_body is not None:
        return {
            "http_status": capture.response_status,
            "is_json": True,
            "json": truncate_sample(capture.response_body),
        }
    return {
        "http_status": capture.response_status,
        "is_json": False,
        "json": None,
    }


def use_auth_for_replay(capture: Capture) -> bool:
    if not capture.auth_required or capture.auth_strategy == "none":
        return False
    path = capture.normalized_path.rstrip("/").lower()
    if path.endswith("/login") or path.endswith("/logout"):
        return False
    return True


def render_main_block(*, var: str, capture: Capture) -> str:
    """``if __name__ == '__main__'`` replay of the recorded E2E sample."""
    query = dict(capture.query or {})
    body = capture.request_body if capture.method != "GET" else None
    if isinstance(body, Mapping):
        body = dict(body)
    recorded = recorded_response_dict(capture)
    use_auth = use_auth_for_replay(capture)
    file_fields = sorted(str(k) for k in (capture.files_schema or {}).keys())
    is_multipart = capture.body_format == "multipart"

    if is_multipart:
        return f'''
if __name__ == "__main__":
    # Replay the last recorded E2E sample (maintained by apps.recorder).
    # Auth: packages.api_objects.auth (Postman/Apifox-style shared credentials).
    # Multipart: file bytes are never frozen. Set TEST_UPLOAD_FILE (or
    # TEST_UPLOAD_FILE_<FIELD>) to a local path to actually upload.
    import os
    import sys
    from pathlib import Path

    for _root in Path(__file__).resolve().parents:
        if (_root / "pyproject.toml").is_file() and (_root / "packages").is_dir():
            if str(_root) not in sys.path:
                sys.path.insert(0, str(_root))
            break

    from packages.api_objects.auth import (
        assert_recorded_response,
        get_auth,  # noqa: F401 — imported for discoverability / manual tweaks
        replay_execute,
    )

    _RECORDED_PATH = {_py_str(capture.path)}
    _RECORDED_QUERY = {_py_repr(query, indent=4)}
    _RECORDED_BODY = {_py_repr(body, indent=4)}
    _RECORDED_FILE_FIELDS = {_py_repr(file_fields, indent=4)}
    _RECORDED_RESPONSE = {_py_repr(recorded, indent=4)}

    _files = {{}}
    for _field in _RECORDED_FILE_FIELDS:
        _env_key = f"TEST_UPLOAD_FILE_{{_field.upper()}}"
        _path = (os.getenv(_env_key) or os.getenv("TEST_UPLOAD_FILE") or "").strip()
        if _path:
            _files[_field] = _path
    if _RECORDED_FILE_FIELDS and not _files:
        print(
            "SKIP multipart replay: set TEST_UPLOAD_FILE or TEST_UPLOAD_FILE_<FIELD> "
            f"for fields {{_RECORDED_FILE_FIELDS}}"
        )
        raise SystemExit(0)

    _resp = replay_execute(
        {var},
        path=_RECORDED_PATH,
        query=_RECORDED_QUERY,
        body=_RECORDED_BODY,
        files=_files or None,
        use_auth={_py_repr(use_auth)},
    )
    assert_recorded_response(_resp, _RECORDED_RESPONSE)
    print("OK", {var}.method, _RECORDED_PATH, "->", _resp.status_code)
'''

    return f'''
if __name__ == "__main__":
    # Replay the last recorded E2E sample (maintained by apps.recorder).
    # Auth: packages.api_objects.auth (Postman/Apifox-style shared credentials).
    import sys
    from pathlib import Path

    for _root in Path(__file__).resolve().parents:
        if (_root / "pyproject.toml").is_file() and (_root / "packages").is_dir():
            if str(_root) not in sys.path:
                sys.path.insert(0, str(_root))
            break

    from packages.api_objects.auth import (
        assert_recorded_response,
        get_auth,  # noqa: F401 — imported for discoverability / manual tweaks
        replay_execute,
    )

    _RECORDED_PATH = {_py_str(capture.path)}
    _RECORDED_QUERY = {_py_repr(query, indent=4)}
    _RECORDED_BODY = {_py_repr(body, indent=4)}
    _RECORDED_RESPONSE = {_py_repr(recorded, indent=4)}

    _resp = replay_execute(
        {var},
        path=_RECORDED_PATH,
        query=_RECORDED_QUERY,
        body=_RECORDED_BODY,
        use_auth={_py_repr(use_auth)},
    )
    assert_recorded_response(_resp, _RECORDED_RESPONSE)
    print("OK", {var}.method, _RECORDED_PATH, "->", _resp.status_code)
'''


def render_api_model_source(
    *,
    capture: Capture,
    major: int = 1,
    query_schema: Mapping[str, Any] | None = None,
    body_schema: Mapping[str, Any] | None = None,
    files_schema: Mapping[str, Any] | None = None,
    asserts: Sequence[Mapping[str, Any]] | None = None,
    extracts: Sequence[Mapping[str, Any]] | None = None,
    name: str | None = None,
) -> tuple[str, str]:
    """Return ``(variable_name, python_source)``."""
    service = service_from_path(capture.normalized_path)
    var = asset_var_name(capture.method, capture.normalized_path, major)
    asset_id = f"{service}.{capture.method}.{capture.normalized_path}@v{major}"
    display_name = name or f"{capture.method} {capture.normalized_path}"

    q_schema = dict(query_schema if query_schema is not None else capture.query_schema)
    b_schema = dict(body_schema if body_schema is not None else capture.body_schema)
    f_schema = dict(files_schema if files_schema is not None else (capture.files_schema or {}))
    assert_ops = list(asserts if asserts is not None else build_assert_ops(capture))
    extract_ops = list(extracts if extracts is not None else build_extract_ops(capture))
    hints = build_response_hints(capture)

    desc_lines = [
        "inputs:",
        "  - query/body keys captured by apps.recorder (optional unless marked required)",
        "outputs:",
        "  - see response_hints / extracts",
        "notes:",
        "  - 资产按路由对齐；认证由运行时注入，不在此处固化",
        "  - ``__main__`` 回放样本见文末；鉴权见 packages.api_objects.auth",
        f"  - fingerprint: {capture.fp}",
    ]
    if capture.body_format == "multipart":
        desc_lines.append(
            "  - multipart: text fields via set_json; files via set_files (never frozen)"
        )
    if not capture.response_is_json:
        desc_lines.append("  - non-JSON response: consumers should read resp.content after execute()")

    description = "\n".join(desc_lines)

    assert_src = []
    for op in assert_ops:
        assert_src.append(
            "        AssertOperation("
            f"name={_py_str(op['name'])}, "
            f"jsonpath={_py_str(op['jsonpath'])}, "
            f"operator={_py_str(op['operator'])}, "
            f"expected={_py_repr(op['expected'])}"
            "),"
        )
    extract_src = []
    for op in extract_ops:
        extract_src.append(
            "        ExtractVariableOperation("
            f"name={_py_str(op['name'])}, "
            f"jsonpath={_py_str(op['jsonpath'])}, "
            f"variable_name={_py_str(op['variable_name'])}"
            "),"
        )

    body_format_line = ""
    if capture.body_format == "form":
        body_format_line = '    body_format="form",\n'
    elif capture.body_format == "multipart":
        body_format_line = '    body_format="multipart",\n'

    files_schema_line = ""
    if f_schema or capture.body_format == "multipart":
        files_schema_line = f"    files_schema={_py_repr(f_schema, indent=4)},\n"

    main_block = render_main_block(var=var, capture=capture)

    source = f'''\
"""Auto-maintained by apps.recorder — do not commit secrets."""

from packages.api_test.model import APIModel, AssertOperation, ExtractVariableOperation

{var} = APIModel(
    id={_py_str(asset_id)},
    name={_py_str(display_name)},
    description="""
{description}
""".strip(),
    method={_py_str(capture.method)},
    path={_py_str(capture.normalized_path)},
    query_schema={_py_repr(q_schema, indent=4)},
    body_schema={_py_repr(b_schema, indent=4)},
{files_schema_line}{body_format_line}    response_hints={_py_repr(hints, indent=4)},
    headers_policy={{
        "allowlist": ["Accept", "Content-Language", "Accept-Language", "Content-Type"],
        "forbidden": ["Authorization", "Cookie", "Set-Cookie"],
    }},
    auth_policy={{
        "required": {_py_repr(capture.auth_required)},
        "strategy": {_py_str(capture.auth_strategy)},
        "source": {_py_str(capture.auth_source)},
    }},
    asserts=[
{chr(10).join(assert_src)}
    ],
    extracts=[
{chr(10).join(extract_src)}
    ],
)
{main_block}'''
    return var, source


def merge_capture_into_schemas(
    *,
    existing_query: Mapping[str, Any],
    existing_body: Mapping[str, Any],
    capture: Capture,
    existing_files: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        _merge_schema(existing_query, capture.query_schema),
        _merge_schema(existing_body, capture.body_schema),
        _merge_schema(existing_files or {}, capture.files_schema or {}),
    )
