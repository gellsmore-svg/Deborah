"""GATED DECISION handling — human ownership of terminal verdicts.

When a DECISION step is tagged GATED / HUMAN (or ``gated: true``), the thin
runtime must **not** invent an accept/reject. Without an injected decision it
returns ``awaiting_decision`` + residual, so the plan terminals as ``open`` with
an explicit unresolved reason.

Inject decisions via:
- ``interpret_plan(..., decisions={"s4": "accept"})``
- context ``decisions`` map (step id → selected)
- ``results_by_id`` on StubHandler (pre-supplied decide product)
"""

from __future__ import annotations

import re
from typing import Any

_GATED_RE = re.compile(r"\b(GATED|HUMAN)\b", re.I)
_ASSISTED = re.compile(r"ASSISTED-BY\s*:", re.I)


def step_is_gated(step: dict[str, Any]) -> bool:
    """True when the step requires human/gated commitment."""
    if step.get("gated") is True:
        return True
    tags = step.get("tags")
    if isinstance(tags, list):
        for t in tags:
            if str(t).upper() in {"GATED", "HUMAN"} or str(t).upper().startswith("HUMAN"):
                return True
            if "GATED" in str(t).upper().split(","):
                return True
    action = str(step.get("action") or step.get("text") or "")
    if _GATED_RE.search(action):
        return True
    # DECISION with HUMAN actor even if GATED omitted
    construct = (step.get("construct") or "").upper()
    if construct == "DECISION" and re.search(r"\[.*\bHUMAN\b", action, re.I):
        return True
    return False


def resolve_injected_decision(
    step: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any] | None:
    """Return a decide product if the harness injected a selection."""
    sid = str(step.get("id") or "")
    decisions = context.get("decisions")
    selected = None
    if isinstance(decisions, dict):
        selected = decisions.get(sid) or decisions.get("default")
    if selected is None and context.get("decision") is not None:
        selected = context.get("decision")
    if selected is None:
        return None
    selected_s = str(selected).strip().lower()
    if selected_s not in {"accept", "reject", "open"}:
        selected_s = str(selected).strip()
    return {
        "selected": selected_s,
        "alternatives": ["accept", "reject", "open"],
        "committed": selected_s not in {"open", ""},
        "gated": True,
        "constraints": ["operator-injected decision"],
        "confidence": {
            "evidence": "medium",
            "inference": "medium",
            "execution": "high",
            "basis": "human_gate",
        },
    }


def gated_decision_outcome(
    step: dict[str, Any],
    context: dict[str, Any],
    *,
    fallback_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Outcome for a GATED decision step.

    Priority: injected decision → explicit fallback result with selected →
    awaiting_decision residual.
    """
    injected = resolve_injected_decision(step, context)
    if injected is not None:
        return {"status": "completed", "result": injected}

    if isinstance(fallback_result, dict) and fallback_result.get("selected") not in (
        None,
        "",
    ):
        # Pre-authored EXAMPLE_RESULTS style — only use if not gated open default
        if not step_is_gated(step):
            return {"status": "completed", "result": fallback_result}
        # Gated: EXAMPLE open is allowed as residual record, but mark awaiting if open
        sel = str(fallback_result.get("selected")).lower()
        # Pre-supplied open without operator injection → still residual
        out: dict[str, Any] = {
            "status": "completed",
            "result": {**fallback_result, "gated": True},
        }
        if sel == "open":
            out["residual"] = True
        return out

    if not step_is_gated(step):
        # Non-gated DECISION without result → residual open (legacy behaviour)
        return {
            "status": "completed",
            "residual": True,
            "result": {
                "selected": "open",
                "committed": False,
                "alternatives": ["accept", "reject", "open"],
            },
        }

    return {
        "status": "awaiting_decision",
        "residual": True,
        "reason": "gated decision: awaiting human selection (accept|reject|open)",
        "result": {
            "selected": "open",
            "alternatives": ["accept", "reject", "open"],
            "committed": False,
            "gated": True,
            "awaiting": True,
            "confidence": {
                "evidence": "unassessed",
                "inference": "unassessed",
                "execution": "high",
                "basis": "gated_awaiting",
            },
        },
    }
