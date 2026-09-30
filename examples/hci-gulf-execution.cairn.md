# HCI: Gulf of execution

Norman: gap between intention and available actions.

## CONTEXT

- **User**: Knows the goal, not the control.
- **System**: Actions poorly signified.

## REQUIREMENTS

```
R1. GULF KIND execution. [MUST]
R2. HUMAN_DEMAND ORIENT/ACT names the demand; GULF names the interface gap. [MUST]
```

## OUTCOMES

The user finds an action, or stalls.

## PROCESS — Formal

```
PROCESS GulfExecution (INPUT: user goal; OUTPUT: action found or stalled)
  1. GULF [KIND: execution] between intention and visible actions. [INTERACTIVE, DISCOVERABLE]
     HCI_TOUCHPOINT: unlabeled toolbar
     HUMAN_DEMAND:
       ORIENT: notice what can be done
       ACT: issue the command
  2. AFFORDANCE [MAP: arbitrary] of hidden gestures. [DISCOVERABLE]
  3. DECISION [ON: guess, search, or abandon]
  4. EMERGENT [TYPE: interactive]
```
