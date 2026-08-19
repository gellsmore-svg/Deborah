# Cairn examples

Worked Cairn descriptions of real systems, used to stress-test the Deborah
specification (**SPEC v0.10**). Documents use the Cairn format (`.cairn.md`);
the maintaining package is `deborah`.

**Framing:** examples that model live PLAN propose/execute/revise
(`tirzah-recursive-planning`, `tirzah-plan-interpreter`) illustrate
crystallisation targets — versioned plans for cross-LLM work, not a claim that
stochastic steps become pure functions.

**SPEC v0.11 golden:**
[`cross-llm-critique.cairn.md`](cross-llm-critique.cairn.md) — observe → infer →
evaluate → decide/open with `COGNITION`, PLAN framing, and mixed
DETERMINISTIC/STOCHASTIC steps.

## Expanded Example Library

The example library now includes categorized suites under subfolders. These are
intended as instructive patterns for both humans and LLMs:

- [`corporate/business-lifecycle-suite.cairn.md`](corporate/business-lifecycle-suite.cairn.md) — twelve corporate lifecycle processes: idea intake, concept-to-MVP, sales, finance, support, marketing, procurement, inventory, HR onboarding, close, and end-to-end product lifecycle.
- [`org-change/ai-native-change-suite.cairn.md`](org-change/ai-native-change-suite.cairn.md) — AI-native operating-model redesign, trauma-informed ERP rollout, post-merger integration, ethical AI governance, adaptive change, regenerative purpose, human-AI symbiosis, and hybrid transition.
- [`psychological/psychological-work-interfaces.cairn.md`](psychological/psychological-work-interfaces.cairn.md) — acute stress, non-diagnostic Cluster B pattern interfaces, loss aversion, present bias, and caregiver mental-load spillover.
- [`sociological/sociological-work-interfaces.cairn.md`](sociological/sociological-work-interfaces.cairn.md) — meeting power/status, reputation flow, hybrid belonging, domestic/work boundary negotiation, open-source contribution, customer community, and organisational ritual.
- [`technical-agentic/technical-agentic-suite.cairn.md`](technical-agentic/technical-agentic-suite.cairn.md) — CI/CD governance, incident response, multi-agent research review, accessibility remediation, layout-load optimization, data quality, HITL agents, and live observers.
- [`occupational-health/occupational-health-suite.cairn.md`](occupational-health/occupational-health-suite.cairn.md) — safety management, incident learning, health surveillance/privacy, psychosocial risk, return to work, contractor coordination, ergonomics, and workplace violence response.
- [`governance-risk-compliance/governance-risk-compliance-suite.cairn.md`](governance-risk-compliance/governance-risk-compliance-suite.cairn.md) — AI model governance, privacy incident triage, audit remediation, regulatory change, third-party risk, speak-up, policy exceptions, crisis governance, records holds, and sustainability claim assurance.
- [`cross-cutting/cairn-meta-examples.cairn.md`](cross-cutting/cairn-meta-examples.cairn.md) — manual agent analysis with the Cairn harness and the process of expanding the example corpus.
- [`mappings/human-systems-interface-map.md`](mappings/human-systems-interface-map.md) — OKF-style mapping of psychological, sociological, work, augmentation, and HCI interfaces.
- [`mappings/research-grounding-notes.md`](mappings/research-grounding-notes.md) — concise research lenses used by the expanded examples.
- [`mappings/spec-grammar-review.md`](mappings/spec-grammar-review.md) — review of whether the new examples require SPEC/GRAMMAR changes.

The subfolder examples are included in `scripts/validate_examples.py` via
recursive validation.

| Example | System | Slice |
|---------|--------|-------|
| [`tirzah-system.cairn.md`](tirzah-system.cairn.md) | Tirzah | **Composition:** ingest → ask → observe |
| [`tirzah.cairn.md`](tirzah.cairn.md) | Tirzah | Ask — direct · agentic · deep retrieval |
| [`tirzah-recursive-planning.cairn.md`](tirzah-recursive-planning.cairn.md) | Tirzah | Live PLAN propose → execute → revise |
| [`tirzah-plan-interpreter.cairn.md`](tirzah-plan-interpreter.cairn.md) | Tirzah | Interpretive step walk (SPEC §4.6) |
| [`tirzah-ingest.cairn.md`](tirzah-ingest.cairn.md) | Tirzah | Source ingestion, dead-letter, profile backfill |
| [`tirzah-semantic-review.cairn.md`](tirzah-semantic-review.cairn.md) | Tirzah | Human-gated semantic-edge review queue |
| [`tirzah-generated-output.cairn.md`](tirzah-generated-output.cairn.md) | Tirzah | Generated-output queue → endorse/reject |
| [`tirzah-web-research.cairn.md`](tirzah-web-research.cairn.md) | Tirzah | `--web` search/fetch override on agentic ask |
| [`codex-review-gate.cairn.md`](codex-review-gate.cairn.md) | Codex + family stack | `codex exec --json` with Cairn/Milcah acceptance gate |
| [`customer-po-review.cairn.md`](customer-po-review.cairn.md) | Customer PO intake | HCI touchpoints + functional layout load for incoming purchase order review |
| [`galeed.cairn.md`](galeed.cairn.md) | Galeed | Cross-project trace spine (emit + query) |
| [`keturah.cairn.md`](keturah.cairn.md) | Keturah | LLM interface manifest + MCP projection |
| [`mizpah.cairn.md`](mizpah.cairn.md) | Mizpah | Cross-session trace browser |
| [`hoglah.cairn.md`](hoglah.cairn.md) | Hoglah | Crash-safe bridge (v2: SERVICE, DURABLE-BEFORE) |
| [`hoglah-submit.cairn.md`](hoglah-submit.cairn.md) | Hoglah | Pure submitter / worker daemon topology |
| [`hoglah-execution.cairn.md`](hoglah-execution.cairn.md) | Hoglah | Low-level worker execution (_process_job, claim, retries, dispatch lease, adapter, deliver, recovery) — based on actual source |
| [`mahalath.cairn.md`](mahalath.cairn.md) | Mahalath | Ingest → debate → ontology |
| [`mahlah.cairn.md`](mahlah.cairn.md) | Mahlah | Three-channel conversational UI |
| [`milcah.cairn.md`](milcah.cairn.md) | Milcah | Recursive coherence-pressure rounds |
| [`relational-substrate.cairn.md`](relational-substrate.cairn.md) | Relational Substrate | Grammar sandbox, sequence traces, sweep |
| [`round-robin-debate.cairn.md`](round-robin-debate.cairn.md) | (pattern) | QUEUE ROUND_ROBIN — turn-based multi-LLM debate |
| [`independent-reconstruction.cairn.md`](independent-reconstruction.cairn.md) | (pattern) | SAMPLE + VIEW + MERGE RULE: admissibility — isolated reconstructions, not a debate |

## Psychological Process Examples
- [`psych-gross-emotion-regulation.cairn.md`](psych-gross-emotion-regulation.cairn.md) — Emotion regulation via Gross process model (situation selection through response modulation).
- [`psych-attachment-regulation.cairn.md`](psych-attachment-regulation.cairn.md) — Attachment system activation, proximity seeking, and co/self-regulation.
- [`psych-cognitive-dissonance.cairn.md`](psych-cognitive-dissonance.cairn.md) — Cognitive dissonance detection and reduction strategies.
- [`psych-dual-process-decision.cairn.md`](psych-dual-process-decision.cairn.md) — System 1 vs System 2 decision making under affect.
- [`psych-metacognition.cairn.md`](psych-metacognition.cairn.md) — Metacognitive monitoring and control in learning/problem-solving.
- [`psych-operant-conditioning.cairn.md`](psych-operant-conditioning.cairn.md) — Operant conditioning, reinforcement schedules, and extinction.
- [`psych-self-determination-motivation.cairn.md`](psych-self-determination-motivation.cairn.md) — SDT basic psychological needs and motivation internalization.

## High-Level Organisational Process Examples
- [`org-kotter-8step-change.cairn.md`](org-kotter-8step-change.cairn.md) — Kotter's 8-step model for leading organisational transformation.
- [`org-adkar-individual-change.cairn.md`](org-adkar-individual-change.cairn.md) — ADKAR model for the individual journey in change (Awareness to Reinforcement).
- [`org-lewin-change.cairn.md`](org-lewin-change.cairn.md) — Lewin's Unfreeze-Change-Refreeze model.
- [`org-mckinsey-7s.cairn.md`](org-mckinsey-7s.cairn.md) — McKinsey 7-S alignment for organisational effectiveness.
- [`org-stakeholder-engagement.cairn.md`](org-stakeholder-engagement.cairn.md) — Stakeholder power mapping and tailored engagement.
- [`org-culture-change.cairn.md`](org-culture-change.cairn.md) — Schein's culture levels and change process (artefacts to basic assumptions).

## Sociological Process Examples
- [`socio-symbolic-interaction.cairn.md`](socio-symbolic-interaction.cairn.md) — Symbolic interactionism: meaning-making, role-taking, and self-formation.
- [`socio-socialization.cairn.md`](socio-socialization.cairn.md) — Primary and secondary socialization of norms, values, and roles.
- [`socio-conflict-resolution.cairn.md`](socio-conflict-resolution.cairn.md) — Social conflict processes and pathways to resolution.
- [`socio-norm-formation.cairn.md`](socio-norm-formation.cairn.md) — Emergence, institutionalization, and enforcement of social norms.
- [`socio-social-movements.cairn.md`](socio-social-movements.cairn.md) — Social movement framing, mobilization, and collective action for change.

**Cross-Domain:**
- [`cross-domain-org-change.cairn.md`](cross-domain-org-change.cairn.md) — Example combining psych regulation, org coalition/align, socio socialize/feedback in one process.

Each describes the system **as it currently stands**, exercising CONTEXT,
REQUIREMENTS/OUTCOMES, and PROCESS modes — and is expected to surface gaps that
feed back into [../SPEC.md](../SPEC.md).

New domain constructs (REGULATION, FEEDBACK, MACRO, COALITION, etc.) are exercised
in the psych/org/socio and cross-domain examples. Use `--profile therapeutic` or
`--profile change_leader` when rendering for human-system focused views.
