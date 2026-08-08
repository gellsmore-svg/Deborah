# Plan ownership: Deborah thin interpreter vs Tirzah recursive planner

**Date:** 2026-08-07 · **Status:** decision · Package ≥ **0.23.0**

Two products emit and walk **the same PLAN dict contract**
(`deborah.validate_plan` / `REQUIRED_PLAN_FIELDS`). They are **not** competing
runtimes — ownership is split by role.

---

## Who owns what

| Concern | Owner | Does **not** own |
|---|---|---|
| Language, conformance, cognitive contracts | **Deborah** | Free-form agent loops, durable memory |
| Crystallised PLAN walk under allow-lists / bounds | **Deborah** thin runtime (`interpret_plan`, substrate slice) | Revision search, web/memory retrieval policy |
| Agentic *authoring* and revision of plans | **Tirzah** recursive planner (`create_initial_plan`, `fallback_plan`, RECURSE) | Deborah grammar evolution |
| Shared PLAN JSON shape | **Both** (Deborah is the schema authority) | Local dialects — Tirzah must stay `validate_plan`-clean |
| Estate retrieve product | **Tirzah** (`tirzah.deborah` adapters) | Control graph structure |
| Critique / intent / confidence products | **Milcah** | Negotiation bounds (Deborah control) |
| Novel-concept evaluate | **Mahalath** | Plan crystallisation |
| Trace / decision / negotiation events | **Galeed** | Plan content |

---

## Dual-planner rule

1. **Tirzah may invent steps** (LLM planner + bounded fallback) and must emit
   plans that pass `deborah.validate_plan(profile="full")`.
2. **Deborah may only walk crystallised plans** — no free re-planning mid-run.
   Post-retrieve negotiation (0.23+) re-enters only as a *gate*, not a graph edit.
3. A Tirzah `fallback_plan` is a valid Deborah input (see
   `tests/fixtures/tirzah_fallback_plan.json` and
   `tests/test_plan_interop.py`).
4. When both are present in one process: Tirzah *produces*, Deborah *frames and
   interprets*. Outcome residual / open questions remain Deborah + Galeed.

---

## Practical seams

```text
operator / LLM
    → Tirzah plan (or human .cairn.md)
    → deborah.validate_plan
    → deborah.runtime.run_substrate_slice / interpret_plan
         ASSUMES → Keturah pins
         CALL observe  → tirzah.retrieve
         CALL evaluate → milcah.* / mahalath.*
         STEP infer    → deborah.infer
         DECISION      → GATED (human / injected)
    → Galeed events + optional open_questions store
```

Interop tests live on **both** sides:

- Tirzah: `test_tirzah_plan_conforms_to_deborah_grammar`, `test_deborah_bridge.py`
- Deborah: `test_plan_interop.py` (frozen fixture + optional live import)

### Runtime handoff (Tirzah ≥1.15)

```text
tirzah.planning.deborah_bridge
  to_deborah_plan / validate_against_deborah   # Phase A seal
  is_framed_substrate_plan                     # auto-detect critique graphs
  run_framed_plan → deborah.runtime.run_substrate_slice
  compose_estate_dispatch                      # tirzah+milcah+mahalath+infer
```

Config (Tirzah `RuntimeConfig`):

- `plan_framed_execution_enabled` (default true) — route framed plans to Deborah
- `plan_require_deborah_conformance` (default false) — soft errors vs hard fail
- `plan_deborah_validate_profile` (default `full`)

Env: `TIRZAH_PLAN_FRAMED_EXECUTION_ENABLED`, `TIRZAH_PLAN_REQUIRE_DEBORAH_CONFORMANCE`.

---

## Non-goals

- Deborah will not grow an agentic revision loop (that stays Tirzah RECURSE).
- Tirzah will not redefine PLAN constructs outside Deborah CORE/EXTENSION sets.
- “Which planner wins” is not a runtime election — **call path** chooses:
  authoring/revision → Tirzah; framed execution → Deborah.
