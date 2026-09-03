#!/usr/bin/env python3
"""Harden the built Vaping26 publication for reviewer-facing, no-JS inspection."""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "build" / "site"
PENDING = "Pending review stage"
BASE_URL = "https://homegundredaroad.github.io/Vaping26/"

NAV_ITEMS = [
    ("index.html", "Overview"),
    ("results.html", "Results"),
    ("health.html", "Health"),
    ("cessation.html", "Cessation"),
    ("young-people.html", "Young people"),
    ("prevalence.html", "Prevalence"),
    ("exposure.html", "Exposure"),
    ("products.html", "Products"),
    ("retail-enforcement.html", "Retail & enforcement"),
    ("regulation.html", "Regulation"),
    ("evidence.html", "Evidence explorer"),
]


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def display_number(value: object, pending: str = PENDING) -> str:
    """Render zero only when the approved payload explicitly contains zero."""
    if value is None or value == "":
        return pending
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return pending


def set_text(document: str, element_id: str, value: object) -> str:
    escaped = html.escape(str(value), quote=False)
    pattern = re.compile(
        rf'(<(?P<tag>[a-zA-Z0-9]+)\b[^>]*\bid=["\']{re.escape(element_id)}["\'][^>]*>)(.*?)(</(?P=tag)>)',
        re.S,
    )
    rendered, count = pattern.subn(lambda m: m.group(1) + escaped + m.group(4), document, count=1)
    if count != 1:
        raise RuntimeError(f"Could not pre-render #{element_id}")
    return rendered


def canonical_nav(filename: str) -> str:
    links = []
    for href, label in NAV_ITEMS:
        current = ' aria-current="page"' if filename == href else ""
        links.append(f'<a{current} href="{href}">{html.escape(label)}</a>')
    return '<nav class="nav-links" aria-label="Primary">' + "".join(links) + "</nav>"


def canonical_url(filename: str) -> str:
    return BASE_URL if filename == "index.html" else BASE_URL + filename


def _meta_content(document: str, name: str) -> str:
    match = re.search(
        rf'<meta\b[^>]*\bname=["\']{re.escape(name)}["\'][^>]*\bcontent=["\']([^"\']*)["\'][^>]*>',
        document,
        re.I,
    )
    return html.unescape(match.group(1)).strip() if match else ""


def _title_text(document: str) -> str:
    match = re.search(r"<title>(.*?)</title>", document, re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", match.group(1))).strip() if match else "Vaping26"


def ensure_global_head_metadata(document: str, filename: str) -> str:
    """Give every public HTML page a consistent browser/search/social identity."""
    additions = []
    canonical = canonical_url(filename)

    if 'name="theme-color"' not in document:
        additions.append('<meta name="theme-color" content="#06111d">')
    if 'rel="icon" href="favicon.svg"' not in document:
        additions.append('<link rel="icon" href="favicon.svg" type="image/svg+xml">')
    if 'rel="icon" href="favicon.ico"' not in document:
        additions.append('<link rel="icon" href="favicon.ico" sizes="any">')
    if 'rel="apple-touch-icon"' not in document:
        additions.append('<link rel="apple-touch-icon" href="apple-touch-icon.png">')
    if 'rel="manifest"' not in document:
        additions.append('<link rel="manifest" href="site.webmanifest">')
    if 'rel="canonical"' not in document:
        additions.append(f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">')

    title = _title_text(document)
    description = _meta_content(document, "description")
    if 'property="og:title"' not in document:
        additions.append(f'<meta property="og:title" content="{html.escape(title, quote=True)}">')
    if description and 'property="og:description"' not in document:
        additions.append(f'<meta property="og:description" content="{html.escape(description, quote=True)}">')
    if 'property="og:type"' not in document:
        additions.append('<meta property="og:type" content="website">')
    if 'property="og:url"' not in document:
        additions.append(f'<meta property="og:url" content="{html.escape(canonical, quote=True)}">')
    if 'name="twitter:card"' not in document:
        additions.append('<meta name="twitter:card" content="summary">')

    if additions:
        if "</head>" not in document:
            raise RuntimeError(f"Missing </head> in {filename}")
        document = document.replace("</head>", "".join(additions) + "</head>", 1)
    return document


def normalise_result_linkage_wording(document: str) -> str:
    """Keep the headline trial-publication metric strictly RESULT-reference based."""
    document = document.replace("t('r-unmatched',n(tr.unmatched_referenced_pmids));", "")
    document = document.replace(
        "Trial-referenced PMIDs still unmatched",
        "Registry RESULT PMIDs still unmatched",
    )
    document = document.replace(
        "trial records linked to candidate evidence, and referenced PMIDs still unresolved",
        "trial records linked to candidate evidence, and RESULT-reference PMIDs still unresolved",
    )
    document = document.replace(
        "Unmatched does not mean unpublished or invalid; it means the current governed linkage process has not reconciled that identifier to a public candidate record.",
        "This headline gap counts only ClinicalTrials.gov RESULT references. BACKGROUND bibliography and DERIVED references remain auditable but are not presented as missing trial-result publications. Unmatched does not mean unpublished or invalid; it means the current governed linkage process has not reconciled that RESULT identifier to a public candidate record.",
    )
    return document


def normalise_navigation_fingerprint_and_metadata() -> None:
    sha = os.environ.get("GITHUB_SHA", "local-build")
    for page in sorted(TARGET.glob("*.html")):
        document = page.read_text(encoding="utf-8")
        document, count = re.subn(
            r'<nav\s+class=["\']nav-links["\']\s+aria-label=["\']Primary["\']>.*?</nav>',
            canonical_nav(page.name),
            document,
            count=1,
            flags=re.S,
        )
        if count != 1:
            raise RuntimeError(f"Missing primary navigation in {page.name}")
        marker = f'<meta name="vaping26-build" content="{html.escape(sha, quote=True)}">'
        if 'name="vaping26-build"' not in document:
            document = document.replace("</head>", marker + "</head>", 1)
        document = ensure_global_head_metadata(document, page.name)
        if page.name == "results.html":
            document = normalise_result_linkage_wording(document)
        page.write_text(document, encoding="utf-8")


def exact_ons_daily(prevalence: dict) -> dict:
    latest = prevalence.get("latest_year")
    for row in prevalence.get("estimates", []) if isinstance(prevalence.get("estimates"), list) else []:
        if not isinstance(row, dict):
            continue
        if str(row.get("year")) != str(latest):
            continue
        if str(row.get("group") or "").strip() != "All persons aged 16 and over":
            continue
        if str(row.get("statistic") or "").strip() != "Proportion of population who are daily e-cigarette users":
            continue
        return row
    return {}


def prerender_overview() -> None:
    page = TARGET / "index.html"
    document = page.read_text(encoding="utf-8")
    evidence = read_json(TARGET / "evidence" / "health_evidence_summary.json")
    cards = read_json(TARGET / "evidence" / "evidence_cards.json")
    synthesis = read_json(TARGET / "evidence" / "synthesis_register.json")
    prevalence = read_json(TARGET / "evidence" / "ons_prevalence.json")
    register = read_json(TARGET / "provenance" / "source_register.json")
    release = read_json(TARGET / "provenance" / "release_evidence.json")

    values = {
        "metric-sources": display_number(register.get("source_count"), "Not yet available"),
        "metric-literature": display_number((evidence.get("literature") or {}).get("canonical_records")),
        "metric-cards": display_number(cards.get("card_count")),
        "metric-trials": display_number((evidence.get("clinical_trials") or {}).get("record_count")),
        "metric-questions": display_number(synthesis.get("question_count")),
        "visual-total": display_number(cards.get("card_count")),
    }
    daily = exact_ons_daily(prevalence)
    estimate = daily.get("estimate_percent") if daily else None
    values["metric-ons-daily"] = f"{float(estimate):.1f}%" if estimate is not None else "Not yet available"
    if daily:
        lo = daily.get("lower_95_percent", daily.get("lower_ci"))
        hi = daily.get("upper_95_percent", daily.get("upper_ci"))
        detail = f"{prevalence.get('latest_year')} England estimate, age 16+"
        if lo is not None and hi is not None:
            detail += f"; 95% CI {float(lo):.1f}–{float(hi):.1f}%."
        else:
            detail += "."
        values["metric-ons-daily-detail"] = detail

    for element_id, value in values.items():
        document = set_text(document, element_id, value)

    design_counts = cards.get("study_design_counts") if isinstance(cards.get("study_design_counts"), dict) else {}
    total = int(cards.get("card_count") or 0)
    design_rows = []
    for key, count in sorted(design_counts.items(), key=lambda item: int(item[1] or 0), reverse=True)[:6]:
        n = int(count or 0)
        share = (100.0 * n / total) if total else 0.0
        label = " ".join(word.capitalize() for word in str(key).replace("_", " ").split())
        design_rows.append(
            f"<tr><td>{html.escape(label)}</td><td>{n:,}</td><td>{share:.1f}%</td></tr>"
        )
    if not design_rows:
        design_rows = ['<tr><td colspan="3">Not yet available</td></tr>']
    document, count = re.subn(
        r'(<tbody\b[^>]*\bid=["\']design-table["\'][^>]*>)(.*?)(</tbody>)',
        lambda m: m.group(1) + "".join(design_rows) + m.group(3),
        document,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Could not pre-render study-design table")

    document = document.replace(
        '<span class="label">Research run</span>',
        '<span class="label">Research release run</span>',
        1,
    )
    document = document.replace(
        '<span class="label">Code revision</span>',
        '<span class="label">Research code revision</span>',
        1,
    )
    public_sha = os.environ.get("GITHUB_SHA", "local-build")
    public_run = os.environ.get("GITHUB_RUN_NUMBER", "local")
    release_grid_pattern = re.compile(
        r'(<section class="section" aria-labelledby="release-title">.*?<div class="metric-grid">)(.*?)(</div><p class="muted">)',
        re.S,
    )
    extra = (
        '<article class="metric"><span class="label">Public build revision</span>'
        f'<span class="value" id="public-build-code">{html.escape(public_sha[:12])}</span></article>'
        '<article class="metric"><span class="label">Public validation run</span>'
        f'<span class="value" id="public-build-run">#{html.escape(str(public_run))}</span></article>'
    )
    document, count = release_grid_pattern.subn(
        lambda m: m.group(1) + m.group(2) + extra + m.group(3), document, count=1
    )
    if count != 1:
        raise RuntimeError("Could not extend release identity panel")

    banner = (
        '<section class="section" id="external-review-status"><div class="notice">'
        '<strong>External review release</strong>'
        "Vaping26 is undergoing independent methodological and scientific review. "
        "Automated discovery does not constitute scientific synthesis; conclusion-sensitive outputs remain review-gated."
        "</div></section>"
    )
    if 'id="external-review-status"' not in document:
        document = document.replace('<main id="main" class="wrap">', '<main id="main" class="wrap">' + banner, 1)

    if release.get("run_id") is not None:
        document = set_text(document, "release-run", release.get("run_id"))
    if release.get("code_revision"):
        document = set_text(document, "release-code", str(release.get("code_revision"))[:12])

    page.write_text(document, encoding="utf-8")


def prerender_sources() -> None:
    page = TARGET / "sources.html"
    document = page.read_text(encoding="utf-8")
    register = read_json(TARGET / "provenance" / "source_register.json")
    coverage = read_json(TARGET / "provenance" / "source_coverage.json")
    run_map = {
        str(item.get("source_id")): item
        for item in coverage.get("sources", [])
        if isinstance(item, dict) and item.get("source_id")
    }
    document = set_text(document, "source-count", display_number(register.get("source_count"), "Not yet available"))
    document = set_text(document, "source-generated", register.get("generated_at") or "Timestamp unavailable")

    rows = []
    for source in register.get("sources", []):
        if not isinstance(source, dict):
            continue
        run = run_map.get(str(source.get("id")), {})
        values = [
            source.get("name") or source.get("id") or "Unnamed source",
            source.get("family") or "Not stated",
            source.get("evidence_role") or "Not stated",
            source.get("authority") or "Not stated",
            source.get("status") or "Not stated",
            run.get("run_status") or "Not attempted in published run",
        ]
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in values) + "</tr>")
    if not rows:
        rows = ['<tr><td colspan="6">No approved source-register rows are present in this release.</td></tr>']
    document, count = re.subn(
        r'(<tbody\b[^>]*\bid=["\']source-rows["\'][^>]*>)(.*?)(</tbody>)',
        lambda m: m.group(1) + "".join(rows) + m.group(3),
        document,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Could not pre-render source table")
    page.write_text(document, encoding="utf-8")


def assert_reviewer_surface() -> None:
    failures = []
    required_results_link = 'href="results.html">Results</a>'
    for page in sorted(TARGET.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        if required_results_link not in text:
            failures.append(f"{page.name}: Results missing from primary navigation")
        if 'name="vaping26-build"' not in text:
            failures.append(f"{page.name}: build fingerprint missing")
        for needle, label in (
            ('name="theme-color"', "theme colour"),
            ('rel="icon" href="favicon.svg"', "SVG favicon"),
            ('rel="icon" href="favicon.ico"', "ICO favicon"),
            ('rel="apple-touch-icon"', "Apple touch icon"),
            ('rel="manifest"', "web manifest"),
            ('rel="canonical"', "canonical URL"),
            ('property="og:title"', "Open Graph title"),
            ('property="og:url"', "Open Graph URL"),
            ('name="twitter:card"', "Twitter card"),
        ):
            if needle not in text:
                failures.append(f"{page.name}: {label} missing")

    for filename in ("index.html", "results.html", "sources.html", "methodology.html"):
        text = (TARGET / filename).read_text(encoding="utf-8")
        if "Loading latest approved synthesis register" in text:
            failures.append(f"{filename}: legacy synthesis loading placeholder remains")
        if '<td colspan="6">Loading…</td>' in text:
            failures.append(f"{filename}: legacy source loading placeholder remains")

    results = (TARGET / "results.html").read_text(encoding="utf-8")
    if "Trial-referenced PMIDs still unmatched" in results:
        failures.append("results.html: legacy all-reference PMID label remains")
    if "t('r-unmatched',n(tr.unmatched_referenced_pmids));" in results:
        failures.append("results.html: legacy all-reference client-side overwrite remains")
    if "Registry RESULT PMIDs still unmatched" not in results:
        failures.append("results.html: RESULT-only PMID label missing")

    sources = (TARGET / "sources.html").read_text(encoding="utf-8")
    if re.search(r'id=["\']source-count["\'][^>]*>\s*[—-]\s*</', sources):
        failures.append("sources.html: source count was not pre-rendered")

    overview = (TARGET / "index.html").read_text(encoding="utf-8")
    for element_id in (
        "metric-sources", "metric-literature", "metric-cards", "metric-trials", "metric-questions",
        "visual-total", "maturity-captured", "maturity-reviewed", "maturity-ready",
        "release-run", "release-code", "public-build-code", "public-build-run",
    ):
        match = re.search(rf'id=["\']{re.escape(element_id)}["\'][^>]*>(.*?)</', overview, re.S)
        if not match or match.group(1).strip() in {"", "—", "STATUS UNAVAILABLE"}:
            failures.append(f"index.html: unresolved reviewer-facing value #{element_id}")
    if 'id="external-review-status"' not in overview:
        failures.append("index.html: external-review banner missing")
    design = re.search(r'id=["\']design-table["\'][^>]*>(.*?)</tbody>', overview, re.S)
    if not design or not design.group(1).strip():
        failures.append("index.html: study-design table was not pre-rendered")

    if failures:
        raise RuntimeError("Reviewer-facing public build hardening failed:\n - " + "\n - ".join(failures))


def main() -> None:
    if not TARGET.is_dir():
        raise SystemExit("build/site does not exist; run scripts/build_site.py first")
    normalise_navigation_fingerprint_and_metadata()
    prerender_overview()
    prerender_sources()
    assert_reviewer_surface()
    print("REVIEWER-FACING PUBLIC BUILD HARDENING PASS")


if __name__ == "__main__":
    main()
