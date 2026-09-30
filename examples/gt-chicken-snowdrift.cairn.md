# Game theory: Chicken / snowdrift

## CONTEXT

- **Players**: Two, each prefers the other to swerve/contribute.
- **Payoff**: T>R>S>P.

## REQUIREMENTS

```
R1. KIND chicken covers snowdrift/hawk-dove. [MUST]
R2. Mixed equilibrium is EQUILIBRIUM CONCEPT mixed. [SHOULD]
```

## OUTCOMES

One swerves, both crash, or a mixed pattern.

## PROCESS — Formal

```
PROCESS ChickenSnowdrift (INPUT: pairing; OUTPUT: swerve or hold)
  1. GAME [STRUCTURE: simultaneous; KIND: chicken] of the contest. [INCENTIVE]
     PAYOFF: T>R>S>P
  2. PLAY [MOVE: mix] if no pure convention. [INCENTIVE, STOCHASTIC]
  3. EQUILIBRIUM [CONCEPT: mixed] check. [COMMON_KNOWLEDGE]
  4. EMERGENT [TYPE: game_theoretic]
```
