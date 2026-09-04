"""Tests for the :mod:`tuner_testkit.excel` framework helpers.

Scope note: these tests cover the framework-level behaviour (reading xlsx
bytes, header trimming, CSV fallback) — they intentionally do not exercise
any domain model (AuthorizationRecord / whitelist / ...), which belongs in
the project-level tests or the behave step layer.
"""
from __future__ import annotations

import io

import pytest
from openpyxl import Workbook

from tuner_testkit.excel import (
    ExcelError,
    ExcelWorkbook,
    first_sheet_rows,
    read_rows,
    rows_as_records,
)


def _make_xlsx_bytes(
    rows: list[list[object]], *, sheet_name: str = "Sheet1"
) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_from_bytes_reads_header_and_records_from_memory() -> None:
    data = _make_xlsx_bytes(
        [
            ["事业部", "医院省份", "授权书编码"],
            ["介入东部", "山东省", "202603270004JX"],
            ["介入西部", "四川省", "202603250016ZB"],
        ],
        sheet_name="授权列表",
    )

    wb = ExcelWorkbook.from_bytes(data)

    assert [s.name for s in wb.sheets] == ["授权列表"]
    sheet = wb.first_sheet
    assert sheet.header == ("事业部", "医院省份", "授权书编码")
    records = sheet.as_records()
    assert records == [
        {"事业部": "介入东部", "医院省份": "山东省", "授权书编码": "202603270004JX"},
        {"事业部": "介入西部", "医院省份": "四川省", "授权书编码": "202603250016ZB"},
    ]


def test_header_trims_leading_trailing_whitespace() -> None:
    data = _make_xlsx_bytes(
        [
            [" 事业部 ", "\t医院省份", "授权书编码\n"],
            ["介入东部", "山东省", "202603270004JX"],
        ],
        sheet_name="授权列表",
    )

    assert first_sheet_rows(data) == [
        {"事业部": "介入东部", "医院省份": "山东省", "授权书编码": "202603270004JX"}
    ]


def test_read_rows_returns_raw_grid_with_header() -> None:
    data = _make_xlsx_bytes(
        [["A", "B"], ["1", "2"], ["3", ""]],
        sheet_name="Sheet1",
    )
    assert read_rows(data) == [["A", "B"], ["1", "2"], ["3", ""]]


def test_rows_as_records_pads_missing_cells_with_empty_string() -> None:
    data = _make_xlsx_bytes(
        [["A", "B", "C"], ["1", "2"], ["", "", ""]],
        sheet_name="Sheet1",
    )
    assert rows_as_records(data) == [
        {"A": "1", "B": "2", "C": ""},
        {"A": "", "B": "", "C": ""},
    ]


def test_csv_fallback_when_bytes_are_not_xlsx() -> None:
    csv_bytes = "事业部,医院省份\n介入东部,山东省\n".encode("utf-8-sig")
    wb = ExcelWorkbook.from_bytes(csv_bytes)
    assert wb.first_sheet.as_records() == [
        {"事业部": "介入东部", "医院省份": "山东省"}
    ]


def test_empty_bytes_raises() -> None:
    with pytest.raises(ExcelError):
        ExcelWorkbook.from_bytes(b"")
