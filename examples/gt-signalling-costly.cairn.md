# Game theory: Costly signalling vs cheap talk

## CONTEXT

- **Sender / receiver**: Quality unknown.
- **Cost**: cheap talk vs Spence-costly.

## REQUIREMENTS

```
R1. SIGNAL COST is cheap or costly. [MUST]
R2. Cheap dashboard scores without evidence are cheap talk. [SHOULD]
```

## OUTCOMES

Separated types if costly; pooling if cheap.

## PROCESS — Formal

```
PROCESS CostlySignal (INPUT: hidden quality; OUTPUT: believed or cheap talk)
  1. GAME [STRUCTURE: sequential; KIND: signalling] of quality. [INCENTIVE]
     INFORMATION: incomplete
  2. SIGNAL [COST: costly] if only high types can bear it. [INCENTIVE]
  3. SIGNAL [COST: cheap] if the badge is free to fake. [INCENTIVE]
  4. PLAY [MOVE: signal] the message. [INCENTIVE]
  5. EQUILIBRIUM [CONCEPT: bayesian] check. [COMMON_KNOWLEDGE]
  6. EMERGENT [TYPE: game_theoretic]
```
