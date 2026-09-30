# Behavioural economics: Prospect theory framing

Kahneman & Tversky 1979: reference dependence and gain/loss framing.
Descriptive process, not a bias inventory dialect.

## CONTEXT

- **Chooser**: Evaluating an outcome relative to a reference.
- **Frame**: Gain vs loss wording of the same objective outcome.
- **Not**: a new WEIGHT construct for probability weighting (use BIAS:).

## REQUIREMENTS

```
R1. Name VALENCE and REF on FRAME. [MUST]
R2. Loss frames sit on or before System 1. [SHOULD]
R3. Do not treat System 2 as cancelling bias deterministically. [MUST]
```

## OUTCOMES

A choice that depends on the displayed frame, not only on final wealth.

## PROCESS — Formal

```
PROCESS FrameProspect (INPUT: outcome pair; OUTPUT: framed choice)
  1. FRAME [VALENCE: loss] [REF: status quo] of the reminder. [FRAMED, HEURISTIC]
     BIAS: loss_aversion
  2. DUAL_PROCESS [SYSTEM: 1] accepts the loss-shaped option. [COGNITIVE, STOCHASTIC]
  3. DUAL_PROCESS [SYSTEM: 2] may re-appraise if time and load allow. [COGNITIVE, STOCHASTIC]
  4. DECISION [ON: which framed option]
  5. EMERGENT [TYPE: behavioural_economic]
```
