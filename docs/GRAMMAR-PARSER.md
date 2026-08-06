# Cairn grammar parser

Executable implementation of [GRAMMAR.md](../GRAMMAR.md) (structural EBNF) and
[SPEC.md](../SPEC.md) §12 well-formedness rules. The parser constrains the
*skeleton* only — step prose stays free text.

Package import path: **`deborah`** (document format name remains Cairn).

## Install

```bash
pip install -e ".[dev]"
# or: pip install deborah
```

## Quick start

```python
import deborah

text = open("examples/hoglah.cairn.md").read()
doc = deborah.parse_document(text)
errors = deborah.validate_document(doc)

if not errors:
    plan = deborah.document_to_plan(doc)  # optional: runtime PLAN dict
    assert deborah.validate_plan(plan) == []
```

CLI:

```bash
deborah-validate examples/hoglah.cairn.md
deborah-validate examples/hoglah.cairn.md --json
deborah-validate plan.cairn.md --export-plan
deborah-validate examples/hoglah.cairn.md --export-ast
```

## API

| Function | Returns | Purpose |
|---|---|---|
| `parse_document(text)` | `CairnDocument` | Parse raw Cairn or `.cairn.md` markdown wrapper |
| `validate_document(doc)` | `list[str]` | SPEC §12 well-formedness (`[]` = well-formed) |
| `document_to_plan(doc)` | `dict` | Export first `PLAN` or first `PROCESS` as a runtime plan |
| `document_to_dict(doc)` | `dict` | JSON-serializable AST |
| `extract_cairn_source(text)` | `(str, kind)` | Strip markdown sections/fences to skeleton text |
| `validate_plan(plan_dict)` | `list[str]` | Runtime PLAN contract (conformance 1.1) |

## PLAN framing fields (SPEC v0.10)

Parsed on the `Plan` AST and exported by `document_to_plan` when present:

| Field | Export key | Notes |
|---|---|---|
| `INTENT:` | `intent`, also feeds `objective` | Caller-facing success meaning |
| `OUTCOMES:` (+ bullets) | `outcomes`, `stopping_conditions` | End-states to judge against |
| `ASSUMES:` | `assumes` | Capability pins `name` or `name@version` |
| `ON_UNCERTAINTY:` | `on_uncertainty` | `record` \| `escalate` \| `abort` |
| `REEVALUATE_WHEN:` | `reevaluate_when` | Reopen hooks for surface/model change |

Terminal plan statuses include `open` and `refused` (residual uncertainty and
capability refusal are outcomes, not crashes).

## Markdown wrappers

`.cairn.md` files use `## CONTEXT` bullets, fenced `REQUIREMENTS` / `PROCESS`
blocks, and optional `OUTCOMES` prose. `extract_cairn_source` lifts these into a
single parseable skeleton.

## Well-formedness (SPEC §12)

1. At least one CONTEXT, REQUIREMENTS/OUTCOMES, or PROCESS
2. Every PROCESS has a name (signature when I/O declared)
3. Consistent step numbering / nesting
4. Reserved tags: one value per dimension; custom tags namespaced
5. `STATE UPDATE` references declared STATE, CONTEXT keys, or signature params
6. LLM-driven `ITERATE`/`RECURSE` carry a bound (`MAX` / `MAX_DEPTH` / …)
7. `BREAK`/`CONTINUE` inside loops
8. `AWAIT` declares `TIMEOUT`

Examples may be **PLAN-only** (PROCESS backbone nested under PLAN) —
`scripts/validate_examples.py` accepts PROCESS or PLAN.

## Render integration

`deborah.render_plan` uses the grammar parser by default
(`normalize_input(use_grammar=True)`), projecting the AST through
`deborah.grammar.bridge.document_to_render_model`. Grammar exceptions raise
unless `lenient=True` / `deborah-render --lenient`.

## Module layout

```
src/deborah/grammar/
  ast.py          # CairnDocument, Process, Step, Plan, …
  lexer.py        # indent-aware lines
  parser.py       # recursive descent
  extract.py      # .cairn.md → skeleton text
  validate.py     # SPEC §12
  plan_export.py  # document_to_plan
  bridge.py       # AST → render.ProcessDocument
  tags.py         # tag dimension parsing
```

## Examples

```bash
python scripts/validate_examples.py
pytest tests/test_grammar.py tests/test_conformance.py
```
