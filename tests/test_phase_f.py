"""Phase F: extended cognitions, exploration_budget, reflective post-pass."""

from __future__ import annotations

from deborah import (
    EXAMPLE_RESULTS,
    StubHandler,
    document_to_plan,
    interpret_plan,
    parse_document,
    validate_document,
)


def test_parse_exploration_budget_and_reflective() -> None:
    text = """\
PLAN p1 REVISION 1 [STATUS: draft]
  PARENT: none
  REQUEST: r
  TRIGGER: initial_request
  ON_UNCERTAINTY: record
  EXPLORATION_BUDGET: 2
  REFLECTIVE_PASS: true
  PROCESS P (INPUT: a; OUTPUT: b)
    1. STEP — infer something. [LLM, STOCHASTIC]
       COGNITION: infer
       OUTPUT: claim
"""
    doc = parse_document(text)
    assert validate_document(doc) == []
    assert doc.plans[0].exploration_budget == 2
    assert doc.plans[0].reflective_pass is True
    plan = document_to_plan(doc)
    assert plan["exploration_budget"] == 2
    assert plan["reflective_pass"] is True


def test_reflective_pass_marks_residual_on_low_inference() -> None:
    plan = {
        "plan_id": "p",
        "revision": 1,
        "objective": "o",
        "status": "active",
        "steps": [
            {
                "id": "s1",
                "action": "infer",
                "construct": "STEP",
                "status": "pending",
                "cognition": "infer",
                "success_criteria": ["claim"],
            }
        ],
        "stopping_conditions": [],
        "revision_decision": "revise",
        "reflective_pass": True,
        "on_uncertainty": "record",
    }
    low = dict(EXAMPLE_RESULTS["infer"])
    low["confidence"] = {
        "evidence": "high",
        "inference": "low",
        "execution": "high",
    }
    run = interpret_plan(
        plan,
        handler=StubHandler(results_by_cognition={"infer": low}),
        reflective_pass=True,
        validate_profile="full",
    )
    assert any(e.get("type") == "plan.reflective.flagged" for e in run.events)
    assert run.terminal == "open"


def test_reentry_consumes_exploration_budget_once() -> None:
    plan = {
        "plan_id": "p",
        "revision": 1,
        "objective": "o",
        "status": "active",
        "steps": [
            {
                "id": "s1",
                "action": "infer",
                "construct": "STEP",
                "status": "pending",
                "cognition": "infer",
                "success_criteria": ["claim"],
            }
        ],
        "stopping_conditions": [],
        "revision_decision": "revise",
        "reflective_pass": True,
        "exploration_budget": 1,
        "on_uncertainty": "record",
    }
    low = dict(EXAMPLE_RESULTS["infer"])
    low["confidence"] = {"evidence": "high", "inference": "low", "execution": "high"}
    calls = {"n": 0}

    def counting_handler(step, context):
        calls["n"] += 1
        return {"status": "completed", "result": low}

    run = interpret_plan(
        plan,
        handler=counting_handler,
        allow_reentry=True,
        reflective_pass=True,
        validate_profile=None,
        max_steps=10,
    )
    # original + one reentry
    assert calls["n"] == 2
    assert any(e.get("type") == "plan.reentry.scheduled" for e in run.events)
    assert run.terminal == "open"


def test_no_reentry_without_flag() -> None:
    plan = {
        "plan_id": "p",
        "revision": 1,
        "objective": "o",
        "status": "active",
        "steps": [
            {
                "id": "s1",
                "action": "infer",
                "construct": "STEP",
                "status": "pending",
                "cognition": "infer",
            }
        ],
        "stopping_conditions": [],
        "revision_decision": "revise",
        "reflective_pass": True,
        "exploration_budget": 5,
        "on_uncertainty": "record",
    }
    low = dict(EXAMPLE_RESULTS["infer"])
    low["confidence"] = {"evidence": "high", "inference": "low", "execution": "high"}
    calls = {"n": 0}

    def counting_handler(step, context):
        calls["n"] += 1
        return {"status": "completed", "result": low}

    interpret_plan(
        plan,
        handler=counting_handler,
        allow_reentry=False,  # default
        reflective_pass=True,
        validate_profile=None,
    )
    assert calls["n"] == 1
