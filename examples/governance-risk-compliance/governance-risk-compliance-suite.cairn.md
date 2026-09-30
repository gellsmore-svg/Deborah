# Governance, Risk, And Compliance Suite

Worked Cairn examples for governance, risk, compliance, speak-up, audit, policy,
and assurance processes. These examples are process-design patterns, not legal
or regulatory advice.

## PROCESS - AI Model Risk And Governance Review

```cairn
PROCESS AIModelRiskGovernanceReview (INPUT: proposed_ai_system; OUTPUT: approved_rejected_or_remediated_ai_use)
  1. Classify use case, affected groups, decision rights, and regulatory exposure. [HUMAN, GATED]
     PURPOSE: make model risk visible before technical momentum makes reversal difficult.
     HUMAN_DEMAND:
       ORIENT: understand who may be affected and what decision the AI influences.
       ACT: classify risk, name accountable owner, and decide whether deeper review is required.
       CLOSE: see review route, evidence requirements, and next owner.
     HUMAN_FACTORS:
       cognitive_load: risk classification combines law, ethics, business context, data quality, and model behavior.
       social_role: product teams may feel review threatens delivery status.

  2. Gather evidence on data, model behavior, human oversight, security, privacy, and contestability. [HUMAN, ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       role_complementarity: AI can organize evidence and missing artifacts; humans judge context and risk appetite.
       automation_bias: do not let a confident model card hide weak test coverage or unclear accountability.
     SUPPORT: show source evidence, unresolved gaps, and confidence separately.

  3. Run governance board decision with dissent and conditions captured. [HUMAN, GATED]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: weak governance can create customer harm, legal exposure, and loss of trust.
     GAME [KIND: principal_agent] of approval vs residual risk. [INCENTIVE]
     PLAY [MOVE: defect] as minimized risk language. [INCENTIVE]
     SIGNAL [COST: costly] if dissent and residual-risk ownership are required. [INCENTIVE]

  4. Track conditions, monitoring, incidents, and periodic re-review. [SERVICE, ASYNC]
     HCI_TOUCHPOINT:
       phase: closure
       human_goal: know whether approval conditions are satisfied and what changed since approval.
     CHANGE_IMPACT:
       reinforcement: governance must become a living control, not a one-time approval ceremony.
```

## PROCESS - Data Privacy Incident Triage

```cairn
PROCESS DataPrivacyIncidentTriage (INPUT: possible_data_incident; OUTPUT: contained_assessed_and_notified_incident)
  1. Receive report and separate immediate containment from legal assessment. [HUMAN, GATED]
     HUMAN_DEMAND:
       ORIENT: identify system, data type, affected population, and current exposure.
       ACT: contain access, preserve evidence, and notify the right response roles.
       RECOVER: correct mistaken reports without shaming reporters.
     HUMAN_FACTORS:
       stress_response: urgency and fear can cause premature conclusions.
       trust: people report faster when the route is clear and non-punitive.

  2. Build factual timeline from logs, access records, user reports, and system changes. [CODE, READONLY]
     HCI_TOUCHPOINT:
       phase: execution
       human_goal: inspect evidence without copying sensitive data into unsafe tools.
     CONSTRAINTS: protect confidentiality, privilege, and data minimization boundaries.

  3. Assess severity, notification duties, affected parties, and corrective action. [HUMAN, ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       trust_calibration: AI may summarize comparable obligations, but legal owner decides.
       bias_mitigation: low-volume incidents can still be high impact when data sensitivity is high.
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: delay, under-classification, or over-disclosure can each cause harm.

  4. Communicate outcome, remediate controls, and update playbook. [FEEDBACK]
     SUPPORT: provide reporter acknowledgement, owner, next action, and closure evidence.
```

## PROCESS - Internal Audit Finding Remediation

```cairn
PROCESS InternalAuditFindingRemediation (INPUT: audit_finding; OUTPUT: verified_control_improvement)
  1. Translate finding into risk, root cause, control owner, and expected evidence. [HUMAN, GATED]
     HUMAN_FACTORS:
       cognitive_load: audit language can obscure what operational change is actually required.
       social_role: control owners can experience findings as personal criticism.
     SUPPORT: distinguish observation, risk, requirement, action, evidence, and due date.

  2. Agree management action plan and realistic remediation path. [HUMAN, GATED]
     GAME [KIND: principal_agent] of wording vs residual risk. [INCENTIVE]
     PLAY [MOVE: defect] as cosmetic actions. [INCENTIVE]
     SIGNAL [COST: costly] if evidence must be independently verified. [INCENTIVE]
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: high
       rationale: unresolved findings accumulate into governance fatigue and repeated failure.

  3. Execute remediation and collect evidence. [HUMAN, ASYNC]
     HCI_TOUCHPOINT:
       phase: execution
       human_goal: know what evidence counts without hunting through policies, tickets, and shared drives.
     FUNCTIONAL_LAYOUT_LOAD:
       related_fields: finding, action, owner, due date, evidence, status, and verifier should remain visually adjacent.
       recovery_cost: high if evidence is scattered across disconnected systems.

  4. Verify effectiveness and close or reopen. [HUMAN, GATED]
     CHANGE_IMPACT:
       reinforcement: closure should confirm changed control behavior, not only uploaded artifacts.
```

## PROCESS - Regulatory Change Impact Assessment

```cairn
PROCESS RegulatoryChangeImpactAssessment (INPUT: regulatory_or_policy_change; OUTPUT: assessed_and_owned_change_response)
  1. Detect change and summarize affected obligations, dates, jurisdictions, and business areas. [ASSISTED-BY: LLM, READONLY]
     AUGMENTATION_PROCESS:
       role_complementarity: AI can draft comparison and issue map; accountable specialists verify meaning.
       automation_bias: never treat a generated legal interpretation as authoritative without review.

  2. Map obligations to products, processes, controls, data, vendors, and people. [HUMAN, GATED]
     HUMAN_DEMAND:
       ORIENT: understand what changed and why it matters.
       ACT: map impact, assign owners, and select response path.
       CLOSE: see accountable owners, deadlines, and unresolved ambiguity.
     HUMAN_FACTORS:
       ambiguity_tolerance: uncertain rules can create delay or over-engineered responses.

  3. Prioritize response using probability, impact, readiness, and customer effect. [HUMAN, ASSISTED-BY: risk_register]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: misread obligations can cause non-compliance, wasted effort, or customer disruption.

  4. Implement, train, attest, and monitor. [ITERATIVE]
     CHANGE_IMPACT:
       adaptation: update procedures, UI labels, evidence capture, support scripts, and audit tests.
```

## PROCESS - Third-Party Risk And Due Diligence

```cairn
PROCESS ThirdPartyRiskDueDiligence (INPUT: proposed_supplier_or_partner; OUTPUT: approved_rejected_or_conditioned_relationship)
  1. Classify supplier criticality, data access, service dependency, geography, and concentration risk. [HUMAN, GATED]
     HUMAN_FACTORS:
       loss_aversion: commercial pressure may make a risky supplier feel too costly to challenge.
       social_role: procurement, security, legal, and business owners may optimize for different outcomes.

  2. Collect questionnaires, attestations, contracts, security evidence, financial indicators, and operational dependencies. [HUMAN, ASSISTED-BY: LLM]
     HCI_TOUCHPOINT:
       phase: execution
       human_goal: compare evidence quality without drowning in attachments.
     FUNCTIONAL_LAYOUT_LOAD:
       evidence_to_action: remediation actions should sit beside the exact missing or weak evidence.

  3. Decide approval, conditions, monitoring, exit plan, or rejection. [HUMAN, GATED]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: weak third-party decisions can import security, continuity, ethical, and customer harms.
     GAME [KIND: principal_agent] of vendor evidence. [INCENTIVE]
     SIGNAL [COST: cheap] of polished incomplete packs. [INCENTIVE]
     SIGNAL [COST: costly] if critical-evidence checks are required. [INCENTIVE]

  4. Monitor changes, incidents, renewals, and offboarding. [SERVICE, ASYNC]
     SUPPORT: expose renewal dates, contract duties, live incidents, and exit readiness in one view.
```

## PROCESS - Speak-Up Concern Handling

```cairn
PROCESS SpeakUpConcernHandling (INPUT: employee_or_stakeholder_concern; OUTPUT: protected_triaged_and_resolved_concern)
  1. Provide safe, accessible, confidential reporting route. [HUMAN, GATED]
     HUMAN_DEMAND:
       ORIENT: know what can be reported and whether anonymity is possible.
       ACT: submit concern, evidence, parties, urgency, and preferred contact boundary.
       CLOSE: receive acknowledgement without exposing identity unnecessarily.
     HUMAN_FACTORS:
       psychological_safety: fear of retaliation is often the central workload, not form completion.
       social_role: power distance can silence valid concerns.

  2. Triage concern type, urgency, conflict of interest, and protection needs. [HUMAN, GATED]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: high
       rationale: mishandled concerns can harm the reporter, accused person, witnesses, and organisational trust.
     SUPPORT: separate confidentiality, investigation scope, welfare support, and anti-retaliation monitoring.

  3. Investigate with procedural fairness and minimal necessary disclosure. [HUMAN, READONLY]
     GAME [KIND: principal_agent] of investigation vs power. [INCENTIVE]
     PLAY [MOVE: defect] as narrative-shaping or witness-discouragement. [INCENTIVE]
     SIGNAL [COST: costly] of conflict checks, evidence log, and independent oversight. [INCENTIVE]

  4. Communicate outcome at the right level and monitor retaliation risk. [FEEDBACK]
     HCI_TOUCHPOINT:
       phase: closure
       human_goal: understand that the concern was handled without requiring unsafe disclosure of private findings.
```

## PROCESS - Policy Exception And Waiver Review

```cairn
PROCESS PolicyExceptionWaiverReview (INPUT: requested_exception; OUTPUT: approved_rejected_or_expired_exception)
  1. Capture requested exception, policy conflict, business rationale, duration, and compensating controls. [HUMAN, GATED]
     HUMAN_FACTORS:
       cognitive_load: policy exceptions fail when the requester cannot tell what evidence is relevant.
       behavioural_economics: a temporary exception can become default through status quo bias.
     HCI_TOUCHPOINT:
       phase: awareness
       human_goal: understand why the policy blocks the action and what alternatives exist.

  2. Assess residual risk, dependency, reversibility, and precedent. [HUMAN, ASSISTED-BY: risk_register]
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       rationale: exceptions can silently weaken controls when expiry and ownership are unclear.

  3. Approve with conditions or reject with rationale and alternatives. [HUMAN, GATED]
     SUPPORT: show decision, expiry, owner, compensating control, review date, and appeal path.

  4. Monitor expiry, renewal, closure, or conversion into policy change. [SERVICE, ASYNC]
     CHANGE_IMPACT:
       adaptation: repeated exceptions may signal that the policy, tool, or process no longer fits reality.
```

## PROCESS - Business Continuity And Crisis Governance Exercise

```cairn
PROCESS BusinessContinuityCrisisGovernanceExercise (INPUT: disruption_scenario; OUTPUT: tested_response_and_improvement_plan)
  1. Define scenario, critical services, dependencies, decision roles, and welfare assumptions. [HUMAN, GATED]
     HUMAN_FACTORS:
       stress_response: crisis exercises should test degraded cognition, not ideal meeting behavior.
       occupational_health: fatigue, safety, and trauma exposure are part of continuity risk.

  2. Run exercise through alerts, escalation, decision cadence, communication, and recovery. [HUMAN, SIMULATED]
     HUMAN_DEMAND:
       ORIENT: know current facts, uncertainty, and decision authority.
       ACT: prioritize actions, allocate scarce attention, and communicate.
       RECOVER: hand over, rest, debrief, and restore normal governance.
     HCI_TOUCHPOINT:
       phase: execution
       human_goal: see situation, decisions, owners, customer impact, and staff welfare without tool switching.

  3. Compare performance to recovery objectives and human-system limits. [HUMAN, ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       role_complementarity: AI can summarize timeline and decision gaps; humans interpret context and welfare impact.

  4. Update plans, contact lists, escalation paths, and training. [FEEDBACK]
     CHANGE_IMPACT:
       reinforcement: exercise learning must alter tools, rosters, delegation, and recovery evidence.
```

## PROCESS - Records Retention And Legal Hold

```cairn
PROCESS RecordsRetentionLegalHold (INPUT: record_class_or_legal_hold_trigger; OUTPUT: retained_preserved_or_disposed_records)
  1. Identify record class, retention rule, legal hold trigger, custodians, and systems. [HUMAN, GATED]
     HUMAN_FACTORS:
       cognitive_load: employees rarely know retention classes without contextual help.
       trust: legal hold language can create fear if duties and limits are unclear.

  2. Preserve relevant records and suspend disposal where required. [CODE, SIDE-EFFECT]
     HCI_TOUCHPOINT:
       phase: execution
       human_goal: confirm preservation without needing to understand every storage backend.
     CONSTRAINTS: preserve chain of custody, access control, and audit trail.

  3. Notify custodians and support compliance without over-collection. [HUMAN, ASYNC]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: missed holds, over-retention, or unclear instructions can create legal and privacy harm.
     SUPPORT: clear instructions, examples, help route, and confirmation state.

  4. Release hold or dispose according to approved retention rules. [HUMAN, GATED]
     CHANGE_IMPACT:
       reinforcement: records governance should reduce decision burden through default rules and visible exceptions.
```

## PROCESS - Sustainability Claim Assurance

```cairn
PROCESS SustainabilityClaimAssurance (INPUT: proposed_public_sustainability_claim; OUTPUT: substantiated_revised_or_rejected_claim)
  1. Capture claim wording, audience, channel, metric, boundary, and source evidence. [HUMAN, GATED]
     HUMAN_FACTORS:
       social_proof: teams may copy market language that is not supported by their own evidence.
       cognitive_load: environmental claims combine technical measurement, legal risk, and reputation.

  2. Validate evidence quality, assumptions, calculation boundary, and uncertainty. [HUMAN, ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       role_complementarity: AI can compare claim language against evidence gaps; reviewers validate data and rules.
       automation_bias: persuasive wording should not substitute for substantiation.
     FUNCTIONAL_LAYOUT_LOAD:
       evidence_to_action: reviewers need claim sentence, metric source, calculation note, and required edit together.

  3. Approve, revise, qualify, or reject claim. [HUMAN, GATED]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: unsupported claims can create regulatory, customer, employee, and reputational harm.

  4. Publish with evidence record and monitor future changes. [FEEDBACK]
     SUPPORT: retain approved wording, evidence, owner, expiry, and trigger conditions for re-review.
```
