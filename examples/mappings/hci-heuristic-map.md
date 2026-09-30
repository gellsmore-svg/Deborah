# HCI heuristic and choice-complexity map

Four verbs: `CHOICE`, `GULF`, `AFFORDANCE`, `FORAGE`. Demand arc stays
`HUMAN_DEMAND:` (ORIENT/ACT/CLOSE/RECOVER/ADAPT). `HCI_TOUCHPOINT:` is an
annotation (where in the UI), not a construct.

Sources: Norman *Design of Everyday Things* / Cognitive Engineering 1986;
Nielsen 1994 heuristics; ISO 9241-11; Sweller cognitive load; Cowan 2001 (~4
chunks); Hick 1952 / Hyman 1953; CHI 2020 on Hick in HCI
(https://doi.org/10.1145/3313831.3376878); Fitts 1954; Card, Moran & Newell
KLM/GOMS; Pirolli & Card information foraging; Iyengar & Lepper 2000; Schwartz
2004; Scheibehenne et al. 2010; Nielsen 2026 cognitive-load-as-budget
(https://jakobnielsenphd.substack.com/p/cognitive-load).

## Norman

Gulfs of execution and evaluation → `GULF [KIND:]`. Seven-stage cycle sits in
`HUMAN_DEMAND`. Affordances, signifiers, mapping → `AFFORDANCE` (no SIGNIFIER
construct).

## Nielsen 10 (1994) — not ten constructs

| Heuristic | Representation |
|---|---|
| Visibility of system status | `GULF [KIND: evaluation]` + `SUPPORT:` |
| Match system / real world | `AFFORDANCE [MAP: natural]` |
| User control and freedom | `CHOICE [ARCHITECTURE: open]` + `SUPPORT:` |
| Consistency and standards | `AFFORDANCE [MAP:]` + prose |
| Error prevention | `FAILURE_MODE:` + `CHOICE [ARCHITECTURE: progressive\|default]` |
| Recognition rather than recall | `AFFORDANCE` + `FORAGE [SCENT: strong]` + `ATTENTION` |
| Flexibility and efficiency of use | `CHOICE [ARCHITECTURE: progressive]` |
| Aesthetic and minimalist design | `CHOICE [SET:]` + `HUMAN_LOAD:` + tag `OVERLOAD` |
| Help users recognise, diagnose, recover from errors | `FAILURE_MODE:` + `HUMAN_DEMAND` RECOVER |
| Help and documentation | `SUPPORT:` |

## Other laws

| Object | Representation |
|---|---|
| ISO 9241-11 usability | OUTCOMES (effectiveness, efficiency, satisfaction) |
| Sweller intrinsic/extraneous/germane | `HUMAN_LOAD:` prose — **not** a LOAD_TYPE annotation |
| Hick–Hyman | `CHOICE [SET: n]` for equiprobable choice-reaction. **Not** “fewer is always faster.” Many UI tasks are visual search → `FORAGE` (CHI 2020). |
| Fitts / KLM / GOMS | `HUMAN_DEMAND` ACT + timing prose, not constructs |
| Information foraging | `FORAGE [SCENT:]` |
| Choice overload | `CHOICE` + `CHOICE_COMPLEXITY:` + tag `OVERLOAD` + optional `AVOIDANCE` / `DECISION [RULE: maximize]`. Mean meta-analytic effect ~0; strongest when options comparable, stakes high, expertise low. |
