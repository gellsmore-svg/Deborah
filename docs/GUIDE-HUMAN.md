# Deborah — complete human guide

**Audience:** operators, authors, reviewers, product owners, and anyone who
needs every Deborah capability explained in plain language.

**Companion:** [GUIDE-AI.md](GUIDE-AI.md) (machine contracts and APIs).  
**Package:** `pip install deborah` (language SPEC and package version are
independent — see README).

---

## 1. What Deborah is

Deborah is the **process language and thin runtime** for framing multi-step and
cross-LLM work. The readable document format is still called **Cairn**
(`.cairn.md` files and ```` ```cairn ```` fences).

**It frames work.** It does **not**:

- turn stochastic model calls into pure functions,
- host free multi-agent chat loops,
- replace memory products (Tirzah), critique (Milcah), ontology (Mahalath),
  or human-factors analysis (Huldah).

**It does**:

- let you write intent, outcomes, allowed capabilities, and uncertainty policy,
- validate that a plan is well-formed,
- walk a crystallised plan under allow-lists and bounds,
- treat **open** (leave residual) as a first-class honest terminal,
- record negotiation, decisions, and open questions for review.

---

## 2. Full feature catalogue (overview)

| Area | Features |
|---|---|
| **Language / Cairn** | PROCESS & PLAN prose, constructs, tags, framing fields, COGNITION |
| **Grammar** | Parse, validate document, export AST, export machine plan |
| **Conformance** | Plan profiles full / core / strict; plan & step field contracts |
| **Cognitive contracts** | observe / infer / evaluate / decide (+ negotiate / learn / optimize) |
| **Thin runtime** | interpret_plan, terminals, GATED decide, re-entry policy |
| **Estate** | ASSUMES resolution, demo & live adapters, Keturah/Galeed hooks |
| **Substrate slice** | Negotiate → phased walk → outcomes → open questions |
| **Negotiation** | Bounded max_rounds; accept / critique / auto / post-retrieve |
| **Infer** | Rule-based reading; optional Ollama |
| **Open questions** | JSONL store; Mongo; list CLI |
| **Render** | Profiles, languages, formats, stylesheets, export |
| **Web** | Interactive composer (`deborah-serve`) |
| **CLIs** | validate, render, serve, run |
| **Interop** | Tirzah plan handoff, shared spine events, family products |
| **Examples** | Domain suites (org, psych, socio, tech, GRC, OH, …) |

---

## 3. Language features (Cairn / process description)

### 3.1 Document kinds

- **Narrative process** — human-readable steps for authoring and review.
- **Formal process** — same backbone with tags (LLM/CODE, STOCHASTIC, SYNC, …).
- **PLAN** — crystallised, versioned execution graph with framing fields.

### 3.2 PLAN framing fields (what you fill in)

| Field | Meaning for you |
|---|---|
| **REQUEST** | The question or job this revision answers |
| **INTENT** | Why this work exists |
| **OUTCOMES** | What “done well enough” looks like |
| **ASSUMES** | Allowed capabilities, often version-pinned (`milcah.critique@1`) |
| **ON_UNCERTAINTY** | `record` / `escalate` / `abort` when residual remains |
| **REEVALUATE_WHEN** | Conditions that should force a new REVISION |
| **EXPLORATION_BUDGET** | Usually `0`; only with host re-entry can a step retry once |
| **REFLECTIVE_PASS** | Flag low-confidence inference as residual (policy, not a step type) |
| **REVISION** / **STATUS** | Version and lifecycle of the plan |
| **REVISION_DECISION** | revise / stable / complete / blocked / open / refused |

### 3.3 Step constructs (what a step *is*)

**Core (execution-normative — the runtime must understand these):**

STEP, CALL, ITERATE, DECISION, RECURSE, QUEUE, PARALLEL, MERGE, SERVICE,
RETRY, AWAIT, BREAK, CONTINUE, MILESTONE, ERROR

**Extension (human-systems / domain documentation; thin runtime may skip):**

REGULATION, APPRAISAL, DUAL_PROCESS, METACOGNITION, ALIGN, COALITION,
RESISTANCE, REINFORCEMENT, CASCADE, VISION, SOCIALIZE, INSTITUTIONALIZE,
SYMBOLIC_INTERACTION, CONFLICT, ACCOMMODATE, ASSIMILATE, ROLE, FEEDBACK, MACRO,
SAMPLE, VIEW

`SAMPLE` describes several isolated attempts at the same problem (they must not
read each other). `VIEW` describes what a later attempt is allowed to see.
`MERGE [RULE: admissibility]` means “keep constraints and open questions,” not
“pick a winner.”

### 3.4 Tags and modifiers (common)

Used in formal style and prose:

- **Actor / medium:** HUMAN, LLM, CODE, ASSISTED-BY  
- **Determinism:** DETERMINISTIC, STOCHASTIC  
- **Sync:** SYNC, ASYNC  
- **Gate:** GATED (human or host must inject a decision)  
- Domain tags in examples (CULTURAL, EVENT, …) per suite  

### 3.5 COGNITION (what a step *owes* when done)

| Cognition | Plain meaning |
|---|---|
| **observe** | Produce evidence items with sources (empty set allowed if explicit) |
| **infer** | Form a claim/reading from evidence; list gaps and assumptions |
| **evaluate** | Score or critique against criteria; list objections |
| **decide** | Select accept / reject / open (use construct **DECISION** when human-owned) |
| **negotiate** | Bounded agreement process; may stay unresolved |
| **learn** | Propose a durable change (must not auto-apply without approval) |
| **optimize** | Search under an explicit stop rule |

**Reflect is not a cognition** — use plan policy `REFLECTIVE_PASS`.

### 3.6 Terminals (how a run can end)

| Terminal | Meaning |
|---|---|
| **complete** | Walk finished under bounds |
| **open** | Residual left explicit (honest incomplete) |
| **refused** | Capability or negotiation refused |
| **blocked** | Invalid plan, allow-list fail, empty steps, hard bound |

**Open is success for honesty**, not a crash.

---

## 4. Grammar & validation features

### 4.1 What the grammar package does

- **Parse** `.cairn.md` / Cairn fences into a document structure  
- **Validate document** well-formedness against grammar rules  
- **Export AST** (`document_to_dict`) for tooling  
- **Export plan** (`document_to_plan`) for the runtime  
- **Extract** Cairn source from larger markdown  

### 4.2 Plan conformance profiles

| Profile | What it checks |
|---|---|
| **full** (default) | Required plan/step fields, constructs, statuses, cognition names |
| **core** | Like full, plus **rejects extension constructs** |
| **strict** | Like full, plus: cognition needs output/success_criteria; CALL tools should match ASSUMES; **`decide` must use construct DECISION** |

### 4.3 CLI: `deborah-validate`

```bash
deborah-validate plan.cairn.md
deborah-validate plan.cairn.md --profile strict
deborah-validate plan.cairn.md --strict          # non-zero exit + strict plan profile
deborah-validate plan.cairn.md --export-plan     # machine plan JSON
deborah-validate plan.cairn.md --export-ast      # AST JSON
deborah-validate plan.cairn.md --json            # machine-readable report
deborah-validate plan.cairn.md --results results.json --results-mode soft|strict
```

`--results` checks cognitive **result** contracts against exported steps.

---

## 5. Cognitive result contracts (quality of step outputs)

When a step has COGNITION, its result can be checked:

| Mode | Behaviour |
|---|---|
| **soft** | Check shape of fields that are present |
| **strict** | Required keys must exist; safety gates enforced |

**Confidence** uses bands on three dimensions — **not** a single float as
system of record:

- dimensions: **evidence**, **inference**, **execution**  
- bands: **high** | **medium** | **low** | **unassessed**  
- optional **basis** string  

Strict gates (summary):

- **negotiate** — no forced agreement  
- **learn** — auto-apply needs approval / human gate  
- **optimize** — needs a stop rule  

Built-in demo result fixtures exist for testing (`EXAMPLE_RESULTS`).

---

## 6. Thin runtime features

### 6.1 What the thin interpreter does

`deborah-run` / `interpret_plan`:

1. Optionally validate the plan  
2. Resolve allow-list from ASSUMES (or explicit set)  
3. Walk steps in dependency order (`depends_on`)  
4. Dispatch each step to a **handler** (stub, demo, or live estate)  
5. Optionally check result contracts  
6. Stop with complete / open / refused / blocked  
7. Respect hard **max_steps**  

**No free re-planning** of the step graph during the walk.

### 6.2 Handlers

| Handler | Role |
|---|---|
| **StubHandler** | Completes core steps; optional canned results by id or cognition |
| **EstateHandler** | Routes CALL tools and cognition to a dispatch map + capability index |
| **Custom** | Any injectable callable `(step, context) → result` |

### 6.3 GATED / HUMAN decisions

- DECISION steps marked gated wait for a **selected** verdict.  
- Without a decision: status **awaiting_decision** (does not invent accept).  
- Inject via CLI `--decision accept|reject|open` or API `decisions={step_id: …, "default": …}`.

### 6.4 Re-entry and reflective pass (Phase F)

| Feature | Default | Meaning |
|---|---|---|
| **allow_reentry** | off | If on **and** plan `exploration_budget > 0`, at most **one** re-dispatch of a low-confidence infer/evaluate step |
| **reflective_pass** | off unless plan/flag | Mark residual when inference confidence is low/unassessed |

These never open free agent loops.

### 6.5 Initial artifacts

Later phases of a split plan can receive **pre-seeded artifacts** from earlier
steps (used by the post-retrieve mid-slice path).

### 6.6 CLI: `deborah-run` (non-slice)

```bash
deborah-run plan.cairn.md
deborah-run plan.json --profile full
deborah-run plan.cairn.md --no-validate
deborah-run plan.cairn.md --check-contracts --contract-mode soft
deborah-run plan.cairn.md --demo-results
deborah-run plan.cairn.md --results results.json
deborah-run plan.cairn.md --estate-demo --check-contracts
deborah-run plan.cairn.md --estate-live --trace
deborah-run plan.cairn.md --max-steps 20
deborah-run plan.cairn.md --allow-reentry --reflective-pass
deborah-run plan.cairn.md --decision open
deborah-run plan.cairn.md --question "Override the request text"
deborah-run plan.cairn.md --json
```

---

## 7. Estate features (capabilities around the plan)

### 7.1 ASSUMES resolution

- **DictCapabilityIndex** — in-process name → metadata  
- Optional **Keturah** registry when installed  
- Unresolved assumes can **block** the run when required  

### 7.2 Demo estate (`--estate-demo`)

In-process stubs for:

- retrieve / observe  
- critique / evaluate  
- rule **infer**  
- novel detect (when Mahalath installed, else fail-open stub)  
- full Milcah portfolio when `milcah` is installed  

### 7.3 Live estate (`--estate-live`)

When packages/DB are available:

- **Tirzah** retrieve against Mongo  
- **Milcah** critique / intent / confidence  
- **Mahalath** novel-concept detection  
- Open questions to family Mongo (`deborah_open_questions`)  

Fail-soft: missing pieces fall back or report without hard dependency in Deborah’s
own install.

### 7.4 Trust marking

Retrieve evidence is treated as an **untrusted channel**:

- demo/live retrieve can mark `trust.level=untrusted`  
- infer records untrusted counts and assumptions  
- do not treat retrieved text as instructions to the model  

### 7.5 Tracing (Galeed)

With `--trace` and Galeed installed:

- negotiation started/finished  
- decision recorded  
- open question recorded  
- mid-slice phase events (`slice.phase.*`)  
- full run events via run recorder  

Browse in **Mizpah** (Phases / Negotiation / Decisions / Open Q filters).

---

## 8. Substrate slice (full vertical path)

The Stage-1 path for “answer a grounded question or leave open.”

### 8.1 Pipeline

1. Optional **pre-negotiate** (bounded rounds)  
2. **Split** at first critique CALL (when post-retrieve gate on)  
3. **Pre phase:** novel → retrieve → infer  
4. **Post-retrieve negotiate:** evidence count / novel terms  
5. **Post phase:** critique → validate intent → assess confidence → decide  
6. **Outcomes check** (evidence + confidence floor)  
7. **Open question** if residual  
8. **Galeed** decision/negotiation/phase events when tracing  

### 8.2 Negotiation features

| Negotiator | Behaviour |
|---|---|
| **accept** | One-shot accept (skip content gate) |
| **critique** | Deterministic clarify / refuse / accept for milcah.critique (underspecified claim, out of scope) |
| **auto** | critique if ASSUMES mention milcah/critique/coherence; else accept |
| **post_retrieve** | After evidence: partial if novel or zero evidence; else accept |

`max_rounds=0` skips the pre-loop and treats as agreed. Exhaustion → **unresolved** → open path.

### 8.3 Outcomes check

- Require cited evidence when configured  
- Enforce **confidence floor** (high / medium / low) on inference band  
- Collect open reasons for the residual record  

### 8.4 Open questions

| Storage | How |
|---|---|
| **JSONL** | `--open-questions PATH` |
| **Mongo** | `--open-questions-mongo` / live estate (`deborah_open_questions`) |
| **List** | `deborah-run --list-open-questions PATH [--plan-id ID] [--json]` |

Each record includes question text, reason, plan id, run terminal, id, timestamp.

### 8.5 CLI: slice flags

```bash
deborah-run examples/answer-substrate-question.cairn.md \
  --slice --estate-demo --check-contracts \
  --negotiator auto \
  --max-rounds 4 \
  --confidence-floor low \
  --question "…" \
  --open-questions ./open.jsonl \
  --decision open \
  --trace

# Skip pre-negotiate or mid-gate
deborah-run … --slice --no-negotiate
deborah-run … --slice --no-post-retrieve-negotiate

# Live
deborah-run … --slice --estate-live --open-questions-mongo --llm-infer
```

Text summary prints: terminal, outcomes_ok, negotiation, **post_retrieve**,
steps, open reasons, open_question id.

---

## 9. Infer feature

- **Rule-based** default: restates claim, counts evidence, lists gaps, untrusted
  and novel assumptions, confidence bands  
- **`--llm-infer`:** optional Ollama when reachable; falls back if not  
- Injected into demo/live dispatch automatically on the slice  

---

## 10. Render & export features

### 10.1 Profiles (simplified views)

Registered profiles include (among others used in examples/docs):

- `narrative_steps` / `narrative` — story-style steps  
- `operator` — operator-facing  
- `therapeutic` — psychological / regulation focus  
- `change_leader` — organisational change  
- `human_demand` — load, support, trust  
- `human_factors` — cognitive/social/org risks  

(See `deborah-render --help` / `registered_profiles()` for the live list.)

### 10.2 Languages

- **en**, **es**, **fr** phrasing for many labels  

### 10.3 Formats

| Format | Notes |
|---|---|
| markdown, text, json, mermaid, html | Core |
| docx, pdf | Require `pip install 'deborah[export]'` |

### 10.4 Options

- `--boxed` card layout  
- `--include-tags`  
- `--max-depth`  
- `--sections` (context, requirements, outcomes, plan, process)  
- `--stylesheet` YAML/JSON  
- `--lenient` fallback heuristic parse with warning  

### 10.5 CLI: `deborah-render`

```bash
deborah-render plan.cairn.md -p narrative_steps
deborah-render plan.cairn.md -p operator -l en -f markdown
deborah-render plan.cairn.md -f html -o view.html
deborah-render plan.cairn.md -f pdf -o plan.pdf   # [export]
deborah-render plan.cairn.md --stylesheet path.yaml
```

Programmatic: `render_plan`, `export_view`, `register_exporter`.

---

## 11. Web composer

```bash
pip install 'deborah[web]'
deborah-serve                 # default 127.0.0.1:8795
deborah-serve --port 8795 --host 127.0.0.1
```

Interactive transformation-view composer (local; no auth — keep on localhost).

---

## 12. Family integration (what Deborah connects to)

| Product | Role relative to Deborah |
|---|---|
| **Tirzah** | Memory/retrieve; agentic plan invent/revise; can **hand off** framed critique plans to Deborah (≥1.15) |
| **Milcah** | Critique, intent alignment, confidence aggregate |
| **Mahalath** | Novel-concept / ontology terms |
| **Keturah** | Capability manifests / MCP pins for ASSUMES |
| **Galeed** | Trace spine (negotiation, decision, OQ, phases) |
| **Mizpah** | Browse sessions; filter Phases / Negotiation / Decisions / Open Q |
| **Huldah** | Human-factors / UI analysis of the same Cairn docs (separate package) |
| **Hoglah** | Queue/LLM transport used by siblings (not owned by Deborah) |

Ownership detail: [PLAN-OWNERSHIP.md](PLAN-OWNERSHIP.md).

---

## 13. Example library (what ships)

Under `examples/` (non-exhaustive):

- **Substrate:** `answer-substrate-question.cairn.md`  
- **Golden critique:** `cross-llm-critique.cairn.md`  
- **Family pins:** `tirzah*.cairn.md`, `milcah.cairn.md`, `mahalath.cairn.md`, `keturah.cairn.md`, `galeed.cairn.md`, `hoglah*.cairn.md`, `mizpah.cairn.md`  
- **Org change:** Kotter, Lewin, ADKAR, McKinsey 7S, stakeholder, culture  
- **Psychological:** attachment, dissonance, dual-process, emotion regulation, metacognition, operant, SDT  
- **Sociological:** conflict, norms, movements, socialization, symbolic interaction  
- **Suites:** corporate lifecycle, AI-native change, GRC, occupational health, technical-agentic, human-systems maps  

Use them as templates; validate with `deborah-validate`.

---

## 14. Install matrix

```bash
pip install deborah                 # core (stdlib only)
pip install 'deborah[render]'       # YAML stylesheets
pip install 'deborah[web]'          # deborah-serve
pip install 'deborah[export]'       # docx + pdf
```

Optional siblings for live estate: `tirzah`, `milcah`, `mahalath`, `galeed`, `keturah`.

---

## 15. What “good” looks like for humans

1. Intent and outcomes a stranger could grade.  
2. ASSUMES name real, pinned capabilities.  
3. Empty evidence is allowed and explicit.  
4. Human commits use DECISION + GATED.  
5. Prefer **open** over false polish.  
6. New REVISION when the process changes — not silent mid-run edits.  
7. Review Galeed/Mizpah when auditing why a verdict was chosen.  

---

## 16. Common confusions

| Confusion | Fact |
|---|---|
| Deborah = deterministic AI | No — frames stochastic steps |
| Open = failure | No — first-class residual |
| Negotiation = free debate | No — bounded protocol |
| Cairn vs Deborah | Cairn = format; Deborah = product/package |
| Tirzah replaced by Deborah | No — Tirzah invents/retrieves; Deborah frames crystallised walks |
| Reflect is a step type | No — plan policy |

---

## 17. Where to go next

| Need | Document |
|---|---|
| Normative language | [SPEC.md](../SPEC.md), [GRAMMAR.md](../GRAMMAR.md) |
| AI / API detail | [GUIDE-AI.md](GUIDE-AI.md) |
| Tirzah handoff | [PLAN-OWNERSHIP.md](PLAN-OWNERSHIP.md) |
| Cognition taxonomy | [TAXONOMY-COGNITION-AND-PATTERNS.md](TAXONOMY-COGNITION-AND-PATTERNS.md) |
| Roadmap history | [PROCESS-SEMANTICS-AND-ROADMAP.md](PROCESS-SEMANTICS-AND-ROADMAP.md) |
| Usage modes | [usage-modes.md](usage-modes.md) |
| Render deep dive | [VIEW-GENERATOR.md](VIEW-GENERATOR.md) |
| Grammar API | [GRAMMAR-PARSER.md](GRAMMAR-PARSER.md) |
| Migration from cairn | [MIGRATING.md](../MIGRATING.md) |
