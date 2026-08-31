"""定位器健康度与 doctor 体检 —— 让「运行时降级」不被静默吞掉。

多定位器 fallback 本身就是**自愈级别一**：首选失效时自动用备用候选，测试不红。
这带来一个新风险 —— 降级若无人知晓，资产会慢慢腐烂：所有首选都已失效、全靠
最后一个脆弱候选在撑，测试却一路绿灯，直到最后一个候选也失效才集体爆炸。

本模块是**自愈级别二（审计）**：把每次解析结果落盘聚合，输出体检报告与建议
patch。**不做级别三**（自动改写资产源码）—— 工具悄悄改代码没人 review，
等发现时已说不清页面到底改了什么。采纳建议由人或 AI 显式执行。
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .locator import ElementSpec, LocatorEvent

SEVERITY_OK = "ok"
SEVERITY_WARN = "warn"
SEVERITY_ERROR = "error"


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").is_file() and (parent / "packages").is_dir():
            return parent
    return Path.cwd()


def artifacts_dir(*parts: str) -> Path:
    """``artifacts/`` 下的运行产出目录，可用 ``PAGE_TEST_ARTIFACTS_DIR`` 覆盖。"""
    base = (os.getenv("PAGE_TEST_ARTIFACTS_DIR") or "").strip()
    root = Path(base) if base else repo_root() / "artifacts" / "page_test"
    target = root.joinpath(*parts) if parts else root
    target.mkdir(parents=True, exist_ok=True)
    return target


def _health_file(page_id: str) -> Path:
    safe = page_id.replace("/", "_").replace("\\", "_").replace("@", "_at_")
    return artifacts_dir("health") / f"{safe}.jsonl"


@dataclass
class HealthCollector:
    """``resolve_element`` 的 sink：收集本次运行的全部解析事件。

    全量收集（``primary`` 也收），因为体检需要「候选 i 命中 n/m 次」这种比率。
    """

    events: list[LocatorEvent] = field(default_factory=list)

    def __call__(self, event: LocatorEvent) -> None:
        self.events.append(event)

    def snapshot(self) -> tuple[LocatorEvent, ...]:
        return tuple(self.events)

    def clear(self) -> None:
        self.events.clear()


def append_events(page_id: str, events: Iterable[LocatorEvent]) -> Path | None:
    """把一次运行的事件追加到 ``artifacts/page_test/health/<page_id>.jsonl``。"""
    rows = list(events)
    if not rows:
        return None
    run_id = uuid.uuid4().hex[:12]
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    target = _health_file(page_id)
    with target.open("a", encoding="utf-8") as handle:
        for event in rows:
            payload = {"run_id": run_id, "ts": stamp, **event.to_dict()}
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return target


def load_events(page_id: str) -> tuple[tuple[LocatorEvent, ...], int]:
    """读回历史事件，返回 ``(events, runs)``。"""
    target = _health_file(page_id)
    if not target.is_file():
        return (), 0
    events: list[LocatorEvent] = []
    runs: set[str] = set()
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        runs.add(str(payload.pop("run_id", "")))
        payload.pop("ts", None)
        candidates = payload.pop("candidates", []) or []
        try:
            events.append(LocatorEvent(candidates=tuple(candidates), **payload))
        except TypeError:
            continue
    return tuple(events), len(runs)


@dataclass(frozen=True)
class CandidateHealth:
    index: int
    signature: str
    confidence: str
    hits: int
    advice: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "signature": self.signature,
            "confidence": self.confidence,
            "hits": self.hits,
            "advice": self.advice,
        }


@dataclass(frozen=True)
class ElementHealth:
    element: str
    resolutions: int
    missing: int
    candidates: tuple[CandidateHealth, ...]
    diagnosis: str
    severity: str
    #: 建议动作："reorder_locators" | "recapture_locators" | "request_test_id"
    #: | "add_fallback_locator"；``ok`` 时为空
    action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "element": self.element,
            "resolutions": self.resolutions,
            "missing": self.missing,
            "severity": self.severity,
            "diagnosis": self.diagnosis,
            "action": self.action,
            "candidates": [c.to_dict() for c in self.candidates],
        }


@dataclass(frozen=True)
class DoctorReport:
    page_id: str
    runs: int
    events: int
    elements: tuple[ElementHealth, ...] = ()

    @property
    def severity(self) -> str:
        levels = {e.severity for e in self.elements}
        if SEVERITY_ERROR in levels:
            return SEVERITY_ERROR
        if SEVERITY_WARN in levels:
            return SEVERITY_WARN
        return SEVERITY_OK

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_id": self.page_id,
            "runs": self.runs,
            "events": self.events,
            "severity": self.severity,
            "elements": [e.to_dict() for e in self.elements],
            "suggested_patch": self.suggested_patch(),
        }

    def suggested_patch(self) -> list[dict[str, Any]]:
        """结构化建议。**只建议不改码**，由人或 AI 在有证据前提下采纳。"""
        patch: list[dict[str, Any]] = []
        for element in self.elements:
            if element.severity == SEVERITY_OK or not element.action:
                continue
            entry: dict[str, Any] = {
                "element": element.element,
                "action": element.action,
                "reason": element.diagnosis,
            }
            if element.action == "reorder_locators":
                winners = [c for c in element.candidates if c.hits > 0]
                entry["promote"] = winners[0].signature if winners else ""
                entry["demote"] = element.candidates[0].signature
            patch.append(entry)
        return patch

    def render(self) -> str:
        lines = [
            f"定位器体检 {self.page_id}   (基于 {self.runs} 次运行 / {self.events} 个健康事件)",
            "",
        ]
        if not self.elements:
            lines.append("没有可体检的元素。")
            return "\n".join(lines)

        for element in self.elements:
            lines.append(element.element)
            width = max((len(c.signature) for c in element.candidates), default=0)
            for candidate in element.candidates:
                row = f"  [{candidate.index}] {candidate.signature.ljust(width)}"
                if element.resolutions:
                    row += f"   命中 {candidate.hits}/{element.resolutions}"
                if candidate.confidence == "fragile":
                    row += "   confidence=fragile"
                if candidate.advice:
                    row += f"   {candidate.advice}"
                lines.append(row)
            if element.missing:
                lines.append(f"  未命中任何候选: {element.missing} 次")
            marker = {SEVERITY_OK: "正常", SEVERITY_WARN: "诊断", SEVERITY_ERROR: "严重"}[
                element.severity
            ]
            lines.append(f"  {marker}: {element.diagnosis}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"


def _diagnose(
    *,
    name: str,
    spec: ElementSpec | None,
    resolutions: int,
    missing: int,
    hits: dict[int, int],
    signatures: list[str],
    confidences: list[str],
) -> ElementHealth:
    candidates: list[CandidateHealth] = []
    winners = [i for i in range(len(signatures)) if hits.get(i, 0) > 0]
    primary_hits = hits.get(0, 0)

    for index, signature in enumerate(signatures):
        advice = ""
        if resolutions and index == 0 and primary_hits == 0 and winners:
            advice = "建议下移或删除"
        elif winners and index == winners[0] and index > 0:
            advice = "建议提升为首选"
        candidates.append(
            CandidateHealth(
                index=index,
                signature=signature,
                confidence=confidences[index] if index < len(confidences) else "",
                hits=hits.get(index, 0),
                advice=advice,
            )
        )

    only_fragile = bool(spec) and all(
        locator.confidence == "fragile" for locator in (spec.locators if spec else ())
    )
    single_candidate = bool(spec) and len(spec.locators) < 2 if spec else False

    def health(diagnosis: str, severity: str, action: str = "") -> ElementHealth:
        return ElementHealth(
            element=name,
            resolutions=resolutions,
            missing=missing,
            candidates=tuple(candidates),
            diagnosis=diagnosis,
            severity=severity,
            action=action,
        )

    if missing:
        return health(
            f"全部候选均未命中 {missing} 次；页面结构可能已变，需重新采集定位器",
            SEVERITY_ERROR,
            "recapture_locators",
        )
    if resolutions and primary_hits == 0 and winners:
        winner = candidates[winners[0]]
        return health(
            f"首选定位器连续失效，实际靠 [{winner.index}] {winner.signature} 兜住；"
            "页面文案或结构可能已改动",
            SEVERITY_WARN,
            "reorder_locators",
        )
    if only_fragile:
        return health(
            "仅有脆弱候选，缺少稳定定位器；建议请研发补 data-testid",
            SEVERITY_WARN,
            "request_test_id",
        )
    if single_candidate:
        return health(
            "只有一个候选，没有备用；首选失效时会直接失败，建议补一个不同策略的候选",
            SEVERITY_WARN,
            "add_fallback_locator",
        )
    if not resolutions:
        return health("结构合理（多候选齐备），尚无运行数据", SEVERITY_OK)
    return health("首选定位器工作正常", SEVERITY_OK)


def build_report(
    page_id: str,
    *,
    events: Sequence[LocatorEvent] = (),
    elements: Mapping[str, ElementSpec] | None = None,
    runs: int = 0,
) -> DoctorReport:
    """聚合事件 + 静态元素声明，产出体检报告。

    即使没有任何运行事件也能体检出结构性问题（只有脆弱候选、没有备用候选），
    所以刚写完资产就能先跑一次 doctor。
    """
    elements = dict(elements or {})
    names = sorted(set(elements) | {e.element for e in events})

    per_element: list[ElementHealth] = []
    for name in names:
        spec = elements.get(name)
        related = [e for e in events if e.element == name]
        signatures = [locator.signature() for locator in (spec.locators if spec else ())]
        confidences = [locator.confidence for locator in (spec.locators if spec else ())]
        if not signatures and related:
            signatures = list(related[-1].candidates)
            confidences = ["" for _ in signatures]

        hits: dict[int, int] = {}
        missing = 0
        for event in related:
            if event.outcome == "missing":
                missing += 1
                continue
            hits[event.used_index] = hits.get(event.used_index, 0) + 1

        per_element.append(
            _diagnose(
                name=name,
                spec=spec,
                resolutions=len(related),
                missing=missing,
                hits=hits,
                signatures=signatures,
                confidences=confidences,
            )
        )

    return DoctorReport(
        page_id=page_id,
        runs=runs,
        events=len(events),
        elements=tuple(per_element),
    )


__all__ = [
    "SEVERITY_OK",
    "SEVERITY_WARN",
    "SEVERITY_ERROR",
    "CandidateHealth",
    "DoctorReport",
    "ElementHealth",
    "HealthCollector",
    "append_events",
    "artifacts_dir",
    "build_report",
    "load_events",
    "repo_root",
]
