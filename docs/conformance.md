# Conformance surface and CLI

The dependency-free conformance API a runtime uses to validate the plans it produces, plus the CLI and the view composer. Moved from the root README (2026-10).


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

## View composer (`deborah-serve`)

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

Grammar parser: [docs/GRAMMAR-PARSER.md](GRAMMAR-PARSER.md). Simplified views:
[docs/VIEW-GENERATOR.md](VIEW-GENERATOR.md).

Tirzah's recursive planner is tested against `deborah.validate_plan` so its output
cannot drift from the grammar.

Works the same on native Linux and WSL. Cairn has no hard runtime dependency on
Keturah; when Keturah is installed, `deborah.manifest` uses it, and otherwise
Cairn provides a small compatible manifest surface.

```bash
pip install -e ".[dev]" && pytest
```
