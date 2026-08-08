"""Phased interpretation helpers — post-retrieve negotiation mid-slice.

Splits a crystallised plan so negotiation can re-enter *after* observe/infer
and *before* critique, without free re-planning of the control graph.
"""

from __future__ import annotations

from typing import Any


def is_critique_call(step: dict[str, Any]) -> bool:
    """True for CALL milcah.critique / coherence_check style steps."""
    if str(step.get("construct") or "").upper() != "CALL":
        return False
    blob = " ".join(
        [
            str(step.get("action") or ""),
            " ".join(str(t) for t in (step.get("allowed_tools") or [])),
        ]
    ).lower()
    return any(
        key in blob
        for key in (
            "milcah.critique",
            "critique",
            "coherence_check",
            "validate_against_intent",
        )
    )


def split_plan_at_critique(plan: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (pre_critique_plan, post_critique_plan) sharing framing fields.

    Pre includes novel/retrieve/infer; post includes critique through decide.
    If no critique CALL is found, pre is the full plan and post has no steps.
    """
    steps = [s for s in (plan.get("steps") or []) if isinstance(s, dict)]
    pre: list[dict[str, Any]] = []
    post: list[dict[str, Any]] = []
    found = False
    for step in steps:
        if not found and is_critique_call(step):
            found = True
            post.append(step)
        elif found:
            post.append(step)
        else:
            pre.append(step)

    def _copy(with_steps: list[dict[str, Any]], suffix: str) -> dict[str, Any]:
        out = dict(plan)
        out["steps"] = with_steps
        # Avoid double-validation collisions on empty phase
        if suffix:
            out["plan_id"] = f"{plan.get('plan_id') or 'plan'}_{suffix}"
        return out

    if not found:
        return _copy(steps, ""), _copy([], "post")
    return _copy(pre, "pre"), _copy(post, "post")


def evidence_stats_from_artifacts(artifacts: dict[str, Any]) -> dict[str, Any]:
    """Summarise observe/novel products for post-retrieve negotiation."""
    evidence_count = 0
    novel_terms: list[str] = []
    novel_detected = False
    for val in (artifacts or {}).values():
        if not isinstance(val, dict):
            continue
        ev = val.get("evidence")
        if isinstance(ev, list):
            evidence_count += len(ev)
        if val.get("novel_detected"):
            novel_detected = True
        if isinstance(val.get("novel"), list):
            novel_terms.extend(str(t) for t in val["novel"])
            if val["novel"]:
                novel_detected = True
    return {
        "evidence_count": evidence_count,
        "novel_detected": novel_detected,
        "novel_terms": novel_terms[:16],
    }


def merge_run_results(first: Any, second: Any) -> Any:
    """Concatenate steps/events from two RunResults into ``first`` (mutates)."""
    first.steps = list(first.steps) + list(second.steps)
    first.events = list(first.events) + list(second.events)
    first.unresolved = list(dict.fromkeys(list(first.unresolved) + list(second.unresolved)))
    first.errors = list(first.errors) + list(second.errors)
    # Prefer second terminal unless first already refused/blocked
    if first.terminal not in {"refused", "blocked"}:
        first.terminal = second.terminal
    return first
