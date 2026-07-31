# Simplified View Generator

Python module `cairn.render` transforms formal Cairn process descriptions into
simplified human-readable views — analogous to an XSLT stylesheet projecting the
canonical backbone into audience-optimised formats without altering source logic.

## API

```python
from cairn import render_plan

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

### Options

- `boxed` — blockquote/card layout per step or phase
- `include_tags` — show `[LLM]`, `[SATISFIES: …]` tags
- `include_sub_blocks` — CONSTRAINTS, OUTPUT, etc.
- `include_footnotes` — append requirement/constraint notes

### Stylesheets

Optional YAML/JSON rules (XSLT-inspired):

```bash
pip install 'cairn-lang[render]'   # adds PyYAML
```

```python
render_plan(md, stylesheet="my-rules.yaml")
```

See `src/cairn/render/styles/default.yaml`.

### Languages

Proof-of-concept: `en`, `es`, `fr`.

## CLI

```bash
deborah-render examples/keturah.cairn.md --profile operator --boxed
deborah-render plan.json --profile audit --format json -o audit.json
deborah-render process.cairn.md --max-depth 2 --sections process,outcomes
deborah-render examples/tirzah.cairn.md -f html -o view.html   # built-in HTML export
```

## Export plugins (docx / PDF)

Built-in "html" exporter is always available. For docx/pdf:

```python
from cairn.render import register_exporter, export_view, render_plan

def to_docx(result, options):
    ...  # your docx builder (pip install python-docx)
    return b"..."

register_exporter("docx", to_docx)

# CLI now supports it:
# deborah-render input.cairn.md -f docx -o out.docx
bytes_out = export_view(render_plan(md), "docx")
```

## Scope

- View generation / transformation only
- Uses `cairn.grammar` by default for markdown/Cairn text; `validate_plan()` for PLAN dicts
- Cairn v0.9 render-profile alignment (`operator`, `executive`)

Full requirements: [VIEW-GENERATOR-REQUIREMENTS.md](VIEW-GENERATOR-REQUIREMENTS.md).