# Behavioural economics: Anchoring heuristic

Tversky & Kahneman anchoring-and-adjustment. Bias name lives in BIAS:, not a construct.

## CONTEXT

- **Judge**: Estimating a number.
- **Anchor**: First number seen.

## REQUIREMENTS

```
R1. Name the bias in BIAS: annotation. [MUST]
R2. Do not mint an ANCHOR construct. [MUST]
```

## OUTCOMES

Estimate insufficiently adjusted from the anchor.

## PROCESS — Formal

```
PROCESS AnchorAdjust (INPUT: first number; OUTPUT: estimate)
  1. FRAME [VALENCE: gain] [REF: the first number] of the estimate. [HEURISTIC, FRAMED]
     BIAS: anchoring
  2. DUAL_PROCESS [SYSTEM: 1] starts at the anchor. [COGNITIVE, STOCHASTIC]
  3. DECISION [ON: adjusted value]
  4. EMERGENT [TYPE: behavioural_economic]
```
