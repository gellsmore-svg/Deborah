# Deborah

**Deborah is a process language that people and AI systems can both read.**
You describe a process in plain numbered steps. Deborah validates it, renders
it for different audiences, and turns it into a plan an interpreter can walk
under allow-lists and bounds.

It is built for **framing cross-LLM work**: which capabilities (tools,
services, roles) an LLM caller may use, under what bounds, and when to stop,
leave a question open, or refuse, with intent, outcomes and residual
uncertainty made explicit. It does **not** pretend to turn stochastic model
steps into pure functions; it constrains the *frame* around them.

> **Renamed from Cairn (v0.9).** The `cairn` package split into Deborah (the
> language) and [Huldah](https://github.com/gellsmore-svg/Huldah) (human-systems
> analysis). **The document format keeps the Cairn name**: `.cairn.md` files
> and ```cairn fences are unchanged. See [MIGRATING.md](MIGRATING.md).

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

## Is it for you?

**Good fit:** you need to describe how work actually happens (an agentic
workflow, a business process, a review gate, a change programme), so that a
non-technical reader understands it and a runtime can still validate it.
That includes iteration, recursion, non-determinism, queues, approvals,
error handling and the human context around them.

**Not a fit:** a new programming language. Deborah describes and frames
processes; it is not a general-purpose way to write code.

## Try it

```bash
pip install deborah
deborah-validate my-process.cairn.md --profile strict     # well-formed? conforms?
deborah-render my-process.cairn.md --profile narrative_steps
```

The [examples](examples/) run as-is, for instance
`deborah-render examples/hoglah.cairn.md` or
`deborah-run examples/cross-llm-critique.cairn.md --demo-results --check-contracts`.

**Version note:** PyPI has package 0.25.1, which implements SPEC v0.12. The
current spec, **v0.14**, adds `SAMPLE`/`VIEW`/named `MERGE` (v0.13) and the
four-area EXTENSION verbs such as `NUDGE`, `GAME` and `CHOICE` (v0.14). It ships
in package 0.26.0, which is not yet released; install from source to use it:
`pip install "git+https://github.com/gellsmore-svg/Deborah"`.

**Writing it with an agent:** copy [`skill/`](skill/) to
`~/.claude/skills/deborah/` (Claude Code) or `~/.grok/skills/deborah/` (Grok)
and invoke `/deborah`. You can describe a process in your own words without
learning the notation.

## Tools

| Tool | Does |
|---|---|
| `deborah-validate` | Checks structure (GRAMMAR.md, SPEC §12) and plan conformance (`full`, `core` or `strict` profile) |
| `deborah-render` | Renders a process for an audience: `operator`, `executive`, `audit`, `narrative_steps`, `simple_prose`, `therapeutic`, `change_leader`, `human_factors`, `human_demand`. Output as markdown, text, JSON, Mermaid or HTML, or DOCX/PDF with `deborah[export]`; English, Spanish or French |
| `deborah-run` | Walks a plan through the reference interpreter and checks cognition contracts |
| `deborah-serve` | A local composer (`deborah[web]`, port 8795): pick a profile and options, watch the view update, save the recipe as a reusable stylesheet |
| `import deborah` | `parse_document`, `validate_document`, `document_to_plan`, `validate_plan`, `render_plan`: the same surface for a runtime ([conformance API](docs/conformance.md)) |

Human-factors and UI analysis of the same documents is in
[Huldah](https://github.com/gellsmore-svg/Huldah) (`pip install huldah`).

## How the pieces fit

- **Two kinds of construct.** The **core** profile (`deborah.CORE_CONSTRUCTS`)
  is execution-normative and portable. **Descriptive** constructs
  (`REGULATION`, `COALITION`, `NUDGE` and others) author and render well, but
  a minimal interpreter may skip them without inventing behaviour (SPEC §16).
- **One backbone, many views.** A process has one canonical structure,
  projected into render profiles for machines and for people.
- **PLANs are versioned.** A `PLAN` wraps a `PROCESS` as a live plan that can
  be revised when new information arrives.
- **In the family:** [Tirzah](https://github.com/gellsmore-svg/tirzah) authors
  and revises plans, and its planner is tested against
  `deborah.validate_plan` so it cannot drift from the grammar
  ([plan ownership](docs/PLAN-OWNERSHIP.md)).
  [Keturah](https://github.com/gellsmore-svg/keturah) carries capability
  manifests (optional; Deborah has a small compatible fallback), and
  [Galeed](https://github.com/gellsmore-svg/galeed) records the trace and cost
  of runs.

Why the language reads the way it does (human-first readability, least
abstraction, core verbs) is in [docs/philosophy.md](docs/philosophy.md).

## Versions

Deborah carries two independent version numbers:

| What | Where | Current |
|---|---|---|
| Specification (the language) | [SPEC.md](SPEC.md), [GRAMMAR.md](GRAMMAR.md) | **v0.14** |
| Package (Python) | `pyproject.toml` | **0.26.0** in source; **0.25.1** on PyPI |

`cairn-lang` on PyPI is a deprecation shim that re-exports Deborah.

## Documentation

- **Authors:** [GUIDE-HUMAN](docs/GUIDE-HUMAN.md) · [examples/](examples/) ·
  [render profiles and export](docs/VIEW-GENERATOR.md)
- **Runtimes and planners:** [GUIDE-AI](docs/GUIDE-AI.md) ·
  [conformance API](docs/conformance.md) · [grammar parser](docs/GRAMMAR-PARSER.md) ·
  [usage modes](docs/usage-modes.md)
- **Language design:** [SPEC.md](SPEC.md) · [GRAMMAR.md](GRAMMAR.md) ·
  [process semantics and roadmap](docs/PROCESS-SEMANTICS-AND-ROADMAP.md) ·
  [cognition taxonomy](docs/TAXONOMY-COGNITION-AND-PATTERNS.md) ·
  [philosophy](docs/philosophy.md) · [okf/](okf/) concept bundle
- **History:** [CHANGELOG](CHANGELOG.md) · [MIGRATING](MIGRATING.md) ·
  [2026-08-08 review](docs/review-2026-08-08.md), actioned in 0.24.0

## Feedback and contributing

Deborah evolves from real use, so **feedback is the point**, especially from
describing your own processes in it. Open an issue for ambiguities, gaps or
proposals, and show the real process that motivated a language change. See
[CONTRIBUTING.md](CONTRIBUTING.md).

Develop: `pip install -e ".[dev]" && pytest`. Works the same on Linux and
WSL. Apache 2.0, see [LICENSE](LICENSE).
