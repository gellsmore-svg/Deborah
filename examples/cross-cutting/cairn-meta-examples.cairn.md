# Cross-Cutting Cairn Meta Examples

Examples showing Cairn being used to analyze or expand Cairn-like work.

## PROCESS — Manual Agent Analysis With Cairn Harness

```cairn
PROCESS ManualAgentAnalysisWithHarness (INPUT: repo_or_process_and_evidence; OUTPUT: cairn_analysis_report)
  1. Generate deterministic harness plan. [CODE, DETERMINISTIC]
     TOOLING: huldah-agent-harness-plan --process process.cairn.md --ui-evidence ui.json --check-files
     PURPOSE: decide which Cairn tools can run before the agent interprets the evidence.

  2. Run planned Cairn validation and analysis commands. [TOOL, SEQUENTIAL]
     HUMAN_FACTORS:
       cognitive_load: the harness reduces agent and human memory burden by making steps explicit.
       trust_calibration: deterministic outputs are separated from LLM interpretation.

  3. Agent inspects artifacts and source evidence. [LLM, READONLY]
     CONSTRAINTS: separate observed evidence from inference and cite OKF concepts for recommendations.

  4. Produce report, open questions, and next actions. [LLM, ASSISTED-BY: human reviewer]
     HCI_TOUCHPOINT:
       phase: feedback
       human_goal: receive a clear, reviewable analysis rather than an opaque agent conclusion.
```

## PROCESS — Expanding Cairn Example Corpus

```cairn
PROCESS ExpandCairnExampleCorpus (INPUT: example_gap_prompt; OUTPUT: validated_example_library)
  1. Read existing examples, SPEC, GRAMMAR, and OKF concepts. [LLM, READONLY]
     PURPOSE: preserve local style and avoid inventing unsupported constructs.

  2. Plan taxonomy across corporate, change, psychological, sociological, technical, and mapping examples. [LLM]
     HUMAN_FACTORS:
       cognitive_load: taxonomy prevents the corpus from becoming a flat list.
       social_role: examples should help humans and LLMs reason without pathologizing people.

  3. Generate examples with explicit human factors and augmentation lenses. [LLM, ITERATIVE]
     CONSTRAINTS: use descriptive patterns, qualitative risk, support, and traceability.

  4. Validate examples and update indexes. [CODE, DETERMINISTIC]
     TOOLING: python scripts/validate_examples.py

  5. Review whether SPEC or GRAMMAR gaps appeared. [HUMAN, GATED, ASSISTED-BY: LLM]
     OUTPUT: validated examples, mapping notes, proposed spec gaps if any.
```
