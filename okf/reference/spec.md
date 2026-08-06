---
type: Reference
title: Specification (SPEC.md)
description: The normative Cairn specification, v0.10 — cross-LLM framing role, PLAN envelopes and framing fields, crystallisation lifecycle, capability references, core vs descriptive constructs, three document modes, backbone and render profiles, grammar, STATE, tags, conformance, non-goals.
resource: https://github.com/gellsmore-svg/Deborah/blob/main/SPEC.md
tags: [deborah, cairn, spec, normative]
timestamp: 2026-08-06T00:00:00Z
---

# Specification — `SPEC.md` (v0.10)

The normative definition of Cairn, maintained by Deborah. Section map:

- Opening role statement — Deborah frames cross-LLM caller↔capability work
- §0 Reading guide · §1 Document structure — three modes
- §2 Design principles · §3 Shared backbone and render profiles
- §4 Core grammar (incl. PLAN §4.5–§4.6) · §5 Constructs
- §6 STATE · §7 Tags · §8 CONTEXT and CONSTRAINTS
- §9 Requirements & Outcomes · §10 Composition (signatures + CALL)
- §11 Worked example · §12 Conformance (structural)
- §13 Usage modes · §14 Authoring vs execution (crystallisation)
- §15 Capability references · §16 Core vs descriptive profiles
- §17 Non-goals · §18 Versioning

It is deliberately readable — the language is meant to fit in one document and
be used by both humans and LLMs. Formal syntax is in the [grammar](grammar.md).

## PLAN interpretation (§4.6)

A `PLAN` may be **interpreted**: walked step-by-step by a runtime that enforces
`depends_on`, `allowed_tools`, and the per-step status machine
(`pending / active / completed / blocked / skipped`). Dispatch is by construct;
execution context crosses steps through a bounded artifact map. Completing steps
is not the same as satisfying `OUTCOMES` — residual uncertainty may end the plan
`open`, and capability refusal may end it `refused`.

## Conformance surface

Machine-readable plan checks live in `deborah.conformance` (version **1.1**):
`validate_plan`, `CORE_CONSTRUCTS`, `PLAN_STATUSES` (includes `open`/`refused`),
`ON_UNCERTAINTY_POLICIES`, `is_core_construct`.
