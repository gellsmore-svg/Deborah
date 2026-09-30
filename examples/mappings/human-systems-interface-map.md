# Human Systems Interface Map

OKF-style semantic mapping for edges between psychological, sociological,
corporate, and augmentation processes.

## Concepts

### Psychological Threat Response
- **Cues**: urgency, ambiguity, public criticism, loss of control, irreversible action.
- **Process interface**: appears in approvals, incidents, customer escalations, and change rollouts.
- **Cairn constructs**: `HUMAN_DEMAND`, `HUMAN_FACTORS`, `HUMAN_RISK`, `REGULATION`, `RECOVER`.
- **Mitigations**: pause points, second review, low-shame escalation, explicit recovery paths.

### Sociological Status And Norm Dynamics
- **Cues**: who speaks first, who can challenge, what gets rewarded, what is punished informally.
- **Process interface**: meetings, governance boards, post-merger integration, AI adoption.
- **Cairn constructs**: `SOCIALIZE`, `COALITION`, `ALIGN`, `FEEDBACK`, `CHANGE_IMPACT`.
- **Mitigations**: decision rules, dissent capture, rotating facilitation, transparent rationale.

### Domestic And Caregiver Load
- **Cues**: invisible planning burden, interruptions, emotional fatigue, schedule rigidity.
- **Process interface**: high-focus tasks, support queues, change training, incident response.
- **Cairn constructs**: `CONTEXT`, `HUMAN_LOAD`, `HUMAN_RISK`, `SUPPORT`, `BOUNDARY`.
- **Mitigations**: async defaults, backup coverage, predictable support, non-surveilling workload design.

### Augmentation Trust Calibration
- **Cues**: AI score without evidence, hidden uncertainty, overconfident summary, ignored override.
- **Process interface**: lead scoring, incident triage, quote approval, hiring, support escalation.
- **Cairn constructs**: `AUGMENTATION_PROCESS`, `ASSISTED-BY`, `HCI_TOUCHPOINT`, `HUMAN_RISK`.
- **Mitigations**: evidence display, challenge path, confidence limits, human audit outcomes.

### Occupational Health And Work Design
- **Cues**: hazard reports, near misses, fatigue, workload strain, psychosocial risk, discomfort, contractor boundary ambiguity.
- **Process interface**: operations, HR, incident response, system rollout, support queues, field work, and AI-assisted monitoring.
- **Cairn constructs**: `HUMAN_RISK`, `SUPPORT`, `CHANGE_IMPACT`, `HCI_TOUCHPOINT`, `FEEDBACK`, `REGULATION`.
- **Mitigations**: worker participation, hierarchy of controls, confidential health boundaries, return-to-work adjustment, and non-retaliatory reporting.

### Governance, Risk, Compliance, And Speak-Up
- **Cues**: ambiguous accountability, fear of blame or retaliation, audit findings, regulatory change, model risk, policy exceptions, legal holds.
- **Process interface**: AI governance boards, privacy incidents, audit remediation, third-party risk, speak-up channels, policy waivers, crisis exercises, and assurance review.
- **Cairn constructs**: `HUMAN_DEMAND`, `HUMAN_RISK`, `GAME` / `PLAY` / `EQUILIBRIUM` / `SIGNAL`, `HCI_TOUCHPOINT`, informal `AUGMENTATION_PROCESS` / `FUNCTIONAL_LAYOUT_LOAD`.
- **Mitigations**: visible decision rights, dissent capture, confidential routes, evidence adjacency, expiry and re-review, independent verification, and non-punitive escalation.

## Relations

- Psychological threat response can amplify sociological status dynamics when a person interprets disagreement as social danger.
- Sociological norms can hide domestic/caregiver load when the group rewards constant availability.
- AI augmentation can reduce cognitive load when evidence is visible, but increase social and psychological risk when it changes status, control, or accountability without explanation.
- HCI layout load becomes a human-systems issue when warnings, evidence, and actions are separated in high-stakes tasks.
- Occupational health risk increases when safety, workload, psychosocial risk, and work design are treated as individual compliance rather than system design.
- Governance risk increases when compliance workflows reward appearance of control more than verified control behavior.
- Speak-up and audit processes degrade when psychological safety, procedural fairness, and evidence traceability are designed as afterthoughts.

## Recommended Cairn Pattern

For any human-facing process step, ask:

1. What must the human notice?
2. What decision or action is actually business-relevant?
3. What UI/system effort is incidental?
4. What psychological state or social context could reduce capacity?
5. What does AI augment, hide, amplify, or bias?
6. What support or recovery path preserves dignity and quality?
