from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "site" / "results.html"


def test_results_explains_non_additive_record_accounting():
    text = RESULTS.read_text(encoding="utf-8")
    assert "two deliberately overlapping acquisition routes" in text
    assert "Ordinary literature input records" in text
    assert "Exact trial-PMID records recovered" in text
    assert "quarantine reasons are non-mutually-exclusive" in text
    assert "must not be summed to infer a unique-record total" in text
    assert "Ordinary inputs + recovered trial references ≠ a unique-record denominator" in text


def test_results_uses_result_only_trial_publication_gap():
    text = RESULTS.read_text(encoding="utf-8")
    assert "tr.unmatched_result_pmids" in text
    assert "Registry RESULT PMIDs still unmatched" in text
    assert "BACKGROUND bibliography and DERIVED references" in text
    assert "tr.unmatched_referenced_pmids" not in text


def test_results_exposes_quarantine_breakdown_from_approved_release():
    text = RESULTS.read_text(encoding="utf-8")
    assert "lit.quarantine_reason_counts" in text
    assert 'id="quarantine-reasons"' in text
    assert 'id="r-quarantined"' in text
    assert 'id="r-before-gate"' in text
    assert "t('r-literature-flow',n(lit.canonical_records))" in text
