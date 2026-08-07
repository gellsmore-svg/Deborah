# Deborah process semantics and implementation roadmap

**Date:** 2026-08-07 · **Status:** Phases A–C implemented · **Baseline:** package
0.10.0; language SPEC **v0.11**; contracts **1.0**

This document:

1. Records a multi-pass critique of the ChatGPT three-layer proposal and the
   first draft roadmap.
2. States the **refined** semantic model (what we keep, cut, rename, defer).
3. Sequences implementation so language, contracts, and runtime stay honest.

It replaces the earlier draft of the same path in spirit; treat this as the
working plan.

---

## Part I — Recursive review (findings)

### Pass 1 — Fit to Deborah’s actual role

**Claim under test:** Deborah should become a “process reasoning language” via
execution × behaviour × cognitive intent.

**What holds**

- Separating *how computation proceeds* from *what product a step owes* is
  useful and currently underspecified.
- Cognitive product types (observe → infer → evaluate → decide) match real
  cross-LLM work (retrieve evidence, form claim, score options, commit).
- Annotations that never affect validation or interpretation rot; contracts
  should be enforceable *when claimed*.

**What fails or overreaches**

- Deborah’s settled role is **framing callers against capabilities** and
  **crystallising** sequences — not hosting continuous multi-agent cognition on
  the hot path (SPEC opening; roles-assessment executive decision).
- Estate phrase *“runs deterministically thereafter”* means a **fixed
  control graph + enforced bounds/allow-lists**, not “every step is
  `[CODE, DETERMINISTIC]`”. Stochastic LLM steps remain valid *inside* a
  crystallised plan. The ChatGPT write-up sometimes blurs that.
- “Process reasoning language” is a long-term *aspiration*, not a licence to
  grow three full runtime subsystems in one language revision.

**Refinement:** Adopt the *axes*, not the maximal product vision. Ship only what
strengthens framing and enforceable step contracts.

---

### Pass 2 — Orthogonality stress-test

| Layer (ChatGPT) | Orthogonal in theory? | In Deborah practice |
|---|---|---|
| Execution (det/stoch) | Yes vs other two | **Already** §7 tags; dual vocabulary would be harmful |
| Control behaviour (5 types) | Claimed composable | **Collides** with constructs (`AWAIT`, `ITERATE`, `DECISION`, `RECURSE`, `RETRY`) and with crystallisation |
| Cognitive intent (7 types) | Yes if defined as *output contract* | Strong; overlaps PURPOSE only if misnamed |

**Behaviour layer problems (material)**

1. **Dual control languages.** `BEHAVIOUR: reactive` vs `AWAIT [EVENT:…]` —
   authors will not know which is authoritative.
2. **Scope confusion.** “Adaptive” and “exploratory” often describe *plan
   policy* or *authoring-time search*, not a single step’s local property.
3. **Combinatorial explosion.** Five multi-select behaviours × seven cognitions
   × det/stoch × actor = untestable policy matrix if all are runtime-live.
4. **Hot-path risk.** Unbounded adaptive/exploratory behaviour *is* Level-4
   replanning under another name unless every use is bound and crystallised.

**Refinement:** Do **not** ship five first-class composable behaviours on every
step in v0.11. Split control into:

- **Already structural** (constructs + bounds + GATED) — keep as source of truth.
- **Narrow, enforceable step modifiers** only where they change contracts
  without duplicating constructs (see Part II).
- **Plan-level policy** for residual/uncertainty/exploration budget (extends
  `ON_UNCERTAINTY`, not a behaviour soup).

---

### Pass 3 — Cognitive set: which seven earn a seat?

| Cognition | Keep in MVP? | Why |
|---|---|---|
| **observe** | **Yes** | Evidence + provenance; matches retrieval/capability read |
| **infer** | **Yes** | Claim + evidence link; core of LLM reasoning steps |
| **evaluate** | **Yes** | Criteria + score without commitment; separates critique from decide |
| **decide** | **Yes** | Commitment; maps to DECISION construct + human GATED |
| negotiate | Defer | Wire protocol + crystallisation already cover multi-party; step-level later |
| learn | Defer as *full* contract | Durable side-effect; belongs with gated evolution (Tirzah) / SIDE-EFFECT; partial: flag only |
| optimize | Defer as *full* contract | Mostly a loop (ITERATE + evaluate + stop); not a single product shape |

**Refinement:** MVP cognitive set = **`observe | infer | evaluate | decide`**.
Reserve `negotiate | learn | optimize` as **documented future** values that
parse as unknown→warning (or reject until defined), not half-implemented
promises.

---

### Pass 4 — Confidence and automatic recursion

ChatGPT’s auto-loop:

```text
low inference_confidence → observe or infer again
```

**Risks**

- Unbounded cost and non-reproducible graphs (estate evidence: pass^k collapse,
  token blow-ups).
- Float confidence is false precision (learning architecture: bands + basis).

**Refinement**

- Confidence: **ordinal bands** (`high|medium|low|unassessed`) with optional
  `basis`, three dimensions: `evidence`, `inference`, `execution`.
- Process-level re-entry only if **all** of:
  1. step declares `COGNITION`,
  2. plan or step declares a **bound** (`MAX` / plan budget),
  3. plan policy allows re-entry (default: **off**; crystallised opt-in),
  4. interpreter records each re-entry as a first-class event (Galeed later).
- Default on low confidence: terminate **`open`** or **`escalate`** per
  `ON_UNCERTAINTY` — not silent re-planning.

---

### Pass 5 — Naming and collisions

| Term | Keep meaning | Do not use for |
|---|---|---|
| PLAN `INTENT` | Application success meaning | Cognitive product type |
| `PURPOSE:` | Why the step/process exists (motivation) | Expected output schema |
| Tag `DETERMINISTIC`/`STOCHASTIC` | Layer A execution | Control behaviour |
| Tag `GATED` / `BLOCKING` | Human/control coupling | Cognitive evaluate |
| **`COGNITION:`** (chosen) | Expected semantic product + contract | Business intent |
| ChatGPT “intent:” | **Rejected as keyword** | — |

**PURPOSE vs COGNITION example**

```text
PURPOSE: keep the operator informed of retrieval quality
COGNITION: evaluate
```

Both valid; different questions.

---

### Pass 6 — Enforceability vs documentation theatre

Principle: *if it is in the language as a contract, something must check it.*

| Annotation | Enforceable without full agent runtime? | How |
|---|---|---|
| DETERMINISTIC/STOCHASTIC | Partially | Lint: CODE steps default det; LLM steps should not claim DETERMINISTIC without note |
| COGNITION + structured result | **Yes** | Schema check on result artifact |
| COGNITION alone | Soft | Warn if OUTPUT missing under strict profile |
| BEHAVIOUR: exploratory | Yes if bound required | Fail validate without MAX/UNTIL on nearby loop |
| BEHAVIOUR: adaptive | **Hard** without runtime metrics | Defer |
| Auto confidence recursion | Only with interpreter + budget | Phase 3+ |

**Refinement:** Phase order is **contracts before behaviours before auto-recursion**.

---

### Pass 7 — Conflict with crystallisation (authoring vs execution)

| Activity | When | Stochastic LLM OK? |
|---|---|---|
| Negotiate capability use, explore surface | Authoring / REVISION | Yes (bounded) |
| Execute crystallised PLAN | Runtime | Yes **on marked steps**; graph fixed |
| Re-open exploration | New REVISION or explicit exploratory *loop construct with MAX* | Not implicit |

**Refinement:** Document explicitly that **crystallised ≠ all-deterministic
steps**. Crystallised means **versioned, allow-listed, bounded control**.

---

### Pass 8 — What the first roadmap got wrong

| Earlier draft | Problem | Refined position |
|---|---|---|
| Five composable `BEHAVIOUR` values in Phase 0 | Too early; dual control language | Defer most; keep 0–2 modifiers later |
| Seven cognitions at once | negotiate/learn/optimize undercooked | Four MVP |
| Optional `EXECUTION:` alias soon | Noise | Spec synonym table only; no new syntax |
| Thin runtime in same breath as axes | Couples large estate work to vocab | Language contracts first |
| “Process reasoning language” as near-term | Overclaims | Framing + contracts; reasoning is emergent from enforced products |

---

## Part II — Refined semantic model

### Layers (stable)

```text
HOW     → execution semantics     → tags DETERMINISTIC | STOCHASTIC  (exists)
PRODUCT → cognitive contract      → COGNITION: observe|infer|evaluate|decide  (new)
FRAME   → plan-level uncertainty  → INTENT, OUTCOMES, ASSUMES, ON_UNCERTAINTY  (0.10)
CONTROL → constructs + bounds     → ITERATE/AWAIT/DECISION/… + MAX/GATED     (exists)
```

**Control behaviour** from ChatGPT is **not** a peer layer in v0.11. Pieces map:

| ChatGPT behaviour | Refined home |
|---|---|
| reactive | `AWAIT` / `SERVICE` / evented plans |
| adaptive | `DECISION` + plan REVISION; later policy |
| exploratory | `ITERATE`/`RECURSE` **with MAX** + residual `open`; optional plan flag `exploration_budget` later |
| reflective | post-condition: residual/assumption check when `COGNITION` ∈ {infer, evaluate, decide} under strict mode |
| adversarial | capability choice: prefer critique/challenge tools when ASSUMES includes them; optional `COGNITION: evaluate` + criteria “adversarial” |

### Cognitive contracts (MVP)

When `COGNITION` is set **and** a structured result is supplied (strict mode),
require approximately:

| COGNITION | Required product keys (illustrative) |
|---|---|
| `observe` | `evidence[]` (each with `source` / provenance), no mandatory `claim` |
| `infer` | `claim`, `evidence_refs[]`, `assumptions[]?`, `confidence.inference` |
| `evaluate` | `criteria[]`, `scores` or `ranking`, `confidence.evidence?` |
| `decide` | `selected`, `alternatives[]?`, `constraints[]?`, commitment flag |

Soft mode: annotation is metadata only + render.

### Confidence (MVP) — implemented in `deborah.contracts`

```text
confidence:
  evidence: high|medium|low|unassessed
  inference: high|medium|low|unassessed
  execution: high|medium|low|unassessed
  basis: short prose optional
```

No single float as the system of record (`validate_confidence` rejects
float-only shapes).

### Re-entry policy (documented only)

Process-level re-entry when inference confidence is low is **not** automatic:

1. Step must declare `COGNITION`
2. Plan or loop must declare a **bound** (MAX / budget)
3. Plan policy must opt in (default **off**)
4. Otherwise use `ON_UNCERTAINTY`: `record` → often terminal `open`, or `escalate`

Silent unbounded re-planning remains a non-goal.

### Surface syntax (proposed, progressive)

```text
2. Form a hypothesis about the outage. [LLM, STOCHASTIC]
   PURPOSE: narrow the incident class before paging
   COGNITION: infer
   OUTPUT: ...
```

Omit `COGNITION` → today’s behaviour (no product contract).

---

## Part III — Refined implementation roadmap

### Principles for sequencing

1. **No dead dialect** — only ship annotations we can validate or render usefully.
2. **Four cognitions before seven.**
3. **No behaviour multi-select in Phase 0.**
4. **Runtime after contracts.**
5. **Crystallisation story stays authoritative** for negotiation/exploration.

### Phase A — Spec + parse + golden example *(Deborah-only, first)* — **DONE**

**Shipped**

- SPEC §17 axes; §5 `COGNITION`; crystallised ≠ all-deterministic (§14.3)
- `COGNITION:` parse + well-formedness (MVP four; reserved rejected)
- Export: step `cognition`, `execution`, `purpose`
- Conformance 1.2 + `COGNITION_MVP` / `COGNITION_RESERVED`
- Golden example `examples/cross-llm-critique.cairn.md`
- Tests: `tests/test_cognition.py`

**Still out (later phases)**

- BEHAVIOUR multi-select
- negotiate/learn/optimize contracts
- Interpreter
- Confidence auto-recursion

### Phase B — Frame enforcement in tools *(Deborah-only)* — **DONE**

- Render PLAN framing + COGNITION in narrative/operator/audit/executive
- `validate_plan(profile="full"|"core"|"strict")`
- Strict: COGNITION requires output/success_criteria; CALL tools ⊆ assumes
- `deborah-validate --profile core|full|strict`
- Bridge projects PLAN-nested PROCESS steps into the render model

### Phase C — Soft/strict result contracts — **DONE**

- `deborah.contracts`: `validate_cognition_result`, `validate_confidence`,
  `validate_step_results`, `EXAMPLE_RESULTS`
- Confidence: ordinal bands on evidence / inference / execution (+ optional basis)
- Soft vs strict modes; fixtures in `tests/fixtures/cognition_results.json`
- CLI: `deborah-validate … --results path.json --results-mode soft|strict`
- Re-entry policy documented (opt-in + MAX; default open/escalate) — **not** implemented

### Phase D — Thin interpreter

- Walk core constructs; allow-list; ON_UNCERTAINTY terminals
- Optional: if step has COGNITION and returns structured result, run contract check
- Re-entry **off by default**; experimental flag later with MAX

### Phase E — Estate integration

- Keturah resolve ASSUMES
- Galeed decision/residual events
- One real slice (retrieve + critique)
- Map adversarial evaluation to Milcah-style critique capability

### Phase F — Deferred cognitions & policies

- `negotiate` / `learn` / `optimize` contracts with explicit gates
- Plan-level `exploration_budget` if still needed
- Reflective post-pass as interpreter policy for evaluate/infer

### Explicit non-goals (unchanged + sharpened)

- Hot-path multi-role free re-planning
- Learning store inside Cairn
- Dual `execution:` syntax competing with tags
- Five composable behaviours as Phase A
- Float-only confidence
- Auto-learn into production defaults

---

## Part IV — PR plan (refined)

| PR | Content | Phase |
|---|---|---|
| R1 | This document + SPEC section (axes, naming, crystallised≠det steps) | A |
| R2 | Parser/validator/export `COGNITION` (4 values) | A |
| R3 | Golden example + tests | A |
| R4 | Render framing + cognition | B |
| R5 | core/strict validate profiles; assumes/CALL checks | B |
| R6 | Result contract schemas + fixtures | C |
| R7 | Thin interpreter + terminals | D |
| R8 | Keturah/Galeed slice | E |
| R9 | Deferred cognitions + optional re-entry under MAX | F |

---

## Part V — Key decisions (after review)

1. **Keep three *ideas*, not three equal runtime layers.** HOW exists; PRODUCT
   is the new language work; ChatGPT “behaviour” mostly maps to constructs +
   plan policy.
2. **MVP cognition = observe, infer, evaluate, decide.**
3. **Name = `COGNITION:`** only.
4. **Confidence = bands, three dimensions; re-entry opt-in and bounded.**
5. **Default low-confidence path = `open` / `escalate`, not silent retry loops.**
6. **Crystallised plans may contain stochastic steps.**
7. **Contracts before interpreter before auto-recursion.**
8. **Do not add `BEHAVIOUR:` multi-select in the first language cut.**

---

## Part VI — Open questions (narrowed)

1. **Strict profile default for CI examples?** Recommend `full` for corpus,
   `strict` only for new cognitive examples.
2. **Structured results in-document vs runtime-only?** Recommend runtime
   artifacts first; optional fenced JSON under OUTPUT later.
3. **Should `decide` require `DECISION` construct?** Recommend lint warning if
   COGNITION=decide on a bare STEP without DECISION/GATED when human-owned.
4. **Thin runtime package location:** `deborah.runtime` stub vs Tirzah extract —
   still open; R7 can stub handlers.

---

## Part VII — One-paragraph summary

The ChatGPT model is directionally right that Deborah should separate **how
steps compute**, **what products they owe**, and **how control is structured** —
but the draft roadmap over-weighted a fifth “behaviour” taxonomy that duplicates
existing constructs and threatens crystallisation. The refined plan reuses
determinism tags, adds a progressive **`COGNITION`** contract for four products
(observe/infer/evaluate/decide), keeps plan framing from 0.10, leaves control
primarily to constructs and bounds, defers negotiate/learn/optimize and
auto-recursion, and sequences **spec → parse → contracts → thin runtime →
estate slice** so every annotation earns its keep.
