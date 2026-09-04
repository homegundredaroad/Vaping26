from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def test_citation_metadata_is_machine_readable_and_project_specific():
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert "cff-version: 1.2.0" in text
    assert 'title: "Vaping26: UK Vaping & Nicotine Evidence Observatory"' in text
    assert 'name: "SCC Nexus"' in text
    assert 'repository-code: "https://github.com/homegundredaroad/Vaping26"' in text
    assert 'url: "https://homegundredaroad.github.io/Vaping26/"' in text
    assert "license: MIT" in text


def test_public_citation_page_separates_ownership_contribution_and_review():
    text = (SITE / "citation.html").read_text(encoding="utf-8")
    assert "CITATION.cff" in text
    assert "project owner and publisher" in text
    assert "scientific contribution" in text
    assert "does not imply sponsorship or endorsement" in text


def test_methodology_exposes_conservative_review_controls():
    text = (SITE / "methodology.html").read_text(encoding="utf-8")
    assert "Unknown is a valid state" in text
    assert "machine suggestion cannot mark a record reviewed or synthesis-ready" in text
    assert "first governed review tranche" in text
    assert "second check before public effect estimates" in text
    assert "references explicitly marked as RESULT" in text
