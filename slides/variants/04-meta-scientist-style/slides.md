---
theme: default
title: "SciOdyssey: Meta Scientist style"
info: |
  A concise visual narrative for SciOdyssey: problem, motivation, system, experience, evaluation, and insights.
author: SciOdyssey Team
colorSchema: light
aspectRatio: 16/9
canvasWidth: 980
transition: fade
fonts:
  sans: Avenir Next
  mono: Fira Code
  provider: none
mdc: true
---

<div class="meta-slide cover-slide">
  <img class="cover-image" src="/assets/research-world-mountain.png" alt="" aria-hidden="true" />
  <div class="topline"><span>SCIODYSSEY</span><i></i><span>DISCOVERY AMPLIFIED</span></div>
  <div class="cover-content">
    <div class="eyebrow">AUTONOMOUS ML RESEARCH / TECHJAM 2026</div>
    <h1>SciOdyssey<span>.</span></h1>
    <p class="cover-subtitle">A persistent research world<br />for fresh scientific trajectories.</p>
  </div>
  <div class="cover-foot">PRESERVE EVIDENCE. REOPEN JUDGMENT.</div>
  <div class="page-no">01</div>
</div>

<!--
Sources: ../../../README.md, ../../../docs/ARCHITECTURE.md, and ../../../docs/FINAL_REPORT.md.
The background is a project-local generated visual asset for this independent variant.
-->

---

<div class="meta-slide">
  <div class="topline"><span>SCIODYSSEY</span><i></i><span>THE PROBLEM</span></div>
  <div class="section-title"><h1>Research agents can execute.<br /><span>Discovery still breaks.</span></h1><p>Long-horizon research is not one tool call. It is a changing environment with expensive context and uncertain recovery.</p></div>
  <div class="problem-grid">
    <div class="soft-card problem-card">
      <div class="icon-circle">◷</div>
      <h2>Too much context</h2>
      <p>Understanding a file costs far more tokens than changing it. The agent pays that reading cost again.</p>
      <small>CONTEXT COST</small>
    </div>
    <div class="soft-card problem-card">
      <div class="icon-circle">◎</div>
      <h2>One trajectory</h2>
      <p>A long-lived context carries yesterday's momentum into today's search.</p>
      <small>ANCHORING</small>
    </div>
    <div class="soft-card problem-card">
      <div class="icon-circle">×</div>
      <h2>Closed workflow</h2>
      <p>Predefined tools and recovery paths stop when the environment produces something unexpected.</p>
      <small>OPEN-WORLD GAP</small>
    </div>
  </div>
  <div class="bottom-line"><span>THE QUESTION</span><strong>Can an agent carry a research task to completion?</strong></div>
  <div class="page-no">02</div>
</div>

<!--
Sources: ../../../README.md, ../../../docs/project_story.md, and ../../../docs/FINAL_REPORT.md §§1, 3.4–3.5, 4.2.
The context-cost statement is a conceptual design pressure, not a measured token ratio.
-->

---

<div class="meta-slide">
  <div class="topline"><span>SCIODYSSEY</span><i></i><span>MOTIVATION</span></div>
  <div class="section-title"><h1>Research is an <span>open-world</span> task.<br />We need an open-world coding agent.</h1><p>When the next capability is unknown, the system must be able to inspect the environment, extend it, and continue.</p></div>
  <div class="capability-grid">
    <div class="soft-card capability-card blue-card">
      <div class="card-index">01</div>
      <h2>Open action space</h2>
      <div class="token-row"><span>⌘</span><b>Shell</b><span>□</span><b>Files</b></div>
      <div class="token-row"><span>◎</span><b>Browser</b><span>⑂</span><b>Git</b></div>
      <small>USE WHAT EXISTS</small>
    </div>
    <div class="soft-card capability-card orange-card">
      <div class="card-index">02</div>
      <h2>Self-recovery</h2>
      <div class="token-row"><span>!</span><b>Read errors</b><span>▤</span><b>Inspect docs</b></div>
      <div class="token-row"><span>&lt;/&gt;</span><b>Inspect source</b><span>＋</span><b>Install</b></div>
      <small>FIX WHAT BREAKS</small>
    </div>
    <div class="soft-card capability-card purple-card">
      <div class="card-index">03</div>
      <h2>Runtime extension</h2>
      <div class="token-row"><span>◌</span><b>MCP</b><span>⌘</span><b>Skills</b></div>
      <div class="token-row"><span>›_</span><b>CLI</b><span>＋</span><b>Packages</b></div>
      <small>ADD WHAT IS MISSING</small>
    </div>
  </div>
  <div class="workflow-ribbon"><div><small>WORKFLOW EXAMPLE</small><strong>LangGraph makes a known path explicit as nodes and edges.</strong></div><span>Open-world research must leave the graph when a capability is missing.</span></div>
  <div class="page-no">03</div>
</div>

<!--
Sources: ../../../README.md, ../../../docs/ARCHITECTURE.md, and the official LangGraph documentation conceptually used in the main deck.
-->

---

<div class="meta-slide">
  <div class="topline"><span>SCIODYSSEY</span><i></i><span>SYSTEM OVERVIEW</span></div>
  <div class="section-title compact-title"><h1>An AI collaborator<br /><span>for scientific discovery.</span></h1><p>One persistent world. Two scientific roles. A runtime that enforces mechanics.</p></div>
  <div class="system-grid">
    <div class="world-card">
      <div class="mini-label blue-text">RESEARCH WORLD / ON DISK</div>
      <div class="world-item"><b>Evidence</b><span>Metrics, failures, original reports</span></div>
      <div class="world-item"><b>Curated priors</b><span>Current understanding, open to revision</span></div>
      <div class="world-item"><b>Code + State</b><span>Recoverable implementation and provenance</span></div>
    </div>
    <div class="roles-column">
      <div class="role-card scientist-card"><div class="role-mark">✦</div><div><small>SCIENTIFIC JUDGMENT</small><h2>Scientist</h2><p>Hypothesize, code, train, evaluate, interpret.</p></div></div>
      <div class="role-connector">reports evidence</div>
      <div class="role-card meta-card"><div class="role-mark">✓</div><div><small>PERSISTENCE AUTHORITY</small><h2>META</h2><p>Audit claims, scope conclusions, preserve memory.</p></div></div>
    </div>
    <div class="runtime-card">
      <div class="mini-label orange-text">RUNTIME</div>
      <h2>Deterministic mechanics.</h2>
      <ul><li>Isolation</li><li>Cancellation</li><li>Runner + evaluator</li><li>Logging and artifacts</li></ul>
      <div class="runtime-foot">The system protects the world.<br />The Scientist chooses the science.</div>
    </div>
  </div>
  <div class="bottom-line"><span>DESIGN PRINCIPLE</span><strong>Preserve the world. Reset the researcher.</strong></div>
  <div class="page-no">04</div>
</div>

<!--
Sources: ../../../README.md, ../../../docs/ARCHITECTURE.md, and ../../../docs/FINAL_REPORT.md §§3.1–3.3.
-->

---

<div class="meta-slide">
  <div class="topline"><span>SCIODYSSEY</span><i></i><span>ARCHITECTURE</span></div>
  <div class="section-title"><h1>Keep the world.<br /><span>Reset the researcher.</span></h1><p>The persistence boundary separates what should survive from what should be allowed to start again.</p></div>
  <div class="lifetime-grid">
    <div class="lifetime-panel persists-panel">
      <div class="lifetime-heading"><span class="number-badge blue-badge">01</span><div><small>PERSISTS</small><h2>Research world</h2></div></div>
      <div class="lifetime-list"><span>✓</span><b>Evidence and experiment ledger</b><span>✓</span><b>Failures and original reports</b><span>✓</span><b>Retained implementation + State</b><span>✓</span><b>Research preferences and constraints</b></div>
    </div>
    <div class="boundary-arrow"><b>CONTEXT RESET</b><span>↓</span><small>Inherit experience, not prior reasoning.</small></div>
    <div class="lifetime-panel resets-panel">
      <div class="lifetime-heading"><span class="number-badge purple-badge">02</span><div><small>RESTARTS</small><h2>Fresh Scientist</h2></div></div>
      <div class="lifetime-list"><span>↗</span><b>New scientific judgment</b><span>↗</span><b>Independent research trajectory</b><span>↗</span><b>New hypothesis selection</b><span>↗</span><b>Recoverable handoff from shared memory</b></div>
    </div>
  </div>
  <div class="handoff-strip"><strong>Audit</strong><span>scope</span><span>preserve</span><span>fresh Scientist</span></div>
  <div class="page-no">05</div>
</div>

<!--
Sources: ../../../README.md — central thesis and design principles; ../../../docs/ARCHITECTURE.md — memory layers, fresh Scientist, META, and runtime boundary.
-->

---

<div class="meta-slide">
  <div class="topline"><span>SCIODYSSEY</span><i></i><span>USER EXPERIENCE</span></div>
  <div class="section-title"><h1>From task contract<br /><span>to retained evidence.</span></h1><p>One bounded autonomous loop turns a plain research brief into checked artifacts and an auditable record.</p></div>
  <div class="experience-grid">
    <div class="experience-column">
      <div class="file-card"><code>task.md</code><h2>What to solve</h2><p>Objectives · constraints · evaluation</p><strong>Rank short videos for each user and interaction context.</strong></div>
      <div class="file-card"><code>PERSONAL.md</code><h2>How to solve it</h2><p>Preferences · research style · priorities</p><strong>Run autonomously. Preserve evidence. Keep credentials safe.</strong></div>
    </div>
    <div class="cycle-column">
      <div class="cycle-head"><small>ONE AUTONOMOUS CYCLE</small><b>E001 → E013</b></div>
      <div class="cycle-step"><span>01</span><b>Define</b><small>Read the contract and inspect the environment</small></div>
      <div class="cycle-step"><span>02</span><b>Run</b><small>Code, train, evaluate, and log the result</small></div>
      <div class="cycle-step"><span>03</span><b>Recover</b><small>Read failures and repair the experiment</small></div>
      <div class="cycle-step"><span>04</span><b>Retain</b><small>Keep evidence, code, and a scoped conclusion</small></div>
    </div>
    <div class="recovery-card">
      <div class="mini-label rose-text">RECOVERY OBSERVED</div>
      <h2>Failure became evidence.</h2>
      <p>NumPy float32 values broke JSON serialization. The Scientist converted the scalars, reran, and retained the measurements.</p>
      <div class="recovery-chain"><span>error</span><b>repair</b><span>rerun</span><b>retain</b></div>
    </div>
  </div>
  <div class="bottom-line"><span>SUPERVISION</span><strong>Autonomous by default. Supervisable by design.</strong></div>
  <div class="page-no">06</div>
</div>

<!--
Sources: ../../../README.md — task contract and autonomous loop; ../../../docs/FINAL_REPORT.md §4.1–4.2; ../../../submission/research-agent-kuairand/research_record/reports/cycle-1.md.
-->

---

<div class="meta-slide">
  <div class="topline"><span>SCIODYSSEY</span><i></i><span>EVALUATION</span></div>
  <div class="section-title"><h1>Verified result.<br /><span>Auditable run.</span></h1><p>Public validation shows the retained recipe and the record behind it.</p></div>
  <div class="evaluation-grid">
    <div class="score-panel">
      <small>PRIMARY / PUBLIC VALIDATION</small>
      <div class="big-score">0.6059363</div>
      <div class="score-delta">+0.0043363 <span>absolute improvement over Official FM</span></div>
      <div class="recipe">46 categorical features<br />eight-seed FM ensemble · NumPy / CPU</div>
    </div>
    <div class="bars-panel">
      <div class="chart-label">Primary score <span>0.6000 – 0.6060</span></div>
      <div class="bar-chart">
        <div class="bar-column"><div class="bar-value">0.6016000</div><div class="bar official-bar"></div><small>Official FM</small></div>
        <div class="bar-column"><div class="bar-value">0.6059363</div><div class="bar sci-bar"></div><small>SciOdyssey</small></div>
      </div>
      <div class="chart-foot">Primary = mean(GAUC, nDCG@5) · public validation only</div>
    </div>
  </div>
  <div class="stat-row"><div><b>13</b><span>named experiments</span></div><div><b>7</b><span>Full evaluations</span></div><div><b>0</b><span>post-launch manual scientific interventions</span></div><div><b>0</b><span>GPU-hours</span></div></div>
  <div class="evaluation-note">170,588 prediction rows passed the unchanged Starter Kit alignment checker. Hidden-test scoring remains organizer-controlled.</div>
  <div class="page-no">07</div>
</div>

<!--
Sources: ../../../README.md; ../../../docs/FINAL_REPORT.md Submission Snapshot and §§2, 4.1, 5.1, 5.3; ../../../submission/research-agent-kuairand/final/submit-check.txt.
-->

---

<div class="meta-slide">
  <div class="topline"><span>SCIODYSSEY</span><i></i><span>KEY INSIGHTS</span></div>
  <div class="section-title"><h1>Four things we learned<br /><span>on the journey.</span></h1><p>The run demonstrates a useful system boundary, while leaving important causal questions open.</p></div>
  <div class="insight-grid">
    <div class="insight-item"><span class="number-badge blue-badge">01</span><div><h2>Fresh trajectories interrupt anchoring</h2><p>Externalized evidence survives. Unfinished reasoning does not have to.</p></div></div>
    <div class="insight-item"><span class="number-badge orange-badge">02</span><div><h2>Context remains the bottleneck</h2><p>Understanding files and surrounding assumptions can dominate the edit itself.</p></div></div>
    <div class="insight-item"><span class="number-badge purple-badge">03</span><div><h2>Recovery is part of science</h2><p>A failed run can become a retained repair and a better-scoped conclusion.</p></div></div>
    <div class="insight-item"><span class="number-badge rose-badge">04</span><div><h2>Breadth needs evidence</h2><p>Parallel search is a capability. Its causal contribution still needs ablation.</p></div></div>
  </div>
  <div class="boundary-note"><small>OBSERVED, NOT PROVEN</small><strong>One task establishes a working boundary, not generality.</strong><span>META, State, and reset effects are not isolated.</span></div>
  <div class="page-no">08</div>
</div>

<!--
Sources: ../../../docs/FINAL_REPORT.md §§3.4–3.5, 4.2, 5.4–5.5, 6.1–6.3, 7.1–7.2; ../../../README.md — Limitations and Parallel breadth.
-->

---

<div class="meta-slide closing-slide">
  <img class="closing-image" src="/assets/research-world-mountain.png" alt="" aria-hidden="true" />
  <div class="topline"><span>SCIODYSSEY</span><i></i><span>NEXT TRAJECTORY</span></div>
  <div class="closing-content">
    <div class="eyebrow">THE RESEARCH WORLD CONTINUES</div>
    <h1>One research world.<br /><span>Many possible trajectories.</span></h1>
    <p>Preserve evidence. Reopen judgment. Let the next Scientist take the work further.</p>
    <div class="closing-link">github.com/zc6600/research-agent-kuairand ↗</div>
  </div>
  <div class="closing-foot">RESEARCH IS OPEN-WORLD.</div>
  <div class="page-no">09</div>
</div>

<!--
Sources: ../../../README.md, ../../../docs/ARCHITECTURE.md, and ../../../docs/FINAL_REPORT.md.
-->

<style>
@import './styles/index.css';
</style>
