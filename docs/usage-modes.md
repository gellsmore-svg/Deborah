# Deborah / Cairn usage modes

Deborah supports several modes without making the core language carry every
runtime concern. Use the lightest mode that fits. The language **frames**
cross-LLM caller↔capability work; it does not replace capability registries,
trace spines, or human-systems analysis products.

## Mode 1: PyPI package and CLI

Use when you want local validation, rendering, or composition.

```bash
pip install deborah
# optional: pip install 'deborah[render]' 'deborah[web]' 'deborah[export]'

deborah-validate examples/hoglah.cairn.md
deborah-validate plan.cairn.md --export-plan
deborah-render examples/keturah.cairn.md --profile operator
deborah-serve   # interactive transformation-view composer
```

Human-factors and UI-analysis CLIs moved to Huldah:

```bash
pip install huldah
huldah-human-factors examples/accounts-payable-exception.cairn.md
```

## Mode 2: Library — parse, validate, plan export, render

```python
from deborah import (
    parse_document,
    validate_document,
    document_to_plan,
    validate_plan,
    CORE_CONSTRUCTS,
)
from deborah.render import render_plan

doc = parse_document(open("examples/tirzah-plan-interpreter.cairn.md").read())
assert not validate_document(doc)
plan = document_to_plan(doc)
assert validate_plan(plan) == []
print(plan.get("intent"), plan.get("assumes"), plan.get("on_uncertainty"))

view = render_plan(open("examples/keturah.cairn.md").read(), profile="operator")
```

For recursive LLM *analysis* of human-system dimensions, use Huldah’s providers
and report builders — not Deborah.

## Mode 3: Crystallised cross-LLM processes

Use when an LLM caller (or human) has agreed how to engage a capability surface
and you need a **versioned** `PROCESS` / `PLAN` that can be interpreted under
bounds (SPEC §14).

Typical flow:

1. Discover capabilities via **Keturah** / MCP.
2. Optionally negotiate (bounded protocol; recorded in **Galeed**).
3. Author or emit a `.cairn.md` PLAN with `INTENT`, `OUTCOMES`, `ASSUMES`,
   `ON_UNCERTAINTY`, and optional step `COGNITION`.
4. Validate with `deborah-validate --profile strict`.
5. Interpret with the **thin runtime**:

```bash
deborah-run examples/cross-llm-critique.cairn.md --demo-results --check-contracts
# or programmatically:
from deborah import interpret_plan, document_to_plan, parse_document, StubHandler, EXAMPLE_RESULTS
plan = document_to_plan(parse_document(open("examples/cross-llm-critique.cairn.md").read()))
run = interpret_plan(plan, handler=StubHandler(results_by_cognition=EXAMPLE_RESULTS))
print(run.terminal)  # complete | open | refused | blocked
```

**Estate demo** (in-process capability index + retrieve/critique stubs):

```bash
deborah-run examples/cross-llm-critique.cairn.md --estate-demo --check-contracts
# optional Galeed tracing if galeed is installed:
deborah-run examples/cross-llm-critique.cairn.md --estate-demo --trace
```

```python
from deborah import interpret_with_estate, document_to_plan, parse_document
plan = document_to_plan(parse_document(open("examples/cross-llm-critique.cairn.md").read()))
run = interpret_with_estate(plan, demo=True, check_contracts=True)
```

Inject real Keturah registries and capability callables for production tools.
Do **not** treat free-form multi-round tool chat as the long-term execution path;
re-negotiation is a new REVISION.

## Mode 4: Embedded governance contract

Use when another product needs Deborah as a semantic contract: validation,
rendering, or plan export inside its own runtime. Keep product logging,
identity, and domain storage outside Deborah unless they are generic enough
for the core (e.g. `ASSUMES` pins).

## Mode 5: CI or review gate

Recommended gates:

- `deborah-validate` (or `scripts/validate_examples.py`) for `.cairn.md` files.
- Optional `deborah-render` smoke for key profiles.
- Huldah CLIs for human-facing process / UI evidence review when those docs
  change.

## Boundary guidance

| Concern | Home |
|---|---|
| Process language, PLAN framing, conformance | **Deborah** |
| Capability manifests / MCP | **Keturah** |
| Trace, decisions, LLM call cost | **Galeed** |
| Human-factors analysis & UI evidence | **Huldah** |
| Continuous learning of surface interrogation | Learning architecture (not Cairn docs) |

Keep Deborah focused on the semantic spine: readable process language,
crystallisable plans, and machine-checkable structure.
