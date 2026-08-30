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


def normalise_navigation_and_fingerprint() -> None:
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
    document = set_text(document, "source-count", f"{int(register.get('source_count') or 0):,}")
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
    for filename in ("index.html", "results.html", "sources.html", "methodology.html"):
        text = (TARGET / filename).read_text(encoding="utf-8")
        if "Loading latest approved synthesis register" in text:
            failures.append(f"{filename}: legacy synthesis loading placeholder remains")
        if "<td colspan=\"6\">Loading…</td>" in text:
            failures.append(f"{filename}: legacy source loading placeholder remains")
    sources = (TARGET / "sources.html").read_text(encoding="utf-8")
    if re.search(r'id=["\']source-count["\'][^>]*>\s*[—-]\s*</', sources):
        failures.append("sources.html: source count was not pre-rendered")
    if failures:
        raise RuntimeError("Reviewer-facing public build hardening failed:\n - " + "\n - ".join(failures))


def main() -> None:
    if not TARGET.is_dir():
        raise SystemExit("build/site does not exist; run scripts/build_site.py first")
    normalise_navigation_and_fingerprint()
    prerender_sources()
    assert_reviewer_surface()
    print("REVIEWER-FACING PUBLIC BUILD HARDENING PASS")


if __name__ == "__main__":
    main()
