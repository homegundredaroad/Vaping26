# Methodology

Vaping26 separates **discovery, collection, validation, evidence extraction, human review, synthesis and publication**. The public repository is the audited publication surface; raw records, credentials and unresolved investigative work remain in the private Research engine.

## Evidence pipeline

1. register each source and assign an evidence role;
2. harvest or capture an official resource;
3. preserve source provenance and hashes where practical;
4. validate expected structure and non-empty responses;
5. normalise identifiers and bibliographic metadata;
6. reconcile duplicates conservatively;
7. apply relevance/date/research-integrity checks;
8. create structured evidence cards;
9. map cards to pre-specified synthesis questions;
10. extract population, comparator, outcomes/effect estimates only from source-grounded material;
11. assess methodological limitations and risk of bias;
12. require human review for conclusion-sensitive fields;
13. run the deny-by-default public publication gate;
14. publish a manifest and compact release provenance.

## Evidence cards

Evidence cards are intended to hold identifiers, study design, population, smoking history, dual-use status, intervention/exposure, comparator, outcomes, quantitative estimates, funding/conflicts, publication-integrity status and risk of bias.

Bibliographic fields may be automatically classified only when supported by collected metadata. Quantitative or interpretation-sensitive fields must remain absent or explicitly unverified until source-grounded extraction and review.

## Study design and certainty

Study design is recorded but is not a universal ranking of truth. Assessment should consider the research question plus risk of bias, directness, precision, consistency, comparator quality, confounding control, applicability, funding/conflicts and publication integrity.

## Protocols and post-publication notices

Study protocols describe planned methods and are not treated as completed result-bearing studies. Corrections, errata, corrigenda and retraction notices are retained for provenance/integrity purposes but are also separated from result-bearing study designs. Synthesis candidate counts may report these records for auditability, while result-bearing counts exclude them.

## Comparator discipline

Comparisons with never-users, continuing smokers, former smokers and dual users answer different questions and must not be mixed silently. Smoking-cessation efficacy is analysed separately from other health effects. A result can only enter a synthesis question when its comparator matches that question's eligibility rules.

## Publication-date normalisation

A single `year` field is not sufficient for all bibliographic records. Electronic publication, issue/volume assignment and print publication can differ.

Where source data permit, the Research engine should retain:

- source-reported year;
- electronic-publication date;
- issue/print publication date;
- retrieval date;
- verifying source/identifier;
- date-anomaly or review reason.

A next-year issue assignment can be legitimate for an already-online publication. Such a record should be flagged for date normalisation/review rather than automatically discarded. Dates beyond a reasonable forthcoming-issue window should fail closed or be quarantined pending verification.

## Synthesis-readiness gate

A bibliographic record is not synthesis-ready merely because it has a study-design label.

Conclusion-sensitive synthesis requires question-specific eligibility plus source-grounded population, exposure/intervention, comparator and outcome fields. Quantitative synthesis additionally requires validated estimates and uncertainty measures where applicable. Records marked not reviewed must not be promoted to a conclusion-sensitive ready state.

## External review

Before mature synthesis claims are published, Vaping26 should obtain independent methodological review. Review is intended to find weaknesses rather than provide a ceremonial endorsement.

The public review questions and requested reviewer classifications are documented in `EXTERNAL_REVIEW.md`. Review observations and resulting methodological changes should be recorded so the audit trail shows how criticism affected the project.

## Trials

ClinicalTrials.gov records are kept distinct from publications. The project captures registered outcomes, enrolment, result modules, adverse-event group counts and publication references where available so registry-to-publication reconciliation can be developed.

## Prevalence

ONS adult estimates and youth/school-age indicators are separate statistical series. Geography, age, sex/category, period, confidence intervals, value notes and survey-method changes must be retained before trend comparison.

## Products, retail and enforcement

Companies House or directory records are candidate discovery, not a physical-shop census. Automated product/entity matching never establishes illegality. News/media remain discovery/context unless corroborated. Enforcement findings require authoritative source evidence.

## Bounded machine learning

Machine learning may assist private review prioritisation. The first evidence-side model uses reproducible text features from titles, publication types and available abstracts to propose study-design candidates for human review. It must abstain when support is weak, excludes rare classes without sufficient training examples, and cannot automatically alter an evidence card or synthesis status.

Where training labels are derived from deterministic rules rather than independent expert review, cross-validation is reported as **bootstrap/weak-label reproduction**, not external scientific accuracy. Validation reports per-class precision/recall/F1/support, confusion matrices, a majority-class baseline and high/moderate/abstain coverage. Related publications are kept within the same validation fold where explicit ClinicalTrials.gov publication-family links allow this; unlinked study families remain a recognised leakage risk.

Human-reviewed labels should replace weak labels as the reviewed corpus grows. A separate blind human benchmark must be withheld from training before scientific classification accuracy is claimed. Model scores remain uncalibrated review-prioritisation scores until sufficient independent human-labelled data exist for calibration. ML review queues and human-review ledgers remain private and are not part of the public evidence bundle.

## Bounded AI

AI may assist candidate extraction from licensed source text, but it must attach exact provenance, pass deterministic schema validation and undergo human review before conclusion-sensitive fields enter synthesis. AI may not autonomously determine causation, safety, diagnosis, product illegality, retailer misconduct or criminality.

## Exposure and ambient context

Vaping aerosol/second-hand/third-hand exposure is a core Vaping26 topic. General ambient air-quality, emissions, models or satellite data can only serve as optional background-control information in a justified study design; they cannot identify an individual vaping event.

## Reproducibility

Generated public outputs include a source register, source-coverage audit, SHA-256 publication manifest and compact release-evidence record linking the public release to the Research run/code and source snapshots where available.
