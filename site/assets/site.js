const V26 = (() => {
  const fmt = new Intl.NumberFormat("en-GB");
  const q = (id) => document.getElementById(id);
  const safe = (value, fallback = "—") => (value === null || value === undefined || value === "" ? fallback : value);
  const number = (value) => Number.isFinite(Number(value)) ? fmt.format(Number(value)) : "—";
  const pct = (value) => Number.isFinite(Number(value)) ? `${Number(value).toFixed(1)}%` : "—";
  const human = (value) => String(value || "unknown").replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
  const date = (value) => {
    if (!value) return "Awaiting research publication";
    const d = new Date(value);
    return Number.isNaN(d.valueOf()) ? String(value) : d.toLocaleString("en-GB", {dateStyle:"medium", timeStyle:"short", timeZone:"Europe/London"});
  };

  async function getJSON(path) {
    const response = await fetch(path, {cache:"no-store"});
    if (!response.ok) throw new Error(`${response.status} ${path}`);
    return response.json();
  }
  async function optionalJSON(path) {
    try { return await getJSON(path); } catch (_) { return {}; }
  }
  function setText(id, value) { const el = q(id); if (el) el.textContent = value; }
  function ciText(row) {
    if (!row) return "95% CI unavailable";
    const lo = row.lower_95_percent ?? row.lower_ci, hi = row.upper_95_percent ?? row.upper_ci;
    return Number.isFinite(Number(lo)) && Number.isFinite(Number(hi)) ? `95% CI ${Number(lo).toFixed(1)}–${Number(hi).toFixed(1)}%` : "95% CI unavailable";
  }
  function exactEstimate(data, year, group, statistic) {
    return (data?.estimates || []).find(x => Number(x.year) === Number(year) && String(x.group || "").trim() === group && String(x.statistic || "").trim() === statistic);
  }
  function collector(status, id) {
    return (status?.collectors || []).find(x => x.collector === id) || {};
  }
  function question(register, id) {
    return (register?.questions || []).find(x => x.id === id) || {};
  }
  function cardLink(card) {
    if (card.pmid) return `https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(card.pmid)}/`;
    if (card.doi) return `https://doi.org/${encodeURIComponent(card.doi)}`;
    return null;
  }
  function renderQuestion(container, item) {
    if (!container || !item?.id) return;
    const article = document.createElement("article"); article.className = "question-card";
    const h = document.createElement("h3"); h.textContent = item.title || item.id; article.appendChild(h);
    const status = document.createElement("p"); status.className = "question-status"; status.textContent = human(item.synthesis_status || item.protocol_status); article.appendChild(status);
    const meta = document.createElement("p"); meta.textContent = `${number(item.candidate_cards)} candidate cards · ${number(item.effect_estimate_ready_cards)} effect-ready`; article.appendChild(meta);
    if (Array.isArray(item.comparators) && item.comparators.length) {
      const p = document.createElement("p"); p.className = "muted"; p.textContent = `Comparators: ${item.comparators.join("; ")}`; article.appendChild(p);
    }
    container.appendChild(article);
  }
  function renderEvidenceCard(container, card) {
    const article = document.createElement("article"); article.className = "evidence-card";
    const top = document.createElement("div"); top.className = "evidence-meta";
    [safe(card.year), human(card.study_design), human(card.integrity_status)].forEach(text => { const span = document.createElement("span"); span.textContent = text; top.appendChild(span); });
    article.appendChild(top);
    const h = document.createElement("h3"); h.textContent = card.title || "Untitled record"; article.appendChild(h);
    const journal = document.createElement("p"); journal.className = "muted"; journal.textContent = safe(card.journal, "Journal not supplied"); article.appendChild(journal);
    if (Array.isArray(card.topic_tags) && card.topic_tags.length) {
      const tags = document.createElement("div"); tags.className = "tag-row";
      card.topic_tags.forEach(t => { const span=document.createElement("span"); span.className="tag"; span.textContent=human(t); tags.appendChild(span); });
      article.appendChild(tags);
    }
    const href = cardLink(card);
    if (href) { const a=document.createElement("a"); a.href=href; a.target="_blank"; a.rel="noopener noreferrer"; a.textContent="Source record ↗"; article.appendChild(a); }
    container.appendChild(article);
  }

  async function dashboard() {
    const [status,evidence,register,coverage,prevalence,cards,synthesis] = await Promise.all([
      optionalJSON("data/public/research_status.json"), optionalJSON("evidence/health_evidence_summary.json"),
      optionalJSON("provenance/source_register.json"), optionalJSON("provenance/source_coverage.json"),
      optionalJSON("evidence/ons_prevalence.json"), optionalJSON("evidence/evidence_cards.json"),
      optionalJSON("evidence/synthesis_register.json")
    ]);
    setText("metric-sources", number(register.source_count));
    setText("metric-literature", number(evidence?.literature?.canonical_records));
    setText("metric-cards", number(cards.card_count ?? evidence?.evidence_cards?.card_count));
    setText("metric-trials", number(evidence?.clinical_trials?.record_count));
    setText("metric-questions", number(synthesis.question_count ?? evidence?.synthesis?.question_count));
    const latest = prevalence.latest_year;
    const daily = exactEstimate(prevalence, latest, "All persons aged 16 and over", "Proportion of population who are daily e-cigarette users");
    setText("metric-ons-daily", pct(daily?.estimate_percent));
    if (daily) setText("metric-ons-daily-detail", `${latest} England estimate, age 16+; ${ciText(daily)}.`);
    setText("last-refresh", date(status.generated_at || register.generated_at));
    setText("publication-level", safe(status.publication_level, "Publication-safe aggregate metadata"));
    if (register.source_count !== undefined) setText("source-summary", `${number(register.source_count)} registered sources are currently catalogued across scientific, official-statistical, regulatory and discovery roles.`);
  }

  async function evidencePage() {
    const [evidence,cards,synthesis] = await Promise.all([
      optionalJSON("evidence/health_evidence_summary.json"), optionalJSON("evidence/evidence_cards.json"), optionalJSON("evidence/synthesis_register.json")
    ]);
    setText("e-lit", number(evidence?.literature?.canonical_records));
    setText("e-input", number(evidence?.literature?.input_records));
    setText("e-dupes", number(evidence?.literature?.duplicates_collapsed));
    setText("e-quarantined", number(evidence?.literature?.quarantined_records));
    setText("e-cards", number(cards.card_count ?? evidence?.evidence_cards?.card_count));
    setText("e-trials", number(evidence?.clinical_trials?.record_count));
    setText("e-results", number(evidence?.clinical_trials?.trials_with_results));
    setText("e-questions", number(synthesis.question_count ?? evidence?.synthesis?.question_count));

    const topics = q("e-topic-counts");
    if (topics) {
      topics.innerHTML = "";
      const rows = Object.entries(evidence?.literature?.topic_counts || {}).sort((a,b)=>b[1]-a[1]);
      if (!rows.length) { const li=document.createElement("li"); li.textContent="No topic-tag summary is available in this publication."; topics.appendChild(li); }
      rows.forEach(([key,count]) => { const li=document.createElement("li"); li.textContent=`${human(key)}: ${number(count)}`; topics.appendChild(li); });
    }
    const limits = q("evidence-limitations");
    if (limits) {
      limits.innerHTML="";
      const items = Array.isArray(evidence.limitations) ? evidence.limitations : ["No generated limitations summary is available yet."];
      items.forEach(item=>{const li=document.createElement("li"); li.textContent=item; limits.appendChild(li);});
    }

    const all = Array.isArray(cards.records) ? cards.records : [];
    const container=q("evidence-cards"), count=q("ev-count");
    if (!container || !all.length) {
      if (count) count.textContent="Evidence-card publication will populate after the first v3 Research run.";
      return;
    }
    const topic=q("ev-topic"), design=q("ev-design"), integrity=q("ev-integrity"), year=q("ev-year"), search=q("ev-search");
    const values = (key, multi=false) => [...new Set(all.flatMap(c => multi ? (c[key]||[]) : [c[key]]).filter(Boolean))].sort((a,b)=>String(a).localeCompare(String(b)));
    values("topic_tags",true).forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=human(v);topic.appendChild(o);});
    values("study_design").forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=human(v);design.appendChild(o);});
    values("integrity_status").forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=human(v);integrity.appendChild(o);});
    values("year").sort((a,b)=>Number(b)-Number(a)).forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;year.appendChild(o);});
    const apply=()=>{
      const term=String(search.value||"").trim().toLowerCase();
      const filtered=all.filter(c => (!term || `${c.title||""} ${c.journal||""}`.toLowerCase().includes(term)) && (!topic.value || (c.topic_tags||[]).includes(topic.value)) && (!design.value || c.study_design===design.value) && (!integrity.value || c.integrity_status===integrity.value) && (!year.value || String(c.year)===year.value));
      container.innerHTML=""; filtered.slice(0,200).forEach(c=>renderEvidenceCard(container,c));
      count.textContent=`${number(filtered.length)} matching evidence card${filtered.length===1?"":"s"}${filtered.length>200?"; first 200 shown":""}.`;
    };
    [topic,design,integrity,year,search].forEach(el=>el.addEventListener(el.tagName==="INPUT"?"input":"change",apply)); apply();
  }

  async function healthPage() {
    const [synthesis,cards] = await Promise.all([optionalJSON("evidence/synthesis_register.json"), optionalJSON("evidence/evidence_cards.json")]);
    const r=question(synthesis,"respiratory_health"), c=question(synthesis,"cardiovascular_health");
    setText("h-respiratory",number(r.candidate_cards)); setText("h-cardiovascular",number(c.candidate_cards));
    const integrity = cards.integrity_status_counts || {};
    setText("h-integrity", number((integrity.retracted||0)+(integrity.expression_of_concern||0)));
    setText("h-ready",number((r.effect_estimate_ready_cards||0)+(c.effect_estimate_ready_cards||0)));
    const container=q("health-questions"); if (container) { container.innerHTML=""; [r,c].forEach(x=>renderQuestion(container,x)); if(!r.id&&!c.id) container.textContent="The health synthesis register will appear after the first v3 publication."; }
  }

  async function cessationPage() {
    const [synthesis,evidence,cards] = await Promise.all([optionalJSON("evidence/synthesis_register.json"), optionalJSON("evidence/health_evidence_summary.json"), optionalJSON("evidence/evidence_cards.json")]);
    const item=question(synthesis,"cessation_nicotine_ecig_vs_nrt");
    setText("c-candidates",number(item.candidate_cards)); setText("c-ready",number(item.effect_estimate_ready_cards));
    setText("c-trials",number(evidence?.clinical_trials?.record_count)); setText("c-results",number(evidence?.clinical_trials?.trials_with_results));
    setText("c-population",safe(item.population)); setText("c-comparators",Array.isArray(item.comparators)?item.comparators.join("; "):"—"); setText("c-outcomes",Array.isArray(item.primary_outcomes)?item.primary_outcomes.join("; "):"—"); setText("c-status",human(item.synthesis_status));
    const container=q("cessation-cards"); if(container){container.innerHTML=""; const rows=(cards.records||[]).filter(c=>(c.topic_tags||[]).includes("cessation")); rows.slice(0,60).forEach(c=>renderEvidenceCard(container,c)); if(!rows.length) container.textContent="Candidate evidence cards will appear after the first v3 publication.";}
  }

  async function youngPeoplePage() {
    const [youth,synthesis] = await Promise.all([optionalJSON("evidence/youth_prevalence.json"), optionalJSON("evidence/synthesis_register.json")]);
    const rows=Array.isArray(youth.records)?youth.records:[]; const indicators=Array.isArray(youth.indicators)?youth.indicators:[];
    setText("y-rows",number(youth.record_count)); setText("y-indicators",number(indicators.length)); setText("y-candidates",number(question(synthesis,"youth_use").candidate_cards)); setText("y-areas",number(new Set(rows.map(r=>r.area_code||r.area_name).filter(Boolean)).size));
    const tbody=q("youth-rows"); if(!tbody || !rows.length) return;
    const indicatorSel=q("y-filter-indicator"), timeSel=q("y-filter-time"), areaInput=q("y-filter-area"), count=q("youth-filter-count");
    indicators.forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;indicatorSel.appendChild(o);});
    [...new Set(rows.map(r=>r.time_period).filter(Boolean))].sort().reverse().forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;timeSel.appendChild(o);});
    const apply=()=>{
      const area=String(areaInput.value||"").trim().toLowerCase(); const filtered=rows.filter(r=>(!indicatorSel.value||r.indicator===indicatorSel.value)&&(!timeSel.value||String(r.time_period)===timeSel.value)&&(!area||String(r.area_name||"").toLowerCase().includes(area)));
      tbody.innerHTML=""; filtered.slice(0,250).forEach(r=>{const tr=document.createElement("tr"); const val=Number.isFinite(Number(r.value))?String(r.value):"—"; const group=[r.sex,r.category_type,r.category].filter(Boolean).join(" · ")||"—"; [r.indicator||"—",r.time_period||"—",r.area_name||r.area_code||"—",r.age||"—",group,val,ciText(r)].forEach(v=>{const td=document.createElement("td");td.textContent=v;tr.appendChild(td)}); tbody.appendChild(tr);});
      count.textContent=`${number(filtered.length)} matching row${filtered.length===1?"":"s"}${filtered.length>250?"; first 250 shown":""}.`;
    }; [indicatorSel,timeSel].forEach(el=>el.addEventListener("change",apply)); areaInput.addEventListener("input",apply); apply();
  }

  async function prevalencePage() {
    const data = await optionalJSON("evidence/ons_prevalence.json"); const body=q("prevalence-age-rows");
    if (!data.latest_year) { if(body) body.innerHTML='<tr><td colspan="5">No validated ONS prevalence extract has been published yet.</td></tr>'; return; }
    const year=data.latest_year; setText("p-year",number(year)); setText("p-count",number(data.estimate_count));
    const group="All persons aged 16 and over", dailyStat="Proportion of population who are daily e-cigarette users", occasionalStat="Proportion of population who are occasional e-cigarette user";
    const daily=exactEstimate(data,year,group,dailyStat), occasional=exactEstimate(data,year,group,occasionalStat);
    setText("p-daily",pct(daily?.estimate_percent)); setText("p-daily-ci",`All persons aged 16+; ${ciText(daily)}.`); setText("p-occasional",pct(occasional?.estimate_percent)); setText("p-occasional-ci",`All persons aged 16+; ${ciText(occasional)}.`); setText("prevalence-status",data.interpretation||"Official survey estimates");
    if(body){body.innerHTML=""; ["16-24","25-34","35-49","50-59","60 and over","16 and over"].forEach(age=>{const g=`All persons aged ${age}`,d=exactEstimate(data,year,g,dailyStat),o=exactEstimate(data,year,g,occasionalStat); if(!d&&!o)return; const tr=document.createElement("tr");[g.replace("All persons aged ",""),pct(d?.estimate_percent),ciText(d),pct(o?.estimate_percent),ciText(o)].forEach(v=>{const td=document.createElement("td");td.textContent=v;tr.appendChild(td)});body.appendChild(tr);});}
    const changes=q("prevalence-changes"); if(changes){changes.innerHTML="";(data.important_data_changes||[]).slice(0,8).forEach(v=>{const li=document.createElement("li");li.textContent=v;changes.appendChild(li)});}
  }

  async function exposurePage() {
    const [synthesis,evidence] = await Promise.all([optionalJSON("evidence/synthesis_register.json"),optionalJSON("evidence/health_evidence_summary.json")]);
    const second=question(synthesis,"secondhand_exposure"), third=question(synthesis,"thirdhand_residue");
    setText("x-secondhand",number(second.candidate_cards)); setText("x-thirdhand",number(third.candidate_cards)); setText("x-particles",number(evidence?.literature?.topic_counts?.ultrafine_particles)); setText("x-biomarkers",number(evidence?.literature?.topic_counts?.exposure_biomarkers));
    const container=q("exposure-questions"); if(container){container.innerHTML="";[second,third].forEach(x=>renderQuestion(container,x));if(!second.id&&!third.id)container.textContent="Exposure synthesis questions will appear after the first v3 publication.";}
  }

  async function productsPage() {
    const [status,register] = await Promise.all([optionalJSON("data/public/research_status.json"),optionalJSON("provenance/source_register.json")]);
    const mhra=collector(status,"mhra_ecig"); const source=(register.sources||[]).find(s=>String(s.id||"").includes("mhra"))||{};
    setText("prod-status",human(mhra.status||source.status)); setText("prod-records",number(mhra.records)); setText("prod-authority",safe(source.authority||source.name,"MHRA"));
  }

  async function retailPage() {
    const [status,register] = await Promise.all([optionalJSON("data/public/research_status.json"),optionalJSON("provenance/source_register.json")]);
    setText("ret-company",number(collector(status,"companies_house").records)); setText("ret-news",number(collector(status,"newsapi_leads").records));
    const count=(register.sources||[]).filter(s=>String(s.family||"").toLowerCase().includes("enforcement")||String(s.evidence_role||"").toLowerCase().includes("enforcement")).length; setText("ret-enforcement-sources",number(count));
  }

  async function environmentPage() {
    const data=await optionalJSON("environment/source_registry.json"); const body=q("environment-rows"); setText("env-count",number(data.source_count));setText("env-production",number(data.production_candidates));setText("env-reviewed",safe(data.reviewed_at)); const s4=(data.sources||[]).find(x=>x.id==="sentinel4_uvn");setText("env-s4",safe(s4?.status)); if(!body)return; body.innerHTML=""; if(!(data.sources||[]).length){body.innerHTML='<tr><td colspan="6">The optional environmental capability registry is not available.</td></tr>';return;} (data.sources||[]).forEach(source=>{const tr=document.createElement("tr");[source.name||source.id,source.role||"—",source.status||"—",source.spatial_scale||"—",(source.parameters||[]).join(", "),source.implementation_phase??"—"].forEach(v=>{const td=document.createElement("td");td.textContent=v;tr.appendChild(td)});body.appendChild(tr)});
  }

  async function regulationPage() {
    const data=await optionalJSON("regulation/timeline.json"); const container=q("regulation-timeline"); setText("r-count",number(data.milestone_count));setText("r-reviewed",safe(data.reviewed_at)); const today=new Date(),future=(data.milestones||[]).filter(x=>new Date(`${x.date}T00:00:00Z`)>=today).sort((a,b)=>String(a.date).localeCompare(String(b.date))),next=future[0];setText("r-next-date",safe(next?.date));setText("r-next-title",safe(next?.title)); if(!container)return; container.innerHTML=""; if(!(data.milestones||[]).length){container.textContent="The verified regulatory timeline has not yet been published.";return;} (data.milestones||[]).forEach(item=>{const article=document.createElement("article");article.className="timeline-item";const db=document.createElement("div");db.className="timeline-date";db.textContent=item.date||"—";const body=document.createElement("div"),h=document.createElement("h3");h.textContent=item.title||item.id;body.appendChild(h);const meta=document.createElement("p");meta.textContent=`${item.status||"—"} · ${item.authority||"—"}`;body.appendChild(meta);const desc=document.createElement("p");desc.textContent=item.summary||"";body.appendChild(desc);if(item.source_url){const a=document.createElement("a");a.href=item.source_url;a.target="_blank";a.rel="noopener noreferrer";a.textContent="Official source ↗";body.appendChild(a)}article.appendChild(db);article.appendChild(body);container.appendChild(article)});
  }

  async function downloadsPage() {
    const container = q("optional-downloads");
    if (!container) return;
    const candidates = [
      ["evidence/ons_prevalence.json", "ONS adult prevalence", "Validated adult estimates with 95% confidence limits and comparability notes."],
      ["evidence/youth_prevalence.json", "Youth prevalence", "Official OHID vaping indicators with geography, age/category and confidence limits."],
      ["evidence/evidence_cards.json", "Evidence cards", "Publication-safe bibliographic and classification metadata for synthesis candidates."],
      ["evidence/synthesis_register.json", "Synthesis register", "Pre-specified research questions and current extraction/synthesis readiness."],
      ["evidence/trial_publication_links.json", "Trial-publication links", "Identifier-based ClinicalTrials.gov to publication evidence-card links."],
      ["provenance/release_evidence.json", "Release evidence", "Compact Research run, code revision and source-snapshot provenance."],
    ];
    const checks = await Promise.all(candidates.map(async item => {
      try { const response = await fetch(item[0], {cache:"no-store"}); return response.ok ? item : null; } catch (_) { return null; }
    }));
    container.innerHTML = "";
    const available = checks.filter(Boolean);
    if (!available.length) { container.textContent = "No optional files are present in this release."; return; }
    available.forEach(([path,title,description]) => {
      const row=document.createElement("div"); row.className="download";
      const body=document.createElement("div"), strong=document.createElement("strong"), p=document.createElement("p");
      strong.textContent=title; p.textContent=description; body.appendChild(strong); body.appendChild(p);
      const a=document.createElement("a"); a.className="mono"; a.href=path; a.textContent=path.split("/").pop();
      row.appendChild(body); row.appendChild(a); container.appendChild(row);
    });
  }

  async function sourcesPage() {
    const body=q("source-rows"); if(!body)return; const [register,coverage]=await Promise.all([optionalJSON("provenance/source_register.json"),optionalJSON("provenance/source_coverage.json")]); const runMap=new Map((coverage.sources||[]).map(x=>[x.source_id,x])); body.innerHTML=""; if(!(register.sources||[]).length){body.innerHTML='<tr><td colspan="6">The public source register has not yet been generated.</td></tr>';return;} (register.sources||[]).forEach(source=>{const run=runMap.get(source.id)||{},tr=document.createElement("tr");[source.name||source.id,source.family||"—",source.evidence_role||"—",source.authority||"—",source.status||"—",run.run_status||"not attempted in published run"].forEach(v=>{const td=document.createElement("td");td.textContent=v;tr.appendChild(td)});body.appendChild(tr)});setText("source-count",number(register.source_count));setText("source-generated",date(register.generated_at));
  }

  function initMobileNav() {
    const nav = document.querySelector(".site-header .nav");
    const links = nav?.querySelector(".nav-links");
    if (!nav || !links || nav.querySelector(".nav-toggle")) return;

    links.id = links.id || "primary-navigation";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "nav-toggle";
    button.setAttribute("aria-controls", links.id);
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-label", "Open navigation menu");
    button.innerHTML = '<span class="nav-toggle-lines" aria-hidden="true"><span></span><span></span><span></span></span><span class="nav-toggle-text">Menu</span>';
    nav.insertBefore(button, links);

    const style = document.createElement("style");
    style.textContent = `
      .nav-toggle{display:none}
      @media(max-width:900px){
        .site-header{position:sticky;top:0}
        .site-header .nav{min-height:64px;padding:.55rem 0;display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:.75rem}
        .site-header .brand{min-width:0}
        .nav-toggle{display:inline-flex;align-items:center;gap:.55rem;justify-self:end;border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.07);color:#fff;border-radius:.6rem;padding:.55rem .7rem;font:inherit;font-size:.86rem;font-weight:750;cursor:pointer}
        .nav-toggle:hover,.nav-toggle:focus-visible{background:rgba(255,255,255,.14);outline:2px solid transparent}
        .nav-toggle-lines{width:1.15rem;display:grid;gap:3px}
        .nav-toggle-lines span{display:block;height:2px;background:currentColor;border-radius:99px;transition:transform .18s ease,opacity .18s ease}
        .nav-toggle[aria-expanded="true"] .nav-toggle-lines span:nth-child(1){transform:translateY(5px) rotate(45deg)}
        .nav-toggle[aria-expanded="true"] .nav-toggle-lines span:nth-child(2){opacity:0}
        .nav-toggle[aria-expanded="true"] .nav-toggle-lines span:nth-child(3){transform:translateY(-5px) rotate(-45deg)}
        .site-header .nav-links{display:none;grid-column:1/-1;width:100%;padding:.45rem 0 .65rem;gap:.15rem;border-top:1px solid rgba(255,255,255,.1)}
        .site-header .nav-links.is-open{display:grid}
        .site-header .nav-links a{display:block;padding:.62rem .7rem;font-size:.92rem;border-radius:.45rem}
        .site-header .nav-links a[aria-current="page"]{background:rgba(255,255,255,.12)}
      }
      @media(max-width:420px){.nav-toggle-text{position:absolute;inline-size:1px;block-size:1px;overflow:hidden;clip-path:inset(50%)}.nav-toggle{padding:.6rem}.site-header .brand{font-size:1.18rem}}
    `;
    document.head.appendChild(style);

    const close = (restoreFocus = false) => {
      links.classList.remove("is-open");
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-label", "Open navigation menu");
      if (restoreFocus) button.focus();
    };
    const open = () => {
      links.classList.add("is-open");
      button.setAttribute("aria-expanded", "true");
      button.setAttribute("aria-label", "Close navigation menu");
    };

    button.addEventListener("click", () => button.getAttribute("aria-expanded") === "true" ? close() : open());
    links.addEventListener("click", event => { if (event.target.closest("a")) close(); });
    document.addEventListener("keydown", event => { if (event.key === "Escape" && button.getAttribute("aria-expanded") === "true") close(true); });
    document.addEventListener("click", event => { if (button.getAttribute("aria-expanded") === "true" && !nav.contains(event.target)) close(); });
    window.addEventListener("resize", () => { if (window.innerWidth > 900) close(); }, {passive:true});
  }

  initMobileNav();
  return {dashboard,evidencePage,healthPage,cessationPage,youngPeoplePage,prevalencePage,exposurePage,productsPage,retailPage,environmentPage,regulationPage,downloadsPage,sourcesPage};
})();
