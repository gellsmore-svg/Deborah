"""Infer handler, GATED decide, novel-concept detection."""

from __future__ import annotations

from deborah.runtime.decide import gated_decision_outcome, step_is_gated
from deborah.runtime.infer import rule_based_infer, make_infer_handler
from deborah.runtime.interpreter import StubHandler, interpret_plan


def test_rule_based_infer_empty_evidence() -> None:
    product = rule_based_infer("Is X true?", [])
    assert product["residual_gaps"]
    assert product["evidence_refs"] == []
    assert product["confidence"]["inference"] == "low"


def test_rule_based_infer_with_evidence() -> None:
    product = rule_based_infer(
        "Is substrate coherent?",
        [
            {
                "statement": "Closed loops matter.",
                "source": "t:1",
                "trace_ref": "n1",
                "trust": {"level": "untrusted", "channel": "memory_retrieval"},
            }
        ],
    )
    assert "n1" in product["evidence_refs"]
    assert product["confidence"]["evidence"] in {"low", "medium"}
    assert product["evidence_trust"]["untrusted_count"] == 1
    assert any("untrusted" in a for a in product["assumptions"])


def test_infer_handler_reads_artifacts() -> None:
    h = make_infer_handler()
    out = h(
        {"id": "s3", "cognition": "infer"},
        {
            "claim": "Is Y supported?",
            "artifacts": {
                "s2": {
                    "evidence": [
                        {"statement": "hit", "source": "t", "trace_ref": "a"}
                    ]
                }
            },
        },
    )
    assert out["status"] == "completed"
    assert out["result"]["evidence_refs"] == ["a"]


def test_step_is_gated_from_action() -> None:
    assert step_is_gated(
        {
            "construct": "DECISION",
            "action": "— Commit. [HUMAN, ASSISTED-BY: LLM, GATED]",
        }
    )


def test_gated_decision_awaits_without_injection() -> None:
    out = gated_decision_outcome(
        {
            "id": "s5",
            "construct": "DECISION",
            "action": "[HUMAN, GATED]",
            "cognition": "decide",
        },
        {},
    )
    assert out["status"] == "awaiting_decision"
    assert out.get("residual") is True


def test_gated_decision_accepts_injection() -> None:
    out = gated_decision_outcome(
        {"id": "s5", "construct": "DECISION", "action": "[GATED]", "cognition": "decide"},
        {"decisions": {"s5": "accept"}},
    )
    assert out["status"] == "completed"
    assert out["result"]["selected"] == "accept"
    assert out["result"]["committed"] is True


def test_interpret_plan_gated_stops_and_opens() -> None:
    plan = {
        "plan_id": "p_gate",
        "on_uncertainty": "record",
        "steps": [
            {"id": "s1", "construct": "STEP", "cognition": "observe", "action": "x"},
            {
                "id": "s2",
                "construct": "DECISION",
                "cognition": "decide",
                "action": "Commit [HUMAN, GATED]",
            },
        ],
    }
    run = interpret_plan(
        plan,
        handler=StubHandler(
            results_by_cognition={
                "observe": {
                    "evidence": [{"statement": "e", "source": "s", "trace_ref": "1"}]
                }
            }
        ),
        validate_profile=None,
    )
    assert run.terminal == "open"
    assert any(s.status == "awaiting_decision" for s in run.steps)
    assert any("awaiting gated" in u for u in run.unresolved)


def test_interpret_plan_gated_with_decision_completes() -> None:
    plan = {
        "plan_id": "p_gate2",
        "on_uncertainty": "record",
        "steps": [
            {
                "id": "s1",
                "construct": "DECISION",
                "cognition": "decide",
                "action": "[GATED]",
            }
        ],
    }
    run = interpret_plan(
        plan,
        handler=StubHandler(),
        validate_profile=None,
        decisions={"s1": "reject"},
    )
    assert run.terminal == "complete"
    assert run.steps[0].result["selected"] == "reject"
