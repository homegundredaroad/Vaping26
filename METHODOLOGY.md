# Methodology

Vaping26 separates **collection, interpretation and publication**. The public repository is the audited publication surface; collection rules, credentials and unresolved investigative work remain in a private feeder repository.

## Evidence pipeline

1. Source registration and evidence-role assignment
2. Collection or official-resource capture
3. Immutable raw snapshot/hash where practical
4. Schema and non-empty-response validation
5. Normalisation and canonical identifiers
6. Cross-source reconciliation and deduplication
7. Source-health and coverage audit
8. Evidence classification and analysis
9. Publication review
10. Deny-by-default sanitisation/disclosure checks
11. Public manifest generation and release

## Health and scientific evidence

Bibliographic surveillance uses multiple sources rather than treating one index as complete. Duplicate publications are reconciled using identifiers such as PMID and DOI, with a conservative title/year fallback. Registered clinical trials are kept distinct from publications and outcomes.

Health evidence will be assessed for study design, population, smoking history, exclusive/dual use, exposure duration, comparator, outcomes, confounding, funding and limitations. Study design or publication count is not treated as an automatic truth score.

## Prevalence evidence

Official ONS and NHS statistical resources can be captured and hashed before table extraction. A captured workbook is source evidence, but its numerical interpretation is a separate, testable stage. Survey changes, definitions and comparability warnings must remain attached to derived estimates.

## Retail and product evidence

Retailer or product records may be observed, candidate-matched, unresolved or verified. Companies House search results are candidate companies rather than a physical-shop census. Automated entity/product matching never establishes illegality or misconduct. Public statements of non-compliance require suitable authoritative evidence.

## Enforcement and media evidence

Official enforcement events are attributed to the originating authority. News and social-media material are discovery/context streams only unless corroborated; they do not independently establish criminality, product illegality or causation.

## Reproducibility

Generated public outputs include a source register, source-coverage summary and SHA-256 publication manifest. See `AUDITABILITY.md` for the public audit surface and its limits.
