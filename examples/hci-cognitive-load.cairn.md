# HCI: Cognitive load (Sweller types in HUMAN_LOAD)

Do not mint LOAD_TYPE as an annotation. Write intrinsic / extraneous / germane
inside HUMAN_LOAD. Cowan ~4 chunks.

## CONTEXT

- **User**: Working-memory budget of about four chunks.
- **Screen**: Split attention between legend and chart.

## REQUIREMENTS

```
R1. Sweller types live in HUMAN_LOAD prose. [MUST]
R2. Include an HCI construct if using OVERLOAD. [MUST]
```

## OUTCOMES

Task completed within budget, or overload.

## PROCESS — Formal

```
PROCESS CognitiveLoadBudget (INPUT: chart plus legend; OUTPUT: understood or overloaded)
  1. CHOICE [SET: 12] of legend items. [OVERLOAD, INTERACTIVE]
     HUMAN_LOAD: extraneous — split attention between legend and chart
     HCI_TOUCHPOINT: dashboard
  2. ATTENTION [MODE: shift] between chart and legend. [COGNITIVE]
  3. GULF [KIND: evaluation] if the two sources do not bind. [INTERACTIVE]
  4. EMERGENT [TYPE: interactive]
```
