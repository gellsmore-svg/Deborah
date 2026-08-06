# Requirements for CAIRN Simplified View Generator (GenTech AI Development)

## 1. Overview / Purpose

Develop a Python-based component (module `deborah.render` in the **Deborah**
package) that transforms a formal Cairn process description into one or more
**simplified human-readable views**.

The goal is to reduce the cognitive load of the full formal syntax (hierarchical
numbered steps, tags, constructs like ITERATE/DECISION/CALL/STATE UPDATE,
CONSTRAINTS, SATISFIES references, PLAN revision envelopes, etc.) while
preserving the exact same underlying process steps and logic. This enables
easier human understanding, documentation, onboarding, stakeholder communication,
and collaboration alongside framed cross-LLM execution.

This component acts analogously to an XSLT stylesheet: it takes structured Cairn
input (text or parsed dict) and projects it into audience-optimized output formats
without altering the canonical source.

**Scope**: Focus on view generation/transformation. Do **not** implement full
parsing/validation (leverage `deborah.validate_plan()` / grammar parse where
possible). Support SPEC **v0.10** (render profiles, PLAN framing fields).

## 2. Functional Requirements

### 2.1 Input Handling

- Accept Cairn process descriptions as:
  - Raw Markdown/text string (`.cairn.md` style content).
  - Parsed Python dict (compatible with Deborah PLAN structures).
- Support full PROCESS blocks, PLAN revision envelopes (including INTENT /
  OUTCOMES / ASSUMES where present), nested hierarchical steps,
  CONTEXT/REQUIREMENTS/CONSTRAINTS, and major constructs from the grammar.
- Surface parser warnings in JSON metadata; optional `lenient` grammar fallback.

### 2.2 Core Transformation Features

- Produce **at least** the following view types/profiles:
  - **Narrative Steps View**
  - **Simple Prose Summary View**
  - **Operator / Guided Narrative View**
  - **Executive / Overview View**
- Support configurable "square/boxed" layout.
- Preserve step numbering, hierarchy, and logical sequence in all views.
- Handle recursion, iteration, decisions, calls to sub-processes, and state updates
  by rephrasing them accessibly without losing meaning.
- Include optional footnotes, appendices, or inline notes for constraints,
  requirements satisfaction, and key metadata that was summarized.

### 2.3 Output Formats

- Primary: Markdown
- Additional: Plain text, structured JSON, and optional Mermaid.js flowchart markup
- Support export hooks for docx/PDF generation (integration points)

### 2.4 Extensibility & Customization

- Pluggable architecture (renderer classes / profile configs)
- Stylesheet-like YAML/JSON configuration
- Multilingual support (English + one other language as proof-of-concept)
- Filtering / focus on specific sections

### 2.5 Integration & API

```python
from deborah import render_plan
view_text = render_plan(input_cairn, profile="narrative_steps", language="en", options={...})
```

## Implementation status

| Requirement | Status |
|---|---|
| PLAN dict input | Done |
| Markdown input (grammar parser default) | Done |
| `validate_plan` / parse warnings in JSON metadata | Done |
| narrative_steps, simple_prose, operator, executive, audit | Done |
| boxed layout | Done |
| markdown, text, json, mermaid, html | Done (html built-in) |
| pluggable profiles | Done |
| export hooks (docx/pdf) | Built-in; `pip install 'deborah[export]'` |
| YAML/JSON stylesheet | Done (`[render]` extra) |
| en + es + fr | Done |
| max_depth / sections filters | Done |
| `deborah-render` / `deborah-serve` | Done |
| Single-pass serve preview + lenient flag | Done |