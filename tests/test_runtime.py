"""Phase D: thin PLAN interpreter."""

from __future__ import annotations

import json
from pathlib import Path

from deborah import (
    EXAMPLE_RESULTS,
    StubHandler,
    document_to_plan,
    interpret_plan,
    parse_document,
)
from deborah.runtime.cli import main as run_main

GOLDEN = Path(__file__).resolve().parents[1] / "examples" / "cross-llm-critique.cairn.md"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "cognition_results.json"


def _golden_plan() -> dict:
    return document_to_plan(parse_document(GOLDEN.read_text(encoding="utf-8")))


def test_interpret_golden_with_demo_results_opens_on_decision() -> None:
    plan = _golden_plan()
    run = interpret_plan(
        plan,
        handler=StubHandler(results_by_cognition=EXAMPLE_RESULTS),
        validate_profile="full",
        check_contracts=True,
        contract_mode="strict",
    )
    # EXAMPLE decide selects "open" → residual → terminal open
    assert run.terminal == "open"
    assert len(run.steps) == 4
    assert all(s.status in {"completed", "skipped"} for s in run.steps)
    assert any(e["type"] == "plan.finished" for e in run.events)


def test_interpret_complete_when_decide_accepts() -> None:
    plan = _golden_plan()
    results = dict(EXAMPLE_RESULTS)
    results["decide"] = {
        "selected": "accept",
        "alternatives": ["accept", "reject", "open"],
        "committed": True,
        "confidence": {
            "evidence": "high",
            "inference": "high",
            "execution": "high",
        },
    }
    run = interpret_plan(
        plan,
        handler=StubHandler(results_by_cognition=results),
        check_contracts=True,
        contract_mode="strict",
    )
    assert run.terminal == "complete"
    assert run.steps[-1].result["selected"] == "accept"


def test_allow_list_blocks_unknown_call() -> None:
    plan = _golden_plan()
    # Restrict allow-list so milcah.critique is not permitted
    run = interpret_plan(
        plan,
        handler=StubHandler(results_by_cognition=EXAMPLE_RESULTS),
        allow_list={"tirzah.retrieve"},
        validate_profile="full",
    )
    assert run.terminal == "blocked"
    assert any(s.status == "blocked" for s in run.steps)


def test_capability_refusal() -> None:
    plan = _golden_plan()
    run = interpret_plan(
        plan,
        handler=StubHandler(
            results_by_cognition=EXAMPLE_RESULTS,
            refuse_tools={"milcah.critique"},
        ),
    )
    assert run.terminal == "refused"


def test_invalid_plan_blocked() -> None:
    run = interpret_plan({"plan_id": "x", "steps": []}, validate_profile="full")
    assert run.terminal == "blocked"
    assert run.errors


def test_max_steps_bound() -> None:
    plan = _golden_plan()
    run = interpret_plan(
        plan,
        handler=StubHandler(results_by_cognition=EXAMPLE_RESULTS),
        max_steps=2,
    )
    assert len(run.steps) == 2
    assert run.terminal == "blocked"
    assert any(e.get("type") == "plan.bound_reached" for e in run.events)


def test_strict_contract_failure_blocks_step() -> None:
    plan = _golden_plan()
    bad = dict(EXAMPLE_RESULTS)
    bad["infer"] = {"claim": "no refs"}  # missing evidence_refs
    run = interpret_plan(
        plan,
        handler=StubHandler(results_by_cognition=bad),
        check_contracts=True,
        contract_mode="strict",
    )
    assert run.terminal == "blocked"
    infer_step = next(s for s in run.steps if s.cognition == "infer")
    assert infer_step.contract_errors


def test_cli_demo(capsys) -> None:
    code = run_main([str(GOLDEN), "--demo-results", "--check-contracts", "--contract-mode", "strict"])
    # open is success exit for CLI
    assert code == 0
    out = capsys.readouterr().out
    assert "terminal: open" in out


def test_cli_json(capsys) -> None:
    code = run_main([str(GOLDEN), "--demo-results", "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["terminal"] in {"complete", "open", "blocked", "refused"}
    assert payload["steps"]
