# HCI: Information foraging

Pirolli & Card: scent, diet, patches. Distinct from presented-set CHOICE.
CHI 2020: many UI tasks are visual search, not Hick choice-reaction.

## CONTEXT

- **Forager**: Hunting information across patches.
- **Scent**: Cue that a patch is worth entering.

## REQUIREMENTS

```
R1. FORAGE declares SCENT. [MUST]
R2. Salience without scent is a decoy, not forage-friendly. [SHOULD]
```

## OUTCOMES

A patch entered, or abandoned search.

## PROCESS — Formal

```
PROCESS InformationForage (INPUT: information ecology; OUTPUT: patch entered or abandoned)
  1. ATTENTION [MODE: select] among patches. [COGNITIVE]
  2. FORAGE [SCENT: strong] toward a labelled cluster. [INTERACTIVE]
     HCI_TOUCHPOINT: search results
  3. NUDGE [TOOL: salience] of a competing badge. [NUDGED]
  4. FORAGE [SCENT: weak] if the badge has no information diet. [INTERACTIVE]
  5. DECISION [ON: enter patch vs leave]
  6. EMERGENT [TYPE: interactive]
```
