"""SAMPLE / VIEW / MERGE RULE — SPEC v0.13 reconstruction constructs."""

from __future__ import annotations

from pathlib import Path

from deborah import (
    CORE_CONSTRUCTS,
    EXTENSION_CONSTRUCTS,
    parse_document,
    validate_document,
    validate_plan,
)
from deborah.runtime.interpreter import interpret_plan


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"

FRAGMENT = """\
PROCESS IndependentReconstruction (INPUT: source; OUTPUT: answer_or_open)
  1. STEP — Write SOURCE. [CODE, DETERMINISTIC]
  2. SAMPLE [N: 5; STATE: isolated; FROM: source] Isolated reconstructions.
     2a. CALL Path(source) → reconstruction  [LLM, STOCHASTIC]
  3. MERGE [RULE: admissibility] Build an admissibility state.
  4. VIEW [ROLE: blind; EXPOSE: source; WITHHOLD: findings] Reconstructability probe.
"""


def test_sample_and_view_are_extension_not_core() -> None:
    assert "SAMPLE" in EXTENSION_CONSTRUCTS
    assert "VIEW" in EXTENSION_CONSTRUCTS
    assert "SAMPLE" not in CORE_CONSTRUCTS
    assert "VIEW" not in CORE_CONSTRUCTS


def test_fragment_parses_and_is_well_formed() -> None:
    doc = parse_document(FRAGMENT)
    assert not doc.parse_errors, doc.parse_errors
    assert validate_document(doc) == []
    proc = doc.processes[0]
    constructs = [s.construct for s in proc.steps]
    assert constructs[1] == "SAMPLE"
    assert constructs[2] == "MERGE"
    assert constructs[3] == "VIEW"


def test_sample_without_n_is_invalid() -> None:
    doc = parse_document(
        """\
PROCESS P (INPUT: s; OUTPUT: o)
  1. SAMPLE Isolated reconstructions.
"""
    )
    errors = validate_document(doc)
    assert any("SAMPLE must declare N or MAX" in e for e in errors), errors


def test_view_without_role_is_invalid() -> None:
    doc = parse_document(
        """\
PROCESS P (INPUT: s; OUTPUT: o)
  1. VIEW Project something.
"""
    )
    errors = validate_document(doc)
    assert any("VIEW must declare" in e for e in errors), errors


def test_unknown_merge_rule_is_invalid() -> None:
    doc = parse_document(
        """\
PROCESS P (INPUT: s; OUTPUT: o)
  1. MERGE [RULE: banana] Combine.
"""
    )
    errors = validate_document(doc)
    assert any("MERGE RULE" in e for e in errors), errors


def test_example_file_is_well_formed() -> None:
    text = (EXAMPLES / "independent-reconstruction.cairn.md").read_text(encoding="utf-8")
    doc = parse_document(text)
    assert not doc.parse_errors, doc.parse_errors
    errors = validate_document(doc)
    assert errors == [], errors


def test_core_profile_rejects_sample_in_a_plan() -> None:
    plan = {
        "plan_id": "p",
        "revision": 1,
        "request": "x",
        "objective": "x",
        "status": "draft",
        "steps": [
            {
                "id": "s1",
                "action": "sample",
                "construct": "SAMPLE",
                "status": "pending",
                "depends_on": [],
            }
        ],
        "stopping_conditions": ["done"],
        "unresolved_questions": [],
        "revision_decision": "revise",
        "revision_reason": "",
    }
    assert validate_plan(plan, profile="full") == []
    errors = validate_plan(plan, profile="core")
    assert any("SAMPLE" in e for e in errors), errors


def test_thin_runtime_skips_sample() -> None:
    plan = {
        "plan_id": "p",
        "revision": 1,
        "request": "x",
        "objective": "x",
        "status": "active",
        "steps": [
            {
                "id": "s1",
                "action": "sample",
                "construct": "SAMPLE",
                "status": "pending",
                "depends_on": [],
            }
        ],
        "stopping_conditions": ["done"],
        "unresolved_questions": [],
        "revision_decision": "stable",
        "revision_reason": "",
    }
    result = interpret_plan(plan, validate_profile="full")
    assert result.steps[0].status == "skipped"
    assert "not executed" in (result.steps[0].reason or "")
