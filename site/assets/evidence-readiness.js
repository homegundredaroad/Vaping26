(() => {
  const fmt = new Intl.NumberFormat("en-GB");
  const number = value => Number.isFinite(Number(value)) ? fmt.format(Number(value)) : "—";
  const pct = value => Number.isFinite(Number(value)) ? `${Number(value).toFixed(1)}%` : "—";
  const set = (id, value) => { const el = document.getElementById(id); if (el) el.textContent = value; };

  async function renderReviewReadiness() {
    try {
      const response = await fetch("evidence/health_evidence_summary.json", {cache: "no-store"});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      const readiness = payload.review_readiness || {};
      const trials = payload.clinical_trials || {};
      const unknownDesign = readiness.unknown_study_design || {};
      const unknownIntegrity = readiness.unknown_integrity_status || {};

      set("rr-reviewed", number(readiness.reviewed_record_count));
      set("rr-ready", number(readiness.conclusion_sensitive_ready_record_count));
      set("rr-design", `${number(unknownDesign.count)} (${pct(unknownDesign.percent)})`);
      set("rr-integrity", `${number(unknownIntegrity.count)} (${pct(unknownIntegrity.percent)})`);
      set("rr-trial-matched", number(trials.trials_with_matched_evidence_cards));
      set("rr-trial-unmatched", number(trials.unmatched_referenced_pmids));

      const status = document.getElementById("rr-status");
      if (status) {
        const ready = Number(readiness.conclusion_sensitive_ready_record_count || 0);
        status.textContent = ready > 0
          ? `${number(ready)} record${ready === 1 ? " is" : "s are"} human-reviewed and marked conclusion-sensitive synthesis ready.`
          : "No record is treated as conclusion-sensitive synthesis ready until both source-grounded extraction and human review are complete.";
      }
    } catch (_) {
      const status = document.getElementById("rr-status");
      if (status) status.textContent = "Review-maturity metrics will appear with the next approved Research publication.";
    }
  }

  window.addEventListener("DOMContentLoaded", renderReviewReadiness);
})();
