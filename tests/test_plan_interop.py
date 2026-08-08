"""Deborah ↔ Tirzah shared PLAN format interop.

Tirzah's recursive planner emits validate_plan-compatible dicts (see Tirzah
``test_tirzah_plan_conforms_to_deborah_grammar``). This fixture freezes the
``fallback_plan`` shape so Deborah can validate and thin-interpret without
importing Tirzah (heavy runtime deps).
"""

from __future__ import annotations

import json
from pathlib import Path

from deborah.conformance import validate_plan
from deborah.runtime.interpreter import StubHandler, interpret_plan

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "tirzah_fallback_plan.json"


def _tirzah_fallback() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_tirzah_fallback_fixture_validates_full() -> None:
    plan = _tirzah_fallback()
    assert validate_plan(plan, profile="full") == []
    assert validate_plan(plan, profile="core") == []


def test_tirzah_fallback_fixture_has_retrieval_and_synthesis() -> None:
    plan = _tirzah_fallback()
    tools = [
        tuple(s.get("allowed_tools") or [])
        for s in plan["steps"]
        if isinstance(s, dict)
    ]
    assert ("tirzah_retrieval",) in tools
    assert ("answer_adapter",) in tools
    constructs = [str(s.get("construct") or "").upper() for s in plan["steps"]]
    assert "RECURSE" in constructs
    assert "CALL" in constructs


def test_deborah_thin_interpret_tirzah_fallback() -> None:
    """Thin runtime walks Tirzah fallback without free re-planning."""
    plan = _tirzah_fallback()
    # Allow Tirzah tool stems so CALL steps are not blocked
    run = interpret_plan(
        plan,
        handler=StubHandler(),
        allow_list={"tirzah_retrieval", "answer_adapter"},
        validate_profile="full",
        check_contracts=False,
    )
    assert run.terminal in {"complete", "open", "blocked"}
    # At least interpret + retrieve + synthesize should start
    assert len(run.steps) >= 3
    assert not run.errors or run.terminal != "blocked" or "validation" not in " ".join(
        run.errors
    ).lower()


def test_live_tirzah_fallback_when_importable() -> None:
    """If Tirzah is installed, live fallback_plan must still validate."""
    try:
        from tirzah.planning.recursive import fallback_plan  # type: ignore[import-not-found]
    except Exception:
        import pytest

        pytest.skip("tirzah not importable in this environment")

    plan = fallback_plan(
        "Research relational substrate",
        plan_id="live_interop",
        reason="deborah interop test",
    )
    d = plan.to_dict()
    assert validate_plan(d, profile="full") == []
