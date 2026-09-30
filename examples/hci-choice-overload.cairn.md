# HCI: Choice overload (Iyengar/Schwartz + Hick caveat)

Iyengar & Lepper 2000 jam study; Schwartz paradox of choice; Scheibehenne 2010
mean effect near zero — overload is conditional. Hick–Hyman is not the overload
mechanism (CHI 2020).

## CONTEXT

- **Chooser**: Facing many comparable options, high stakes, low expertise.
- **Set**: Large, unsorted.

## REQUIREMENTS

```
R1. Record moderators in CHOICE_COMPLEXITY. [MUST]
R2. Do not cite Hick as why purchase drops. [MUST]
R3. Opt-out may be AVOIDANCE, not a new OPT_OUT construct. [SHOULD]
```

## OUTCOMES

Purchase, deferral, or opt-out.

## PROCESS — Formal

```
PROCESS ChoiceOverload (INPUT: large comparable set; OUTPUT: pick or opt-out)
  1. CHOICE [SET: 24] [ARCHITECTURE: open] of options. [INTERACTIVE, OVERLOAD]
     CHOICE_COMPLEXITY: comparable options; high stakes; low expertise
     HCI_TOUCHPOINT: catalogue grid
     HUMAN_LOAD: extraneous — unsorted comparable list
  2. DECISION [ON: whether to search further; RULE: maximize] keep looking. [HUMAN]
  3. AVOIDANCE [MODE: behavioral] of choosing. [AVOIDANT]
  4. EMERGENT [TYPE: interactive]
```
