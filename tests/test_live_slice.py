"""Live estate slice smoke — skip when Tirzah Mongo is unreachable.

Heavy retrieval (vector / Hoglah / large corpus) can block for minutes. Live
tests inject a **fast** search stub by default so the suite finishes; set
``DEBORAH_LIVE_REAL_RETRIEVE=1`` to exercise the real pipeline (may hang on
embeddings or Hoglah).
"""

from __future__ import annotations

import os
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


def _fast_dispatch(db) -> dict:
    """Tirzah retrieve with injectable empty search (no embedding / Hoglah)."""
    try:
        from tirzah.deborah import deborah_dispatch  # type: ignore[import-not-found]

        def _empty_search(query: str, limit: int = 10):
            return []

        return deborah_dispatch(db=db, search=_empty_search, limit=3)
    except Exception:
        return {}


def test_prepare_live_slice_failsoft_without_tirzah() -> None:
    # Always returns a dict; ok may be false if nothing installed/reachable.
    bits = prepare_live_slice()
    assert "live_ok" in bits
    assert "dispatch" in bits
    assert isinstance(bits["dispatch"], dict)


def test_live_retrieve_dispatch_when_mongo_up() -> None:
    db = _mongo_or_skip()
    if os.environ.get("DEBORAH_LIVE_REAL_RETRIEVE") == "1":
        bits = prepare_live_slice(db=db)
        assert bits["live_ok"]
        handler = bits["dispatch"].get("tirzah.retrieve") or bits["dispatch"].get(
            "retrieve"
        )
    else:
        dispatch = _fast_dispatch(db)
        if not dispatch:
            pytest.skip("tirzah.deborah not importable")
        handler = dispatch.get("tirzah.retrieve") or dispatch.get("retrieve")
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
    if os.environ.get("DEBORAH_LIVE_REAL_RETRIEVE") == "1":
        bits = prepare_live_slice(db=db)
        dispatch = bits.get("dispatch") or {}
    else:
        dispatch = _fast_dispatch(db)
        # Merge milcah / infer / mahalath when available (rule paths).
        try:
            from milcah.deborah import deborah_dispatch as milcah_dispatch  # type: ignore

            dispatch = {**dispatch, **milcah_dispatch()}
        except Exception:
            pass
        try:
            from deborah.runtime.infer import deborah_infer_dispatch

            dispatch = {**dispatch, **deborah_infer_dispatch(use_llm=False)}
        except Exception:
            pass
    result = run_substrate_slice(
        _plan(),
        question="Is relational substrate coherence well-supported by the local corpus?",
        demo=False,
        live=True,
        dispatch=dispatch,
        open_questions_db=db,
        use_live_open_questions=True,
        negotiate=True,
        negotiator_name="accept",  # skip content gate for smoke
        post_retrieve_negotiate=True,
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
