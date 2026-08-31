"""Random / derived value generators for action words.

Implementation lives in ``packages.fake``. This module re-exports the
historical names so ``from packages.action_words._internal import generators``
keeps working.
"""
from __future__ import annotations

from packages.fake import (
    batch_number,
    date_str,
    digits,
    doc_no,
    money,
    now,
    now_str,
    qty,
    random_future_date,
    random_past_date,
    task_id,
    today_str,
)

__all__ = [
    "batch_number",
    "date_str",
    "digits",
    "doc_no",
    "money",
    "now",
    "now_str",
    "qty",
    "random_future_date",
    "random_past_date",
    "task_id",
    "today_str",
]
