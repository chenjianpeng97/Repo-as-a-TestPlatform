"""定位器健康度与 doctor 体检：让运行时降级可见，但不自动改写资产。"""
from __future__ import annotations

import pytest

from packages.page_test.health import (
    SEVERITY_ERROR,
    SEVERITY_OK,
    SEVERITY_WARN,
    HealthCollector,
    append_events,
    build_report,
    load_events,
)
from packages.page_test.locator import ElementSpec, LocatorEvent, LocatorSpec

ELEMENTS = {
    "username_input": ElementSpec(
        name="username_input",
        locators=(
            LocatorSpec("label", "用户名"),
            LocatorSpec("test_id", "login-username"),
        ),
    )
}


@pytest.fixture(autouse=True)
def _isolated_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("PAGE_TEST_ARTIFACTS_DIR", str(tmp_path / "page_test"))


def _event(outcome: str, used_index: int) -> LocatorEvent:
    signatures = tuple(
        locator.signature() for locator in ELEMENTS["username_input"].locators
    )
    return LocatorEvent(
        element="username_input",
        outcome=outcome,
        page_id="example.login@v1",
        used_index=used_index,
        used=signatures[used_index] if used_index >= 0 else "",
        preferred=signatures[0],
        candidates=signatures,
    )


def test_collector_records_every_resolution():
    collector = HealthCollector()
    collector(_event("primary", 0))
    collector(_event("fallback", 1))

    assert len(collector.snapshot()) == 2
    collector.clear()
    assert collector.snapshot() == ()


def test_primary_hits_report_as_healthy():
    report = build_report(
        "example.login@v1",
        events=[_event("primary", 0)] * 3,
        elements=ELEMENTS,
        runs=3,
    )

    assert report.severity == SEVERITY_OK
    element = report.elements[0]
    assert element.candidates[0].hits == 3
    assert element.candidates[1].hits == 0
    assert report.suggested_patch() == []


def test_dead_primary_locator_is_flagged_with_reorder_advice():
    """首选连续失效但测试仍绿 —— 正是这种「静默腐烂」需要被看见。"""
    report = build_report(
        "example.login@v1",
        events=[_event("fallback", 1)] * 3,
        elements=ELEMENTS,
        runs=3,
    )

    assert report.severity == SEVERITY_WARN
    element = report.elements[0]
    assert element.candidates[0].hits == 0
    assert element.candidates[0].advice == "建议下移或删除"
    assert element.candidates[1].advice == "建议提升为首选"
    assert "首选定位器连续失效" in element.diagnosis

    patch = report.suggested_patch()
    assert len(patch) == 1
    assert patch[0]["action"] == "reorder_locators"
    assert patch[0]["promote"].startswith("test_id=")
    assert patch[0]["demote"].startswith("label=")


def test_all_candidates_missing_escalates_to_error():
    report = build_report(
        "example.login@v1", events=[_event("missing", -1)], elements=ELEMENTS, runs=1
    )

    assert report.severity == SEVERITY_ERROR
    assert report.elements[0].missing == 1
    assert report.suggested_patch()[0]["action"] == "recapture_locators"


def test_structural_problems_are_reported_without_any_run():
    """刚写完资产、还没跑过时也能体检出结构性风险。"""
    fragile_only = {
        "row_delete": ElementSpec(
            name="row_delete",
            locators=(
                LocatorSpec("css", ".row .del", confidence="fragile", note="无 testid"),
            ),
        )
    }
    report = build_report("example.list@v1", elements=fragile_only)

    assert report.runs == 0
    assert report.severity == SEVERITY_WARN
    assert "data-testid" in report.elements[0].diagnosis
    assert report.suggested_patch()[0]["action"] == "request_test_id"


def test_single_candidate_element_is_warned_about_missing_backup():
    """已经是稳定定位器但没有备用时，建议补候选而不是笼统地要 test_id。"""
    single = {
        "banner": ElementSpec(name="banner", locators=(LocatorSpec("test_id", "welcome"),))
    }
    report = build_report("example.login@v1", elements=single)

    assert report.severity == SEVERITY_WARN
    assert "没有备用" in report.elements[0].diagnosis
    assert report.suggested_patch()[0]["action"] == "add_fallback_locator"


def test_healthy_structure_without_runs_does_not_claim_evidence():
    report = build_report("example.login@v1", elements=ELEMENTS)

    assert report.severity == SEVERITY_OK
    assert report.elements[0].diagnosis == "结构合理（多候选齐备），尚无运行数据"
    assert report.suggested_patch() == []


def test_render_omits_hit_counts_when_there_are_no_runs():
    rendered = build_report("example.login@v1", elements=ELEMENTS).render()

    assert "命中" not in rendered
    assert "尚无运行数据" in rendered


def test_events_roundtrip_through_disk_and_count_runs():
    append_events("example.login@v1", [_event("primary", 0), _event("fallback", 1)])
    append_events("example.login@v1", [_event("fallback", 1)])

    events, runs = load_events("example.login@v1")

    assert len(events) == 3
    assert runs == 2
    assert {e.outcome for e in events} == {"primary", "fallback"}
    assert events[0].candidates == tuple(
        locator.signature() for locator in ELEMENTS["username_input"].locators
    )


def test_load_events_returns_empty_for_unknown_page():
    assert load_events("never.seen@v1") == ((), 0)


def test_report_renders_human_readable_text():
    report = build_report(
        "example.login@v1", events=[_event("fallback", 1)] * 3, elements=ELEMENTS, runs=3
    )
    rendered = report.render()

    assert "定位器体检 example.login@v1" in rendered
    assert "基于 3 次运行" in rendered
    assert "命中 0/3" in rendered
    assert "命中 3/3" in rendered
    assert "username_input" in rendered


def test_report_serializes_for_platform_dashboard():
    payload = build_report(
        "example.login@v1", events=[_event("fallback", 1)], elements=ELEMENTS, runs=1
    ).to_dict()

    assert payload["page_id"] == "example.login@v1"
    assert payload["severity"] == SEVERITY_WARN
    assert payload["elements"][0]["candidates"][0]["hits"] == 0
    assert payload["suggested_patch"][0]["action"] == "reorder_locators"
