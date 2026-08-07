"""Validate a finished run against plan OUTCOMES and confidence floors.

Substrate-slice support: after interpret, check whether the declared outcomes
are met, partially met, or require an open question. No free re-planning —
failure to meet outcomes yields residual / open, not a new plan graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from deborah.contracts import CONFIDENCE_BANDS, inference_confidence_band
from deborah.runtime.interpreter import RunResult

# Ordered: high is strongest. Used for floor comparisons.
_BAND_RANK = {"high": 3, "medium": 2, "low": 1, "unassessed": 0}


@dataclass
class OutcomeCheck:
    """Result of checking a run against plan-level outcome policy."""

    ok: bool
    met: list[str] = field(default_factory=list)
    unmet: list[str] = field(default_factory=list)
    open_reasons: list[str] = field(default_factory=list)
    confidence_ok: bool = True
    min_band_seen: str | None = None
    floor: str = "low"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "met": list(self.met),
            "unmet": list(self.unmet),
            "open_reasons": list(self.open_reasons),
            "confidence_ok": self.confidence_ok,
            "min_band_seen": self.min_band_seen,
            "floor": self.floor,
            "details": dict(self.details),
        }


def _band_rank(band: str | None) -> int:
    if not band:
        return _BAND_RANK["unassessed"]
    return _BAND_RANK.get(str(band).strip().lower(), 0)


def min_inference_band(run: RunResult) -> str | None:
    """Weakest inference confidence band among completed infer/evaluate steps."""
    worst: str | None = None
    worst_rank = 99
    for step in run.steps:
        if not step.cognition or str(step.cognition).lower() not in {"infer", "evaluate"}:
            continue
        if step.status != "completed":
            continue
        band = inference_confidence_band(step.result) or "unassessed"
        r = _band_rank(band)
        if r < worst_rank:
            worst_rank = r
            worst = band
    return worst


def _evidence_count(run: RunResult) -> int:
    n = 0
    for step in run.steps:
        if not isinstance(step.result, dict):
            continue
        ev = step.result.get("evidence")
        if isinstance(ev, list):
            n += len(ev)
        # observe product may nest statements
    return n


def _has_objections(run: RunResult) -> bool:
    for step in run.steps:
        if not isinstance(step.result, dict):
            continue
        obj = step.result.get("objections")
        if isinstance(obj, list) and obj:
            return True
    return False


def _decision_selected(run: RunResult) -> str | None:
    for step in reversed(run.steps):
        if str(step.cognition or "").lower() != "decide":
            continue
        if isinstance(step.result, dict) and step.result.get("selected") is not None:
            return str(step.result.get("selected")).strip().lower()
    # Fallback: terminal as decision proxy
    if run.terminal == "open":
        return "open"
    if run.terminal == "complete":
        return "accept"
    if run.terminal == "refused":
        return "reject"
    return None


def check_outcomes(
    plan: dict[str, Any],
    run: RunResult,
    *,
    confidence_floor: str = "low",
    require_evidence: bool = True,
    prefer_open_on_empty_evidence: bool = True,
    prefer_open_on_objections: bool = False,
) -> OutcomeCheck:
    """Check whether ``run`` satisfies plan outcomes / confidence policy.

    Parameters
    ----------
    confidence_floor:
        Minimum inference band for infer/evaluate steps (``high|medium|low``).
        ``unassessed`` never meets a floor above unassessed.
    require_evidence:
        At least one evidence item somewhere in the run when the terminal is
        complete/accept.
    prefer_open_on_empty_evidence:
        Empty evidence → open reason (substrate slice default).
    prefer_open_on_objections:
        If True, any critique objections force open_reasons (strict).
        Default False: objections may be recorded while still accepting.
    """
    floor = str(confidence_floor or "low").strip().lower()
    if floor not in CONFIDENCE_BANDS or floor == "unassessed":
        floor = "low"

    check = OutcomeCheck(ok=True, floor=floor)
    declared = plan.get("outcomes") or []
    if isinstance(declared, list):
        check.details["declared_outcomes"] = [
            str(o) for o in declared if isinstance(o, (str, int, float))
        ]

    min_band = min_inference_band(run)
    check.min_band_seen = min_band
    if min_band is not None and _band_rank(min_band) < _BAND_RANK.get(floor, 1):
        check.confidence_ok = False
        check.ok = False
        check.open_reasons.append(
            f"inference confidence {min_band!r} below floor {floor!r}"
        )
        check.unmet.append("confidence_floor")
    else:
        check.met.append("confidence_floor")

    ev_n = _evidence_count(run)
    check.details["evidence_count"] = ev_n
    selected = _decision_selected(run)
    check.details["selected"] = selected
    check.details["terminal"] = run.terminal

    if require_evidence and ev_n == 0:
        if prefer_open_on_empty_evidence:
            check.ok = False
            check.open_reasons.append("no cited evidence retrieved")
            check.unmet.append("cited_evidence")
        elif selected in {"accept", "reject"} or run.terminal == "complete":
            check.ok = False
            check.unmet.append("cited_evidence")
            check.open_reasons.append("accept/reject without evidence")
    else:
        if ev_n > 0:
            check.met.append("cited_evidence")

    if _has_objections(run):
        check.details["has_objections"] = True
        check.met.append("objections_recorded")
        if prefer_open_on_objections and selected == "accept":
            check.ok = False
            check.open_reasons.append("objections present; prefer open or revise")
            check.unmet.append("objection_policy")
    else:
        check.details["has_objections"] = False

    if run.terminal == "open" or selected == "open":
        check.met.append("open_path_available")
        if not check.open_reasons and run.unresolved:
            check.open_reasons.extend(run.unresolved)

    if run.terminal == "blocked":
        check.ok = False
        check.unmet.append("run_blocked")
        check.open_reasons.append("run blocked before a verdict")

    if run.terminal == "refused":
        check.ok = False
        check.unmet.append("run_refused")
        check.open_reasons.append("capability or policy refusal")

    # Declared outcome prose is free text — we only mark structural checks.
    if check.ok and not check.unmet:
        check.met.append("structural_outcomes")
    return check
