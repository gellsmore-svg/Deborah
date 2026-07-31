# Deborah

Deborah is a human-readable process language for **governed agentic work in human
systems**.

> **Renamed from Cairn (v0.9).** The package `cairn` was split into **Deborah**
> (this repo — the process language) and **[Huldah](https://github.com/gellsmore-svg/Huldah)**
> (human-systems analysis: human factors, UI evidence, layout load, live
> observation). The *document format keeps the Cairn name* — your `.cairn.md`
> files and ```` ```cairn ```` fences are unchanged. See
> [MIGRATING.md](MIGRATING.md).

It gives humans and AI systems a shared way to describe, plan, interpret, and
review complex work across technical, psychological, organisational, and
sociological dimensions. It bridges pseudocode-style clarity with modern
agentic realities: iteration, recursion, non-determinism, sync/async, queuing,
outcome review, error handling, and human context.

**The specification lives in [SPEC.md](SPEC.md) (v0.9).**

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
from deborah.render import render_plan, export_view

view = render_plan(text, profile="operator")
pdf = export_view(view, "pdf")

from deborah import analyze_human_factors, build_agent_harness_plan
report = analyze_human_factors(text)  # pure Python; no LLM service required
plan = build_agent_harness_plan(process_path="my-process.cairn.md", ui_evidence_path="ui-evidence.json")

from deborah import CommandLLMProvider, HoglahLLMProvider, interpret_human_factors
provider = CommandLLMProvider("my-llm-wrapper --model local")
interpretation = interpret_human_factors(text, provider)

queued = HoglahLLMProvider(model="gemma3:1b")
queued_interpretation = interpret_human_factors(text, queued)
```

Interactive composer: `deborah-serve`

## What it's for

- Documenting **requirements** and technical specifications in design documents.
- **Reverse-engineering** hidden or unclear processes out of existing code, AI
  systems, or legacy implementations.
- Defining **governed agentic** processes — recursive calls, iterative
  refinement, dynamic LLM decisions, tool boundaries, serialized agent
  discussions, trace, and outcome alignment.
- Real-world use cases: recursive agentic workflows (chat interfaces, autonomous
  systems), low-resource queuing, semantic engines, multi-step reasoning.
- Describing work as it actually happens: technical mechanisms embedded in
  human contexts, including cognitive, emotional, organisational, and social
  dynamics.
- New constructs for human dimensions: REGULATION, APPRAISAL, FEEDBACK, MACRO (psych), COALITION, ALIGN, VISION, RESISTANCE (org), SOCIALIZE, SYMBOLIC_INTERACTION, ROLE (socio), etc.
- Multi-scale STATE (e.g. scope: org.team), enhanced EMERGENT with attrs, domain-aware validation.
- Human demand mapping: ORIENT / ACT / CLOSE demand, recovery, trust, support,
  AI role-play simulation findings, and cognitive-load metrics for human-facing
  process steps.
- Human factors semantics: a browsable lens library for plausible cognitive,
  psychological, social, organisational, behavioural-economic, and incentive
  risks, with qualitative probability/impact estimates.
- Augmentation process semantics: human-AI role complementarity,
  cognitive-state adaptation, interaction richness, trust calibration, and
  bias dynamics.

Put simply: Cairn treats software work, thinking work, and organisational work
as processes embedded in human systems, not as purely mechanical flows.

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
systems. These dimensions are not a separate ambition from the agentic use case;
they are part of the operating environment that a useful agentic process must be
able to notice, express, and review.

The human-factors layer is portable by design. The OKF concept bundle supplies a
local semantic lookup for cognitive load, trust, social pressure,
organisational change, behavioural economics, and incentive patterns. The
offline analyzer can run as a normal PyPI module without a service dependency;
an LLM can later be attached as an optional interpreter that reads the same
report and starts a richer design conversation.

LLM integration is provider-neutral. A command provider receives JSON on stdin
(`task`, `prompt`, and `context`) and returns either plain text or JSON with a
`text` field. That means local llama.cpp/Ollama scripts, hosted-model CLIs,
Claude/Codex wrappers, or a Hoglah queue submitter can all sit behind the same
adapter. Hoglah is a natural fit for durable queued analysis jobs, retries, and
audit trails, and `HoglahLLMProvider` is available when `hoglah` is installed,
but Cairn does not require it.

See `examples/llm_command_stub.py` for the minimal provider contract.

### Practical and evolving
Cairn is meant to be used "in anger" on real projects, evolving from actual needs
rather than theoretical perfection.

> The ultimate test: a reader thinks *"I get what's happening here,"* not
> *"I need to learn the notation first."*

## Status

Cairn carries **two independent version numbers**, and they are not meant to match:

| What | Where it lives | Current |
|---|---|---|
| **Specification version** — the language itself | `SPEC.md` heading, `GRAMMAR.md` | **v0.9** |
| **Package version** — the Python implementation on PyPI as `cairn-lang` | `pyproject.toml`, `CHANGELOG.md`, git tag | **0.8.2** |

The package version is the single source of truth for anything installable; it is
set in `pyproject.toml`, recorded in `CHANGELOG.md`, and tagged (`v0.8.2`). The
specification version moves only when the language changes — v0.9 added versioned
live `PLAN` envelopes for bounded recursive revision of a `PROCESS` backbone.

**Package 0.8.2** — complete export support (`html`/`docx`/`pdf`), interactive `deborah-serve`, executable grammar + conformance, multiple render profiles, and real usage examples across the family stack.

A structural grammar is in [GRAMMAR.md](GRAMMAR.md). Refined by describing real
systems (Tirzah, Hoglah, Mahalath, etc.).

## Repository

- [SPEC.md](SPEC.md) — the specification (v0.9).
- [GRAMMAR.md](GRAMMAR.md) — structural EBNF for the skeleton.
- [examples/](examples/) — real systems described in Cairn (Tirzah, Hoglah, Mahalath, Mahlah, Milcah, Mizpah); see `tirzah-system.cairn.md` for end-to-end composition.
- [CHANGELOG.md](CHANGELOG.md) — how the spec has evolved.
- [docs/HUMAN-FACTORS-METHODOLOGY.md](docs/HUMAN-FACTORS-METHODOLOGY.md) — how
  to annotate human demand, factors, qualitative risk, and LLM-assisted review.
- [docs/HCI-TOUCHPOINTS.md](docs/HCI-TOUCHPOINTS.md) — how consuming LLMs should
  analyze UI touchpoints and cognitive-aesthetic load.
- [docs/FUNCTIONAL-LAYOUT-LOAD.md](docs/FUNCTIONAL-LAYOUT-LOAD.md) — how to
  estimate form/layout traversal load from UI geometry.
- [docs/usage-modes.md](docs/usage-modes.md) — PyPI, recursive LLM, manual
  GitHub-link agent, embedded, and CI/review-gate usage modes.
- [docs/orchestration/manual-agent-analysis.cairn.md](docs/orchestration/manual-agent-analysis.cairn.md)
  — a Cairn-described orchestration pattern for manual agent analysis.
- [docs/orchestration/agent-harness-playbook.md](docs/orchestration/agent-harness-playbook.md)
  — concrete CLI/Python sequence for tool-assisted interactive agent use.
- [docs/future-usage-logging-spec.md](docs/future-usage-logging-spec.md) —
  future plan for real-world touchpoint logging and analysis.
- [docs/augmentation-integration-notes.md](docs/augmentation-integration-notes.md)
  — how the augmentation process research was mapped into Cairn.
- [okf/](okf/index.md) — an [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
  knowledge bundle: Cairn's concepts and reference, as linked markdown.

## Feedback & contributing

Cairn evolves from real use, so **feedback is the point** — especially from
describing your own processes in it. That is exactly how v0.7 was shaped.

- **Ambiguity, gap, or rough edge?** Open a
  [feedback issue](../../issues/new/choose).
- **A new construct, tag, or change?** Open a proposal (same chooser) — say what
  real process motivated it; concrete beats theoretical.
- **Questions, ideas, show-and-tell?** Use the
  [Discussions](../../discussions) tab.
- See [CONTRIBUTING.md](CONTRIBUTING.md) for how proposals are handled.

## License

[Apache License 2.0](LICENSE).

## Conformance (`cairn` package)

Cairn is primarily a spec, but it also ships a tiny, dependency-free
**conformance surface** so a runtime can validate the plans it produces instead of
embedding a private dialect:

```python
import deborah

# Runtime PLAN dict conformance (SPEC §4.5)
errors = deborah.validate_plan(plan_dict)   # [] when conformant

# Structural grammar (GRAMMAR.md EBNF + SPEC §12 well-formedness)
doc = deborah.parse_document(cairn_text_or_markdown)
errors = deborah.validate_document(doc)   # [] when well-formed
plan = deborah.document_to_plan(doc)        # first PLAN or PROCESS → plan dict

# Simplified human-readable views
view = deborah.render_plan(cairn_text_or_markdown, profile="narrative_steps")
cairn.CANONICAL_PLAN                       # an executable known-good fixture
cairn.PLAN_CONSTRUCTS                      # the allowed step constructs (SPEC §5)
```

CLI: `deborah-validate examples/hoglah.cairn.md` · `deborah-render examples/hoglah.cairn.md`

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
