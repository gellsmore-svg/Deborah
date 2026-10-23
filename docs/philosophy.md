# Deborah design philosophy

Why the language reads the way it does. Moved from the root README (2026-10).


## Human-first readability
The primary goal is **maximum human readability**. Anyone — technical or not —
should read a Cairn description and quickly understand the process without
wrestling with syntax, jargon, or abstraction. We remove cognitive barriers so
attention stays on **what the process actually does**, not on decoding notation.

This matters because agentic work is rarely just computation. It often includes
judgement, uncertainty, memory, motivation, trust, conflict, change, and review.
Cairn keeps those human dimensions describable without losing the governed
runtime spine that lets AI systems validate and interpret plans.

## Least abstract, simplest language possible
- Concrete, everyday words wherever they suffice.
- Short, direct sentences; active voice.
- Structure scaffolds without getting in the way.
- Details (constraints, context, edge cases) are optional layers consulted when
  needed — the main flow stays clean and punchy.

## Consistency through core verbs
A small recommended lexicon (Initialize, Propose, Evaluate, Decide, Update,
Execute, Iterate, Queue, Merge, Handle…) gives a consistent rhythm and "process
feel" that helps readers scan, compare, and mentally simulate flows — and helps
multiple people or LLMs write consistently. Verbs are **not rigid rules**;
clarity always wins.

## Balance of structure and flexibility
- Numbered steps + indentation give sequence and hierarchy.
- `PLAN` envelopes turn a `PROCESS` into a versioned live plan that can be revised when new information arrives.
- Tags (`[LLM, SYNC, DYNAMIC]`) add precision without cluttering prose.
- One canonical backbone is projected into audience **render profiles** (readable
  `operator`, `executive`, `audit` and more) — serving machines and humans alike.
- CONTEXT and CONSTRAINTS supply supporting knowledge on demand.

## Human-system awareness
Cairn can describe psychological, organisational, and sociological processes
alongside technical ones because governed agentic work happens inside human
systems. Domain constructs (`REGULATION`, `AVOIDANCE`, `NUDGE`, `GAME`, `CHOICE`, `COALITION`, `SOCIALIZE`, …) are in the
**descriptive** profile — they author and render well; a minimal interpreter may
skip them without inventing runtime behaviour (SPEC §16).

Human-factors analysis tooling and provider adapters for offline interpretation
ship in **Huldah**, not Deborah. Capability manifests for MCP/tool discovery
ship in **Keturah**. Trace and cost of runs live in **Galeed**.

## Practical and evolving
Cairn is meant to be used "in anger" on real projects, evolving from actual needs
rather than theoretical perfection.

> The ultimate test: a reader thinks *"I get what's happening here,"* not
> *"I need to learn the notation first."*
