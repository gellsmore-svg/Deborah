"""Live estate slice smoke — skip when Tirzah Mongo is unreachable."""

from __future__ import annotations

from pathlib import Path

import pytest

from deborah import document_to_plan, parse_document
from deborah.runtime.live import prepare_live_slice, try_tirzah_db
from deborah.runtime.open_questions import list_open_questions_mongo
from deborah.runtime.slice import run_substrate_slice

ROOT = Path(__file__).resolve().parents[1]
SLICE_PLAN = ROOT / "examples" / "answer-substrate-question.cairn.md"


def _mongo_or_skip():
    db = try_tirzah_db()
    if db is None:
        pytest.skip("Tirzah/Mongo not reachable")
    return db


def _plan() -> dict:
    return document_to_plan(parse_document(SLICE_PLAN.read_text(encoding="utf-8")))


def test_prepare_live_slice_failsoft_without_tirzah() -> None:
    # Always returns a dict; ok may be false if nothing installed/reachable.
    bits = prepare_live_slice()
    assert "live_ok" in bits
    assert "dispatch" in bits
    assert isinstance(bits["dispatch"], dict)


def test_live_retrieve_dispatch_when_mongo_up() -> None:
    db = _mongo_or_skip()
    bits = prepare_live_slice(db=db)
    assert bits["live_ok"]
    assert "tirzah.retrieve" in bits["dispatch"] or "retrieve" in bits["dispatch"]

    # Exercise retrieve against the live store (may return empty evidence).
    handler = bits["dispatch"].get("tirzah.retrieve") or bits["dispatch"].get("retrieve")
    assert handler is not None
    out = handler(
        {"construct": "STEP", "cognition": "observe"},
        {"claim": "relational substrate coherence"},
    )
    assert out["status"] in {"completed", "blocked"}
    assert "result" in out
    assert "evidence" in out["result"]


def test_live_slice_records_open_question_in_mongo() -> None:
    db = _mongo_or_skip()
    # Ensure milcah critique handler is available (rule path) or demo fallback.
    bits = prepare_live_slice(db=db)
    result = run_substrate_slice(
        _plan(),
        question="Is relational substrate coherence well-supported by the local corpus?",
        demo=False,
        live=True,
        dispatch=bits.get("dispatch"),
        open_questions_db=db,
        use_live_open_questions=True,
        negotiate=True,
        negotiator_name="accept",  # skip content gate for smoke
        check_contracts=True,
        confidence_floor="low",
        require_evidence=True,
    )
    assert result.negotiation is not None
    assert result.terminal in {"complete", "open", "refused", "blocked"}
    # Residual / open path should persist when outcomes force open or terminal open
    if result.open_question is not None:
        listed = list_open_questions_mongo(
            db, plan_id=result.plan_id, limit=20
        )
        ids = {q.open_question_id for q in listed}
        assert result.open_question.open_question_id in ids
