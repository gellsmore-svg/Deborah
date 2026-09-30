# Proposal: Four-area process language (psych, BE, GT, HCI)

**Date:** 2026-08-25
**Status:** Implemented (SPEC v0.14 / conformance 1.6 / package 0.26.0)
**Method:** Recursive confidence loop run-1a5df5b9 (STABILIZED). Score stability is not verification.

## Gap

Shipped psych EXTENSION (`REGULATION`, `APPRAISAL`, `DUAL_PROCESS`, `METACOGNITION`)
could not name avoidance, habit, attention-as-process, or interpersonal process.
Behavioural economics, game theory, and HCI (including complexity of choice) had
no first-class verbs. Informal `GAME_THEORY:` / `HCI_TOUCHPOINT:` drifted in
examples without parser support.

Encoding every DSM-5-TR / ICD-11 condition as a construct would violate SPEC §2
(least abstraction, human-first, evolve from use). Coverage of recognised
conditions is a **mapping**, not a dialect.

## Freeze

Additive **four EXTENSION verbs per area** (psych keeps its four and adds four).
Inventories live in `examples/mappings/*-map.md`.

| Area | Add | Tags | Annotations |
|---|---|---|---|
| Psych | AVOIDANCE, HABIT, ATTENTION, INTERPERSONAL | TRANSDIAGNOSTIC, INTERPERSONAL, AVOIDANT | CONDITION_MAP |
| BE | FRAME, NUDGE, ACCOUNT, DISCOUNT | HEURISTIC, FRAMED, NUDGED | BIAS |
| GT | GAME, PLAY, EQUILIBRIUM, SIGNAL | INCENTIVE, COMMON_KNOWLEDGE, RECIPROCAL | PAYOFF, INFORMATION |
| HCI | CHOICE, GULF, AFFORDANCE, FORAGE | INTERACTIVE, OVERLOAD, DISCOVERABLE | CHOICE_COMPLEXITY, HCI_TOUCHPOINT |

CORE modifier only: `DECISION [ON: …; RULE: satisfice | maximize]` in the **same
first bracket**. Runtime ignores RULE.

Rejected: SATISFICE construct, DEFENSE, TOUCHPOINT construct, CLINICAL,
STRATEGIC as a GT tag, LOAD_TYPE, diagnosis names, GAME_THEORY as parser
annotation, new render profiles, interpreter behaviour.

## Equal depth

7 new PROCESS examples per new area + 4 psych + 2 cross. Mapping docs cover
DSM-5-TR chapters, ICD-11 Ch.06, HiTOP/RDoC, BE inventories, GT axes, HCI
laws/heuristics. No new profiles (`therapeutic` / `human_factors` notes extended).

## Interactions

See SPEC disambiguation (HABIT ≠ org REINFORCEMENT ≠ NUDGE incentive ≠ PAYOFF)
and `examples/cross-avoidance-loss-choice-trust.cairn.md` /
`examples/cross-habit-nudge-forage.cairn.md`.
