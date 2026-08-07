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
from deborah.contracts import validate_cognition_result

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
                if stem not in allow and not any(stem in a or a in stem for a in allow):
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

        out: dict[str, Any] = {"status": "completed"}
        if result is not None:
            out["result"] = result
        # DECISION without a selected result → residual uncertainty
        if construct == "DECISION" and (
            result is None
            or (isinstance(result, dict) and result.get("selected") in (None, "", "open"))
        ):
            if isinstance(result, dict) and result.get("selected") == "open":
                out["residual"] = True
            elif result is None:
                out["residual"] = True
                out["result"] = {"selected": "open", "committed": False}
        return out


def _step_tools(step: dict[str, Any]) -> list[str]:
    tools: list[str] = []
    allowed = step.get("allowed_tools")
    if isinstance(allowed, list):
        tools.extend(str(t).strip() for t in allowed if str(t).strip())
    if (step.get("construct") or "").upper() == "CALL" and not tools:
        action = str(step.get("action") or "")
        head = action.split("[", 1)[0].strip()
        head = head.split("—", 1)[0].split("–", 1)[0].strip()
        parts = head.split()
        if parts:
            tools.append(parts[0])
    return tools


def _allow_list_from_plan(plan: dict[str, Any], explicit: set[str] | None) -> set[str] | None:
    if explicit is not None:
        return {a.lower() for a in explicit}
    assumes = plan.get("assumes")
    if not assumes:
        return None  # unrestricted
    stems: set[str] = set()
    for ref in assumes:
        if isinstance(ref, str) and ref.strip():
            stems.add(ref.strip().split("@", 1)[0].lower())
    return stems or None


def _ready_order(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Topological order by depends_on; fall back to document order on cycles."""
    by_id = {str(s.get("id")): s for s in steps if isinstance(s, dict) and s.get("id")}
    pending = set(by_id)
    done: set[str] = set()
    ordered: list[dict[str, Any]] = []
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
            # Cycle or missing deps — append remaining in sorted id order
            for sid in sorted(pending):
                ordered.append(by_id[sid])
            break
    # Steps without ids (shouldn't happen) append at end
    for s in steps:
        if isinstance(s, dict) and s not in ordered:
            ordered.append(s)
    return ordered


def interpret_plan(
    plan: dict[str, Any],
    *,
    handler: Handler | None = None,
    allow_list: set[str] | None = None,
    validate_profile: str | None = "full",
    check_contracts: bool = False,
    contract_mode: str = "soft",
    max_steps: int | None = None,
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

    context: dict[str, Any] = {
        "allow_list": allow,
        "plan_id": plan_id,
        "artifacts": {},  # step_id → result
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
        }
    )

    for step in _ready_order([s for s in steps_in if isinstance(s, dict)]):
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

        if outcome.get("residual"):
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
                "residual": bool(outcome.get("residual")),
            }
        )
        executed += 1

        # Hard stop on blocked/refused mid-plan (no free re-planning)
        if status in {"blocked", "refused"}:
            break

    terminal = _resolve_terminal(
        blocked=blocked,
        refused=refused,
        residual=residual,
        on_uncertainty=on_unc,
        records=records,
    )
    unresolved: list[str] = []
    if residual or terminal == "open":
        unresolved.append("residual uncertainty after interpretation")
    if terminal == "refused":
        unresolved.append("capability or policy refusal")

    events.append({"type": "plan.finished", "terminal": terminal})
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
