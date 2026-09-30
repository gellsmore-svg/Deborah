# HCI: Gulf of evaluation

Norman: gap between system state and what the user can read.

## CONTEXT

- **User**: Has acted; cannot tell if it worked.
- **System**: Weak feedback.

## REQUIREMENTS

```
R1. GULF KIND evaluation. [MUST]
R2. Threat appraisal of unread state is APPRAISAL after the gulf, not instead of it. [SHOULD]
```

## OUTCOMES

State understood, or false threat / false success.

## PROCESS — Formal

```
PROCESS GulfEvaluation (INPUT: after action; OUTPUT: understood or misread state)
  1. GULF [KIND: evaluation] of silent success. [INTERACTIVE]
     HCI_TOUCHPOINT: save with no confirmation
     HUMAN_DEMAND:
       CLOSE: know the work is done
  2. APPRAISAL [TYPE: primary] of missing feedback as threat. [APPRAISAL]
  3. DECISION [ON: retry, wait, or escalate]
  4. EMERGENT [TYPE: interactive]
```
