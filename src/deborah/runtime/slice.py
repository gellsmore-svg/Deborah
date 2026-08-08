"""Substrate question slice — framed E2E path (architecture Stage 1, thin form).

1. Optional bounded negotiation (control pattern; default one-shot accept)
2. Pre-critique interpret (novel / retrieve / infer)
3. Optional post-retrieve negotiation (evidence / novel gate — no re-plan)
4. Post-critique interpret with carried artifacts
5. Outcome / confidence check
6. Open-question record when residual or unmet outcomes

Does **not** re-plan. Does **not** require Tirzah Mongo unless you pass a store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from deborah.runtime.estate import DictCapabilityIndex, interpret_with_estate
from deborah.runtime.interpreter import RunResult
from deborah.runtime.negotiate import (
    NegotiationResult,
    Negotiator,
    post_retrieve_negotiator,
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
from deborah.runtime.phased import (
    evidence_stats_from_artifacts,
    merge_run_results,
    split_plan_at_critique,
)


@dataclass
class SliceResult:
    """Full substrate-slice output for CLI / tests / Galeed handoff."""

    plan_id: str
    run: RunResult
    outcomes: OutcomeCheck
    negotiation: NegotiationResult | None = None
    post_retrieve_negotiation: NegotiationResult | None = None
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
            "post_retrieve_negotiation": (
                self.post_retrieve_negotiation.to_dict()
                if self.post_retrieve_negotiation
                else None
            ),
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
    post_retrieve_negotiate: bool = True,
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
    decisions: dict[str, str] | None = None,
    use_llm_infer: bool = False,
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
    post_retrieve_negotiate:
        When True (default), split at the first critique CALL: run observe/infer,
        then a second bounded gate (evidence/novel), then critique→decide with
        pre-phase artifacts. No free re-planning.
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

    # Demo / default: always attach rule-based infer (+ optional novel stub)
    if dispatch is None:
        dispatch = {}
    if not any(k.endswith("infer") or k == "infer" for k in dispatch):
        from deborah.runtime.infer import deborah_infer_dispatch

        dispatch = {**deborah_infer_dispatch(use_llm=use_llm_infer), **dispatch}

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
            _persist_oq(oq, open_questions_path, open_questions_db, tracer=tracer)
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
            _persist_oq(oq, open_questions_path, open_questions_db, tracer=tracer)
            return SliceResult(
                plan_id=run.plan_id,
                run=run,
                outcomes=outcomes,
                negotiation=negotiation,
                open_question=oq,
                events=events,
            )

    from deborah.runtime.estate import EstateHandler, demo_capability_index, demo_critique_dispatch
    from deborah.runtime.interpreter import StubHandler, interpret_plan
    from deborah.contracts import EXAMPLE_RESULTS

    if demo and not live:
        index = index or demo_capability_index()
        dispatch = {**demo_critique_dispatch(), **(dispatch or {})}
        # Full Milcah portfolio (critique + intent + confidence) when installed
        try:
            from milcah.deborah import deborah_dispatch as milcah_dispatch  # type: ignore[import-not-found]

            dispatch = {**milcah_dispatch(), **dispatch}
        except Exception:
            pass
        try:
            from mahalath.deborah import deborah_dispatch as mahalath_dispatch  # type: ignore[import-not-found]

            dispatch = {**mahalath_dispatch(), **dispatch}
        except Exception:
            # Offline novel: treat all candidates as novel (fail open)
            try:
                from mahalath.deborah import make_novel_concept_handler  # type: ignore[import-not-found]

                h = make_novel_concept_handler(db=None)
                dispatch = {
                    **dispatch,
                    "mahalath.detect_novel": h,
                    "detect_novel": h,
                }
            except Exception:
                pass
        # Infer already in dispatch
        if index is not None and isinstance(index, DictCapabilityIndex):
            for stem in dispatch:
                if index.find(stem) is None:
                    index.add(stem, product=stem.split(".")[0] if "." in stem else "demo")
            for ref in plan.get("assumes") or []:
                if isinstance(ref, str) and ref.strip():
                    stem = ref.strip().split("@", 1)[0]
                    if index.find(stem) is None:
                        index.add(
                            stem,
                            product=stem.split(".")[0] if "." in stem else "demo",
                        )

    interpret_one = _make_interpret(
        plan=plan,
        claim=claim,
        demo=demo,
        live=live,
        dispatch=dispatch,
        index=index,
        tracer=tracer,
        check_contracts=check_contracts,
        contract_mode=contract_mode,
        decisions=decisions,
        confidence_floor=confidence_floor,
        interpret_plan=interpret_plan,
        EstateHandler=EstateHandler,
        StubHandler=StubHandler,
        EXAMPLE_RESULTS=EXAMPLE_RESULTS,
    )

    post_neg: NegotiationResult | None = None
    pre_plan, post_plan = split_plan_at_critique(plan)
    use_phased = (
        post_retrieve_negotiate
        and bool(pre_plan.get("steps"))
        and bool(post_plan.get("steps"))
    )

    if use_phased:
        split_ev = {
            "type": "slice.phase.split",
            "pre_steps": len(pre_plan.get("steps") or []),
            "post_steps": len(post_plan.get("steps") or []),
        }
        events.append(split_ev)
        _emit_slice_event(
            tracer,
            "slice.phase.split",
            summary=(
                f"phase split pre={split_ev['pre_steps']} post={split_ev['post_steps']}"
            ),
            plan_id=str(plan.get("plan_id") or "unknown"),
            pre_steps=split_ev["pre_steps"],
            post_steps=split_ev["post_steps"],
        )
        pre_run = interpret_one(pre_plan)
        events.extend(pre_run.events)
        events.append(
            {
                "type": "slice.phase.pre_complete",
                "terminal": pre_run.terminal,
                "steps": len(pre_run.steps),
            }
        )
        _emit_slice_event(
            tracer,
            "slice.phase.pre_complete",
            summary=f"pre-critique terminal={pre_run.terminal}",
            plan_id=str(plan.get("plan_id") or "unknown"),
            terminal=pre_run.terminal,
            steps=len(pre_run.steps),
        )

        if pre_run.terminal in {"refused", "blocked"}:
            run = pre_run
        else:
            artifacts = {
                str(s.id): s.result
                for s in pre_run.steps
                if s.id and isinstance(s.result, dict)
            }
            stats = evidence_stats_from_artifacts(artifacts)
            events.append({"type": "slice.phase.evidence_stats", **stats})
            _emit_slice_event(
                tracer,
                "slice.phase.evidence_stats",
                summary=(
                    f"evidence={stats.get('evidence_count')} "
                    f"novel={stats.get('novel_detected')}"
                ),
                plan_id=str(plan.get("plan_id") or "unknown"),
                **stats,
            )

            _emit_negotiation(
                tracer,
                phase="started",
                plan_id=str(plan.get("plan_id") or "unknown"),
                max_rounds=1,
                note="post_retrieve",
            )
            # Capability sees evidence/novel stats on the proposal (one-shot).
            post_neg = run_negotiation(
                intent=str(plan.get("intent") or claim or "framed critique"),
                assumes=list(plan.get("assumes") or []),
                claim=str(claim),
                context=json_safe_context(plan.get("context"), stats),
                max_rounds=1,
                negotiator=_stats_bound_post_retrieve(stats),
            )
            events.append(
                {
                    "type": "slice.post_retrieve_negotiation.finished",
                    **post_neg.to_dict(),
                    **stats,
                }
            )
            _emit_negotiation(
                tracer,
                phase="finished",
                plan_id=str(plan.get("plan_id") or "unknown"),
                status=post_neg.status,
                rounds_used=post_neg.rounds_used,
                max_rounds=post_neg.max_rounds,
                reason=post_neg.reason or (post_neg.tradeoffs[0] if post_neg.tradeoffs else None),
                note="post_retrieve",
                metadata={
                    "evidence_count": stats.get("evidence_count"),
                    "novel_detected": stats.get("novel_detected"),
                },
            )

            if post_neg.status == "refused":
                pre_run.terminal = "refused"
                pre_run.unresolved = list(pre_run.unresolved) + [
                    post_neg.reason or "post-retrieve negotiation refused"
                ]
                run = pre_run
            elif post_neg.status == "unresolved":
                pre_run.terminal = "open"
                pre_run.unresolved = list(pre_run.unresolved) + [
                    post_neg.reason or "post-retrieve negotiation unresolved"
                ]
                run = pre_run
            else:
                # agreed or partial → critique phase with carried artifacts
                # Restore original plan_id on post phase for consistent RunResult
                post_for_run = dict(post_plan)
                post_for_run["plan_id"] = plan.get("plan_id") or post_plan.get("plan_id")
                post_run = interpret_one(post_for_run, initial_artifacts=artifacts)
                events.extend(post_run.events)
                events.append(
                    {
                        "type": "slice.phase.post_complete",
                        "terminal": post_run.terminal,
                        "steps": len(post_run.steps),
                        "post_retrieve_status": post_neg.status,
                    }
                )
                run = merge_run_results(pre_run, post_run)
                # Prefer original plan_id on the merged result
                run.plan_id = str(plan.get("plan_id") or run.plan_id)
    else:
        run = interpret_one(plan)
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
    # Novel concepts after retrieve → residual open (empty evidence is already
    # caught by outcomes when require_evidence). Partial alone does not force open.
    if post_neg is not None and post_neg.status == "partial":
        last_payload: dict[str, Any] = {}
        if post_neg.messages:
            last_payload = dict(post_neg.messages[-1].payload or {})
        if last_payload.get("novel_terms") or "novel" in str(
            last_payload.get("note") or ""
        ).lower():
            should_open = True

    if should_open:
        reasons = list(outcomes.open_reasons)
        if run.terminal != "complete" and run.terminal not in {r for r in reasons}:
            reasons.append(f"terminal={run.terminal}")
        if post_neg is not None and post_neg.status == "partial":
            note = ""
            if post_neg.messages:
                last = post_neg.messages[-1]
                note = str((last.payload or {}).get("note") or "")
            if note:
                reasons.append(f"post_retrieve:{note}")
            elif post_neg.tradeoffs:
                reasons.append(f"post_retrieve:{post_neg.tradeoffs[0]}")
            else:
                reasons.append("post_retrieve:partial")
        open_q = open_question_from_run(plan, run, reasons=reasons, claim=str(claim))
        _persist_oq(open_q, open_questions_path, open_questions_db, tracer=tracer)
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
        post_retrieve_negotiation=post_neg,
        open_question=open_q,
        events=events,
    )


def json_safe_context(context: Any, stats: dict[str, Any]) -> str:
    """Build a short context string that embeds evidence stats for negotiators."""
    base = str(context or "")
    return f"{base}\n[post_retrieve evidence_count={stats.get('evidence_count')} novel={stats.get('novel_detected')}]"


def _stats_bound_post_retrieve(stats: dict[str, Any]) -> Negotiator:
    """Wrap post_retrieve_negotiator so proposal carries evidence stats."""

    def _neg(
        proposal: dict[str, Any],
        history: list,
        round_index: int,
    ):
        enriched = dict(proposal)
        enriched.update(stats)
        return post_retrieve_negotiator(enriched, history, round_index)

    return _neg


def _make_interpret(
    *,
    plan: dict[str, Any],
    claim: Any,
    demo: bool,
    live: bool,
    dispatch: dict | None,
    index: Any,
    tracer: Any,
    check_contracts: bool,
    contract_mode: str,
    decisions: dict[str, str] | None,
    confidence_floor: str,
    interpret_plan: Any,
    EstateHandler: Any,
    StubHandler: Any,
    EXAMPLE_RESULTS: Any,
) -> Callable[..., RunResult]:
    """Return ``interpret_one(plan_dict, initial_artifacts=None)``."""

    def interpret_one(
        phase_plan: dict[str, Any],
        *,
        initial_artifacts: dict[str, Any] | None = None,
    ) -> RunResult:
        if dispatch or decisions is not None:
            from deborah.runtime.estate import resolve_assumes

            resolution = resolve_assumes(phase_plan.get("assumes") or plan.get("assumes"), index)
            allow = set(resolution.stems) if resolution.stems else None
            fallback = StubHandler(
                results_by_cognition=EXAMPLE_RESULTS if (demo and not live) else {}
            )
            handler = EstateHandler(
                index=index,
                dispatch=dispatch,
                fallback=fallback,
                route_cognition=True,
            )
            claim_ctx = plan.get("request") or plan.get("intent") or claim

            def _handler(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
                context = dict(context)
                context.setdefault("request", claim_ctx)
                context.setdefault("claim", claim_ctx)
                context.setdefault("intent", plan.get("intent") or claim_ctx)
                context.setdefault("outcomes", plan.get("outcomes") or [])
                context.setdefault("plan", plan)
                context.setdefault("confidence_floor", confidence_floor)
                if decisions:
                    context.setdefault("decisions", dict(decisions))
                return handler(step, context)

            return interpret_plan(
                phase_plan,
                handler=_handler,
                allow_list=allow,
                validate_profile="full",
                check_contracts=check_contracts,
                contract_mode=contract_mode,
                decisions=decisions,
                initial_artifacts=initial_artifacts,
            )

        # interpret_with_estate has no initial_artifacts; fall back for full plan only
        return interpret_with_estate(
            phase_plan,
            demo=demo and not live,
            live=live,
            dispatch=dispatch,
            index=index,
            tracer=tracer,
            check_contracts=check_contracts,
            contract_mode=contract_mode,
            validate_profile="full",
        )

    return interpret_one


def _persist_oq(
    oq: OpenQuestion,
    path: str | Path | None,
    db: Any,
    *,
    tracer: Any = None,
) -> None:
    if path is not None:
        OpenQuestionStore(path).record(oq)
    if db is not None:
        record_open_question_mongo(db, oq)
    if tracer is not None:
        try:
            from galeed import record_open_question_event  # type: ignore[import-not-found]

            record_open_question_event(
                tracer=tracer,
                open_question_id=oq.open_question_id,
                question=oq.question,
                reason=oq.reason,
                plan_id=oq.plan_id,
                run_terminal=oq.run_terminal,
            )
        except Exception:
            pass


def _emit_negotiation(tracer: Any, **kwargs: Any) -> None:
    if tracer is None:
        return
    try:
        from galeed import record_negotiation  # type: ignore[import-not-found]

        record_negotiation(tracer=tracer, **kwargs)
    except TypeError:
        # Older galeed without note= — fold into metadata.
        try:
            from galeed import record_negotiation  # type: ignore[import-not-found]

            note = kwargs.pop("note", None)
            meta = dict(kwargs.pop("metadata", None) or {})
            if note:
                meta.setdefault("note", note)
                meta.setdefault("negotiation_phase", note)
            record_negotiation(tracer=tracer, metadata=meta or None, **kwargs)
        except Exception:
            pass
    except Exception:
        pass


def _emit_slice_event(tracer: Any, type_: str, summary: str = "", **metadata: Any) -> None:
    """Best-effort Galeed emit for mid-slice phase markers (extensible types)."""
    if tracer is None:
        return
    try:
        tracer.emit(type_, summary=summary or type_, status="ok", **metadata)
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
