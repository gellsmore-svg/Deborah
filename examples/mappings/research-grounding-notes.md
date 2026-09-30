# Research Grounding Notes For Expanded Examples

These notes summarize the research lenses used by the expanded example library.
They are intentionally concise; they point examples toward concepts rather than
turning Cairn into a literature-review repository.

## AI-Native Organisational Change

- AI adoption changes roles, decision rights, trust, and psychological contracts.
- Human-AI collaboration needs clear accountability, AI literacy, challenge
  paths, and transparency at the point of work.
- Automation bias and algorithmic authority can make human oversight weaker than
  expected unless evidence, uncertainty, and contestability are designed into the workflow.

Source anchors:
- Frontiers / PMC, "Algorithmic anxiety: AI, work, and the evolving psychological contract": https://pmc.ncbi.nlm.nih.gov/articles/PMC12954588/
- Springer AI & Society, "Exploring automation bias in human-AI collaboration": https://link.springer.com/article/10.1007/s00146-025-02422-7
- SIOP TIP, "Examining AI-Driven Organizational Change in I-O Psychology": https://www.siop.org/tip-article/examining-ai-driven-organizational-change-in-i-o-psychology/

## Trauma-Informed And Stress-Aware Change

- Trauma-informed organisational change emphasizes safety, trust, choice,
  collaboration, empowerment, and cultural humility.
- In work processes this maps to predictable change communication, safe recovery
  paths, reduced shame in help-seeking, and pacing that respects depleted capacity.
- Acute stress can narrow attention and reasoning, so high-stakes workflows
  should include pause, support, and reversible action where possible.

Source anchors:
- "Leading Organizations From Burnout to Trauma-Informed Resilience": https://pmc.ncbi.nlm.nih.gov/articles/PMC10940251/
- Institute on Trauma and Trauma-Informed Care, "Trauma-Informed Organizational Change Manual": https://www.dcjs.virginia.gov/sites/dcjs.virginia.gov/files/publications/victims/1_ITTIC_2022_T-I_Organizational_Change_Manual.pdf

## Behavioural Economics And Game Theory

- Loss aversion, sunk cost, status quo bias, salience, social proof, and effort
  avoidance are predictable process risks.
- Incentives and status rewards can make individually rational actions produce
  poor system outcomes.
- Cairn examples should therefore state the incentive pattern, not only the task.
- First-class verbs (SPEC v0.14): `FRAME` `NUDGE` `ACCOUNT` `DISCOUNT`;
  `GAME` `PLAY` `EQUILIBRIUM` `SIGNAL`. Inventories:
  [`be-bias-map.md`](be-bias-map.md), [`gt-game-map.md`](gt-game-map.md).

Source anchors:
- Kahneman & Tversky, prospect theory (1979): https://doi.org/10.2307/1914185
- Camerer-style economic games overview: https://online.ucpress.edu/collabra/article/7/1/19004/116331/Economic-Games-An-Introduction-and-Guide-for

## Sociological And Domestic-Work Interfaces

- Group norms, power, belonging, reputation, and informal information flows shape
  whether formal process is actually followed.
- Domestic and caregiving cognitive load can spill into work capacity. Good
  process design supports flexibility and coverage without turning private life
  into surveillance data.

Source anchors:
- "Cognitive household labor: gender disparities and consequences": https://pmc.ncbi.nlm.nih.gov/articles/PMC11761833/
- IZA Discussion Paper, "Beyond Time: Unveiling the Invisible Burden of Mental Load": https://docs.iza.org/dp17912.pdf
- "Caregiver Employees' Mental Well-Being in Hong Kong": https://pmc.ncbi.nlm.nih.gov/articles/PMC11121220/

## HCI And Functional Layout Load

- Interface decisions create cognitive, perceptual, and motor demands.
- Related evidence and actions should be close enough that users do not need to
  reconstruct meaning from memory.
- Cairn examples should model awareness, orientation, execution, feedback,
  recovery, handoff, and adaptation touchpoints when UI is present.
- First-class verbs (SPEC v0.14): `CHOICE` `GULF` `AFFORDANCE` `FORAGE`.
  `HCI_TOUCHPOINT:` is now a parsed annotation. Hick–Hyman is not “fewer is
  always faster”; visual search is `FORAGE`. Map: [`hci-heuristic-map.md`](hci-heuristic-map.md).

Source anchors:
- CHI 2020, How Relevant is Hick's Law for HCI?: https://doi.org/10.1145/3313831.3376878
- Scheibehenne, Greifeneder & Todd (2010) choice-overload meta-analysis:
  https://www.researchgate.net/publication/48210291_Can_There_Ever_be_Too_Many_Options_A_Meta-analytic_Review_of_Choice_Overload

## Occupational Health And Healthy Work

- Occupational health and safety management should be proactive, participatory,
  and continuously improved, not limited to post-incident compliance.
- Worker participation, hazard identification, prevention/control, education,
  program evaluation, and contractor/host coordination map naturally to Cairn
  process steps and feedback loops.
- Total Worker Health and healthy workplace models extend the lens from injury
  prevention to work design, psychosocial risk, well-being, participation, and
  community/work interface.

Source anchors:
- OSHA Recommended Practices for Safety and Health Programs: https://www.osha.gov/safety-management
- OSHA Worker Participation: https://www.osha.gov/safety-management/worker-participation
- NIOSH Total Worker Health Program: https://www.cdc.gov/niosh/twh/programs/index.html
- WHO Healthy Workplace Framework and Model: https://www.who.int/publications/i/item/who-healthy-workplace-framework-and-model
- ISO 45001 overview: https://www.iso.org/standard/63787.html

## Governance, Compliance, And Assurance Work

- Compliance and governance workflows are human systems: they rely on truthful
  reporting, clear accountability, contestability, proportional evidence, and
  visible follow-through.
- AI governance benefits from risk-based review, mapped accountability,
  monitoring, and challenge paths; generated summaries should support, not
  replace, accountable judgement.
- Compliance management should be maintained and improved as an operating
  system, not reduced to periodic evidence collection.
- Speak-up, audit, privacy incident, and third-party-risk processes carry
  psychological and sociological load because they involve blame risk, power
  asymmetry, reputational stakes, and uncertain evidence.

Source anchors:
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF Core overview: https://airc.nist.gov/airmf-resources/airmf/
- ISO 37301 compliance management systems: https://www.iso.org/standard/75080.html
- OECD AI Principles: https://www.oecd.org/en/topics/sub-issues/ai-principles.html
- EU AI Act overview: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
