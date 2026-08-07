# Deborah — AI systems guide

**Audience:** LLM agents, planners, tool-calling runtimes, and automated
authors that must emit, validate, or walk crystallised process plans.

**Companion:** [GUIDE-HUMAN.md](GUIDE-HUMAN.md) for operator framing.  
**Normative:** [SPEC.md](../SPEC.md), [conformance](../src/deborah/conformance.py).  
**Ownership vs Tirzah:** [PLAN-OWNERSHIP.md](PLAN-OWNERSHIP.md).

---

## Role contract (read first)

```text
YOU MAY
  - author / revise PLAN JSON or .cairn.md that validates under deborah.validate_plan
  - emit ASSUMES, INTENT, OUTCOMES, ON_UNCERTAINTY, step COGNITION
  - call validate_plan / interpret_plan / run_substrate_slice via host tools
  - leave residual OPEN; record open questions

YOU MUST NOT
  - free re-plan mid crystallised walk (no inventing steps during interpret)
  - force agreement in negotiation (force_agreement forbidden)
  - invent evidence sources when observe returns empty
  - treat COGNITION as free natural language — products have contracts
  - redefine PLAN constructs outside Deborah CORE|EXTENSION sets
```

Deborah is the **schema + framed execution** authority. Tirzah may invent plans
and run a rich agentic executor; for substrate/critique graphs, Tirzah hands
off to Deborah’s thin slice. Do not implement a second dialect of PLAN.

---

## Install / import

```text
pip install deborah>=0.23.3
import deborah
# validate_plan, document_to_plan, interpret_plan, run_substrate_slice, …
```

Optional host stack for live estate:

| Stem (ASSUMES / CALL) | Product module |
|---|---|
| `tirzah.retrieve` | `tirzah.deborah` |
| `milcah.critique`, `validate_against_intent`, `assess_confidence` | `milcah.deborah` |
| `mahalath.detect_novel` | `mahalath.deborah` |
| `deborah.infer` | `deborah.runtime.infer` |
| Trace events | `galeed` |

---

## Plan object (machine shape)

Required fields (`REQUIRED_PLAN_FIELDS`):

```json
{
  "plan_id": "string",
  "revision": 1,
  "objective": "string",
  "status": "draft|active|stable|complete|blocked|open|refused",
  "steps": [ /* non-empty */ ],
  "stopping_conditions": ["…"],
  "revision_decision": "revise|stable|complete|blocked|open|refused"
}
```

Recommended framing (validated when present):

```json
{
  "request": "operator question",
  "intent": "why this run exists",
  "outcomes": ["verdict with evidence or open"],
  "assumes": ["tirzah.retrieve@1", "milcah.critique@1"],
  "on_uncertainty": "record",
  "exploration_budget": 0,
  "reflective_pass": true
}
```

Step minimum:

```json
{
  "id": "s1",
  "action": "…",
  "construct": "STEP|CALL|DECISION|…",
  "status": "pending|active|completed|blocked|skipped"
}
```

Optional step fields: `depends_on`, `allowed_tools`, `success_criteria`,
`output`, `cognition`, tags in prose/action.

### Validate

```python
from deborah import validate_plan
errors = validate_plan(plan_dict, profile="full")   # default
errors = validate_plan(plan_dict, profile="strict") # + cognition output; decide→DECISION
# errors == []  means conformant
```

Profiles:

| Profile | Use |
|---|---|
| `full` | Default structural contract |
| `core` | Reject EXTENSION constructs |
| `strict` | COGNITION needs output/success_criteria; CALL tools ⊆ ASSUMES; **decide requires construct DECISION** |

From prose:

```python
from deborah import parse_document, validate_document, document_to_plan
doc = parse_document(cairn_md_text)
assert validate_document(doc) == []
plan = document_to_plan(doc)
```

---

## COGNITION product contracts

Attach `cognition` only when the step returns a structured product.

| Value | Product (strict spirit) | Notes |
|---|---|---|
| `observe` | `evidence[]` with provenance | Empty set allowed if explicit |
| `infer` | claim + evidence_refs (+ assumptions/gaps) | Treat retrieve as untrusted |
| `evaluate` | criteria (+ scores/objections) | Critique / intent / confidence |
| `decide` | `selected` ∈ accept\|reject\|open | Prefer construct `DECISION`; GATED |
| `negotiate` | status, no force_agreement | Control pattern may record this shape |
| `learn` | change; auto_apply needs approval | Gated |
| `optimize` | needs stop_rule | Gated |

**Reflect is not a cognition** — use `reflective_pass` plan policy.

Validate results:

```python
from deborah.contracts import validate_cognition_result
errs = validate_cognition_result("observe", result_dict, mode="soft")  # or strict
```

---

## Thin interpreter vs substrate slice

### `interpret_plan` — crystallised walk

```python
from deborah.runtime import interpret_plan, StubHandler
run = interpret_plan(
    plan,
    handler=StubHandler(results_by_cognition=…),  # or EstateHandler
    allow_list={"tirzah.retrieve", "milcah.critique"},  # or from ASSUMES
    validate_profile="full",
    check_contracts=True,
    contract_mode="soft",
    decisions={"s7": "open", "default": "open"},  # GATED decide
    max_steps=32,
    allow_reentry=False,  # default off
)
# run.terminal ∈ complete|open|refused|blocked
```

**Hard rules during walk:**

- Do not add/remove steps.
- CALL tools must be allow-listed when ASSUMES/allow_list set.
- `exploration_budget` + `allow_reentry` only permit **at most one** re-dispatch of a low-confidence infer/evaluate step — not free re-planning.

### `run_substrate_slice` — Stage-1 critique path

```python
from deborah.runtime import run_substrate_slice
result = run_substrate_slice(
    plan,
    question="…",                 # overrides request
    demo=True,                    # or live=True + estate
    negotiate=True,
    negotiator_name="auto",       # accept | critique | auto
    post_retrieve_negotiate=True, # mid-gate after observe/infer
    confidence_floor="low",
    open_questions_path="oq.jsonl",
    open_questions_db=mongo_db,   # optional
    tracer=galeed_tracer,         # optional spine
    decisions={"default": "open"},
    check_contracts=True,
)
# result.terminal, result.negotiation, result.post_retrieve_negotiation
# result.open_question, result.outcomes, result.run
```

**Phase order (when plan splits at first critique CALL):**

```text
[pre-negotiate]
  → pre: novel / retrieve / infer
  → post_retrieve_negotiator (evidence_count / novel_detected)
  → post: critique / intent / confidence / decide
  → outcomes + open_question if residual
```

Galeed event types of interest (extensible vocabulary):

- `negotiation.started` / `negotiation.finished` (`metadata.note=post_retrieve` for mid-gate)
- `slice.phase.split` / `pre_complete` / `evidence_stats`
- `decision.recorded`
- `open_question.recorded`
- plan step events via `record_run_on_tracer`

---

## Emitting plans as an AI planner

### Do

1. Emit complete JSON with required fields; keep `steps` ≤ host `max_steps`.  
2. Use CORE constructs for executable control (`STEP`, `CALL`, `DECISION`, `RECURSE`, …).  
3. Pin capabilities: `assumes: ["tirzah.retrieve@1", "milcah.critique@1"]`.  
4. Put tool names in `allowed_tools` and/or CALL `action` stems.  
5. Set `on_uncertainty: "record"` unless host policy says otherwise.  
6. For human commit: `construct: "DECISION"`, `cognition: "decide"`, GATED/HUMAN tags in prose.  
7. Call `validate_plan` **before** execute; on errors, fix payload or use host fallback_plan.  
8. Prefer terminal **open** when evidence empty, critique weak, or confidence below floor.

### Do not

1. Return prose instead of JSON when the host expects a plan object.  
2. Use Tirzah-only status `awaiting` / construct `CONCURRENT` without normalisation (map to `pending` / `PARALLEL`).  
3. Invent ASSUMES that the estate cannot resolve.  
4. Put multi-round free search inside a single step without a stop_rule (`optimize` contract).  
5. Auto-apply learn products without approval.  
6. Collapse open residual into accept to “finish the task.”

### Minimal framed critique template

```json
{
  "plan_id": "plan_…",
  "revision": 1,
  "objective": "Ground claim or leave open",
  "status": "active",
  "request": "<user question>",
  "intent": "Evidence + adversarial critique, or open",
  "outcomes": ["verdict with ≥1 evidence or open with reason"],
  "assumes": [
    "tirzah.retrieve@1",
    "deborah.infer@1",
    "milcah.critique@1",
    "milcah.validate_against_intent@1",
    "milcah.assess_confidence@1"
  ],
  "on_uncertainty": "record",
  "exploration_budget": 0,
  "reflective_pass": true,
  "steps": [
    {"id": "s1", "construct": "STEP", "action": "Retrieve evidence", "status": "pending",
     "cognition": "observe", "allowed_tools": ["tirzah.retrieve"],
     "success_criteria": ["evidence list explicit even if empty"]},
    {"id": "s2", "construct": "STEP", "action": "Form provisional reading", "status": "pending",
     "cognition": "infer", "success_criteria": ["claim + evidence_refs"]},
    {"id": "s3", "construct": "CALL", "action": "milcah.critique — pressure-test", "status": "pending",
     "cognition": "evaluate", "allowed_tools": ["milcah.critique"],
     "success_criteria": ["criteria + objections"]},
    {"id": "s4", "construct": "DECISION", "action": "Commit accept|reject|open", "status": "pending",
     "cognition": "decide", "success_criteria": ["selected terminal"]}
  ],
  "stopping_conditions": ["verdict or open recorded"],
  "revision_decision": "stable"
}
```

Host detection (Tirzah ≥1.15): `is_framed_substrate_plan(plan)` → may call
`run_framed_plan` instead of the agentic executor.

---

## Negotiation (control, not free chat)

```python
from deborah.runtime.negotiate import run_negotiation, resolve_negotiator
neg = run_negotiation(
    intent=…, claim=…, assumes=…, max_rounds=4,
    negotiator=resolve_negotiator("auto", assumes=assumes),
)
# status: agreed | partial | unresolved | refused
# force_agreement must never be true in products
```

`post_retrieve_negotiator`: deterministic partial on `novel_detected` or
`evidence_count==0`; else acceptance. Does not rewrite the plan graph.

---

## Terminals and residuals

| Terminal | Meaning |
|---|---|
| `complete` | Walk finished under bounds |
| `open` | Residual / max_rounds / policy leave open |
| `refused` | Capability or negotiation refused |
| `blocked` | Validation, allow-list, empty plan, bound |

Open questions (JSONL / Mongo `deborah_open_questions`):

```python
from deborah.runtime.open_questions import OpenQuestionStore, open_question_from_run
# or CLI: deborah-run --list-open-questions path.jsonl [--json]
```

---

## CLI surface (host automation)

```bash
deborah-validate plan.cairn.md --profile strict
deborah-run plan.cairn.md --slice --estate-demo --check-contracts \
  --negotiator auto --decision open --open-questions oq.jsonl --trace
deborah-run plan.cairn.md --slice --estate-live --open-questions-mongo
deborah-run --list-open-questions oq.jsonl --plan-id plan_…
deborah-run plan.cairn.md --slice --no-post-retrieve-negotiate   # single-pass
```

Exit: prefer treating `complete` and `open` as successful process outcomes;
`refused` / `blocked` as hard failure unless host policy says otherwise.

---

## Interop checklist (Tirzah)

1. Convert with `tirzah.planning.to_deborah_plan` (or emit Deborah-clean JSON).  
2. `validate_against_deborah(plan, profile="full")` → empty errors.  
3. If framed → `run_framed_plan(..., tracer=session_tracer, open_questions_db=db)`.  
4. Else → Tirzah `interpret_plan` agentic executor.  
5. Share one Galeed `Tracer` session across invent + framed walk.  
6. Pin `deborah>=0.23.3`, `galeed>=0.3.2`.

---

## Anti-patterns (reject or rewrite)

| Pattern | Problem |
|---|---|
| Unbounded `while` search in one STEP | Violates crystallisation / optimize stop_rule |
| `COGNITION: decide` on bare `STEP` under strict | Use `DECISION` |
| Silent accept on empty evidence | Outcomes / post_retrieve should open |
| Dual local PLAN dialects | Deborah is schema authority |
| Emitting only RECURSE without CALL tools | No grounded work; host may fallback_plan |
| Negotiation with `force_agreement: true` | Forbidden by contract |

---

## Versioning

- **Language SPEC** (SPEC.md) and **package** (`deborah.__version__`) are independent.  
- Prefer pinning package minors when estate adapters depend on spine fields
  (e.g. post_retrieve `note`, slice phase events).

---

## Quick self-test for an emitting model

Before returning a plan to the host, assert mentally (or via tools):

1. `validate_plan(plan) == []`  
2. Every CALL tool appears in ASSUMES (strict)  
3. Empty observe is representable  
4. Decide path can select `open`  
5. No step requires free re-planning to succeed  
6. Intent string is non-empty and specific  

If any fail: repair JSON or defer to host `fallback_plan` / human author.
