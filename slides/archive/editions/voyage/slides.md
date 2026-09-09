---
theme: default
title: "SciOdyssey: Long-Horizon Autonomous ML Research Agent (Voyage Edition)"
info: |
  A technical presentation of SciOdyssey in the Voyage Editorial Style.
author: Research Agent
colorSchema: light
aspectRatio: 16/9
canvasWidth: 980
transition: fade
drawings:
  persist: false
fonts:
  sans: 'Arial Narrow'
  serif: 'Times New Roman'
  mono: Fira Code
  provider: none
mdc: true
defaults:
  class: voyage-theme
---

<div class="eyebrow">AUTONOMOUS ML RESEARCH / TECHJAM 2026</div>

<img class="cover-art" src="/assets/research-voyage-v2.png" alt="" aria-hidden="true">

<div class="hero cover-title"><span>SciOdyssey:</span><span>Long-Horizon Autonomous</span><span>ML Research Agent</span></div>

<div class="lead">Autonomous ML discovery through <span class="blue">pure evidence.</span></div>

<div class="cover-meta mono"><span>PERSISTENT WORLD</span><span>FRESH SCIENTIST</span><span>EVIDENCE FIRST</span></div>

<div class="narrative-route">Problem → Motivation → System → Experience → Evaluation → Insights</div>

<!--
A lightweight framework for long-running ML research. Its central design gives the research world and the researcher different lifetimes.
[Sources]
- ../README.md — introduction and design principles
-->

---

<div class="visual-kicker orange">01 / PROBLEM · THE RESEARCH TASK</div>

# Can an agent carry a research task to completion?

<div class="lead">Turn a task contract into a tested model, a reproducible implementation, and evidence another researcher can inspect.</div>

<div class="roles narrative-roles">
  <div class="role"><strong>Explore</strong><span>Choose hypotheses, write code, and run experiments.</span><small>Scientific judgment</small></div>
  <div class="role"><strong>Recover</strong><span>Handle failures and revise unsuccessful ideas.</span><small>Long-running work</small></div>
  <div class="role"><strong>Deliver</strong><span>Retain a valid model and the evidence behind it.</span><small>Verifiable progress</small></div>
</div>

<div class="bottom-note note">Our test case: short-video ranking on KuaiRand-Pure, with a fixed evaluator and public-validation boundary.</div>

<!--
Open with the research job. The benchmark makes that job concrete; broader task generality remains unproven.
[Sources]
- ../README.md — introduction and TikTok TechJam 2026 result
- ../competitions/kuairand/task.md — challenge target and optimization objective
-->

---

<!-- class: failure-modes-slide -->

<div class="visual-kicker orange failure-modes-kicker">01 / PROBLEM · FAILURE MODES</div>

# Why Current Research Agents Fall Short

<div class="failure-modes-thesis">Three obstacles to sustained autonomous research.</div>

<div class="failure-modes-grid">
  <div class="failure-mode failure-mode-closed">
    <div class="failure-mode-head"><span class="failure-mode-number mono">01</span><span class="failure-mode-label">CLOSED-WORLD WORKFLOW</span></div>
    <div class="failure-mode-visual failure-graph" aria-label="A fixed workflow hits an error and stops">
      <div class="failure-graph-flow"><span>Observe</span><b>→</b><span>Hypothesize</span><b>→</b><span>Code</span><b>→</b><span>Evaluate</span></div>
      <div class="failure-graph-error"><span class="i-carbon:error-outline"></span><b>ERROR</b></div>
      <div class="failure-graph-dead"><span>↓</span><strong>dead end</strong></div>
    </div>
    <p class="failure-mode-explanation">Predefined tools and recovery paths cannot handle the unexpected.</p>
    <div class="failure-mode-takeaway"><strong>Unexpected problems require developer intervention.</strong></div>
  </div>

  <div class="failure-mode failure-mode-trajectory">
    <div class="failure-mode-head"><span class="failure-mode-number mono">02</span><span class="failure-mode-label">SINGLE TRAJECTORY</span></div>
    <div class="failure-mode-visual failure-basin" aria-label="A long-lived agent remains in one research basin">
      <div class="failure-basin-star">★ <small>better idea</small></div>
      <div class="failure-basin-line"><i></i><i></i><i></i><i class="current"></i><i></i><i></i></div>
      <div class="failure-basin-caption mono">same basin</div>
    </div>
    <p class="failure-mode-explanation">A long-lived context carries yesterday's momentum into today's search.</p>
    <div class="failure-mode-takeaway"><strong>More iterations <span>≠</span> more exploration.</strong></div>
  </div>

  <TreeSearchFlip />
</div>

<div class="failure-modes-bridge">
  <div class="failure-modes-bridge-label mono">DESIGN RESPONSE</div>
  <div class="failure-modes-bridge-copy">Research is open-world, non-linear, and exploratory.</div>
  <div class="failure-modes-bridge-tags"><span>ADAPT</span><span>DIVERSIFY</span><span>LEARN</span></div>
</div>

<!--
This is a synthesis of the design pressures observed in the project, not a universal claim about all research agents.
[Sources]
- ../README.md — Why fresh Scientists?, Architecture, and Parallel breadth
- ../docs/project_story.md — Inspiration and Challenges
- ../docs/FINAL_REPORT.md — sections 1, 3.4–3.5, and 4.2

The Tree Search card opens an embedded reverse page using the project-shaped one-edit AGY replication recorded in `../docs/experiments/one-edit-telemetry.md`: a read-only arm used 340,087 inclusive tokens and a write-only arm used 42,377, an 8.03:1 ratio. The reverse page's TOKEN ABLATION projects eight children from those measured arms: rereading for every child costs 3,059,712 inclusive tokens, while reading once and repeating only the edits costs 679,103, a 4.51:1 ratio. The read arm made ten `view_file` calls over selected KuaiRand project context; the write arm made one line mutation with the exact target supplied in its prompt. The two arms were separate sessions with the same model and effort. Inclusive totals add AGY's separately reported cache-read input. The eight-child comparison is arithmetic based on the measured arms, not another delegated run or a main-agent proxy.
-->

---

<!-- class: open-world-slide -->

<div class="visual-kicker blue">02 / MOTIVATION · OPEN-WORLD RESEARCH</div>

<div class="open-world-claim"><span class="claim-line">Research is an <span class="open-highlight orange-open">open-world</span> task.</span><span class="claim-line claim-line-shift">We need an <span class="open-highlight blue-open">open-world</span> coding agent.</span></div>

<div class="capability-rails">
  <div class="capability-rail blue-rail">
    <div class="rail-heading"><span class="rail-number blue">01</span><span class="capability-title blue">OPEN ACTION SPACE</span></div>
    <div class="icon-row">
      <div class="icon-item"><span class="capability-icon blue i-carbon:terminal"></span><span>Shell</span></div>
      <div class="icon-item"><span class="capability-icon blue i-carbon:folder"></span><span>Files</span></div>
      <div class="icon-item"><span class="capability-icon blue i-carbon:earth"></span><span>Browser</span></div>
      <div class="icon-item"><span class="capability-icon blue i-carbon:branch"></span><span>Git</span></div>
    </div>
    <div class="capability-foot">Use what exists</div>
  </div>
  <div class="capability-rail orange-rail">
    <div class="rail-heading"><span class="rail-number orange">02</span><span class="capability-title orange">SELF-RECOVERY</span></div>
    <div class="icon-row">
      <div class="icon-item"><span class="capability-icon orange i-carbon:error-outline"></span><span>Read errors</span></div>
      <div class="icon-item"><span class="capability-icon orange i-carbon:book"></span><span>Inspect docs</span></div>
      <div class="icon-item"><span class="capability-icon orange i-carbon:code"></span><span>Inspect source</span></div>
      <div class="icon-item"><span class="capability-icon orange i-carbon:package"></span><span>Install packages</span></div>
    </div>
    <div class="capability-foot">Fix what breaks</div>
  </div>
  <div class="capability-rail rose-rail">
    <div class="rail-heading"><span class="rail-number rose">03</span><span class="capability-title rose">RUNTIME EXTENSION</span></div>
    <div class="icon-row">
      <div class="icon-item"><span class="capability-icon rose i-carbon:api"></span><span>MCP</span></div>
      <div class="icon-item"><span class="capability-icon rose i-carbon:tools"></span><span>Skills</span></div>
      <div class="icon-item"><span class="capability-icon rose i-carbon:terminal"></span><span>CLI</span></div>
      <div class="icon-item"><span class="capability-icon rose i-carbon:package"></span><span>Packages</span></div>
    </div>
    <div class="capability-foot">Add what's missing</div>
  </div>
</div>

<div class="open-world-line"><div class="open-world-line-label mono">WORKFLOW EXAMPLE · LANGGRAPH</div><div class="open-world-line-strong"><span class="blue">LangGraph</span> makes a known workflow explicit as nodes + edges.</div><div class="open-world-line-detail">Missing capability? Leave the graph <span class="blue">→</span> inspect <span class="blue">→</span> extend <span class="blue">→</span> retry</div></div>

<!--
The open-world framing and capability taxonomy are adapted from the user's supplied talk-track. LangGraph is used as a concrete workflow example: its documentation distinguishes predetermined workflows from dynamic agents and models workflows with state, nodes, and edges.
[Sources]
- https://docs.langchain.com/oss/python/langgraph/workflows-agents — workflows vs. agents
- https://docs.langchain.com/oss/python/langgraph/graph-api — state, nodes, and edges
-->

---

<div class="visual-kicker green">02 / MOTIVATION · TWO DIFFERENT LIFETIMES</div>

<div class="statement"><p>Preserve the<br><span class="green">research world.</span></p><p style="margin-top: 17px">Reset the researcher.</p></div>

<div class="bottom-note lead">Pass evidence, failures, and code to a fresh Scientist.</div>

<!--
A fresh Scientist inherits externalized experience without continuing its predecessor's unfinished reasoning. Resets happen at trajectory boundaries; productive inquiry can continue within a trajectory.
[Sources]
- ../README.md — central thesis and design principles
-->

---

<div class="visual-kicker blue">03 / SYSTEM · RESPONSIBILITIES</div>

# Two scientific roles. One safe runtime.

<div class="roles">
  <div class="role"><strong class="green">Scientist</strong><span>Hypothesize · code · test · interpret</span><small>One trajectory</small></div>
  <div class="role"><strong>META</strong><span>Audit · preserve · hand off</span><small>Across trajectories</small></div>
  <div class="role"><strong>Runtime</strong><span>Isolation · cancellation · invariants</span><small>System lifetime</small></div>
</div>

<div class="bottom-note note">The Scientist chooses the science. META maintains the world. Runtime enforces mechanics, not scientific judgment.</div>

<!--
Scientific authority is separate from persistence authority. META does not choose the next hypothesis, model, feature, or experiment.
[Sources]
- ../README.md — Architecture
- ../docs/ARCHITECTURE.md
-->

---

<div class="visual-kicker">03 / SYSTEM · PERSISTENCE BOUNDARY</div>

# The persistence boundary is explicit.

<div class="architecture-diagram" aria-label="Research Agent system architecture">
  <div class="architecture-main">
    <div class="arch-column arch-environment">
      <div class="arch-area-title">Environment</div>
      <div class="arch-panel">
        <div class="arch-card"><span class="arch-icon blue i-carbon:document"></span><div><strong>Task contract</strong></div></div>
        <div class="arch-card"><span class="arch-icon blue i-carbon:data-base"></span><div><strong>Curated data + evaluator</strong></div></div>
        <div class="arch-card"><span class="arch-icon blue i-carbon:code"></span><div><strong>Starter baseline</strong></div></div>
        <div class="arch-card"><span class="arch-icon blue i-carbon:locked"></span><div><strong>Budget + permissions</strong></div></div>
      </div>
    </div>
    <div class="arch-arrow blue">→</div>
    <div class="arch-column arch-world">
      <div class="arch-area-title">Research World</div>
      <div class="arch-panel">
        <div class="world-lane"><div class="world-lane-label">A · VERIFIED / EVIDENCE</div><div class="world-items"><div class="world-item"><span class="arch-icon green i-carbon:verified"></span><strong>Verified knowledge</strong></div><div class="world-item"><span class="arch-icon green i-carbon:document"></span><strong>Evidence ledger</strong></div></div></div>
        <div class="world-lane"><div class="world-lane-label">B · CURATED / REVISABLE</div><div class="world-items"><div class="world-item"><span class="arch-icon green i-carbon:document"></span><strong>Research brief</strong></div><div class="world-item"><span class="arch-icon green i-carbon:idea"></span><strong>Working priors</strong></div></div></div>
        <div class="world-lane"><div class="world-lane-label">C · IMPLEMENTATION</div><div class="world-items"><div class="world-item"><span class="arch-icon green i-carbon:data-base"></span><strong>Implementation State</strong></div></div></div>
        <div class="arch-persist">What persists across trajectories</div>
      </div>
    </div>
    <div class="arch-reset"><span class="arch-reset-icon i-carbon:reset"></span><strong>CONTEXT<br>RESET</strong><small>No previous<br>reasoning<br>trajectory</small></div>
    <div class="arch-column arch-scientist">
      <div class="arch-area-title">Fresh Scientist</div>
      <div class="arch-panel">
        <span class="arch-hero-icon purple i-carbon:chemistry"></span>
        <strong class="arch-hero-title">Scientist</strong>
        <small class="arch-hero-subtitle">owns scientific judgment</small>
        <div class="arch-divider"></div>
        <ul class="arch-list purple-list"><li>reads the research world</li><li>forms hypotheses</li><li>runs experiments</li><li>interprets evidence</li><li>writes a report</li></ul>
        <div class="arch-callout purple-callout">inherits experience,<br>not momentum</div>
      </div>
    </div>
    <div class="arch-arrow rose">→</div>
    <div class="arch-column arch-meta">
      <div class="arch-area-title">META Review</div>
      <div class="arch-panel">
        <span class="arch-hero-icon rose i-carbon:security"></span>
        <strong class="arch-hero-title">META</strong>
        <small class="arch-hero-subtitle">owns what survives</small>
        <div class="arch-divider"></div>
        <ul class="arch-list rose-list"><li>audits claim ↔ evidence validity</li><li>scopes conclusions</li><li>maintains shared research memory</li><li>crystallizes retained implementation into State</li></ul>
      </div>
    </div>
  </div>
  <div class="architecture-handoff"><span></span><strong>Selective persistence / trajectory handoff</strong><span></span></div>
  <div class="architecture-handoff-sub">audit → scope → preserve</div>
  <div class="runtime-band">
    <strong class="runtime-title">Runtime — deterministic mechanics</strong>
    <div class="runtime-items">
      <div><span class="runtime-icon orange i-carbon:workspace"></span><span>Workspace<br>isolation</span></div>
      <div><span class="runtime-icon orange i-carbon:play"></span><span>Runner +<br>evaluator</span></div>
      <div><span class="runtime-icon orange i-carbon:document"></span><span>Logging</span></div>
      <div><span class="runtime-icon orange i-carbon:folder"></span><span>Artifact<br>capture</span></div>
      <div><span class="runtime-icon orange i-carbon:data-base"></span><span>State<br>operations</span></div>
    </div>
  </div>
</div>
<!--
[Sources]
- ../docs/system.png — project architecture figure
- ../docs/project_story.md — How we built it
-->

---
class: handoff-loop-slide voyage-theme
clicks: 4
transition: fade
---

<div class="visual-kicker orange">03 / SYSTEM · THE HANDOFF LOOP</div>

# Each cycle leaves a world to build on.

<div class="cycle-map">
  <svg class="cycle-map-lines" viewBox="0 0 1000 300" preserveAspectRatio="none" aria-hidden="true">
    <defs>
      <marker id="cycle-arrow-neutral" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#687986" /></marker>
      <marker id="cycle-arrow-blue" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#00527b" /></marker>
      <marker id="cycle-arrow-purple" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#4a386c" /></marker>
      <marker id="cycle-arrow-rose" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#b83212" /></marker>
    </defs>
    <path d="M126 146 C210 146 235 58 318 58" fill="none" stroke="#cfd6de" stroke-width="2" marker-end="url(#cycle-arrow-neutral)" />
    <path d="M382 58 C480 58 510 146 604 146" fill="none" stroke="#cfd6de" stroke-width="2" marker-end="url(#cycle-arrow-neutral)" />
    <path d="M674 146 C760 146 790 58 872 58" fill="none" stroke="#cfd6de" stroke-width="2" marker-end="url(#cycle-arrow-neutral)" />
    <path d="M904 93 C956 120 930 222 720 236 C470 250 185 234 128 174" fill="none" stroke="#b83212" stroke-opacity=".25" stroke-width="2" marker-end="url(#cycle-arrow-rose)" />
    <path v-click="1" class="cycle-path-progress cycle-path-blue" d="M126 146 C210 146 235 58 318 58" fill="none" stroke="#00527b" stroke-width="3" pathLength="1" marker-end="url(#cycle-arrow-blue)" />
    <path v-click="2" class="cycle-path-progress cycle-path-orange" d="M382 58 C480 58 510 146 604 146" fill="none" stroke="#b83212" stroke-width="3" pathLength="1" marker-end="url(#cycle-arrow-neutral)" />
    <path v-click="3" class="cycle-path-progress cycle-path-purple" d="M674 146 C760 146 790 58 872 58" fill="none" stroke="#4a386c" stroke-width="3" pathLength="1" marker-end="url(#cycle-arrow-neutral)" />
    <path v-click="4" class="cycle-path-progress cycle-path-rose" d="M904 93 C956 120 930 222 720 236 C470 250 185 234 128 174" fill="none" stroke="#b83212" stroke-width="3" pathLength="1" marker-end="url(#cycle-arrow-rose)" />
  </svg>
  <div class="cycle-node cycle-world-node">
    <div class="cycle-node-visual cycle-world-visual" aria-hidden="true"><span class="cycle-world-ring world-ring-outer"></span><span class="cycle-world-ring world-ring-middle"></span><span class="cycle-world-ring world-ring-inner"></span><span class="cycle-world-core"></span><i class="cycle-particle particle-blue"></i><i class="cycle-particle particle-orange"></i><i class="cycle-particle particle-purple"></i></div>
    <strong>WORLD</strong><small>evidence · failures · code</small>
  </div>
  <div v-click="1" class="cycle-node cycle-scientist-node">
    <div class="cycle-node-visual cycle-scientist-visual"><span class="cycle-node-icon purple i-carbon:chemistry"></span></div>
    <strong>SCIENTIST</strong><small>hypothesis · experiment</small>
  </div>
  <div v-click="2" class="cycle-node cycle-evidence-node">
    <div class="cycle-node-visual cycle-evidence-visual"><span class="evidence-line"><i class="blue-dot"></i>metrics</span><span class="evidence-line"><i class="orange-dot"></i>failures</span><span class="evidence-line"><i class="green-dot"></i>code</span></div>
    <strong>EVIDENCE</strong><small>report the result</small>
  </div>
  <div v-click="3" class="cycle-node cycle-meta-node">
    <div class="cycle-node-visual cycle-meta-visual"><span>✓</span></div>
    <strong>META</strong><small>audit · scope · preserve</small>
  </div>
  <div v-click="4" class="cycle-loop-label"><strong>SELECTIVE PERSISTENCE</strong><small>updated world → fresh Scientist</small></div>
</div>

<div v-click="4" class="cycle-explain">
  <div class="cycle-explain-item"><span class="cycle-explain-label green">PERSISTS</span><span>metrics · code · failures · original reports</span></div>
  <div class="cycle-explain-item"><span class="cycle-explain-label purple">RESTARTS</span><span>an independent reasoning trajectory</span></div>
</div>

<!--
The serial loop is the core protocol. State crystallization is optional; a handoff does not require creating a new State every time.
[Sources]
- ../README.md — serial loop
- ../docs/FINAL_REPORT.md — sections 3.1–3.3
-->

---

<div class="visual-kicker green">03 / SYSTEM · RESEARCH MEMORY</div>

# Keep facts distinct from intuition.

<div class="memory">
<pre>research world
├── evidence &amp; provenance
├── verified knowledge
├── current research state
├── fallible priors
└── State + implementation</pre>
<div class="rule"><h2>Built to be re-examined.</h2><p>Facts have evidence.<br>Priors can be overturned.<br>Code can be picked up again.</p><div class="note">Original reports remain available for audit.</div></div>
</div>

<!--
The tree shows information categories, not a literal directory layout. State identifies a retained implementation and its evidence. Compression is lossy, so raw evidence remains available.
[Sources]
- ../README.md — Research memory
- ../docs/FINAL_REPORT.md — sections 3.2–3.3
-->

---
class: parallel-breadth-slide voyage-theme
clicks: 1
transition: slide-left | slide-right
---

<div class="visual-kicker blue">03 / SYSTEM · PARALLEL EXPLORATION</div>

# One starting point. Independent answers.

<div class="parallel-motion" aria-label="One research world branches into three independent scientists and reconverges at a reviewer.">
  <svg viewBox="0 0 1000 340" role="img" aria-hidden="true">
    <path class="parallel-branch-base" d="M100 170 C180 170 190 50 300 50 H760 C820 50 830 170 900 170" />
    <path class="parallel-branch-base" d="M100 170 H900" />
    <path class="parallel-branch-base" d="M100 170 C180 170 190 290 300 290 H760 C820 290 830 170 900 170" />
    <path id="parallel-rail-a" class="parallel-branch-progress parallel-auto-rail parallel-progress-a" d="M100 170 C180 170 190 50 300 50 H760" pathLength="1" />
    <path id="parallel-rail-b" class="parallel-branch-progress parallel-auto-rail parallel-progress-b" d="M100 170 H760" pathLength="1" />
    <path id="parallel-rail-c" class="parallel-branch-progress parallel-auto-rail parallel-progress-c" d="M100 170 C180 170 190 290 300 290 H760" pathLength="1" />
    <circle cx="0" cy="0" r="4" class="parallel-flow-dot parallel-flow-dot-a"><animateMotion dur="2.8s" repeatCount="indefinite" rotate="auto"><mpath href="#parallel-rail-a" /></animateMotion></circle>
    <circle cx="0" cy="0" r="4" class="parallel-flow-dot parallel-flow-dot-b"><animateMotion dur="2.8s" begin=".35s" repeatCount="indefinite" rotate="auto"><mpath href="#parallel-rail-b" /></animateMotion></circle>
    <circle cx="0" cy="0" r="4" class="parallel-flow-dot parallel-flow-dot-c"><animateMotion dur="2.8s" begin=".7s" repeatCount="indefinite" rotate="auto"><mpath href="#parallel-rail-c" /></animateMotion></circle>
    <circle cx="100" cy="170" r="20" class="parallel-world-ring" />
    <circle cx="100" cy="170" r="13" class="parallel-world-dot" />
    <text x="100" y="214" text-anchor="middle" class="parallel-world-label">Research world</text>
    <g class="parallel-card parallel-card-a parallel-auto-card parallel-auto-card-a">
      <rect x="350" y="21" width="330" height="58" rx="29" />
      <circle cx="376" cy="50" r="7" class="parallel-card-dot" />
      <text x="397" y="57" class="parallel-card-name">Scientist A</text>
      <text x="650" y="57" text-anchor="end" class="parallel-card-branch">r1b1</text>
    </g>
    <g class="parallel-card parallel-card-b parallel-auto-card parallel-auto-card-b">
      <rect x="350" y="141" width="330" height="58" rx="29" />
      <circle cx="376" cy="170" r="7" class="parallel-card-dot" />
      <text x="397" y="177" class="parallel-card-name">Scientist B</text>
      <text x="650" y="177" text-anchor="end" class="parallel-card-branch">r1b2</text>
    </g>
    <g class="parallel-card parallel-card-c parallel-auto-card parallel-auto-card-c">
      <rect x="350" y="261" width="330" height="58" rx="29" />
      <circle cx="376" cy="290" r="7" class="parallel-card-dot" />
      <text x="397" y="297" class="parallel-card-name">Scientist C</text>
      <text x="650" y="297" text-anchor="end" class="parallel-card-branch">r1b3</text>
    </g>
    <path v-click="1" class="parallel-merge-progress parallel-merge-a" d="M760 50 C820 50 830 170 900 170" pathLength="1" />
    <path v-click="1" class="parallel-merge-progress parallel-merge-b" d="M760 170 H900" pathLength="1" />
    <path v-click="1" class="parallel-merge-progress parallel-merge-c" d="M760 290 C820 290 830 170 900 170" pathLength="1" />
    <g v-click="1" class="parallel-reviewer">
      <circle cx="900" cy="170" r="40" class="parallel-reviewer-halo" />
      <circle cx="900" cy="170" r="31" class="parallel-reviewer-ring" />
      <circle cx="900" cy="170" r="23" class="parallel-reviewer-core" />
      <path d="M887 170 l8 8 18 -20" class="parallel-reviewer-check" />
      <text x="900" y="231" text-anchor="middle" class="parallel-reviewer-title">Reviewer</text>
      <text x="900" y="248" text-anchor="middle" class="parallel-reviewer-subtitle">MERGE · CHECK</text>
    </g>
  </svg>
</div>

<div class="rule lead parallel-takeaway"><span>Explore in isolated worktrees.</span><span v-click="1">Review after completion.</span></div>

<div class="note" style="margin-top: 20px">Optional synthesis: one implementation parent + reference evidence from other branches.<br>Adoption is explicit via parallel-promote. Code and memory are not merged automatically.</div>

<!--
Parallel breadth is a framework capability, not the claimed cause of the final benchmark gain. Branches do not share a live reasoning context during development.
[Sources]
- ../README.md — Parallel breadth
- ../docs/FINAL_REPORT.md — section 3.4
-->

---

<div class="visual-kicker orange entry-page-kicker">04 / EXPERIENCE · DEFINE THE TASK</div>

# Start with the task and working constraints.

<div class="entry-lede">The operator defines the objective and constraints; the agent chooses and executes the experiments.</div>

<div class="entry-inputs">
  <div class="entry-input entry-input-task">
    <div class="entry-file"><span class="entry-file-mark mono">01</span><span class="entry-file-name mono">task.md</span></div>
    <div class="entry-rule"></div>
    <div class="entry-input-title">What to solve.</div>
    <div class="entry-input-detail mono">Objectives · constraints · evaluation</div>
    <div class="entry-example">
      <div class="entry-example-label mono">EXAMPLE</div>
      <div class="entry-example-text">Rank short videos for each user and interaction context.</div>
      <div class="entry-example-meta mono">KuaiRand-Pure · long_view · GAUC + nDCG@5</div>
    </div>
  </div>
  <div class="entry-input entry-input-personal">
    <div class="entry-file"><span class="entry-file-mark mono">02</span><span class="entry-file-name mono">PERSONAL.md</span></div>
    <div class="entry-rule"></div>
    <div class="entry-input-title">How you want it solved.</div>
    <div class="entry-input-detail mono">Preferences · research style · priorities</div>
    <div class="entry-example">
      <div class="entry-example-label mono">EXAMPLE</div>
      <div class="entry-example-text">Run on macOS / Apple Silicon with uv.</div>
      <div class="entry-example-meta mono">≤ 15 min / experiment · never print credentials</div>
    </div>
  </div>
</div>

<div class="entry-footer">Autonomous by default. Supervisable by design.</div>

<!--
This entry-point framing is grounded in the repository's general-purpose coding-agent interface, task contract, and bounded autonomous cycle.
[Sources]
- ../README.md — What it does, Quick start, and autonomous research loop
- ../docs/project_story.md — What it does and How we built it
-->

---

<div class="visual-kicker orange">04 / EXPERIENCE · THE RESEARCH TRAJECTORY</div>

# Evidence changed the next experiment.

<div class="lead">E001–E013: reject weak ideas, improve representations, then test ensembles.</div>

<div class="roles narrative-roles">
  <div class="role"><strong>E001</strong><span>Screen historical target encodings; reject weak variants.</span><small>Medium screening</small></div>
  <div class="role"><strong>E003</strong><span>Establish a valid rich-FM checkpoint.</span><small>Full · 0.6016310</small></div>
  <div class="role"><strong>E008</strong><span>Retain a five-seed, 38-field FM ensemble.</span><small>Full · 0.6040901</small></div>
  <div class="role"><strong>E013</strong><span>Select the eight-seed, 46-field FM ensemble.</span><small>Full · 0.6059363</small></div>
</div>

<div class="bottom-note note">These are milestones within four autonomous cycles. Medium screens ideas; Full evaluations support retained score claims.</div>

<!--
This is the canonical submission trajectory, distinct from the later RA-only Cycle-2 E008 DIN experiment.
[Sources]
- ../docs/FINAL_REPORT.md — section 4.1, retained experiment trajectory
- ../submission/research-agent-kuairand/research_record/RESEARCH_RECORD.yaml
-->

---

<div class="visual-kicker orange">04 / EXPERIENCE · RECOVERY IN THE RUN</div>

# An evaluation failure became a recoverable step.

<div class="lead">Cycle 1 completed training and evaluation, then failed while writing the evidence file.</div>

<div class="roles narrative-roles">
  <div class="role"><strong>Failure</strong><span>NumPy float32 values broke JSON serialization.</span><small>Evidence writer</small></div>
  <div class="role"><strong>Repair</strong><span>The Scientist converted scalars and reran.</span><small>Agent-authored fix</small></div>
  <div class="role"><strong>Retain</strong><span>Printed measurements and saved evidence survived.</span><small>Auditable recovery</small></div>
</div>

<div class="bottom-note note">Autonomous execution: no human selected this repair or edited the code. The agent recovered its evidence instead of terminating.</div>

<!--
Use the concrete recovery incident to connect the open-world motivation with observed behavior.
[Sources]
- ../docs/FINAL_REPORT.md — section 4.2, autonomous recovery
- ../submission/research-agent-kuairand/research_record/reports/cycle-1.md
-->

---
class: checkpoint-slide voyage-theme
clicks: 1
transition: fade
---

<div class="visual-kicker purple">04 / EXPERIENCE · INSPECT THE RESULT</div>

# A retained state keeps the evidence inspectable.

<div class="checkpoint-motion">
  <div class="checkpoint-window">
    <div class="checkpoint-windowbar"><span>Research Dashboard</span><span>RECORDED VALIDATION</span></div>
    <div class="checkpoint-viewport">
      <div
        v-motion
        :initial="{ scale: 0.72, x: 0, y: 0 }"
        :enter="{ scale: 0.72, x: 0, y: 0 }"
        :click-1="{ scale: 0.82, x: 0, y: -10 }"
        class="checkpoint-zoom"
      >
        <img src="/assets/dashboard-result.png" alt="Research dashboard showing the retained validation result, metrics, and evidence path">
      </div>
      <div v-click="1" class="checkpoint-focus-box" aria-hidden="true"></div>
      <div v-click="1" class="checkpoint-focus-label">S004 · RETAINED STATE</div>
    </div>
  </div>
  <div class="checkpoint-caption"><span v-click="1">Inspect the retained state and the evidence behind it.</span></div>
</div>

<div class="visual-caption">Retained validation checkpoint · evidence path · reproducible implementation.</div>

<!--
[Sources]
- ../docs/dashboard/2.png — retained validation result dashboard
- ../docs/project_story.md — Accomplishments that we're proud of
-->

---

<div class="visual-kicker orange">05 / EVALUATION · PUBLIC-VALIDATION RESULT</div>

# Autonomous research. Measured gains.

<div class="score">
  <div><div class="mono muted" style="font-size: 13px">PRIMARY / RESEARCH AGENT</div><div class="big-number">0.6059363</div><div class="delta"><span class="green">+0.0043363</span> <span class="muted">absolute improvement</span></div></div>
  <div><table><thead><tr><th>METRIC</th><th>Official FM</th><th>Ours</th></tr></thead><tbody><tr><td>GAUC</td><td>0.6674000</td><td class="green">0.6728421</td></tr><tr><td>nDCG@5</td><td>0.5357000</td><td class="green">0.5390304</td></tr><tr><td>Primary</td><td>0.6016000</td><td class="green">0.6059363</td></tr></tbody></table></div>
</div>

<div class="bottom-note note">Primary = mean(GAUC, nDCG@5). Public validation only; hidden-test scoring is organizer-controlled.<br>Final recipe: 46 categorical features × 8-seed FM ensemble · NumPy / CPU</div>

<!--
These are validation scores, not hidden-test results or a competition placement. The official reference is a five-field FM. The final model uses rank k=16.
[Sources]
- ../README.md — TikTok TechJam 2026 result
- ../docs/FINAL_REPORT.md — Submission Snapshot and section 2
-->

---

<div class="visual-kicker blue">05 / EVALUATION · AUTONOMY AND AUDITABILITY</div>

# An audit trail from experiment to output.

<div class="stats">
  <div class="rule"><strong>4</strong><p>Autonomous cycles</p><small>Within a 50-iteration cap</small></div>
  <div class="rule"><strong>13</strong><p>Named experiments</p><small>E001–E013 · 7 Full evaluations</small></div>
  <div class="rule"><strong>0</strong><p>Manual scientific interventions</p><small>After launch · 0 GPU-hours</small></div>
</div>

<div class="bottom-note note">170,588 prediction rows passed the unchanged Starter Kit alignment checker.<br>LLM tokens: 48.24M including cache reads; 4.02M excluding cache reads.</div>

<!--
Zero manual scientific interventions applies after launch in the retained run, not to building the framework or setting up the benchmark. Total tokens: 48,240,128; excluding cache reads: 4,020,880. Zero GPU-hours does not mean zero LLM cost.
[Sources]
- ../docs/FINAL_REPORT.md — Submission Snapshot
- ../submission/research-agent-kuairand/final/submit-check.txt
-->

---

<div class="visual-kicker orange resources-page-kicker">05 / EVALUATION · RESOURCE ACCOUNTING</div>

# Resource use is part of the evidence.

<div class="resources-thesis">Project-level subscription estimate, with run-level telemetry reported separately.</div>

<div class="resource-hero">
  <div class="resource-hero-number">~$10</div>
  <div class="resource-hero-subtitle">from first line of code to final result</div>
  <div class="resource-hero-detail mono">coding · debugging · agent runs · all experiments</div>
</div>

<div class="resource-support">
  <div class="resource-support-item">
    <div class="resource-support-label blue">MODEL</div>
    <div class="resource-support-title">One GPT Plus + One Gemini Pro for 7 days</div>
    <div class="resource-support-detail">Two consumer subscriptions covered the entire research loop.</div>
  </div>
  <div class="resource-support-item">
    <div class="resource-support-label purple">COMPUTE</div>
    <div class="resource-support-title">1 × MacBook M2</div>
    <div class="resource-support-detail">All development and experiments ran on a single consumer laptop.</div>
  </div>
</div>

<div class="resource-conclusion">The recorded runs used CPU training; LLM usage remains a separate cost.</div>

<div class="resource-footnote">~$10 is the estimated subscription-equivalent usage across the entire project, including coding, debugging and all experiments — not cost per experiment.</div>

<!--
This page frames resource usage as supporting evidence, not as a claim that cost alone explains performance. The dollar estimate is the user's requested subscription-equivalent accounting; telemetry-backed token and compute facts are documented below.
[Sources]
- ../docs/project_story.md — sections 3 and 4, measured token and compute telemetry
- ../README.md — autonomous runs and zero GPU-hours
- User-provided resource accounting for the estimated ~$10 project usage
-->

---

<div class="visual-kicker orange">05 / EVALUATION · DIRECT-AGENT COMPARISON</div>

# Compare scores alongside their evidence.

<div class="token-chart-wrap">
<svg class="token-chart" viewBox="0 0 1000 620" role="img" aria-labelledby="token-chart-title token-chart-desc">
<title id="token-chart-title">Public-validation Primary score versus measured total LLM tokens</title>
<desc id="token-chart-desc">The retained Research Agent result reaches a Primary score of 0.605936 at 48.240 million total LLM tokens, above the official reference score of 0.601600.</desc>
<rect class="chart-paper" x="0" y="0" width="1000" height="620" rx="18" />
<text class="chart-inline-title" x="92" y="34">Score versus measured LLM-token investment</text>
<text class="chart-inline-subtitle" x="92" y="58">Public validation; input + output including cache-read; whole recorded agent system</text>
<rect class="chart-plot" x="92" y="82" width="840" height="420" rx="4" />
<g class="chart-grid">
<line x1="92" y1="464" x2="932" y2="464" />
<line x1="92" y1="388" x2="932" y2="388" />
<line x1="92" y1="311" x2="932" y2="311" />
<line x1="92" y1="235" x2="932" y2="235" />
<line x1="92" y1="158" x2="932" y2="158" />
<line x1="92" y1="82" x2="932" y2="82" />
<line x1="92" y1="82" x2="92" y2="502" />
<line x1="245" y1="82" x2="245" y2="502" />
<line x1="397" y1="82" x2="397" y2="502" />
<line x1="550" y1="82" x2="550" y2="502" />
<line x1="703" y1="82" x2="703" y2="502" />
<line x1="856" y1="82" x2="856" y2="502" />
<line x1="932" y1="82" x2="932" y2="502" />
</g>
<g class="chart-y-labels">
<text x="78" y="469">0.602</text>
<text x="78" y="393">0.603</text>
<text x="78" y="316">0.604</text>
<text x="78" y="240">0.605</text>
<text x="78" y="163">0.606</text>
</g>
<line class="chart-reference" x1="92" y1="494" x2="932" y2="494" />
<text class="chart-reference-label" x="118" y="488">Official reference 0.601600</text>
<g class="chart-leaders">
<line x1="223" y1="267" x2="151" y2="249" />
<line x1="521" y1="265" x2="510" y2="216" />
<line x1="697" y1="253" x2="790" y2="181" />
<line x1="827" y1="219" x2="900" y2="259" />
<line x1="829" y1="163" x2="850" y2="124" />
</g>
<g class="chart-series">
<circle class="chart-point chart-point-blue" cx="223" cy="267" r="8" />
<circle class="chart-point chart-point-blue" cx="521" cy="265" r="8" />
<polygon class="chart-point chart-point-orange" points="697,243 707,253 697,263 687,253" />
<line class="chart-range" x1="780" y1="219" x2="874" y2="219" />
<line class="chart-range" x1="780" y1="210" x2="780" y2="228" />
<line class="chart-range" x1="874" y1="210" x2="874" y2="228" />
<polygon class="chart-point chart-point-purple" points="827,208 839,230 815,230" />
<circle class="chart-point chart-point-green" cx="829" cy="163" r="9" />
</g>
<g class="chart-point-labels">
<text class="chart-label-main" x="151" y="242">AGY</text>
<text class="chart-label-sub" x="151" y="258">gemini-3.7-flash · direct</text>
<text class="chart-label-meta" x="151" y="274">8.565M · 0.6045803 · artifact-backed</text>
<text class="chart-label-main chart-label-right" x="510" y="196">gpt-5.6-luna · direct</text>
<text class="chart-label-sub chart-label-right" x="510" y="212">28.070M · ≈0.6046 · provisional</text>
<text class="chart-label-main chart-label-right" x="790" y="156">heterogeneous run</text>
<text class="chart-label-sub chart-label-right" x="790" y="172">gemini-3.7-flash · 39.607M · ≈0.6047</text>
<text class="chart-label-main chart-label-right" x="925" y="274">RA-only · Cycle 2</text>
<text class="chart-label-sub chart-label-right" x="925" y="290">gemini-3.7-flash-only · 45.044–51.174M · 0.6052 · E008</text>
<text class="chart-label-main chart-label-right chart-label-retained" x="925" y="108">Research Agent submission</text>
<text class="chart-label-sub chart-label-right chart-label-retained" x="925" y="124">48.240M · 0.605936 · verified</text>
</g>
<g class="chart-axis-labels">
<text x="92" y="522">0</text>
<text x="238" y="522">10</text>
<text x="390" y="522">20</text>
<text x="543" y="522">30</text>
<text x="696" y="522">40</text>
<text x="849" y="522">50</text>
<text x="918" y="522">55M</text>
<text class="chart-axis-title" x="512" y="548">Total LLM tokens (millions)</text>
<text class="chart-axis-title chart-axis-y" x="22" y="296" transform="rotate(-90 22 296)">Primary score</text>
</g>
<g class="chart-legend">
<circle class="chart-point chart-point-blue" cx="110" cy="584" r="6" />
<text x="124" y="589">direct model run</text>
<polygon class="chart-point chart-point-orange" points="267,578 274,584 267,590 260,584" />
<text x="282" y="589">heterogeneous run</text>
<polygon class="chart-point chart-point-purple" points="431,577 439,591 423,591" />
<text x="447" y="589">RA-only sweep</text>
<circle class="chart-point chart-point-green" cx="584" cy="584" r="6" />
<text x="598" y="589">retained verified result</text>
</g>
</svg>
</div>

<div class="visual-caption">Comparative exploration across distinct agent setups under KuaiRand-Pure benchmark constraints.</div>

<!--
[Sources]
- ../docs/figures/token-score-comparison.svg — original evidence figure and exact plotted values
- ../docs/FINAL_REPORT.md — section 5.3, public validation and token accounting
- ../docs/project_story.md — Accomplishments that we're proud of
-->

---

<!-- class: insight-slide -->

<div class="visual-kicker purple">06 / INSIGHTS · WHAT THE RUN TAUGHT US</div>

# The run taught us more than the final score.

<div class="insight-lede">Two ways to widen the search without losing evidence.</div>

<div class="insight-grid">
  <div class="insight-item">
    <span class="insight-index blue">01</span>
    <div><strong>Different agents search differently.</strong><p>Recorded runs took different routes: local refinement, mechanism pivots, and broader search. Heterogeneous Scientists turn those search styles into a broader exploration prior.</p></div>
  </div>
  <div class="insight-item">
    <span class="insight-index orange">02</span>
    <div><strong>Parallel search + review can produce a stronger candidate.</strong><p>Independent Scientists explore without a shared live context. Review selects a branch, then a fresh Scientist synthesizes the evidence. One observed run moved from ≈0.6015 to 0.6055536 Primary. The run shows a promising pattern, but it does not isolate parallelism as the cause.</p></div>
  </div>
</div>

<div class="insight-bottom">
  <div class="insight-boundary"><div class="insight-boundary-label mono">OBSERVED, NOT PROVEN</div><div class="insight-boundary-copy">Parallel/Synthesis reached public-validation Primary <strong>0.6055536</strong>; the canonical E001–E013 frontier remains <strong>0.6059363</strong>.</div></div>
  <div class="insight-stats"><div class="insight-stat"><strong class="blue">4</strong><small>cycles</small></div><div class="insight-stat"><strong class="orange">0</strong><small>post-launch interventions</small></div><div class="insight-stat"><strong class="rose">0</strong><small>GPU-hours</small></div></div>
</div>

<!--
This section distills two process observations from the final report: heterogeneous agents bring different search styles, and independent Parallel search followed by review can produce a stronger candidate. The Parallel/Synthesis score is an observed public-validation result, not part of the canonical E001–E013 frontier. Its improvement followed concrete modeling changes, so the run does not isolate parallelism as the cause.
[Sources]
- ../docs/FINAL_REPORT.md — sections 3.4–3.5, 4.2, 5.5, and 7.1–7.2
- ../docs/trajectories/parallel-synthesis.md — independent search, review, synthesis, and observed Primary 0.6055536270
-->

---

<div class="visual-kicker purple">06 / INSIGHTS · LIMITS AND NEXT EXPERIMENTS</div>

# Reproducible evidence. Open questions.

<div class="roles">
  <div class="role"><strong class="green">01</strong><span>One task does not establish generality.</span><small>External validity</small></div>
  <div class="role"><strong class="green">02</strong><span>META, State, and reset are not isolated.</span><small>Causal attribution</small></div>
  <div class="role"><strong class="green">03</strong><span>Summaries can lose context and anchor.</span><small>Memory quality</small></div>
</div>

<div class="bottom-note note">Next questions: broader tasks, targeted ablations, and less repeated execution.</div>

<!--
Next questions are proposed directions based on documented limitations, not completed features or a committed roadmap. KuaiRand-1K / 27K bonus benchmarks were not attempted.
[Sources]
- ../README.md — Limitations
-->

---

<!-- class: agentic-swe-fieldnote-slide -->

<div class="visual-kicker orange">06 / INSIGHTS · ENGINEERING PRACTICE</div>

<div class="fieldnote-title-row"><h1>A clean repo. A continuous agent.</h1><span class="fieldnote-stamp mono">FIELD NOTE / 01</span></div>

<div class="fieldnote-lede">Engineering practices to apply next: isolate parallel changes and make unattended work reviewable.</div>

<div class="fieldnote-grid">
  <div class="fieldnote-card fieldnote-branches">
    <div class="fieldnote-card-head"><span class="fieldnote-number mono">01</span><span class="fieldnote-kicker mono">MANY AGENTS</span><span class="fieldnote-card-icon orange i-carbon:branch"></span></div>
    <h2>Give every agent a branch.</h2>
    <div class="fieldnote-branch-flow">
      <div class="fieldnote-branch-source"><strong class="mono">main</strong><small>clean trunk</small></div>
      <div class="fieldnote-branch-list"><span><i></i>agent A / branch</span><span><i></i>agent B / branch</span><span><i></i>agent C / branch</span></div>
      <div class="fieldnote-branch-merge"><strong>review</strong><small>→ merge</small></div>
    </div>
    <p>Let agents work independently. Conflicts stay local, and the main branch stays clean.</p>
  </div>
  <div class="fieldnote-card fieldnote-remote">
    <div class="fieldnote-card-head"><span class="fieldnote-number mono">02</span><span class="fieldnote-kicker mono">NO QUOTA / NO LAPTOP</span><span class="fieldnote-card-icon blue i-carbon:cloud-upload"></span></div>
    <h2>Leave the next move in GitHub.</h2>
    <div class="fieldnote-remote-flow">
      <div class="fieldnote-remote-step"><span class="mono">01</span><strong>Issue / prompt</strong><small>inject the task</small></div><span class="fieldnote-flow-arrow">→</span>
      <div class="fieldnote-remote-step"><span class="mono">02</span><strong>GitHub Action</strong><small>run the agent</small></div><span class="fieldnote-flow-arrow">→</span>
      <div class="fieldnote-remote-step"><span class="mono">03</span><strong>Commit</strong><small>review the change</small></div>
    </div>
    <p>Connect the agent to GitHub Actions. It can code and commit while you are offline; review before merging.</p>
  </div>
</div>

<div class="fieldnote-footer"><span class="fieldnote-footer-label mono">PRACTICAL WORKFLOW</span><span>Recommended engineering pattern for unattended overnight exploration.</span></div>

<!--
This engineering field note distills the user's Agentic SWE workflow suggestion into two operational patterns: branch isolation for parallel agents, and GitHub-based continuation for unattended work. It is guidance, not a feature claim of the research system.
-->

---

<div class="visual-kicker blue">06 / INSIGHTS · KEEP EXPERIENCE, REOPEN SEARCH</div>

<div class="closing">Keep the experience.<br><span class="green">Reopen the search.</span></div>

<div class="terminal"><pre><span class="muted"># From the configured repo, run one autonomous cycle</span>
<span class="green">$</span> ./scripts/research-agent step --cli codex \
    --target /absolute/path/to/project --allow-edits</pre></div>

<div class="note" style="margin-top: 21px"><a href="https://github.com/zc6600/research-agent-kuairand" target="_blank">github.com/zc6600/research-agent-kuairand ↗</a><br>Code · Technical report · Experiment ledger · Checked output</div>

<!--
Prerequisites are in the repository Quick start: Git, uv, the Python environment, and an installed, authenticated agent CLI. Replace target with a real research project path. The command is display text and does not execute.
[Sources]
- ../README.md — Quick start
-->

---

<div class="visual-kicker orange team-page-kicker">APPENDIX / THE TEAM</div>

# Five people. One autonomous research loop.

<div class="team-intro"><span class="team-intro-line"></span><span class="team-intro-text mono">OVERLAPPING RESPONSIBILITIES / SHARED WORLD</span><span class="team-intro-line"></span></div>

<div class="team-stage">
  <div class="team-thread" aria-hidden="true"></div>
  <div class="team-row">
    <div class="team-member team-member-1">
      <div class="team-avatar" style="--team-accent: var(--orange)" aria-label="Chen Zhu"><span>CZ</span></div>
      <div class="team-name">Chen Zhu</div>
      <div class="team-role mono">TEAM LEAD / SYSTEM</div>
      <div class="team-contribution">Direction · architecture · integration</div>
    </div>
    <div class="team-member team-member-2">
      <div class="team-avatar" style="--team-accent: var(--blue)" aria-label="Zhou Ziyu"><span>ZZ</span></div>
      <div class="team-name">Zhou Ziyu</div>
      <div class="team-role mono">MODELING / EXPERIMENTS</div>
      <div class="team-contribution">Features · ensembles · evidence review</div>
    </div>
    <div class="team-member team-member-3">
      <div class="team-avatar" style="--team-accent: #16803b" aria-label="Shilin Xu"><span>SX</span></div>
      <div class="team-name">Shilin Xu</div>
      <div class="team-role mono">DATA / METRICS</div>
      <div class="team-contribution">Data workflow · contracts · alignment</div>
    </div>
    <div class="team-member team-member-4">
      <div class="team-avatar" style="--team-accent: var(--purple)" aria-label="GE GAO"><span>GG</span></div>
      <div class="team-name">GE GAO</div>
      <div class="team-role mono">RUNTIME / RELIABILITY</div>
      <div class="team-contribution">Execution · testing · integration support</div>
    </div>
    <div class="team-member team-member-5">
      <div class="team-avatar" style="--team-accent: var(--rose)" aria-label="Jiran Li"><span>JL</span></div>
      <div class="team-name">Jiran Li</div>
      <div class="team-role mono">EVIDENCE / REPRODUCIBILITY</div>
      <div class="team-contribution">Telemetry · documentation · packaging</div>
    </div>
  </div>
</div>

<div class="team-footer"><span class="team-footer-label mono">SCIODYSSEY TEAM</span><span>Every handoff kept the research world moving.</span></div>

<!--
Team names and responsibilities are drawn from the repository's documented team contributions.
[Sources]
- ../README.md — Team contributions
- ../docs/FINAL_REPORT.md — section 6.4, Team contributions
-->

---

<!-- class: recovery-compare-slide -->

<div class="visual-kicker orange">APPENDIX / CAPABILITY RECOVERY</div>

# The difference is not orchestration. It is recoverability.

<div class="compare-grid">
  <div class="compare-side failure-side">
    <div class="compare-kicker rose">LangGraph-style orchestration</div>
    <div class="compare-subtitle">predefined graph</div>
    <div class="static-graph">
      <div class="graph-top"><span class="graph-icon rose i-carbon:flow-data"></span><span>fixed tool set</span></div>
      <div class="graph-arrow">↓</div>
      <div class="graph-tools">
        <div class="graph-node"><span class="graph-node-icon rose i-carbon:tools"></span><span>Tool A</span></div>
        <div class="graph-node"><span class="graph-node-icon rose i-carbon:tools"></span><span>Tool B</span></div>
        <div class="graph-node"><span class="graph-node-icon rose i-carbon:tools"></span><span>Tool C</span></div>
      </div>
    </div>
    <div class="compare-failure">
      <div class="failure-step"><span class="failure-icon rose i-carbon:error-outline"></span><span>API fails</span></div>
      <div class="failure-arrow">↓</div>
      <div class="failure-step muted"><span class="failure-icon i-carbon:stop-outline"></span><span>no recovery tool</span></div>
      <div class="failure-arrow">↓</div>
      <div class="dead-end"><span class="failure-icon rose i-carbon:error-outline"></span>DEAD END</div>
    </div>
    <div class="compare-note">Capabilities are bounded by what developers anticipated.</div>
  </div>
  <div class="compare-side recovery-side">
    <div class="compare-kicker blue">Coding-agent harness</div>
    <div class="compare-subtitle">open action space</div>
    <div class="harness-diagram">
      <div class="harness-computer"><span class="harness-icon blue i-carbon:laptop"></span><span>Computer</span></div>
      <div class="harness-arrow">↓</div>
      <div class="harness-paths">
        <div class="harness-path"><div class="harness-node"><span class="harness-icon blue i-carbon:terminal"></span><span>shell</span></div><span class="harness-arrow">↓</span><div class="harness-node"><span class="harness-icon blue i-carbon:branch"></span><span>git</span></div></div>
        <div class="harness-path"><div class="harness-node"><span class="harness-icon blue i-carbon:folder"></span><span>files</span></div><span class="harness-arrow">↓</span><div class="harness-node"><span class="harness-icon blue i-carbon:document"></span><span>docs</span></div></div>
        <div class="harness-path"><div class="harness-node"><span class="harness-icon blue i-carbon:earth"></span><span>browser</span></div><span class="harness-arrow">↓</span><div class="harness-node"><span class="harness-icon blue i-carbon:package"></span><span>packages</span></div></div>
      </div>
      <div class="agent-band">
        <div class="agent-branch agent-branch-skills"><span class="harness-icon blue i-carbon:tools"></span><span class="agent-branch-copy"><strong>skills</strong></span></div>
        <span class="agent-connector" aria-hidden="true">→</span>
        <div class="agent-core"><span class="agent-core-mark" aria-hidden="true"></span><span class="agent-core-copy"><strong>agent</strong></span></div>
        <span class="agent-connector" aria-hidden="true">←</span>
        <div class="agent-branch agent-branch-mcp"><span class="harness-icon blue i-carbon:api"></span><span class="agent-branch-copy"><strong>MCP</strong></span></div>
      </div>
      <div class="harness-arrow">↓</div>
      <div class="cli-api">CLI / API</div>
    </div>
    <div class="recovery-flow compact"><div class="recovery-sequence"><span>fail</span><b>→</b><span>inspect</span><b>→</b><span>learn</span><b>→</b><span>modify environment</span><b>→</b><span>retry</span></div><div class="recovery-caption">The agent can acquire the missing capability at runtime.</div></div>
  </div>
</div>

<!--
The comparison describes two capability models: a bounded predefined graph and a coding-agent harness that can inspect, modify its environment, and retry.
-->
