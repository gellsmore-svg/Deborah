---
type: Concept
title: Composition & conformance
description: Processes compose via signatures and CALL; requirements/outcomes are declarative testable assertions linked to the steps that satisfy them; structural conformance defines what makes a document valid Cairn, and versioning governs how the language evolves.
resource: https://github.com/gellsmore-svg/Deborah/blob/main/SPEC.md
tags: [cairn, composition, requirements, conformance, versioning]
timestamp: 2026-06-19T00:00:00Z
---

# Composition & conformance (SPEC §9–13)

- **Composition (§10)** — a process declares a **signature** and is invoked by
  `CALL <Process>(args)`; [RECURSE](constructs.md) is a guarded self-call. This is
  how larger flows are built from smaller, named ones.
- **Requirements & outcomes (§9)** — the REQUIREMENTS/OUTCOMES
  [mode](document-modes.md) holds declarative, testable assertions with acceptance
  criteria; steps link to them (`SATISFIES: R1`), and the `audit`
  [profile](backbone-and-render-profiles.md) surfaces those links.
- **Conformance (§12)** — structural rules for what makes a document valid Cairn
  (the modes, the backbone, required vs optional blocks), independent of any tool.
- **Versioning & evolution (§13)** — how the spec changes over time; the current
  spec is **v0.8**.

Together these make a Cairn document **traceable** (requirement ↔ step) and
**composable** (process ↔ process). The precise forms are in the
[grammar](../reference/grammar.md) and demonstrated in the
[examples](../reference/examples.md).
