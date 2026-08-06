---
type: Concept
title: Document modes
description: A Cairn document is built from three kinds of block kept deliberately distinct — CONTEXT (what world are we in?), REQUIREMENTS/OUTCOMES (what must be true?), and PROCESS (how does it flow?). A document may use any subset in any combination.
resource: https://github.com/gellsmore-svg/Deborah/blob/main/SPEC.md
tags: [cairn, modes, context, requirements, process]
timestamp: 2026-06-19T00:00:00Z
---

# Document modes (SPEC §1)

A Cairn document is built from three kinds of block; a document may use any subset,
in any combination:

| Mode | Answers | Shape |
|---|---|---|
| **CONTEXT** | "what world are we in?" | scene-setting, definitions, frames |
| **REQUIREMENTS / OUTCOMES** | "what must be true?" | declarative, testable assertions |
| **PROCESS** | "how does it flow?" | the numbered, imperative steps |

Keeping these distinct is deliberate: **requirements are assertions** (with
acceptance criteria), not control flow, and **scene-setting is background**, not
steps. Mixing them is what makes most design docs hard to follow.

PROCESS blocks are built from [constructs](constructs.md) and may declare
[STATE](state.md); REQUIREMENTS link to the steps that satisfy them (see
[composition](composition.md)). All three are authored on the one
[backbone](backbone-and-render-profiles.md).
