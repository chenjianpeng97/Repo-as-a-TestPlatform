"""packages.fake China identifiers."""
from __future__ import annotations

from tuner_testkit.fake import company_name, is_valid_uscc, seed, uscc


def test_uscc_checksum_valid():
    seed(1)
    code = uscc()
    assert len(code) == 18
    assert is_valid_uscc(code)
    flipped = code[:-1] + ("0" if code[-1] != "0" else "1")
    assert not is_valid_uscc(flipped)


def test_uscc_region_override():
    code = uscc(region="440300")
    assert code.startswith("91440300")
    assert is_valid_uscc(code)


def test_company_name_kinds():
    generic = company_name(kind="generic")
    medical = company_name(kind="medical_device")
    hospital = company_name(kind="hospital")
    assert generic
    assert any(token in medical for token in ("医疗", "生物", "医用"))
    assert any(token in hospital for token in ("医院", "保健院"))
