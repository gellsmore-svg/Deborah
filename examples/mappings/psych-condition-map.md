# Psychological condition and pattern map

Cairn names **process verbs**, not diagnoses. This table maps recognised
diagnostic *groupings* and generally accepted patterns onto those verbs.
`CONDITION_MAP:` is a bibliographic pointer, **not a diagnosis**.

Sources: APA DSM-5-TR (https://dsm.psychiatryonline.org/doi/book/10.1176/appi.books.9780890425787);
chapter overview (https://simpleandpractical.com/dsm-5/); WHO ICD-11 CDDR
(https://www.who.int/publications/i/item/9789240077263); Reed et al. 2019
(https://doi.org/10.1002/wps.20611); grouping table
(https://pmc.ncbi.nlm.nih.gov/articles/PMC7365296/); HiTOP
(https://pmc.ncbi.nlm.nih.gov/articles/PMC6497550/); RDoC
(https://www.nimh.nih.gov/research/research-funded-by-nimh/rdoc/definitions-of-the-rdoc-domains-and-constructs);
Unified Protocol (https://pmc.ncbi.nlm.nih.gov/articles/PMC7215073/);
Process-Based Therapy (https://cpe.psychopen.eu/index.php/cpe/article/view/11987).

Do **not** mint one construct per DSM/ICD code. Coverage of “all recognised
conditions” is **chapter/grouping-complete**, not 193 separate PROCESS files.

## Transdiagnostic backbone

| Framework | Role in Cairn |
|---|---|
| HiTOP spectra | Primary map. Tag `TRANSDIAGNOSTIC` on shared verbs. |
| RDoC domains | Verb selection (Negative Valence → APPRAISAL/AVOIDANCE/REGULATION; Positive Valence → HABIT/APPRAISAL/DISCOUNT; Cognitive Systems → ATTENTION/METACOGNITION/DUAL_PROCESS; Social Processes → INTERPERSONAL; Arousal/Regulatory → REGULATION/HABIT). |
| Unified Protocol (Barlow) | Shared aversive reaction to emotion → APPRAISAL + AVOIDANCE + REGULATION (descriptive). |
| PBT / EEMM (Hofmann & Hayes) | Failed adaptation → eight psych verbs + CORE ITERATE/DECISION/FEEDBACK. |

## DSM-5-TR Section II chapters → verbs

| Chapter | Primary verbs |
|---|---|
| Neurodevelopmental | ATTENTION, HABIT, METACOGNITION, REGULATION |
| Schizophrenia spectrum and other psychotic | APPRAISAL, ATTENTION, METACOGNITION, INTERPERSONAL |
| Bipolar and related | REGULATION, APPRAISAL, HABIT |
| Depressive | APPRAISAL, AVOIDANCE, ATTENTION (bias), REGULATION, ITERATE (rumination) |
| Anxiety | AVOIDANCE, APPRAISAL, ATTENTION (bias), REGULATION, AWAIT |
| Obsessive-compulsive and related | HABIT, AVOIDANCE (safety), APPRAISAL, METACOGNITION, ITERATE |
| Trauma- and stressor-related | AVOIDANCE, APPRAISAL, ATTENTION, REGULATION, INTERPERSONAL |
| Dissociative | ATTENTION, REGULATION, APPRAISAL, METACOGNITION |
| Somatic symptom and related | APPRAISAL, AVOIDANCE, ATTENTION, INTERPERSONAL |
| Feeding and eating | HABIT, AVOIDANCE, APPRAISAL, REGULATION, INTERPERSONAL |
| Elimination | HABIT, REGULATION |
| Sleep-wake | HABIT, REGULATION, ATTENTION |
| Sexual dysfunctions | APPRAISAL, AVOIDANCE, INTERPERSONAL (descriptive only) |
| Gender dysphoria | APPRAISAL, INTERPERSONAL, REGULATION (descriptive process only) |
| Disruptive, impulse-control, and conduct | HABIT, AVOIDANCE, INTERPERSONAL (rank), REGULATION |
| Substance-related and addictive | HABIT, AVOIDANCE, APPRAISAL, DISCOUNT, NUDGE, ACCOUNT |
| Neurocognitive | ATTENTION, METACOGNITION, HABIT; HCI GULF/CHOICE when interface load is the process |
| Personality | INTERPERSONAL, REGULATION, APPRAISAL, AVOIDANCE |
| Paraphilic | HABIT, APPRAISAL, AVOIDANCE — **mapping row only; no example file** |
| Other mental disorders | HiTOP spectrum of closest match |
| Medication-induced movement | CONDITION_MAP + REGULATION TARGET response if modelled at all |
| Other conditions that may be a focus of clinical attention | INTERPERSONAL, CONTEXT |

## ICD-11 Chapter 06 groupings

Map as the DSM table with these deltas: Catatonia → REGULATION TARGET response + AWAIT;
Mood → bipolar + depressive; Disorders specifically associated with stress → trauma;
Bodily distress → somatic + APPRAISAL/ATTENTION; Impulse control → HABIT/DISCOUNT;
Personality (ICD-11 trait model) → INTERPERSONAL + REGULATION rather than categorical names;
Factitious → INTERPERSONAL, APPRAISAL; Pregnancy/puerperium → REGULATION, APPRAISAL, INTERPERSONAL.

## HiTOP spectra

| Spectrum | Verbs |
|---|---|
| Internalizing | AVOIDANCE, APPRAISAL, REGULATION, ATTENTION |
| Thought disorder | APPRAISAL, METACOGNITION, ATTENTION |
| Disinhibited externalizing | HABIT, REGULATION, DISCOUNT |
| Antagonistic externalizing | INTERPERSONAL (rank), REGULATION |
| Detachment | INTERPERSONAL (attachment), AVOIDANCE |
| Somatoform | APPRAISAL, ATTENTION, AVOIDANCE |
| p-factor | tag TRANSDIAGNOSTIC across the eight verbs |

## Patterns that must not become constructs

| Pattern | Representation |
|---|---|
| Vaillant / DSM Defensive Functioning Scale | REGULATION STRATEGY |
| CBT cognitive distortions (Beck) | APPRAISAL + METACOGNITION MONITOR |
| Rumination / worry | ITERATE + APPRAISAL |
| Approach–avoidance / impulsivity | AVOIDANCE + HABIT + ATTENTION MODE bias |
| Intolerance of uncertainty | APPRAISAL + AWAIT |
| Gross emotion-regulation families | existing REGULATION TARGET |
| Attachment | INTERPERSONAL PATTERN attachment (see psych-attachment-regulation) |
