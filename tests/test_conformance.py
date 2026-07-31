from deborah import (
    CANONICAL_PLAN,
    PLAN_CONSTRUCTS,
    is_conformant,
    validate_plan,
)


def test_canonical_fixture_is_conformant() -> None:
    assert validate_plan(CANONICAL_PLAN) == []
    assert is_conformant(CANONICAL_PLAN)


def test_missing_fields_are_reported() -> None:
    errors = validate_plan({"plan_id": "p", "steps": []})
    assert any("missing plan field: objective" in e for e in errors)
    assert any("at least one step" in e for e in errors)


def test_invalid_construct_and_status_rejected() -> None:
    plan = dict(CANONICAL_PLAN)
    plan["status"] = "bogus"
    plan["steps"] = [dict(CANONICAL_PLAN["steps"][0], construct="WAT")]
    errors = validate_plan(plan)
    assert any("invalid plan status" in e for e in errors)
    assert any("invalid construct: 'WAT'" in e for e in errors)


def test_tirzah_step_constructs_are_in_the_grammar() -> None:
    # the constructs Tirzah's planner is allowed to emit must all be Cairn constructs
    assert {"STEP", "CALL", "ITERATE", "DECISION", "RECURSE"} <= PLAN_CONSTRUCTS


def test_invalid_step_status_rejected() -> None:
    plan = dict(CANONICAL_PLAN)
    plan["steps"] = [dict(CANONICAL_PLAN["steps"][0], status="running")]
    errors = validate_plan(plan)
    assert any("invalid status: 'running'" in e for e in errors)


def test_grammar_constructs_all_validate():
    """Drift guard: every construct the grammar parser accepts as a step must
    also pass validate_plan. The grammar and the conformance surface share one
    construct set (CORE + EXTENSION), so a document that PARSES must VALIDATE."""
    import re as _re

    import deborah
    from deborah.grammar.parser import _CONSTRUCT_NORMALIZE, _CONSTRUCT_STEP

    names = sorted({n for n in _re.findall(r"[A-Z_]{3,}", _CONSTRUCT_STEP.pattern)})
    offenders = []
    for name in names:
        src = (
            "## PROCESS — Formal\n```\n"
            "PROCESS P (INPUT: a; OUTPUT: b)\n"
            f"  1. {name} — do a thing. [CODE]\n"
            "  2. STEP — do another. [CODE]\n```\n"
        )
        plan = deborah.document_to_plan(deborah.parse_document(src))
        if any("invalid construct" in e for e in deborah.validate_plan(plan)):
            offenders.append(_CONSTRUCT_NORMALIZE.get(name, name))
    assert not offenders, f"grammar accepts constructs conformance rejects: {offenders}"
