# Behavioural-economics inventory map

Grammar names four verbs (`FRAME`, `NUDGE`, `ACCOUNT`, `DISCOUNT`) plus CORE
`DECISION [ON: …; RULE: satisfice | maximize]`. Bias *names* live in `BIAS:`.
Do not mint one construct per Decision Lab entry.

Sources: Kahneman & Tversky 1979 prospect theory (https://doi.org/10.2307/1914185);
Tversky & Kahneman 1974 heuristics; Thaler mental accounting / endowment;
Thaler & Sunstein *Nudge* (2008); Simon satisficing; MINDSPACE (Dolan et al. 2010);
EAST (BIT 2014); Iyengar & Lepper 2000; Schwartz 2004; Scheibehenne, Greifeneder
& Todd 2010 (https://www.researchgate.net/publication/48210291_Can_There_Ever_be_Too_Many_Options_A_Meta-analytic_Review_of_Choice_Overload).

| Inventory item | Representation |
|---|---|
| Prospect theory (reference, loss aversion, diminishing sensitivity, probability weighting) | `FRAME [VALENCE:][REF:]`; probability weighting as `BIAS: probability_weighting` |
| Availability, representativeness, anchoring-and-adjustment | `BIAS:` + `DUAL_PROCESS [SYSTEM: 1]` + often `FRAME` |
| Mental accounting, endowment | `ACCOUNT [KIND: mental \| fungible]` |
| Nudge / choice architecture | `NUDGE` + HCI `CHOICE [ARCHITECTURE:]` |
| Satisficing / bounded rationality | `DECISION [ON: …; RULE: satisfice]` (same first bracket as ON) |
| Present bias / hyperbolic discounting | `DISCOUNT [SHAPE: hyperbolic]` |
| Status quo / default | `NUDGE [TOOL: default]` and/or `CHOICE [ARCHITECTURE: default]` |
| Sunk cost | `ACCOUNT [KIND: mental]` + `APPRAISAL` |
| Social proof | `NUDGE [TOOL: social_proof]` |
| Mullainathan & Thaler bounded rationality / willpower / self-interest | `DECISION [RULE:]`, `DISCOUNT`, GT `PLAY`/`RECIPROCAL` |
| Choice overload | HCI `CHOICE` + `CHOICE_COMPLEXITY:` + tag `OVERLOAD` + optional `AVOIDANCE` / `DECISION [RULE: maximize]` |

## MINDSPACE → NUDGE TOOL

Messenger→`messenger`; Incentives→`incentive`; Norms→`social_proof`;
Defaults→`default`; Salience→`salience`; Priming→`salience` or `affect` +
`BIAS: priming`; Affect→`affect`; Commitments→`commitment`; Ego→`affect` /
`messenger` + `BIAS: ego`.

## EAST → NUDGE TOOL

Easy→`friction` (reduce or add); Attractive→`salience`/`affect`;
Social→`social_proof`; Timely→`timing`.

Choice-overload moderators (Scheibehenne et al.): option comparability, stakes,
expertise, set size. Mean meta-analytic effect near zero — encode as
`CHOICE_COMPLEXITY:` prose, not a boolean construct.
