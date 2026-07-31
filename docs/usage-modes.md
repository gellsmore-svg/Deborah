# Cairn Usage Modes

Cairn supports several modes without making the core language carry every
runtime concern. Use the lightest mode that fits the work.

## Mode 1: PyPI Package And CLI

Use when you want deterministic local analysis, validation, rendering, UI
evidence, recommendations, or reports.

```bash
pip install cairn-lang
deborah-validate examples/hoglah.cairn.md
huldah-human-factors examples/accounts-payable-exception.cairn.md
huldah-layout-load docs/analysis/customer-po-review-layout.json
huldah-recommend-interface-changes docs/analysis/customer-po-review-ui-sim-report.json
huldah-generate-report --input examples/accounts-payable-exception.cairn.md \
  --interface-evidence docs/analysis/customer-po-review-ui-sim-report.json \
  --format html --output report.html
```

Use `cairn-lang[export]` when PDF or DOCX export is needed.

## Mode 2: Repo Or Library With LLM Calls

Use when Cairn is part of a recursive local or remote analysis loop. The core
contract is still small: Cairn prepares prompts and context, and a provider
returns text.

- `CommandLLMProvider` calls any command that reads JSON on stdin.
- `HoglahLLMProvider` submits durable queued jobs when Hoglah is installed.
- Hosted wrappers in `cairn.llm_wrappers` provide non-interactive HTTP adapters
  for Grok/xAI, Claude/Anthropic, OpenAI-compatible endpoints, and Gemini.

API keys are read from environment variables: `XAI_API_KEY`,
`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `GEMINI_API_KEY`.

## Mode 3: Manual Agent Analysis From A GitHub Link

Use when a person gives a repo link or process file to an agent such as Codex,
Claude, Grok, Amazon Q, Cursor, or Gemini and asks it to analyze with Cairn.

Do not rely on a loose prompt. Point the agent to:

- `docs/orchestration/manual-agent-analysis.cairn.md`
- `docs/orchestration/agent-harness-playbook.md`
- `okf/concepts/index.md`
- `docs/HCI-TOUCHPOINTS.md`
- `docs/FUNCTIONAL-LAYOUT-LOAD.md`

The orchestration pattern requires the agent to load the OKF bundle, apply
human-factors and augmentation lenses, generate OKF-traceable recommendations,
and produce a report. Every recommendation must cite the exact OKF file and
concept that drove it.

When the interactive harness can run local code, treat the manual mode as
tool-assisted rather than prompt-only. An agentic interface such as Codex CLI
should use the installed Cairn Python package and CLI commands for validation,
human-factors analysis, UI evidence review, layout-load analysis, interface
recommendations, and report generation wherever those tools fit the evidence.
The agent still interprets, prioritises, and explains, but deterministic Cairn
libraries should carry the repeatable parts of the work.

For a concrete sequence, see
`docs/orchestration/agent-harness-playbook.md`.

## Mode 4: Embedded Governance Library

Use when another product needs Cairn as a semantic contract: validation,
rendering, human-factor review, UI evidence, or recommendation generation inside
its own runtime. Keep product logging, user identity, and domain storage outside
Cairn unless they are generic enough for the core.

## Mode 5: CI Or Review Gate

Use when a repo wants pull requests to validate process files, render views, or
generate review artifacts. Recommended gates:

- `deborah-validate` for `.cairn.md` files.
- `huldah-human-factors` for human-facing process changes.
- `huldah-recommend-interface-changes` for UI evidence snapshots.
- `huldah-generate-report` for review bundles.

## Boundary Guidance

Keep Cairn focused on the semantic spine: process language, OKF concepts,
deterministic analysis, traceable recommendations, and portable reporting.
Separate repos or modules are better for durable production telemetry, hosted
dashboards, long-running workflow workers, and product-specific integrations.
