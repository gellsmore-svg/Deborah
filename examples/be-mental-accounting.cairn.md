# Behavioural economics: Mental accounting

Thaler mental accounting and endowment. Not time preference (that is DISCOUNT).

## CONTEXT

- **Person**: Treats earmarked money as non-fungible.
- **Pile**: Named budget (windfall, gift, fun).

## REQUIREMENTS

```
R1. ACCOUNT KIND is mental or fungible, not temporal. [MUST]
R2. Sunk cost is ACCOUNT plus APPRAISAL, not a SUNK_COST construct. [MUST]
```

## OUTCOMES

Spend from the labelled pile, or refuse an equivalent fungible transfer.

## PROCESS — Formal

```
PROCESS MentalAccount (INPUT: labelled money; OUTPUT: spend or withhold)
  1. ACCOUNT [KIND: mental] of the windfall pile. [HEURISTIC]
  2. APPRAISAL [TYPE: secondary] of already-spent slots as non-fungible. [APPRAISAL]
     BIAS: sunk_cost
  3. DECISION [ON: spend from this pile vs treat as fungible]
  4. EMERGENT [TYPE: behavioural_economic]
```
