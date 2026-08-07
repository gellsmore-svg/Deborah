# Answer a substrate question (Stage 1 vertical slice)

Crystallised plan for one real domain question: retrieve evidence, form a
reading, critique, then **accept / reject / open**. The open path is first-class
— residual uncertainty becomes an open question, not a crash.

See `docs/TAXONOMY-COGNITION-AND-PATTERNS.md` (product vs pattern) and
`docs/PROCESS-SEMANTICS-AND-ROADMAP.md`.

## CONTEXT

- **Caller** — operator asking whether a relational-substrate claim holds.
- **Capabilities** — `tirzah.retrieve`, `milcah.critique` (Keturah-pinned).
- **Frame** — fixed graph; negotiation (if any) is bounded *before* interpret.

## OUTCOMES

- Verdict with ≥1 cited evidence item, **or** an explicit open question + reason.
- Critique objections recorded even when accepting.
- Inference confidence not below the configured floor (default `low`).

## PLAN — answer substrate question

```
PLAN plan_answer_substrate_question REVISION 1 [STATUS: draft]
  PARENT: none
  REQUEST: Is relational substrate coherence well-supported by the local corpus?
  TRIGGER: operator_question
  INTENT: Ground a substrate claim in retrieved evidence and adversarial critique, or leave open
  ON_UNCERTAINTY: record
  ASSUMES: tirzah.retrieve@1, mahalath.detect_novel@1, milcah.critique@1, deborah.infer@1
  REFLECTIVE_PASS: true
  EXPLORATION_BUDGET: 0
  OUTCOMES:
    - verdict with cited evidence, or open with residual uncertainty
    - critique objections listed even on accept
    - unmodelled concepts recorded as open (not silent invent)
  REEVALUATE_WHEN:
    - milcah.critique major version change
    - corpus re-ingest changes substrate nodes
    - mahalath ontology major revision
  PROCESS AnswerSubstrateQuestion (INPUT: question; OUTPUT: verdict_or_open)
    1. STEP — Detect unmodelled concepts in the claim. [CODE, DETERMINISTIC]
       PURPOSE: open residual when ontology cannot ground key terms
       COGNITION: evaluate
       OUTPUT: known vs novel terms; residual if novel_detected
       CONSTRAINTS: fail open on novel concepts — do not invent definitions.
    2. STEP — Retrieve corpus material that bears on the claim. [CODE, DETERMINISTIC]
       PURPOSE: gather evidence before any interpretation
       COGNITION: observe
       OUTPUT: evidence items with source provenance
       CONSTRAINTS: do not invent sources; empty set is allowed and must be explicit.
    3. STEP — Form a provisional reading given the evidence. [CODE, DETERMINISTIC]
       PURPOSE: state what the evidence appears to support (rule-based infer; optional LLM)
       COGNITION: infer
       OUTPUT: claim restatement, evidence refs, assumptions, residual gaps
       RISKS: weak models over-claim; keep assumptions visible.
    4. CALL milcah.critique — Pressure-test the provisional reading. [LLM, STOCHASTIC]
       PURPOSE: find contradictions and unsupported inferences
       COGNITION: evaluate
       OUTPUT: criteria scores, objections, citations
       CONSTRAINTS: do not commit to accept/reject here; evaluation only.
    5. DECISION — Commit or leave open. [HUMAN, ASSISTED-BY: LLM, GATED]
       PURPOSE: operator owns the terminal verdict
       COGNITION: decide
       OUTPUT: selected terminal — accept | reject | open
       CONSTRAINTS: if evidence is empty or critique underspecified, prefer open; without injected human decision remain awaiting.
```

## Run

```bash
# Demo adapters (no Mongo / Hoglah)
deborah-run examples/answer-substrate-question.cairn.md --slice --estate-demo --check-contracts

# Live adapters when tirzah + milcah installed
deborah-run examples/answer-substrate-question.cairn.md --slice --estate-live --check-contracts \
  --open-questions /tmp/deborah-open-questions.jsonl \
  --question "Is relational substrate coherence well-supported?"
```

Open path writes a JSONL open-question record (local file; optional Mongo later).
