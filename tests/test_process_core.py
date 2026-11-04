"""The process-description core is a separate, overridable contract."""

from __future__ import annotations

from pathlib import Path

import cairn_core
from cairn_core import (
    CORE_VERSION,
    DEFAULT_METAMODEL,
    AnnotationRule,
    parse_document,
    validate_document,
    validate_plan,
)


def test_core_version_is_not_the_package_version():
    assert CORE_VERSION == "1.0.0"
    assert cairn_core.SPEC_VERSION == "0.15"
    assert cairn_core.CONFORMANCE_VERSION == "1.7"
    assert DEFAULT_METAMODEL.version == CORE_VERSION


def test_core_sources_do_not_import_deborah():
    root = Path(cairn_core.__file__).resolve().parent
    for path in root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "deborah" not in text, path.name


def test_extend_adds_a_construct_and_an_annotation():
    def links(text: str, lineno: int, model) -> list[str]:
        if text.strip() != "ok":
            return [f"line {lineno}: LINKS must be ok"]
        return []

    model = DEFAULT_METAMODEL.extend(
        extension_constructs=frozenset({"AUDIT"}),
        annotation_surfaces=("LINKS",),
        annotation_rules=(AnnotationRule("LINKS", links),),
    )
    source = """\
PROCESS P (INPUT: a; OUTPUT: b)
  1. AUDIT the books.
     LINKS: no
"""
    extended = parse_document(source, model=model)
    assert extended.parse_errors == []
    step = extended.processes[0].steps[0]
    assert step.construct == "AUDIT"
    assert step.annotations[0].keyword == "LINKS"
    assert any("LINKS must be ok" in error for error in validate_document(extended, model=model))

    plain = parse_document(source)
    assert plain.processes[0].steps[0].construct is None
    assert plain.processes[0].steps[0].annotations == []


def test_override_replaces_cognition_values():
    model = DEFAULT_METAMODEL.override(cognition_values=frozenset({"observe"}))
    source = """\
PROCESS P (INPUT: a; OUTPUT: b)
  1. Look.
     COGNITION: infer
"""
    document = parse_document(source, model=model)
    assert any("unknown COGNITION" in error for error in validate_document(document, model=model))
    assert validate_document(parse_document(source)) == []


def test_dropped_construct_is_rejected_on_a_plan():
    model = DEFAULT_METAMODEL.extend(dropped_constructs=frozenset({"SAMPLE"}))
    plan = {
        "plan_id": "p",
        "revision": 1,
        "objective": "Show the override.",
        "status": "draft",
        "steps": [{"id": "s1", "action": "Draw.", "construct": "SAMPLE", "status": "pending"}],
        "stopping_conditions": ["done"],
        "revision_decision": "stable",
    }
    assert any("invalid construct" in error for error in validate_plan(plan, model=model))
    assert not any("invalid construct" in error for error in validate_plan(plan))


def test_extra_step_check_runs():
    def flag(step, model) -> list[str]:
        if "hold" in step.text:
            return [f"line {step.lineno}: held"]
        return []

    model = DEFAULT_METAMODEL.extend(extra_step_checks=(flag,))
    source = """\
PROCESS P (INPUT: a; OUTPUT: b)
  1. hold the line.
"""
    document = parse_document(source, model=model)
    assert any("held" in error for error in validate_document(document, model=model))
