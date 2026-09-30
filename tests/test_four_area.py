"""Four-area EXTENSION: psych add, behavioural economics, game theory, HCI."""

from __future__ import annotations

from deborah import (
    CONFORMANCE_VERSION,
    EXTENSION_CONSTRUCTS,
    parse_document,
    validate_document,
    validate_plan,
    document_to_plan,
)
from deborah.grammar.parser import _CONSTRUCT_STEP


NEW_VERBS = (
    "AVOIDANCE",
    "HABIT",
    "ATTENTION",
    "INTERPERSONAL",
    "FRAME",
    "NUDGE",
    "ACCOUNT",
    "DISCOUNT",
    "GAME",
    "PLAY",
    "EQUILIBRIUM",
    "SIGNAL",
    "CHOICE",
    "GULF",
    "AFFORDANCE",
    "FORAGE",
)

SHOULD_MOD = {
    "AVOIDANCE": "[MODE: experiential]",
    "HABIT": "[PHASE: cue]",
    "ATTENTION": "[MODE: bias]",
    "INTERPERSONAL": "[PATTERN: attachment]",
    "FRAME": "[VALENCE: loss]",
    "NUDGE": "[TOOL: default]",
    "ACCOUNT": "[KIND: mental]",
    "DISCOUNT": "[SHAPE: hyperbolic]",
    "GAME": "[KIND: pd]",
    "PLAY": "[MOVE: cooperate]",
    "EQUILIBRIUM": "[CONCEPT: nash]",
    "SIGNAL": "[COST: costly]",
    "CHOICE": "[SET: 6]",
    "GULF": "[KIND: execution]",
    "AFFORDANCE": "[MAP: natural]",
    "FORAGE": "[SCENT: strong]",
}


def _proc(body: str) -> str:
    return (
        "PROCESS P (INPUT: a; OUTPUT: b)\n"
        f"{body}"
    )


def test_conformance_version_is_1_6() -> None:
    assert CONFORMANCE_VERSION == "1.6"


def test_new_verbs_are_extension_and_in_step_regex() -> None:
    pattern = _CONSTRUCT_STEP.pattern
    for name in NEW_VERBS:
        assert name in EXTENSION_CONSTRUCTS
        assert name in pattern


def test_each_new_verb_parses_and_validates_with_should_modifier() -> None:
    for name, mod in SHOULD_MOD.items():
        src = _proc(f"  1. {name} {mod} of the step. [CODE]\n")
        doc = parse_document(src)
        assert doc.parse_errors == [], (name, doc.parse_errors)
        errors = validate_document(doc)
        assert not any("should declare" in e for e in errors), (name, errors)
        plan = document_to_plan(doc)
        assert validate_plan(plan) == []


def test_missing_should_modifier_is_reported() -> None:
    src = _proc("  1. AVOIDANCE of the cue. [CODE]\n")
    errors = validate_document(parse_document(src))
    assert any("AVOIDANCE should declare MODE" in e for e in errors)


def test_choice_accepts_architecture_instead_of_set() -> None:
    src = _proc("  1. CHOICE [ARCHITECTURE: progressive] of options. [CODE]\n")
    errors = validate_document(parse_document(src))
    assert not any("CHOICE should declare" in e for e in errors)


def test_be_tag_requires_be_construct() -> None:
    src = _proc("  1. STEP pick an option. [NUDGED]\n")
    errors = validate_document(parse_document(src))
    assert any("behavioural-economic tags" in e for e in errors)


def test_gt_tag_requires_gt_construct() -> None:
    src = _proc("  1. STEP act. [RECIPROCAL]\n")
    errors = validate_document(parse_document(src))
    assert any("game-theoretic tags" in e for e in errors)


def test_hci_tag_requires_hci_construct() -> None:
    src = _proc("  1. STEP click. [OVERLOAD]\n")
    errors = validate_document(parse_document(src))
    assert any("hci tags" in e for e in errors)


def test_strategic_on_game_still_requires_org_construct() -> None:
    src = _proc("  1. GAME [KIND: pd] of the pairing. [STRATEGIC]\n")
    errors = validate_document(parse_document(src))
    assert any("organisational tags" in e for e in errors)


def test_hci_touchpoint_is_stored() -> None:
    src = _proc(
        "  1. CHOICE [SET: 6] of clinics. [INTERACTIVE]\n"
        "     HCI_TOUCHPOINT: directory page\n"
    )
    doc = parse_document(src)
    assert doc.parse_errors == []
    step = doc.processes[0].steps[0]
    keys = {a.keyword for a in step.annotations}
    assert "HCI_TOUCHPOINT" in keys


def test_decision_rule_same_bracket_is_modifier() -> None:
    src = _proc(
        "  1. FRAME [VALENCE: loss] of the menu. [HEURISTIC]\n"
        "  2. DECISION [ON: whether to search further; RULE: satisfice] stop. [HUMAN]\n"
    )
    doc = parse_document(src)
    assert doc.parse_errors == []
    step = doc.processes[0].steps[1]
    parsed = getattr(step, "parsed_modifiers", {}) or {}
    keys = {k.upper() for k in parsed} | {m.upper() for m in (step.modifiers or [])}
    blob = " ".join(step.tags).upper()
    assert "RULE" in keys or "satisfice" in str(parsed).lower()
    assert "RULE: SATISFICE" not in blob


def test_decision_rule_second_bracket_is_not_a_modifier() -> None:
    """Wrong form: second [RULE:] is a tag, not a construct modifier."""
    src = _proc(
        "  1. FRAME [VALENCE: gain] of the menu. [HEURISTIC]\n"
        "  2. DECISION [ON: x] [RULE: satisfice] stop. [HUMAN]\n"
    )
    doc = parse_document(src)
    step = doc.processes[0].steps[1]
    parsed = getattr(step, "parsed_modifiers", {}) or {}
    keys = {k.upper() for k in parsed}
    assert "RULE" not in keys


def test_lowercase_play_is_not_a_construct() -> None:
    src = _proc("  1. Play the recording. [CODE]\n")
    doc = parse_document(src)
    assert doc.processes[0].steps[0].construct in {None, "STEP"}


def test_condition_map_is_not_validated_against_codes() -> None:
    src = _proc(
        "  1. AVOIDANCE [MODE: experiential] of the cue. [AVOIDANT]\n"
        "     CONDITION_MAP: not-a-real-code XYZ-999\n"
    )
    errors = validate_document(parse_document(src))
    assert not any("XYZ" in e or "CONDITION_MAP" in e for e in errors)
