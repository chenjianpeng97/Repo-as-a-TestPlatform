from __future__ import annotations

from tuner_testkit.action_words.base import ActionCategory, ActionResult, ActionWord
from tuner_testkit.action_words.plane import export_plane_action_words, plane_db_assert, plane_db_seed
from tuner_testkit.action_words.registry import reset_registry_for_tests
from packages.api_objects.plane import plane_apiobject


def setup_function() -> None:
    reset_registry_for_tests()


def teardown_function() -> None:
    reset_registry_for_tests()


class _DummyParams(ActionWord.Params):
    pass


def test_unmarked_register_is_not_exported() -> None:
    from tuner_testkit.action_words.registry import register

    @register
    class LocalOnly(ActionWord):
        """local-only word, not on Plane."""

        word_id = "db_seed.local_only"
        name = "local only"
        category = ActionCategory.DB_SEED
        Params = _DummyParams

        def run(self, params: ActionWord.Params) -> ActionResult:
            return self.Result()

    rows = {row["word_id"]: row for row in export_plane_action_words()}
    assert "db_seed.local_only" not in rows


def test_plane_db_seed_is_exported() -> None:
    @plane_db_seed
    class SeedExample(ActionWord):
        """plane-visible seed."""

        word_id = "db_seed.plane_example"
        name = "plane example"
        category = ActionCategory.DB_SEED
        Params = _DummyParams

        def run(self, params: ActionWord.Params) -> ActionResult:
            return self.Result()

    rows = {row["word_id"]: row for row in export_plane_action_words()}
    assert "db_seed.plane_example" in rows
    seed = rows["db_seed.plane_example"]
    assert seed["plane_kind"] == "db_seed"
    assert seed["plane_runnable"] is True
    assert seed["destructive"] is True
    assert seed["module"] == "packages.action_words"
    assert seed["argv"][:4] == ["python", "-m", "packages.action_words", "run"]
    assert seed["argv_plan"][0]["key"] == "word_id"


def test_plane_db_assert_not_destructive() -> None:
    @plane_db_assert
    class AssertExample(ActionWord):
        """plane-visible assert."""

        word_id = "db_assert.plane_example"
        name = "plane assert"
        category = ActionCategory.DB_ASSERT
        Params = _DummyParams

        def run(self, params: ActionWord.Params) -> ActionResult:
            return self.Result()

    row = next(item for item in export_plane_action_words() if item["word_id"] == "db_assert.plane_example")
    assert row["destructive"] is False
    assert row["plane_kind"] == "db_assert"


def test_wrong_category_rejected() -> None:
    try:

        @plane_db_seed
        class Wrong(ActionWord):
            """mismatch."""

            word_id = "db_assert.wrong"
            name = "wrong"
            category = ActionCategory.DB_ASSERT
            Params = _DummyParams

            def run(self, params: ActionWord.Params) -> ActionResult:
                return self.Result()
    except ValueError as exc:
        assert "requires category=db_seed" in str(exc)
        return
    raise AssertionError("expected ValueError")


def test_plane_apiobject_sets_kind() -> None:
    class _Model:
        method = "POST"
        path = "/invoices"
        name = "create invoice"
        id = "create_invoice"

    marked = plane_apiobject(_Model())
    assert getattr(marked, "_plane_kind") == "api_object"


def test_plane_apiobject_frozen_dataclass() -> None:
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Frozen:
        method: str = "GET"
        path: str = "/"
        name: str = "x"
        id: str = "x"

    marked = plane_apiobject(Frozen())
    assert getattr(marked, "_plane_kind") == "api_object"
