# Deborah process semantics and implementation roadmap

**Date:** 2026-08-07 · **Status:** agreed direction for planning (not yet fully
implemented) · **Package baseline:** 0.10.0 / SPEC v0.10

This plan merges:

1. The post-0.10.0 improvement backlog (enforce the frame, core profile, runtime
   slice, Keturah pins, golden example).
2. The ChatGPT **three-layer process semantics** proposal (execution / control
   behaviour / cognitive intent), reconciled with Cairn’s existing tag system
   and non-goals.

---

## 0. Load-bearing principles (do not break these)

1. **Orthogonal layers stay orthogonal.** Do not invent a single taxonomy that
   mixes “how computation proceeds”, “how control loops behave”, and “what
   cognitive product is expected”.
2. **Deborah frames; it does not determinise models.** Stochastic steps stay
   stochastic. Determinism is one *execution* value, not the purpose of the
   language (SPEC opening role statement).
3. **Annotations that claim runtime contracts must eventually be enforceable.**
   Descriptive metadata that never affects validation or interpretation is a
   dead dialect — either wire it or keep it progressive/optional.
4. **Progressive formality.** Defaults remain terse. New axes are opt-in.
5. **Crystallisation.** Multi-round negotiation and exploration belong at
   *authoring* (or explicit REVISION); hot-path Level-4 free re-planning is out
   of scope (SPEC §14, §17).
6. **Name collisions avoided.**
   - PLAN `INTENT` = *application success meaning* (already in SPEC).
   - `PURPOSE:` = *why this step/process exists* (already in SPEC).
   - **Cognitive intent** (observe/infer/…) = *expected semantic product of a
     step* — must **not** reuse the word “intent” alone in the grammar. Proposed
     surface: **`COGNITION:`** sub-block or a dedicated tag dimension
     (`OBSERVE`, `INFER`, …).

---

## 1. Three orthogonal layers (target model)

### Layer A — Execution semantics

**Question:** How is the next state determined?

| Value | Meaning | Current Cairn home |
|---|---|---|
| `deterministic` | Same state + inputs → same transition/output | Tag `DETERMINISTIC` (§7) |
| `stochastic` | Sampling, generative models, probabilistic transitions | Tag `STOCHASTIC` (§7) |

**Decision:** Keep this **as the existing determinism tag dimension**. Do not
add a parallel `execution:` key that duplicates it. Document the synonym:

```text
execution: deterministic  ≡  […, DETERMINISTIC]
execution: stochastic     ≡  […, STOCHASTIC]
```

Optional later: allow `EXECUTION: deterministic|stochastic` as a sub-block
alias for readability; parser maps to the same dimension (one value per
dimension rule still holds).

### Layer B — Control behaviour

**Question:** How should the process behave while executing (orchestration
around steps)?

Composable (not exclusive):

| Behaviour | Meaning | Related existing constructs |
|---|---|---|
| `reactive` | Event-driven; re-evaluate on input change | `AWAIT`, `SERVICE`, event triggers |
| `adaptive` | Change routing/strategy from outcomes | `DECISION`, revision, learning *scope* |
| `exploratory` | Expand search / hypotheses under cost bounds | `ITERATE`/`RECURSE` + MAX, open questions |
| `reflective` | Reassess quality of prior steps/assumptions | `RECURSE` across steps, audit, residual |
| `adversarial` | Seek falsification / counter-evidence | Future: challenge CALL; Milcah critique |

**Decision:** Introduce as **optional composable annotations**, not five new
top-level constructs.

Proposed surface (v0.11 language):

```text
3. Pressure-test the draft answer. [LLM, STOCHASTIC]
   COGNITION: evaluate
   BEHAVIOUR: reflective, adversarial
   CRITERIA: groundedness, internal consistency
```

- `BEHAVIOUR:` comma-separated subset of the five values.
- Runtime meaning is **policy hints** for the interpreter (when present): e.g.
  `adversarial` prefers critique capabilities; `exploratory` requires a bound;
  `reflective` may schedule a residual check after OUTPUT.

### Layer C — Cognitive intent (expected semantic product)

**Question:** What kind of cognitive transformation is this step attempting?

| Cognition | Expected product (contract sketch) |
|---|---|
| `observe` | Evidence + provenance (not conclusions) |
| `infer` | Claim(s) + supporting evidence + assumptions + confidence bands |
| `evaluate` | Criteria + scores/ranks + comparison (no commitment) |
| `decide` | Selected alternative + constraints + commitment |
| `negotiate` | Agreement / residual disagreement + trade-offs |
| `learn` | Named durable change + scope + reversibility |
| `optimize` | Objective + constraints + candidate + stop rule |

**Decision:** First-class optional **`COGNITION:`** on steps (one value). This is
the axis that most clearly upgrades Deborah from workflow text toward a
**process reasoning language** — *if* the runtime enforces output contracts.

Naming: **`COGNITION`**, never bare `intent` (reserved for PLAN application
intent and PURPOSE prose).

### Composition (independent axes)

```text
[LLM, STOCHASTIC]          # Layer A
BEHAVIOUR: exploratory     # Layer B
COGNITION: infer           # Layer C
```

Means: stochastic computation, exploratory control, product is an inference
with evidence→claim structure — not “a random exploratory inference type” as a
single enum.

---

## 2. Mapping ChatGPT ideas onto Deborah’s existing spine

| ChatGPT idea | Do this in Deborah | Do **not** do this |
|---|---|---|
| Deterministic vs stochastic | Keep §7 tags; document as Layer A | New competing vocabulary |
| Control behaviours | `BEHAVIOUR:` optional multi-value | Five new constructs that bypass ITERATE/AWAIT |
| Cognitive intents | `COGNITION:` + output contracts | Collapse into PURPOSE or PLAN INTENT |
| Confidence dimensions | Structured OUTPUT / RESULT schema in runtime + optional sub-block | Single float confidence as truth |
| Process-level recursion | IR policies: low inference confidence → re-enter observe/infer under MAX | Implicit unbounded re-planning every call |
| Learn as first-class | `COGNITION: learn` + durable scope fields | Auto-write memory without gate (Tirzah evolution stays human-gated) |
| Negotiate | Crystallisation + protocol (authoring); optional step cognition | Full ACL in the grammar |
| “Process reasoning language” | Long-term product story | Boil the ocean in one release |

### Confidence (layered, not one float)

Align with learning-architecture bands where possible:

| Dimension | Meaning |
|---|---|
| `evidence_confidence` | Quality/sufficiency of observations |
| `inference_confidence` | Strength of claim given evidence |
| `execution_confidence` | Did the step machinery complete as intended? |

Optional later: `causal_confidence` (did the method cause the outcome?).

Runtime recursion sketch (only when COGNITION + bounds present):

```text
observe → infer → evaluate
              ↓
     inference_confidence low?
         → if exploratory/reflective allowed and budget remains
         → schedule observe or infer (MAX rounds)
         → else terminal open / escalate per ON_UNCERTAINTY
```

This is **process-level** recursion, distinct from `RECURSE` inside one step’s
tool loop.

---

## 3. Improvement backlog (from 0.10.0 review) — still in scope

| # | Work item | Depends on |
|---|---|---|
| B1 | Golden v0.10(+semantics) example + pytest | — |
| B2 | Render INTENT / ASSUMES / OUTCOMES / (later COGNITION) in operator/executive/audit | B1 |
| B3 | `validate_plan(..., profile="core")` | — |
| B4 | Structured CALL / ASSUMES checks (tools ⊆ assumes when both present) | — |
| B5 | Round-trip serialize PLAN framing (+ new fields) | semantics parse |
| B6 | Thin Deborah runtime: walk plan, allow-list, ON_UNCERTAINTY, terminals | B1, B3 |
| B7 | Keturah resolve for ASSUMES | B6 optional |
| B8 | Outcome satisfaction ≠ step completion | B6 |
| B9 | Estate STATUS note for consumers | release |

---

## 4. Phased plan (PRs)

### Phase 0 — Spec sketch only (no runtime)  
**Goal:** Land the three-layer model in SPEC without breaking existing docs.

**Deliverables**

- SPEC § (new) **Process semantic axes**  
  - Layer A = existing determinism tags  
  - Layer B = `BEHAVIOUR:` (optional, multi)  
  - Layer C = `COGNITION:` (optional, single)  
  - Explicit non-collision with PLAN INTENT / PURPOSE  
  - Progressive formality: omit = no extra contract  
- GRAMMAR.md annotations  
- Conformance: allow-list of cognition/behaviour tokens (validate if present)  
- Parser + AST fields on `Step` (or annotations)  
- Export into plan step dicts (`cognition`, `behaviour[]`, `execution` derived from tags)  
- Golden example `examples/cross-llm-critique.cairn.md` (or similar)  
- Tests  

**Out of scope for Phase 0:** enforcing output schemas at runtime.

**Acceptance:** parse/validate/export round-trip; existing examples still green;
SPEC states orthogonality.

---

### Phase 1 — Deborah-local polish (frame enforcement in *tools*)  
**Goal:** Make 0.10 framing visible and checkable without a full interpreter.

**Deliverables**

- B2 render of PLAN framing (+ cognition/behaviour when present)  
- B3 core-profile validation  
- B4 structured CALL + assumes consistency  
- B5 serialize round-trip  
- `deborah-validate --profile core|full`  

**Acceptance:** CI can gate `core` on selected examples; composer/JSON views show
framing fields.

---

### Phase 2 — Cognitive contracts (static → soft runtime)  
**Goal:** Each `COGNITION` value defines an **expected result shape** the
validator/runtime can check *when structured OUTPUT is provided*.

**Deliverables**

- Result schema sketches per cognition (JSON Schema or typed dicts in
  `deborah.contracts` or similar)  
- Soft validation: if step claims `COGNITION: infer` and provides structured
  result, require claim + evidence linkage keys  
- Confidence object shape (`evidence` / `inference` / `execution` bands or
  floats with basis — prefer bands for honesty)  
- Document process-level recursion *policy* (when interpreter may re-enter)  

**Acceptance:** fixture results validate; incomplete infer results warn/error
under strict mode.

---

### Phase 3 — Thin interpretive runtime (estate Stage 1)  
**Goal:** Enforce the frame.

**Deliverables**

- Minimal IR from PLAN (core constructs only)  
- Dispatch CALL under allow-list ∩ ASSUMES  
- Apply `ON_UNCERTAINTY`  
- Terminals: complete / open / refused / blocked  
- Optional: behaviour-guided tool choice (adversarial → critique capability)  
- Optional: cognition-triggered re-entry under MAX  
- One end-to-end slice (e.g. question → retrieve → critique → open or answer)  
- Galeed events for decisions and residuals (when available)  

**Depends on:** architecture Stage 0 (Keturah/Galeed extensions) for full slice;
can stub handlers for pure unit tests.

---

### Phase 4 — Control behaviour policies  
**Goal:** Behaviour annotations change scheduling, not just labels.

| Behaviour | Runtime policy (initial) |
|---|---|
| reactive | Subscribe/await events; cancel/redirect only via explicit AWAIT/ERROR |
| adaptive | Allow DECISION to use prior step metrics; no silent tool widening |
| exploratory | Require MAX/UNTIL; cost budget; residual open on exhaustion |
| reflective | After OUTPUT, run residual/assumption check before complete |
| adversarial | Prefer registered challenge/critique capabilities; record counter-evidence |

**Acceptance:** policy tests with stub capabilities; no unbounded loops.

---

### Phase 5 — Learn / negotiate / optimize depth  
**Goal:** Only after Phases 0–4 prove the axes.

- `learn`: explicit artifact + scope + reversibility; **no auto-apply** to shared
  memory without external gate (Tirzah evolution / human review)  
- `negotiate`: step-level contract for multi-party trade-off; wire format stays
  in negotiation protocol; crystallise to PLAN  
- `optimize`: objective + stop rule required when cognition=optimize  

---

## 5. What we explicitly defer

- Multi-role adaptive replanning on every request (Level 4)  
- Applicability profiles / exploration frontier *inside* Cairn (learning arch)  
- Numeric confidence as the only truth (false precision)  
- Replacing DETERMINISTIC/STOCHASTIC with a different word  
- Encoding full FIPA performatives in the grammar  
- Auto-promotion of `learn` outputs into operational defaults  

---

## 6. Suggested PR sequence (implementation order)

| PR | Title | Phase |
|---|---|---|
| P1 | docs: process semantic axes + roadmap (this file + SPEC draft section) | 0 |
| P2 | feat: parse/validate COGNITION + BEHAVIOUR; export on steps | 0 |
| P3 | test+example: golden cross-LLM critique plan with three layers | 0 |
| P4 | feat: render PLAN framing + cognition/behaviour | 1 |
| P5 | feat: validate_plan profile=core + assumes/CALL consistency | 1 |
| P6 | feat: deborah-validate --profile; serialize round-trip | 1 |
| P7 | feat: cognition result contracts (soft/strict) | 2 |
| P8 | feat: minimal plan interpreter + terminals + ON_UNCERTAINTY | 3 |
| P9 | feat: behaviour policies (exploratory/reflective/adversarial first) | 4 |
| P10 | feat: learn/negotiate/optimize contracts | 5 |

P1 can land immediately. P2–P6 stay inside Deborah. P8+ may touch estate
repos (Keturah, Galeed, Tirzah handlers).

---

## 7. Key decisions (summary)

| Decision | Choice | Rationale |
|---|---|---|
| Three layers | Adopt as **orthogonal** axes | Matches ChatGPT insight; prevents taxonomy soup |
| Execution layer | **Reuse** DETERMINISTIC/STOCHASTIC | Already shipped; dual vocabulary is harmful |
| Cognitive axis name | **`COGNITION:`** not `intent` | Avoid clash with PLAN INTENT / PURPOSE |
| Control axis | **`BEHAVIOUR:`** multi-value optional | Composable by design |
| When contracts bind | Only if COGNITION present (progressive) | Human-first; no forced ceremony |
| Runtime recursion | Bounded re-entry by confidence + MAX | Process-level recursion without Level 4 chaos |
| Learn | Explicit durable change + external gate | Estate evidence: ungated reuse fails |
| Priority vs runtime | Semantics in language **before** full runtime | Parse/validate first; enforce next |

---

## 8. Open questions (resolve before Phase 2+)

1. **Bands vs floats** for confidence — recommend ordinal bands first (learning
   handoff); floats only if a real decision needs them.  
2. **Where structured results live** — step OUTPUT as YAML/JSON fence vs
   runtime-only artifact map?  
3. **Default cognition** when omitted — none (no contract) vs infer from
   construct (CALL→? STEP→?) — recommend **none**.  
4. **Estate ownership of thin runtime** — `deborah.runtime` package now vs
   extract from Tirzah later — recommend stub in Deborah with adapter to Tirzah
   handlers for the first slice.  

---

## 9. Success criteria (programme-level)

Deborah has improved when:

1. Authors can declare **how / behave / why** without overloading PURPOSE.  
2. Validators catch **incoherent** combinations (e.g. `COGNITION: observe` with
   decision-only OUTPUT under strict mode).  
3. An interpreter can terminate with **open/refused** for the right cognitive
   reasons, not only crash.  
4. The language still reads human-first with axes omitted.  
5. We have not recreated a 50-construct zoo for what belongs in policy/runtime.

---

## 10. Immediate next step

**Implement Phase 0 / P1–P3:** SPEC section + parser/validator + golden example,
then Phase 1 polish — *before* building the thin runtime — so the three-layer
model is real in the document format that 0.10 already established for framing.
