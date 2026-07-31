# Incoming Customer PO Review

```cairn
CONTEXT
Incoming customer PO - a purchase order received from a customer through email, portal upload, EDI, or manual entry.
Order coordinator - the operator who checks whether the PO can become a valid sales order.
ERP order record - the internal order state that downstream fulfilment, finance, and customer service rely on.
Layout load - cognitive and motor effort caused by the spatial arrangement of fields, evidence, warnings, and actions.

REQUIREMENTS
R1. The coordinator must see customer identity, PO number, duplicate status, commercial terms, delivery date, and line exceptions before accepting the PO. [MUST]
R2. Duplicate, stale, incomplete, or conflicting PO data must be visible before the accept action. [MUST]
R3. The system must leave an audit trail showing evidence viewed, decision, reason, owner, and downstream handoff. [MUST]
R4. The UI must minimize avoidable scan distance between related fields, warnings, evidence, and actions. [SHOULD]

OUTCOMES
Routine POs become sales orders without hidden rework.
Risky or incomplete POs are corrected or escalated before fulfilment commits.
Operators can review POs without excessive memory, eye travel, pointer travel, or uncertainty loops.

PROCESS ReviewIncomingCustomerPO (INPUT: incoming_po; OUTPUT: po_review_outcome)
  1. Detect and classify the incoming PO. [CODE, DETERMINISTIC, ASYNC]
     PURPOSE: create a review item only when the PO needs human confirmation or exception handling.
     OUTPUT: po_review_case

  2. Show the PO review item in the coordinator queue. [UI, HUMAN: order coordinator]
     PURPOSE: bring one customer PO into awareness with enough context to choose the next action.
     HUMAN_DEMAND:
       ORIENT: notice the queue item, customer, age, due date, duplicate risk, and exception status.
       ACT: decide whether to open now, defer, or route to another owner.
       CLOSE: see that the item has moved into active review or remains safely queued.
       RECOVER: defer or reassign without losing why the PO matters.
     HCI_TOUCHPOINT:
       phase: awareness
       ui_surface: customer PO review queue
       human_goal: choose the next PO to review without reading every row in detail.
       cognitive_aesthetic: risk, age, customer, and next action should dominate over decorative status chips.
     HUMAN_LOAD:
       focus_actions: 3
       business_actions: 1
       trivial_actions: 2
       explicit_decisions: 1
       context_switches: 0
       closure_clarity: medium
     HUMAN_FACTORS:
       cognitive_load: vigilance and prioritisation load in the review queue.
       interface_friction: weak row hierarchy can make the operator scan irrelevant metadata.
     SUPPORT: show customer, PO number, duplicate indicator, exception count, age, due date, and owner in one row.
     FAILURE_MODE: vague queue rows create queue fatigue and late discovery of duplicate or urgent POs.

  3. Review customer, PO identity, duplicate risk, and commercial evidence. [HUMAN: order coordinator, GATED]
     PURPOSE: decide whether the incoming PO can safely become a sales order or needs repair/escalation.
     HUMAN_DEMAND:
       ORIENT: understand customer identity, PO source, system match confidence, duplicate warning, line/price exceptions, and required next action.
       ACT: compare PO header, customer account, existing orders, commercial terms, delivery requirements, and line exceptions.
       CLOSE: reach a defensible accept, reject, repair, or escalate judgement.
       RECOVER: request missing information, correct matching, open duplicate evidence, or escalate to sales/finance.
     HCI_TOUCHPOINT:
       phase: orientation
       ui_surface: PO review detail page
       human_goal: understand whether this PO is valid, duplicate, incomplete, or commercially risky.
       weak_context: duplicate warning, customer credit status, line exceptions, and accept/reject actions must not be spatially separated.
     FUNCTIONAL_LAYOUT_LOAD:
       related_field_distance: high when PO number, customer account, duplicate warning, and accept action sit in separate regions.
       label_field_distance: medium when labels sit far left but fields align in a wide second column.
       evidence_action_distance: high when exception evidence is below the fold and accept/reject actions are pinned top-right.
       cumulative_pointer_travel: medium to high across a large desktop viewport.
       column_complexity: high if header, evidence, and actions occupy three competing visual lanes.
       scan_path_linearity: low if the operator must zig-zag between header, warning panel, line grid, and action bar.
     HUMAN_LOAD:
       focus_actions: 10
       business_actions: 4
       trivial_actions: 6
       explicit_decisions: 4
       context_switches: 3
       uncertainty_loops: 2
       input_burden: medium
       closure_clarity: medium
     HUMAN_FACTORS:
       cognitive_load: working memory burden, comparison load, ambiguity load.
       interface_friction: functional layout load, evidence/action separation, possible multicolumn scan burden.
       social_role: accountability without control if downstream fulfilment depends on this decision.
       behavioural_economics: effort avoidance may favour accepting a plausible-looking PO rather than inspecting distant warnings.
       incentives_game_theory: throughput pressure may compete with careful duplicate and exception review.
     HUMAN_RISK:
       probability: high
       impact: high
       confidence: medium
       score: critical
       rationale: the decision affects customer fulfilment, finance, and downstream rework; spatially separated warnings and actions can reduce effective review capacity.
     SUPPORT: group PO identity, customer match, duplicate warning, exception evidence, and required next action in one decision panel.
     SIMULATION_FINDINGS:
       Functional layout load should be measured with `measureLayout` and `huldah-layout-load`.
       Duplicate warnings must be adjacent to PO identity and the accept/reject action.
       Evidence-to-action distance should be treated as a human-risk cue, not a styling preference.
     IMPROVEMENT:
       Create a primary decision panel containing customer, PO number, duplicate status, exception count, confidence, and next action.
       Place accept/reject/repair/escalate actions beside the evidence that justifies them.
       Collapse secondary metadata until after the operator has resolved identity, duplicate, and exception questions.

  4. Confirm the review decision and record the reason. [HUMAN: order coordinator, SIDE-EFFECT]
     PURPOSE: make the outcome auditable and usable by downstream order processing.
     HUMAN_DEMAND:
       ORIENT: see the available outcomes and their downstream consequences.
       ACT: choose accept, reject, repair, or escalate, then record a reason.
       CLOSE: know the decision has been saved and what system or person receives the handoff.
       RECOVER: edit before final submission or cancel without changing the case.
     HCI_TOUCHPOINT:
       phase: feedback
       ui_surface: decision modal or action panel
       human_goal: complete the decision without losing evidence context.
       cognitive_aesthetic: reason entry should preserve visible evidence and distinguish human reason from AI/system-suggested wording.
     HUMAN_LOAD:
       focus_actions: 5
       business_actions: 2
       trivial_actions: 3
       explicit_decisions: 2
       input_burden: medium
       closure_clarity: medium
     HUMAN_FACTORS:
       interface_friction: blank reason fields create avoidable language burden.
       trust_automation: suggested reasons can anchor the operator if not clearly marked.
       social_role: audit visibility can encourage defensive wording.
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       score: significant
       rationale: reason quality affects audit, customer follow-up, and future exception learning.
     SUPPORT: provide editable reason templates grounded in the selected evidence and outcome.

  5. Show completion and downstream handoff. [CODE, UI, ASYNC]
     PURPOSE: close the mental loop and make the new PO state visible to downstream teams.
     HUMAN_DEMAND:
       ORIENT: see final status, timestamp, owner, and downstream destination.
       ACT: move on, monitor escalation, or reopen if status is wrong.
       CLOSE: queue count decreases and the sales-order or exception state is visible.
       RECOVER: reopen or add a note if the confirmation contradicts the decision.
     HCI_TOUCHPOINT:
       phase: handoff
       ui_surface: queue row, PO timeline, and order status panel
       human_goal: trust that the PO has moved to the correct next state.
     HUMAN_LOAD:
       focus_actions: 1
       business_actions: 0
       trivial_actions: 0
       closure_clarity: high
     SUPPORT: show status, destination, owner, and audit link in the same surface where the task began.
     FAILURE_MODE: unclear handoff creates duplicate checking, anxious re-opening, or downstream surprise.

  6. Review recurring PO intake patterns. [HUMAN: operations lead, ASSISTED-BY: LLM, x:periodic]
     PURPOSE: reduce repeated layout, data-quality, customer, and process defects.
     HUMAN_DEMAND:
       ORIENT: understand repeated duplicate warnings, missing fields, high-layout-load screens, and customer-specific exception patterns.
       ACT: decide whether to change customer onboarding, PO templates, EDI rules, UI grouping, or team process.
       CLOSE: assign improvement actions and see whether exceptions and layout-load findings reduce.
       ADAPT: the team learns from repeated PO friction instead of absorbing it as normal workload.
     CHANGE_IMPACT:
       role_shift: coordinators move from data entry toward exception judgement and customer-data quality feedback.
       adoption_support: training, reversible rollout, visible audit trail, and manager support.
       reinforcement: show reduced duplicate warnings, fewer repairs, and lower functional layout load over time.
```
