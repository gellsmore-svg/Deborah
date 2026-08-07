# COGNITION taxonomy: primitives vs higher-order patterns

**Date:** 2026-08-07 · **Status:** decision (post Phase F / package ≥0.15)
**Audience:** SPEC authors, ChatGPT process-semantics reviews, estate integrators

---

## Question

Should Deborah's taxonomy primitives include **optimise, negotiate, learn,
reflect** as first-class `COGNITION` values, or can those be expressed only as
higher-order patterns over observe / infer / evaluate / decide?

---

## Decision (this stage)

| Name | Role | In language as |
|---|---|---|
| **observe, infer, evaluate, decide** | Core **product** primitives | `COGNITION` MVP — always |
| **negotiate, learn, optimize** | Extended **product** contracts (gated) | `COGNITION` extended — Phase F |
| **reflect** | Plan/runtime **policy**, not a product type | `REFLECTIVE_PASS` + residual path — **not** a COGNITION |
| Multi-round negotiation / search / re-entry | **Control** patterns | Constructs + bounds (`MAX`, `EXPLORATION_BUDGET`, protocol `max_rounds`) |

**Short answer for ChatGPT:** keep negotiate / learn / optimize as *named product
contracts* (they already ship with gates). Do **not** add **reflect** as a
cognition — it is a higher-order check over infer/evaluate. Multi-round
behaviour is expressed as control patterns (ITERATE / protocol / budget), not as
extra product kinds.

---

## Why not collapse everything to four?

The four MVP cognitions are **single-step product shapes**: what one step owes
when it completes.

| Cognition | Product (strict) | Gate |
|---|---|---|
| observe | `evidence[]` with provenance | empty set must be explicit |
| infer | claim + evidence_refs (+ assumptions/gaps) | — |
| evaluate | criteria (+ scores/objections) | — |
| decide | `selected` | open is first-class residual |

Negotiate / learn / optimize are still **products** (structured results a step
can return), but with **different social and safety contracts**:

- **negotiate** — may remain unresolved; `force_agreement` forbidden  
- **learn** — `auto_apply` requires `approved` / `human_gate`  
- **optimize** — requires a `stop_rule` (search is not unbounded)

If we *only* composed them as “patterns of the four,” we would lose:

1. **Enforceable shape** — soft/strict contracts cannot check a free-form
   “pattern” without a named product type.
2. **Gates** — learning and agreement pressure must fail closed in the contract
   layer, not only in prose PURPOSE lines.
3. **Discovery** — Keturah/ASSUMES and CALL steps need a stable label for “this
   step’s product is a negotiation status,” not a multi-step script.

So they are **not** control primitives (that would re-introduce behaviour
multi-select). They **are** optional product labels on steps that *perform*
those acts, while the *loop* around them stays in constructs and plan policy.

## Why reflect is different

**Reflect** does not introduce a new *artifact type*. It means:

> after infer/evaluate, if inference confidence is low/unassessed (or missing),
> mark residual / prefer open — and optionally re-enter once under budget.

That is already:

- PLAN field `REFLECTIVE_PASS`
- interpreter flag `reflective_pass`
- residual / `ON_UNCERTAINTY` / `open` terminal

Encoding reflect as `COGNITION: reflect` would dual-describe the same policy and
invite authors to put “reflection” mid-plan without a product contract. Prefer
**pattern over product**.

## Higher-order patterns (how to author them)

| Intent | Pattern (not a new cognition) |
|---|---|
| Multi-round negotiation | Bounded protocol (`max_rounds`) → crystallise → CALL with `COGNITION: negotiate` or evaluate |
| Learning from a run | REVISION or new PLAN; step with `COGNITION: learn` only when a durable change artifact is intended |
| Optimize candidates | `ITERATE`/`RECURSE` with MAX + step `COGNITION: optimize` + `stop_rule` in the result |
| Reflect | `REFLECTIVE_PASS` + confidence bands on infer/evaluate; optional `EXPLORATION_BUDGET` + `allow_reentry` |
| “I don’t know” | terminal `open` + open-questions store (substrate slice) |

## Progressive disclosure (unchanged)

1. Omit `COGNITION` → no product contract.  
2. MVP four → ordinary cross-LLM work.  
3. Extended three → only when the result shape and gates matter.  
4. Reflect / budget / re-entry → plan flags and interpreter opts, default off.

## Non-goals

- Seven cognitions as a peer multi-select *behaviour* layer  
- Hot-path free re-planning under the name “optimize” or “learn”  
- Learning store inside Deborah  
- Making reflect a step product so every plan must “reflect” as a step

---

## Summary one-liner

**Product taxonomy:** four core + three gated extensions.  
**Control taxonomy:** constructs + plan policy.  
**Reflect:** policy pattern over the four, not an eighth cognition.
