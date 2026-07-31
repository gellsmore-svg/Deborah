---
type: Project
title: Deborah
description: A human-readable process language for governed agentic work in human systems, giving humans and AI systems a shared way to describe, plan, interpret, and review technical, psychological, organisational, and sociological processes.
resource: https://github.com/gellsmore-svg/Deborah
tags: [deborah, meta-language, process, agentic, specification]
timestamp: 2026-06-19T00:00:00Z
---

# Cairn

Cairn is a human-readable **process language for governed agentic work in human
systems**. It gives humans and AI systems a shared way to describe, plan,
interpret, and review complex work across technical, psychological,
organisational, and sociological dimensions, bridging pseudocode-style clarity
with modern agentic realities: iteration, recursion, non-determinism, sync/async,
queuing, outcome review, error handling, and human context.

The specification is [SPEC.md](https://github.com/gellsmore-svg/Cairn/blob/main/SPEC.md)
(v0.8); this bundle is an [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
description of its concepts and reference material.

## Map

- **[Concepts](concepts/index.md)** — the language ideas: the three document
  modes, the shared backbone + render profiles, the process constructs, STATE,
  tags, and composition.
- **[Reference](reference/index.md)** — the concrete artifacts: the spec, the
  grammar, and the worked examples.

## At a glance

- One **canonical backbone**, rendered to audience [profiles](concepts/backbone-and-render-profiles.md)
  (`ai` / `operator` / `executive` / `audit`) — authored once, not maintained in
  parallel.
- Three [document modes](concepts/document-modes.md): CONTEXT, REQUIREMENTS/OUTCOMES,
  PROCESS.
- A small set of [constructs](concepts/constructs.md) for real control flow,
  plus domain vocabularies for human-system awareness.
- An [augmentation process](concepts/augmentation-process.md) lens for
  human-AI collaboration, cognitive-state adaptation, complementarity, trust
  calibration, and bias dynamics.
- License: Apache-2.0. Used across the family — see the
  [examples](reference/examples.md) (Tirzah, Hoglah, Mahalath).
