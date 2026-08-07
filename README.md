# Deborah

Deborah is a human-readable process language for **framing cross-LLM work** —
how LLM *callers* interact with LLM-consumed *capabilities* (versioned tools,
services, and roles), with intent, outcomes, bounds, and residual uncertainty
made explicit.

It is **not** a device for turning stochastic model steps into pure functions.
Stochastic steps stay stochastic; Deborah constrains the *frame* around them
(which capabilities may run, under what bounds, when to stop, open, or refuse).

> **Renamed from Cairn (v0.9).** The package `cairn` was split into **Deborah**
> (this repo — the process language) and **[Huldah](https://github.com/gellsmore-svg/Huldah)**
> (human-systems analysis: human factors, UI evidence, layout load, live
> observation). The *document format keeps the Cairn name* — your `.cairn.md`
> files and ```` ```cairn ```` fences are unchanged. See
> [MIGRATING.md](MIGRATING.md).

It gives humans and AI systems a shared way to describe, crystallise, interpret,
and review complex work across technical, psychological, organisational, and
sociological dimensions — including iteration, recursion, non-determinism,
sync/async, queuing, outcome review, error handling, and human context.

**The specification lives in [SPEC.md](SPEC.md) (v0.12).**

Install: `pip install deborah` — import `deborah`. (The old `cairn-lang`
distribution now installs a compatibility shim that re-exports from here.)

Optional extras:
- `pip install 'deborah[render]'` — YAML stylesheets
- `pip install 'deborah[web]'` — `deborah-serve` interactive composer
- `pip install 'deborah[export]'` — HTML / DOCX / PDF export (python-docx + fpdf2)

## What it looks like

A small slice, in the readable **Narrative** style:

```
PROCESS — Answer a question from local memory.
  1. Gather context with read-only tools (search, then compile the surrounding nodes).
  2. The model writes the answer using only what was gathered — no invented sources.
  3. Save the exchange so the next turn can resume.
```

The same step in the precise **Formal** style (same backbone, with tags +
traceability):

```
2. Generate the answer from gathered_context.  [LLM, STOCHASTIC, SYNC] [SATISFIES: R1]
   CONSTRAINTS: answer only from retrieved context; do not invent sources.
```

Full worked descriptions and categorized example suites are in [`examples/`](examples/).
The example library includes real systems plus suites for corporate lifecycle,
AI-native organisational change, psychological and sociological work interfaces,
technical/agentic workflows, occupational health, governance/risk/compliance,
and OKF-style human-systems mappings.

### Rendering & export
Cairn can be turned into audience-friendly views:

```bash
deborah-render my-process.cairn.md --profile narrative_steps
# Domain examples:
#   --profile therapeutic     (psychological / regulation + feedback focus)
#   --profile change_leader   (organisational change + coalition/alignment focus)
#   --profile human_demand    (human load, support, trust + simulation findings)
#   --profile human_factors   (cognitive/social/org/incentive risks + mitigations)
deborah-render my-process.cairn.md -f html -o view.html
deborah-render my-process.cairn.md -f pdf -o plan.pdf   # requires [export]

```

The human-systems analysis CLIs (`huldah-human-factors`,
`huldah-agent-harness-plan`, `huldah-recommend-interface-changes`,
`huldah-generate-report`, the `huldah-ui-*` family) moved to
**[Huldah](https://github.com/gellsmore-svg/Huldah)** — `pip install huldah`.
They read the same `.cairn.md` documents this package defines.

Or programmatically:

```python
from deborah import parse_document, validate_document, document_to_plan, validate_plan
from deborah.render import render_plan, export_view

doc = parse_document(text)
errors = validate_document(doc)
plan = document_to_plan(doc)
assert validate_plan(plan) == []

view = render_plan(text, profile="operator")
pdf = export_view(view, "pdf")  # requires deborah[export]
```

Interactive composer: `deborah-serve` (requires `deborah[web]`).

## What it's for

- **Framing cross-LLM work** — how LLM callers interact with LLM-consumed
  capabilities (tools, services, roles): intent, outcomes, pins, bounds, and
  residual uncertainty (`open` / `refused`), without pretending to make
  stochastic steps pure functions. See [SPEC.md](SPEC.md) §14–§17.
- **Crystallising** negotiated or hand-authored sequences into versioned
  `PROCESS` / `PLAN` documents that an interpreter can walk under allow-lists
  and bounds.
- Documenting **requirements** and technical specifications in design docs.
- **Reverse-engineering** hidden or unclear processes out of existing systems.
- Governed agentic flows: recursion, iteration, tool boundaries, revision,
  approval gates, and outcome alignment.
- Describing work in **human systems** (cognitive, organisational, social) with
  descriptive constructs and render profiles — while the **core** construct
  profile stays portable for execution (`deborah.CORE_CONSTRUCTS`).

Human-factors analysis, UI evidence, layout load, and agent-harness reporting
live in **[Huldah](https://github.com/gellsmore-svg/Huldah)** and consume the
same `.cairn.md` format.

Put simply: Cairn describes how callers and capabilities work together inside
real human systems — not only mechanical control flow.

## Philosophy

### Human-first readability
The primary goal is **maximum human readability**. Anyone — technical or not —
should read a Cairn description and quickly understand the process without
wrestling with syntax, jargon, or abstraction. We remove cognitive barriers so
attention stays on **what the process actually does**, not on decoding notation.

This matters because agentic work is rarely just computation. It often includes
judgement, uncertainty, memory, motivation, trust, conflict, change, and review.
Cairn keeps those human dimensions describable without losing the governed
runtime spine that lets AI systems validate and interpret plans.

### Least abstract, simplest language possible
- Concrete, everyday words wherever they suffice.
- Short, direct sentences; active voice.
- Structure scaffolds without getting in the way.
- Details (constraints, context, edge cases) are optional layers consulted when
  needed — the main flow stays clean and punchy.

### Consistency through core verbs
A small recommended lexicon (Initialize, Propose, Evaluate, Decide, Update,
Execute, Iterate, Queue, Merge, Handle…) gives a consistent rhythm and "process
feel" that helps readers scan, compare, and mentally simulate flows — and helps
multiple people or LLMs write consistently. Verbs are **not rigid rules**;
clarity always wins.

### Balance of structure and flexibility
- Numbered steps + indentation give sequence and hierarchy.
- `PLAN` envelopes turn a `PROCESS` into a versioned live plan that can be revised when new information arrives.
- Tags (`[LLM, SYNC, DYNAMIC]`) add precision without cluttering prose.
- One canonical backbone is projected into audience **render profiles** (precise
  `ai`, readable `operator`, and more) — serving machines and humans alike.
- CONTEXT and CONSTRAINTS supply supporting knowledge on demand.

### Human-system awareness
Cairn can describe psychological, organisational, and sociological processes
alongside technical ones because governed agentic work happens inside human
systems. Domain constructs (`REGULATION`, `COALITION`, `SOCIALIZE`, …) are in the
**descriptive** profile — they author and render well; a minimal interpreter may
skip them without inventing runtime behaviour (SPEC §16).

Human-factors analysis tooling and provider adapters for offline interpretation
ship in **Huldah**, not Deborah. Capability manifests for MCP/tool discovery
ship in **Keturah**. Trace and cost of runs live in **Galeed**.

### Practical and evolving
Cairn is meant to be used "in anger" on real projects, evolving from actual needs
rather than theoretical perfection.

> The ultimate test: a reader thinks *"I get what's happening here,"* not
> *"I need to learn the notation first."*

## Status

Deborah carries **two independent version numbers** (they are not meant to match):

| What | Where it lives | Current |
|---|---|---|
| **Specification** — the language | `SPEC.md`, `GRAMMAR.md` | **v0.12** |
| **Package** — installable Python | `pyproject.toml` (`deborah` on PyPI) | **0.18.0** |

Package **0.18.0** adds a **content-aware** `milcah.critique` negotiator
(clarify / refuse / accept) on the substrate slice (`--negotiator auto`). See
[CHANGELOG.md](CHANGELOG.md).

Compat: `cairn-lang` on PyPI is a deprecation shim re-exporting Deborah (and
Huldah where needed). Prefer `pip install deborah`.

## Repository

- [SPEC.md](SPEC.md) — normative specification (**v0.12**).
- [GRAMMAR.md](GRAMMAR.md) — structural EBNF (including PLAN framing fields).
- [examples/](examples/) — family systems and domain suites in `.cairn.md`.
- [CHANGELOG.md](CHANGELOG.md) — package and language evolution.
- [MIGRATING.md](MIGRATING.md) — Cairn → Deborah / Huldah split.
- [docs/usage-modes.md](docs/usage-modes.md) — CLI, library, embedded, CI modes.
- [docs/GRAMMAR-PARSER.md](docs/GRAMMAR-PARSER.md) — executable grammar API.
- [docs/VIEW-GENERATOR.md](docs/VIEW-GENERATOR.md) — render profiles and export.
- [docs/PROCESS-SEMANTICS-AND-ROADMAP.md](docs/PROCESS-SEMANTICS-AND-ROADMAP.md)
  — three-layer process semantics (execution / behaviour / cognition) and
  phased implementation roadmap after 0.10.0.
- [docs/TAXONOMY-COGNITION-AND-PATTERNS.md](docs/TAXONOMY-COGNITION-AND-PATTERNS.md)
  — which cognitions are primitives vs higher-order patterns.
- [examples/answer-substrate-question.cairn.md](examples/answer-substrate-question.cairn.md)
  — Stage 1 vertical slice plan.
- [okf/](okf/) — Open Knowledge Format concept bundle for the language.
- [docs/future-usage-logging-spec.md](docs/future-usage-logging-spec.md) —
  notes on future touchpoint logging.
- [docs/augmentation-integration-notes.md](docs/augmentation-integration-notes.md)
  — how augmentation-process research maps into Cairn.
- Human-factors / UI analysis docs and CLIs →
  [Huldah](https://github.com/gellsmore-svg/Huldah).

## Feedback & contributing

Cairn evolves from real use, so **feedback is the point** — especially from
describing your own processes in it.

- Open a GitHub issue for ambiguities, gaps, or proposals (show the real process
  that motivated a language change).
- See [CONTRIBUTING.md](CONTRIBUTING.md) for principles (including core vs
  descriptive constructs and non-goals).

## License

[Apache License 2.0](LICENSE).

## Conformance (`deborah` package)

Deborah is primarily a language package, but it ships a tiny, dependency-free
**conformance surface** so a runtime can validate the plans it produces instead of
embedding a private dialect:

```python
import deborah

# Runtime PLAN dict conformance (profiles: full | core | strict)
errors = deborah.validate_plan(plan_dict, profile="strict")

# Cognitive product contracts (Phase C)
from deborah import validate_cognition_result, EXAMPLE_RESULTS
assert validate_cognition_result("infer", EXAMPLE_RESULTS["infer"], mode="strict") == []

# Structural grammar (GRAMMAR.md EBNF + SPEC §12 well-formedness)
doc = deborah.parse_document(cairn_text_or_markdown)
errors = deborah.validate_document(doc)   # [] when well-formed
plan = deborah.document_to_plan(doc)        # first PLAN or PROCESS → plan dict

# Simplified human-readable views
view = deborah.render_plan(cairn_text_or_markdown, profile="narrative_steps")
deborah.CANONICAL_PLAN                      # known-good fixture
deborah.CORE_CONSTRUCTS                     # execution-normative constructs
deborah.COGNITION_MVP                       # observe|infer|evaluate|decide
```

CLI:

```bash
deborah-validate examples/cross-llm-critique.cairn.md --profile strict
deborah-run examples/cross-llm-critique.cairn.md --demo-results --check-contracts
deborah-render examples/hoglah.cairn.md
```

### View composer (`deborah-serve`)

An interactive, local composer for building a transformation view of a process
and **saving the recipe as a named template**:

```bash
pip install 'deborah[web]'
deborah-serve            # http://127.0.0.1:8795
```

Paste a Cairn process, pick a profile and options (language, format, depth,
sections, layout), watch the view update live, then **Save as template**. A
template is persisted as a stylesheet under `~/.cairn/templates/<name>.json`,
so it is directly reusable on the CLI:
`deborah-render --stylesheet ~/.cairn/templates/<name>.json input.cairn.md`.

Grammar parser: [docs/GRAMMAR-PARSER.md](docs/GRAMMAR-PARSER.md). Simplified views:
[docs/VIEW-GENERATOR.md](docs/VIEW-GENERATOR.md).

Tirzah's recursive planner is tested against `deborah.validate_plan` so its output
cannot drift from the grammar.

Works the same on native Linux and WSL. Cairn has no hard runtime dependency on
Keturah; when Keturah is installed, `deborah.manifest` uses it, and otherwise
Cairn provides a small compatible manifest surface.

```bash
pip install -e ".[dev]" && pytest
```
