# Deborah — human guide

**Audience:** operators, authors, reviewers, and product owners who need a
clear process frame around multi-step or multi-LLM work — without becoming
runtime engineers.

**What this is not:** a tutorial on training models, or a claim that AI steps
become deterministic. Stochastic steps stay stochastic; Deborah constrains the
*frame* around them.

---

## In one paragraph

Deborah is a **process language** (the document format is still called **Cairn**)
for saying: what we intend, which capabilities may run, what “done” looks like,
and what to do when evidence is thin or the model is uncertain. You write or
review a plan; a thin runtime walks it under those bounds. Residual uncertainty
is first-class: the honest answer is often **open**, not a forced accept.

---

## Why it exists

Cross-LLM work fails when:

- tools are called without a stated intent or outcome,
- empty evidence is papered over as success,
- the system invents a terminal “yes” because stopping is awkward,
- nobody can see *why* accept / reject / open was chosen.

Deborah makes those choices **visible and reviewable** in a human-readable
`.cairn.md` plan, then optionally **runs** that plan under allow-lists and
bounds.

---

## Core ideas (plain language)

| Idea | Meaning for you |
|---|---|
| **Frame, don’t free-loop** | The control graph is fixed once crystallised. No silent re-planning mid-run. |
| **Intent & outcomes** | Why this work exists and what “good enough” looks like. |
| **ASSUMES** | Which capabilities are allowed (e.g. retrieve, critique), often version-pinned. |
| **ON_UNCERTAINTY** | Prefer record / escalate / abort — not invent. |
| **COGNITION products** | What a step *owes* when it finishes: evidence (observe), a reading (infer), scores (evaluate), a commit (decide). |
| **Open is valid** | Leaving a question open is a success mode for honesty, not a crash. |
| **GATED decide** | Final accept / reject / open is often human-owned (or explicitly injected). |

---

## The document you work with

Files use the **Cairn** format (usually `*.cairn.md`). A plan typically has:

- **CONTEXT** — who is calling, what capabilities exist  
- **OUTCOMES** — what “done” means  
- **PLAN** — ordered steps with purpose, constraints, and optional `COGNITION`

Example (abbreviated):

```text
PLAN plan_answer_substrate_question REVISION 1 [STATUS: draft]
  REQUEST: Is relational substrate coherence well-supported by the local corpus?
  INTENT: Ground a claim in evidence and critique, or leave open
  ON_UNCERTAINTY: record
  ASSUMES: tirzah.retrieve@1, milcah.critique@1, …
  …
  PROCESS AnswerSubstrateQuestion
    1. CALL … detect novel concepts
    2. STEP — retrieve evidence
    3. STEP — form a provisional reading
    4. CALL … critique
    5–6. intent / confidence checks
    7. DECISION — accept | reject | open  [GATED]
```

Full example: [`examples/answer-substrate-question.cairn.md`](../examples/answer-substrate-question.cairn.md).

---

## What you can do day-to-day

### 1. Install and validate

```bash
pip install deborah
deborah-validate path/to/plan.cairn.md
deborah-validate path/to/plan.cairn.md --profile strict   # tighter checks
```

### 2. Read a friendlier view

```bash
deborah-render plan.cairn.md --profile narrative_steps
deborah-render plan.cairn.md --profile operator
```

### 3. Run a framed path (demo estate)

No Mongo required for a smoke run:

```bash
deborah-run examples/answer-substrate-question.cairn.md \
  --slice --estate-demo --check-contracts --negotiator accept
```

Commit a human decision when the decide step is gated:

```bash
deborah-run examples/answer-substrate-question.cairn.md \
  --slice --estate-demo --decision open --negotiator accept
```

### 4. Inspect open questions

Residual runs can write JSONL:

```bash
deborah-run … --slice --open-questions ./open.jsonl
deborah-run --list-open-questions ./open.jsonl
```

### 5. Live estate (optional)

When Tirzah Mongo / Milcah / family tools are up:

```bash
deborah-run examples/answer-substrate-question.cairn.md \
  --slice --estate-live --open-questions-mongo --decision open --trace
```

`--trace` records negotiation, decisions, and phase events for the **Mizpah**
log browser (Galeed spine).

---

## How a “substrate” run feels end-to-end

1. **Pre-negotiate** — bounded check that the claim is in scope (not free chat).  
2. **Novel / retrieve / infer** — gather and form a reading.  
3. **Post-retrieve gate** — empty evidence or novel terms are flagged (still no re-plan).  
4. **Critique → intent → confidence** — pressure-test the reading.  
5. **Decide** — accept, reject, or **open**.  
6. **Open question** — if residual, a durable record (JSONL and/or Mongo).

You should be able to answer: *What was intended? What ran? Why open?*

---

## Who owns what (family picture)

| Concern | Product |
|---|---|
| Process language, contracts, thin framed walk | **Deborah** (this package) |
| Memory, retrieval, agentic plan invent/revise | **Tirzah** |
| Critique / intent / confidence scores | **Milcah** |
| Novel / ontology terms | **Mahalath** |
| Capability registry / MCP manifests | **Keturah** |
| Trace events (negotiation, decision, phases) | **Galeed** |
| Browse sessions / filter events | **Mizpah** |
| Human-factors analysis of plans | **Huldah** |

Tirzah may **hand off** crystallised critique plans to Deborah’s framed path
so you get the same residual and spine behaviour whether you started from
`deborah-run` or a Tirzah session.

---

## What “good” looks like as a human author

- Intent and outcomes are specific enough that a stranger could grade the run.  
- ASSUMES lists real capabilities, not vague “use AI”.  
- Observe steps allow **empty evidence** to be explicit.  
- Decide steps use construct **DECISION** when a human must commit.  
- Prefer **open** over a polished false accept.  
- Version the plan when the process changes (REVISION), not by silent edit mid-run.

---

## Common confusions

| Confusion | Clarification |
|---|---|
| “Deborah makes models deterministic.” | No. It bounds tools, steps, and terminals. |
| “Open means failure.” | Open is a first-class residual terminal. |
| “Negotiation is free multi-agent chat.” | It is a **bounded** control protocol (`max_rounds`). |
| “Tirzah and Deborah both plan freely.” | Tirzah may invent/revise; Deborah walks **crystallised** graphs. |
| “Cairn vs Deborah.” | Cairn = format; Deborah = package / product name after the split. |

---

## Where to go next

| Need | Doc / path |
|---|---|
| Normative language rules | [SPEC.md](../SPEC.md) |
| AI-oriented contracts & APIs | [GUIDE-AI.md](GUIDE-AI.md) |
| Tirzah vs Deborah ownership | [PLAN-OWNERSHIP.md](PLAN-OWNERSHIP.md) |
| Cognition vs patterns | [TAXONOMY-COGNITION-AND-PATTERNS.md](TAXONOMY-COGNITION-AND-PATTERNS.md) |
| CLI / library modes | [usage-modes.md](usage-modes.md) |
| Examples | [examples/](../examples/) |

---

## Install reminder

```bash
pip install deborah
# optional: pip install 'deborah[render]' 'deborah[web]' 'deborah[export]'
```

Package version evolves independently of the language SPEC version (see README).
