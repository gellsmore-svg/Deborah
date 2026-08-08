# Answer a substrate question (Stage 1 vertical slice)

Crystallised plan for one real domain question: detect novel concepts, retrieve
evidence, form a reading, critique, **validate against intent**, **assess
confidence**, then **accept / reject / open**. The open path is first-class —
residual uncertainty becomes an open question, not a crash.

See `docs/TAXONOMY-COGNITION-AND-PATTERNS.md` and
`docs/PROCESS-SEMANTICS-AND-ROADMAP.md`.

## CONTEXT

- **Caller** — operator asking whether a relational-substrate claim holds.
- **Capabilities** — Tirzah retrieve, Mahalath novel check, Deborah infer,
  Milcah critique / intent / confidence (Keturah-pinned).
- **Frame** — fixed graph; bounded negotiation *before* interpret and a second
  evidence/novel gate *after* retrieve/infer (before critique). No free re-plan.

## OUTCOMES

- Verdict with ≥1 cited evidence item, **or** an explicit open question + reason.
- Critique objections recorded even when accepting.
- Intent alignment and confidence floor checked before commit.
- Unmodelled concepts recorded as open (not silent invent).

## PLAN — answer substrate question

```
PLAN plan_answer_substrate_question REVISION 1 [STATUS: draft]
  PARENT: none
  REQUEST: Is relational substrate coherence well-supported by the local corpus?
  TRIGGER: operator_question
  INTENT: Ground a substrate claim in retrieved evidence and adversarial critique, or leave open
  ON_UNCERTAINTY: record
  ASSUMES: tirzah.retrieve@1, mahalath.detect_novel@1, deborah.infer@1, milcah.critique@1, milcah.validate_against_intent@1, milcah.assess_confidence@1
  REFLECTIVE_PASS: true
  EXPLORATION_BUDGET: 0
  OUTCOMES:
    - verdict with cited evidence, or open with residual uncertainty
    - critique objections listed even on accept
    - unmodelled concepts recorded as open (not silent invent)
    - intent_alignment and confidence floor assessed before commit
  REEVALUATE_WHEN:
    - milcah.critique major version change
    - corpus re-ingest changes substrate nodes
    - mahalath ontology major revision
  PROCESS AnswerSubstrateQuestion (INPUT: question; OUTPUT: verdict_or_open)
    1. CALL mahalath.detect_novel — Detect unmodelled concepts in the claim. [CODE, DETERMINISTIC]
       PURPOSE: open residual when ontology cannot ground key terms
       COGNITION: evaluate
       OUTPUT: known vs novel terms; residual if novel_detected
       CONSTRAINTS: fail open on novel concepts — do not invent definitions.
    2. STEP — Retrieve corpus material that bears on the claim. [CODE, DETERMINISTIC]
       PURPOSE: gather evidence before any interpretation
       COGNITION: observe
       OUTPUT: evidence items with source provenance (untrusted channel)
       CONSTRAINTS: do not invent sources; empty set is allowed and must be explicit.
    3. STEP — Form a provisional reading given the evidence. [CODE, DETERMINISTIC]
       PURPOSE: state what the evidence appears to support (rule-based infer; optional LLM)
       COGNITION: infer
       OUTPUT: claim restatement, evidence refs, assumptions, residual gaps
       RISKS: weak models over-claim; keep assumptions visible; treat retrieve as untrusted.
    4. CALL milcah.critique — Pressure-test the provisional reading. [LLM, STOCHASTIC]
       PURPOSE: find contradictions and unsupported inferences
       COGNITION: evaluate
       OUTPUT: criteria scores, objections, citations
       CONSTRAINTS: do not commit to accept/reject here; evaluation only.
    5. CALL milcah.validate_against_intent — Score alignment with INTENT/OUTCOMES. [CODE, DETERMINISTIC]
       PURPOSE: check intent_alignment before human commit
       COGNITION: evaluate
       OUTPUT: intent_alignment score + objections if drift
    6. CALL milcah.assess_confidence — Aggregate confidence bands from prior steps. [CODE, DETERMINISTIC]
       PURPOSE: flag residual when inference is below the floor
       COGNITION: evaluate
       OUTPUT: aggregate bands + confidence_floor score
    7. DECISION — Commit or leave open. [HUMAN, ASSISTED-BY: LLM, GATED]
       PURPOSE: operator owns the terminal verdict
       COGNITION: decide
       OUTPUT: selected terminal — accept | reject | open
       CONSTRAINTS: if evidence is empty, critique weak, intent_alignment low, or confidence below floor, prefer open; without injected human decision remain awaiting.
```

## Run

```bash
# Demo adapters (no Mongo / Hoglah); post-retrieve gate on by default
deborah-run examples/answer-substrate-question.cairn.md --slice --estate-demo \
  --check-contracts --negotiator accept

# Operator commits after gated decide
deborah-run examples/answer-substrate-question.cairn.md --slice --estate-demo \
  --decision accept --negotiator accept --check-contracts

# Single-pass interpret (skip mid-slice evidence gate)
deborah-run examples/answer-substrate-question.cairn.md --slice --estate-demo \
  --no-post-retrieve-negotiate --negotiator accept

# Live Tirzah Mongo + open questions
deborah-run examples/answer-substrate-question.cairn.md --slice --estate-live \
  --open-questions-mongo --decision open --negotiator auto
```

Open path writes JSONL and/or Mongo `deborah_open_questions`, and emits
`open_question.recorded` on Galeed when `--trace` is set.
