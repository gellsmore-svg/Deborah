---
name: deborah
description: >
  Author, revise, validate, and render Deborah/Cairn process documents
  (.cairn.md or cairn fences) without requiring the user to know the
  language. Use when asked to fill business-process documentation, SOPs,
  requirements, design docs, agentic/LLM workflows, review gates, GRC,
  org-change; to represent code as abstract control flow (not a new
  programming language); or when the user mentions /deborah, Cairn,
  PROCESS/PLAN, deborah-validate, deborah-render, deborah-run.
metadata:
  short-description: "Deborah / Cairn process language"
---

# Deborah

You are using **Deborah** — the process language. The **document format** is
**Cairn**. Package name: `deborah`. Write `.cairn.md` (or a cairn fence) that a
human can follow on first read.

Formal tags and PLAN fields are **progressive**: narrative PROCESS first;
add tags when actors or determinism matter; add PLAN framing only when the
work will be validated or walked as an execution graph.

Normative sources (do not paraphrase into competing rules):

- `SPEC.md` — meaning
- `GRAMMAR.md` — shape
- `docs/GUIDE-AI.md` — agent contract
- `examples/` — real patterns

If this session can see a Deborah checkout, prefer those files over memory.
Typical path: `/home/cello/domains/Deborah`.

Read order: **this file** (what to do) → `references/scenarios.md` (what
shape) → `references/cairn-mini.md` (how to type it). Open SPEC/GRAMMAR only
when the mini cannot say it.

## Not this skill

| Need | Use instead |
|---|---|
| Human-factors / UI load analysis of a Cairn doc | **Huldah** |
| Capability schemas / MCP tool catalog | **Keturah** |
| Run traces / cost / LLM I/O log | **Galeed** |
| Independent multi-path reconstruction as a *method* | **multipath-reasoning** skill |
| Recursive score-stabilisation | **recursive-confidence-loop** skill |
| Implementing the described system in code | ordinary engineering |

Deborah **frames** caller↔capability work. It does **not** turn
`[LLM, STOCHASTIC]` steps into pure functions. `open` (residual recorded) is
an honest terminal, not a failure to paper over.

Name Huldah, Keturah, Galeed, or Multipath only when ASSUMES/CALL must pin
them. Do not redefine their jobs.

## Procedure

1. **Classify** using `references/scenarios.md`. Several rows may apply: one
   document may mix CONTEXT + REQUIREMENTS + PROCESS. Use PLAN only when the
   work will be validated or walked as an execution graph.
   - An existing `.cairn.md` or cairn fence in the thread → **revise in
     place**. Do not restyle or raise formality unless asked.
   - Filling business-process documentation → narrative CONTEXT +
     REQUIREMENTS + PROCESS.
   - Representing code as abstract logic → the same language; steps follow
     control flow and durability, not source order (see cairn-mini).

2. **Pick formality:**
   - narrative PROCESS (default for docs, SOPs, explanations, filled templates)
   - same PROCESS with tags (`[CODE, DETERMINISTIC]`, `[LLM, STOCHASTIC]`,
     `[HUMAN, GATED]`) when actors or determinism matter
   - PLAN with framing fields when the user wants a crystallised, versioned
     walk (strict validation or `deborah-run`)

   When in doubt, **fewer constructs** and **lower formality**.

3. **Author** following `references/cairn-mini.md`. Golden rule: a reader
   should think “I get what’s happening,” not “I need the notation.” Prefer a
   project file `*.cairn.md`; otherwise a fenced `cairn` block. COGNITION
   first tokens and `decide` → `DECISION` are in the mini.

4. **Invent no constructs.** CORE constructs for anything that must execute.
   Extension constructs (psych/org/socio, SAMPLE/VIEW) are documentation; a
   core runtime may skip them. If the grammar cannot say it, use a numbered
   STEP plus CONSTRAINTS/PURPOSE — do not mint syntax. Forbidden aliases
   live in cairn-mini.

5. **Validate** when Deborah is installed and the artefact is more than a
   sketch. Use the `deborah-validate` commands in cairn-mini. Fix grammar
   errors before presenting the doc as done. If `deborah` is not installed,
   say so and still emit well-formed Cairn. Emit plan JSON only if they asked.

6. **Render** only if the user needs an audience view:

   ```bash
   deborah-render path.cairn.md --profile operator
   # profiles: narrative_steps, simple_prose, operator, executive, audit,
   # therapeutic, change_leader, human_demand, human_factors
   ```

7. **Do not walk** a live plan (`deborah-run` / `interpret_plan`) unless the
   user asked to execute, simulate, or check contracts. Default handler is a
   stub; real capabilities need an estate/index.

## Hard constraints (GUIDE-AI)

- Do not free-replan during a crystallised interpret walk.
- Do not invent evidence for empty `observe`.
- Do not collapse leftover uncertainty into accept in order to “finish.”
- Stochastic steps stay tagged STOCHASTIC.
- `learn` must not auto-apply; `optimize` needs an explicit stop rule.
- Do not upgrade a narrative SOP into a PLAN walk unless asked to
  crystallise, validate as a graph, or execute.

## Default output

Unless the user asked only for advice, **write the Cairn document** (file
under the project if they have one, otherwise a fenced `cairn` block).
Briefly state scenario, formality, and whether it was validated.
