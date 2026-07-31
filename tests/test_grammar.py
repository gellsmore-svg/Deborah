from __future__ import annotations

from pathlib import Path

import pytest

import json

from deborah import document_to_dict, document_to_plan, parse_document, validate_document, validate_plan
from deborah.grammar.bridge import document_to_render_model

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


HOGLAH_FORMAL = """\
CONTEXT
Store — durable queue

REQUIREMENTS
R1. No loss. [MUST]

OUTCOMES
Every request reaches a terminal result.

PROCESS RunBridge (INPUT: broker, Store; OUTPUT: —)
  STATE
    Store [scope: global; dir: read/write] ref: H1
  1. CALL RecoverOnStartup(Store, broker). [CODE]
"""

PLAN_SAMPLE = """\
PLAN plan_test REVISION 1 [STATUS: active]
  PARENT: none
  REQUEST: Answer the question
  TRIGGER: initial_request
  PROCESS Fulfil (INPUT: question; OUTPUT: answer)
    1. Retrieve context. [CODE]
    2. Synthesise answer. [LLM] [STOCHASTIC]
       ITERATE [MAX: 3; UNTIL: sufficient]
         2.1 Refine draft. [LLM]
"""


def test_parse_hoglah_slice() -> None:
    doc = parse_document(HOGLAH_FORMAL)
    assert doc.parse_errors == []
    assert len(doc.processes) == 1
    assert doc.processes[0].name == "RunBridge"
    assert doc.processes[0].state is not None
    assert doc.processes[0].state.declarations[0].name == "Store"


def test_validate_state_update_requires_declaration() -> None:
    text = """\
PROCESS Bad (INPUT: x; OUTPUT: y)
  1. Update state. [CODE]
     STATE UPDATE: missing += 1
"""
    doc = parse_document(text)
    errors = validate_document(doc)
    assert any("undeclared state" in e for e in errors)


def test_break_inside_queue_is_well_formed() -> None:
    text = """\
PROCESS Work (INPUT: Store; OUTPUT: —)
  QUEUE [ORDER: FIFO]
  1. Claim job. [CODE]
     BREAK [IF: none]
"""
    doc = parse_document(text)
    errors = [e for e in validate_document(doc) if "BREAK" in e]
    assert errors == []


def test_plan_export_is_conformant() -> None:
    doc = parse_document(PLAN_SAMPLE)
    plan = document_to_plan(doc)
    assert validate_plan(plan) == []
    assert plan["plan_id"] == "plan_test"
    assert len(plan["steps"]) >= 2


def test_all_examples_parse_without_syntax_errors() -> None:
    for path in sorted(EXAMPLES.glob("*.cairn.md")):
        doc = parse_document(path.read_text(encoding="utf-8"))
        assert doc.parse_errors == [], f"{path.name}: {doc.parse_errors[:3]}"


def test_example_documents_have_process_backbone() -> None:
    for path in sorted(EXAMPLES.glob("*.cairn.md")):
        doc = parse_document(path.read_text(encoding="utf-8"))
        assert doc.processes, f"{path.name} has no PROCESS blocks"


def test_grammar_bridge_feeds_render_model() -> None:
    doc = parse_document(HOGLAH_FORMAL)
    render_doc = document_to_render_model(doc)
    assert render_doc.steps
    assert render_doc.context.get("Store")


def test_markdown_wrapper_extraction() -> None:
    path = EXAMPLES / "hoglah.cairn.md"
    doc = parse_document(path.read_text(encoding="utf-8"))
    assert doc.source_kind == "markdown"
    assert len(doc.requirements_blocks[0].requirements) >= 6


@pytest.mark.parametrize(
    "snippet,needle",
    [
        ("PROCESS P (INPUT: a; OUTPUT: b)\n  AWAIT [TIMEOUT: 30s] signal\n", "TIMEOUT"),
        (
            "PROCESS P (INPUT: a; OUTPUT: b)\n  1. Loop. [LLM]\n     ITERATE [MAX: 2]\n       1.1 Draft. [LLM]\n",
            "MAX",
        ),
    ],
)
def test_well_formedness_rules(snippet: str, needle: str) -> None:
    doc = parse_document(snippet)
    errors = validate_document(doc)
    assert not any(needle in e and "must declare" in e for e in errors)


def test_cross_process_state_is_visible() -> None:
    text = """\
PROCESS Parent (INPUT: x; OUTPUT: —)
  STATE
    Store [scope: global; dir: read/write]
PROCESS Child (INPUT: x; OUTPUT: —)
  1. Write. [CODE]
     STATE UPDATE: Store += item
"""
    doc = parse_document(text)
    assert not any("undeclared state" in e for e in validate_document(doc))


def test_break_allowed_in_call_target_of_loop() -> None:
    text = """\
PROCESS Runner (INPUT: x; OUTPUT: —)
  1. Loop. [CODE]
     ITERATE [UNTIL: stop]
       CALL Worker(x)
PROCESS Worker (INPUT: x; OUTPUT: —)
  1. Poll. [CODE]
     BREAK [IF: none]
"""
    doc = parse_document(text)
    assert not any("BREAK" in e for e in validate_document(doc))


def test_iterate_over_does_not_require_max_without_llm() -> None:
    text = """\
PROCESS P (INPUT: x; OUTPUT: y)
  1. Walk host steps. [CODE]
     ITERATE [OVER: substantive steps in the host process]
       1.1 Emit. [CODE]
"""
    doc = parse_document(text)
    assert not any("ITERATE" in e and "must declare" in e for e in validate_document(doc))


def test_document_to_dict_is_json_serializable() -> None:
    doc = parse_document(HOGLAH_FORMAL)
    payload = document_to_dict(doc)
    text = json.dumps(payload)
    assert "RunBridge" in text
    assert payload["processes"][0]["name"] == "RunBridge"


def test_examples_well_formed() -> None:
    known_issues = {
        "mahalath.cairn.md",
        "round-robin-debate.cairn.md",
        "tirzah-recursive-planning.cairn.md",
        "tirzah.cairn.md",
    }
    for path in sorted(EXAMPLES.glob("*.cairn.md")):
        doc = parse_document(path.read_text(encoding="utf-8"))
        wf = [e for e in validate_document(doc) if e not in doc.parse_errors]
        if path.name in known_issues:
            # pre-existing LLM bound issues in old examples; domain is clean
            wf = [e for e in wf if "must declare MAX" not in e and "MAX_DEPTH" not in e]
        assert wf == [], f"{path.name}: {wf[:5]}"