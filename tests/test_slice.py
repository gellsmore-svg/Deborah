"""Substrate slice: negotiation, outcomes, open questions."""

from __future__ import annotations

from pathlib import Path

from deborah import document_to_plan, parse_document
from deborah.runtime.negotiate import NegotiationMessage, run_negotiation
from deborah.runtime.open_questions import OpenQuestionStore
from deborah.runtime.outcomes import check_outcomes
from deborah.runtime.slice import run_substrate_slice
from deborah.runtime.interpreter import RunResult, StepRecord

ROOT = Path(__file__).resolve().parents[1]
SLICE_PLAN = ROOT / "examples" / "answer-substrate-question.cairn.md"
GOLDEN = ROOT / "examples" / "cross-llm-critique.cairn.md"


def _plan(path: Path = SLICE_PLAN) -> dict:
    return document_to_plan(parse_document(path.read_text(encoding="utf-8")))


def test_negotiation_default_one_shot_agreed() -> None:
    result = run_negotiation(intent="test", assumes=["milcah.critique"], max_rounds=4)
    assert result.status == "agreed"
    assert result.ok
    product = result.as_cognition_result()
    assert product["status"] == "agreed"
    assert product.get("force_agreement") is False


def test_negotiation_exhaustion_is_unresolved() -> None:
    def always_clarify(proposal, history, round_index):
        return NegotiationMessage(
            type="clarification_request",
            role="capability",
            payload={"need": "more context"},
        )

    result = run_negotiation(
        intent="test", max_rounds=2, negotiator=always_clarify
    )
    assert result.status == "unresolved"
    assert result.rounds_used == 2
    assert "exhausted" in (result.reason or "").lower() or result.tradeoffs


def test_negotiation_refusal() -> None:
    def refuse(proposal, history, round_index):
        return NegotiationMessage(
            type="refusal",
            role="capability",
            payload={"reason": "out of scope"},
        )

    result = run_negotiation(intent="x", max_rounds=3, negotiator=refuse)
    assert result.status == "refused"
    assert not result.ok


def test_outcomes_empty_evidence_opens() -> None:
    run = RunResult(
        plan_id="p",
        terminal="complete",
        steps=[
            StepRecord(
                id="1",
                construct="STEP",
                status="completed",
                cognition="observe",
                result={"evidence": []},
            ),
            StepRecord(
                id="2",
                construct="STEP",
                status="completed",
                cognition="infer",
                result={
                    "claim": "c",
                    "evidence_refs": [],
                    "confidence": {"inference": "medium", "evidence": "low", "execution": "high"},
                },
            ),
            StepRecord(
                id="4",
                construct="DECISION",
                status="completed",
                cognition="decide",
                result={"selected": "accept", "committed": True},
            ),
        ],
        events=[],
    )
    check = check_outcomes({"plan_id": "p", "outcomes": ["x"]}, run, confidence_floor="low")
    assert not check.ok
    assert any("evidence" in r for r in check.open_reasons)


def test_outcomes_confidence_floor() -> None:
    run = RunResult(
        plan_id="p",
        terminal="complete",
        steps=[
            StepRecord(
                id="1",
                construct="STEP",
                status="completed",
                cognition="observe",
                result={"evidence": [{"statement": "s", "source": "t", "trace_ref": "1"}]},
            ),
            StepRecord(
                id="2",
                construct="STEP",
                status="completed",
                cognition="infer",
                result={
                    "claim": "c",
                    "evidence_refs": ["1"],
                    "confidence": {
                        "inference": "low",
                        "evidence": "low",
                        "execution": "high",
                    },
                },
            ),
        ],
        events=[],
    )
    check = check_outcomes({}, run, confidence_floor="medium")
    assert not check.confidence_ok
    assert not check.ok


def test_open_question_store_roundtrip(tmp_path: Path) -> None:
    store = OpenQuestionStore(tmp_path / "oq.jsonl")
    from deborah.runtime.open_questions import OpenQuestion

    q = OpenQuestion(question="Is X true?", reason="no evidence", plan_id="p1")
    store.record(q)
    listed = store.list(plan_id="p1")
    assert len(listed) == 1
    assert listed[0].question == "Is X true?"


def test_substrate_slice_demo_path(tmp_path: Path) -> None:
    oq_path = tmp_path / "open.jsonl"
    result = run_substrate_slice(
        _plan(),
        demo=True,
        negotiate=True,
        max_rounds=4,
        open_questions_path=oq_path,
        check_contracts=True,
        confidence_floor="low",
    )
    assert result.negotiation is not None
    assert result.negotiation.status == "agreed"
    assert result.run.terminal in {"complete", "open"}
    assert result.outcomes.to_dict()["floor"] == "low"
    # Demo retrieve produces evidence → structural path should not force empty-evidence open
    if result.run.terminal == "complete" and result.outcomes.ok:
        # may or may not write OQ
        pass
    else:
        assert result.open_question is not None or result.run.terminal == "open"


def test_substrate_slice_unresolved_negotiation(tmp_path: Path) -> None:
    def always_clarify(proposal, history, round_index):
        return NegotiationMessage(
            type="clarification_request",
            role="capability",
            payload={},
        )

    result = run_substrate_slice(
        _plan(GOLDEN),
        demo=True,
        negotiate=True,
        max_rounds=2,
        negotiator=always_clarify,
        open_questions_path=tmp_path / "oq.jsonl",
    )
    assert result.terminal == "open"
    assert result.open_question is not None
    assert (tmp_path / "oq.jsonl").exists()
    assert "exhausted" in result.open_question.reason.lower() or result.negotiation


def test_cli_slice(tmp_path: Path) -> None:
    from deborah.runtime.cli import main

    oq = tmp_path / "oq.jsonl"
    code = main(
        [
            str(SLICE_PLAN),
            "--slice",
            "--estate-demo",
            "--check-contracts",
            "--open-questions",
            str(oq),
            "--question",
            "Is substrate coherence well-supported?",
        ]
    )
    assert code == 0


def test_slice_with_tracer_records_decision_when_galeed_present() -> None:
    try:
        from galeed import EventType, Tracer
    except ImportError:
        import pytest

        pytest.skip("galeed not installed")

    tracer = Tracer(source="deborah-test", session_id="slice-test")
    result = run_substrate_slice(
        _plan(),
        demo=True,
        negotiate=True,
        tracer=tracer,
        check_contracts=True,
    )
    types = [e.type for e in tracer.events]
    assert EventType.NEGOTIATION_STARTED in types
    assert EventType.NEGOTIATION_FINISHED in types
    assert EventType.DECISION_RECORDED in types
    assert result.negotiation is not None
