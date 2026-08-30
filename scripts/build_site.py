#!/usr/bin/env python3
"""Build the validated Vaping26 static publication bundle."""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from build_results_pdf import build_results_pdf
from validate_public import ROOT, validate_repository

PUBLIC_DATA_ROOTS = (
    Path("data/public"), Path("evidence"), Path("environment"), Path("regulation"), Path("provenance"),
)
REQUIRED_PUBLIC_JSON = (
    Path("data/public/research_status.json"), Path("evidence/evidence_cards.json"), Path("evidence/health_evidence_summary.json"),
    Path("evidence/ons_prevalence.json"), Path("evidence/synthesis_register.json"), Path("evidence/youth_prevalence.json"),
    Path("evidence/trial_publication_links.json"),
    Path("provenance/source_register.json"), Path("provenance/source_coverage.json"), Path("provenance/publication_manifest.json"),
    Path("provenance/release_evidence.json"),
)

def _read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict): raise RuntimeError(f"Expected JSON object in {path}")
    return payload

def _human(value: object) -> str:
    text = str(value or "unknown").replace("_", " ")
    return " ".join(word.capitalize() for word in text.split())

def _num(value: object) -> str:
    try: return f"{int(value):,}"
    except (TypeError, ValueError): return "Data unavailable"

def _replace_id_text(document: str, element_id: str, value: object) -> str:
    escaped = html.escape(str(value), quote=False)
    pattern = re.compile(rf'(<(?P<tag>[a-zA-Z0-9]+)\b[^>]*\bid=["\']{re.escape(element_id)}["\'][^>]*>)(.*?)(</(?P=tag)>)', re.S)
    rendered, count = pattern.subn(lambda m: m.group(1) + escaped + m.group(4), document, count=1)
    if count != 1: raise RuntimeError(f"Could not render build-time result for #{element_id}")
    return rendered

def _daily_ons_estimate(prevalence: dict) -> dict:
    latest = prevalence.get("latest_year")
    rows = prevalence.get("estimates") or prevalence.get("latest_year_estimates") or []
    for row in rows:
        if not isinstance(row, dict) or str(row.get("year")) != str(latest): continue
        if str(row.get("group") or "").strip() != "All persons aged 16 and over": continue
        if "daily e-cigarette users" not in str(row.get("statistic") or ""): continue
        return row
    return {}

def _result_reference_stats(links: dict) -> dict[str, int]:
    referenced: set[str] = set()
    matched: set[str] = set()
    for trial in links.get("records", []) if isinstance(links.get("records"), list) else []:
        if not isinstance(trial, dict): continue
        for ref in trial.get("publication_references", []) or []:
            if not isinstance(ref, dict) or str(ref.get("reference_type") or "").upper() != "RESULT": continue
            pmid = str(ref.get("pmid") or "").strip()
            if not pmid: continue
            referenced.add(pmid)
            if ref.get("matched_to_evidence_card") is True: matched.add(pmid)
    return {"referenced": len(referenced), "matched": len(matched), "unmatched": len(referenced - matched)}

def _question_rows(questions: list[dict]) -> str:
    if not questions: return '<tr><td colspan="4">No approved synthesis register is available for this release.</td></tr>'
    rows=[]
    for question in questions:
        title=html.escape(str(question.get("title") or question.get("id") or "Untitled question"))
        rows.append(f"<tr><td>{title}</td><td>{_num(question.get('candidate_cards'))}</td><td>{_num(question.get('effect_estimate_ready_cards'))}</td><td>{html.escape(_human(question.get('synthesis_status') or question.get('protocol_status')))}</td></tr>")
    return "".join(rows)

def _dataset_jsonld(status: dict) -> str:
    payload={"@context":"https://schema.org","@type":"Dataset","name":"Vaping26 current evidence results","description":"Vaping26 approved public evidence release containing quality-gated vaping literature coverage, clinical-trial linkage, synthesis-readiness metadata and official UK prevalence extracts.","url":"https://homegundredaroad.github.io/Vaping26/results.html","isAccessibleForFree":True,"dateModified":status.get("generated_at"),"creator":{"@type":"Organization","name":"Vaping26"},"license":"https://github.com/homegundredaroad/Vaping26","measurementTechnique":"Registered-source harvesting, deterministic validation, deduplication, relevance gating and governed publication","distribution":[{"@type":"DataDownload","encodingFormat":"application/pdf","contentUrl":"https://homegundredaroad.github.io/Vaping26/downloads/vaping26-current-results.pdf"},{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":"https://homegundredaroad.github.io/Vaping26/evidence/health_evidence_summary.json"}]}
    return '<script type="application/ld+json">'+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"</script>"

def render_overview_page(target: Path) -> None:
    page=target/"index.html"; document=page.read_text(encoding="utf-8")
    status=_read_json(target/"data/public/research_status.json")
    evidence=_read_json(target/"evidence/health_evidence_summary.json")
    cards=_read_json(target/"evidence/evidence_cards.json")
    release=_read_json(target/"provenance/release_evidence.json")
    coverage=status.get("source_coverage") if isinstance(status.get("source_coverage"),dict) else {}
    readiness=evidence.get("review_readiness") if isinstance(evidence.get("review_readiness"),dict) else {}
    generated=status.get("generated_at")
    state="OPERATIONAL"
    age_text="Release freshness unavailable."
    if generated:
        try:
            stamp=datetime.fromisoformat(str(generated).replace("Z","+00:00"))
            age=max(0.0,(datetime.now(timezone.utc)-stamp.astimezone(timezone.utc)).total_seconds()/86400)
            age_text=f"Latest approved export is {'less than one day' if age < 1 else str(int(age))+' day'+('' if int(age)==1 else 's')} old."
            if age>10: state="STALE"
        except ValueError: pass
    attempted=int(coverage.get("attempted_sources") or 0); successful=int(coverage.get("successful_sources") or 0); failed=int(coverage.get("failed_attempts") or 0)
    if state!="STALE" and (failed>0 or (attempted>0 and successful<attempted)): state="DEGRADED"
    values={
        "last-refresh":generated or "Release timestamp unavailable",
        "publication-level":_human(status.get("publication_level")),
        "maturity-captured":_num(cards.get("card_count")),
        "maturity-reviewed":_num(readiness.get("reviewed_record_count")),
        "maturity-ready":_num(readiness.get("conclusion_sensitive_ready_record_count")),
        "pipeline-state":state,
        "pipeline-age":age_text,
        "pipeline-attempted":_num(attempted),
        "pipeline-successful":_num(successful),
        "pipeline-failed":_num(failed),
        "pipeline-integrity":"PASS" if coverage.get("no_silent_disappearance") is True else "CHECK REQUIRED",
        "release-run":release.get("run_id") or "Unavailable",
        "release-code":str(release.get("code_revision") or "Unavailable")[:12],
        "release-validation":"PASS",
    }
    for element_id,value in values.items(): document=_replace_id_text(document,element_id,value)
    page.write_text(document,encoding="utf-8")

def render_results_page(target: Path) -> None:
    page=target/"results.html"; document=page.read_text(encoding="utf-8")
    status=_read_json(target/"data/public/research_status.json"); evidence=_read_json(target/"evidence/health_evidence_summary.json"); synthesis=_read_json(target/"evidence/synthesis_register.json"); prevalence=_read_json(target/"evidence/ons_prevalence.json"); links=_read_json(target/"evidence/trial_publication_links.json")
    literature=evidence.get("literature") if isinstance(evidence.get("literature"),dict) else {}; cards=evidence.get("evidence_cards") if isinstance(evidence.get("evidence_cards"),dict) else {}; trials=evidence.get("clinical_trials") if isinstance(evidence.get("clinical_trials"),dict) else {}; readiness=evidence.get("review_readiness") if isinstance(evidence.get("review_readiness"),dict) else {}
    result_refs=_result_reference_stats(links)
    values={"r-literature":_num(literature.get("canonical_records")),"r-cards":_num(cards.get("card_count")),"r-trials":_num(trials.get("record_count")),"r-trial-results":_num(trials.get("trials_with_results")),"r-linked":_num(trials.get("trials_with_matched_evidence_cards")),"r-unmatched":_num(result_refs.get("unmatched")),"r-reviewed":_num(readiness.get("reviewed_record_count")),"r-ready":_num(readiness.get("conclusion_sensitive_ready_record_count")),"r-unknown-design":f"{_num((readiness.get('unknown_study_design') or {}).get('count'))} ({float((readiness.get('unknown_study_design') or {}).get('percent') or 0):.1f}%)","r-integrity":f"{_num((readiness.get('unknown_integrity_status') or {}).get('count'))} ({float((readiness.get('unknown_integrity_status') or {}).get('percent') or 0):.1f}%)","r-prev-year":_num(prevalence.get("latest_year")),"r-release":str(status.get("generated_at") or "Release timestamp unavailable")}
    daily=_daily_ons_estimate(prevalence)
    if daily:
        values["r-prev"]=f"{float(daily.get('estimate_percent')):.1f}%"; lo=daily.get("lower_95_percent",daily.get("lower_ci")); hi=daily.get("upper_95_percent",daily.get("upper_ci"))
        if lo is not None and hi is not None: values["r-prev-detail"]=f"England, age 16+, {prevalence.get('latest_year')}; 95% CI {float(lo):.1f}-{float(hi):.1f}%."
    else: values["r-prev"]="Data unavailable"; values["r-prev-detail"]="No matching approved ONS daily-use estimate is present in this release."
    for element_id,value in values.items(): document=_replace_id_text(document,element_id,value)
    questions=synthesis.get("questions") if isinstance(synthesis.get("questions"),list) else []
    document,count=re.subn(r'(<tbody\b[^>]*\bid=["\']question-rows["\'][^>]*>)(.*?)(</tbody>)',lambda m:m.group(1)+_question_rows([q for q in questions if isinstance(q,dict)])+m.group(3),document,count=1,flags=re.S)
    if count!=1: raise RuntimeError("Could not render build-time synthesis question rows")
    # Do not let the legacy all-reference summary overwrite the correct RESULT-only build-time value.
    document=document.replace("t('r-unmatched',n(tr.unmatched_referenced_pmids));", "")
    document=document.replace("Trial-referenced PMIDs still unmatched", "Registry RESULT PMIDs still unmatched")
    document=document.replace(
        "trial records linked to candidate evidence, and referenced PMIDs still unresolved",
        "trial records linked to candidate evidence, and RESULT-reference PMIDs still unresolved",
    )
    document=document.replace(
        "Unmatched does not mean unpublished or invalid; it means the current governed linkage process has not reconciled that identifier to a public candidate record.",
        "This headline gap counts only ClinicalTrials.gov RESULT references. BACKGROUND bibliography and DERIVED references remain auditable but are not presented as missing trial-result publications. Unmatched does not mean unpublished or invalid; it means the current governed linkage process has not reconciled that RESULT identifier to a public candidate record.",
    )
    document=document.replace("</head>",_dataset_jsonld(status)+"</head>",1); page.write_text(document,encoding="utf-8")

def validate_built_bundle(target: Path) -> None:
    errors=[]
    if not (target/"index.html").is_file(): errors.append("missing index.html")
    if not (target/"assets/site.js").is_file(): errors.append("missing assets/site.js")
    if not (target/"assets/youth.js").is_file(): errors.append("missing assets/youth.js")
    for rel in REQUIRED_PUBLIC_JSON:
        path=target/rel
        if not path.is_file(): errors.append(f"missing public JSON: {rel.as_posix()}"); continue
        if path.stat().st_size==0: errors.append(f"empty public JSON: {rel.as_posix()}"); continue
        try: payload=json.loads(path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError) as exc: errors.append(f"invalid public JSON {rel.as_posix()}: {exc}"); continue
        if not isinstance(payload,dict): errors.append(f"public JSON must contain an object: {rel.as_posix()}")
    results=target/"results.html"
    if not results.is_file(): errors.append("missing results.html")
    else:
        text=results.read_text(encoding="utf-8")
        if 'type="application/ld+json"' not in text or '"@type":"Dataset"' not in text: errors.append("results.html missing Dataset structured data")
        if "Loading latest approved synthesis register" in text: errors.append("results.html still contains unresolved synthesis loading placeholder")
        if "Trial-referenced PMIDs still unmatched" in text: errors.append("results.html still labels all registry references as missing trial publications")
        for element_id in ("r-literature","r-cards","r-trials","r-prev-year","r-unmatched"):
            match=re.search(rf'id=["\']{element_id}["\'][^>]*>(.*?)</',text,re.S)
            if not match or match.group(1).strip() in {"","—","Data unavailable"}: errors.append(f"results.html has unresolved required result: {element_id}")
    overview=(target/"index.html").read_text(encoding="utf-8")
    for element_id in ("maturity-captured","maturity-reviewed","maturity-ready","pipeline-state","release-run","release-code"):
        match=re.search(rf'id=["\']{element_id}["\'][^>]*>(.*?)</',overview,re.S)
        if not match or match.group(1).strip() in {"","—","STATUS UNAVAILABLE"}: errors.append(f"index.html has unresolved release state: {element_id}")
    cards=_read_json(target/"evidence/evidence_cards.json")
    evidence_html=(target/"evidence.html").read_text(encoding="utf-8")
    if int(cards.get("card_count") or 0)>0 and "will populate after the first approved publication" in evidence_html.lower(): errors.append("evidence.html claims records are awaiting first publication despite published cards")
    for rel in ("ai-governance.html","citation.html"):
        if not (target/rel).is_file(): errors.append(f"missing governance page: {rel}")
    pdf=target/"downloads/vaping26-current-results.pdf"
    if not pdf.is_file() or pdf.stat().st_size < 2000: errors.append("missing or implausibly small results PDF")
    if errors: raise RuntimeError("Built public bundle contract failed:\n - "+"\n - ".join(errors))

def build_site() -> Path:
    errors=validate_repository()
    if errors: raise RuntimeError("Public repository validation failed:\n - "+"\n - ".join(errors))
    target=ROOT/"build"/"site"
    if target.exists(): shutil.rmtree(target)
    shutil.copytree(ROOT/"site",target)
    for rel in PUBLIC_DATA_ROOTS:
        source=ROOT/rel
        if source.exists():
            destination=target/rel; destination.parent.mkdir(parents=True,exist_ok=True); shutil.copytree(source,destination,dirs_exist_ok=True)
    render_overview_page(target)
    render_results_page(target)
    build_results_pdf(target,target/"downloads/vaping26-current-results.pdf")
    (target/".nojekyll").write_text("",encoding="utf-8")
    validate_built_bundle(target)
    return target

if __name__=="__main__":
    destination=build_site(); print(f"Built validated site at {destination}")
