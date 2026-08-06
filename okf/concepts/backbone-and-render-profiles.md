---
type: Concept
title: Backbone & render profiles
description: Every Cairn description has one canonical backbone, projected to audience-specific render profiles (ai, operator, executive, audit) by rules for what to expose and compress. You author the backbone once; the ai projection is authoritative when profiles disagree.
resource: https://github.com/gellsmore-svg/Deborah/blob/main/SPEC.md
tags: [cairn, backbone, render-profiles, ai, operator]
timestamp: 2026-06-19T00:00:00Z
---

# Backbone & render profiles (SPEC §3)

Every Cairn description has **one canonical backbone**. A **render profile**
projects that backbone for an audience, with rules for what to **expose**, what to
**compress**, and how to phrase it. You author the backbone once; a tool or AI
renders the profile — you never hand-maintain parallel versions.

The standard profiles:

| Profile | For | Exposes | Compresses |
|---|---|---|---|
| **`ai`** | machines / execution | everything: every step, modifier, tag, state | nothing |
| **`operator`** | the person running it | intent, ownership, decisions, iteration, milestones, outputs | internal calls, mechanical sub-steps |
| **`executive`** | oversight | purpose, milestones, outcomes | almost all mechanism |
| **`audit`** | traceability | steps + requirement/tag links | prose |

`ai` and `operator` are the **canonical pair** (the precise form and the readable
form); `executive` and `audit` are further projections. Select one with
`render-profile: operator`. Profiles other than `ai` are **lossy by design** —
when they seem to disagree, **the `ai` projection wins**. The backbone is composed
of [constructs](constructs.md), [STATE](state.md), and [tags](tags.md); the same
backbone underlies all three [document modes](document-modes.md).
