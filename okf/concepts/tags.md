---
type: Concept
title: Tags
description: Orthogonal execution dimensions attached to a step in square brackets — e.g. who acts (LLM/HUMAN/SYSTEM), determinism (DETERMINISTIC/STOCHASTIC), and timing (SYNC/ASYNC) — so the same backbone carries machine-relevant detail without changing the prose.
resource: https://github.com/gellsmore-svg/Deborah/blob/main/SPEC.md
tags: [cairn, tags, execution, dimensions]
timestamp: 2026-06-19T00:00:00Z
---

# Tags (SPEC §7)

Tags are **orthogonal dimensions** attached to a [step](constructs.md) in square
brackets, e.g. `[LLM, STOCHASTIC, SYNC]`. They annotate *how* a step executes
without changing the narrative:

- **Actor** — who performs it (e.g. `LLM`, `HUMAN`, `SYSTEM`).
- **Determinism** — `DETERMINISTIC` vs `STOCHASTIC` (an LLM step is typically
  stochastic).
- **Timing** — `SYNC` vs `ASYNC`.

**Domain extensions** (see proposals):
- Psychological: `EMOTIONAL`, `COGNITIVE`, `APPRAISAL`, `REGULATION`, `MOTIVATIONAL`, `METACOGNITIVE`, `BEHAVIORAL`
- Organisational: `LEADERSHIP`, `STRATEGIC`, `CULTURAL`, `POWER`, `STAKEHOLDER`, `STRUCTURAL`, `ALIGNMENT`, `RESISTANCE`
- Sociological: `SOCIAL`, `GROUP`, `NORM`, `ROLE`, `SYMBOLIC`

Because the dimensions are independent, a step can carry several at once. Tags are
exposed in full by the [`ai` profile](backbone-and-render-profiles.md) and the
`audit` profile (alongside requirement links), and compressed away in the
`operator` / `executive` profiles. They sit beside `CONTEXT` and `CONSTRAINTS`
sub-blocks (SPEC §8) on a step. See the [worked examples](../reference/examples.md)
for tagged steps in practice.
