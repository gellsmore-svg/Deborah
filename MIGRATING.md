# Migrating from `cairn` to `deborah` + `huldah`

`cairn` was two products in one package: a process **language** and a
human-systems **analysis** toolkit. They had different users, release cadences
and dependency profiles, so v0.9 splits them.

| Was | Is now |
|---|---|
| `cairn` (language: spec, grammar, conformance, render) | **`deborah`** |
| `cairn` (analysis: human factors, UI evidence, layout load, live observation, agent harness, LLM wrappers) | **`huldah`** |
| distribution `cairn-lang` | compatibility shim that installs `deborah` |

## What did *not* change

**The document format keeps the Cairn name.** Your `.cairn.md` files, ```` ```cairn ````
fences, `HUMAN_*` annotation blocks and every example are unchanged, and both
packages still read and write them. Only the Python distributions were renamed —
the rename was about a crowded PyPI/GitHub namespace, not about the language.

The grammar, the conformance rules and the plan schema are byte-identical to
`cairn-lang` v0.8.2. This is a repackaging, not a language revision.

## Nothing breaks on day one

`pip install cairn-lang` still works and now installs a shim. Existing code
keeps running:

```python
import cairn
cairn.validate_plan(plan)          # -> deborah.validate_plan, with a DeprecationWarning
cairn.analyze_human_factors(doc)   # -> huldah.analyze_human_factors
from cairn.grammar import parse_document   # -> deborah.grammar.parse_document
```

Submodules resolve too, including deep paths (`cairn.grammar.parser`). Each
name warns once, naming its new home.

The shim depends only on `deborah`. If you used the analysis half, either
`pip install huldah` or `pip install 'cairn-lang[analysis]'` — otherwise those
names raise an `ImportError` telling you exactly which package to install,
rather than failing obscurely.

The shim is removed one minor release after the last family consumer migrates.

## Migrating your imports

```python
# language
from cairn import validate_plan, render_plan      # before
from deborah import validate_plan, render_plan    # after

# analysis
from cairn import analyze_human_factors           # before
from huldah import analyze_human_factors          # after
```

## Console scripts

| Was | Is now | Package |
|---|---|---|
| `cairn-render` | `deborah-render` | deborah |
| `cairn-validate` | `deborah-validate` | deborah |
| `cairn-serve` | `deborah-serve` | deborah |
| `cairn-human-factors` | `huldah-human-factors` | huldah |
| `cairn-agent-harness-plan` | `huldah-agent-harness-plan` | huldah |
| `cairn-generate-report` | `huldah-generate-report` | huldah |
| `cairn-recommend-interface-changes` | `huldah-recommend-interface-changes` | huldah |
| `cairn-layout-load` | `huldah-layout-load` | huldah |
| `cairn-live-observe` | `huldah-live-observe` | huldah |
| `cairn-system-discover` | `huldah-system-discover` | huldah |
| `cairn-galeed-observe` | `huldah-galeed-observe` | huldah |
| `cairn-ui-sim`, `-ui-evidence`, `-ui-roleplay`, `-ui-annotations`, `-ui-scenario-validate`, `-ui-pipeline` | `huldah-ui-*` | huldah |

Console scripts are **not** shimmed — the old command names disappear when you
upgrade. They are invoked from shell scripts and CI where a silent alias would
hide the migration rather than surface it.

## MCP / Keturah manifests

The single fused `cairn` manifest advertised 11 capabilities, 6 of which lived
in the analysis layer. It is now two manifests, each advertising only what its
own package can execute:

- `deborah` — `validate_plan`, `render_plan`, `parse_document`,
  `validate_document`, and the `plan_schema` resource.
- `huldah` — `analyze_human_factors`, `analyze_ui_simulation_report`,
  `analyze_functional_layout`, `recommend_interface_changes`,
  `build_analysis_report`, `build_agent_harness_plan`.

MCP tool names change namespace accordingly: `cairn.render_plan` →
`deborah.render_plan`, `cairn.analyze_human_factors` → `huldah.analyze_human_factors`.

## Extras

`[render]`, `[web]` and `[export]` stay with **deborah** — the docx/pdf
exporters live in `deborah.render.export`, and Huldah's reporting calls into
them. `huldah[export]` simply defers to `deborah[export]`.
