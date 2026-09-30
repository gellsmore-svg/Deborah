# Behavioural economics: Present bias / hyperbolic discounting

## CONTEXT

- **Person**: Values now more steeply than later.
- **Not**: mental accounting.

## REQUIREMENTS

```
R1. DISCOUNT names SHAPE and REF. [MUST]
R2. Do not pack this into ACCOUNT KIND temporal. [MUST]
```

## OUTCOMES

Choose the smaller-sooner option, or commit later-self if a nudge is present.

## PROCESS — Formal

```
PROCESS PresentBias (INPUT: now vs later pair; OUTPUT: chosen time)
  1. DISCOUNT [SHAPE: hyperbolic] [REF: now] of later rewards. [HEURISTIC]
  2. DECISION [ON: smaller-sooner vs larger-later]
  3. NUDGE [TOOL: commitment] if a lock-in is offered. [NUDGED]
  4. EMERGENT [TYPE: behavioural_economic]
```
