# HCI: Choice architecture (progressive disclosure / defaults)

If the step describes the UI, use CHOICE; if it is the intervention, use NUDGE.
This file names the UI.

## CONTEXT

- **Screen**: Many options, some hidden behind progressive disclosure.
- **Default**: A pre-selected value.

## REQUIREMENTS

```
R1. CHOICE declares SET or ARCHITECTURE. [MUST]
R2. Hick SET is cardinality, not fewer-is-always-faster. [MUST]
```

## OUTCOMES

A path through the set, or opt-out.

## PROCESS — Formal

```
PROCESS ChoiceArchitecture (INPUT: option set; OUTPUT: selected or deferred)
  1. CHOICE [SET: 24] [ARCHITECTURE: progressive] of settings. [INTERACTIVE]
     HCI_TOUCHPOINT: settings page
  2. NUDGE [TOOL: default] of the recommended path. [NUDGED]
  3. DECISION [ON: pick, drill down, or leave]
  4. EMERGENT [TYPE: interactive]
```
