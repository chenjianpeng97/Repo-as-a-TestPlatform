"""packages.fake medical generators."""
from __future__ import annotations

from datetime import date

from packages.fake.catalog import GS
from packages.fake.medical import gtin14_check_digit, parse_udi, sn_code, strip_gs, udi, unique_code


def test_udi_with_gs_inserts_separator_only_before_ai21():
    code = udi(with_gs=True, di="06938450812307", serial="2510351968", serial_length=10)
    assert GS in code
    assert code.count(GS) == 1
    _before, after = code.split(GS)
    assert after.startswith("21")
    parts = parse_udi(code)
    assert parts.with_gs is True
    assert parts.di == "06938450812307"
    assert parts.serial == "2510351968"


def test_udi_without_gs_same_payload_no_separator():
    kwargs = dict(
        di="06938450812307",
        serial="2510351968",
        serial_length=10,
        batch_number="1025030713",
        production_date=date(2025, 3, 7),
        expiry_date=date(2027, 3, 6),
    )
    with_gs = udi(with_gs=True, **kwargs)
    no_gs = udi(with_gs=False, **kwargs)
    assert GS in with_gs
    assert GS not in no_gs
    assert strip_gs(with_gs) == no_gs
    assert len(with_gs) == len(no_gs) + 1


def test_gtin14_check_digit_roundtrip():
    body = "0693845081230"
    full = body + gtin14_check_digit(body)
    assert len(full) == 14
    assert gtin14_check_digit(full[:13]) == full[13]


def test_unique_code_from_snowflake():
    assert unique_code(snowflake_id=123, length=10) == "0000000123"


def test_sn_code_default_21_digits():
    value = sn_code()
    assert len(value) == 21
    assert value.isdigit()
