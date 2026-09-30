# Game theory: Public goods / free-rider

## CONTEXT

- **Players**: Many. Contribution is non-rival.
- **Interface**: Friction on defect is a nudge, not a new equilibrium concept.

## REQUIREMENTS

```
R1. Name KIND public_goods. [MUST]
R2. Friction on defect is NUDGE, still write the GAME. [SHOULD]
```

## OUTCOMES

Contribute, free-ride, or punish.

## PROCESS — Formal

```
PROCESS PublicGoods (INPUT: group; OUTPUT: contribution or free-ride)
  1. GAME [STRUCTURE: simultaneous; KIND: public_goods] of the pool. [INCENTIVE]
     PAYOFF: contribute costs, free-ride T>R
  2. NUDGE [TOOL: friction] on the defect/exit control. [NUDGED]
  3. PLAY [MOVE: defect] as free-ride, or cooperate as contribute. [INCENTIVE, STOCHASTIC]
  4. PLAY [MOVE: punish] if a sanction is available. [RECIPROCAL]
  5. EQUILIBRIUM [CONCEPT: nash] check: zero contribution without punishment. [COMMON_KNOWLEDGE]
  6. EMERGENT [TYPE: game_theoretic]
```
