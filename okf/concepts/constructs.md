---
type: Concept
title: Process constructs
description: The vocabulary of PROCESS blocks — PROCESS, STEP, PURPOSE, MILESTONE, ITERATE (with BREAK/CONTINUE), RECURSE, QUEUE, PARALLEL…MERGE, SERVICE, DECISION, RETRY, ERROR, AWAIT, and CALL — covering iteration, recursion, concurrency, queuing, decisions, and error handling.
resource: https://github.com/gellsmore-svg/Deborah/blob/main/SPEC.md
tags: [cairn, constructs, control-flow]
timestamp: 2026-06-19T00:00:00Z
---

# Process constructs (SPEC §5)

The constructs that build a PROCESS ([document mode](document-modes.md)):

- **PROCESS** — a named, numbered flow. **STEP** — one numbered action. **PURPOSE**
  — a one-line statement of *intent* on a process/milestone/step. **MILESTONE** — a
  meaningful checkpoint (top-level steps may be implicit milestones).
- **ITERATE** `[UNTIL; MAX]` — a loop; **BREAK** / **CONTINUE** `[IF]` are its
  loop control (preferred over a DECISION whose only job is to exit).
- **RECURSE** `[BASE; MAX_DEPTH]` — a self-`CALL` with guards (recursion *is* a
  self-call; don't write both).
- **QUEUE** `[ORDER: FIFO|PRIORITY|ROUND_ROBIN; ONE_AT_A_TIME]` — ordered work.
- **PARALLEL … MERGE** `[STATE: isolated|shared]` — concurrency that **joins**.
  **SERVICE** — concurrency that **never joins** (a long-running consumer/ingester);
  run a set with `CONCURRENT { … }`.
- **DECISION** — a branch. **RETRY** — bounded re-attempt. **ERROR** — a failure
  path. **AWAIT** — wait on an external event/result.
- **CALL** — invoke another process by [signature](composition.md).

**Domain extensions (see proposals):**
- Psychological: `REGULATION`, `APPRAISAL`, `DUAL_PROCESS`, `METACOGNITION`, `FEEDBACK`
- Organisational: `ALIGN`, `COALITION`, `RESISTANCE`, `REINFORCEMENT`, `CASCADE`, `VISION`
- Sociological: `SOCIALIZE`, `INSTITUTIONALIZE`, `SYMBOLIC_INTERACTION`, `CONFLICT`, `ACCOMMODATE`, `ASSIMILATE`, `ROLE`

New: `FEEDBACK` for loops in human systems.

Steps carry [tags](tags.md) and may read/write [STATE](state.md). The full grammar
is in [GRAMMAR.md](../reference/grammar.md); see [worked examples](../reference/examples.md).
