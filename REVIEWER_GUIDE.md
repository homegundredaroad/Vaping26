# Vaping26 — Academic & Methodological Reviewer Guide

**Version:** Reviewer Freeze Release  
**Public Repository:** https://github.com/homegundredaroad/Vaping26  
**Public Observatory:** https://homegundredaroad.github.io/Vaping26/  
**Associated Research engine revision:** `5b5500778bf83637e6ec3e8388046cb73789d58d`  
**Associated Research run:** `33306721309`

> **How to identify the exact public build under review:** use the `vaping26-build` fingerprint embedded in the deployed HTML, the shortened **Public build revision** displayed on the Observatory homepage, and the corresponding successful GitHub Actions validation/deployment run. The guide intentionally does not hard-code the current public commit because changing this document would itself create a new commit and make that value stale.

## 1. Executive summary and review scope

Vaping26 is an evidence-ingestion, provenance, auditability and synthesis-readiness observatory for UK vaping and nicotine evidence.

This reviewer freeze exposes the engineering-assurance and methodological-firewall layers for independent academic evaluation. It is not presented as a completed systematic review, clinical guideline, causal inference engine or regulatory authority.

| Evaluation dimension | In scope for assessment | Explicitly out of scope |
| --- | --- | --- |
| **Engineering assurance** | Deterministic pipeline execution, automated deduplication, source tracking, static hardening, release identity and SHA-256 publication integrity. | Performance optimisation or aesthetic preferences unrelated to scientific interpretation. |
| **Pipeline & auditability** | Data ingestion, canonical-record handling, source provenance, publication manifests, reviewer-facing reproducibility controls. | Pooled effect estimates or meta-analytic conclusions. |
| **Scientific governance** | Firewalls prohibiting unreviewed AI/automation from increasing evidential status; separation of discovery, review and synthesis. | Automated causal assertions, safety verdicts or clinical recommendations. |
| **Methodological design** | Study-design taxonomy, publication/trial linkage, comparator discipline, planned study-family independence and structured confounding assessment. | Final health-policy or regulatory recommendations. |
| **Scientific readiness** | Whether the current architecture is an appropriate foundation for independently reviewed synthesis. | Treating record counts as evidence strength or health effects. |

## 2. Core epistemological position: zero as success

Reviewers may observe headline synthesis metrics reported as `0` or as **Pending review stage** / **Not yet available**.

- **Collection is not synthesis.** Automated discovery and ingestion do not equal evidence review.
- **A verified zero is meaningful.** The publication layer reports `0` only where the approved payload explicitly contains zero.
- **Unknown is not zero.** Uncalculated, absent or unreviewed states are rendered as an explicit pending/unavailable state rather than silently coerced to zero.
- **Review firewall.** The pipeline must not convert candidate records into conclusion-sensitive outputs until the required source-grounded extraction and human review exist.
- **Counts describe the evidence system, not health effects.** Candidate-record volume is not interpreted as benefit, harm, certainty or causal weight.

## 3. Governing automation rule

> **No automated transformation may increase the evidential status of a record without a documented rule, provenance and, where conclusion-sensitive, human verification.**

AI or other automated tooling may assist bounded extraction or classification where the source and transformation are traceable. It must not invent outcomes, effect estimates, risk-of-bias judgements, pooled estimates, causal conclusions, safety judgements, diagnoses, illegality or criminality.

## 4. Release identity

The Observatory deliberately separates the scientific-engine release from the public-presentation release.

- **Research release:** Research run `33306721309`, Research code revision `5b5500778bf83637e6ec3e8388046cb73789d58d`.
- **Public build:** identified by the full public commit SHA embedded in deployed HTML as the `vaping26-build` fingerprint and displayed in shortened form on the homepage.
- **Publication validation:** GitHub Actions validates the build, reviewer-facing static hardening, public JSON/PDF presence and post-deployment live parity.

This distinction prevents a Research-engine provenance identifier from being mistaken for the public-site commit.

## 5. Local build and verification

### Prerequisites

- Python 3.12 recommended (the public CI uses Python 3.12)
- Git
- A SHA-256 utility such as `sha256sum` or `shasum -a 256`
- `curl` for raw-HTML inspection

### Reproduce the exact public build

First obtain the full public commit SHA from the deployed `vaping26-build` fingerprint or the successful GitHub Actions run being assessed, then:

```bash
git clone https://github.com/homegundredaroad/Vaping26.git
cd Vaping26
git checkout <PUBLIC_COMMIT_SHA>
python -m pip install reportlab==4.4.3
python scripts/validate_public.py
python -m unittest discover -s tests -v
python scripts/build_site.py
GITHUB_SHA=<PUBLIC_COMMIT_SHA> GITHUB_RUN_NUMBER=<PUBLIC_RUN_NUMBER> python scripts/harden_public_build.py
```

The CI environment supplies `GITHUB_SHA` and `GITHUB_RUN_NUMBER`. A purely local run without those variables will display local-build placeholders for public-build identity; scientific/public data values are still derived from the checked-out approved JSON.

### Inspect publication integrity

The publication manifest is stored at:

```text
provenance/publication_manifest.json
```

Do not assume a root-level `release_manifest.json`; that is not the current repository contract.

Reviewers can inspect the manifest and independently hash listed public files, for example:

```bash
python scripts/validate_public.py
sha256sum data/public/research_status.json
sha256sum evidence/evidence_cards.json
sha256sum evidence/health_evidence_summary.json
sha256sum evidence/synthesis_register.json
sha256sum provenance/source_register.json
```

The repository validation script is the normative manifest/disclosure-boundary check because the manifest is structured JSON rather than a POSIX `sha256sum -c` checksum file.

## 6. No-JavaScript inspection

The reviewer-facing build pre-renders headline values so raw HTML remains interpretable without client-side execution.

```bash
curl -s https://homegundredaroad.github.io/Vaping26/index.html | grep "External review release"
curl -s https://homegundredaroad.github.io/Vaping26/index.html | grep "Research code revision"
curl -s https://homegundredaroad.github.io/Vaping26/index.html | grep "Public build revision"
curl -s https://homegundredaroad.github.io/Vaping26/index.html | grep 'id="metric-sources"'
curl -s https://homegundredaroad.github.io/Vaping26/index.html | grep 'id="metric-literature"'
curl -s https://homegundredaroad.github.io/Vaping26/index.html | grep 'id="design-table"'
```

Primary reviewer surfaces include:

- `index.html`
- `results.html`
- `methodology.html`
- `sources.html`
- `ai-governance.html`
- `limitations.html`
- `evidence.html`

The deployment workflow itself performs HTTP 200 and semantic-content checks against key live HTML, JSON and PDF endpoints after GitHub Pages deployment.

## 7. Priority methodological findings already acknowledged

Two scientific risks are intentionally treated as highest priority because either could materially change future synthesis even if all software controls function perfectly.

### C1 — Study-family independence

Vaping26 must distinguish bibliographic records from underlying studies and research families so protocols, registrations, primary reports, follow-up publications and secondary analyses do not create false independence or duplicate participant weighting.

Tracked publicly in GitHub issue **#7**.

### C4 — Structured confounding assessment

Observational evidence requires structured capture of smoking history, prior combustible exposure, dual use, exposure intensity/duration, baseline health, age, socioeconomic context, cessation intent, adjustment models/covariates, temporality and residual-confounding concerns.

Tracked publicly in GitHub issue **#8**.

## 8. Questions reviewers are explicitly invited to challenge

1. Is the separation of discovery → classification → appraisal → synthesis → conclusion scientifically appropriate?
2. Are the registered sources and search strategies sufficiently comprehensive and reproducible for their stated purposes?
3. Are automated study-design classification and abstention rules defensible, and what independent benchmark should be required?
4. Are protocols, registrations, primary publications, secondary analyses and post-publication notices represented correctly?
5. Are population, exposure/intervention, comparator, outcome and time definitions precise enough for future synthesis?
6. Is the proposed study-family model sufficient to prevent duplicate participant or duplicate study weighting?
7. Is the planned confounding framework adequate for major vaping-health observational designs?
8. What design-specific risk-of-bias tools or mappings should be adopted?
9. What body-of-evidence certainty framework should govern conclusion strength?
10. Are the provenance, release and methodological-change controls sufficient for an independent group to reproduce and critique the process?

## 9. Current scientific boundary

The appropriate current description is:

> **A functioning, auditable UK vaping and nicotine evidence observatory undergoing independent scientific and methodological validation.**

The appropriate readiness verdict is:

> **Vaping26 is ready for independent scientific and methodological review, but is not yet ready to issue unrestricted authoritative causal health conclusions.**

Critical feedback, missing sources, classification errors, comparator problems, study-family linkage errors, confounding concerns, risk-of-bias objections, automation-governance problems and reproducibility failures are explicitly requested. A substantive reviewer criticism should become a documented methodological finding, decision, corrective change and regression test where applicable.
