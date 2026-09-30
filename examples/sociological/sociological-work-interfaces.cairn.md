# Sociological Work Interface Suite

Examples for group dynamics, informal systems, and domestic/work interfaces.

## PROCESS — Meeting Power And Status Dynamics

```cairn
PROCESS MeetingPowerStatusDynamics (INPUT: decision_meeting; OUTPUT: legitimate_or_captured_decision)
  1. Establish agenda, roles, and decision rule. [HUMAN, SOCIAL]
     HUMAN_FACTORS:
       power_distance: high-status speakers can set frames before evidence is reviewed.
       social_proof: early agreement can suppress dissent.

  2. Surface evidence and minority views. [HUMAN, GATED]
     SUPPORT: use pre-reads, round-robin input, anonymous concerns, and explicit dissent capture.

  3. Decide and record rationale. [DECISION, SIDE-EFFECT]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: captured decisions appear aligned while hiding unspoken risk.

  4. Review whether dissent was heard and acted on. [FEEDBACK]
```

## PROCESS — Informal Reputation And Gossip Flow

```cairn
PROCESS InformalReputationFlow (INPUT: ambiguous_event; OUTPUT: corrected_or_distorted_reputation)
  1. Ambiguous event is interpreted by witnesses. [SOCIAL, SYMBOLIC]
     HUMAN_FACTORS:
       attribution_bias: people infer character from limited behaviour.
       status: reputation effects differ by role power and group membership.

  2. Story spreads through informal channels. [ASYNC, SOCIAL]
     GAME [STRUCTURE: sequential; KIND: signalling] of inside information. [INCENTIVE]
     SIGNAL [COST: cheap] of the informal story. [INCENTIVE]
     PLAY [MOVE: signal] for status reward. [INCENTIVE]
     INTERPERSONAL [PATTERN: rank] of who may speak. [INTERPERSONAL]

  3. Individual or manager responds. [HUMAN, GATED]
     SUPPORT: separate facts, impact, privacy, and repair path.

  4. Norms either reinforce gossip or shift toward accountable feedback. [EMERGENT]
```

## PROCESS — Inclusion And Belonging In Hybrid Work

```cairn
PROCESS HybridBelongingProcess (INPUT: hybrid_team_interactions; OUTPUT: inclusion_or_exclusion_pattern)
  1. Work interactions occur across office, video, chat, and asynchronous tools. [SOCIAL, UI]
     HCI_TOUCHPOINT:
       phase: awareness
       human_goal: know where decisions and relationship signals happen.
     HUMAN_FACTORS:
       social_presence: remote members may miss informal context and status cues.

  2. Norms form around who gets attention and information. [SOCIALIZE, EMERGENT]
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       rationale: belonging affects retention, voice, and decision quality.

  3. Design inclusive rituals and information defaults. [HUMAN, SUPPORT]
     SUPPORT: decision logs, rotating facilitation, async-first updates, and explicit informal onboarding.

  4. Review participation patterns without reducing people to metrics. [FEEDBACK]
```

## PROCESS — Domestic Stress And Work Boundary Negotiation

```cairn
PROCESS DomesticStressWorkBoundary (INPUT: domestic_stress_and_work_expectations; OUTPUT: negotiated_or_failed_boundary)
  1. Domestic demands collide with work schedule or cognitive load. [HUMAN, CONTEXT]
     HUMAN_FACTORS:
       spillover: strain can move across home and work systems.
       social_norm: employees may hide domestic strain to preserve professional identity.

  2. Employee chooses disclose, compensate, withdraw, or request support. [HUMAN, DECISION]
     GAME [KIND: pd] of disclose vs conceal. [INCENTIVE]
     PLAY [MOVE: defect] as concealment if support requests are punished. [INCENTIVE]
     AVOIDANCE [MODE: behavioral] of asking for help. [AVOIDANT]
     PAYOFF: T>R>P>S for hide vs disclose

  3. Manager negotiates boundary and coverage. [HUMAN, SUPPORT]
     SUPPORT: clarify priority, deadline, coverage, and confidentiality.

  4. Team adjusts work design and norms. [SOCIALIZE, FEEDBACK]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: unmanaged boundary conflict can become burnout, quality loss, or attrition.
```

## PROCESS — Open Source Contribution Norming

```cairn
PROCESS OpenSourceContributionNorming (INPUT: new_contributor_pull_request; OUTPUT: integrated_or_lost_contributor)
  1. Contributor interprets project norms from docs, issues, review tone, and response time. [HUMAN, SOCIAL]
     HCI_TOUCHPOINT:
       phase: awareness
       human_goal: know how to contribute without guessing hidden rules.
     HUMAN_FACTORS:
       belonging: first interaction shapes whether contributor returns.

  2. Maintainers review contribution and communicate standards. [HUMAN, GATED]
     GAME [STRUCTURE: repeated; KIND: pd] of review vs future contribution. [INCENTIVE]
     PLAY [MOVE: punish] as harsh review. [INCENTIVE]
     DISCOUNT [SHAPE: hyperbolic] [REF: now] if maintainers overweight current quality. [HEURISTIC]

  3. Project accepts, requests change, or redirects. [SIDE-EFFECT]
     SUPPORT: provide rationale, next action, and path to successful future contribution.

  4. Norms update through repeated review interactions. [SOCIALIZE, EMERGENT]
```

## PROCESS — Customer Community Signal Flow

```cairn
PROCESS CustomerCommunitySignalFlow (INPUT: community_posts_and_reactions; OUTPUT: product_learning_or_noise)
  1. Customers share workarounds, complaints, praise, and identity signals. [SOCIAL, ASYNC]
     HUMAN_FACTORS:
       social_proof: repeated stories can become perceived truth before product data confirms them.
       reputation: visible response quality affects trust.

  2. Community manager triages signals and escalates patterns. [HUMAN, ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       role_complementarity: AI clusters themes; human detects tone, harm, and relationship context.

  3. Product team decides whether to act, observe, or communicate. [HUMAN, GATED]
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       rationale: loud communities can either reveal real pain or skew prioritisation.

  4. Feed back decision to community. [FEEDBACK]
     SUPPORT: close the loop visibly even when the product decision is no.
```

## PROCESS — Cultural Ritual And Meaning In Organisations

```cairn
PROCESS CulturalRitualMeaning (INPUT: repeated_organizational_ritual; OUTPUT: reinforced_or_changed_meaning)
  1. Group repeats meeting, celebration, review, or story ritual. [SOCIAL, SYMBOLIC]
     HUMAN_FACTORS:
       symbolic_interaction: rituals tell people what is valued more strongly than policy.

  2. Members interpret who is praised, ignored, blamed, or protected. [HUMAN, APPRAISAL]
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       rationale: rituals can reinforce trust or cynicism depending on lived evidence.

  3. Leaders adjust ritual to align values and behaviour. [HUMAN, GATED]
     SUPPORT: change who speaks, what evidence is shown, what is rewarded, and what is repaired.

  4. New meaning stabilizes or is rejected by informal norms. [EMERGENT]
```
