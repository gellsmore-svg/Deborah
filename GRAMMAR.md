# Cairn — structural grammar (v0.10)

A minimal EBNF for the **structural skeleton** of a Cairn description. It defines
*shape*, not meaning: the prose in step descriptions, CONTEXT, ACCEPTANCE, etc. is
intentionally **free text** (that is where human readability lives). Tooling and
LLMs validate the skeleton; they do not parse the words.

Notation: `=` defines, `|` alternation, `{ }` zero-or-more, `[ ]` optional,
`( )` grouping, `"…"` literal, `(* … *)` comment. Indentation is significant
(shown as `INDENT` / `DEDENT`). `TEXT` is free-form text to end of line; `NL` is a
newline.

```ebnf
document        = { directive | block } ;
directive       = "render-profile:" profile-name NL ;   (* ai | operator | human_demand | human_factors | executive | audit | custom *)
block           = context-block
                | requirements-block
                | outcomes-block
                | process
                | plan ;

(* ---- scene & requirements modes ---- *)
context-block   = "CONTEXT" NL { TEXT NL } ;
outcomes-block  = "OUTCOMES" NL { TEXT NL } ;
requirements-block = "REQUIREMENTS" NL { requirement } ;
requirement     = req-id "." TEXT [ priority ] NL
                  [ "ACCEPTANCE:" TEXT NL ] ;
req-id          = "R" digit { digit } ;
priority        = "[" ( "MUST" | "SHOULD" | "MAY" ) "]" ;

(* ---- process mode ---- *)
plan            = "PLAN" name "REVISION" number "[STATUS:" plan-status "]" NL
                  INDENT [ "PARENT:" (number | "none") NL ]
                         "REQUEST:" TEXT NL
                         "TRIGGER:" TEXT NL
                         [ "INTENT:" TEXT NL ]
                         [ "ON_UNCERTAINTY:" uncertainty-policy NL ]
                         [ "ASSUMES:" capability-ref { "," capability-ref } NL ]
                         [ plan-outcomes ]
                         [ plan-reevaluate ]
                         process
                  DEDENT ;
plan-status     = "draft" | "active" | "stable" | "complete" | "blocked"
                | "open" | "refused" ;
uncertainty-policy = "record" | "escalate" | "abort" ;
capability-ref  = name [ "@" version ] ;
plan-outcomes   = "OUTCOMES:" [ TEXT ] NL { INDENT "-" TEXT NL } ;
plan-reevaluate = "REEVALUATE_WHEN:" [ TEXT ] NL { INDENT "-" TEXT NL } ;

process         = "PROCESS" name [ signature ] NL
                  INDENT { proc-element } DEDENT ;
signature       = "(" "INPUT:" params ";" "OUTPUT:" params ")" ;
params          = TEXT | "—" ;
proc-element    = state-block
                | constraints-block
                | context-block
                | step ;

state-block     = "STATE" NL INDENT { state-decl } DEDENT ;
state-decl      = name "[" "scope:" scope ";" "dir:" dir "]"
                  [ "ref:" ref-id ] [ comment ] NL ;
scope           = "global" | "process" | "session" | "iteration" | multi-scale ;   (* multi-scale e.g. org.team, individual.cognitive for human systems *)
multi-scale     = word ("." | "/") word { ("." | "/") word } ;
dir             = "read" | "write" | "read/write" ;
ref-id          = letter { digit } ;          (* e.g. S1, T4, M2, H1 *)

constraints-block = ( "CONSTRAINTS" | "BOUNDARIES" ) ( ":" TEXT NL
                  | NL INDENT { TEXT NL } DEDENT ) ;

(* ---- steps ---- *)
step            = step-id [ construct ] TEXT [ tags ] NL
                  [ INDENT { sub-block } DEDENT ] ;
step-id         = number { "." number } [ letter ] "." ;   (* 1.  2.1  3a. *)

sub-block       = annotation
                | construct-line
                | step ;                       (* nested steps *)
annotation      = ( "STATE UPDATE:" | "OUTPUT:" | "RISKS:" | "PURPOSE:"
                  | "CONSTRAINTS:" | "BOUNDARIES:" | "CONTEXT:"
                  | "HUMAN_DEMAND:" | "HUMAN_LOAD:" | "HUMAN_SIMULATION:"
                  | "HUMAN_FACTORS:" | "HUMAN_RISK:"
                  | "TRUST:" | "SUPPORT:" | "FAILURE_MODE:"
                  | "SIMULATION_FINDINGS:" | "IMPROVEMENT:" | "CHANGE_IMPACT:"
                  | emergent-satisfies ) TEXT NL ;
emergent-satisfies = "EMERGENT" ( satisfies | attrs ) NL { TEXT NL } ;   (* e.g. EMERGENT [TYPE: psychological; FROM: regulation] or [SATISFIES: R3]; attrs for domain/feedback *)

(* a step may *be* a construct, or a construct may stand on its own line *)
construct       = "STEP" | "MILESTONE" | "ITERATE" | "RECURSE" | "QUEUE"
                | "PARALLEL" | "SERVICE" | "DECISION" | "RETRY"
                | "ERROR" | "AWAIT" | "CALL"
                | "REGULATION" | "APPRAISAL" | "DUAL_PROCESS" | "METACOGNITION"
                | "ALIGN" | "COALITION" | "RESISTANCE" | "REINFORCEMENT"
                | "CASCADE" | "VISION" | "SOCIALIZE" | "INSTITUTIONALIZE"
                | "SYMBOLIC_INTERACTION" | "CONFLICT" | "ACCOMMODATE"
                | "ASSIMILATE" | "ROLE" | "FEEDBACK" | "MACRO" ;
construct-line  = ( "MILESTONE" | "ITERATE" | "RECURSE" | "QUEUE" | "PARALLEL"
                  | "SERVICE" | "CONCURRENT" | "DECISION" | "RETRY" | "ERROR"
                  | "AWAIT" | "CALL" | "MERGE" | "BREAK" | "CONTINUE" | "ATOMIC"
                  | "REGULATION" | "APPRAISAL" | "DUAL_PROCESS" | "METACOGNITION"
                  | "ALIGN" | "COALITION" | "RESISTANCE" | "REINFORCEMENT"
                  | "CASCADE" | "VISION" | "SOCIALIZE" | "INSTITUTIONALIZE"
                  | "SYMBOLIC_INTERACTION" | "CONFLICT" | "ACCOMMODATE"
                  | "ASSIMILATE" | "ROLE" | "FEEDBACK" | "MACRO" )
                  [ modifiers ] [ "→" TEXT ] TEXT? NL ;
modifiers       = "[" mod { ";" mod } "]" ;
mod             = key ":" TEXT | flag ;        (* e.g. UNTIL: …; MAX: 5 *)

(* ---- tags ---- *)
tags            = "[" tag { "," tag } "]" ;
tag             = reserved-tag [ "[" TEXT "]" ]    (* IDEMPOTENT [KEY: …], BATCH [n] *)
                | assisted-by
                | satisfies
                | ext-tag ;
reserved-tag    = actor | determinism | timing | effect | control
                | domain-tag ;
domain-tag      = psychological-tag | organisational-tag | sociological-tag ;
psychological-tag = "EMOTIONAL" | "COGNITIVE" | "APPRAISAL" | "REGULATION"
                | "MOTIVATIONAL" | "METACOGNITIVE" | "BEHAVIORAL" ;
organisational-tag = "LEADERSHIP" | "STRATEGIC" | "CULTURAL" | "POWER"
                | "STAKEHOLDER" | "STRUCTURAL" | "ALIGNMENT" | "RESISTANCE" ;
sociological-tag = "SOCIAL" | "GROUP" | "NORM" | "ROLE" | "SYMBOLIC" ;
actor           = ( "LLM" | "HUMAN" | "CODE" | "EXTERNAL" ) [ ":" role ] ;  (* HUMAN: Product Lead *)
assisted-by     = "ASSISTED-BY:" actor { "," actor } ;
role            = word { word } ;
determinism     = "DETERMINISTIC" | "STOCHASTIC" ;
timing          = "SYNC" | "ASYNC" ;
effect          = "PURE" | "SIDE-EFFECT" | "IDEMPOTENT" ;
control         = "BLOCKING" | "GATED" | "CACHED" | "BATCH" ;
satisfies       = "SATISFIES:" req-id { ( "," | "+" ) req-id } [ TEXT ] ;
ext-tag         = namespace ":" word ;         (* e.g. x:rerank, team:billing *)

name            = word { word } ;
number          = digit { digit } ;
```

## Well-formedness (from SPEC §12)

Beyond grammar, a description is well-formed if:

1. it has at least one CONTEXT, REQUIREMENTS/OUTCOMES, or PROCESS block;
2. every PROCESS has a name (and a signature when it has input/output);
3. step numbering is consistent and properly nested;
4. reserved tags use at most one value per dimension; custom tags are namespaced;
5. every `STATE UPDATE` names a piece declared in a `STATE` block;
6. LLM-driven `ITERATE`/`RECURSE` carry a bound (`MAX`/`MAX_DEPTH`);
7. `BREAK`/`CONTINUE` appear only inside a loop;
8. every `AWAIT` states a `TIMEOUT`.
9. Domain constructs (REGULATION, COALITION, SOCIALIZE, FEEDBACK, MACRO, etc.) are encouraged when using matching tags for psych/org/socio work in human systems.
10. Human-facing high-load steps should expose human demand (ORIENT / ACT / CLOSE), support, trust, recovery, and change impact where relevant.
11. New render profiles: `therapeutic`, `change_leader`, `human_demand`, and `human_factors` for domain-focused views.

This grammar is deliberately permissive about prose — it constrains the
*scaffolding*, so a human stays free to write each step in plain language.
