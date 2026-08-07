"""Substrate question slice — framed E2E path (architecture Stage 1, thin form).

1. Optional bounded negotiation (control pattern; default one-shot accept)
2. interpret_with_estate (demo or live adapters)
3. Outcome / confidence check
4. Open-question record when residual or unmet outcomes

Does **not** re-plan. Does **not** require Tirzah Mongo unless you pass a store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from deborah.runtime.estate import DictCapabilityIndex, interpret_with_estate
from deborah.runtime.interpreter import RunResult
from deborah.runtime.negotiate import (
    NegotiationResult,
    Negotiator,
    resolve_negotiator,
    run_negotiation,
)
from deborah.runtime.open_questions import (
    OpenQuestion,
    OpenQuestionStore,
    open_question_from_run,
    record_open_question_mongo,
)
from deborah.runtime.outcomes import OutcomeCheck, check_outcomes


@dataclass
class SliceResult:
    """Full substrate-slice output for CLI / tests / Galeed handoff."""

    plan_id: str
    run: RunResult
    outcomes: OutcomeCheck
    negotiation: NegotiationResult | None = None
    open_question: OpenQuestion | None = None
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def terminal(self) -> str:
        if self.open_question is not None and self.run.terminal == "complete":
            # Structural complete but outcomes force open
            if not self.outcomes.ok:
                return "open"
        return self.run.terminal

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "terminal": self.terminal,
            "run": self.run.to_dict(),
            "outcomes": self.outcomes.to_dict(),
            "negotiation": self.negotiation.to_dict() if self.negotiation else None,
            "open_question": self.open_question.to_dict() if self.open_question else None,
            "events": list(self.events),
        }


def run_substrate_slice(
    plan: dict[str, Any],
    *,
    question: str | None = None,
    demo: bool = True,
    live: bool = False,
    negotiate: bool = True,
    max_rounds: int = 4,
    negotiator: Negotiator | None = None,
    negotiator_name: str | None = "auto",
    confidence_floor: str = "low",
    open_questions_path: str | Path | None = None,
    open_questions_db: Any = None,
    check_contracts: bool = True,
    contract_mode: str = "soft",
    dispatch: dict | None = None,
    index: Any = None,
    tracer: Any = None,
    require_evidence: bool = True,
    use_live_open_questions: bool = False,
) -> SliceResult:
    """Execute the substrate critique slice under framed control.

    Parameters
    ----------
    question:
        Overrides plan REQUEST/claim text for this run.
    negotiate:
        When True, run bounded negotiation before interpret.
    negotiator_name:
        ``auto`` (critique when ASSUMES milcah.*), ``accept``, or ``critique``.
        Ignored when ``negotiator`` is injected.
    open_questions_path:
        JSONL path for local open-question persistence.
    open_questions_db:
        Optional Mongo db for ``deborah_open_questions`` collection.
    live:
        When True, load Tirzah/Milcah live dispatch (and Mongo open-questions
        if ``use_live_open_questions`` or ``open_questions_db`` is set).
    use_live_open_questions:
        Auto-bind Tirzah Mongo for open-question persistence when live.
    """
    events: list[dict[str, Any]] = []
    plan = dict(plan)
    claim = (
        question
        or plan.get("request")
        or plan.get("intent")
        or plan.get("objective")
        or ""
    )
    if question:
        plan["request"] = question

    # Live estate bootstrap (Tirzah retrieve + Milcah critique when installed).
    if live and dispatch is None:
        from deborah.runtime.live import prepare_live_slice

        live_bits = prepare_live_slice()
        events.append(
            {
                "type": "slice.live.prepared",
                "live_ok": live_bits.get("live_ok"),
                "error": live_bits.get("error"),
                "has_dispatch": bool(live_bits.get("dispatch")),
            }
        )
        dispatch = live_bits.get("dispatch") or {}
        if open_questions_db is None and (
            use_live_open_questions or live_bits.get("open_questions_db") is not None
        ):
            open_questions_db = live_bits.get("open_questions_db")
        if index is None and live_bits.get("dispatch"):
            idx = DictCapabilityIndex()
            for stem in live_bits["dispatch"]:
                idx.add(stem, product=stem.split(".")[0] if "." in stem else "live")
            # Ensure ASSUMES stems resolve
            for ref in plan.get("assumes") or []:
                if isinstance(ref, str) and ref.strip():
                    stem = ref.strip().split("@", 1)[0]
                    if idx.find(stem) is None:
                        idx.add(stem, product=stem.split(".")[0] if "." in stem else "live")
            index = idx

    negotiation: NegotiationResult | None = None
    if negotiate:
        assumes = list(plan.get("assumes") or [])
        neg = negotiator or resolve_negotiator(negotiator_name, assumes=assumes)
        _emit_negotiation(
            tracer,
            phase="started",
            plan_id=str(plan.get("plan_id") or "unknown"),
            max_rounds=max_rounds,
        )
        negotiation = run_negotiation(
            intent=str(plan.get("intent") or claim or "framed critique"),
            assumes=assumes,
            claim=str(claim),
            context=str(plan.get("context") or ""),
            max_rounds=max_rounds,
            negotiator=neg,
        )
        events.append({"type": "slice.negotiation.finished", **negotiation.to_dict()})
        _emit_negotiation(
            tracer,
            phase="finished",
            plan_id=str(plan.get("plan_id") or "unknown"),
            status=negotiation.status,
            rounds_used=negotiation.rounds_used,
            max_rounds=negotiation.max_rounds,
            reason=negotiation.reason,
        )
        if negotiation.status == "refused":
            run = RunResult(
                plan_id=str(plan.get("plan_id") or "unknown"),
                terminal="refused",
                steps=[],
                events=list(events),
                on_uncertainty=str(plan.get("on_uncertainty") or "record"),
                unresolved=[negotiation.reason or "negotiation refused"],
                errors=[],
            )
            outcomes = check_outcomes(
                plan, run, confidence_floor=confidence_floor, require_evidence=False
            )
            oq = open_question_from_run(
                plan, run, reasons=[negotiation.reason or "negotiation refused"], claim=str(claim)
            )
            _persist_oq(oq, open_questions_path, open_questions_db)
            return SliceResult(
                plan_id=run.plan_id,
                run=run,
                outcomes=outcomes,
                negotiation=negotiation,
                open_question=oq,
                events=events,
            )
        if negotiation.status == "unresolved":
            run = RunResult(
                plan_id=str(plan.get("plan_id") or "unknown"),
                terminal="open",
                steps=[],
                events=list(events),
                on_uncertainty=str(plan.get("on_uncertainty") or "record"),
                unresolved=[negotiation.reason or "negotiation unresolved"],
                errors=[],
            )
            outcomes = check_outcomes(
                plan, run, confidence_floor=confidence_floor, require_evidence=False
            )
            oq = open_question_from_run(
                plan,
                run,
                reasons=[negotiation.reason or "max_rounds exhausted"],
                claim=str(claim),
            )
            _persist_oq(oq, open_questions_path, open_questions_db)
            return SliceResult(
                plan_id=run.plan_id,
                run=run,
                outcomes=outcomes,
                negotiation=negotiation,
                open_question=oq,
                events=events,
            )

    run = interpret_with_estate(
        plan,
        demo=demo and not live,
        live=live,
        dispatch=dispatch,
        index=index,
        tracer=tracer,
        check_contracts=check_contracts,
        contract_mode=contract_mode,
        validate_profile="full",
    )
    events.extend(run.events)

    outcomes = check_outcomes(
        plan,
        run,
        confidence_floor=confidence_floor,
        require_evidence=require_evidence,
    )
    events.append({"type": "slice.outcomes.checked", **outcomes.to_dict()})

    open_q: OpenQuestion | None = None
    should_open = (
        run.terminal in {"open", "refused", "blocked"}
        or not outcomes.ok
        or bool(outcomes.open_reasons)
    )
    # Complete + decision open
    for step in run.steps:
        if (
            str(step.cognition or "").lower() == "decide"
            and isinstance(step.result, dict)
            and str(step.result.get("selected") or "").lower() == "open"
        ):
            should_open = True

    if should_open:
        reasons = list(outcomes.open_reasons)
        if run.terminal != "complete" and run.terminal not in {r for r in reasons}:
            reasons.append(f"terminal={run.terminal}")
        open_q = open_question_from_run(plan, run, reasons=reasons, claim=str(claim))
        _persist_oq(open_q, open_questions_path, open_questions_db)
        events.append({"type": "slice.open_question.recorded", **open_q.to_dict()})

    selected = "open" if open_q is not None else (
        "accept" if run.terminal == "complete" else run.terminal
    )
    for step in run.steps:
        if (
            str(step.cognition or "").lower() == "decide"
            and isinstance(step.result, dict)
            and step.result.get("selected") is not None
        ):
            selected = str(step.result.get("selected")).lower()
            break
    if open_q is not None and selected not in {"open", "reject"}:
        selected = "open"

    _emit_decision(
        tracer,
        selected=selected,
        plan_id=str(plan.get("plan_id") or run.plan_id),
        basis=(
            open_q.reason
            if open_q is not None
            else ("; ".join(outcomes.open_reasons) if outcomes.open_reasons else "outcomes ok")
        ),
        confidence=outcomes.min_band_seen,
        open_question_id=open_q.open_question_id if open_q else None,
        rejected=(
            [x for x in ("accept", "reject", "open") if x != selected]
            if selected
            else []
        ),
    )
    if tracer is not None:
        try:
            from deborah.runtime.estate import record_run_on_tracer

            record_run_on_tracer(run, tracer)
            events.append({"type": "galeed.recorded", "ok": True})
        except Exception:
            pass

    return SliceResult(
        plan_id=str(plan.get("plan_id") or run.plan_id),
        run=run,
        outcomes=outcomes,
        negotiation=negotiation,
        open_question=open_q,
        events=events,
    )


def _persist_oq(
    oq: OpenQuestion,
    path: str | Path | None,
    db: Any,
) -> None:
    if path is not None:
        OpenQuestionStore(path).record(oq)
    if db is not None:
        record_open_question_mongo(db, oq)


def _emit_negotiation(tracer: Any, **kwargs: Any) -> None:
    if tracer is None:
        return
    try:
        from galeed import record_negotiation  # type: ignore[import-not-found]

        record_negotiation(tracer=tracer, **kwargs)
    except Exception:
        pass


def _emit_decision(tracer: Any, **kwargs: Any) -> None:
    if tracer is None:
        return
    try:
        from galeed import record_decision  # type: ignore[import-not-found]

        record_decision(tracer=tracer, **kwargs)
    except Exception:
        pass
