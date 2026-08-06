---
type: Concept
title: STATE
description: Explicitly declared state that steps read and write, with scopes that say how widely it is shared — process-local, shared across a parallel branch, or isolated — so data flow and concurrency semantics are visible rather than implied.
resource: https://github.com/gellsmore-svg/Deborah/blob/main/SPEC.md
tags: [cairn, state, scope, concurrency]
timestamp: 2026-06-19T00:00:00Z
---

# STATE (SPEC §6)

Cairn makes **data flow explicit**: a process declares `STATE` that its
[steps](constructs.md) read and write, rather than leaving variables implicit. The
scope says how widely that state is shared — process-local, **shared** across a
`PARALLEL` branch, or **isolated** per branch — so concurrency semantics are
visible on the page.

This matters where it interacts with the [constructs](constructs.md): `PARALLEL
[STATE: isolated|shared] … MERGE` declares whether branches see each other's
state and how results are merged; `ITERATE`/`QUEUE` bodies thread state across
rounds. Declared state is exposed in full by the [`ai` render profile](backbone-and-render-profiles.md)
and compressed in the operator/executive ones. Grammar: [GRAMMAR.md](../reference/grammar.md).
