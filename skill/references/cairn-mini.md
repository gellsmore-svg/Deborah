# Cairn mini (authoring)

Normative: `SPEC.md`, `GRAMMAR.md`. This is only a writing aid.

## Document modes (any mix)

```
CONTEXT
…scene, terms, components…

REQUIREMENTS
R1. Assertion. [MUST]
   ACCEPTANCE: how we would know.

OUTCOMES
…what done well enough looks like…

PROCESS Name (INPUT: x; OUTPUT: y)
  1. Do the first thing.
  2. Do the next thing. [LLM, STOCHASTIC]
     PURPOSE: why this step exists
     CONSTRAINTS: bounds
     OUTPUT: artefact name
```

PLAN (crystallised walk — extra fields on top of a PROCESS):

```
PLAN Name REVISION 1 [STATUS: draft]
  REQUEST: …
  TRIGGER: …
  INTENT: …
  ON_UNCERTAINTY: record
  ASSUMES: capability@1.0
  OUTCOMES:
    - …
  REEVALUATE_WHEN:
    - …
  PROCESS …
```

Statuses: `draft` | `active` | `stable` | `complete` | `blocked` | `open` | `refused`.
`ON_UNCERTAINTY`: `record` | `escalate` | `abort`.

## Core constructs (runtime must understand)

`STEP` `CALL` `ITERATE` `DECISION` `RECURSE` `QUEUE` `PARALLEL` `MERGE`
`SERVICE` `RETRY` `AWAIT` `BREAK` `CONTINUE` `MILESTONE` `ERROR`

## Extension constructs (docs; core walker may skip)

Psych/org/socio: `REGULATION` `APPRAISAL` `DUAL_PROCESS` `METACOGNITION`
`ALIGN` `COALITION` `RESISTANCE` `REINFORCEMENT` `CASCADE` `VISION`
`SOCIALIZE` `INSTITUTIONALIZE` `SYMBOLIC_INTERACTION` `CONFLICT`
`ACCOMMODATE` `ASSIMILATE` `ROLE` `FEEDBACK` `MACRO`

Isolated reconstruction: `SAMPLE` (needs `N` or `MAX`), `VIEW` (needs
`ROLE`, `EXPOSE`, or `WITHHOLD`), `MERGE [RULE: admissibility|winner|vote|synthesis|none]`.

## Common tags

`HUMAN` `LLM` `CODE` `ASSISTED-BY` · `DETERMINISTIC` `STOCHASTIC` ·
`SYNC` `ASYNC` · `GATED` · `TOOL` · `[SATISFIES: R1]`

## COGNITION (optional product contract)

First token only: `observe` | `infer` | `evaluate` | `decide` |
`negotiate` | `learn` | `optimize`.

Omit COGNITION when the step is ordinary prose. `decide` → construct
`DECISION`. Reflect is plan policy `REFLECTIVE_PASS`, not a cognition.

## Useful annotations

`PURPOSE:` `OUTPUT:` `CONSTRAINTS:` `STATE UPDATE:` `RISKS:`
`HUMAN_DEMAND:` `HUMAN_FACTORS:` `SUPPORT:` `FAILURE_MODE:`

## Code → Cairn (abstract logic)

1. Name the process after the behaviour, not the file.
2. CONTEXT: modules, stores, other services — not import lists.
3. REQUIREMENTS: invariants you could test (idempotency, terminals, bounds).
4. Steps follow **control flow and durability**, not source order.
5. Tag `[CODE, DETERMINISTIC]` for ordinary functions; `[LLM, STOCHASTIC]`
   only where a model is actually invoked.
6. STATE for durable/shared data (`scope: process|session|global`, `dir:`).
7. CALL/SERVICE for another process; do not inline its entire graph.
8. ERROR/RETRY only for paths the code really has.

## Validate

```bash
deborah-validate FILE.cairn.md --strict
deborah-validate FILE.cairn.md --profile core    # reject extension constructs
deborah-validate FILE.cairn.md --profile strict --export-plan
```
