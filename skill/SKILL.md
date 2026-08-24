---
name: deborah
description: >
  Author, revise, validate, and render Deborah/Cairn process documents
  (.cairn.md) without requiring the user to know the language. Use when
  asked to write business processes, SOPs, requirements, design docs,
  agentic/LLM workflows, review gates, GRC, org-change, or to represent
  code as abstract control flow; also for /deborah, Cairn, PROCESS/PLAN,
  deborah-validate, deborah-render, deborah-run.
metadata:
  short-description: "Deborah / Cairn process language"
---

# Deborah

You are using **Deborah** — the process language (document format: **Cairn**).
Write `.cairn.md` (or ` ```cairn ` fences) that a human can follow on first
read. Formal tags and PLAN fields are progressive: add them only where
validation, execution, or audit needs them.

Normative sources (do not paraphrase into competing rules):

- `SPEC.md` — meaning
- `GRAMMAR.md` — shape
- `docs/GUIDE-AI.md` — agent contract
- `examples/` — real patterns

If this session can see a Deborah checkout, prefer those files over memory.
Typical path: `/home/cello/domains/Deborah`. Skill extras:
`references/scenarios.md` (what to write) and `references/cairn-mini.md`
(how to write it).

## Not this skill

| Need | Use instead |
|---|---|
| Human-factors / UI load analysis of a Cairn doc | **Huldah** |
| Capability schemas / MCP tool catalog | **Keturah** |
| Run traces / cost / LLM I/O log | **Galeed** |
| Independent multi-path reconstruction as a *method* | **multipath-reasoning** skill |
| Recursive score-stabilisation | **recursive-confidence-loop** skill |
| Implementing the described system in code | ordinary engineering |

Deborah **frames** caller↔capability work. It does **not** turn `[LLM, STOCHASTIC]`
steps into pure functions. `open` (residual recorded) is an honest terminal,
not a failure to paper over.

## Procedure

1. **Classify** the request using `references/scenarios.md`. If several apply,
   one document may mix CONTEXT + REQUIREMENTS + PROCESS; use PLAN only when
   the work will be validated/walked as an execution graph.
2. **Pick formality:**
   - narrative PROCESS (default for docs, SOPs, explanations)
   - same PROCESS with tags (`[CODE, DETERMINISTIC]`, `[LLM, STOCHASTIC]`,
     `[HUMAN, GATED]`) when actors or determinism matter
   - PLAN with framing fields when the user wants a crystallised, versioned
     walk (`deborah-validate --profile strict`, `deborah-run`)
3. **Author** a `.cairn.md` following `references/cairn-mini.md`. Golden rule:
   a reader should think “I get what’s happening,” not “I need the notation.”
4. **Invent no constructs.** Use CORE constructs for anything that must
   execute. Extension constructs (psych/org/socio, SAMPLE/VIEW) are
   documentation; a core runtime may skip them. If the grammar cannot say
   it, use a numbered STEP plus CONSTRAINTS/PURPOSE — do not mint syntax.
5. **Validate** when Deborah is installed and the artefact is more than a
   sketch:

   ```bash
   deborah-validate path.cairn.md --strict
   # PLAN meant for a walker:
   deborah-validate path.cairn.md --profile strict --export-plan
   ```

   Fix grammar errors before presenting the doc as done. If `deborah` is not
   installed, say so and still emit well-formed Cairn.
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
- `COGNITION` first token is one of: observe, infer, evaluate, decide,
  negotiate, learn, optimize — not free prose.
- `decide` as a product contract uses construct **DECISION**.
- `learn` must not auto-apply; `optimize` needs an explicit stop rule.
- Do not collapse leftover uncertainty into accept in order to “finish.”
- `ON_UNCERTAINTY` is `record` | `escalate` | `abort`.
- Stochastic steps stay tagged STOCHASTIC.

## Default output

Unless the user asked only for advice, **write the Cairn document** (file
under the project if they have one, otherwise a fenced `cairn` block).
Briefly state scenario, formality, and whether it was validated.

## Sibling products

Name them only when the document’s ASSUMES/CALL surface needs them. Do not
redefine their jobs. Deborah does not own Multipath; SAMPLE/VIEW/MERGE
`admissibility` *describe* isolated reconstruction, they do not run that skill.
