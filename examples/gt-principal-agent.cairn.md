# Game theory: Principal–agent / mechanism design

## CONTEXT

- **Principal**: Designs incentives; cannot see effort.
- **Agent**: Chooses hidden effort.

## REQUIREMENTS

```
R1. KIND principal_agent. [MUST]
R2. Incentive-compatible design is still GAME plus NUDGE/PAYOFF, not a MECHANISM construct. [MUST]
```

## OUTCOMES

Aligned effort, or moral hazard.

## PROCESS — Formal

```
PROCESS PrincipalAgent (INPUT: hidden effort; OUTPUT: aligned or shirk)
  1. GAME [STRUCTURE: sequential; KIND: principal_agent] of the contract. [INCENTIVE]
     INFORMATION: incomplete
     PAYOFF: agent cost of effort vs principal surplus
  2. NUDGE [TOOL: incentive] of the contract terms. [NUDGED]
  3. PLAY [MOVE: cooperate] effort, or defect shirk. [INCENTIVE, STOCHASTIC]
  4. SIGNAL [COST: costly] if verification is expensive. [INCENTIVE]
  5. EQUILIBRIUM [CONCEPT: bayesian] check. [COMMON_KNOWLEDGE]
  6. EMERGENT [TYPE: game_theoretic]
```
