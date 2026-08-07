# Cross-LLM critique (SPEC v0.11 golden example)

Crystallised plan for framed caller↔capability work: **observe → infer →
evaluate → decide/open**. Demonstrates process-semantic axes without claiming
that stochastic steps are pure functions.

- **HOW:** `[CODE, DETERMINISTIC]` vs `[LLM, STOCHASTIC]`
- **PRODUCT:** `COGNITION: observe|infer|evaluate|decide`
- **FRAME:** PLAN `INTENT`, `OUTCOMES`, `ASSUMES`, `ON_UNCERTAINTY`
- **CONTROL:** linear steps + residual open (not free re-planning)

## CONTEXT

- **Caller** — an operator or agent asking whether a substrate claim holds.
- **Capabilities** — retrieval and critique surfaces (Keturah-pinned names).
- **Frame** — fixed plan graph; model sampling only where tagged STOCHASTIC.

## OUTCOMES

- A grounded verdict **or** an explicit open question with reason.
- Every inference cites retrieved evidence.
- Critique objections are recorded even when the claim is accepted.

## PLAN — critique claim

```
PLAN plan_cross_llm_critique REVISION 1 [STATUS: draft]
  PARENT: none
  REQUEST: Is the claim about relational substrate coherence well-supported?
  TRIGGER: initial_request
  INTENT: Accept, reject, or leave open a domain claim with evidence and critique
  ON_UNCERTAINTY: record
  ASSUMES: tirzah.retrieve@1, milcah.critique@1
  OUTCOMES:
    - verdict with cited evidence, or open with residual uncertainty
    - critique objections listed even on accept
  REEVALUATE_WHEN:
    - milcah.critique major version change
  PROCESS CritiqueClaim (INPUT: claim; OUTPUT: verdict_or_open)
    1. STEP — Retrieve material that bears on the claim. [CODE, DETERMINISTIC]
       PURPOSE: gather evidence before any interpretation
       COGNITION: observe
       OUTPUT: evidence items with source provenance
       CONSTRAINTS: do not invent sources; empty set is allowed and must be explicit.
    2. STEP — Form a provisional reading of the claim given the evidence. [LLM, STOCHASTIC]
       PURPOSE: state what the evidence appears to support
       COGNITION: infer
       OUTPUT: claim restatement, evidence refs, assumptions, residual gaps
       RISKS: weak models over-claim; keep assumptions visible.
    3. CALL milcah.critique — Pressure-test the provisional reading. [LLM, STOCHASTIC]
       PURPOSE: find contradictions and unsupported inferences
       COGNITION: evaluate
       OUTPUT: criteria scores, objections, citations
       CONSTRAINTS: do not commit to accept/reject here; evaluation only.
    4. DECISION — Commit or leave open. [HUMAN, ASSISTED-BY: LLM, GATED]
       PURPOSE: operator owns the terminal verdict
       COGNITION: decide
       OUTPUT: selected terminal — accept | reject | open
       CONSTRAINTS: if evidence is empty or critique marks underspecified, prefer open.
```

## Notes

- Crystallised control graph; steps 2–3 remain stochastic.
- Low confidence / underspecified → plan status path `open` via `ON_UNCERTAINTY: record`,
  not silent re-planning.
- `negotiate` / `learn` / `optimize` cognitions intentionally absent (deferred).
