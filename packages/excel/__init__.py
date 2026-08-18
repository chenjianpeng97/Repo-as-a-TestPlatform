"""Framework-level Excel/CSV reader for test assets.

This module intentionally knows nothing about business domain (授权/经销商/...).
It reads a workbook from bytes or a file path and returns:

- :class:`ExcelWorkbook` / :class:`ExcelSheet` — thin wrappers around openpyxl
- :func:`read_rows` — list[list[str]] for one sheet (header + data rows)
- :func:`first_sheet_rows` — shortcut for the first sheet
- :func:`rows_as_records` — list[dict[str, str]] (header → cell value)

All cell values are coerced to ``str`` (``""`` for empty cells). No date / int
parsing happens here — callers that need typed values must convert explicitly,
keeping the business interpretation out of this framework layer.

When the source bytes are not a valid xlsx (magic check fails), the loader
falls back to a CSV reader (UTF-8 with BOM stripping). This supports servers
that historically served ``.csv`` as the export format.
"""
from __future__ import annotations

from .workbook import (
    ExcelError,
    ExcelSheet,
    ExcelWorkbook,
    first_sheet_rows,
    read_rows,
    rows_as_records,
)

__all__ = [
    "ExcelError",
    "ExcelSheet",
    "ExcelWorkbook",
    "first_sheet_rows",
    "read_rows",
    "rows_as_records",
]
