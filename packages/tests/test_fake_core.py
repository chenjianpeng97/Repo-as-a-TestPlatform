"""packages.fake core / Faker wrappers / seed."""
from __future__ import annotations

from packages.fake import ean13, id_card, phone, run, seed, udi, uuid4


def test_seed_reproducible_sequence():
    seed(1)
    a = [uuid4() for _ in range(3)]
    seed(1)
    b = [uuid4() for _ in range(3)]
    assert a == b


def test_id_card_and_phone_shapes():
    card = id_card()
    assert len(card) == 18
    mobile = phone()
    assert len(mobile) == 11
    assert mobile.isdigit()


def test_uuid4_has_hyphens():
    value = uuid4()
    assert value.count("-") == 4
    assert len(value) == 36


def test_ean13_is_not_udi():
    barcode = ean13()
    assert len(barcode) == 13
    udi_code = udi(with_gs=False)
    assert udi_code.startswith("01")
    assert len(udi_code) != 13


def test_run_count_unique():
    result = run("uscc", count=5, seed=2, unique=True)
    assert result.count == 5
    assert len(set(result.values)) == 5
    assert len(result.display_values) == 5


def test_action_words_generators_reexport():
    from packages.action_words._internal import generators as gen

    assert gen.task_id()
    assert len(gen.digits(8)) == 8
