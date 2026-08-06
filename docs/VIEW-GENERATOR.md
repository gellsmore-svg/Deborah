# Simplified View Generator

Python module `deborah.render` transforms formal Cairn process descriptions into
simplified human-readable views — analogous to an XSLT stylesheet projecting the
canonical backbone into audience-optimised formats without altering source logic.

## API

```python
from deborah import render_plan

# From a PLAN dict (validate_plan-compatible)
view = render_plan(plan_dict, profile="narrative_steps", language="en")

# From Cairn markdown
view = render_plan(open("examples/keturah.cairn.md").read(), profile="operator")

# JSON / Mermaid / plain text
diagram = render_plan(plan_dict, output_format="mermaid")
payload = render_plan(plan_dict, output_format="json")
```

### Profiles

| Profile | Purpose |
|---|---|
| `narrative_steps` | Hierarchical numbered plain-English steps |
| `simple_prose` | High-level flowing summary |
| `operator` | Guided narrative: purpose, owner, outputs (SPEC §3.2) |
| `executive` | Milestones, objectives, outcomes |
| `audit` | Defensible record: steps, tags, requirements (SPEC §3.1) |
| `narrative` | Alias for `narrative_steps` |
| Domain profiles | e.g. `therapeutic`, `change_leader`, `human_demand`, `human_factors` |

### Options

- `boxed` — blockquote/card layout per step or phase
- `include_tags` — show `[LLM]`, `[SATISFIES: …]` tags
- `include_sub_blocks` — CONSTRAINTS, OUTPUT, etc.
- `include_footnotes` — append requirement/constraint notes
- `lenient` — fall back to legacy parser on grammar failure (with warning)
- `max_depth`, `sections` — filters

### Stylesheets

Optional YAML/JSON rules (XSLT-inspired). Saved composer templates are usable
as stylesheets:

```bash
pip install 'deborah[render]'   # adds PyYAML
deborah-render input.cairn.md --stylesheet ~/.cairn/templates/ops.json
```

A repo-only example lives at `src/deborah/render/styles/default.yaml` (not
shipped in the wheel).

### Languages

`en`, `es`, `fr` (phrasing tables; other codes fall back to English).

## CLI

```bash
deborah-render examples/keturah.cairn.md --profile operator --boxed
deborah-render plan.json --profile audit --format json -o audit.json
deborah-render process.cairn.md --max-depth 2 --sections process,outcomes
deborah-render examples/tirzah.cairn.md -f html -o view.html
deborah-render draft.cairn.md --lenient   # explicit legacy fallback + warning
```

Interactive: `deborah-serve` (`pip install 'deborah[web]'`) — single-pass
preview with warnings from the render result.

## Export plugins (docx / PDF)

Built-in `html` exporter is always available. For docx/pdf:

```bash
pip install 'deborah[export]'
```

```python
from deborah.render import export_view, render_plan

bytes_out = export_view(render_plan(md), "docx")
```

## Scope

- View generation / transformation only
- Uses `deborah.grammar` by default for markdown/Cairn text; `validate_plan()`
  for PLAN dicts
- Aligned with SPEC render profiles (`operator`, `executive`, `audit`, …)

Full requirements: [VIEW-GENERATOR-REQUIREMENTS.md](VIEW-GENERATOR-REQUIREMENTS.md).
