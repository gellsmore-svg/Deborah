"""Round-robin / turn-based QUEUE steps must render their semantics, not a bare
"Queue:" — the ORDER / ROUNDS / UNTIL parameters carry the meaning."""

from __future__ import annotations

from deborah.render import render_plan
from deborah.render.phrasing import describe_queue, parse_queue_params, phrase_construct

_TAGS = ["ORDER: ROUND_ROBIN; ONE_AT_A_TIME; ROUNDS: 5; UNTIL: consensus"]

_EXAMPLE = """## OUTCOMES
A verdict.

## PROCESS — Formal

```
PROCESS Debate (INPUT: claim; OUTPUT: verdict)
  1. STEP — frame the claim. [CODE, DETERMINISTIC]
  2. QUEUE [ORDER: ROUND_ROBIN; ONE_AT_A_TIME; ROUNDS: 5; UNTIL: consensus]
     2a. CALL Proposer(claim) → argument   [LLM, STOCHASTIC]
     2b. CALL Challenger(claim) → rebuttal  [LLM, STOCHASTIC]
  3. CALL Summarise(transcript) → verdict   [LLM, STOCHASTIC]
```
"""


def test_parse_queue_params() -> None:
    p = parse_queue_params(_TAGS)
    assert p == {"order": "ROUND_ROBIN", "rounds": "5", "until": "consensus", "serial": True}
    assert parse_queue_params(["ORDER: PRIORITY"]) == {"order": "PRIORITY"}
    assert parse_queue_params(["MAX: 3"]) == {"rounds": "3"}
    assert parse_queue_params([]) == {}


def test_describe_queue_english() -> None:
    assert describe_queue(_TAGS) == (
        "Queue the participants round-robin, one at a time, "
        "for up to 5 rounds, until consensus"
    )
    # No parameters → a sensible default, never empty.
    assert describe_queue([]) == "Queue the participants in turn"
    assert describe_queue(["ORDER: PRIORITY"]) == "Queue the participants by priority"
    # Singular round.
    assert "for up to 1 round" in describe_queue(["ORDER: ROUND_ROBIN; ROUNDS: 1"])


def test_describe_queue_localised() -> None:
    fr = describe_queue(_TAGS, "fr")
    assert fr.startswith("Mettre les participants en file à tour de rôle")
    assert "un à la fois" in fr and "5 tours" in fr
    es = describe_queue(_TAGS, "es")
    assert es.startswith("Encolar a los participantes por turnos rotativos")
    assert "uno a la vez" in es and "5 rondas" in es


def test_phrase_construct_queue_uses_description() -> None:
    out = phrase_construct("QUEUE", "", "en", _TAGS)
    assert out == describe_queue(_TAGS)
    # Backward compatible: other constructs unchanged, tags optional.
    assert phrase_construct("CALL", "Foo()", "en") == "Invoke Foo()"
    assert phrase_construct("ITERATE", "the batch", "en") == "Repeat the following: the batch"


def test_narrative_view_shows_round_robin() -> None:
    out = render_plan(_EXAMPLE, profile="narrative_steps")
    assert "round-robin" in out
    assert "for up to 5 rounds" in out
    assert "until consensus" in out
    assert "Queue: " not in out  # the old bare rendering is gone


def test_operator_view_no_longer_empty_for_queue() -> None:
    out = render_plan(_EXAMPLE, profile="operator")
    # The QUEUE step previously rendered an empty "Purpose:"; now it is described.
    assert "round-robin" in out
    assert "**Purpose:** \n" not in out and not out.rstrip().endswith("**Purpose:**")


def test_mermaid_labels_the_queue() -> None:
    out = render_plan(_EXAMPLE, profile="narrative_steps", output_format="mermaid")
    assert "round-robin" in out


def test_audit_view_still_carries_parameters() -> None:
    out = render_plan(_EXAMPLE, profile="audit")
    assert "[QUEUE]" in out
    assert "ROUND_ROBIN" in out
