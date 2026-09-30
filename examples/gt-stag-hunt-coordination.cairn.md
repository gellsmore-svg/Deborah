# Game theory: Stag Hunt coordination and framing

## CONTEXT

- **Players**: Two hunters. Stag needs both; rabbit is safe alone.
- **Payoff**: R>T>P>S.

## REQUIREMENTS

```
R1. Both (stag,stag) and (rabbit,rabbit) are Nash. [MUST]
R2. A loss frame can make stag feel like risking a sure rabbit. [SHOULD]
R3. Do not tag STRATEGIC. [MUST]
```

## OUTCOMES

Payoff-dominant stag, risk-dominant rabbit, or a focal default.

## PROCESS — Formal

```
PROCESS StagHunt (INPUT: pairing; OUTPUT: stag or rabbit)
  1. GAME [STRUCTURE: simultaneous; KIND: stag_hunt] of the hunt. [INCENTIVE, COMMON_KNOWLEDGE]
     PAYOFF: R=5,T=4,P=2,S=0 so R>T>P>S
  2. FRAME [VALENCE: loss] [REF: rabbit-certain] if UI labels stag as risking the sure 4. [FRAMED]
  3. PLAY [MOVE: cooperate] stag, or defect rabbit. [INCENTIVE, STOCHASTIC]
  4. EQUILIBRIUM [CONCEPT: nash] check: both stag-stag and rabbit-rabbit are Nash. [COMMON_KNOWLEDGE]
  5. EQUILIBRIUM [CONCEPT: pareto] check: stag-stag dominates. [COMMON_KNOWLEDGE]
  6. EQUILIBRIUM [CONCEPT: focal] if salience picks rabbit. [COMMON_KNOWLEDGE]
  7. EMERGENT [TYPE: game_theoretic]
```
