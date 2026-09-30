# Game-theory inventory map

Four verbs: `GAME`, `PLAY`, `EQUILIBRIUM`, `SIGNAL`. Do not mint one construct
per 2×2 or solution concept. Do **not** tag GAME steps `STRATEGIC` (org tag).

Sources: Fudenberg & Tirole; Osborne; Nash 1950; Camerer *Behavioral Game Theory*
(2003); ultimatum/dictator/trust guide
(https://online.ucpress.edu/collabra/article/7/1/19004/116331/Economic-Games-An-Introduction-and-Guide-for).

| Axis / object | Representation |
|---|---|
| Simultaneous vs sequential | `GAME [STRUCTURE:]` |
| One-shot vs repeated | omit `repeated` vs `STRUCTURE: repeated` |
| Complete vs incomplete information | `INFORMATION:` annotation |
| Zero-sum vs general-sum | `KIND: zero_sum` vs other kinds |
| Cooperative vs non-cooperative | KIND/prose |
| Canonical 2×2 | `KIND: pd \| stag_hunt \| chicken \| coordination` + `PAYOFF:` |
| Dominant / Nash / mixed / Pareto / correlated / ESS / focal / SPE / Bayesian Nash | `EQUILIBRIUM [CONCEPT:]` |
| Mechanism design / principal–agent | `KIND: principal_agent` |
| Signalling vs cheap talk | `SIGNAL [COST: cheap \| costly]` |
| Iterated PD / tit-for-tat | `GAME [STRUCTURE: repeated; KIND: pd]` + `ITERATE` + `PLAY` (no TIT_FOR_TAT construct) |
| Public goods / free-rider | `KIND: public_goods` |
| Behavioural GT (ultimatum ~40% offers, reject <20%; dictator ~20–30%; trust; inequity aversion, reciprocity, level-k) | tag `RECIPROCAL`; `PLAY`; psych `INTERPERSONAL`/`APPRAISAL`; level-k as `METACOGNITION` |

## Worked 2×2 orderings

| Game | Ordering |
|---|---|
| Prisoner's Dilemma | T>R>P>S |
| Stag Hunt | R>T>P>S |
| Chicken / snowdrift | T>R>S>P |

## Rewrite of informal `GAME_THEORY:` (same PR)

Informal `GAME_THEORY:` was silently dropped by the parser. Replace with
`GAME`/`PLAY`/`EQUILIBRIUM`/`SIGNAL` + `PAYOFF:`/`INFORMATION:`. Do **not**
add `GAME_THEORY` to `_ANNOTATION`.

| Former prose | Frozen verbs |
|---|---|
| Intermittent reassurance reinforces escalation | `HABIT [PHASE: reward]` + repeated `GAME` + `PLAY [MOVE: cooperate]` |
| Public challenge rewards dominance | `GAME [KIND: chicken]` + `INTERPERSONAL [PATTERN: rank]` + `PLAY [MOVE: defect]` |
| Sharing inside information for status | `GAME [KIND: signalling]` + `SIGNAL [COST: cheap]` + `PLAY [MOVE: signal]` |
| Support requests punished → concealment | `GAME [KIND: pd]` + `PLAY [MOVE: defect]` + `AVOIDANCE` |
| Harsh review vs future contribution | `GAME [STRUCTURE: repeated; KIND: pd]` + `PLAY [MOVE: punish]` + `DISCOUNT` |
| GRC speak-up / audit / vendor | `GAME [KIND: principal_agent\|public_goods]` + `SIGNAL [COST: costly]` |
