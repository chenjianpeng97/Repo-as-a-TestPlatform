from __future__ import annotations

from pathlib import Path

from apps.recorder.capture import build_capture
from apps.recorder.freeze import ApiObjectFreezer


def _multipart_body(*, boundary: str = "----BoundaryTest") -> bytes:
    # Minimal multipart: text field + file field (binary-ish content must not be frozen)
    parts = [
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="bizType"\r\n\r\n'
            f"1\r\n"
        ).encode("utf-8"),
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="import.xlsx"\r\n'
            f"Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
        ).encode("utf-8")
        + b"PK\x03\x04FAKE_XLSX_BYTES_SHOULD_NOT_APPEAR\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(parts)


def test_capture_multipart_splits_text_and_file_fields():
    raw = _multipart_body()
    cap = build_capture(
        method="POST",
        url="http://example.com/prod-api/inout/import",
        request_headers={
            "Content-Type": "multipart/form-data; boundary=----BoundaryTest",
            "Authorization": "Bearer SECRETTOKEN1234567890ABCDEF",
        },
        request_content=raw,
        response_status=200,
        response_headers={"Content-Type": "application/json"},
        response_content=b'{"code":200,"data":true}',
    )
    assert cap.body_format == "multipart"
    assert cap.request_body == {"bizType": "1"}
    assert "file" in cap.files_schema
    assert cap.files_schema["file"]["type"] == "file"
    assert "FAKE_XLSX" not in str(cap.request_body)
    assert "FAKE_XLSX" not in str(cap.files_schema)
    assert "|files:file" in cap.fp


def test_freeze_multipart_writes_files_schema_without_bytes(tmp_path: Path):
    freezer = ApiObjectFreezer(tmp_path)
    cap = build_capture(
        method="POST",
        url="http://example.com/prod-api/inout/import",
        request_headers={"Content-Type": "multipart/form-data; boundary=----BoundaryTest"},
        request_content=_multipart_body(),
        response_status=200,
        response_headers={"Content-Type": "application/json"},
        response_content=b'{"code":200,"data":true}',
    )
    result = freezer.freeze(cap)
    text = result.path.read_text(encoding="utf-8")
    assert 'body_format="multipart"' in text
    assert "files_schema=" in text
    assert '"file"' in text
    assert "bizType" in text
    assert "FAKE_XLSX_BYTES_SHOULD_NOT_APPEAR" not in text
    assert "_RECORDED_FILE_FIELDS" in text
    assert "TEST_UPLOAD_FILE" in text
