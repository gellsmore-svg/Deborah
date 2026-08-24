# Scenario routing

Match the user request to a row. Open the listed example in the Deborah
checkout when you need a pattern; do not copy the whole example into the
reply. Paths are relative to the Deborah repo root.

Prefer the first matching row. Mix CONTEXT + REQUIREMENTS + PROCESS in one
document rather than stacking every construct. PLAN only when the work will
be validated or walked.

| If they want… | Write | Start from |
|---|---|---|
| Fill / complete **business-process documentation** from notes, a template, or an interview (SOP, exception queue, AP/PO, finance close, handoffs) | CONTEXT (trigger, systems, roles) + REQUIREMENTS + narrative PROCESS; exceptions as later steps or ERROR; judgement = `[HUMAN, GATED]` / DECISION. Do not raise to PLAN unless they asked to walk it | `examples/accounts-payable-exception.cairn.md`, `examples/customer-po-review.cairn.md`, `examples/corporate/business-lifecycle-suite.cairn.md` |
| Represent **code** as abstract logical language (not a new programming language, not a source rewrite) | CONTEXT (components, stores — not imports), REQUIREMENTS (testable invariants), PROCESS of **control flow and durability**; `[CODE, DETERMINISTIC]` vs `[LLM, STOCHASTIC]` only where true; STATE for stores; CALL/SERVICE for other processes — do not inline their graphs | `examples/hoglah-execution.cairn.md` (code-backed), `examples/hoglah-submit.cairn.md` |
| Corporate lifecycle slice (intake, MVP, sales, procurement, HR, close, …) | Same as business process; pick the matching PROCESS in the suite rather than one megadoc | `examples/corporate/business-lifecycle-suite.cairn.md` |
| Requirements / design-doc backbone | REQUIREMENTS with `R#` + ACCEPTANCE; PROCESS steps `[SATISFIES: Rn]` | SPEC §1; any example with REQUIREMENTS |
| Architecture / runtime topology | PROCESS + SERVICE + QUEUE + AWAIT; skip line-by-line dump | `examples/hoglah.cairn.md`, `examples/hoglah-submit.cairn.md` |
| Intended vs implemented process | Two PROCESS blocks or two files; REQUIREMENTS as the shared assertions | code-backed Hoglah trio vs higher-level `hoglah.cairn.md` |
| Agentic / tool-using LLM workflow | PLAN with INTENT, OUTCOMES, ASSUMES, ON_UNCERTAINTY; CALL + COGNITION; mixed DETERMINISTIC/STOCHASTIC | `examples/cross-llm-critique.cairn.md`, `examples/technical-agentic/technical-agentic-suite.cairn.md` |
| Observe → infer → evaluate → decide / `open` (critique walk) | PLAN + COGNITION tokens; `open` is an allowed terminal | `examples/cross-llm-critique.cairn.md` |
| Human approval, HITL, review gate | `[HUMAN, GATED]` and/or DECISION; HUMAN_DEMAND if load matters | `examples/codex-review-gate.cairn.md`, CI/CD and incident slices in the technical-agentic suite |
| Incident, CI/CD, multi-agent research | PROCESS with PARALLEL, FEEDBACK, GATED | `examples/technical-agentic/technical-agentic-suite.cairn.md` |
| Queues, retries, async workers, data/event pipelines | QUEUE, RETRY, AWAIT, ERROR, SERVICE | `examples/round-robin-debate.cairn.md`, Hoglah examples |
| Multi-party debate / turn-taking | QUEUE with round-robin discipline (not SAMPLE, not PARALLEL-as-debate) | `examples/round-robin-debate.cairn.md` |
| Parallel work then combine | PARALLEL then MERGE | any PROCESS that fans out then joins |
| Isolated reconstructions of one source | SAMPLE + VIEW + `MERGE [RULE: admissibility]`. Describes the method; the Multipath skill *runs* it | `examples/independent-reconstruction.cairn.md` |
| GRC, audit, policy exception, privacy incident | REQUIREMENTS + PROCESS; audit render profile | `examples/governance-risk-compliance/governance-risk-compliance-suite.cairn.md` |
| Org change, stakeholders, culture | ALIGN, COALITION, RESISTANCE, … (extension; core runtime may skip) | `examples/org-*.cairn.md`, `examples/org-change/` |
| Psychological / sociological work interface | Extension constructs; say it is descriptive, not a clinical protocol | `examples/psychological/`, `examples/sociological/`, `examples/psych-*.cairn.md`, `examples/socio-*.cairn.md` |
| Psych + org + socio in one change story | One PROCESS mixing extension constructs; note that a core runtime may skip them | `examples/cross-domain-org-change.cairn.md` |
| Occupational health / safety | PROCESS + FEEDBACK; `RISKS:` / `HUMAN_DEMAND:` annotations as needed | `examples/occupational-health/` |
| Crystallise messy notes / a negotiation into something walkable | PLAN REVISION with REQUEST, INTENT, ASSUMES, ON_UNCERTAINTY | `examples/tirzah-plan-interpreter.cairn.md`, `examples/tirzah-recursive-planning.cairn.md` |
| Revise or patch existing Cairn | Same modes as the source; bump PLAN REVISION if it is a PLAN; do not restyle or add constructs unless asked | the file they provided |
| Validate / fix a Cairn document | Run `deborah-validate`; fix grammar only; do not raise formality | — |
| What is Deborah / how do I write Cairn | Do not dump SPEC. Follow this skill; if they want a demo, emit a tiny CONTEXT + PROCESS | `docs/GUIDE-AI.md`, `examples/README.md` |
| Audience-specific view of an existing Cairn doc | Do not rewrite the source; `deborah-render --profile …` | profiles in SKILL.md |
| Simulate / contract-check a PLAN | `deborah-run` / `interpret_plan` with stubs unless they asked for a real estate | `docs/usage-modes.md` Mode 3 |
| Frame a capability another LLM will call | ASSUMES pins + CALL; schemas live in Keturah | `examples/keturah.cairn.md` |

If nothing matches: still write a short CONTEXT + PROCESS. Prefer fewer
constructs over a kitchen-sink document.
