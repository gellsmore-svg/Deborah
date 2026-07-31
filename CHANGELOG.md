# Changelog

## [Unreleased]
- `__version__` is derived from the installed distribution instead of a
  hand-maintained literal, so it cannot drift from `pyproject.toml`. Guarded by
  `tests/test_version.py`. (Nothing had drifted; this closes the trap that left
  Hanani advertising 0.1.0 while shipping 0.8.0.)

## [0.9.0] — 2026-07-31

**Renamed from Cairn, and split.** `cairn` was two products in one package; it is
now `deborah` (this repo — the process language) and
[`huldah`](https://github.com/gellsmore-svg/Huldah) (human-systems analysis).
See [MIGRATING.md](MIGRATING.md).

- Import `deborah`; distribution `deborah`. Console scripts `cairn-render` /
  `cairn-validate` / `cairn-serve` → `deborah-*`.
- The published `cairn-lang` distribution becomes a compatibility shim that
  re-exports from `deborah` (and `huldah`) with a `DeprecationWarning`, including
  submodules and deep paths. Removed one minor after the last consumer migrates.
- **The document format is unchanged**: `.cairn.md` sources, ```cairn fences and
  every example still parse identically. This is a repackaging, not a language
  revision — the grammar and conformance rules are byte-identical to v0.8.2.
- The fused manifest was split: Deborah advertises the five language capabilities,
  Huldah advertises the six analysis ones, so neither claims tools it cannot run.
- `[render]`, `[web]` and `[export]` stay here — the docx/pdf exporters live in
  `deborah.render.export`, which Huldah's reporting calls into.
- Added the `py.typed` marker the `Typing :: Typed` classifier had been claiming
  without shipping (was Cairn #12).
- Dependency-free by default is now verified in CI by importing with every
  optional dependency blocked.

## [0.8.2] — 2026-07-10

- Added consuming-agent prompts to agent harness plans so Codex CLI, Kiro,
  Claude Code, and similar interactive agents are explicitly steered to use
  Cairn's deterministic Python/CLI tools, inspect HCI touchpoints, separate
  business work from interface overhead, assess cognitive aesthetic, and state
  probability, impact, confidence, and evidence source separately.
- Rendered the new guidance in Markdown, shell, and JSON harness-plan output.

## [Unreleased] — 2026-07-09

- Added browser-driven UI evidence tooling for human-load analysis:
  - `cairn-ui-sim` scenarios can collect `measureLayout` snapshots from Playwright.
  - `cairn-ui-evidence` and `cairn-ui-pipeline` turn simulation reports into
    HCI phase evidence, human-factor findings, qualitative risk, and Cairn
    annotation snippets.
  - Layout overlay exports now support single snapshots, selected snapshot
    indices, bulk numbered SVG exports, Markdown indexes, and JSON manifests.
- Added functional layout-load analysis for UI geometry:
  - `cairn-layout-load` estimates label/control distance, related-element
    distance, evidence-to-action distance, columns, scan path, pointer travel,
    and recovery load.
  - Reports include suggested `FUNCTIONAL_LAYOUT_LOAD` Cairn blocks and SVG
    overlays for visual review.
- Expanded package and manifest surfaces so deterministic UI evidence and
  layout-load analyzers are discoverable from Python and Keturah-compatible
  tooling.
- Removed the hard runtime dependency on Keturah. Cairn now uses Keturah when it
  is installed and otherwise provides a small compatible manifest representation,
  keeping `pip install cairn-lang` dependency-light.
- Added the OKF Augmentation Process lens for human-AI collaboration:
  cognitive-state adaptation, role complementarity, shared mental models,
  interaction richness, trust calibration, and automation-bias risk.
- Extended HCI touchpoints, functional layout load, and the offline
  human-factors analyzer with augmentation-specific cues and review questions.
- Added usage-mode documentation and a Cairn-described manual agent analysis
  orchestration pattern for GitHub-link/process-file analysis.
- Added interactionless hosted LLM wrappers for Grok/xAI, Claude/Anthropic,
  OpenAI-compatible endpoints, and Gemini.
- Added OKF-traceable interface recommendation generation and report assembly
  (`cairn-recommend-interface-changes`, `cairn-generate-report`).
- Added a future usage logging and touchpoint analytics specification, with
  explicit guidance to keep production telemetry outside Cairn core unless it
  becomes a portable semantic contract.
- Clarified that manual interactive agent analysis can and should invoke Cairn
  Python APIs and CLI tools when the harness can execute local code.
- Added an agent harness playbook with a concrete CLI and Python sequence for
  tool-assisted manual Cairn analysis.
- Added `cairn-agent-harness-plan` and `build_agent_harness_plan` so interactive
  agents can ask Cairn which deterministic commands fit the available evidence.
- Added shell-script formatting for agent harness plans.
- Added harness-plan input provenance, repository/screenshot inputs, optional
  local file checks, and shell preflight guards for supplied evidence.
- Added `--fail-on-missing` for agent harness plans so unattended callers can
  write a plan and still fail fast on missing local evidence.
- Made `--fail-on-missing` imply local input checking for agent harness plans.
- Added a categorized expanded example library covering corporate lifecycle,
  AI-native organisational change, psychological and sociological work
  interfaces, technical/agentic workflows, cross-cutting Cairn meta-processes,
  and OKF-style human-systems mappings.
- Added research grounding notes and a SPEC/GRAMMAR review note for the expanded
  example corpus.
- Expanded the categorized suites with additional corporate, change,
  psychological, sociological, and technical/agentic examples, including the
  remaining non-diagnostic Cluster B pattern lenses and end-to-end lifecycle
  coverage.
- Added an occupational health and safety suite covering safety-management
  systems, incident learning, health surveillance/privacy, psychosocial risk,
  return to work, contractor coordination, ergonomics, and workplace violence.
- Added a governance, risk, and compliance suite covering AI model governance,
  privacy incident triage, audit remediation, regulatory change, third-party
  risk, speak-up, policy waivers, crisis governance, records holds, and
  sustainability claim assurance.
- Added agent-harness review checks so generated plans explicitly steer
  consuming LLMs toward UI touchpoint phases, functional layout load, interface
  overhead, evidence/inference boundaries, and AI challenge/override paths.
- Updated example validation to recurse into categorized example folders.

## [0.8.0] — 2026-07-07

- **Export story completed**: Built-in exporters for `html` (always available), `docx` (via python-docx), `pdf` (via fpdf2) under the new `cairn-lang[export]` extra.
  - `cairn-render -f html|docx|pdf -o out.ext` now works.
  - `cairn.render.export_view()` and `register_exporter()` fully functional.
  - Clean error messages when optional deps are missing.
  - Updated CLI, render pipeline, tests, and documentation.
- Packaging: Published 0.7.0 / 0.8.0 to PyPI as `cairn-lang`. Fixed license metadata for modern PyPI compatibility.
- Version bumped to 0.8.0.

## [0.7.0] — 2026-07-07
- Initial public PyPI release (as `cairn-lang`).

## [0.5.2] — 2026-07-05

- **`document_to_dict`:** JSON-serializable AST export; `cairn-validate --export-ast`.
- **GitHub Actions CI** (Python 3.11/3.12): pytest + `validate_examples.py`.
- Docs: VIEW-GENERATOR grammar integration note; OKF grammar reference links parser.

## [0.5.1] — 2026-07-05

- **Grammar validation refinements:** document-wide STATE visibility, CALL-target
  loop context for `BREAK`/`CONTINUE`, `OVER` bounds, LLM-only iteration guards,
  `IDEMPOTENT`+`SIDE-EFFECT` and `GATED`+`HUMAN` tag pairs, process-level
  `SERVICE`/`PARALLEL` construct lines.
- All `examples/*.cairn.md` now pass full well-formedness validation.
- Added [docs/GRAMMAR-PARSER.md](docs/GRAMMAR-PARSER.md).

## [0.5.0] — 2026-07-05

- **`cairn.grammar`:** executable GRAMMAR.md EBNF parser — `parse_document`,
  `validate_document` (SPEC §12 well-formedness), `document_to_plan`,
  markdown `.cairn.md` extraction, AST bridge to `cairn.render`.
- **`cairn-validate` CLI** and Keturah manifest capabilities `parse_document` /
  `validate_document`.
- **`scripts/validate_examples.py`** now uses the grammar parser (zero syntax
  errors required across `examples/*.cairn.md`).

## [0.4.1] — 2026-07-05

- **`cairn.render` continued:** `audit` profile (SPEC §3.1), French (`fr`) phrasing,
  `max_depth` / `sections` filters, PLAN envelope header in views, operator phase
  parsing (unnumbered titles), `register_exporter` / `export_view` hooks for docx/PDF
  plugins, `cairn-render` CLI.

## [0.4.0] — 2026-07-05

- **`cairn.render` / `render_plan`:** simplified view generator — narrative_steps,
  simple_prose, operator, executive profiles; markdown/text/json/mermaid output;
  en/es phrasing; optional YAML stylesheets (`[render]` extra); Keturah manifest
  capability. See [docs/VIEW-GENERATOR.md](docs/VIEW-GENERATOR.md).

## [Unreleased] (spec / examples — prior)

- **SPEC §4.6** — PLAN interpretation: step state machine, handler dispatch, trace.
- Added **`STEP_STATUSES`** to conformance validation.
- Tirzah: `answer_query` unified via retrieve/synthesize phases; `plan_executions` resume store.
- Tirzah: split `retrieve_for_answer` / `synthesize_from_retrieval` for interpretive handlers.
- Added **`tirzah-plan-interpreter.cairn.md`** — interpretive execution target + Tirzah v1 handlers.
- Added **`tirzah-recursive-planning.cairn.md`** — live PLAN propose/execute/revise seam.
- Added **`hoglah-submit.cairn.md`** (pure submitter) and **`relational-substrate.cairn.md`**.
- Added **`tirzah-generated-output.cairn.md`** — queue → unreviewed nodes → endorse/reject.
- Added **`tirzah-web-research.cairn.md`** — `--web` promotion and bounded search/fetch.
- Added **`keturah.cairn.md`** (manifest + MCP) and **`galeed.cairn.md`** (trace spine).
- Updated **`tirzah-system.cairn.md`** composition map (TRUST milestone, web, Galeed).
- Added Cairn stress-test examples for **Mahlah** (three-channel conversational
  ask UI) and **Milcah** (recursive coherence-pressure rounds).
- Added **`tirzah-ingest.cairn.md`** — ingestion pipeline, dead-letter, profile backfill.
- Rewrote **`hoglah.cairn.md` v2** — `CONCURRENT`/`SERVICE`, `DURABLE-BEFORE`,
  `RECOVERY`, `IDEMPOTENT [KEY: …]`, `EMERGENT [SATISFIES: …]` illustration.
- Added **`mizpah.cairn.md`** (cross-session trace browser) and
  **`tirzah-system.cairn.md`** (ingest → ask → observe composition).
- Expanded **`tirzah.cairn.md`** — `DECISION` across direct/agentic/deep modes.
- Added **`tirzah-semantic-review.cairn.md`** — enqueue → human review → graph edge.
- Added **`scripts/validate_examples.py`** + pytest skeleton check for `*.cairn.md`.
- SPEC §9 — documented `EMERGENT [SATISFIES: …]` block form (equivalent to inline `via` form).
- Updated `examples/README.md` and OKF examples reference; fixed README SPEC
  version line (v0.9).

## [0.3.0] — 2026-07-04

- **Distribution renamed to `cairn-lang`** (import name stays `cairn`): the PyPI
  'cairn' is an unrelated project occupying 0.1.0–0.2.3, and once won a
  find-links + index resolve. 0.3.0 also dodges its version range.

## [0.2.0] — 2026-07-04

- `STEP_STATUSES` conformance (SPEC §4.6 step state machine: pending/active/
  completed/blocked/skipped) validated per step by `validate_plan`.
- SPEC §4.6 "PLAN interpretation — live step execution" + interpreter examples.

## [0.9] — 2026-06-24

- Added the `PLAN` revision envelope for live recursive process instances,
  including identity, parent revision, status, trigger information, and a complete
  bounded `PROCESS` backbone on every revision.

# Changelog

All notable changes to the Cairn specification are recorded here.

## [0.8] — 2026-06-16

From feedback after modelling an end-to-end human-led, AI-assisted delivery
process (customer idea → frame → build → verify → release → change management):

- **Render profiles (§3).** The "two styles" generalise to audience profiles —
  one canonical backbone *projected* into `ai` (precise), `operator` (guided
  operational narrative), `executive` (overview), and `audit` (defensible record).
  Profiles are rendered by tooling/AI, not hand-authored. `render-profile:` selects
  one. The **operator profile** is specified in full (Purpose / Owner / Assisted-by
  / Outputs / Iterate-until / Next, with compression rules + a "don't over-compress"
  guardrail).
- **Ownership vs. contribution (§7).** The `Actor` dimension is the *accountable
  owner*; `ASSISTED-BY: <actors>` names who materially contributes — e.g.
  `[HUMAN, ASSISTED-BY: LLM]`. Owners may carry a role (`[HUMAN: Product Lead]`).
  Hybrid human-led / AI-assisted work no longer disappears at the top level.
- **`MILESTONE` and `PURPOSE`** constructs — major transitions and per-phase intent,
  the signals the human-facing profiles render.

## [0.7] — 2026-06-16

First **stress-tested release**: the v0.6 draft plus everything learned from
describing three real systems (Tirzah, Hoglah, Mahalath) in Cairn. Adds a
structural grammar ([GRAMMAR.md](GRAMMAR.md)).

**Renamed** from the working title "APML" to **Cairn** — a cairn marks a route
with simple waypoints so anyone who follows can stay on the path, which is what a
Cairn description does for humans and AI.

Revision following design review. Adds:

- **Three document modes** — CONTEXT (scene), REQUIREMENTS/OUTCOMES (testable
  assertions), PROCESS (flow) — kept distinct.
- **Shared backbone + dual styles.** Formal and Narrative are two renderings of
  one canonical structure (numbering + constructs + tags + state); an AI keeps
  them in sync. Formal is canonical for machine semantics.
- **Scoped, referenced STATE.** Inline directional declarations
  (`scope`/`dir`/`ref`) linked by number to a definitive STATE REFERENCE.
- **Progressive-formality construct modifiers** with defaults (ITERATE
  `UNTIL/MAX`, RECURSE `BASE/MAX_DEPTH`, QUEUE `ORDER`, PARALLEL `STATE/MERGE`,
  RETRY `MAX/BACKOFF`, ERROR propagation).
- **Tags as orthogonal dimensions** (Actor / Determinism / Timing / Effects /
  Control) + namespaced extensions; vocabulary grows from real use.
- **Requirements & Outcomes mode** — `R#` SHALL/SHOULD assertions with
  `ACCEPTANCE`, `[MUST/SHOULD/MAY]`, and `[SATISFIES: R#]` traceability.
- **Composition** — PROCESS signatures (INPUT/OUTPUT) + `CALL`.
- **Structural conformance** rules + a worked example in both styles.

Refinements from the first stress test (Tirzah, `examples/tirzah.cairn.md`):

- **`BREAK` / `CONTINUE`** loop control + `ITERATE UNTIL` may read body-set state
  (explicit loop exit instead of a DECISION "falling out").
- **Fan-out clarified** — a step may make many like calls (`[BATCH]`) and still be
  one step; `PARALLEL` is reserved for concurrent independent branches.
- **`ERROR THEN: fallback → <target>`** names the concrete recovery.
- **STATE scope semantics** spelled out (§6.4); `iteration` scope resets each round.
- **STATE across `CALL`** is private by default (§6.5) — data crosses via
  INPUT/OUTPUT; shared mutable state must be declared at a shared scope.

Refinements from stress tests 2–3 (Hoglah, Mahalath):

- **`SERVICE` + `CONCURRENT`** — long-running concurrent activities that never
  join (worker loops, consumers, watched folders), distinct from `PARALLEL`
  (which joins at MERGE).
- **`AWAIT [EVENT/TIMEOUT/THEN]`** — suspend until a human/system event; real
  processes wait (the `[GATED, HUMAN]` and broker-ack cases).
- **`ATOMIC` / `DURABLE-BEFORE` / `RECOVERY:`** — express safety-critical ordering
  between steps and what happens if a crash lands between them (the crash-window
  analogue of `ERROR` fallback).
- **`RECURSE` is a self-`CALL`** — clarified, so recursion isn't double-notated.
- **`DECISION` branch bodies** — multi-step branches nest with letters (`2a.`/`2b.`),
  like PARALLEL.
- **`IDEMPOTENT [KEY: …]`** + parameterised tags (`BATCH [n]`).
- **Emergent guarantees** — `[SATISFIES]` may name several steps across processes;
  `[MAY]` = capability, so `[SATISFIES]` on it means "supports", not "guarantees".

## [0.5] — prior

Initial prototype: PROCESS / numbered hierarchy / core verbs / tags / constructs
(ITERATE, RECURSE, QUEUE, PARALLEL, DECISION, RETRY, ERROR, STATE UPDATE, OUTPUT,
RISKS), CONSTRAINTS/BOUNDARIES and CONTEXT blocks, Formal + Narrative styles.
