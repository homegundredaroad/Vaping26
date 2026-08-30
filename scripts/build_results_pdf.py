#!/usr/bin/env python3
"""Generate a compact, source-grounded PDF summary from the approved public release."""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def read_json(root: Path, rel: str) -> dict:
    payload = json.loads((root / rel).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {rel}")
    return payload


def number(value: object) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "Data unavailable"


def daily_ons(prevalence: dict) -> dict:
    latest = prevalence.get("latest_year")
    for row in prevalence.get("estimates") or prevalence.get("latest_year_estimates") or []:
        if not isinstance(row, dict) or str(row.get("year")) != str(latest):
            continue
        if str(row.get("group") or "").strip() != "All persons aged 16 and over":
            continue
        if "daily e-cigarette users" in str(row.get("statistic") or ""):
            return row
    return {}


def result_reference_stats(links: dict) -> dict[str, int]:
    referenced: set[str] = set()
    matched: set[str] = set()
    for trial in links.get("records", []) if isinstance(links.get("records"), list) else []:
        if not isinstance(trial, dict):
            continue
        for ref in trial.get("publication_references", []) or []:
            if not isinstance(ref, dict) or str(ref.get("reference_type") or "").upper() != "RESULT":
                continue
            pmid = str(ref.get("pmid") or "").strip()
            if not pmid:
                continue
            referenced.add(pmid)
            if ref.get("matched_to_evidence_card") is True:
                matched.add(pmid)
    return {"referenced": len(referenced), "matched": len(matched), "unmatched": len(referenced - matched)}


def build_results_pdf(site_root: Path, output: Path) -> Path:
    status = read_json(site_root, "data/public/research_status.json")
    evidence = read_json(site_root, "evidence/health_evidence_summary.json")
    synthesis = read_json(site_root, "evidence/synthesis_register.json")
    prevalence = read_json(site_root, "evidence/ons_prevalence.json")
    coverage = read_json(site_root, "provenance/source_coverage.json")
    links = read_json(site_root, "evidence/trial_publication_links.json")

    literature = evidence.get("literature") or {}
    cards = evidence.get("evidence_cards") or {}
    trials = evidence.get("clinical_trials") or {}
    readiness = evidence.get("review_readiness") or {}
    daily = daily_ons(prevalence)
    result_refs = result_reference_stats(links)

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=15*mm,
                            title="Vaping26 - Current Results", author="Vaping26")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="V26Title", parent=styles["Title"], fontSize=22, leading=25, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle(name="V26Sub", parent=styles["Normal"], fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#444444"), spaceAfter=12))
    styles.add(ParagraphStyle(name="V26H2", parent=styles["Heading2"], fontSize=13, leading=16, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="V26Body", parent=styles["BodyText"], fontSize=9.2, leading=13))
    styles.add(ParagraphStyle(name="V26Small", parent=styles["BodyText"], fontSize=7.8, leading=10, textColor=colors.HexColor("#555555")))

    story = [
        Paragraph("Vaping26 - Current Results", styles["V26Title"]),
        Paragraph("UK Vaping &amp; Nicotine Observatory | Approved public release: " + str(status.get("generated_at") or "timestamp unavailable"), styles["V26Sub"]),
        Paragraph("What this report is", styles["V26H2"]),
        Paragraph("A run-specific summary generated automatically from the same approved public JSON release used by the Vaping26 website. Counts describe evidence coverage, source status, trial linkage, prevalence and review maturity. They are not a single verdict on vaping safety or harm.", styles["V26Body"]),
    ]

    metrics = [
        ["Validated literature", number(literature.get("canonical_records")), "Evidence cards", number(cards.get("card_count"))],
        ["Clinical trials", number(trials.get("record_count")), "Trials with results", number(trials.get("trials_with_results"))],
        ["Trials linked to cards", number(trials.get("trials_with_matched_evidence_cards")), "Unmatched RESULT PMIDs", number(result_refs.get("unmatched"))],
        ["Human-reviewed records", number(readiness.get("reviewed_record_count")), "Conclusion-ready records", number(readiness.get("conclusion_sensitive_ready_record_count"))],
    ]
    table = Table(metrics, colWidths=[47*mm, 24*mm, 47*mm, 24*mm])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#BBBBBB")),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F1F3F5")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#F1F3F5")),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME", (1,0), (1,-1), "Helvetica-Bold"),
        ("FONTNAME", (3,0), (3,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.2),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [
        Paragraph("Evidence coverage", styles["V26H2"]),
        table,
        Paragraph(
            f"ClinicalTrials.gov RESULT references are reported separately: {number(result_refs.get('referenced'))} unique RESULT PMIDs, "
            f"{number(result_refs.get('matched'))} matched to candidate evidence records and {number(result_refs.get('unmatched'))} currently unmatched. "
            "BACKGROUND bibliography and DERIVED references remain auditable but are not counted as missing trial-result publications.",
            styles["V26Small"],
        ),
    ]

    unknown_design = readiness.get("unknown_study_design") or {}
    unknown_integrity = readiness.get("unknown_integrity_status") or {}
    story += [
        Paragraph("Review maturity", styles["V26H2"]),
        Paragraph(f"Unknown study design: <b>{number(unknown_design.get('count'))}</b> ({float(unknown_design.get('percent') or 0):.1f}%). Integrity unresolved: <b>{number(unknown_integrity.get('count'))}</b> ({float(unknown_integrity.get('percent') or 0):.1f}%). These are maturity indicators, not evidence-certainty scores.", styles["V26Body"]),
    ]

    if daily:
        lo = daily.get("lower_95_percent", daily.get("lower_ci")); hi = daily.get("upper_95_percent", daily.get("upper_ci"))
        ci = f"; 95% CI {float(lo):.1f}-{float(hi):.1f}%" if lo is not None and hi is not None else ""
        prev_text = f"ONS {prevalence.get('latest_year')}: daily e-cigarette use among all persons aged 16+ in England: <b>{float(daily.get('estimate_percent')):.1f}%</b>{ci}."
    else:
        prev_text = "No matching approved ONS daily-use estimate is present in this release."
    story += [Paragraph("Latest official prevalence", styles["V26H2"]), Paragraph(prev_text, styles["V26Body"])]

    questions = [q for q in synthesis.get("questions", []) if isinstance(q, dict)]
    qdata = [["Synthesis question", "Candidates", "Effect-ready", "Status"]]
    for q in questions:
        qdata.append([Paragraph(str(q.get("title") or q.get("id") or "Untitled"), styles["V26Small"]), number(q.get("candidate_cards")), number(q.get("effect_estimate_ready_cards")), str(q.get("synthesis_status") or q.get("protocol_status") or "unknown").replace("_", " ")])
    qtable = Table(qdata, colWidths=[82*mm, 23*mm, 23*mm, 42*mm], repeatRows=1)
    qtable.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E9ECEF")), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#C5C5C5")), ("FONTSIZE", (0,0), (-1,-1), 7.5),
        ("VALIGN", (0,0), (-1,-1), "TOP"), ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story += [Paragraph("Synthesis register", styles["V26H2"]), qtable]

    attempted = coverage.get("attempted_sources", coverage.get("attempted")); successful = coverage.get("successful_sources", coverage.get("successful")); failed = coverage.get("failed_sources", coverage.get("failed_attempts"))
    story += [
        Paragraph("Publication and provenance", styles["V26H2"]),
        Paragraph(f"Source coverage: attempted <b>{number(attempted)}</b>; successful <b>{number(successful)}</b>; failed <b>{number(failed)}</b>. The public release is governed by the publication firewall and SHA-256 manifest. Raw records, credentials and unresolved investigative material are not included in this PDF.", styles["V26Body"]),
        Spacer(1, 5*mm),
        Paragraph("Interpretation: candidate counts show mapped evidence, not direction or magnitude of effect. Comparator-specific pooled effects, causal conclusions and risk-of-bias judgements remain gated until source-grounded extraction and human review are complete.", styles["V26Small"]),
        Paragraph("Live observatory: https://homegundredaroad.github.io/Vaping26/results.html", styles["V26Small"]),
    ]
    doc.build(story)
    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("site_root", nargs="?", default="build/site")
    parser.add_argument("output", nargs="?", default="build/site/downloads/vaping26-current-results.pdf")
    args = parser.parse_args()
    print(build_results_pdf(Path(args.site_root), Path(args.output)))
