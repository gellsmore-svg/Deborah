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

CONFORMANCE_VERSION = "1.5"

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
        "SAMPLE",
        "VIEW",
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

# Cognitive product contracts on steps (SPEC process-semantic axes). Progressive:
# omit cognition = no product contract.
# MVP core four; Phase F extends with negotiate/learn/optimize (gated contracts).
COGNITION_MVP: frozenset[str] = frozenset({"observe", "infer", "evaluate", "decide"})
COGNITION_EXTENDED: frozenset[str] = frozenset({"negotiate", "learn", "optimize"})
# Back-compat alias — no longer rejected; extended cognitions are first-class.
COGNITION_RESERVED: frozenset[str] = frozenset()  # emptied in Phase F
COGNITION_VALUES: frozenset[str] = COGNITION_MVP | COGNITION_EXTENDED

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
    "exploration_budget",
    "reflective_pass",
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


VALIDATE_PROFILES: frozenset[str] = frozenset({"full", "core", "strict"})


def _capability_stem(ref: str) -> str:
    """``milcah.critique@1`` → ``milcah.critique``."""
    return ref.strip().split("@", 1)[0].strip().lower()


def _tools_from_step(step: dict[str, Any]) -> list[str]:
    """Collect capability-like tool names from allowed_tools and CALL actions.

    Prefer ``allowed_tools`` when present so prose actions like
    ``Synthesise an answer…`` are not treated as tool names (review F5/M5).
    """
    tools: list[str] = []
    allowed = step.get("allowed_tools")
    if isinstance(allowed, list):
        tools.extend(str(t).strip() for t in allowed if str(t).strip())
        if tools:
            return tools
    action = str(step.get("action") or "")
    # "milcah.critique — …" or "Invoke milcah.critique" patterns after CALL construct
    if str(step.get("construct") or "").upper() == "CALL":
        # action may be "milcah.critique — Pressure-test…" or full phrase with tags
        head = action.split("[", 1)[0].strip()
        head = head.split("—", 1)[0].split("–", 1)[0].strip()
        parts = head.split()
        if parts:
            candidate = parts[0] if parts[0].lower() != "invoke" else (parts[1] if len(parts) > 1 else "")
            if candidate and ("." in candidate or candidate.replace("_", "").isalnum()):
                tools.append(candidate.rstrip("."))
    return tools


def validate_plan(plan: Any, *, profile: str = "full") -> list[str]:
    """Return a list of conformance errors for ``plan`` (empty list = conformant).

    Profiles (Phase B):

    - ``full`` — default structural contract (constructs, statuses, cognition MVP).
    - ``core`` — as full, plus reject **extension** constructs (core profile only).
    - ``strict`` — as full, plus COGNITION requires output/success_criteria;
      when ``assumes`` is set, CALL/allowed_tools should reference assumed stems.
    """
    if profile not in VALIDATE_PROFILES:
        return [f"unknown validate profile {profile!r} (allowed: {sorted(VALIDATE_PROFILES)})"]

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
    assume_stems: set[str] = set()
    if assumes is not None:
        if not isinstance(assumes, list):
            errors.append("assumes must be a list of capability refs (name or name@version)")
        else:
            for index, ref in enumerate(assumes):
                if not isinstance(ref, str) or not ref.strip():
                    errors.append(f"assumes[{index}] must be a non-empty string")
                else:
                    assume_stems.add(_capability_stem(ref))

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
            if not isinstance(step, dict):
                continue
            construct = step.get("construct")
            if profile == "core" and construct in EXTENSION_CONSTRUCTS:
                errors.append(
                    f"step[{index}] construct {construct!r} is not in the core profile "
                    f"(use full profile or a CORE construct)"
                )
            cognition = step.get("cognition")
            if cognition is not None and cognition != "":
                value = str(cognition).strip().lower()
                if value not in COGNITION_VALUES:
                    errors.append(
                        f"step[{index}] unknown cognition {value!r} "
                        f"(allowed: {sorted(COGNITION_VALUES)})"
                    )
                elif profile == "strict":
                    has_output = bool(step.get("success_criteria")) or bool(
                        str(step.get("output") or "").strip()
                    )
                    # Also accept OUTPUT folded into action prose is too weak; require criteria.
                    if not has_output:
                        errors.append(
                            f"step[{index}] strict: COGNITION {value!r} requires "
                            f"success_criteria or output"
                        )
                    # Human-owned decide should use DECISION (not bare STEP) —
                    # roadmap Part VI #3; GATED lives on DECISION.
                    if value == "decide" and str(construct or "").upper() != "DECISION":
                        errors.append(
                            f"step[{index}] strict: COGNITION decide should use "
                            f"construct DECISION (got {construct!r})"
                        )
            execution = step.get("execution")
            if execution is not None and execution != "":
                if str(execution).strip().lower() not in {"deterministic", "stochastic"}:
                    errors.append(
                        f"step[{index}] invalid execution {execution!r} "
                        f"(allowed: deterministic|stochastic)"
                    )

            if profile == "strict" and assume_stems and construct == "CALL":
                tools = _tools_from_step(step)
                if not tools:
                    errors.append(
                        f"step[{index}] strict: CALL step should name a capability "
                        f"in action or allowed_tools when assumes is set"
                    )
                else:
                    for tool in tools:
                        stem = _capability_stem(tool)
                        # Exact stem or namespace child of an assumed capability.
                        if stem not in assume_stems and not any(
                            stem == a or stem.startswith(a + ".")
                            for a in assume_stems
                        ):
                            errors.append(
                                f"step[{index}] strict: CALL tool {tool!r} not in "
                                f"assumes {sorted(assume_stems)}"
                            )

        # Graph integrity (review H4) — always, all profiles.
        errors.extend(_validate_step_graph(steps))

    # Scalar plan fields that must be well-typed.
    revision = plan.get("revision")
    if revision is not None and not isinstance(revision, int):
        errors.append(f"revision must be an int (got {type(revision).__name__})")
    max_steps = plan.get("max_steps")
    if max_steps is not None:
        try:
            if int(max_steps) < 0:
                errors.append("max_steps must be >= 0")
        except (TypeError, ValueError):
            errors.append(f"max_steps must be an int (got {max_steps!r})")

    return errors


def _validate_step_graph(steps: list[Any]) -> list[str]:
    """Id uniqueness, dangling/self depends_on, and cycles (review H4)."""
    errors: list[str] = []
    ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        sid = step.get("id")
        if sid is None or str(sid).strip() == "":
            errors.append(f"step[{index}] missing id")
            continue
        sid = str(sid)
        if sid in by_id:
            errors.append(f"duplicate step id {sid!r}")
        by_id[sid] = step
        ids.append(sid)

    # depends_on integrity
    for sid, step in by_id.items():
        deps = step.get("depends_on") or []
        if not isinstance(deps, list):
            errors.append(f"step {sid!r} depends_on must be a list")
            continue
        for dep in deps:
            dep_s = str(dep)
            if dep_s == sid:
                errors.append(f"step {sid!r} has a self-dependency")
            elif dep_s not in by_id:
                errors.append(f"step {sid!r} depends_on missing step {dep_s!r}")

    # Cycle detection (DFS)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {sid: WHITE for sid in by_id}
    cycle_nodes: list[str] = []

    def visit(u: str) -> bool:
        color[u] = GRAY
        deps = by_id[u].get("depends_on") or []
        if not isinstance(deps, list):
            deps = []
        for dep in deps:
            v = str(dep)
            if v not in by_id:
                continue
            if color[v] == GRAY:
                cycle_nodes.append(v)
                return True
            if color[v] == WHITE and visit(v):
                return True
        color[u] = BLACK
        return False

    for sid in by_id:
        if color[sid] == WHITE and visit(sid):
            errors.append(
                f"dependency cycle involving step {cycle_nodes[0]!r}"
                if cycle_nodes
                else "dependency cycle in plan steps"
            )
            break

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
