const V26 = (() => {
  const fmt = new Intl.NumberFormat("en-GB");
  const q = (id) => document.getElementById(id);
  const safe = (value, fallback = "—") => (value === null || value === undefined || value === "" ? fallback : value);
  const number = (value) => Number.isFinite(Number(value)) ? fmt.format(Number(value)) : "—";
  const pct = (value) => Number.isFinite(Number(value)) ? `${Number(value).toFixed(1)}%` : "—";
  const date = (value) => {
    if (!value) return "Awaiting first research publication";
    const d = new Date(value);
    return Number.isNaN(d.valueOf()) ? String(value) : d.toLocaleString("en-GB", {dateStyle:"medium", timeStyle:"short", timeZone:"Europe/London"});
  };
  async function getJSON(path) {
    const response = await fetch(path, {cache:"no-store"});
    if (!response.ok) throw new Error(`${response.status} ${path}`);
    return response.json();
  }
  function setText(id, value) { const el = q(id); if (el) el.textContent = value; }
  function ciText(row) {
    if (!row) return "95% CI unavailable";
    const lo = row.lower_95_percent, hi = row.upper_95_percent;
    return Number.isFinite(Number(lo)) && Number.isFinite(Number(hi)) ? `95% CI ${Number(lo).toFixed(1)}–${Number(hi).toFixed(1)}%` : "95% CI unavailable";
  }
  function exactEstimate(data, year, group, statistic) {
    return (data?.estimates || []).find(x => Number(x.year) === Number(year) && String(x.group || "").trim() === group && String(x.statistic || "").trim() === statistic);
  }

  async function dashboard() {
    const results = await Promise.allSettled([
      getJSON("data/public/research_status.json"),
      getJSON("evidence/health_evidence_summary.json"),
      getJSON("provenance/source_register.json"),
      getJSON("provenance/source_coverage.json"),
      getJSON("environment/source_registry.json"),
      getJSON("evidence/ons_prevalence.json")
    ]);
    const status = results[0].status === "fulfilled" ? results[0].value : {};
    const evidence = results[1].status === "fulfilled" ? results[1].value : {};
    const register = results[2].status === "fulfilled" ? results[2].value : {};
    const coverage = results[3].status === "fulfilled" ? results[3].value : {};
    const environment = results[4].status === "fulfilled" ? results[4].value : {};
    const prevalence = results[5].status === "fulfilled" ? results[5].value : {};
    setText("metric-sources", number(register.source_count));
    setText("metric-literature", number(evidence?.literature?.canonical_records));
    setText("metric-trials", number(evidence?.clinical_trials?.record_count));
    setText("metric-successful", number(coverage?.summary?.evidence_successful_sources));
    setText("metric-environment", number(environment.source_count));
    const latest = prevalence.latest_year;
    const daily = exactEstimate(prevalence, latest, "All persons aged 16 and over", "Proportion of population who are daily e-cigarette users");
    setText("metric-ons-daily", pct(daily?.estimate_percent));
    if (daily) setText("metric-ons-daily-detail", `${latest} England estimate, age 16+; ${ciText(daily)}.`);
    setText("last-refresh", date(status.generated_at || register.generated_at));
    setText("publication-level", safe(status.publication_level, "Bootstrap publication boundary"));
    if (register.source_count !== undefined) setText("source-summary", `${number(register.source_count)} registered public source entries are currently catalogued.`);
  }

  async function evidencePage() {
    try {
      const evidence = await getJSON("evidence/health_evidence_summary.json");
      setText("e-lit", number(evidence?.literature?.canonical_records));
      setText("e-input", number(evidence?.literature?.input_records));
      setText("e-dupes", number(evidence?.literature?.duplicates_collapsed));
      setText("e-quarantined", number(evidence?.literature?.quarantined_records));
      setText("e-trials", number(evidence?.clinical_trials?.record_count));
      setText("e-results", number(evidence?.clinical_trials?.trials_with_results));
      setText("e-prevalence", number(evidence?.official_prevalence_resources?.length));
      const topics = q("e-topic-counts");
      if (topics && evidence?.literature?.topic_counts) {
        topics.innerHTML = "";
        const labels = {
          secondhand_exposure: "Second-hand aerosol exposure",
          thirdhand_residue: "Third-hand residue",
          indoor_air: "Indoor air / confined spaces",
          ultrafine_particles: "Ultrafine particles / particle number",
          aerosol_chemistry: "Aerosol chemistry / emissions",
          exposure_biomarkers: "Exposure biomarkers",
          cessation: "Smoking cessation / switching",
          youth: "Children / adolescents / young people",
          cardiovascular: "Cardiovascular outcomes",
          respiratory: "Respiratory outcomes"
        };
        const rows = Object.entries(evidence.literature.topic_counts).sort((a,b) => b[1]-a[1]);
        for (const [key, count] of rows) {
          const li = document.createElement("li");
          li.textContent = `${labels[key] || key}: ${number(count)}`;
          topics.appendChild(li);
        }
        if (!rows.length) topics.innerHTML = "<li>No topic tags are present in this publication.</li>";
      }
      const limits = q("evidence-limitations");
      if (limits && Array.isArray(evidence.limitations)) {
        limits.innerHTML = "";
        for (const item of evidence.limitations) {
          const li = document.createElement("li"); li.textContent = item; limits.appendChild(li);
        }
      }
    } catch (err) {
      setText("evidence-status", "No generated evidence summary has been published yet. The page will populate automatically after an approved Research publication.");
    }
  }

  async function prevalencePage() {
    const body = q("prevalence-age-rows");
    try {
      const data = await getJSON("evidence/ons_prevalence.json");
      const year = data.latest_year;
      setText("p-year", number(year));
      setText("p-count", number(data.estimate_count));
      const group = "All persons aged 16 and over";
      const dailyStat = "Proportion of population who are daily e-cigarette users";
      const occasionalStat = "Proportion of population who are occasional e-cigarette user";
      const daily = exactEstimate(data, year, group, dailyStat);
      const occasional = exactEstimate(data, year, group, occasionalStat);
      setText("p-daily", pct(daily?.estimate_percent)); setText("p-daily-ci", `All persons aged 16+; ${ciText(daily)}.`);
      setText("p-occasional", pct(occasional?.estimate_percent)); setText("p-occasional-ci", `All persons aged 16+; ${ciText(occasional)}.`);
      setText("prevalence-status", data.interpretation || "");

      if (body) {
        body.innerHTML = "";
        const ages = ["16-24", "25-34", "35-49", "50-59", "60 and over", "16 and over"];
        for (const age of ages) {
          const g = `All persons aged ${age}`;
          const d = exactEstimate(data, year, g, dailyStat);
          const o = exactEstimate(data, year, g, occasionalStat);
          if (!d && !o) continue;
          const tr = document.createElement("tr");
          [g.replace("All persons aged ", ""), pct(d?.estimate_percent), ciText(d), pct(o?.estimate_percent), ciText(o)].forEach((value, idx) => {
            const td = document.createElement("td"); td.textContent = value; if (idx === 2 || idx === 4) td.className = "confidence"; tr.appendChild(td);
          });
          body.appendChild(tr);
        }
      }
      const changes = q("prevalence-changes");
      if (changes && Array.isArray(data.important_data_changes)) {
        changes.innerHTML = "";
        for (const change of data.important_data_changes.slice(0, 6)) { const li = document.createElement("li"); li.textContent = change; changes.appendChild(li); }
      }
    } catch (err) {
      if (body) body.innerHTML = '<tr><td colspan="5">No validated ONS prevalence extract has been published yet.</td></tr>';
      setText("prevalence-status", "Awaiting an approved prevalence publication.");
    }
  }

  async function environmentPage() {
    const body = q("environment-rows");
    try {
      const data = await getJSON("environment/source_registry.json");
      setText("env-count", number(data.source_count));
      setText("env-production", number(data.production_candidates));
      setText("env-reviewed", safe(data.reviewed_at));
      const s4 = (data.sources || []).find(x => x.id === "sentinel4_uvn");
      setText("env-s4", safe(s4?.status));
      if (body) {
        body.innerHTML = "";
        for (const source of data.sources || []) {
          const tr = document.createElement("tr");
          const values = [source.name || source.id, source.role || "—", source.status || "—", source.spatial_scale || "—", (source.parameters || []).join(", "), source.implementation_phase ?? "—"];
          values.forEach((value, idx) => {
            const td = document.createElement("td");
            if (idx === 2) { const span = document.createElement("span"); span.className = `status ${String(value).replace(/[^a-z0-9_-]/gi,"-")}`; span.textContent = value; td.appendChild(span); }
            else td.textContent = value;
            tr.appendChild(td);
          });
          body.appendChild(tr);
        }
      }
    } catch (err) {
      if (body) body.innerHTML = '<tr><td colspan="6">The environmental source registry has not yet been published.</td></tr>';
    }
  }

  async function regulationPage() {
    const container = q("regulation-timeline");
    try {
      const data = await getJSON("regulation/timeline.json");
      setText("r-count", number(data.milestone_count));
      setText("r-reviewed", safe(data.reviewed_at));
      const today = new Date();
      const future = (data.milestones || []).filter(x => new Date(`${x.date}T00:00:00Z`) >= today).sort((a,b) => String(a.date).localeCompare(String(b.date)));
      const next = future[0];
      setText("r-next-date", safe(next?.date));
      setText("r-next-title", safe(next?.title));
      if (container) {
        container.innerHTML = "";
        for (const item of data.milestones || []) {
          const article = document.createElement("article"); article.className = "timeline-item";
          const dateBox = document.createElement("div"); dateBox.className = "timeline-date"; dateBox.textContent = item.date || "—";
          const body = document.createElement("div");
          const h = document.createElement("h3"); h.textContent = item.title || item.id; body.appendChild(h);
          const meta = document.createElement("p"); meta.textContent = `${item.status || "—"} · ${item.authority || "—"}`; body.appendChild(meta);
          const desc = document.createElement("p"); desc.textContent = item.summary || ""; body.appendChild(desc);
          if (item.source_url) { const a = document.createElement("a"); a.href = item.source_url; a.target = "_blank"; a.rel = "noopener noreferrer"; a.textContent = "Official source ↗"; body.appendChild(a); }
          article.appendChild(dateBox); article.appendChild(body); container.appendChild(article);
        }
      }
    } catch (err) {
      if (container) container.innerHTML = '<p>The verified regulatory timeline has not yet been published.</p>';
    }
  }

  async function sourcesPage() {
    const body = q("source-rows");
    if (!body) return;
    try {
      const [register, coverage] = await Promise.all([
        getJSON("provenance/source_register.json"),
        getJSON("provenance/source_coverage.json").catch(() => ({}))
      ]);
      const runMap = new Map((coverage.sources || []).map(x => [x.source_id, x]));
      body.innerHTML = "";
      for (const source of register.sources || []) {
        const run = runMap.get(source.id) || {};
        const tr = document.createElement("tr");
        const cells = [source.name || source.id, source.family || "—", source.evidence_role || "—", source.authority || "—", source.status || "—", run.run_status || "not attempted in published run"];
        cells.forEach((value, index) => {
          const td = document.createElement("td");
          if (index === 4) { const span = document.createElement("span"); span.className = `status ${String(value).replace(/[^a-z0-9_-]/gi, "-")}`; span.textContent = value; td.appendChild(span); }
          else td.textContent = value;
          tr.appendChild(td);
        });
        body.appendChild(tr);
      }
      setText("source-count", number(register.source_count));
      setText("source-generated", date(register.generated_at));
    } catch (err) {
      body.innerHTML = '<tr><td colspan="6">The public source register has not yet been generated.</td></tr>';
    }
  }

  return {dashboard, evidencePage, prevalencePage, environmentPage, regulationPage, sourcesPage};
})();
