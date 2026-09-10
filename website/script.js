"use strict";

// Content and measurements follow slides/slides.md and its current components.
// All interactive demos are local illustrations; no research commands are executed.
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const setText = (selector, value) => {
  $(selector).textContent = value;
};
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
function animateContent(element) {
  if (reducedMotion.matches) return;
  element.classList.remove("content-enter");
  void element.offsetWidth;
  element.classList.add("content-enter");
}

// Native buttons, roving focus, and arrow / Home / End navigation for every tab set.
function wireTabs(selector, onSelect) {
  const tabs = $$(selector);
  function select(tab, focus = false) {
    tabs.forEach((item) => {
      const active = item === tab;
      item.setAttribute("aria-selected", String(active));
      item.tabIndex = active ? 0 : -1;
    });
    onSelect(tab);
    if (focus) tab.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => select(tab));
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight" || event.key === "ArrowDown")
        next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft" || event.key === "ArrowUp")
        next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next !== undefined) {
        event.preventDefault();
        select(tabs[next], true);
      }
    });
  });
  return select;
}

const menu = $(".menu-toggle");
const navigation = $("#navigation");
function closeMenu(returnFocus = false) {
  menu.setAttribute("aria-expanded", "false");
  menu.setAttribute("aria-label", "Open navigation");
  navigation.classList.remove("is-open");
  if (returnFocus) menu.focus();
}
menu.addEventListener("click", () => {
  const opened = menu.getAttribute("aria-expanded") !== "true";
  menu.setAttribute("aria-expanded", String(opened));
  menu.setAttribute(
    "aria-label",
    opened ? "Close navigation" : "Open navigation",
  );
  navigation.classList.toggle("is-open", opened);
});
$$("a", navigation).forEach((link) =>
  link.addEventListener("click", () => closeMenu()),
);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menu.getAttribute("aria-expanded") === "true")
    closeMenu(true);
});
document.addEventListener("click", (event) => {
  if (!$(".site-header").contains(event.target)) closeMenu();
});
window.matchMedia("(min-width: 641px)").addEventListener("change", (event) => {
  if (event.matches) closeMenu();
});

const capabilities = {
  robust: {
    number: "01",
    html: `<h2 class="scene-title">An unexpected error.<br><em>A way forward.</em></h2><div class="scene-stage"><div class="scene-row error"><span class="scene-icon">!</span><div>Experiment interrupted<small>NumPy scalar serialization error</small></div><span class="scene-end">INSPECT</span></div><div class="connecting-arrow" aria-hidden="true">↓</div><div class="scene-row"><span class="scene-icon">⌘</span><div>Scientist repairs the code<small>Read traceback · patch helper · retry</small></div><span class="scene-end">RECOVER</span></div><div class="scene-row selected"><span class="scene-icon">✓</span><div>Research continues<small>Evidence and telemetry preserved</small></div></div></div><p class="scene-caption">CYCLE 01 RECOVERY / NO HUMAN BUGFIX</p>`,
  },
  supervisable: {
    number: "02",
    html: `<h2 class="scene-title">Let it investigate.<br><em>See what stays.</em></h2><div class="scene-stage"><div class="scene-row"><span class="scene-icon">↗</span><div>Scientist runs an experiment<small>Hypothesis · code · metrics · report</small></div></div><div class="scene-row review"><span class="scene-icon">✓</span><div>META checks the science<small>Claims audited against evidence</small></div></div><div class="scene-row selected"><span class="scene-icon">◎</span><div>Inspect the retained State<small>One bounded step returns control to you</small></div></div></div><p class="scene-caption">AUTONOMOUS RESEARCH / VISIBLE EVIDENCE</p>`,
  },
  broad: {
    number: "03",
    html: `<h2 class="scene-title">One starting point.<br><em>Independent answers.</em></h2><div class="branch-source">Research World <span class="tiny-label">/ SHARED CONTEXT</span></div><div class="branch-spread" aria-hidden="true">↙↓↘</div><div class="hero-branches"><div><b>A</b><strong>Scientist</strong><small>Isolated worktree</small></div><div><b>B</b><strong>Scientist</strong><small>Isolated worktree</small></div><div><b>C</b><strong>Scientist</strong><small>Isolated worktree</small></div></div><div class="branch-spread" aria-hidden="true">↘↓↙</div><div class="branch-source">Reviewer <span class="tiny-label">/ EXPLICIT ADOPTION</span></div><p class="scene-caption">EXPLORE INDEPENDENTLY / REVIEW AFTER COMPLETION</p>`,
  },
};
function showCapability(tab) {
  const data = capabilities[tab.dataset.capability];
  setText("#hero-scene-number", data.number);
  $("#hero-scene").innerHTML = data.html;
  $("#hero-scene").setAttribute("aria-labelledby", tab.id);
  animateContent($("#hero-scene"));
}
wireTabs("[data-capability]", showCapability);
showCapability($("#capability-robust"));

$$(".insight-toggle").forEach((button) =>
  button.addEventListener("click", () => {
    const open = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-expanded", String(open));
    $(`#${button.getAttribute("aria-controls")}`).hidden = !open;
    $("span", button).textContent = open ? "−" : "+";
  }),
);

const layers = {
  world: {
    mark: "◎",
    kicker: "01 / THE CONTINUITY LAYER",
    title: "Experience is<br>the starting point.",
    description:
      "The research world outlives any single conversation. Every new Scientist starts with what the project has learned.",
    items: [
      "Verified knowledge and an evidence ledger",
      "A curated research brief and revisable priors",
      "Retained implementation state",
    ],
    principle: "Persistent experience. Independent reasoning.",
  },
  scientist: {
    mark: "S",
    kicker: "02 / SCIENTIFIC AUTHORITY",
    title: "A fresh mind.<br>An informed start.",
    description:
      "The Scientist owns scientific judgment. A new reasoning trajectory can deepen a promising direction or investigate a different mechanism.",
    items: [
      "Read the world and form hypotheses",
      "Write code, run experiments, interpret results",
      "Leave evidence and a free-form report",
    ],
    principle: "Inherit the experience, not the momentum.",
  },
  meta: {
    mark: "✓",
    kicker: "03 / PERSISTENCE AUTHORITY",
    title: "Keep the evidence.<br>Check the conclusion.",
    description:
      "META independently audits what should survive. It maintains research memory without choosing the Scientist’s next hypothesis.",
    items: [
      "Check scientific claims against code and evidence",
      "Scope conclusions and preserve negative results",
      "Crystallize retained implementation into State",
    ],
    principle: "A working experiment is not automatically valid science.",
  },
  runtime: {
    mark: "⌘",
    kicker: "FOUNDATION / DETERMINISTIC MECHANICS",
    title: "Open tools.<br>Room to recover.",
    description:
      "The coding-agent harness acts in an open environment. Runtime supports reliable execution while the agent can inspect errors and acquire missing tools.",
    items: [
      "Isolated workspaces and process cancellation",
      "Runner, evaluator, logs, and artifact capture",
      "Shell, files, browser, Git, Skills, and MCP",
    ],
    principle: "Use what exists. Fix what breaks. Add what is missing.",
  },
};
wireTabs("[data-layer]", (tab) => {
  const data = layers[tab.dataset.layer];
  $$("[data-layer]").forEach((button) =>
    button.classList.toggle("selected", button === tab),
  );
  setText(".detail-mark", data.mark);
  setText("#layer-kicker", data.kicker);
  $("#layer-title").innerHTML = data.title;
  setText("#layer-description", data.description);
  $("#layer-list").innerHTML = data.items
    .map((item) => `<li>${item}</li>`)
    .join("");
  setText("#layer-principle", data.principle);
  $("#layer-detail").setAttribute("aria-labelledby", tab.id);
  animateContent($("#layer-detail"));
});

const taskEditor = $("#demo-content").innerHTML;
const personalEditor = `<div class="editor-line"><span>01</span><b># Working preferences</b></div><div class="editor-line"><span>02</span>Use macOS / Apple Silicon + uv.</div><div class="editor-line"><span>03</span></div><div class="editor-line"><span>04</span><b># Constraints</b></div><div class="editor-line"><span>05</span>≤ 15 minutes per experiment.</div><div class="editor-line"><span>06</span>Never print credentials.</div><div class="editor-line"><span>07</span></div><span class="editor-cursor" aria-hidden="true"></span>`;
const defineDemo = `<div class="brief-tabs" role="group" aria-label="Research brief files"><button data-brief="task" aria-pressed="true">task.md</button><button data-brief="personal" aria-pressed="false">PERSONAL.md</button></div><div id="brief-editor">${taskEditor}</div>`;
$("#demo-content").addEventListener("click", (event) => {
  const button = event.target.closest("[data-brief]");
  if (!button) return;
  $$("[data-brief]").forEach((item) =>
    item.setAttribute("aria-pressed", String(item === button)),
  );
  $("#brief-editor").innerHTML =
    button.dataset.brief === "personal" ? personalEditor : taskEditor;
});
const command = (verb, options) =>
  `<pre class="terminal-command"><span class="prompt">❯</span> ./scripts/research-agent ${verb}\n  ${options}</pre>`;
const journeys = [
  {
    kicker: "START YOUR JOURNEY",
    title: "Set the question.<br>Define the boundaries.",
    description:
      "Write the research objective in task.md and your working preferences in PERSONAL.md. The Scientist chooses the experiments.",
    filename: "task.md + PERSONAL.md",
    status: "Research brief ready",
    footer: "YOU SET THE BOUNDARY",
    html: defineDemo,
  },
  {
    kicker: "ONE STEP",
    title: "Run one cycle.<br>Then, review.",
    description:
      "Run a bounded autonomous cycle. The Scientist investigates, evidence is recorded, and control returns to you.",
    filename: "Terminal / step",
    status: "Evidence retained. Control returned.",
    footer: "ONE BOUNDED CYCLE",
    html:
      command("step", "--cli codex --target ./project --allow-edits") +
      '<div class="demo-flow"><div class="demo-node">Scientist<small>Investigate</small></div><i>→</i><div class="demo-node">Evidence<small>Record</small></div><i>→</i><div class="demo-node">META<small>Audit + retain</small></div></div><p class="demo-result">✓ Your turn. Inspect the evidence before continuing.</p>',
  },
  {
    kicker: "LET IT RUN",
    title: "Continue the work.<br>Across cycles.",
    description:
      "Set a cycle budget. Each round starts with a fresh Scientist while task, memory, and evidence stay with the project.",
    filename: "Terminal / run",
    status: "Four bounded cycles, one shared world",
    footer: "CONTINUITY ACROSS TIME",
    html:
      command(
        "run",
        "--cli codex --target ./project\n  --max-cycles 4 --allow-edits",
      ) +
      '<div class="demo-flow">' +
      [1, 2, 3, 4]
        .map(
          (n, i) =>
            `${i ? "<i>→</i>" : ""}<div class="demo-node" style="animation-delay:${i * 120}ms">Cycle ${n}<small>Scientist → META</small></div>`,
        )
        .join("") +
      '</div><p class="demo-result">↻ Fresh reasoning. Audited evidence. Updated world.</p>',
  },
  {
    kicker: "NOW, EXPLORE WIDER",
    title: "Same starting point.<br>Different directions.",
    description:
      "Explore in independent worktrees. A Reviewer compares completed worlds; adopting a result remains an explicit decision.",
    filename: "Terminal / parallel",
    status: "Branches reviewed; adoption is explicit",
    footer: "INDEPENDENT SEARCH",
    html:
      command(
        "parallel",
        "--cli codex --target ./project --branches 3\n  --parallelism 3 --keep 1 --allow-edits",
      ) +
      '<div class="demo-parallel">' +
      ["A", "B", "C"]
        .map(
          (name, i) =>
            `<div class="demo-branch">Scientist ${name}<small>worktree r1b${i + 1}</small></div>`,
        )
        .join("") +
      '</div><p class="demo-result">Reviewer → adopt with parallel-promote</p>',
  },
  {
    kicker: "SEE WHAT STAYS",
    title: "The result.<br>And the evidence.",
    description:
      "Open the read-only dashboard. Inspect the retained score, implementation state, research record, and resource usage.",
    filename: "Research Agent / dashboard",
    status: "Retained checkpoint S004",
    footer: "READ-ONLY VIEW",
    html:
      command("gui", "--target ./project") +
      '<div class="dashboard-demo"><span class="tiny-label">S004 / RETAINED PUBLIC-VALIDATION PRIMARY</span><div class="dashboard-score">0.6059363 <span style="font-size:17px;color:var(--muted)">↗</span></div><div class="dashboard-metrics"><span><strong>4</strong>Autonomous cycles</span><span><strong>13</strong>Experiments</span><span><strong>48.24M</strong>Tokens incl. cache</span></div></div>',
  },
  {
    kicker: "ALREADY IN YOUR WORKFLOW",
    title: "Your coding agent.<br>A research workflow.",
    description:
      "Use the research-agent skill in your existing coding agent. The task, memory, and evidence remain connected to your project.",
    filename: "Coding agent / research-agent skill",
    status: "Research workflow connected",
    footer: "YOUR TOOLS. YOUR PROJECT.",
    html: '<p class="tiny-label" style="color:var(--muted);margin-bottom:20px">SKILL.md / research-agent</p><div class="skill-prompt">Use the research-agent skill.</div><p class="skill-response">“Explore in parallel. Let me review what to keep.”</p><p class="demo-result">S Research workflow, connected.</p><p class="skill-files">task.md &nbsp;·&nbsp; research_record/ &nbsp;·&nbsp; system/</p>',
  },
];
let journeyIndex = 0;
function showJourney(tab) {
  journeyIndex = Number(tab.dataset.step);
  const data = journeys[journeyIndex];
  setText("#journey-kicker", data.kicker);
  $("#journey-title").innerHTML = data.title;
  setText("#journey-description", data.description);
  setText(
    "#journey-count",
    `${String(journeyIndex + 1).padStart(2, "0")} / 06`,
  );
  setText("#demo-filename", data.filename);
  setText("#demo-status", data.status);
  setText("#demo-footer-label", data.footer);
  $("#demo-content").innerHTML = data.html;
  $("#demo-content").scrollTop = 0;
  $("#journey-panel").setAttribute("aria-labelledby", tab.id);
  $("#journey-next").setAttribute(
    "aria-label",
    journeyIndex === 5 ? "Restart walkthrough" : "Next walkthrough step",
  );
  animateContent($("#demo-content"));
}
const selectJourney = wireTabs("[data-step]", showJourney);
$("#journey-next").addEventListener("click", () =>
  selectJourney($(`[data-step="${(journeyIndex + 1) % journeys.length}"]`)),
);
showJourney($("#journey-tab-0"));

// Experience View Switcher (Video Demo vs Interactive Walkthrough)
const videoTab = $("#view-tab-video");
const walkthroughTab = $("#view-tab-walkthrough");
const videoView = $("#experience-video-view");
const walkthroughView = $("#experience-walkthrough-view");

function setExperienceView(mode) {
  const isVideo = mode === "video";
  videoTab.classList.toggle("active", isVideo);
  videoTab.setAttribute("aria-selected", String(isVideo));
  videoTab.tabIndex = isVideo ? 0 : -1;

  walkthroughTab.classList.toggle("active", !isVideo);
  walkthroughTab.setAttribute("aria-selected", String(!isVideo));
  walkthroughTab.tabIndex = !isVideo ? 0 : -1;

  videoView.hidden = !isVideo;
  walkthroughView.hidden = isVideo;

  if (isVideo) {
    animateContent(videoView);
  } else {
    animateContent(walkthroughView);
    showJourney($(`[data-step="${journeyIndex}"]`));
  }
}

videoTab.addEventListener("click", () => setExperienceView("video"));
walkthroughTab.addEventListener("click", () => setExperienceView("walkthrough"));
videoTab.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight" || e.key === "ArrowDown") {
    e.preventDefault();
    setExperienceView("walkthrough");
    walkthroughTab.focus();
  }
});
walkthroughTab.addEventListener("keydown", (e) => {
  if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
    e.preventDefault();
    setExperienceView("video");
    videoTab.focus();
  }
});

// Demo Video Player & Narration Sync
const expVideo = $("#experience-video");
const videoOverlay = $("#video-overlay");
const videoPlayBtn = $("#video-play-btn");
const videoFsBtn = $("#video-fs-btn");
const chapterPills = $$(".chapter-pill");
const liveCaption = $("#live-caption-text");

const demoCues = [
  { start: 0.8, end: 8.5, text: "SciOdyssey. A research layer over your agent harness. Your tools. One persistent research world." },
  { start: 9.4, end: 12.2, text: "Start with your research question." },
  { start: 13.7, end: 19.8, text: "Define the objective and how success will be measured." },
  { start: 20.7, end: 27.8, text: "Then set your working preferences: the environment, experiment budget, and boundaries." },
  { start: 29.2, end: 32.2, text: "One step. Then, review." },
  { start: 33.3, end: 43.7, text: "Run one research cycle with step. The Scientist investigates. Evidence is recorded. And control returns to you." },
  { start: 45.0, end: 48.0, text: "Or, let it run." },
  { start: 49.1, end: 61.5, text: "Set a cycle budget. A fresh Scientist continues the work each round, while the project carries the task, memory, and evidence forward." },
  { start: 62.8, end: 65.6, text: "Now, explore wider." },
  { start: 66.9, end: 73.2, text: "Use parallel to explore different directions in independent worktrees." },
  { start: 74.0, end: 81.3, text: "A Reviewer compares the evidence. Choosing a branch to adopt remains an explicit decision." },
  { start: 82.6, end: 85.5, text: "See what stays." },
  { start: 86.7, end: 91.0, text: "Open the dashboard to inspect the retained result." },
  { start: 91.7, end: 101.0, text: "See the score, the implementation state, and the evidence behind it. Then decide what comes next." },
  { start: 102.4, end: 105.4, text: "Already in your workflow." },
  { start: 106.5, end: 109.8, text: "Use the research-agent skill." },
  { start: 110.1, end: 114.0, text: "Explore in parallel. Let me review what to keep." },
  { start: 114.5, end: 119.2, text: "Research workflow, connected. Task, memory, and evidence stay with the project." },
  { start: 120.3, end: 126.0, text: "SciOdyssey. Let research run. Start your journey." }
];

const chapterStarts = [0.8, 29.2, 45.0, 62.8, 82.6, 102.4];

async function playExpVideo() {
  try {
    expVideo.muted = false;
    await expVideo.play();
    videoOverlay.classList.add("hidden");
  } catch {
    expVideo.muted = true;
    await expVideo.play();
    videoOverlay.classList.add("hidden");
  }
}

videoOverlay.addEventListener("click", playExpVideo);
videoPlayBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  playExpVideo();
});

expVideo.addEventListener("play", () => videoOverlay.classList.add("hidden"));
expVideo.addEventListener("pause", () => {
  if (expVideo.currentTime < expVideo.duration) videoOverlay.classList.remove("hidden");
});
expVideo.addEventListener("ended", () => videoOverlay.classList.remove("hidden"));

videoFsBtn.addEventListener("click", async () => {
  if (expVideo.requestFullscreen) await expVideo.requestFullscreen();
  else if (expVideo.webkitEnterFullscreen) expVideo.webkitEnterFullscreen();
});

chapterPills.forEach((pill) => {
  pill.addEventListener("click", () => {
    const time = parseFloat(pill.dataset.time);
    expVideo.currentTime = time;
    playExpVideo();
    chapterPills.forEach((p) => p.classList.toggle("active", p === pill));
  });
});

expVideo.addEventListener("timeupdate", () => {
  const current = expVideo.currentTime;
  const cue = demoCues.find((c) => current >= c.start && current < c.end);
  if (cue && liveCaption.textContent !== cue.text) {
    liveCaption.textContent = cue.text;
  }
  let activeChapterIdx = 0;
  for (let i = 0; i < chapterStarts.length; i++) {
    if (current >= chapterStarts[i]) activeChapterIdx = i;
  }
  chapterPills.forEach((pill, idx) => {
    pill.classList.toggle("active", idx === activeChapterIdx);
  });
});

wireTabs("[data-evidence]", (tab) => {
  $$("[data-evidence]").forEach((button) => {
    $(`#evidence-${button.dataset.evidence}`).hidden = button !== tab;
  });
  animateContent($(`#evidence-${tab.dataset.evidence}`));
});

// Actual seven Full evaluation scores from EvaluationTrajectory.vue.
const experiments = [
  { id: "E003", score: 0.601631, cycle: 0 },
  { id: "E004", score: 0.601631, cycle: 0 },
  { id: "E007", score: 0.6030889, cycle: 1 },
  { id: "E008", score: 0.6040901, cycle: 1 },
  { id: "E009", score: 0.6044289, cycle: 2 },
  { id: "E012", score: 0.6054846, cycle: 3 },
  { id: "E013", score: 0.6059363, cycle: 3 },
];
const cycles = [
  {
    range: "E001–E004",
    description:
      "Reject weak target encoding and establish a valid, recoverable 15-field FM baseline.",
    score: "0.6016310",
  },
  {
    range: "E005–E008",
    description:
      "Expand to 38 fields and a five-seed ensemble to move beyond the initial plateau.",
    score: "0.6040901",
  },
  {
    range: "E009",
    description:
      "An eight-seed ensemble reduces optimization variance and improves the retained frontier.",
    score: "0.6044289",
  },
  {
    range: "E010–E013",
    description:
      "46 feature interactions and an eight-seed FM ensemble deliver the final retained result.",
    score: "0.6059363",
  },
];
const xs = [65, 155, 320, 420, 565, 750, 870];
const chartY = (score) => 222 - ((score - 0.6013) / 0.0049) * 184;
const points = experiments.map((e, i) => ({
  ...e,
  x: xs[i],
  y: chartY(e.score),
}));
const line = points.map((p) => `${p.x},${p.y}`).join(" ");
$("#trajectory-chart").innerHTML =
  `<svg viewBox="0 0 940 268" role="img" aria-labelledby="trajectory-title trajectory-description"><title id="trajectory-title">Retained public-validation Primary across seven Full evaluations</title><desc id="trajectory-description">Official reference: 0.6016; Reproduced baseline (E003): 0.6016310. E003 and E004: 0.6016310. E007: 0.6030889. E008: 0.6040901. E009: 0.6044289. E012: 0.6054846. E013: 0.6059363.</desc><defs><linearGradient id="trajectory-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#38bdf8" stop-opacity=".19"/><stop offset="1" stop-color="#38bdf8" stop-opacity="0"/></linearGradient></defs><rect id="active-cycle-zone" class="chart-zone" x="673" y="20" width="237" height="205" rx="4"/>${[0.602, 0.603, 0.604, 0.605, 0.606].map((v) => `<line class="chart-grid" x1="55" x2="910" y1="${chartY(v)}" y2="${chartY(v)}"/><text class="chart-label" x="3" y="${chartY(v) + 4}">${v.toFixed(3)}</text>`).join("")}<line class="chart-reference" x1="55" x2="910" y1="${chartY(0.6016)}" y2="${chartY(0.6016)}"/><text class="chart-label" x="430" y="${chartY(0.6016) - 10}">Official reference · 0.6016</text><path class="chart-area" d="M${points[0].x},225 L${line.replaceAll(" ", " L")} L870,225Z"/><polyline class="chart-frontier" points="${line}"/>${points.map((p) => `<circle class="chart-point ${p.cycle === 3 ? "active" : ""}" data-point-cycle="${p.cycle}" cx="${p.x}" cy="${p.y}" r="4.5"><title>${p.id}: ${p.score.toFixed(7)}</title></circle><text class="chart-label" text-anchor="middle" x="${p.x}" y="${p.y - 15}">${p.id}</text>`).join("")}<text class="chart-label" x="65" y="252">FULL PUBLIC-VALIDATION EVALUATIONS</text><text class="chart-label" text-anchor="end" x="870" y="252">E001–E013 / RETAINED RUN</text></svg>`;
const cycleZones = [
  [55, 183],
  [248, 249],
  [507, 151],
  [668, 242],
];
$$("[data-cycle]").forEach((button) =>
  button.addEventListener("click", () => {
    const index = Number(button.dataset.cycle);
    $$("[data-cycle]").forEach((item) =>
      item.setAttribute("aria-pressed", String(item === button)),
    );
    const data = cycles[index];
    $("#cycle-detail").innerHTML =
      `<span>${data.range}</span><p>${data.description}</p><strong>${data.score}</strong>`;
    $$("[data-point-cycle]").forEach((point) =>
      point.classList.toggle(
        "active",
        Number(point.dataset.pointCycle) === index,
      ),
    );
    $("#active-cycle-zone").setAttribute("x", cycleZones[index][0]);
    $("#active-cycle-zone").setAttribute("width", cycleZones[index][1]);
  }),
);

// Comparison numbers and status come from the chart in slides/slides.md.
const setups = [
  {
    label: "Direct Gemini",
    score: 0.6045803,
    tokens: 8.565,
    color: "#5d7fbd",
    detail:
      "Direct gemini-3.7-flash: 8.565M tokens · Primary 0.6045803 · artifact-backed result.",
  },
  {
    label: "Direct GPT Luna",
    score: 0.6046,
    tokens: 28.07,
    color: "#e98238",
    detail:
      "Direct gpt-5.6-luna: 28.070M tokens · Primary ≈0.6046 · provisional. This is a distinct control from the eleven-cycle Codex trajectory.",
  },
  {
    label: "Heterogeneous",
    score: 0.6047,
    tokens: 39.607,
    color: "#df7328",
    detail:
      "Heterogeneous delegated run with gemini-3.7-flash: 39.607M tokens · Primary ≈0.6047.",
  },
  {
    label: "SciOdyssey + Antigravity",
    score: 0.6052,
    tokens: (45.044 + 51.174) / 2,
    color: "#a66cff",
    detail:
      "SciOdyssey with Antigravity, Gemini-only: E008 · Primary 0.6052 · 45.044–51.174M tokens. The horizontal interval represents token-accounting uncertainty.",
  },
  {
    label: "SciOdyssey submission",
    score: 0.6059363,
    tokens: 48.24,
    color: "#16803b",
    detail:
      "Retained SciOdyssey submission: 48.240M tokens · Primary 0.6059363 · verified. Full-system tokens include input, output, and cache-read input.",
  },
];
const sx = (tokens) => 67 + (tokens / 55) * 795;
const sy = (score) => 252 - ((score - 0.6015) / 0.0048) * 215;
$("#comparison-chart").innerHTML =
  `<svg viewBox="0 0 930 330" role="img" aria-labelledby="comparison-title comparison-desc"><title id="comparison-title">Primary score versus measured LLM-token investment</title><desc id="comparison-desc">Distinct setups rather than a controlled causal ablation. Direct Gemini: 8.565M, 0.6045803. Direct GPT Luna: 28.070M, approximately 0.6046, provisional. Heterogeneous: 39.607M, approximately 0.6047. SciOdyssey Antigravity: 45.044 to 51.174M, 0.6052. Retained SciOdyssey: 48.240M, 0.6059363.</desc>${[0.602, 0.603, 0.604, 0.605, 0.606].map((v) => `<line class="chart-grid" x1="67" x2="862" y1="${sy(v)}" y2="${sy(v)}"/><text class="chart-label" x="12" y="${sy(v) + 4}">${v.toFixed(3)}</text>`).join("")}${[0, 10, 20, 30, 40, 50, 55].map((v) => `<line class="chart-grid" x1="${sx(v)}" x2="${sx(v)}" y1="25" y2="257"/><text class="chart-label" text-anchor="middle" x="${sx(v)}" y="280">${v}</text>`).join("")}<line class="chart-reference" x1="67" x2="862" y1="${sy(0.6016)}" y2="${sy(0.6016)}"/><text class="chart-label" x="85" y="${sy(0.6016) - 8}">Official reference · 0.6016</text><line x1="${sx(45.044)}" x2="${sx(51.174)}" y1="${sy(0.6052)}" y2="${sy(0.6052)}" stroke="#a66cff" stroke-width="2"/>${setups.map((s, i) => `<g><circle class="scatter-dot" data-scatter="${i}" cx="${sx(s.tokens)}" cy="${sy(s.score)}" r="${i === 4 ? 9 : 6}" fill="${s.color}"><title>${s.detail}</title></circle><text class="scatter-label" text-anchor="${i >= 2 ? "end" : "start"}" x="${sx(s.tokens) + (i >= 2 ? -12 : 12)}" y="${sy(s.score) + (i === 2 ? 26 : -13)}">${s.label}</text></g>`).join("")}<text class="chart-label" text-anchor="middle" x="465" y="310">TOTAL LLM TOKENS (MILLIONS) · INCLUDING CACHE-READ</text></svg>`;
$(".comparison-options").innerHTML = setups
  .map(
    (s, i) =>
      `<button type="button" data-setup="${i}" aria-pressed="${i === 4}">${s.label}</button>`,
  )
  .join("");
setText("#comparison-detail", setups[4].detail);
$$("[data-setup]").forEach((button) =>
  button.addEventListener("click", () => {
    const index = Number(button.dataset.setup);
    $$("[data-setup]").forEach((b) =>
      b.setAttribute("aria-pressed", String(b === button)),
    );
    $$("[data-scatter]").forEach((point) => {
      point.setAttribute("r", Number(point.dataset.scatter) === index ? 10 : 5);
      point.style.opacity =
        Number(point.dataset.scatter) === index ? "1" : ".4";
    });
    setText("#comparison-detail", setups[index].detail);
  }),
);

const modelPatterns = {
  depth: {
    description:
      "Disciplined local refinement: feature cleanup, hyperparameter tuning, and careful exploitation.",
    color: "#ff873f",
    edges: "M30 40L105 62L180 62L260 62L365 62",
    quiet: "M30 40L105 16 M105 62L180 25 M180 62L260 28",
    points: [
      [30, 40],
      [105, 62],
      [180, 62],
      [260, 62],
      [365, 62],
    ],
  },
  breadth: {
    description:
      "Broad hypothesis exploration: representation changes, mechanism pivots, and candidate screening.",
    color: "#38bdf8",
    edges:
      "M30 40L125 13L365 13 M30 40L125 34L365 34 M30 40L125 55L365 55 M30 40L125 76L365 76",
    quiet: "",
    points: [
      [30, 40],
      [125, 13],
      [125, 34],
      [125, 55],
      [125, 76],
      [365, 13],
      [365, 34],
      [365, 55],
      [365, 76],
    ],
  },
};
function showModel(button) {
  const data = modelPatterns[button.dataset.model];
  $$("[data-model]").forEach((b) =>
    b.setAttribute("aria-pressed", String(b === button)),
  );
  $("#model-pattern").innerHTML =
    `<svg viewBox="0 0 400 90" role="img" aria-label="Conceptual ${button.dataset.model}-oriented search pattern, not a measured trajectory"><path d="${data.quiet}" stroke="#e2e8f0" stroke-dasharray="3 4" fill="none"/><path d="${data.edges}" stroke="${data.color}" stroke-width="2" fill="none"/>${data.points.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="4" fill="#ffffff" stroke="${data.color}" stroke-width="2"/>`).join("")}</svg>`;
  setText("#model-observation", data.description);
  animateContent($("#model-pattern"));
}
$$("[data-model]").forEach((button) =>
  button.addEventListener("click", () => showModel(button)),
);
showModel($('[data-model="depth"]'));
const branches = [
  "Branch A reached approximately 0.6048, but its findings were redundant. The reviewer considered research quality alongside the score.",
  "Branch B was selected for further work. It remained the sole implementation parent.",
  "Branch C scored lower, yet contributed useful ideas. Its findings became reference-only evidence for a fresh Scientist working on B.",
];
$$("[data-branch]").forEach((button) =>
  button.addEventListener("click", () => {
    $$("[data-branch]").forEach((b) =>
      b.setAttribute("aria-pressed", String(b === button)),
    );
    setText("#branch-observation", branches[Number(button.dataset.branch)]);
  }),
);

let copyReset;
$("#copy-command").addEventListener("click", async () => {
  const content = $("#setup-command").textContent;
  try {
    if (!navigator.clipboard?.writeText)
      throw new Error("Clipboard unavailable");
    await navigator.clipboard.writeText(content);
    setText("#copy-command", "Copied ✓");
    setText("#copy-status", "Setup commands copied to clipboard.");
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents($("#setup-command"));
    selection.removeAllRanges();
    selection.addRange(range);
    setText("#copy-command", "Select + copy");
    setText(
      "#copy-status",
      "Clipboard unavailable. Commands selected; press Command+C or Control+C to copy.",
    );
  }
  clearTimeout(copyReset);
  copyReset = window.setTimeout(() => {
    setText("#copy-command", "Copy ⧉");
  }, 3000);
});
