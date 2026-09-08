---
theme: default
title: "SciOdyssey: Long-Horizon Autonomous ML Research Agent"
info: |
  A technical introduction to Research Agent. Sources: README.md, docs/FINAL_REPORT.md, and docs/ARCHITECTURE.md.
author: Research Agent
colorSchema: light
aspectRatio: 16/9
canvasWidth: 980
transition: fade
drawings:
  persist: false
fonts:
  sans: Nunito
  mono: Fira Code
  provider: none
mdc: true
---

<div class="eyebrow">AUTONOMOUS ML RESEARCH / TECHJAM 2026</div>

<img class="cover-art" src="/assets/research-world-cover.png" alt="" aria-hidden="true">

<div class="hero cover-title"><span>SciOdyssey:</span><span>Long-Horizon Autonomous</span><span>ML Research Agent</span></div>

<div class="lead">Autonomous by default. <span class="blue">Supervisable by design.</span></div>

<div class="cover-meta mono"><span>ROBUST</span><span>SUPERVISABLE</span><span>BROAD SEARCH</span></div>

<!--
A lightweight framework for long-running ML research. Its central design gives the research world and the researcher different lifetimes.
[Sources]
- ../README.md — introduction and design principles
-->

---

<!-- class: toc-slide -->

<div class="visual-kicker orange">ROADMAP / TALK ORDER</div>

<div class="toc-heading">
  <div>
    <h1>The run, in four moves</h1>
    <div class="toc-intro">A single route from the problem to the proof.</div>
  </div>
</div>

<div class="toc-track" aria-label="Talk order">
  <div class="toc-track-line" aria-hidden="true"></div>
  <div class="toc-step toc-step-blue">
    <div class="toc-step-marker"><span class="toc-step-number mono">01</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">PROBLEM</div>
    <strong>Why current agents fail</strong>
    <span>Set the task and its failure modes.</span>
  </div>
  <div class="toc-step toc-step-orange">
    <div class="toc-step-marker"><span class="toc-step-number mono">02</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">SYSTEM</div>
    <strong>A system for sustained research</strong>
    <span>Keep experience while resetting the scientist.</span>
  </div>
  <div class="toc-step toc-step-purple">
    <div class="toc-step-marker"><span class="toc-step-number mono">03</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">USER EXPERIENCE</div>
    <strong>Run the research journey</strong>
    <span>Move from task contract to retained state.</span>
  </div>
  <div class="toc-step toc-step-green">
    <div class="toc-step-marker"><span class="toc-step-number mono">04</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">EVALUATION</div>
    <strong>From claim to evidence</strong>
    <span>Measure what survives the run.</span>
  </div>
</div>

<!--
The directory follows the live talk order. Experience is narrated/played back; the remaining sections advance with the normal next-slide action.
-->

---

<!-- class: research-task-slide -->

<div class="visual-kicker orange">01 / PROBLEM · THE RESEARCH TASK</div>

# Automating ML experimentation

<div class="research-task-lead">Given a dataset and a scoring metric, an agent must build a model and improve it through repeated experiments.</div>

<div class="research-loop" aria-label="The ML engineer iteration loop">
  <div class="research-loop-stages">
    <div class="research-loop-stage stage-blue">
      <span class="research-loop-number mono">01</span>
      <strong>Read the problem</strong>
      <span>What should the model predict?</span>
    </div>
    <div class="research-loop-stage stage-orange">
      <span class="research-loop-number mono">02</span>
      <strong>Inspect data</strong>
      <span>What patterns does the data contain?</span>
    </div>
    <div class="research-loop-stage stage-purple">
      <span class="research-loop-number mono">03</span>
      <strong>Engineer features</strong>
      <span>Turn raw data into useful model inputs</span>
    </div>
    <div class="research-loop-stage stage-rose">
      <span class="research-loop-number mono">04</span>
      <strong>Train + tune</strong>
      <span>Fit a model and adjust its settings</span>
    </div>
    <div class="research-loop-stage stage-green">
      <span class="research-loop-number mono">05</span>
      <strong>Evaluate</strong>
      <span>Check performance on validation data</span>
    </div>
  </div>
  <div class="research-loop-reflect">
    <span class="research-loop-reflect-label mono">REFLECT + REVISE</span>
    <span>The agent uses the results to choose what to change, revises the code, and runs the next experiment.</span>
  </div>
</div>

<div class="research-task-bottom">
  <div class="research-task-why">
    <span class="research-task-label mono">THE AGENT'S JOB</span>
    <p><strong>Write the code and run the full loop autonomously.</strong> This includes building the pipeline and deciding which experiments to try next.</p>
  </div>
  <div class="research-task-brief">
    <span class="research-task-label mono">THE CHALLENGE GOAL</span>
    <p><strong>Reproduce, then improve on the organizer's baseline.</strong> Develop with training data and public validation. The organizer scores the final submission on a hidden test set.</p>
  </div>
</div>

<!--
The five stages describe the ML engineer's familiar iteration loop. Code-generating LLMs make automation plausible because feature engineering and training largely happen in code. The challenge requires the agent to reproduce the organizer's reported baseline validation score, then demonstrate sustained improvement. Individual experiments may regress. The agent selects a final submission for one hidden-test evaluation and never accesses the hidden test during development. Our test case is short-video recommendation on KuaiRand-Pure. Prior systems and detailed recommender metrics belong in later context or evidence slides rather than this task introduction.
[Sources]
- User-supplied challenge brief — sections 2.1 Background and 2.2 Problem Statement
- ../README.md — introduction and TikTok TechJam 2026 result
- ../competitions/kuairand/task.md — challenge target and optimization objective
-->

---

<!-- class: failure-modes-slide -->

<div class="visual-kicker orange failure-modes-kicker">01 / PROBLEM · FAILURE MODES</div>

# Why current agents fail

<ProblemInsights />

<!--
This is a synthesis of the design pressures observed in the project, not a universal claim about all research agents.
[Sources]
- ../README.md — Why fresh Scientists?, Architecture, and Parallel breadth
- ../docs/project_story.md — Inspiration and Challenges
- ../docs/FINAL_REPORT.md — sections 1, 3.4–3.5, and 4.2
- ../competition_archive/kuairand-pure/reports/direct-codex-goal-baseline.md — local refinement trajectory
- ../competition_archive/kuairand-pure/reports/direct-gemini-3.7-flash-goal-baseline.md — mechanism-pivot trajectory

The Tree Search card opens an embedded reverse page using the project-shaped one-edit AGY replication recorded in `../docs/experiments/one-edit-telemetry.md`: a read-only arm used 340,087 inclusive tokens and a write-only arm used 42,377, an 8.03:1 ratio. The reverse page's TOKEN ABLATION projects eight children from those measured arms: rereading for every child costs 3,059,712 inclusive tokens, while reading once and repeating only the edits costs 679,103, a 4.51:1 ratio. The read arm made ten `view_file` calls over selected KuaiRand project context; the write arm made one line mutation with the exact target supplied in its prompt. The two arms were separate sessions with the same model and effort. Inclusive totals add AGY's separately reported cache-read input. The eight-child comparison is arithmetic based on the measured arms, not another delegated run or a main-agent proxy.
Card 02 is a qualitative, descriptive comparison of two recorded single-agent trajectories. Its back face shows how a previous pattern can shape the next experiment.
Card 02 reverse is multi-page: page 1 covers search momentum; page 2 covers Gemini's audited scientific-validity failures; page 3 follows 02 / SYSTEM · THE HANDOFF LOOP with four click-reveal steps. The findings are branch-level and do not invalidate every final Gemini result.
- ../competition_archive/kuairand-pure/reports/baseline-protocol-audit.md — sections 5 and 6, Gemini target-statistics leakage and cross-user BPR
- ../docs/FINAL_REPORT.md — sections 3.1–3.3, serial loop and selective persistence
-->

---

<div class="visual-kicker">02 / SYSTEM · DESIGN</div>

# A system for sustained research

<InsightArchitecture>
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
    <div class="arch-reset"><span class="arch-reset-icon i-carbon:reset"></span><strong>CONTEXT<br>RESET</strong></div>
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
  <div class="runtime-band">
    <strong class="runtime-title">Coding-agent harness + runtime</strong>
    <div class="runtime-items">
      <div><span class="runtime-icon orange i-carbon:workspace"></span><span>Workspace<br>isolation</span></div>
      <div><span class="runtime-icon orange i-carbon:play"></span><span>Runner +<br>evaluator</span></div>
      <div><span class="runtime-icon orange i-carbon:document"></span><span>Logging</span></div>
      <div><span class="runtime-icon orange i-carbon:folder"></span><span>Artifact<br>capture</span></div>
      <div><span class="runtime-icon orange i-carbon:data-base"></span><span>State<br>operations</span></div>
    </div>
  </div>
</div>
</InsightArchitecture>
<!--
[Sources]
- ../docs/system.png — project architecture figure
- ../docs/project_story.md — How we built it
- ../docs/ARCHITECTURE.md — scientific authority, persistence authority, and runtime mechanics

The preceding cards motivate this design: adaptive tools inform the coding-agent harness,
fresh reasoning informs Scientist resets, claim auditing informs META, and reusable context
informs the persistent Research World. Runtime still owns deterministic mechanics.
The transition is a design explanation, not experimental proof of causal attribution.
-->

---

<ExperienceJourney />

<!--
03 / UX opens with “SciOdyssey — A research layer over your agent harness.”
After expansion, a compact “Works with” row identifies Codex, Claude Code,
OpenCode, Antigravity, and Trae as supported agents; the outer card has no icons.
Six acts autoplay: edit task.md and PERSONAL.md, step, run, parallel, dashboard, skill.
Playback is an illustrative walkthrough rendered with native Vue/HTML/SVG elements.
Only command entry has a Terminal frame; execution uses animated research diagrams.
Theme wording: ../terminal/deck.mjs and slides-voyage.md.
Each act first explains its purpose with a Keynote-style headline, then demonstrates
the operation: Start your journey / One step / Let it run / Now, explore wider /
See what stays / Already in your workflow.
The approximately 127-second sequence opens embedded in the chapter card, expands,
then closes on the same product introduction before retracting into the card.
Hover over the lower right of the demo for pause and replay.
The outro holds with an explicit Continue to Evaluation action; re-entry replays the chapter.
Command semantics and working constraints: ../README.md, ../PERSONAL.md.
Motion reference: ../video/src/compositions/keynote/scenes/TerminalJourney.tsx.
Skill scene reference: ../video/src/compositions/keynote/scenes/AgentJourney.tsx.
Parallel review does not automatically adopt a branch; adoption requires parallel-promote.
-->

---

<div class="visual-kicker orange resources-page-kicker">04 / EVALUATION · RESOURCE ACCOUNTING</div>

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

<div class="visual-kicker orange">04 / EVALUATION · DIRECT-AGENT COMPARISON</div>

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

<div class="visual-kicker purple">05 / INSIGHTS · WHAT THE RUN TAUGHT US</div>

# The run taught us more than the final score.

<div class="insight-lede">Two ways to widen the search without losing evidence.</div>

<div class="insight-grid">
  <div class="insight-item">
    <span class="insight-index blue">01</span>
    <div><strong>Different agents search differently.</strong><p>Recorded runs took different routes: local refinement, mechanism pivots, and broader search. Heterogeneous Scientists turn those search styles into a broader exploration prior.</p></div>
  </div>
  <div class="insight-item">
    <span class="insight-index orange">02</span>
    <div><strong>Parallel search + review can produce a stronger candidate.</strong><p>Independent Scientists explore without a shared live context. Review selects a branch, then a fresh Scientist synthesizes the evidence. One observed run moved from ≈0.6015 to 0.6055536 Primary.</p></div>
  </div>
</div>

<!--
This section distills two process observations from the final report: heterogeneous agents bring different search styles, and independent Parallel search followed by review can produce a stronger candidate. The Parallel/Synthesis score is an observed public-validation result, not part of the canonical E001–E013 frontier. Its improvement followed concrete modeling changes, so the run does not isolate parallelism as the cause.
[Sources]
- ../docs/FINAL_REPORT.md — sections 3.4–3.5, 4.2, 5.5, and 7.1–7.2
- ../docs/trajectories/parallel-synthesis.md — independent search, review, synthesis, and observed Primary 0.6055536270
-->

---

<!-- class: agentic-swe-fieldnote-slide -->

<div class="visual-kicker orange">05 / INSIGHTS · ENGINEERING PRACTICE</div>

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

<!-- class: open-world-slide -->

<div class="visual-kicker blue">APPENDIX / OPEN-WORLD RESEARCH</div>

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


<!--
The open-world framing and capability taxonomy are adapted from the user's supplied talk-track. LangGraph is used as a concrete workflow example: its documentation distinguishes predetermined workflows from dynamic agents and models workflows with state, nodes, and edges.
[Sources]
- https://docs.langchain.com/oss/python/langgraph/workflows-agents — workflows vs. agents
- https://docs.langchain.com/oss/python/langgraph/graph-api — state, nodes, and edges
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
