# Behavioural economics: Default nudge (status quo)

## CONTEXT

- **Chooser**: Unset preference, low effort.
- **Architect**: Pre-selects an option.
- **Not**: a Nash label; a default is not EQUILIBRIUM.

## REQUIREMENTS

```
R1. The intervention is NUDGE [TOOL: default]. [MUST]
R2. System 1 acceptance stays STOCHASTIC. [MUST]
R3. Opt-out is DECISION, not a new OPT_OUT construct. [MUST]
```

## OUTCOMES

Default accepted, or effortful override.

## PROCESS — Formal

```
PROCESS NudgeDefault (INPUT: unset choice; OUTPUT: default accepted or overridden)
  1. NUDGE [TOOL: default] pre-selects the status-quo option. [NUDGED]
  2. DUAL_PROCESS [SYSTEM: 1] accepts unless effort is spent. [COGNITIVE, STOCHASTIC]
  3. DECISION [ON: keep default vs opt out]
  4. EMERGENT [TYPE: behavioural_economic]
```
