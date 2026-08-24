# Scenario routing

Match the user request to a row. Open the listed example in the Deborah
checkout when you need a pattern; do not copy the whole example into the
reply. Paths are relative to the Deborah repo root.

| If they want… | Write | Start from |
|---|---|---|
| Business process, SOP, exception queue, AP/PO/finance close | CONTEXT + REQUIREMENTS + PROCESS; HUMAN/GATED on judgement steps | `examples/accounts-payable-exception.cairn.md`, `examples/customer-po-review.cairn.md`, `examples/corporate/business-lifecycle-suite.cairn.md` |
| Requirements / design-doc backbone | REQUIREMENTS with `R#` + ACCEPTANCE; PROCESS steps `[SATISFIES: Rn]` | SPEC §1; any example with REQUIREMENTS |
| Represent **code** as abstract logic (not a new programming language) | CONTEXT (components), REQUIREMENTS (invariants), PROCESS of the real control flow; `[CODE, DETERMINISTIC]` vs `[LLM, STOCHASTIC]`; STATE for stores; CALL/SERVICE for other processes | `examples/hoglah-execution.cairn.md` (code-backed), `examples/hoglah-submit.cairn.md` |
| Architecture / runtime topology | PROCESS + SERVICE + QUEUE + AWAIT; skip line-by-line dump | `examples/hoglah.cairn.md`, `examples/hoglah-submit.cairn.md` |
| Agentic / tool-using LLM workflow | PLAN with INTENT, OUTCOMES, ASSUMES, ON_UNCERTAINTY; CALL + COGNITION | `examples/cross-llm-critique.cairn.md`, `examples/technical-agentic/technical-agentic-suite.cairn.md` |
| Human approval, HITL, review gate | `[HUMAN, GATED]` and/or DECISION; HUMAN_DEMAND if load matters | `examples/codex-review-gate.cairn.md`, CI/CD and incident slices in the technical-agentic suite |
| Incident, CI/CD, multi-agent research | PROCESS with PARALLEL, FEEDBACK, GATED | `examples/technical-agentic/technical-agentic-suite.cairn.md` |
| Queues, retries, async workers | QUEUE, RETRY, AWAIT, ERROR, SERVICE | `examples/round-robin-debate.cairn.md`, Hoglah examples |
| Parallel work then combine | PARALLEL then MERGE; isolated reconstructions use SAMPLE + VIEW + `MERGE [RULE: admissibility]` | `examples/independent-reconstruction.cairn.md` |
| GRC, audit, policy exception, privacy incident | REQUIREMENTS + PROCESS; audit render profile | `examples/governance-risk-compliance/governance-risk-compliance-suite.cairn.md` |
| Org change, stakeholders, culture | ALIGN, COALITION, RESISTANCE, … (extension; core runtime may skip) | `examples/org-*.cairn.md`, `examples/org-change/` |
| Psychological / sociological work interface | Extension constructs; say it is descriptive, not a clinical protocol | `examples/psychological/`, `examples/sociological/`, `examples/psych-*.cairn.md`, `examples/socio-*.cairn.md` |
| Occupational health / safety | PROCESS + FEEDBACK + HUMAN_RISK as needed | `examples/occupational-health/` |
| Crystallise messy notes / a negotiation into something walkable | PLAN REVISION with REQUEST, INTENT, ASSUMES, ON_UNCERTAINTY | `examples/tirzah-plan-interpreter.cairn.md`, `examples/tirzah-recursive-planning.cairn.md` |
| Audience-specific view of an existing Cairn doc | Do not rewrite the source; `deborah-render --profile …` | profiles in SKILL.md |
| Simulate / contract-check a PLAN | `deborah-run` / `interpret_plan` with stubs unless they asked for a real estate | `docs/usage-modes.md` Mode 3 |
| Intended vs implemented process | Two PROCESS blocks or two files; REQUIREMENTS as the shared assertions | code-backed Hoglah trio vs higher-level `hoglah.cairn.md` |
| Frame a capability another LLM will call | ASSUMES pins + CALL; schemas live in Keturah | `examples/keturah.cairn.md` |

If nothing matches: still write a short CONTEXT + PROCESS. Prefer fewer
constructs over a kitchen-sink document.
