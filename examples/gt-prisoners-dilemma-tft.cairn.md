# Game theory: Iterated Prisoner's Dilemma and conditional cooperation

Tit-for-tat is a PLAY policy in prose, not a TIT_FOR_TAT construct.

## CONTEXT

- **Players**: Two agents in a repeated general-sum game.
- **Payoff**: T>R>P>S.

## REQUIREMENTS

```
R1. Write the matrix in PAYOFF, not as a new KIND. [MUST]
R2. TFT is PLAY cooperate then punish, inside ITERATE. [MUST]
R3. EQUILIBRIUM is a check step, not a solver. [MUST]
R4. Do not tag STRATEGIC (org). [MUST]
```

## OUTCOMES

Stable mutual defect, or conditional cooperation, or late defect under discounting.

## PROCESS — Formal

```
PROCESS IteratedPD (INPUT: pairing; OUTPUT: action path)
  1. GAME [STRUCTURE: repeated; KIND: pd] of the pairing. [INCENTIVE, COMMON_KNOWLEDGE]
     PAYOFF: T=5,R=3,P=1,S=0 so T>R>P>S
     INFORMATION: complete
  2. PLAY [MOVE: cooperate] on the first round. [RECIPROCAL]
  3. ITERATE [UNTIL: last round]
       PLAY [MOVE: punish] if the other defected last round. [INCENTIVE]
       PLAY [MOVE: cooperate] if the other cooperated. [RECIPROCAL]
  4. DISCOUNT [SHAPE: hyperbolic] [REF: now] if the shadow of the future shrinks. [HEURISTIC]
  5. EQUILIBRIUM [CONCEPT: nash] check: mutual defect is always Nash. [COMMON_KNOWLEDGE]
  6. EMERGENT [TYPE: game_theoretic]
```
