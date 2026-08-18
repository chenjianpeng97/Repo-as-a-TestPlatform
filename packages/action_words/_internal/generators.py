"""Random / derived value generators for action words.

All randomness lives here so seed words stay declarative and so a single
``random.seed(...)`` (set by a caller) makes a whole run reproducible.
Nothing in this module touches the database.
"""
from __future__ import annotations

import random
import string
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal


def now() -> datetime:
    return datetime.now()


def now_str() -> str:
    """``YYYY-MM-DD HH:MM:SS`` timestamp string (datetime column friendly)."""
    return now().strftime("%Y-%m-%d %H:%M:%S")


def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def date_str(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def random_past_date(*, max_days_ago: int = 365, min_days_ago: int = 0) -> date:
    delta = random.randint(min_days_ago, max_days_ago)
    return date.today() - timedelta(days=delta)


def random_future_date(*, min_days: int = 30, max_days: int = 1095) -> date:
    return date.today() + timedelta(days=random.randint(min_days, max_days))


def digits(n: int) -> str:
    return "".join(random.choices(string.digits, k=n))


def doc_no(prefix: str = "DOC") -> str:
    """Document number like ``DOC-1519793648781230080``."""
    return f"{prefix}-{digits(19)}"


def task_id() -> str:
    """32-char hex task id (UUID without dashes)."""
    return "".join(random.choices("0123456789abcdef", k=32))


def batch_number(*, length: int = 10) -> str:
    """Numeric batch / lot number string."""
    return digits(length)


def money(low: float = 10.0, high: float = 100000.0, *, places: int = 2) -> Decimal:
    """Random monetary ``Decimal`` rounded to ``places`` decimals."""
    raw = Decimal(str(random.uniform(low, high)))
    quant = Decimal(10) ** -places
    return raw.quantize(quant, rounding=ROUND_HALF_UP)


def qty(low: int = 1, high: int = 100) -> int:
    return random.randint(low, high)
