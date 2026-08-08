"""Phased plan split + post-retrieve negotiation."""

from __future__ import annotations

from pathlib import Path

from deborah import document_to_plan, parse_document
from deborah.runtime.negotiate import post_retrieve_negotiator, run_negotiation
from deborah.runtime.phased import (
    evidence_stats_from_artifacts,
    merge_run_results,
    split_plan_at_critique,
)
from deborah.runtime.interpreter import RunResult, StepRecord
from deborah.runtime.slice import run_substrate_slice

ROOT = Path(__file__).resolve().parents[1]
SLICE_PLAN = ROOT / "examples" / "answer-substrate-question.cairn.md"


def _plan() -> dict:
    return document_to_plan(parse_document(SLICE_PLAN.read_text(encoding="utf-8")))


def test_split_plan_at_critique_substrate() -> None:
    pre, post = split_plan_at_critique(_plan())
    assert len(pre["steps"]) == 3  # novel, retrieve, infer
    assert len(post["steps"]) == 4  # critique, intent, confidence, decide
    pre_actions = " ".join(str(s.get("action") or "") for s in pre["steps"]).lower()
    post_actions = " ".join(str(s.get("action") or "") for s in post["steps"]).lower()
    assert "detect_novel" in pre_actions or "retrieve" in pre_actions
    assert "critique" in post_actions
    assert "decide" in post_actions or any(
        str(s.get("construct") or "").upper() == "DECISION" for s in post["steps"]
    )


def test_split_without_critique_puts_all_in_pre() -> None:
    plan = {
        "plan_id": "p",
        "revision": 1,
        "objective": "x",
        "status": "active",
        "steps": [
            {"id": "1", "construct": "STEP", "action": "do", "status": "pending"},
        ],
        "stopping_conditions": ["done"],
        "revision_decision": "stable",
    }
    pre, post = split_plan_at_critique(plan)
    assert len(pre["steps"]) == 1
    assert post["steps"] == []


def test_evidence_stats_from_artifacts() -> None:
    stats = evidence_stats_from_artifacts(
        {
            "s1": {"novel_detected": True, "novel": ["foo"]},
            "s2": {"evidence": [{"statement": "a"}, {"statement": "b"}]},
        }
    )
    assert stats["evidence_count"] == 2
    assert stats["novel_detected"] is True
    assert "foo" in stats["novel_terms"]


def test_post_retrieve_negotiator_partial_on_empty() -> None:
    result = run_negotiation(
        intent="ground claim",
        claim="Is X true?",
        assumes=["milcah.critique"],
        max_rounds=1,
        negotiator=lambda p, h, r: post_retrieve_negotiator(
            {**p, "evidence_count": 0, "novel_detected": False}, h, r
        ),
    )
    assert result.status == "partial"


def test_post_retrieve_negotiator_accepts_with_evidence() -> None:
    result = run_negotiation(
        intent="ground claim",
        claim="Is X true?",
        max_rounds=1,
        negotiator=lambda p, h, r: post_retrieve_negotiator(
            {**p, "evidence_count": 3, "novel_detected": False}, h, r
        ),
    )
    assert result.status == "agreed"


def test_merge_run_results() -> None:
    a = RunResult(
        plan_id="p",
        terminal="complete",
        steps=[StepRecord(id="1", construct="STEP", status="completed")],
        events=[{"type": "a"}],
    )
    b = RunResult(
        plan_id="p_post",
        terminal="open",
        steps=[StepRecord(id="2", construct="CALL", status="completed")],
        events=[{"type": "b"}],
        unresolved=["gap"],
    )
    merge_run_results(a, b)
    assert len(a.steps) == 2
    assert a.terminal == "open"
    assert a.unresolved == ["gap"]
    assert len(a.events) == 2


def test_substrate_slice_post_retrieve_events(tmp_path: Path) -> None:
    result = run_substrate_slice(
        _plan(),
        demo=True,
        negotiate=True,
        negotiator_name="accept",
        post_retrieve_negotiate=True,
        open_questions_path=tmp_path / "oq.jsonl",
        check_contracts=True,
        confidence_floor="low",
    )
    types = [e.get("type") for e in result.events]
    assert "slice.phase.split" in types
    assert "slice.post_retrieve_negotiation.finished" in types
    assert result.post_retrieve_negotiation is not None
    assert result.post_retrieve_negotiation.status in {"agreed", "partial"}
    # Pre + post steps should both appear
    assert len(result.run.steps) >= 4


def test_substrate_slice_can_disable_post_retrieve() -> None:
    result = run_substrate_slice(
        _plan(),
        demo=True,
        negotiate=True,
        negotiator_name="accept",
        post_retrieve_negotiate=False,
        check_contracts=True,
    )
    types = [e.get("type") for e in result.events]
    assert "slice.phase.split" not in types
    assert result.post_retrieve_negotiation is None
