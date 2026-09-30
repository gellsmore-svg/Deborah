# HCI: Affordance and mapping

Natural vs arbitrary mapping. Signifiers fold into AFFORDANCE, not a SIGNIFIER construct.

## CONTEXT

- **Control**: A slider, button, or badge.
- **Mapping**: How control motion matches the user's model.

## REQUIREMENTS

```
R1. AFFORDANCE MAP natural or arbitrary. [MUST]
R2. Recognition-rather-than-recall is AFFORDANCE plus FORAGE, not a new construct. [SHOULD]
```

## OUTCOMES

The control is used as intended, or misused.

## PROCESS — Formal

```
PROCESS AffordanceMap (INPUT: control; OUTPUT: intended or misused act)
  1. AFFORDANCE [MAP: natural] if motion matches the user's model. [DISCOVERABLE]
     HCI_TOUCHPOINT: volume slider
  2. AFFORDANCE [MAP: arbitrary] if the same motion is inverted elsewhere. [DISCOVERABLE]
  3. FORAGE [SCENT: strong] if the label is visible. [INTERACTIVE]
  4. EMERGENT [TYPE: interactive]
```
