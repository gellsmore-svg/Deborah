# Game theory: Ultimatum and reciprocity (behavioural GT)

Camerer: offers ~40%, reject below ~20%. Not a diagnosis. INTERPERSONAL rank/validation
drives rejection; tag RECIPROCAL not STRATEGIC.

## CONTEXT

- **Proposer / responder**: Divide a pie; responder can reject both to zero.

## REQUIREMENTS

```
R1. Rejection is PLAY punish plus INTERPERSONAL, not irrational noise. [MUST]
R2. Do not tag STRATEGIC. [MUST]
```

## OUTCOMES

Near-equal split accepted, or a low offer rejected.

## PROCESS — Formal

```
PROCESS UltimatumReciprocity (INPUT: pie; OUTPUT: accepted split or zero)
  1. GAME [STRUCTURE: sequential; KIND: bargaining] of the ultimatum. [INCENTIVE, RECIPROCAL]
     PAYOFF: accept (pie-x, x) or reject (0,0)
  2. INTERPERSONAL [PATTERN: rank] of unfairness. [INTERPERSONAL]
  3. PLAY [MOVE: cooperate] typical offer near 40 percent. [RECIPROCAL]
  4. PLAY [MOVE: punish] if offer is below about 20 percent. [RECIPROCAL]
  5. EQUILIBRIUM [CONCEPT: nash] check: selfish subgame-perfect is near-zero offer. [COMMON_KNOWLEDGE]
  6. EMERGENT [TYPE: game_theoretic]
```
