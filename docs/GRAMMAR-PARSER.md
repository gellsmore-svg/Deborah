# Cairn grammar parser

Executable implementation of [GRAMMAR.md](../GRAMMAR.md) (structural EBNF) and
[SPEC.md](../SPEC.md) §12 well-formedness rules. The parser constrains the
*skeleton* only — step prose stays free text.

## Install

```bash
pip install -e ".[dev]"
```

## Quick start

```python
import cairn

text = open("examples/hoglah.cairn.md").read()
doc = cairn.parse_document(text)
errors = cairn.validate_document(doc)

if not errors:
    plan = cairn.document_to_plan(doc)   # optional: runtime PLAN dict
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
| `document_to_dict(doc)` | `dict` | JSON-serializable AST (for tooling / inspection) |
| `extract_cairn_source(text)` | `(str, kind)` | Strip markdown sections/fences to skeleton text |

`cairn.validate_plan(plan_dict)` remains the runtime PLAN contract (JSON dicts
from planners). `validate_document` validates authored Cairn prose/markdown.

## Markdown wrappers

`.cairn.md` files use `## CONTEXT` bullets, fenced `REQUIREMENTS` / `PROCESS`
blocks, and optional `OUTCOMES` prose. `extract_cairn_source` lifts these into a
single parseable skeleton (section headers are re-inserted where needed).

## Well-formedness (SPEC §12)

1. At least one CONTEXT, REQUIREMENTS/OUTCOMES, or PROCESS
2. Every PROCESS has a name (signature when I/O declared)
3. Consistent step numbering / nesting
4. Reserved tags: one value per dimension; custom tags namespaced
5. `STATE UPDATE` references declared STATE (document-wide), CONTEXT keys, or signature params
6. LLM-driven `ITERATE`/`RECURSE` carry `MAX`/`MAX_DEPTH`/`UNTIL`/`OVER`
7. `BREAK`/`CONTINUE` inside loops — including callee PROCESSes invoked from `ITERATE`/`QUEUE`
8. `AWAIT` declares `TIMEOUT`

Syntax errors land in `doc.parse_errors`; well-formedness errors are returned
by `validate_document` (which also includes parse errors).

## Render integration

`cairn.render_plan` uses the grammar parser by default (`normalize_input(use_grammar=True)`),
projecting the AST through `cairn.grammar.bridge.document_to_render_model`.

## Module layout

```
src/cairn/grammar/
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

All files in `examples/*.cairn.md` must parse with zero syntax errors:

```bash
python scripts/validate_examples.py
pytest tests/test_grammar.py
```