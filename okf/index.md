---
type: Project
title: Deborah
description: A human-readable process language for framing cross-LLM work — callers, capabilities, crystallised PROCESS/PLAN documents, and governed interpretation — including technical and human-system dimensions.
resource: https://github.com/gellsmore-svg/Deborah
tags: [deborah, cairn, meta-language, process, agentic, specification]
timestamp: 2026-08-06T00:00:00Z
---

# Deborah / Cairn

**Deborah** is the package that maintains **Cairn**, a human-readable process
language for **framing how LLM callers interact with LLM-consumed capabilities**
(and how those processes sit in human systems). It is not a device for turning
stochastic model steps into pure functions: it fixes the *frame* (intent,
outcomes, capability pins, bounds, residual uncertainty) around agentic work.

The specification is [SPEC.md](https://github.com/gellsmore-svg/Deborah/blob/main/SPEC.md)
(**v0.10**). This bundle is an [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
description of its concepts and reference material.

## Map

- **[Concepts](concepts/index.md)** — document modes, backbone + render profiles,
  constructs, STATE, tags, composition, augmentation.
- **[Reference](reference/index.md)** — SPEC, GRAMMAR, examples.

## At a glance

- One **canonical backbone**, rendered to audience profiles (`ai` / `operator` /
  `executive` / `audit`) — authored once.
- Three document modes: CONTEXT, REQUIREMENTS/OUTCOMES, PROCESS.
- Versioned **PLAN** envelopes with optional framing fields (`INTENT`,
  `OUTCOMES`, `ASSUMES`, `ON_UNCERTAINTY`, …) and terminals `open` / `refused`.
- **Core** constructs for portable execution vs **descriptive** domain vocabulary.
- License: Apache-2.0. Family examples under `examples/`.
