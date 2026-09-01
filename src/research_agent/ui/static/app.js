const $ = (id) => document.getElementById(id);

let lastEventId = 0;
let activeRawKey = null;
let latestRaw = {};
let refreshInFlight = false;

function text(id, value, fallback = "—") {
  const node = $(id);
  if (!node) return;
  const resolved = value === null || value === undefined || value === "" ? fallback : String(value);
  node.textContent = resolved;
  node.classList.toggle("muted", resolved === fallback);
}

function titleCase(value) {
  if (!value) return "";
  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatTokens(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n >= 10_000_000 ? 0 : 2)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(n >= 100_000 ? 0 : 1)}K`;
  return n.toLocaleString();
}

function setPill(id, value, variant = "") {
  const node = $(id);
  if (!node) return;
  node.textContent = value || "—";
  node.className = `quiet-pill${variant ? ` ${variant}` : ""}`;
}

function renderUsage(research) {
  const total = research.usage_status === "unavailable" ? null : research.usage_total;
  text("token-total", total === null || total === undefined ? null : formatTokens(total));
  const models = Array.isArray(research.usage_models) ? research.usage_models : [];
  const note = models.map(usageModelLabel).join(" · ");
  text("token-models", note || null, "No measured usage");
}

function usageModelLabel(item) {
  const roles = { meta: "META", scientist: "SCI", baseline: "BASE" };
  const role = roles[item.role] || titleCase(item.role || "model");
  const model = item.model && item.model !== "default" ? item.model : `${item.runner || "runner"} default`;
  const measured = ["measured", "partial"].includes(item.accounting_status);
  const amount = measured ? formatTokens(item.total) : "—";
  return `${role} ${model} ${amount}`;
}

function formatDuration(run) {
  if (!run?.started_at) return null;
  const started = Date.parse(run.started_at);
  if (!Number.isFinite(started)) return null;

  const ended = run.status === "running"
    ? Date.now()
    : run.ended_at
      ? Date.parse(run.ended_at)
      : NaN;
  if (!Number.isFinite(ended)) return null;

  let seconds = Math.max(0, Math.floor((ended - started) / 1000));
  const hours = Math.floor(seconds / 3600);
  seconds %= 3600;
  const minutes = Math.floor(seconds / 60);
  seconds %= 60;
  if (hours) return `${hours}h ${minutes}m`;
  if (minutes) return `${minutes}m ${seconds}s`;
  return `${seconds}s`;
}

function compactRun(run) {
  if (!run) return "No active run";
  const id = String(run.run_id || "run").slice(0, 8);
  const kind = run.kind ? ` · ${titleCase(run.kind)}` : "";
  return `${id}${kind}`;
}

function statusLabel(run) {
  if (!run) return "Idle";
  if (run.status === "running") return "Running";
  return titleCase(run.terminal_status || run.status || "Closed");
}

function renderRun(run, research) {
  const banner = $("run-banner");
  if (!banner) return;
  banner.className = "overview-strip";
  if (!run) {
    banner.classList.add("idle");
  } else if (run.status === "running") {
    banner.classList.add("running");
  } else if (["needs_human", "failed", "budget_exhausted"].includes(run.terminal_status)) {
    banner.classList.add("attention");
  } else {
    banner.classList.add("finished");
  }

  const mode = run?.kind === "parallel"
    ? "Parallel research and post-hoc review"
    : run?.kind === "baseline"
      ? "Blank-control optimization run"
      : "Live view of the current research world";
  text("header-subtitle", mode, "Live view of the current research world");
  text("record-version-badge", research.record_version ? research.record_version : null, "record version —");
  text("project", research.project);
  text("project-menu-name", research.project, "Project");
  text("run-detail", compactRun(run), "No active run");
  text("status-value", statusLabel(run), "Idle");
  const researchCycle = research.research_cycle_id ?? research.cycle_id;
  text("cycle", researchCycle);
  const cycleNote = research.research_cycle_id !== null && research.research_cycle_id !== undefined
    ? research.cycle_id !== null && research.cycle_id !== undefined && research.cycle_id !== research.research_cycle_id
      ? `State provenance · META cycle ${research.cycle_id}`
      : "State provenance"
    : "Current META cycle";
  text("cycle-note", cycleNote, "Research cycle");
  text("run-duration", formatDuration(run));
  text(
    "run-duration-note",
    run ? (run.status === "running" ? "Current run · updating" : "Latest closed run") : null,
    "No run duration",
  );
  text("state", research.state_id);
  const stateNote = research.state_id
    ? [research.state_git_tag, research.state_derived_from ? `from ${research.state_derived_from}` : null]
      .filter(Boolean)
      .join(" · ") || "Materialized State"
    : "No materialized State";
  text("state-note", stateNote, "No materialized State");
  text("best-score", research.best_metric, "No official score recorded");
  const bestScoreNote = [
    research.best_experiment_id ? `Experiment ${research.best_experiment_id}` : null,
    research.best_state_id ? `State ${research.best_state_id}` : null,
  ].filter(Boolean).join(" · ");
  text("best-score-note", bestScoreNote || null, "No official score recorded");
  renderUsage(research);
}

function renderState(research) {
  const stateId = research.state_id;
  text("current-state-id", stateId);
  if (stateId) {
    setPill("current-state-tag", "materialized", "state-pill");
    text("state-summary", research.state_summary, "State has no summary recorded.");
    const provenance = [
      research.state_git_tag,
      research.state_scientist_report ? `report · ${research.state_scientist_report}` : null,
    ].filter(Boolean).join(" · ");
    text("state-provenance", provenance || "State provenance is not available.", "State provenance is not available.");
  } else {
    setPill("current-state-tag", "not materialized", "muted-pill");
    text("state-summary", null, "No materialized State recorded.");
    text("state-provenance", null, "State provenance is not available.");
  }
}

function metricValue(metrics, name) {
  if (!Array.isArray(metrics)) return null;
  const item = metrics.find((candidate) => candidate && candidate.name === name);
  return item ? item.value : null;
}

function formatMetric(value, { signed = false } = {}) {
  const number = Number(value);
  if (!Number.isFinite(number)) return null;
  const formatted = number.toFixed(6);
  return signed && number >= 0 ? `+${formatted}` : formatted;
}

function renderFinalResult(research) {
  const stateId = research.state_id;
  const metrics = research.state_validation_metrics || [];
  const deltas = research.state_baseline_deltas || [];
  const hasMetrics = metrics.length > 0;

  text("final-result-state", stateId);
  setPill(
    "final-result-tag",
    stateId && hasMetrics ? "retained checkpoint" : "not recorded",
    stateId && hasMetrics ? "official" : "muted-pill",
  );
  text("final-result-summary", research.state_summary, "No retained validation result recorded.");
  text("final-result-gauc", formatMetric(metricValue(metrics, "GAUC")));
  text("final-result-ndcg", formatMetric(metricValue(metrics, "nDCG@5")));
  text("final-result-primary", formatMetric(metricValue(metrics, "primary")));
  text("final-result-delta", formatMetric(metricValue(deltas, "primary"), { signed: true }));
  text(
    "final-result-evidence",
    research.state_evidence_ref ? `Evidence · ${research.state_evidence_ref}` : null,
    "Evidence is not available.",
  );
}

function optionalRow(rowId, textId, value) {
  const row = $(rowId);
  if (!row) return false;
  const visible = value !== null && value !== undefined && String(value).trim() !== "";
  row.hidden = !visible;
  if (visible) text(textId, value);
  return visible;
}

function renderExperiment(research) {
  const hasExperiment = research.experiment_id !== null && research.experiment_id !== undefined;
  text("experiment-id", hasExperiment ? research.experiment_id : null);

  if (!hasExperiment) {
    setPill("experiment-status", "not recorded", "muted-pill");
  } else {
    const status = research.experiment_status ? titleCase(research.experiment_status) : "Recorded";
    const fidelity = research.experiment_fidelity ? titleCase(research.experiment_fidelity) : null;
    const label = [fidelity, status].filter(Boolean).join(" · ");
    const variant = research.experiment_official_score === true
      ? "official"
      : research.experiment_official_score === false
        ? "diagnostic"
        : "";
    setPill("experiment-status", label, variant);
  }

  const officialLabel = research.experiment_official_score === true
    ? "Official frontier"
    : research.experiment_official_score === false
      ? "Diagnostic only"
      : null;
  text("experiment-fidelity", research.experiment_fidelity);
  text("experiment-official", officialLabel);
  text("experiment-state", research.experiment_resulting_state);
  const evidenceCount = research.experiment_evidence_count;
  text("experiment-evidence", evidenceCount === null || evidenceCount === undefined ? null : `${evidenceCount} path${evidenceCount === 1 ? "" : "s"}`);

  const facts = $("evaluation-facts");
  if (facts) facts.hidden = !hasExperiment;
  const result = research.focus_kind === "experiment" ? null : research.experiment_result;
  const hasExperimentDetails = [
    optionalRow("experiment-result-row", "experiment-result", result),
    optionalRow("experiment-metric-row", "experiment-metric", research.experiment_metric),
    optionalRow("experiment-conclusion-row", "experiment-conclusion", research.experiment_conclusion),
  ].some(Boolean);
  const experimentDetails = $("experiment-details");
  const experimentPlaceholder = $("experiment-placeholder");
  if (experimentDetails) experimentDetails.hidden = !hasExperimentDetails;
  if (experimentPlaceholder) experimentPlaceholder.hidden = hasExperimentDetails || hasExperiment;
  if (experimentPlaceholder && hasExperiment && !hasExperimentDetails) {
    experimentPlaceholder.hidden = false;
    experimentPlaceholder.textContent = "No additional evaluation narrative recorded.";
    experimentPlaceholder.classList.add("muted");
  }
}

function renderResearch(research) {
  const focusKind = research.focus_kind ? titleCase(research.focus_kind) : "Latest record";
  text("focus-kind", focusKind, "Latest record");
  text("focus-id", research.focus_id);
  text("focus", research.focus, "No research record recorded.");

  const hasHypothesis = research.hypothesis_id || research.hypothesis;
  const hypothesisBlock = $("hypothesis-block");
  if (hypothesisBlock) hypothesisBlock.hidden = !hasHypothesis;
  if (hasHypothesis) {
    text("hypothesis-id", research.hypothesis_id);
    text("hypothesis", research.hypothesis, "No hypothesis recorded.");
  }

  renderState(research);
  renderExperiment(research);
  text("intuition", research.intuition, "No research intuition recorded yet.");
  text("summary", research.last_summary, "No run summary yet.");
  text("next-action", research.next_action, "No next action recorded.");

  const concerns = $("concerns");
  if (!concerns) return;
  concerns.replaceChildren();
  const visibleConcerns = Array.isArray(research.meta_concerns) ? research.meta_concerns.slice(0, 3) : [];
  if (visibleConcerns.length) {
    visibleConcerns.forEach((concern) => {
      const li = document.createElement("li");
      li.textContent = concern;
      concerns.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.className = "muted";
    li.textContent = "No current concerns.";
    concerns.appendChild(li);
  }
}

function renderParallel(run, research) {
  const card = $("parallel-card");
  if (!card) return;
  const visible = run?.kind === "parallel";
  card.hidden = !visible;
  if (!visible) return;

  text("parallel-id", research.parallel_id || run.parallel_id);
  const completed = research.parallel_rounds_completed;
  const total = research.parallel_rounds_total;
  const rounds = completed === null || completed === undefined
    ? null
    : `${completed}/${total || completed}`;
  text("parallel-rounds", rounds, "No rounds recorded");
  const selected = Array.isArray(research.parallel_selected_branches)
    ? research.parallel_selected_branches
    : [];
  text("parallel-selected", selected.length ? selected.join(" · ") : null, "No branch selected");
  text(
    "parallel-synthesis",
    research.parallel_synthesis_status ? titleCase(research.parallel_synthesis_status) : null,
    "Not requested",
  );

  const list = $("parallel-branches");
  if (!list) return;
  const branches = Array.isArray(research.parallel_branches) ? research.parallel_branches : [];
  list.replaceChildren();
  if (!branches.length) {
    list.innerHTML = '<div class="empty-state">Waiting for branch results…</div>';
    return;
  }

  branches.slice().reverse().forEach((branch) => {
    const row = document.createElement("div");
    row.className = `branch-row ${branch.status || "unknown"}`;

    const marker = document.createElement("div");
    marker.className = "branch-marker";

    const body = document.createElement("div");
    body.className = "branch-body";
    const heading = document.createElement("div");
    heading.className = "branch-heading";
    const name = document.createElement("span");
    name.className = "branch-name";
    name.textContent = branch.branch_id || "branch";
    const status = document.createElement("span");
    status.className = "branch-status";
    status.textContent = titleCase(branch.status || "unknown");
    heading.append(name, status);
    const summary = document.createElement("div");
    summary.className = "branch-summary";
    summary.textContent = branch.summary || "No branch summary recorded.";
    body.append(heading, summary);

    const meta = document.createElement("div");
    meta.className = "branch-meta";
    const labels = [
      branch.round ? `R${branch.round}` : null,
      branch.candidate_state_id || null,
      branch.selected ? "selected" : null,
    ].filter(Boolean);
    meta.textContent = labels.join(" · ") || "—";
    row.append(marker, body, meta);
    list.appendChild(row);
  });
}

function relativeTime(iso) {
  const timestamp = Date.parse(iso);
  if (!Number.isFinite(timestamp)) return "";
  const seconds = Math.max(0, Math.floor((Date.now() - timestamp) / 1000));
  if (seconds < 45) return "now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function cleanEventText(value) {
  return String(value || "").replace(/^[→✓✦]\s*/, "").trim();
}

function renderEvents(events) {
  const feed = $("events");
  if (!feed) return;
  if (!Array.isArray(events) || !events.length) {
    feed.innerHTML = '<div class="empty-state">Waiting for research activity…</div>';
    return;
  }

  const recent = events.slice(-5).reverse();
  feed.replaceChildren();
  recent.forEach((event) => {
    const row = document.createElement("div");
    row.className = `activity-row ${event.kind || "detail"}`;
    if (event.id > lastEventId) row.classList.add("new");

    const dot = document.createElement("div");
    dot.className = "activity-dot";

    const content = document.createElement("div");
    content.className = "activity-text";
    content.textContent = cleanEventText(event.text);

    const time = document.createElement("div");
    time.className = "activity-time";
    time.textContent = relativeTime(event.at);

    row.append(dot, content, time);
    feed.appendChild(row);
  });

  lastEventId = Math.max(lastEventId, ...events.map((event) => event.id || 0));
}

function setConnection(connected) {
  text("connection-label", connected ? "Live connection" : "Reconnecting…");
  const dot = $("live-dot");
  if (dot) dot.classList.toggle("offline", !connected);
}

async function refresh() {
  if (refreshInFlight) return;
  refreshInFlight = true;
  try {
    const response = await fetch("/api/status", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const research = data.research || {};
    renderRun(data.run, research);
    renderResearch(research);
    renderFinalResult(research);
    renderEvents(data.events);
    renderParallel(data.run, research);
    setConnection(true);
  } catch (error) {
    setConnection(false);
    console.error(error);
  } finally {
    refreshInFlight = false;
  }
}

function rawLabel(key) {
  const labels = {
    brief: "META brief",
    usage: "Usage",
    version: "Record version",
    state: "State",
    record: "Research record",
    intuition: "Research intuition",
    "parallel-manifest": "Parallel manifest",
    "parallel-result": "Parallel result",
    "parallel-aggregate": "Branch aggregate",
  };
  return labels[key] || key;
}

function selectRaw(key) {
  activeRawKey = key;
  const item = latestRaw[key];
  text("raw-path", item?.path || null, "Unknown artifact");
  text("raw-content", item?.content || null, "(empty or not created yet)");
  document.querySelectorAll(".raw-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.key === key);
    button.setAttribute("aria-pressed", button.dataset.key === key ? "true" : "false");
  });
}

async function loadRawFiles() {
  try {
    const response = await fetch("/api/files", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    latestRaw = payload && typeof payload === "object" ? payload : {};
    const toolbar = $("raw-tabs");
    if (!toolbar) return;
    toolbar.replaceChildren();
    const keys = Object.keys(latestRaw);
    keys.forEach((key) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "raw-tab";
      button.dataset.key = key;
      button.setAttribute("aria-pressed", "false");
      button.textContent = rawLabel(key);
      button.addEventListener("click", () => selectRaw(key));
      toolbar.appendChild(button);
    });
    const selectedKey = activeRawKey && latestRaw[activeRawKey] ? activeRawKey : keys[0];
    if (selectedKey) selectRaw(selectedKey);
  } catch (error) {
    setConnection(false);
    text("raw-path", null, "Dashboard disconnected");
    text(
      "raw-content",
      null,
      "Raw artifacts are unavailable while the local dashboard backend is disconnected. Restart or reconnect the GUI server, then reopen this panel.",
    );
    console.error(error);
  }
}

const rawDetails = document.querySelector(".raw-section details");
if (rawDetails) {
  rawDetails.addEventListener("toggle", (event) => {
    if (event.currentTarget.open) loadRawFiles();
  });
}

refresh();
setInterval(refresh, 1000);
