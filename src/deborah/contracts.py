"""Cognitive product contracts for step results (SPEC process-semantic axes).

Phase C: when a step declares ``COGNITION``, a structured *result* artifact can
be checked against the expected product shape. Progressive:

- omit cognition → no product contract
- ``mode="soft"`` → type/shape issues only for fields that are present
- ``mode="strict"`` → required keys must be present

Confidence uses **ordinal bands**, not a single float as system of record.

Re-entry policy (documented, not implemented here): process-level re-entry on
low inference confidence is **opt-in**, requires an explicit bound (MAX / plan
budget), and defaults to plan ``ON_UNCERTAINTY`` (``record`` / ``escalate``)
rather than silent re-planning. See ``docs/PROCESS-SEMANTICS-AND-ROADMAP.md``.
"""

from __future__ import annotations

from typing import Any

from deborah.conformance import COGNITION_MVP, COGNITION_RESERVED

CONTRACT_VERSION = "1.0"

CONFIDENCE_BANDS: frozenset[str] = frozenset({"high", "medium", "low", "unassessed"})
CONFIDENCE_DIMENSIONS: tuple[str, ...] = ("evidence", "inference", "execution")
CONTRACT_MODES: frozenset[str] = frozenset({"soft", "strict"})

# Required top-level keys per cognition under strict mode.
REQUIRED_RESULT_KEYS: dict[str, tuple[str, ...]] = {
    "observe": ("evidence",),
    "infer": ("claim", "evidence_refs"),
    "evaluate": ("criteria",),
    "decide": ("selected",),
}


def validate_confidence(confidence: Any, *, path: str = "confidence") -> list[str]:
    """Validate a layered confidence object (bands on three dimensions)."""
    if confidence is None:
        return []
    if not isinstance(confidence, dict):
        return [f"{path} must be an object with dimensions {list(CONFIDENCE_DIMENSIONS)}"]
    errors: list[str] = []
    for dim in CONFIDENCE_DIMENSIONS:
        if dim not in confidence:
            continue
        band = confidence[dim]
        if band is None or band == "":
            continue
        if str(band).strip().lower() not in CONFIDENCE_BANDS:
            errors.append(
                f"{path}.{dim} must be one of {sorted(CONFIDENCE_BANDS)}, got {band!r}"
            )
    # Reject lone float as the only form of confidence
    if set(confidence.keys()) <= {"value", "score"} or (
        len(confidence) == 1 and "value" in confidence and isinstance(confidence["value"], (int, float))
    ):
        errors.append(
            f"{path}: use band dimensions {list(CONFIDENCE_DIMENSIONS)}, "
            f"not a single float as system of record"
        )
    if "basis" in confidence and confidence["basis"] is not None:
        if not isinstance(confidence["basis"], str):
            errors.append(f"{path}.basis must be a string when present")
    return errors


def _require_list(result: dict[str, Any], key: str, path: str, errors: list[str]) -> None:
    if key not in result:
        return
    if not isinstance(result[key], list):
        errors.append(f"{path}.{key} must be a list")


def _validate_observe(result: dict[str, Any], path: str, *, strict: bool) -> list[str]:
    errors: list[str] = []
    if strict and "evidence" not in result:
        errors.append(f"{path}: observe requires evidence[]")
    _require_list(result, "evidence", path, errors)
    evidence = result.get("evidence")
    if isinstance(evidence, list):
        for i, item in enumerate(evidence):
            if not isinstance(item, dict):
                errors.append(f"{path}.evidence[{i}] must be an object")
                continue
            if strict and not (
                item.get("statement") or item.get("text") or item.get("content")
            ):
                errors.append(
                    f"{path}.evidence[{i}] needs statement|text|content under strict mode"
                )
            # provenance encouraged but not required in soft
            if strict and not (item.get("source") or item.get("provenance") or item.get("trace_ref")):
                errors.append(
                    f"{path}.evidence[{i}] needs source|provenance|trace_ref under strict mode"
                )
    # observe must not require a claim; if claim present, warn via soft? keep silent soft.
    if strict and result.get("claim") and not result.get("evidence"):
        errors.append(f"{path}: observe with claim but no evidence is not a pure observe product")
    return errors


def _validate_infer(result: dict[str, Any], path: str, *, strict: bool) -> list[str]:
    errors: list[str] = []
    if strict:
        if not str(result.get("claim") or "").strip():
            errors.append(f"{path}: infer requires claim")
        if "evidence_refs" not in result:
            errors.append(f"{path}: infer requires evidence_refs[]")
    _require_list(result, "evidence_refs", path, errors)
    _require_list(result, "assumptions", path, errors)
    if "alternatives" in result:
        _require_list(result, "alternatives", path, errors)
    errors.extend(validate_confidence(result.get("confidence"), path=f"{path}.confidence"))
    if strict and result.get("confidence") is None:
        errors.append(f"{path}: infer should include confidence bands under strict mode")
    return errors


def _validate_evaluate(result: dict[str, Any], path: str, *, strict: bool) -> list[str]:
    errors: list[str] = []
    if strict and "criteria" not in result:
        errors.append(f"{path}: evaluate requires criteria[]")
    _require_list(result, "criteria", path, errors)
    has_scores = result.get("scores") is not None
    has_ranking = result.get("ranking") is not None
    if has_scores and not isinstance(result["scores"], (dict, list)):
        errors.append(f"{path}.scores must be an object or list")
    if has_ranking and not isinstance(result["ranking"], list):
        errors.append(f"{path}.ranking must be a list")
    if strict and not has_scores and not has_ranking:
        errors.append(f"{path}: evaluate requires scores or ranking under strict mode")
    # evaluate must not require selected commitment
    errors.extend(validate_confidence(result.get("confidence"), path=f"{path}.confidence"))
    return errors


def _validate_decide(result: dict[str, Any], path: str, *, strict: bool) -> list[str]:
    errors: list[str] = []
    if strict and result.get("selected") in (None, ""):
        errors.append(f"{path}: decide requires selected")
    _require_list(result, "alternatives", path, errors)
    _require_list(result, "constraints", path, errors)
    if "committed" in result and result["committed"] is not None:
        if not isinstance(result["committed"], bool):
            errors.append(f"{path}.committed must be a boolean when present")
    elif strict:
        # default: selected implies commitment unless committed: false
        pass
    errors.extend(validate_confidence(result.get("confidence"), path=f"{path}.confidence"))
    return errors


_VALIDATORS = {
    "observe": _validate_observe,
    "infer": _validate_infer,
    "evaluate": _validate_evaluate,
    "decide": _validate_decide,
}


def validate_cognition_result(
    cognition: str | None,
    result: Any,
    *,
    mode: str = "soft",
    path: str = "result",
) -> list[str]:
    """Validate a structured step result against a cognition product contract.

    Returns a list of error strings (empty = ok). ``mode`` is ``soft`` or ``strict``.
    """
    if mode not in CONTRACT_MODES:
        return [f"unknown contract mode {mode!r} (allowed: {sorted(CONTRACT_MODES)})"]
    if cognition is None or str(cognition).strip() == "":
        return []
    value = str(cognition).strip().lower()
    if value in COGNITION_RESERVED:
        return [
            f"{path}: cognition {value!r} is reserved; MVP allows {sorted(COGNITION_MVP)}"
        ]
    if value not in COGNITION_MVP:
        return [f"{path}: unknown cognition {value!r} (allowed: {sorted(COGNITION_MVP)})"]
    if result is None:
        if mode == "strict":
            return [f"{path}: strict mode requires a result object for cognition {value!r}"]
        return []
    if not isinstance(result, dict):
        return [f"{path} must be an object for cognition {value!r}"]
    return _VALIDATORS[value](result, path, strict=(mode == "strict"))


def validate_step_results(
    plan: dict[str, Any],
    *,
    mode: str = "soft",
) -> list[str]:
    """Validate ``result`` (or ``cognition_result``) on each plan step that has one.

    Steps without a result object are skipped in soft mode; in strict mode, any
    step with ``cognition`` set must include ``result``.
    """
    if not isinstance(plan, dict):
        return ["plan must be an object"]
    steps = plan.get("steps")
    if not isinstance(steps, list):
        return ["plan.steps must be a list"]
    errors: list[str] = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        cognition = step.get("cognition")
        result = step.get("result", step.get("cognition_result"))
        if cognition and result is None and mode == "strict":
            errors.append(
                f"step[{index}]: strict result check requires result for cognition {cognition!r}"
            )
            continue
        if result is None and not cognition:
            continue
        errors.extend(
            validate_cognition_result(
                cognition,
                result,
                mode=mode,
                path=f"step[{index}].result",
            )
        )
    return errors


# Illustrative minimal fixtures (also used in tests).
EXAMPLE_RESULTS: dict[str, dict[str, Any]] = {
    "observe": {
        "evidence": [
            {
                "statement": "CPU utilisation remained above 95% for 20 minutes.",
                "source": "metrics.prom",
                "trace_ref": "obs_001",
            }
        ],
    },
    "infer": {
        "claim": "The service is likely CPU-bound.",
        "evidence_refs": ["obs_001"],
        "assumptions": ["No concurrent network saturation"],
        "alternatives": ["GC thrashing"],
        "confidence": {
            "evidence": "high",
            "inference": "medium",
            "execution": "high",
            "basis": "single metric window",
        },
    },
    "evaluate": {
        "criteria": ["groundedness", "internal_consistency"],
        "scores": {"groundedness": "high", "internal_consistency": "medium"},
        "ranking": ["option_a", "option_b"],
        "confidence": {
            "evidence": "high",
            "inference": "medium",
            "execution": "high",
        },
    },
    "decide": {
        "selected": "open",
        "alternatives": ["accept", "reject", "open"],
        "constraints": ["prefer open when underspecified"],
        "committed": True,
        "confidence": {
            "evidence": "medium",
            "inference": "low",
            "execution": "high",
            "basis": "critique marked underspecified",
        },
    },
}
