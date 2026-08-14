# External auditability

Vaping26 is designed so that the public claims can be inspected without publishing private credentials, unresolved investigative leads or proprietary collection/matching procedures.

## Public audit surface

After a validated publication run, the public repository may contain:

- `data/public/research_status.json` — aggregate run status and record counts.
- `provenance/source_register.json` — source families, authorities, access types, implementation states and evidence roles.
- `provenance/source_coverage.json` — which registered sources were attempted and whether they produced non-empty validated records.
- `evidence/health_evidence_summary.json` — aggregate bibliographic/trial/source-capture counts, not medical conclusions.
- `provenance/publication_manifest.json` — SHA-256 hashes and byte sizes for every generated public file.

The public validator checks the manifest whenever it exists and rejects forbidden private directory names and common credential patterns.

## Deliberately private

Raw downloads, API credentials, unpublished news leads, unresolved retailer/product matches, matching rules, investigation notes and private notebooks remain in the feeder research system. Their absence from this repository must not be interpreted as evidence that a public conclusion is untraceable: public outputs include source identifiers and publication hashes, while sensitive evidence can be reviewed under appropriate controls where justified.

## Interpretation rules

- A successful API or webpage response does not itself establish reliable evidence; collectors validate expected structure and non-empty records.
- Companies House candidates do not establish physical vape shops or wrongdoing.
- News/media results are discovery/context only until corroborated by appropriate authoritative material.
- A registered or completed clinical trial does not itself establish a published finding.
- Literature counts are not effect estimates, certainty ratings or proof of causation.
- Product or retailer matching never establishes illegality without suitable authoritative evidence.

## Change control

Methodology and generated evidence are version-controlled. Publication output is deny-by-default and only allowlisted aggregate/provenance directories can cross from the private feeder repository into the public repository.
