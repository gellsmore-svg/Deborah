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

from deborah.runtime.estate import interpret_with_estate
from deborah.runtime.interpreter import RunResult
from deborah.runtime.negotiate import NegotiationResult, Negotiator, run_negotiation
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
    confidence_floor: str = "low",
    open_questions_path: str | Path | None = None,
    open_questions_db: Any = None,
    check_contracts: bool = True,
    contract_mode: str = "soft",
    dispatch: dict | None = None,
    index: Any = None,
    tracer: Any = None,
    require_evidence: bool = True,
) -> SliceResult:
    """Execute the substrate critique slice under framed control.

    Parameters
    ----------
    question:
        Overrides plan REQUEST/claim text for this run.
    negotiate:
        When True, run bounded negotiation before interpret (default one-shot).
    open_questions_path:
        JSONL path for local open-question persistence.
    open_questions_db:
        Optional Mongo db for ``deborah_open_questions`` collection.
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

    negotiation: NegotiationResult | None = None
    if negotiate:
        negotiation = run_negotiation(
            intent=str(plan.get("intent") or claim or "framed critique"),
            assumes=list(plan.get("assumes") or []),
            claim=str(claim),
            max_rounds=max_rounds,
            negotiator=negotiator,
        )
        events.append({"type": "slice.negotiation.finished", **negotiation.to_dict()})
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
