"""Phase A: progressive COGNITION product contracts (SPEC v0.11)."""

from __future__ import annotations

from pathlib import Path

import deborah
from deborah import COGNITION_MVP, document_to_plan, parse_document, validate_document, validate_plan

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"

_PLAN = """\
PLAN p1 REVISION 1 [STATUS: draft]
  PARENT: none
  REQUEST: test
  TRIGGER: initial_request
  INTENT: demo cognition
  ON_UNCERTAINTY: record
  ASSUMES: milcah.critique@1
  PROCESS P (INPUT: x; OUTPUT: y)
    1. STEP — gather facts. [CODE, DETERMINISTIC]
       COGNITION: observe
       OUTPUT: evidence list
    2. STEP — form a claim. [LLM, STOCHASTIC]
       PURPOSE: interpret the facts
       COGNITION: infer
    3. STEP — score the claim. [LLM, STOCHASTIC]
       COGNITION: evaluate
    4. DECISION — pick a terminal. [HUMAN, GATED]
       COGNITION: decide
"""


def test_cognition_mvp_constants() -> None:
    assert COGNITION_MVP == {"observe", "infer", "evaluate", "decide"}


def test_parse_and_export_cognition_and_execution() -> None:
    doc = parse_document(_PLAN)
    assert doc.parse_errors == []
    assert validate_document(doc) == []
    plan = document_to_plan(doc)
    assert validate_plan(plan) == []
    cognitions = [s.get("cognition") for s in plan["steps"]]
    assert cognitions == ["observe", "infer", "evaluate", "decide"]
    assert plan["steps"][0].get("execution") == "deterministic"
    assert plan["steps"][1].get("execution") == "stochastic"
    assert plan["steps"][1].get("purpose")


def test_unknown_cognition_is_well_formedness_error() -> None:
    text = """\
PROCESS P (INPUT: a; OUTPUT: b)
  1. STEP — invent. [LLM]
     COGNITION: hallucinate
"""
    doc = parse_document(text)
    errors = validate_document(doc)
    assert any("unknown COGNITION" in e for e in errors)


def test_reserved_cognition_rejected_in_mvp() -> None:
    text = """\
PROCESS P (INPUT: a; OUTPUT: b)
  1. STEP — update priors. [LLM]
     COGNITION: learn
"""
    doc = parse_document(text)
    errors = validate_document(doc)
    assert any("reserved" in e and "learn" in e for e in errors)


def test_validate_plan_rejects_bad_cognition_on_dict() -> None:
    plan = dict(deborah.CANONICAL_PLAN)
    plan["steps"] = [dict(plan["steps"][0], cognition="teleport")]
    assert any("unknown cognition" in e for e in validate_plan(plan))


def test_golden_cross_llm_critique_example() -> None:
    path = EXAMPLES / "cross-llm-critique.cairn.md"
    doc = parse_document(path.read_text(encoding="utf-8"))
    assert doc.parse_errors == [], doc.parse_errors
    errors = validate_document(doc)
    assert errors == [], errors
    assert doc.plans
    plan = document_to_plan(doc)
    assert validate_plan(plan) == []
    assert plan["assumes"]
    assert "milcah.critique@1" in plan["assumes"]
    cognitions = [s.get("cognition") for s in plan["steps"] if s.get("cognition")]
    assert cognitions == ["observe", "infer", "evaluate", "decide"]
