# External auditability

Vaping26 is designed so public claims can be inspected without publishing credentials, raw investigative material or unresolved product/retailer leads.

## Public audit surface

A validated publication may contain:

- `data/public/research_status.json` — aggregate collector and run status;
- `provenance/source_register.json` — source roles, authorities and implementation states;
- `provenance/source_coverage.json` — run-level source attempts/successes;
- `evidence/health_evidence_summary.json` — literature/trial/synthesis-readiness summaries;
- `evidence/ons_prevalence.json` — validated adult ONS estimates when available;
- `evidence/youth_prevalence.json` — approved official youth indicators when available;
- `evidence/evidence_cards.json` — publication-safe bibliographic/classification cards when available;
- `evidence/synthesis_register.json` — pre-specified research questions and readiness status when available;
- `regulation/timeline.json` — source-qualified regulatory milestones;
- `provenance/release_evidence.json` — compact run/code/source-snapshot provenance when available;
- `provenance/publication_manifest.json` — SHA-256 hashes and byte sizes for generated public files.

The public validator rejects forbidden private paths and common credential patterns and requires generated public files to be covered by the publication manifest.

## Deliberately private

Raw downloads, full-text working material, API credentials, unpublished discovery leads, unresolved retailer/product matches, private matching rules, investigation notes and notebooks remain in the feeder Research repository.

## Interpretation rules

- A successful API response is not automatically reliable evidence.
- Companies House candidates do not establish physical vape shops or wrongdoing.
- News/media results are discovery/context only until corroborated.
- A registered/completed trial does not itself establish a published result.
- Literature counts and evidence-card counts are not effect estimates or certainty ratings.
- Automated product matching never establishes illegality.
- AI extraction cannot create a public causal or safety conclusion without source-grounded validation and review.

## Change control

Methodology and generated evidence are version controlled. Cross-repository publication is deny-by-default and only allowlisted aggregate/provenance roots can pass from the private feeder into the public repository.
