(() => {
  const fmt = new Intl.NumberFormat("en-GB");
  const q = id => document.getElementById(id);
  const number = value => Number.isFinite(Number(value)) ? fmt.format(Number(value)) : "—";

  async function getJSON(path) {
    const response = await fetch(path, {cache: "no-store"});
    if (!response.ok) throw new Error(`${response.status} ${path}`);
    return response.json();
  }

  function ciText(row) {
    const lo = row.lower_ci ?? row.lower_95_percent;
    const hi = row.upper_ci ?? row.upper_95_percent;
    return Number.isFinite(Number(lo)) && Number.isFinite(Number(hi))
      ? `${Number(lo).toFixed(1)}–${Number(hi).toFixed(1)}%`
      : "Not supplied";
  }

  function sourceName(row) {
    if (row.source_id === "ohid_fingertips") return "OHID Fingertips";
    if (row.source_id === "nhs_england_sdd") return "NHS England SDD";
    return row.source_id || "Source not supplied";
  }

  function normalise(row) {
    const source = sourceName(row);
    const period = row.time_period ?? row.survey_year ?? "";
    const area = row.area_name ?? row.region ?? (row.source_id === "nhs_england_sdd" ? "England" : "");
    const age = row.age ?? row.age_group ?? "";
    const sex = row.sex ?? row.gender ?? "";
    const group = [sex, row.category_type, row.category, row.smoking_status].filter(Boolean).join(" · ");
    return {
      raw: row,
      source,
      indicator: row.indicator || "—",
      period: String(period || ""),
      area: area || "—",
      age: age || "—",
      group: group || "—",
      value: Number.isFinite(Number(row.value)) ? String(row.value) : "—",
      ci: ciText(row),
    };
  }

  function addOption(select, value, label = value) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    select.appendChild(option);
  }

  async function loadYouthPage() {
    const status = q("youth-filter-count");
    try {
      const [youth, synthesis] = await Promise.all([
        getJSON("evidence/youth_prevalence.json"),
        getJSON("evidence/synthesis_register.json"),
      ]);
      const rows = Array.isArray(youth.records) ? youth.records.map(normalise) : [];
      const indicators = Array.isArray(youth.indicators) ? youth.indicators : [];
      const youthQuestion = (synthesis.questions || []).find(item => item.id === "youth_use") || {};

      q("y-rows").textContent = number(youth.record_count);
      q("y-indicators").textContent = number(indicators.length);
      q("y-candidates").textContent = number(youthQuestion.candidate_cards);
      q("y-areas").textContent = number(new Set(rows.map(row => row.area).filter(value => value && value !== "—")).size);

      const tbody = q("youth-rows");
      const indicatorSel = q("y-filter-indicator");
      const timeSel = q("y-filter-time");
      const areaInput = q("y-filter-area");
      if (!tbody || !indicatorSel || !timeSel || !areaInput) return;

      indicators.forEach(value => addOption(indicatorSel, value));
      [...new Set(rows.map(row => row.period).filter(Boolean))]
        .sort((a, b) => String(b).localeCompare(String(a), undefined, {numeric: true}))
        .forEach(value => addOption(timeSel, value));

      const apply = () => {
        const area = String(areaInput.value || "").trim().toLowerCase();
        const filtered = rows.filter(row =>
          (!indicatorSel.value || row.indicator === indicatorSel.value) &&
          (!timeSel.value || row.period === timeSel.value) &&
          (!area || row.area.toLowerCase().includes(area))
        );
        tbody.innerHTML = "";
        filtered.slice(0, 250).forEach(row => {
          const tr = document.createElement("tr");
          [row.source, row.indicator, row.period || "—", row.area, row.age, row.group, row.value, row.ci].forEach(value => {
            const td = document.createElement("td");
            td.textContent = value;
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
        status.textContent = `${number(filtered.length)} matching official-statistics row${filtered.length === 1 ? "" : "s"}${filtered.length > 250 ? "; first 250 shown" : ""}. OHID and NHS England retain their original source schemas in the downloadable JSON.`;
      };

      [indicatorSel, timeSel].forEach(el => el.addEventListener("change", apply));
      areaInput.addEventListener("input", apply);
      apply();
    } catch (error) {
      const tbody = q("youth-rows");
      if (tbody) tbody.innerHTML = '<tr><td colspan="8">Approved youth data could not be loaded. Check the current release status rather than interpreting missing values as zero.</td></tr>';
      if (status) status.textContent = `Data load error: ${error.message}`;
    }
  }

  window.V26YouthPage = loadYouthPage;
})();
