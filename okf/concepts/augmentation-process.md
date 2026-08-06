---
type: Concept
title: Augmentation process
description: A Cairn lens for human-AI augmentation, cognitive-state awareness, adaptation, complementarity, trust calibration, and bias dynamics in collaborative workflows.
resource: https://github.com/gellsmore-svg/Deborah/blob/main/SPEC.md
tags: [cairn, augmentation, human-ai, trust, cognitive-state, adaptation]
timestamp: 2026-07-09T00:00:00Z
---

# Augmentation process

An augmentation process is a human-AI workflow where the goal is not simply
automation, but a better combined human-system capability. The lens asks whether
the AI role, interface, feedback, and organisational setting actually extend
human capacity, or merely move cognitive work into a less visible place.

Use this concept alongside [Human factors semantics](human-factors.md),
[HCI touchpoints](hci-touchpoints.md), and
[Functional layout load](functional-layout-load.md).

## Cognitive State And Adaptation

**Meaning:** how the process senses, infers, or responds to human workload,
attention, uncertainty, fatigue, or confidence.

**Common factors:** cognitive-state visibility, workload detection, adaptation
trigger quality, loop closure, human override, state drift.

**Cairn cues:** `ADAPT`, `HUMAN_LOAD`, cognitive-state signal, workload gauge,
dynamic interface, model changes output when the person is overloaded, hidden
adaptation, adaptation without explanation.

**Mitigations:** surface why adaptation happened, keep human override visible,
validate workload signals before acting on them, log adaptation triggers, close
the loop by showing whether adaptation helped.

**Research backing:** DARPA Augmented Cognition TIE evaluated cognitive-state
gauges in a complex decision task; shared mental model work in human-agent teams
frames agents as maintaining task, role, and workload models for coordination.

## Augmentation Dynamics And Complementarity

**Meaning:** whether the AI and human roles fit together well enough to produce
better work than either alone.

**Common factors:** role complementarity, AI role clarity, user trait fit,
thriving predictors, deskilling or upskilling, symbiosis conditions, enabling
practice.

**Cairn cues:** `[ASSISTED-BY: LLM]`, human reviewer signs off on AI work,
unclear division of labour, AI handles easy work and leaves hard ambiguity,
different users need different levels of support.

**Mitigations:** name the human role and AI role separately, tune augmentation
level by expertise and context, preserve inspectability, onboard the new joint
skill, track longitudinal outcomes and workarounds.

**Research backing:** workplace HAI augmentation reviews emphasise fragmented
evidence and the need for behavioural and longitudinal study; recent lab work on
who thrives with AI highlights individual differences; Cyborg Psychology frames
human-AI systems as reciprocal cognitive and behavioural influence.

## HAI Bias And Trust Calibration

**Meaning:** whether the process helps people rely on AI appropriately, neither
rubber-stamping nor reflexively rejecting useful support.

**Common factors:** automation bias, under-reliance, explanation over-trust,
false precision, authority effect, accountability gap, strategic delegation.

**Cairn cues:** AI recommendation appears before evidence, uncertainty hidden,
accept path is easier than inspect or reject, explanation looks authoritative
but cannot be verified, human accountable for an AI-shaped decision.

**Mitigations:** show evidence and uncertainty at the decision point, make
inspect/reject/defer legitimate and low effort, separate confidence from
authority, record override reasons without punishing escalation, design
explanations to support verification rather than persuasion.

**Research backing:** experimental-economics trust work frames AI trust as
calibrated reliance under informational and institutional constraints;
automation-bias reviews warn that explanations can increase acceptance without
improving decision accuracy.

## Interaction Pattern Richness

**Meaning:** whether the human-AI interaction is a one-way recommendation or a
richer collaboration with critique, question asking, correction, and adaptation.

**Common factors:** human initiation, AI initiation, iterative critique,
bidirectional adaptation, contestability, shared task state.

**Cairn cues:** single AI answer, no chance to ask why, no correction path, no
memory of human disagreement, hidden model update, no shared view of task state.

**Mitigations:** support ask-why, compare alternatives, challenge, revise,
escalate, and remember human corrections; expose interaction state and handoff.

**Research backing:** systematic reviews of AI-assisted decision making find
many systems still use simplistic interaction patterns, with limited support for
genuine collaboration.

## Qualitative Risk

Use the same `HUMAN_RISK:` scale as `human-factors.md`. Prioritise augmentation
risk when:

- the decision is high consequence,
- the AI recommendation is fluent but weakly evidenced,
- adaptation changes what the human sees or does,
- the human is accountable without full inspectability,
- repeated use may change skill, role, trust, or escalation norms.

## Agent Conversation Starters

- What is being augmented: attention, memory, judgement, speed, coordination, or
  confidence?
- Which cognitive-state signals are visible, inferred, or absent?
- How does the person know the AI adapted, and can they override it?
- Is human-AI role complementarity explicit and reviewed over time?
- Where could automation bias, under-reliance, or explanation over-trust arise?
- Is the interaction pattern one-way assistance or genuine collaboration?
- What happens to skill, authority, and accountability after repeated use?

## Research References

- St. John et al., "Overview of the DARPA Augmented Cognition Technical
  Integration Experiment"; see the
  [Semantic Scholar record](https://www.semanticscholar.org/paper/Overview-of-the-DARPA-Augmented-Cognition-Technical-John-Kobus/98228d1f499802a2106d1e48716d4e810414f243)
  and DARPA AugCog TIE reports.
- Nguyen and Elbanna, 2025,
  [Understanding Human-AI Augmentation in the Workplace](https://link.springer.com/article/10.1007/s10796-025-10591-5).
- Gomez et al., 2025,
  [Human-AI collaboration is not very collaborative yet](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2024.1521066/full).
- Irlenbusch et al., 2026,
  [Human Trust in AI: Evidence from Experimental Economics](https://ideas.repec.org/p/ajk/ajkdps/417.html).
- Romeo and Conti, 2025,
  [Exploring automation bias in human-AI collaboration](https://link.springer.com/article/10.1007/s00146-025-02422-7).
- Scheutz, DeLoach, and Adams, 2017,
  [A framework for developing and using shared mental models in human-agent teams](https://hrilab.tufts.edu/publications/scheutzetal17smm.pdf).
