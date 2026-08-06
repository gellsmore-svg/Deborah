"""Machine-readable conformance contract for Cairn PLANs.

Cairn is primarily a spec (SPEC.md / GRAMMAR.md). This module is the small,
reusable surface a runtime can validate its plans against, so a producer (e.g.
Tirzah's recursive planner) cannot silently drift into a local dialect.

It is intentionally minimal and additive: it checks the *core* plan/step contract
(required fields, allowed constructs, allowed statuses), not the full prose grammar.
``CANONICAL_PLAN`` is the executable fixture — a known-conformant plan.
"""

from __future__ import annotations

from typing import Any

CONFORMANCE_VERSION = "1.1"

# Step-level constructs from SPEC §5 (the ones a PLAN step may *be*).
#
# CORE = execution-normative control-flow (the interpreter must understand these).
# EXTENSION = human-systems / domain constructs the grammar also accepts for
# documentation; a runtime may skip them without violating the core profile.
# Both stay in PLAN_CONSTRUCTS so a document that PARSES can still VALIDATE.
# (test_conformance enumerates the parser's constructs to enforce this.)
CORE_CONSTRUCTS: frozenset[str] = frozenset(
    {
        "STEP",
        "CALL",
        "ITERATE",
        "DECISION",
        "RECURSE",
        "QUEUE",
        "PARALLEL",
        "MERGE",
        "SERVICE",
        "RETRY",
        "AWAIT",
        "BREAK",
        "CONTINUE",
        "MILESTONE",
        "ERROR",
    }
)

EXTENSION_CONSTRUCTS: frozenset[str] = frozenset(
    {
        "REGULATION",
        "APPRAISAL",
        "DUAL_PROCESS",
        "METACOGNITION",
        "ALIGN",
        "COALITION",
        "RESISTANCE",
        "REINFORCEMENT",
        "CASCADE",
        "VISION",
        "SOCIALIZE",
        "INSTITUTIONALIZE",
        "SYMBOLIC_INTERACTION",
        "CONFLICT",
        "ACCOMMODATE",
        "ASSIMILATE",
        "ROLE",
        "FEEDBACK",
        "MACRO",
    }
)

PLAN_CONSTRUCTS: frozenset[str] = CORE_CONSTRUCTS | EXTENSION_CONSTRUCTS

# PLAN status (SPEC §4.5). ``open`` and ``refused`` are first-class terminals:
# residual uncertainty and explicit capability refusal are outcomes, not crashes.
PLAN_STATUSES: frozenset[str] = frozenset(
    {"draft", "active", "stable", "complete", "blocked", "open", "refused"}
)
REVISION_DECISIONS: frozenset[str] = frozenset(
    {"revise", "stable", "complete", "blocked", "open", "refused"}
)

# Per-step execution status for interpretive PLAN walkers (SPEC §4.6).
STEP_STATUSES: frozenset[str] = frozenset({"pending", "active", "completed", "blocked", "skipped"})

# Uncertainty policy when outcomes cannot be fully satisfied (SPEC §4.5).
ON_UNCERTAINTY_POLICIES: frozenset[str] = frozenset({"record", "escalate", "abort"})

# The cross-repo core contract: fields a Cairn plan/step consumer can rely on.
REQUIRED_PLAN_FIELDS: tuple[str, ...] = (
    "plan_id",
    "revision",
    "objective",
    "status",
    "steps",
    "stopping_conditions",
    "revision_decision",
)
# Additive framing fields (SPEC v0.10). Optional for backward compatibility;
# when present they are validated.
OPTIONAL_PLAN_FIELDS: tuple[str, ...] = (
    "intent",
    "outcomes",
    "assumes",
    "on_uncertainty",
    "reevaluate_when",
    "request",
)
REQUIRED_STEP_FIELDS: tuple[str, ...] = ("id", "action", "construct", "status")


def _validate_step(step: Any, index: int) -> list[str]:
    if not isinstance(step, dict):
        return [f"step[{index}] must be an object"]
    errors = [f"step[{index}] missing field: {f}" for f in REQUIRED_STEP_FIELDS if f not in step]
    construct = step.get("construct")
    if construct is not None and construct not in PLAN_CONSTRUCTS:
        errors.append(f"step[{index}] invalid construct: {construct!r} (allowed: {sorted(PLAN_CONSTRUCTS)})")
    status = step.get("status")
    if status is not None and status not in STEP_STATUSES:
        errors.append(f"step[{index}] invalid status: {status!r} (allowed: {sorted(STEP_STATUSES)})")
    return errors


def validate_plan(plan: Any) -> list[str]:
    """Return a list of conformance errors for ``plan`` (empty list = conformant)."""
    if not isinstance(plan, dict):
        return ["plan must be an object"]

    errors = [f"missing plan field: {f}" for f in REQUIRED_PLAN_FIELDS if f not in plan]

    status = plan.get("status")
    if status is not None and status not in PLAN_STATUSES:
        errors.append(f"invalid plan status: {status!r} (allowed: {sorted(PLAN_STATUSES)})")

    decision = plan.get("revision_decision")
    if decision is not None and decision not in REVISION_DECISIONS:
        errors.append(f"invalid revision_decision: {decision!r} (allowed: {sorted(REVISION_DECISIONS)})")

    policy = plan.get("on_uncertainty")
    if policy is not None and policy != "" and policy not in ON_UNCERTAINTY_POLICIES:
        errors.append(
            f"invalid on_uncertainty: {policy!r} (allowed: {sorted(ON_UNCERTAINTY_POLICIES)})"
        )

    assumes = plan.get("assumes")
    if assumes is not None:
        if not isinstance(assumes, list):
            errors.append("assumes must be a list of capability refs (name or name@version)")
        else:
            for index, ref in enumerate(assumes):
                if not isinstance(ref, str) or not ref.strip():
                    errors.append(f"assumes[{index}] must be a non-empty string")

    for list_field in ("outcomes", "stopping_conditions", "reevaluate_when"):
        value = plan.get(list_field)
        if value is not None and not isinstance(value, list):
            errors.append(f"{list_field} must be a list")

    steps = plan.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("plan must have at least one step")
    else:
        for index, step in enumerate(steps):
            errors.extend(_validate_step(step, index))
            # Core-profile note: extension constructs are allowed in the document
            # but CORE_CONSTRUCTS is the set a minimal interpreter must implement.
            construct = step.get("construct") if isinstance(step, dict) else None
            if construct in EXTENSION_CONSTRUCTS:
                # Not an error — descriptive profile. Consumers of the core
                # profile may skip; recorded only so tests can assert the split.
                pass

    return errors


def is_core_construct(construct: str | None) -> bool:
    """True if ``construct`` is in the execution-normative core profile."""
    return construct is not None and construct in CORE_CONSTRUCTS


def is_conformant(plan: Any) -> bool:
    return not validate_plan(plan)


# Executable fixture: a known-conformant minimal plan. Producers can diff against
# this and consumers can use it as a stable example in tests.
CANONICAL_PLAN: dict[str, Any] = {
    "plan_id": "plan_canonical_0001",
    "revision": 1,
    "parent_revision": None,
    "request": "Summarise the retrieved context and answer the question.",
    "intent": "Produce a grounded answer to the user's question.",
    "objective": "Produce a grounded answer to the user's question.",
    "status": "active",
    "steps": [
        {
            "id": "s1",
            "action": "Retrieve relevant context for the question.",
            "construct": "STEP",
            "status": "pending",
            "depends_on": [],
            "success_criteria": ["relevant chunks gathered"],
            "allowed_tools": ["retrieval"],
        },
        {
            "id": "s2",
            "action": "Synthesise an answer from the gathered context.",
            "construct": "CALL",
            "status": "pending",
            "depends_on": ["s1"],
            "success_criteria": ["answer cites gathered context"],
            "allowed_tools": ["answer_adapter"],
        },
    ],
    "stopping_conditions": ["answer produced", "no further context improves sufficiency"],
    "outcomes": ["answer produced", "no further context improves sufficiency"],
    "assumes": ["retrieval@1", "answer_adapter@1"],
    "on_uncertainty": "record",
    "reevaluate_when": [],
    "unresolved_questions": [],
    "revision_decision": "revise",
    "revision_reason": "",
}
