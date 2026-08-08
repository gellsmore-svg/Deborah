"""Regression tests for the 2026-08-08 functional/code review."""

from __future__ import annotations

from pathlib import Path

from deborah import (
    CANONICAL_PLAN,
    parse_document,
    validate_document,
    validate_plan,
)
from deborah.runtime.interpreter import StubHandler, _stem_allowed, interpret_plan
from deborah.render import render_plan


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_canonical_plan_passes_strict() -> None:
    assert validate_plan(CANONICAL_PLAN, profile="full") == []
    assert validate_plan(CANONICAL_PLAN, profile="strict") == [], validate_plan(
        CANONICAL_PLAN, profile="strict"
    )


def test_allow_list_rejects_substring_bypass() -> None:
    allow = {"tirzah.retrieve", "milcah.critique"}
    assert _stem_allowed("tirzah.retrieve", allow)
    assert _stem_allowed("milcah.critique", allow)
    assert _stem_allowed("milcah.critique@1", allow)
    assert not _stem_allowed("z", allow)
    assert not _stem_allowed("a", allow)
    assert not _stem_allowed("ret", allow)
    assert not _stem_allowed("evilmilcah.critique", allow)
    # Namespace child of an assumed stem is ok.
    assert _stem_allowed("tirzah.retrieve.deep", allow)


def test_validate_plan_rejects_cycles_and_dup_ids() -> None:
    plan = {
        "plan_id": "p",
        "revision": 1,
        "request": "x",
        "objective": "x",
        "status": "active",
        "steps": [
            {
                "id": "s1",
                "action": "a",
                "construct": "STEP",
                "status": "pending",
                "depends_on": ["s2"],
            },
            {
                "id": "s2",
                "action": "b",
                "construct": "STEP",
                "status": "pending",
                "depends_on": ["s1"],
            },
        ],
        "stopping_conditions": ["done"],
        "unresolved_questions": [],
        "revision_decision": "revise",
        "revision_reason": "",
    }
    errors = validate_plan(plan)
    assert any("cycle" in e for e in errors), errors

    plan2 = dict(plan)
    plan2["steps"] = [
        {"id": "s1", "action": "a", "construct": "STEP", "status": "pending", "depends_on": []},
        {"id": "s1", "action": "b", "construct": "STEP", "status": "pending", "depends_on": []},
    ]
    assert any("duplicate" in e for e in validate_plan(plan2))

    plan3 = dict(plan)
    plan3["steps"] = [
        {
            "id": "s1",
            "action": "a",
            "construct": "STEP",
            "status": "pending",
            "depends_on": ["s1"],
        },
    ]
    assert any("self-dependency" in e for e in validate_plan(plan3))


def test_interpret_reports_cycle_does_not_complete() -> None:
    plan = {
        "plan_id": "cycle",
        "revision": 1,
        "request": "x",
        "objective": "x",
        "status": "active",
        "steps": [
            {
                "id": "s1",
                "action": "a",
                "construct": "STEP",
                "status": "pending",
                "depends_on": ["s2"],
            },
            {
                "id": "s2",
                "action": "b",
                "construct": "STEP",
                "status": "pending",
                "depends_on": ["s1"],
            },
        ],
        "stopping_conditions": ["done"],
        "unresolved_questions": [],
        "revision_decision": "revise",
        "revision_reason": "",
        "assumes": [],
    }
    # Skip validate so we exercise interpreter cycle path alone.
    result = interpret_plan(plan, handler=StubHandler(), validate_profile=None)
    assert result.terminal != "complete"
    assert any("cycle" in e for e in result.errors)


def test_multi_process_narrative_keeps_headings() -> None:
    text = (EXAMPLES / "hoglah.cairn.md").read_text(encoding="utf-8")
    body = render_plan(text, profile="narrative_steps")
    if hasattr(body, "body"):
        body = body.body
    body = str(body)
    # Multiple PROCESS names should appear as headings.
    assert body.count("## ") >= 2
    assert "RunBridge" in body
    assert "Ingest" in body or "Work" in body


def test_all_examples_validate_without_allowlist() -> None:
    for path in sorted(EXAMPLES.glob("*.cairn.md")):
        doc = parse_document(path.read_text(encoding="utf-8"))
        wf = [e for e in validate_document(doc) if e not in doc.parse_errors]
        assert wf == [], f"{path.name}: {wf[:5]}"
