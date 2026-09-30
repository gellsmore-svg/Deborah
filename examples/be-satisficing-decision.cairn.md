# Behavioural economics: Satisficing vs maximising

Simon satisficing as DECISION RULE in the same bracket as ON.
Include FRAME so HEURISTIC tag-consistency holds.

## CONTEXT

- **Chooser**: Searching a large set.
- **Rule**: satisfice (first good-enough) vs maximize (keep looking).

## REQUIREMENTS

```
R1. RULE shares the first bracket with ON. [MUST]
R2. Do not mint a SATISFICE construct. [MUST]
R3. Include a BE construct if using HEURISTIC/FRAMED/NUDGED tags. [MUST]
```

## OUTCOMES

Stop at a threshold, or keep searching with rising regret.

## PROCESS — Formal

```
PROCESS SatisficeOrMaximize (INPUT: option stream; OUTPUT: stop or continue)
  1. FRAME [VALENCE: gain] [REF: aspiration] of the next option. [HEURISTIC, FRAMED]
  2. DECISION [ON: whether to search further; RULE: satisfice] stop at first good-enough. [HUMAN]
  3. METACOGNITION [MONITOR] if the chooser is maximising instead. [METACOGNITIVE]
  4. EMERGENT [TYPE: behavioural_economic]
```
