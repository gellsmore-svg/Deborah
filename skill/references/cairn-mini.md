# Cairn mini (authoring)

Normative: `SPEC.md`, `GRAMMAR.md`. This is only a writing aid.

Fence as a `cairn` block or save `name.cairn.md`. Progressive: numbered prose
first; tags when actors/determinism matter; PLAN fields only for a walk.

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
`open` is an honest residual terminal, not a crash.

Optional PLAN policy (omit unless the walk needs them; see SPEC):
`EXPLORATION_BUDGET`, `REFLECTIVE_PASS`. Reflect is plan policy, not a
cognition.

## Skeletons

Business-process documentation (default formality):

```
CONTEXT
  Trigger, systems, roles.

REQUIREMENTS
R1. Policy invariant. [MUST]
   ACCEPTANCE: observable check.

PROCESS Name (INPUT: request; OUTPUT: record)
  1. Capture the request.
  2. Apply the policy.
  3. DECISION Approve or return. [HUMAN, GATED]
  4. Record the outcome.
```

Code as abstract logic (same language, not a programming dialect):

```
CONTEXT
  Components and stores — not import lists.

REQUIREMENTS
R1. Claim is idempotent. [MUST]
   ACCEPTANCE: a retried claim does not double-apply.

PROCESS WorkerClaim (INPUT: lease; OUTPUT: result)
  1. Claim the job. [CODE, DETERMINISTIC]
  2. CALL Run the adapter. [CODE, DETERMINISTIC]
  3. Persist the result. [CODE, DETERMINISTIC]
     STATE UPDATE: job store
  4. RETRY On failure, retry or dead-letter.
```

## Core constructs (runtime must understand)

`STEP` `CALL` `ITERATE` `DECISION` `RECURSE` `QUEUE` `PARALLEL` `MERGE`
`SERVICE` `RETRY` `AWAIT` `BREAK` `CONTINUE` `MILESTONE` `ERROR`

Plain numbered lines are STEP. After the number, an optional CORE name as a
bare word (do not wrap it in `[ ]` — brackets are for tags), then prose:

`1. DECISION Approve. [HUMAN, GATED]`

`BREAK` and `CONTINUE` stand on their own line, not in the step-id slot.
Do not inline another process’s graph — `CALL` / `SERVICE` it.

## Extension constructs (docs; core walker may skip)

Psych/org/socio: `REGULATION` `APPRAISAL` `DUAL_PROCESS` `METACOGNITION`
`AVOIDANCE` `HABIT` `ATTENTION` `INTERPERSONAL`
`ALIGN` `COALITION` `RESISTANCE` `REINFORCEMENT` `CASCADE` `VISION`
`SOCIALIZE` `INSTITUTIONALIZE` `SYMBOLIC_INTERACTION` `CONFLICT`
`ACCOMMODATE` `ASSIMILATE` `ROLE` `FEEDBACK` `MACRO`

Behavioural economics: `FRAME` `NUDGE` `ACCOUNT` `DISCOUNT`
(`DECISION [ON: …; RULE: satisfice|maximize]` — same first bracket as ON).

Game theory: `GAME` `PLAY` `EQUILIBRIUM` `SIGNAL` (do not tag `STRATEGIC`).

HCI: `CHOICE` `GULF` `AFFORDANCE` `FORAGE`. Hick `CHOICE [SET:]` is not
“fewer is always faster”; visual search is `FORAGE`.

Isolated reconstruction: `SAMPLE` (needs `N` or `MAX`), `VIEW` (needs
`ROLE`, `EXPOSE`, or `WITHHOLD`), `MERGE [RULE: admissibility|winner|vote|synthesis|none]`.

`SAMPLE` is not debate and not a batch loop. Debate / turn-taking uses
`QUEUE` (see `examples/round-robin-debate.cairn.md`). Fan-out/join uses
`PARALLEL` then `MERGE`.

## Do not write

- Invented constructs or tags (no DSM/ICD diagnosis names as constructs)
- `DECISION [ON: x] [RULE: satisfice]` — RULE must share the first `[ON: …]` bracket
- `GAME_THEORY:` — use `GAME`/`PLAY`/`EQUILIBRIUM`/`SIGNAL`
- `CONCURRENT` → use `PARALLEL`
- `BATCH` → `ITERATE` / `QUEUE`, or `SAMPLE` for isolated reconstructions
- A programming dialect (types, functions, source order)
- Family product names as constructs (Huldah, Keturah, Galeed, Multipath)

## Common tags

`HUMAN` `LLM` `CODE` `ASSISTED-BY` · `DETERMINISTIC` `STOCHASTIC` ·
`SYNC` `ASYNC` · `GATED` · `TOOL` · `[SATISFIES: R1]`

## COGNITION (optional product contract)

First token only: `observe` | `infer` | `evaluate` | `decide` |
`negotiate` | `learn` | `optimize`.

Omit COGNITION when the step is ordinary prose. `decide` → construct
`DECISION`. Empty-observe / learn / optimize must-nots: SKILL.

## Useful annotations

`PURPOSE:` `OUTPUT:` `CONSTRAINTS:` `STATE UPDATE:` `RISKS:`
`HUMAN_DEMAND:` `HUMAN_FACTORS:` `SUPPORT:` `FAILURE_MODE:`
`CONDITION_MAP:` (pointer, not a diagnosis) `BIAS:` `PAYOFF:` `INFORMATION:`
`CHOICE_COMPLEXITY:` `HCI_TOUCHPOINT:`

STATE is for durable/shared data (`scope: process|session|global`, `dir:`).

## Patterns (CORE only)

```
  1. PARALLEL Do A and B.
  2. MERGE Combine.

  1. DECISION Approve. [HUMAN, GATED]

  1. CALL Hand off.
  1. AWAIT Wait for a worker.
  1. QUEUE Enqueue.
  1. RETRY Retry a failed attempt.
  1. ERROR Dead-letter.
```

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
deborah-validate FILE.cairn.md --strict           # non-zero exit; force profile strict
deborah-validate FILE.cairn.md --profile core     # reject extension constructs
deborah-validate FILE.cairn.md --profile strict --export-plan
```
