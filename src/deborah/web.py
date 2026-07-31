"""FastAPI app: an interactive composer for Cairn transformation views.

Single-file — routes + HTML/CSS/JS built in Python, the same minimal pattern
as the family's other browsers (Milcah, Hoglah, Mahalath). No templating
dependency; the page is static and talks to small JSON APIs.

The composer is a thin UI over the existing render engine
(``deborah.render.render_plan``) and the template store
(``deborah.render.templates.TemplateStore``). A user pastes a Cairn process,
picks a **profile** and options (language, format, depth, sections, layout),
sees the transformed **view** update live, and **saves the recipe as a named
template** — which is persisted as a stylesheet, directly reusable via
``deborah-render --stylesheet``.

Security posture: bind to 127.0.0.1 by default. There is no auth; the operator
runs it locally, browser on the same host.

Requires the ``web`` extra: ``pip install 'cairn-lang[web,render]'``.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from deborah.render import registered_profiles, render_plan
from deborah.render.templates import (
    OUTPUT_FORMATS,
    SECTIONS,
    DEFAULT_TEMPLATE_DIR,
    TemplateStore,
    normalize_recipe,
    stylesheet_of,
)

LANGUAGES: tuple[str, ...] = ("en", "es", "fr")

_SAMPLE = """# Release review — a worked Cairn process

## CONTEXT

A change is proposed; it is reviewed, tested, and either shipped or sent back.

## OUTCOMES

A merged change with a green test run, or a recorded reason it was held.

## PROCESS — Formal

```
PROCESS ReleaseReview (INPUT: change; OUTPUT: decision)
  STATE
    evidence  [scope: process; dir: read/write]  ref: E1

  1. MILESTONE REVIEW — read the change and its intent.   [HUMAN, ASSISTED-BY: LLM]
  2. STEP — run the test suite and gather results.        [CODE, DETERMINISTIC]
     STATE UPDATE: evidence ← test output
  3. DECISION — ship, or send back with reasons.          [HUMAN]
     3.1 STEP — on ship: merge and tag the release.        [CODE, DETERMINISTIC]
     3.2 STEP — on hold: record the blocking reasons.      [HUMAN]
  OUTPUT: decision (shipped | held, with rationale)
```
"""

_CSS = """
:root {
  --bg:#f6f7f9; --surface:#fff; --ink:#1c2128; --muted:#667085;
  --line:#e3e6ea; --line-soft:#edf0f3; --accent:#2f5fd0; --accent-soft:#e8eefc;
  --good:#14803c; --bad:#c22736;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg:#12151b; --surface:#1a1e26; --ink:#e5e8ee; --muted:#97a0af;
    --line:#2a3039; --line-soft:#232833; --accent:#7c9cff; --accent-soft:#232c45;
    --good:#7edc9f; --bad:#ff9aa4;
  }
}
* { box-sizing:border-box; }
body { font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; margin:0;
  color:var(--ink); background:var(--bg); font-size:14px; line-height:1.5; }
header { position:sticky; top:0; z-index:10; background:var(--surface);
  border-bottom:1px solid var(--line); }
header nav { display:flex; align-items:center; gap:.6em; padding:.55em 1em; }
.brand { font-weight:700; }
header .muted { color:var(--muted); }
.status { margin-left:auto; color:var(--muted); font-size:.85em;
  font-family:ui-monospace,"SF Mono",Menlo,monospace; }
.grid { display:grid; grid-template-columns: 1.1fr .8fr 1.3fr; gap:1px;
  background:var(--line); height:calc(100vh - 47px); }
.pane { background:var(--bg); overflow:auto; padding:1em; display:flex; flex-direction:column; }
.pane h2 { font-size:.78em; text-transform:uppercase; letter-spacing:.05em;
  color:var(--muted); font-weight:600; margin:0 0 .7em; }
textarea#source { flex:1; width:100%; resize:none; min-height:200px;
  font-family:ui-monospace,"SF Mono",Menlo,monospace; font-size:12.5px; line-height:1.5;
  background:var(--surface); color:var(--ink); border:1px solid var(--line);
  border-radius:8px; padding:.7em; }
.field { margin-bottom:.8em; }
.field label { display:block; font-size:.82em; color:var(--muted); margin-bottom:.25em; }
select, input[type=text], input[type=number] { width:100%; padding:.4em .5em;
  background:var(--surface); color:var(--ink); border:1px solid var(--line);
  border-radius:6px; font-size:13px; }
.checks { display:flex; flex-direction:column; gap:.35em; }
.checks label, .seclist label { display:flex; align-items:center; gap:.45em;
  font-size:.86em; color:var(--ink); }
.seclist { display:flex; flex-wrap:wrap; gap:.5em .9em; }
.row { display:flex; gap:.6em; }
.row > * { flex:1; }
button { cursor:pointer; border:1px solid var(--line); background:var(--surface);
  color:var(--ink); border-radius:6px; padding:.45em .7em; font-size:13px; }
button.primary { background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600; }
button:hover { border-color:var(--accent); }
.preview { flex:1; background:var(--surface); border:1px solid var(--line);
  border-radius:8px; padding:.8em 1em; overflow:auto; white-space:pre-wrap;
  word-break:break-word; font-family:ui-monospace,"SF Mono",Menlo,monospace;
  font-size:12.5px; margin:0; }
.warnbox { color:var(--bad); font-size:.82em; margin:.5em 0 0; }
.errbox { color:var(--bad); }
.tpl-list { list-style:none; margin:.3em 0 0; padding:0; }
.tpl-list li { display:flex; align-items:center; gap:.4em; padding:.35em .1em;
  border-bottom:1px solid var(--line-soft); }
.tpl-list .tname { flex:1; cursor:pointer; }
.tpl-list .tname b { color:var(--accent); }
.tpl-list .tdesc { display:block; color:var(--muted); font-size:.8em; }
.tpl-list button { padding:.2em .45em; font-size:.8em; }
hr { border:none; border-top:1px solid var(--line); margin:1em 0; }
small.hint { color:var(--muted); }
"""

# The page is fully static: all data flows through the JSON APIs below.
_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cairn — view composer</title>
<style>__CSS__</style>
</head>
<body>
<header><nav>
  <span class="brand">Cairn</span>
  <span class="muted">transformation-view composer</span>
  <span class="status" id="status"></span>
</nav></header>
<div class="grid">
  <section class="pane">
    <h2>Source process</h2>
    <textarea id="source" spellcheck="false"></textarea>
    <div class="row" style="margin-top:.6em">
      <button id="loadSample">Load sample</button>
    </div>
  </section>

  <section class="pane">
    <h2>View</h2>
    <div class="field"><label>Profile</label><select id="profile"></select></div>
    <div class="row">
      <div class="field"><label>Language</label><select id="language"></select></div>
      <div class="field"><label>Format</label><select id="output_format"></select></div>
    </div>
    <div class="field"><label>Max depth (blank = all)</label>
      <input type="number" id="max_depth" min="1" placeholder="all"></div>
    <div class="field"><label>Options</label>
      <div class="checks">
        <label><input type="checkbox" id="boxed"> Boxed / card layout</label>
        <label><input type="checkbox" id="include_tags"> Include tags</label>
        <label><input type="checkbox" id="include_sub_blocks" checked> Include sub-blocks</label>
        <label><input type="checkbox" id="include_footnotes" checked> Include footnotes</label>
      </div>
    </div>
    <div class="field"><label>Sections (none checked = all)</label>
      <div class="seclist" id="sections"></div></div>
    <hr>
    <h2>Templates</h2>
    <div class="row">
      <button class="primary" id="saveTpl">Save as template</button>
      <button id="refreshTpl">Refresh</button>
    </div>
    <ul class="tpl-list" id="tplList"></ul>
    <small class="hint">Templates save as stylesheets under<br><code id="tplDir"></code></small>
  </section>

  <section class="pane">
    <h2>Preview</h2>
    <div class="warnbox" id="warn"></div>
    <pre class="preview" id="preview">…</pre>
  </section>
</div>
<script>__JS__</script>
</body>
</html>"""

_JS = r"""
const $ = (id) => document.getElementById(id);
const CTRL_IDS = ["profile","language","output_format","max_depth","boxed",
  "include_tags","include_sub_blocks","include_footnotes"];
let META = null;

function setStatus(t){ $("status").textContent = t; }

function opt(sel, values, current){
  sel.innerHTML = "";
  for (const v of values){
    const o = document.createElement("option");
    o.value = v; o.textContent = v; if (v === current) o.selected = true;
    sel.appendChild(o);
  }
}

function currentRecipe(){
  const sections = [...document.querySelectorAll("#sections input:checked")].map(c => c.value);
  const md = $("max_depth").value.trim();
  return {
    profile: $("profile").value,
    language: $("language").value,
    output_format: $("output_format").value,
    boxed: $("boxed").checked,
    include_tags: $("include_tags").checked,
    include_sub_blocks: $("include_sub_blocks").checked,
    include_footnotes: $("include_footnotes").checked,
    max_depth: md === "" ? null : Number(md),
    sections: sections,
  };
}

function applyRecipe(r){
  if (!r) return;
  if (r.profile) $("profile").value = r.profile;
  if (r.language) $("language").value = r.language;
  if (r.output_format) $("output_format").value = r.output_format;
  $("max_depth").value = (r.max_depth == null) ? "" : r.max_depth;
  for (const k of ["boxed","include_tags","include_sub_blocks","include_footnotes"])
    $(k).checked = (r[k] === undefined) ? $(k).checked : !!r[k];
  const secs = new Set(r.sections || []);
  document.querySelectorAll("#sections input").forEach(c => { c.checked = secs.has(c.value); });
}

let timer = null;
function scheduleRender(){ clearTimeout(timer); timer = setTimeout(render, 250); }

async function render(){
  setStatus("rendering…");
  try {
    const res = await fetch("/api/render", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ source: $("source").value, recipe: currentRecipe() }),
    });
    const data = await res.json();
    if (data.ok){
      $("preview").textContent = data.output || "(empty view)";
      $("preview").classList.remove("errbox");
      $("warn").textContent = (data.warnings && data.warnings.length)
        ? "⚠ " + data.warnings.join("  ·  ") : "";
      setStatus(data.format + " · " + (data.line_count) + " lines");
    } else {
      $("preview").textContent = data.error || "render failed";
      $("preview").classList.add("errbox");
      $("warn").textContent = ""; setStatus("error");
    }
  } catch(e){ $("preview").textContent = String(e); setStatus("error"); }
}

async function loadTemplates(){
  const items = await (await fetch("/api/templates")).json();
  const ul = $("tplList"); ul.innerHTML = "";
  if (!items.length){ ul.innerHTML = '<li class="tdesc">No templates yet.</li>'; return; }
  for (const t of items){
    const li = document.createElement("li");
    const span = document.createElement("span");
    span.className = "tname";
    span.innerHTML = "<b>"+escapeHtml(t.name)+"</b> <span class='muted'>("+escapeHtml(t.profile)+")</span>"
      + (t.description ? "<span class='tdesc'>"+escapeHtml(t.description)+"</span>" : "");
    span.onclick = () => { applyRecipe(t); render(); setStatus("loaded “"+t.name+"”"); };
    const del = document.createElement("button");
    del.textContent = "✕"; del.title = "Delete";
    del.onclick = async () => {
      if (!confirm("Delete template “"+t.name+"”?")) return;
      await fetch("/api/templates/"+encodeURIComponent(t.name), {method:"DELETE"});
      loadTemplates();
    };
    li.appendChild(span); li.appendChild(del); ul.appendChild(li);
  }
}

function escapeHtml(s){ const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

async function saveTemplate(){
  const name = prompt("Template name:");
  if (!name) return;
  const description = prompt("Short description (optional):") || "";
  const res = await fetch("/api/templates", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({ name, description, recipe: currentRecipe() }),
  });
  const data = await res.json();
  if (data.ok){ setStatus("saved “"+name+"”"); loadTemplates(); }
  else alert("Save failed: " + (data.error || "unknown"));
}

async function init(){
  META = await (await fetch("/api/meta")).json();
  opt($("profile"), META.profiles, "narrative_steps");
  opt($("language"), META.languages, "en");
  opt($("output_format"), META.output_formats, "markdown");
  const sec = $("sections");
  for (const s of META.sections){
    const lab = document.createElement("label");
    lab.innerHTML = "<input type='checkbox' value='"+s+"'> "+s;
    sec.appendChild(lab);
  }
  $("tplDir").textContent = META.template_dir;
  $("source").value = META.sample;

  for (const id of CTRL_IDS) $(id).addEventListener("input", scheduleRender);
  document.querySelectorAll("#sections input").forEach(c => c.addEventListener("change", scheduleRender));
  $("source").addEventListener("input", scheduleRender);
  $("loadSample").onclick = () => { $("source").value = META.sample; render(); };
  $("saveTpl").onclick = saveTemplate;
  $("refreshTpl").onclick = loadTemplates;

  await loadTemplates();
  render();
}
init();
"""


def _render_preview(source: str, recipe: dict[str, Any]) -> dict[str, Any]:
    """Render a preview + surface parser warnings, tolerant of bad input."""
    try:
        clean = normalize_recipe(recipe)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    if not source.strip():
        return {"ok": True, "output": "", "format": clean["output_format"],
                "warnings": [], "line_count": 0}

    fmt = clean["output_format"]
    options = {k: v for k, v in clean.items() if k not in ("profile", "language", "output_format")}
    try:
        out = render_plan(
            source, profile=clean["profile"], language=clean["language"],
            output_format=fmt, options=dict(options),
        )
        text = json.dumps(out, indent=2) if isinstance(out, dict) else str(out)
        # A second pass in JSON to pull structured warnings (cheap, pure).
        warnings: list[str] = []
        try:
            meta = render_plan(
                source, profile=clean["profile"], language=clean["language"],
                output_format="json", options=dict(options),
            )
            if isinstance(meta, dict):
                warnings = (meta.get("metadata") or {}).get("warnings") or []
        except Exception:  # noqa: BLE001 - warnings are best-effort
            warnings = []
        return {"ok": True, "output": text, "format": fmt,
                "warnings": warnings, "line_count": text.count("\n") + 1}
    except Exception as exc:  # noqa: BLE001 - report any render error to the UI
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def create_app(store: TemplateStore | None = None):
    """Build the FastAPI composer app over a template store."""
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse

    store = store or TemplateStore()
    app = FastAPI(title="Cairn view composer",
                  description="Compose and save Cairn transformation views")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _PAGE.replace("__CSS__", _CSS).replace("__JS__", _JS)

    @app.get("/api/meta")
    def meta() -> dict[str, Any]:
        return {
            "profiles": registered_profiles(),
            "languages": list(LANGUAGES),
            "output_formats": list(OUTPUT_FORMATS),
            "sections": list(SECTIONS),
            "template_dir": str(store.directory),
            "sample": _SAMPLE,
        }

    @app.post("/api/render")
    async def render_view(payload: dict[str, Any]) -> dict[str, Any]:
        return _render_preview(str(payload.get("source", "")), payload.get("recipe") or {})

    @app.get("/api/templates")
    def list_templates() -> list[dict[str, Any]]:
        return store.list_templates()

    @app.get("/api/templates/{name}")
    def get_template(name: str) -> dict[str, Any]:
        tpl = store.get_template(name)
        if tpl is None:
            raise HTTPException(status_code=404, detail="template not found")
        return tpl

    @app.post("/api/templates")
    async def save_template(payload: dict[str, Any]) -> Any:
        name = str(payload.get("name", "")).strip()
        if not name:
            return JSONResponse({"ok": False, "error": "name is required"}, status_code=400)
        try:
            record = store.save_template(
                name, payload.get("recipe") or {}, str(payload.get("description", ""))
            )
        except ValueError as exc:
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
        return {"ok": True, "template": record, "stylesheet": stylesheet_of(record)}

    @app.delete("/api/templates/{name}")
    def delete_template(name: str) -> dict[str, Any]:
        return {"ok": store.delete_template(name)}

    return app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deborah-serve",
        description="Serve the interactive Cairn transformation-view composer.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (keep local; no auth).")
    parser.add_argument("--port", type=int, default=8795, help="Port for the composer.")
    parser.add_argument("--templates-dir", default=str(DEFAULT_TEMPLATE_DIR),
                        help="Directory for saved view templates.")
    args = parser.parse_args(argv)

    try:
        import uvicorn
    except ImportError:
        print("The composer needs the 'web' extra: pip install 'cairn-lang[web,render]'")
        return 1

    store = TemplateStore(args.templates_dir)
    print(f"Cairn view composer on http://{args.host}:{args.port} — templates: {store.directory}")
    uvicorn.run(create_app(store), host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
