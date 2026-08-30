# Vaping26 — Reviewer Transmission Checklist

Use this checklist immediately before sending a reviewer-facing release.

- [ ] Public validation/deployment workflow is green for the commit being circulated.
- [ ] Post-deployment live parity check passed for `index.html`, `methodology.html`, `sources.html`, `results.html`, required public JSON and current-results PDF.
- [ ] Raw `index.html` contains the external-review banner, Research release identity, Public build identity and pre-rendered headline metrics.
- [ ] Raw `index.html` contains a non-empty pre-rendered study-design table or an explicit not-yet-available state.
- [ ] No uncomputed metric is silently represented as `0`; zero is reserved for an explicitly present numeric zero in the approved release payload.
- [ ] `provenance/publication_manifest.json` passes `python scripts/validate_public.py` and no unmanifested generated public data is present.
- [ ] Repository regression tests pass from a clean GitHub Actions checkout.
- [ ] `ai-governance.html` and `methodology.html` preserve the boundary that AI/automation must not autonomously create conclusion-sensitive scientific judgements.
- [ ] Health, cessation and young-people copy contains no unreviewed causal/safety conclusion.
- [ ] Known high-priority scientific limitations are public and traceable: C1 study-family independence and C4 structured confounding.
- [ ] Reviewer guide accurately states that the project is undergoing independent scientific and methodological validation and is not yet an authoritative causal evidence synthesis.

The transmission boundary is:

> **Vaping26 is ready for independent scientific and methodological review, but is not yet ready to issue unrestricted authoritative causal health conclusions.**
