"""Interpret a crystallised PLAN dict (SPEC §4.6 + framing).

This is a *thin* runtime: deterministic control (order, allow-list, bounds,
terminals). Stochastic steps still call handlers that may use models; the
interpreter does not re-plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from deborah.conformance import (
    CORE_CONSTRUCTS,
    EXTENSION_CONSTRUCTS,
    ON_UNCERTAINTY_POLICIES,
    validate_plan,
)
from deborah.contracts import inference_confidence_band, validate_cognition_result

# Terminal plan statuses the interpreter may emit.
TERMINALS: frozenset[str] = frozenset({"complete", "open", "refused", "blocked"})


class Handler(Protocol):
    """Dispatch a single plan step; return status + optional structured result."""

    def __call__(self, step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Return ``{"status": "completed"|"blocked"|"skipped"|"refused", ...}``.

        Optional keys: ``result`` (dict), ``reason`` (str), ``residual`` (bool —
        marks unresolved uncertainty for ON_UNCERTAINTY handling).
        """
        ...


@dataclass
class StepRecord:
    id: str
    construct: str | None
    status: str
    reason: str | None = None
    result: dict[str, Any] | None = None
    cognition: str | None = None
    contract_errors: list[str] = field(default_factory=list)


@dataclass
class RunResult:
    plan_id: str
    terminal: str
    steps: list[StepRecord]
    events: list[dict[str, Any]]
    unresolved: list[str] = field(default_factory=list)
    on_uncertainty: str = "record"
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "terminal": self.terminal,
            "on_uncertainty": self.on_uncertainty,
            "unresolved": list(self.unresolved),
            "errors": list(self.errors),
            "events": list(self.events),
            "steps": [
                {
                    "id": s.id,
                    "construct": s.construct,
                    "status": s.status,
                    "reason": s.reason,
                    "cognition": s.cognition,
                    "result": s.result,
                    "contract_errors": list(s.contract_errors),
                }
                for s in self.steps
            ],
        }


class StubHandler:
    """Default handler: complete core steps; block unknown extension constructs.

    CALL steps succeed if the tool is allow-listed (or no allow-list is set).
    Inject ``results_by_id`` to supply structured cognition results for contract
    checks without a real model.

    GATED / HUMAN DECISION steps use :mod:`deborah.runtime.decide` — without an
    injected selection they return ``awaiting_decision`` rather than inventing
    a verdict.
    """

    def __init__(
        self,
        *,
        results_by_id: dict[str, dict[str, Any]] | None = None,
        results_by_cognition: dict[str, dict[str, Any]] | None = None,
        refuse_tools: set[str] | None = None,
    ) -> None:
        self.results_by_id = results_by_id or {}
        self.results_by_cognition = results_by_cognition or {}
        self.refuse_tools = {t.lower() for t in (refuse_tools or set())}

    def __call__(self, step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        from deborah.runtime.decide import gated_decision_outcome, step_is_gated

        sid = str(step.get("id", ""))
        construct = (step.get("construct") or "STEP").upper()
        cognition = step.get("cognition")
        allow = context.get("allow_list")  # None = unrestricted; set = stems

        if construct in EXTENSION_CONSTRUCTS:
            return {
                "status": "skipped",
                "reason": f"extension construct {construct} not executed by thin runtime",
            }

        if construct not in CORE_CONSTRUCTS and construct != "STEP":
            return {"status": "blocked", "reason": f"unknown construct {construct}"}

        tools = _step_tools(step)
        if allow is not None and tools:
            for tool in tools:
                stem = tool.split("@", 1)[0].lower()
                if not _stem_allowed(stem, allow):
                    return {
                        "status": "blocked",
                        "reason": f"tool {tool!r} not in allow-list {sorted(allow)}",
                    }
                if stem in self.refuse_tools or tool.lower() in self.refuse_tools:
                    return {
                        "status": "refused",
                        "reason": f"capability refused {tool!r}",
                        "residual": True,
                    }

        result = self.results_by_id.get(sid)
        if result is None and cognition:
            result = self.results_by_cognition.get(str(cognition).lower())

        # GATED decisions: never invent accept/reject without injection
        if construct == "DECISION" or str(cognition or "").lower() == "decide":
            if step_is_gated(step) or construct == "DECISION":
                # Non-gated DECISION still uses gated_decision_outcome for open residual
                return gated_decision_outcome(step, context, fallback_result=result)

        out: dict[str, Any] = {"status": "completed"}
        if result is not None:
            out["result"] = result
        return out


def _stem_allowed(stem: str, allow: set[str]) -> bool:
    """Exact allow-list match (review H1).

    Bidirectional substring matching accepted single-char and
    ``evilmilcah.critique``-style extensions. Allow:

    - exact stem equality after ``@`` strip
    - namespace child: ``stem.startswith(allowed + ".")``
    """
    stem = stem.lower().split("@", 1)[0]
    if stem in allow:
        return True
    for a in allow:
        a = a.lower().split("@", 1)[0]
        if stem == a or stem.startswith(a + "."):
            return True
    return False


def _step_tools(step: dict[str, Any]) -> list[str]:
    tools: list[str] = []
    allowed = step.get("allowed_tools")
    if isinstance(allowed, list):
        tools.extend(str(t).strip() for t in allowed if str(t).strip())
    # Prefer explicit allowed_tools (review M5 / F5). Only infer from action
    # when the author did not declare tools.
    if (step.get("construct") or "").upper() == "CALL" and not tools:
        action = str(step.get("action") or "")
        head = action.split("[", 1)[0].strip()
        head = head.split("—", 1)[0].split("–", 1)[0].strip()
        parts = head.split()
        if parts:
            # Prefer dotted capability names (milcah.critique) over prose.
            candidate = parts[0]
            if candidate.lower() == "invoke" and len(parts) > 1:
                candidate = parts[1]
            if "." in candidate or candidate.isidentifier():
                tools.append(candidate)
    return tools


def _allow_list_from_plan(plan: dict[str, Any], explicit: set[str] | None) -> set[str] | None:
    if explicit is not None:
        return {a.lower() for a in explicit}
    assumes = plan.get("assumes")
    if not assumes:
        # Default-open when assumes is absent — explicit decision (review M6).
        import logging

        logging.getLogger("deborah.runtime").debug(
            "plan %s has empty/missing assumes; tool allow-list unrestricted",
            plan.get("plan_id"),
        )
        return None  # unrestricted
    stems: set[str] = set()
    for ref in assumes:
        if isinstance(ref, str) and ref.strip():
            stems.add(ref.strip().split("@", 1)[0].lower())
    return stems or None


def _ready_order(
    steps: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Topological order by depends_on.

    Returns ``(ordered_steps, cycle_errors)``. On a cycle, remaining steps are
    appended in sorted id order *and* an error is reported (review H4) — no
    silent reordering.
    """
    by_id = {
        str(s.get("id")): s
        for s in steps
        if isinstance(s, dict) and s.get("id") is not None and str(s.get("id")).strip()
    }
    pending = set(by_id)
    done: set[str] = set()
    ordered: list[dict[str, Any]] = []
    errors: list[str] = []
    # Safety: at most n² picks
    for _ in range(len(by_id) * len(by_id) + 1):
        if not pending:
            break
        progressed = False
        for sid in sorted(pending):
            step = by_id[sid]
            deps = step.get("depends_on") or []
            if not isinstance(deps, list):
                deps = []
            dep_ids = [str(d) for d in deps]
            if all(d in done or d not in by_id for d in dep_ids):
                ordered.append(step)
                pending.remove(sid)
                done.add(sid)
                progressed = True
        if not progressed:
            remaining = sorted(pending)
            errors.append(
                f"dependency cycle or unresolvable depends_on among steps: {remaining}"
            )
            for sid in remaining:
                ordered.append(by_id[sid])
            break
    # Steps without ids append at end (track by object id, not dict value — L1)
    seen_ids = {id(s) for s in ordered}
    for s in steps:
        if isinstance(s, dict) and id(s) not in seen_ids:
            ordered.append(s)
            seen_ids.add(id(s))
    return ordered, errors


def interpret_plan(
    plan: dict[str, Any],
    *,
    handler: Handler | None = None,
    allow_list: set[str] | None = None,
    validate_profile: str | None = "full",
    check_contracts: bool = False,
    contract_mode: str = "soft",
    max_steps: int | None = None,
    allow_reentry: bool = False,
    reflective_pass: bool | None = None,
    decisions: dict[str, str] | None = None,
    initial_artifacts: dict[str, Any] | None = None,
) -> RunResult:
    """Walk ``plan`` under the framed control policy.

    Parameters
    ----------
    plan:
        ``validate_plan``-compatible dict (e.g. from ``document_to_plan``).
    handler:
        Step dispatcher; default :class:`StubHandler`.
    allow_list:
        Explicit tool stems. If omitted, derived from ``plan["assumes"]`` when
        present; if assumes empty, tools are unrestricted.
    validate_profile:
        Run ``validate_plan`` first (``full``/``core``/``strict``); ``None`` skips.
    check_contracts:
        When true, validate each step ``result`` against ``cognition`` if set.
    contract_mode:
        ``soft`` or ``strict`` for result contracts.
    max_steps:
        Hard cap on executed steps (default: len(steps) or plan metadata).
    allow_reentry:
        Phase F: if true **and** plan has ``exploration_budget`` > 0, at most
        one re-dispatch of a low-inference infer/evaluate step (budget
        decremented). Default false — no free re-planning.
    reflective_pass:
        Phase F: if true (or plan.reflective_pass), mark residual when
        infer/evaluate reports low/unassessed inference confidence.
    decisions:
        Optional map of step id → selected verdict for GATED DECISION steps
        (``accept`` | ``reject`` | ``open``).
    initial_artifacts:
        Optional pre-seeded ``context["artifacts"]`` (e.g. phase-1 slice results
        carried into a post-retrieve critique phase).
    """
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    plan_id = str(plan.get("plan_id") or "unknown")
    on_unc = str(plan.get("on_uncertainty") or "record").lower()
    if on_unc not in ON_UNCERTAINTY_POLICIES:
        on_unc = "record"

    if validate_profile is not None:
        verrs = validate_plan(plan, profile=validate_profile)
        if verrs:
            return RunResult(
                plan_id=plan_id,
                terminal="blocked",
                steps=[],
                events=[{"type": "plan.validation.failed", "errors": verrs}],
                on_uncertainty=on_unc,
                errors=list(verrs),
            )

    steps_in = plan.get("steps")
    if not isinstance(steps_in, list) or not steps_in:
        return RunResult(
            plan_id=plan_id,
            terminal="blocked",
            steps=[],
            events=[{"type": "plan.empty"}],
            on_uncertainty=on_unc,
            errors=["plan has no steps"],
        )

    allow = _allow_list_from_plan(plan, allow_list)
    h: Handler = handler or StubHandler()
    bound = max_steps
    if bound is None:
        meta_max = plan.get("max_steps")
        bound = int(meta_max) if meta_max is not None else len(steps_in)
    bound = max(0, int(bound))

    try:
        exploration_budget = int(plan.get("exploration_budget") or 0)
    except (TypeError, ValueError):
        exploration_budget = 0
    do_reflective = (
        bool(plan.get("reflective_pass")) if reflective_pass is None else bool(reflective_pass)
    )
    reentry_used = 0

    context: dict[str, Any] = {
        "allow_list": allow,
        "plan_id": plan_id,
        "artifacts": dict(initial_artifacts or {}),  # step_id → result
        "decisions": dict(decisions or {}),
    }
    records: list[StepRecord] = []
    residual = False
    refused = False
    blocked = False
    executed = 0

    events.append(
        {
            "type": "plan.started",
            "plan_id": plan_id,
            "allow_list": sorted(allow) if allow is not None else None,
            "max_steps": bound,
            "exploration_budget": exploration_budget,
            "reflective_pass": do_reflective,
            "allow_reentry": allow_reentry,
        }
    )

    worklist, order_errors = _ready_order(
        [s for s in steps_in if isinstance(s, dict)]
    )
    if order_errors:
        errors.extend(order_errors)
        events.append({"type": "plan.dependency_errors", "errors": list(order_errors)})
        # Cycles are terminal: do not silently reorder and complete (H4).
        blocked = True
        worklist = []
    # Track which step ids already consumed a re-entry slot
    reentered: set[str] = set()

    while worklist:
        step = worklist.pop(0)
        if executed >= bound:
            events.append({"type": "plan.bound_reached", "max_steps": bound})
            blocked = True
            break

        sid = str(step.get("id") or f"anon_{executed}")
        construct = step.get("construct")
        cognition = step.get("cognition")
        events.append({"type": "plan.step.started", "id": sid, "construct": construct})

        try:
            outcome = h(step, context)
        except Exception as exc:  # noqa: BLE001 — surface handler failure as blocked step
            outcome = {"status": "blocked", "reason": f"{type(exc).__name__}: {exc}"}

        status = str(outcome.get("status") or "blocked")
        reason = outcome.get("reason")
        result = outcome.get("result")
        if isinstance(result, dict):
            context["artifacts"][sid] = result

        contract_errors: list[str] = []
        if check_contracts and cognition and isinstance(result, dict):
            contract_errors = validate_cognition_result(
                str(cognition), result, mode=contract_mode, path=f"step[{sid}].result"
            )
            if contract_errors and contract_mode == "strict":
                status = "blocked"
                reason = (reason or "") + "; contract: " + "; ".join(contract_errors)

        step_residual = bool(outcome.get("residual"))
        # Reflective post-pass: low/unassessed inference confidence on infer/evaluate
        if (
            do_reflective
            and status == "completed"
            and cognition
            and str(cognition).lower() in {"infer", "evaluate"}
        ):
            band = inference_confidence_band(result if isinstance(result, dict) else None)
            if band in {"low", "unassessed", None}:
                # None = missing confidence counts as unassessed for reflective policy
                if band is None:
                    band = "unassessed"
                step_residual = True
                events.append(
                    {
                        "type": "plan.reflective.flagged",
                        "id": sid,
                        "cognition": cognition,
                        "inference_confidence": band,
                    }
                )
                # Bounded opt-in re-entry (at most once per step, consumes budget)
                if (
                    allow_reentry
                    and exploration_budget > 0
                    and sid not in reentered
                    and executed + 1 < bound
                ):
                    exploration_budget -= 1
                    reentered.add(sid)
                    reentry_used += 1
                    worklist.insert(0, step)  # re-dispatch same step once
                    events.append(
                        {
                            "type": "plan.reentry.scheduled",
                            "id": sid,
                            "exploration_budget_remaining": exploration_budget,
                        }
                    )

        if step_residual:
            residual = True
        if status == "refused":
            refused = True
        if status == "blocked":
            blocked = True

        rec = StepRecord(
            id=sid,
            construct=str(construct) if construct else None,
            status=status,
            reason=str(reason) if reason else None,
            result=result if isinstance(result, dict) else None,
            cognition=str(cognition) if cognition else None,
            contract_errors=contract_errors,
        )
        records.append(rec)
        events.append(
            {
                "type": "plan.step.finished",
                "id": sid,
                "status": status,
                "reason": reason,
                "residual": step_residual,
            }
        )
        executed += 1

        # Hard stop on blocked/refused mid-plan (no free re-planning)
        if status in {"blocked", "refused"}:
            break
        # GATED await: stop walk so later steps do not run without a verdict
        if status == "awaiting_decision":
            residual = True
            break

    terminal = _resolve_terminal(
        blocked=blocked,
        refused=refused,
        residual=residual,
        on_uncertainty=on_unc,
        records=records,
    )
    unresolved: list[str] = []
    if any(r.status == "awaiting_decision" for r in records):
        unresolved.append("awaiting gated human decision")
    if residual or terminal == "open":
        if "awaiting gated human decision" not in unresolved:
            unresolved.append("residual uncertainty after interpretation")
    if terminal == "refused":
        unresolved.append("capability or policy refusal")
    if reentry_used:
        unresolved.append(f"reentry_used={reentry_used}")

    events.append(
        {
            "type": "plan.finished",
            "terminal": terminal,
            "exploration_budget_remaining": exploration_budget,
            "reentry_used": reentry_used,
        }
    )
    return RunResult(
        plan_id=plan_id,
        terminal=terminal,
        steps=records,
        events=events,
        unresolved=unresolved,
        on_uncertainty=on_unc,
        errors=errors,
    )


def _resolve_terminal(
    *,
    blocked: bool,
    refused: bool,
    residual: bool,
    on_uncertainty: str,
    records: list[StepRecord],
) -> str:
    if refused:
        return "refused"
    if blocked:
        return "blocked"
    if any(r.status == "awaiting_decision" for r in records):
        return "open"
    if residual:
        if on_uncertainty == "abort":
            return "blocked"
        if on_uncertainty == "escalate":
            return "open"  # open + unresolved marks escalation path for harnesses
        return "open"  # record
    if not records:
        return "blocked"
    if all(r.status in {"completed", "skipped"} for r in records):
        return "complete"
    return "blocked"


# Type alias for custom handler factories
HandlerFactory = Callable[[], Handler]
