# Independent reconstruction (SPEC v0.13)

A Cairn description of **several isolated stochastic reconstructions from one
persistent source**, a non-authoritative join, and later generations that see
**role-specific views** — not a winner paragraph.

This is a **process description**. Deborah does not execute isolated sampling.
`SAMPLE` and `VIEW` are extension constructs: a core-profile runtime may skip
them with a trace; a skip is not independence.

The same pattern is used by the Multipath Reasoning skill
(`gellsmore-svg/multipath-reasoning`). That skill owns the procedure. This file
does not make Deborah a Multipath runtime.

Do **not** substitute `QUEUE` (shared transcript) or `BATCH` (one step, many
like calls). Those are different processes.

## CONTEXT

- **SOURCE** — the original request, constraints, and evidence, written once
  and passed verbatim. Later summaries must not replace it.
- **Caller** — an orchestrator that spawns isolated child contexts and keeps
  the full admissibility record.
- **Paths** — independent reconstructions. They do not see siblings.

## OUTCOMES

- A best-supported answer **or** an explicit open result with remaining
  alternatives (`ON_UNCERTAINTY: record`).
- Agreement is not treated as verification.
- A claim that only survived because later paths inherited it is weaker than
  one recovered from SOURCE without being told.

## PROCESS — Formal

```
PROCESS IndependentReconstruction (INPUT: source; OUTPUT: answer_or_open)
  STATE
    source          [scope: process; dir: read]        ref: S1
    admissibility   [scope: process; dir: read/write]  ref: S2

  1. STEP — Write SOURCE verbatim. Never replace it with a later summary. [CODE, DETERMINISTIC]
     PURPOSE: keep the original problem as the drift guard
     COGNITION: observe
     OUTPUT: source.md
     CONSTRAINTS: list ambiguities that would change the answer; ask before guessing them into invariants.

  2. SAMPLE [N: 5; STATE: isolated; FROM: source] Independent reconstructions.
     PURPOSE: preserve real variation before any join
     2a. CALL Path(source) → reconstruction  [LLM, STOCHASTIC]
     2b. CALL Path(source) → reconstruction  [LLM, STOCHASTIC]
     2c. CALL Path(source) → reconstruction  [LLM, STOCHASTIC]
     2d. CALL Path(source) → reconstruction  [LLM, STOCHASTIC]
     2e. CALL Path(source) → reconstruction  [LLM, STOCHASTIC]
     CONSTRAINTS: identical SOURCE; no sibling answers; no personas-as-diversity.

  3. MERGE [RULE: admissibility] Build constraints, open alternatives, and disagreements.
     PURPOSE: pass an admissibility state, not a canonical answer
     COGNITION: evaluate
     OUTPUT: admissibility (invariants, findings, disagreements, uncertainty)
     CONSTRAINTS: do not write a winner paragraph; do not treat agreement as support.

  4. ITERATE [UNTIL: stop_test; MAX: 5] Later generations from SOURCE plus a view.
     4.1 VIEW [ROLE: blind; EXPOSE: source + hard_constraints; WITHHOLD: findings + scores + stability]
         PURPOSE: reconstructability probe — recover the claim without being told it
     4.2 VIEW [ROLE: dissent; EXPOSE: disagreements + minority_findings]
         PURPOSE: steelman alternatives; do not erase minority findings
     4.3 VIEW [ROLE: constraint; EXPOSE: source + constraints + open_questions; WITHHOLD: findings + scores]
         PURPOSE: hypothesis-test; may still name prior candidates
     4.4 VIEW [ROLE: retained; EXPOSE: findings + provenance]
         PURPOSE: carry what earned preservation
     4.5 VIEW [ROLE: full; EXPOSE: admissibility]
         PURPOSE: strongest overall reconstruction; still not a verdict
     4.6 SAMPLE [N: 5; STATE: isolated; FROM: source] New population.
         CONSTRAINTS: each branch receives SOURCE plus its VIEW; never sibling answers; never resume a prior path.
     4.7 MERGE [RULE: admissibility] Update admissibility.
         CONSTRAINTS: a claim recovered only under constraint is mixed at best; blind recovery is stronger.

  5. SAMPLE [N: 1; STATE: isolated; FROM: source] Closing blind audit.
     PURPOSE: one check not authored by the parent
     CONSTRAINTS: give only SOURCE plus the proposed answer; if it does not follow, do not claim high confidence.

  6. DECISION — Commit, leave open, or ask. [HUMAN, ASSISTED-BY: LLM, GATED]
     PURPOSE: residual uncertainty is a valid terminal
     COGNITION: decide
     OUTPUT: selected terminal — accept | open | need_external_evidence | ask
     CONSTRAINTS: if another generation would only repeat inheritance, stop and say so.
```

## Narrative (same backbone)

> Write the original problem down and keep it. Sample five isolated
> reconstructions from that source — they must not see each other. Merge into
> an admissibility state (what is allowed, what is still open), not a winner.
> Then iterate: project role-specific views, sample a new isolated population
> from the source plus each view, and merge again as admissibility. Before
> claiming a confident answer, run one last isolated check that sees only the
> source and the proposed answer. Leave the question open if alternatives still
> fit.

## How this differs from nearby constructs

| Construct | Process |
|-----------|---------|
| `SAMPLE` | Independent reconstructions from one source; no sibling answers |
| `BATCH [n]` | Many similar calls, still one step |
| `QUEUE` | Turn-taking on a shared transcript (a debate) |
| `PARALLEL … MERGE [RULE: synthesis]` | Concurrent branches whose join *is* the next ancestor |
| `MERGE [RULE: admissibility]` | Join that later samples must not inherit as the answer |
