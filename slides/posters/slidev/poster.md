---
theme: default
layout: default
class: poster-page
title: "SciOdyssey: Persistent research worlds, fresh scientific trajectories"
author: SciOdyssey Team
colorSchema: light
aspectRatio: 841/1189
canvasWidth: 1440
fonts:
  sans: Avenir Next
  mono: Fira Code
  provider: none
mdc: true
---
<div class="poster-shell">
  <header class="p-header">
    <div class="p-kicker">AUTONOMOUS ML RESEARCH / TECHJAM 2026 · TECHNICAL HANDOUT</div>
    <h1>SciOdyssey<span>.</span></h1>
    <div class="p-subtitle">Autonomous ML Research Agent</div>
    <div class="p-thesis">Preserve the <span>research world.</span> Reset the researcher.</div>
  </header>
  <main class="p-columns">
    <div class="p-left">
      <section class="p-section p-problem">
        <div class="p-kicker">01 / PROBLEM · FAILURE MODES</div>
        <h2>Why current research agents fall short.</h2>
        <p class="p-method-intro">Three obstacles to sustained autonomous research.</p>
        <div class="failure-grid">
          <article class="failure-card failure-closed">
            <div class="failure-head"><b>01</b><span>CLOSED-WORLD WORKFLOW</span></div>
            <div class="failure-visual"><span>Observe</span><span>Hypothesize</span><span>Code</span><span>Evaluate</span><em>× ERROR</em><small>dead end</small></div>
            <p>Predefined tools and rigid paths cannot handle the unexpected.</p>
            <strong>Unexpected problems require developer intervention.</strong>
          </article>
          <article class="failure-card failure-trajectory">
            <div class="failure-head"><b>02</b><span>SINGLE TRAJECTORY</span></div>
            <div class="failure-visual basin"><span>◆</span><i></i><i></i><i></i><small>same basin</small></div>
            <p>A long-lived context carries yesterday's momentum into today's search.</p>
            <strong>More iterations ≠ more exploration.</strong>
          </article>
          <article class="failure-card failure-tree">
            <div class="failure-head"><b>03</b><span>TREE SEARCH</span></div>
            <div class="failure-visual tree"><span>UNDERSTAND</span><b>→</b><span>EDIT</span><b>→</b><span>READ CONTEXT</span><b>→</b><small>repeat</small></div>
            <p>Reconstructing file context costs far more tokens than the edit itself.</p>
            <strong>Context cost forces repeated reading.</strong>
          </article>
        </div>
        <div class="failure-bridge"><b>DESIGN RESPONSE</b><span>Research is open-world, non-linear, and exploratory.</span><i>ADAPT</i><i>DIVERSIFY</i><i>LEARN</i></div>
      </section>

      <section class="p-section p-system p-design-section">
        <div class="p-kicker">02 / DESIGN · PERSISTENCE + RESET</div>
        <h2>One persistent world. Fresh scientific trajectories.</h2>
        <div class="p-design-core">
          <div class="p-world">
            <h3><span class="i-carbon:earth"></span>Research world <small>PERSISTENT / ON DISK</small></h3>
            <div class="p-memory"><b>EVIDENCE</b><div><strong>Knowledge + experiment ledger</strong><span>Metrics, failures and original reports</span></div></div>
            <div class="p-memory"><b>CURATED</b><div><strong>Research brief + working priors</strong><span>Working hypotheses; open to revision</span></div></div>
            <div class="p-memory"><b>CODE</b><div><strong>Retained implementation + State</strong><span>Recoverable version with evidence and provenance</span></div></div>
          </div>
          <div class="p-boundary"><span>↓</span><b>CONTEXT RESET</b><small>Inherit experience, not prior reasoning.</small></div>
        </div>
        <div class="architecture-mini">
          <div class="architecture-node environment"><b>ENVIRONMENT</b><span>Task contract<br />Curated data + evaluation<br />Starter baseline<br />Budget + permissions</span></div>
          <i aria-hidden="true">→</i>
          <div class="architecture-node world"><b>RESEARCH WORLD</b><span>Verified evidence<br />Knowledge ledger<br />Research brief<br />Implementation + State</span></div>
          <div class="architecture-reset"><b>CONTEXT<br />RESET</b><span>inherit experience,<br />not prior reasoning</span></div>
          <div class="architecture-node scientist"><b>FRESH SCIENTIST</b><span>reads world<br />forms hypotheses<br />runs experiments<br />reports evidence</span></div>
          <i aria-hidden="true">→</i>
          <div class="architecture-node meta"><b>META REVIEW</b><span>audits claims<br />scopes conclusions<br />curates memory<br />preserves optional State</span></div>
        </div>
        <div class="p-handoff"><span>↻</span><div><strong>Selective persistence / trajectory handoff</strong><small>Audit → scope → preserve → fresh Scientist</small></div></div>
        <div class="p-runtime"><strong>Runtime / deterministic mechanics</strong><span>Workspace isolation · runner + evaluator · logging · artifact capture · State operations</span></div>
        <div class="p-parallel-line"><b>PARALLEL BREADTH</b><span>isolated branches</span><i>→</i><span>post-hoc review</span><i>→</i><strong>explicit adoption</strong></div>
      </section>
    </div>

    <div class="p-right">
      <section class="p-section p-comparison p-evaluation">
        <div class="p-kicker">03 / EVALUATION · OUTCOME IN CONTEXT</div>
        <h2>Best retained run: public validation.</h2>
        <div class="p-eval-anchor">
          <strong>0.6059363</strong>
          <div><b>Primary score</b><span>+0.0043363 over the official FM reference</span></div>
        </div>
        <p class="p-chart-subtitle">KuaiRand-Pure · public validation · one recorded run per condition</p>
        <figure class="p-figure">
          <svg class="p-chart" viewBox="0 0 500 482" role="img" aria-label="Public-validation Primary versus total LLM tokens including cache reads. SciOdyssey 0.6059363 at 48.240 million; Codex approximately 0.6046 at 28.070 million.">
            <line x1="55" y1="366.88888888889267" x2="478" y2="366.88888888889267" class="grid"/><text x="44" y="371.88888888889267" text-anchor="end" class="axis">0.602</text>
<line x1="55" y1="310.03703703704076" x2="478" y2="310.03703703704076" class="grid"/><text x="44" y="315.03703703704076" text-anchor="end" class="axis">0.603</text>
<line x1="55" y1="253.18518518518883" x2="478" y2="253.18518518518883" class="grid"/><text x="44" y="258.18518518518886" text-anchor="end" class="axis">0.604</text>
<line x1="55" y1="196.33333333333695" x2="478" y2="196.33333333333695" class="grid"/><text x="44" y="201.33333333333695" text-anchor="end" class="axis">0.605</text>
<line x1="55" y1="139.48148148148505" x2="478" y2="139.48148148148505" class="grid"/><text x="44" y="144.48148148148505" text-anchor="end" class="axis">0.606</text>
            <line x1="55" y1="94" x2="55" y2="401" class="vgrid"/><text x="55" y="427" text-anchor="middle" class="axis">0</text>
<line x1="131.9090909090909" y1="94" x2="131.9090909090909" y2="401" class="vgrid"/><text x="131.9090909090909" y="427" text-anchor="middle" class="axis">10</text>
<line x1="208.8181818181818" y1="94" x2="208.8181818181818" y2="401" class="vgrid"/><text x="208.8181818181818" y="427" text-anchor="middle" class="axis">20</text>
<line x1="285.72727272727275" y1="94" x2="285.72727272727275" y2="401" class="vgrid"/><text x="285.72727272727275" y="427" text-anchor="middle" class="axis">30</text>
<line x1="362.6363636363636" y1="94" x2="362.6363636363636" y2="401" class="vgrid"/><text x="362.6363636363636" y="427" text-anchor="middle" class="axis">40</text>
<line x1="439.54545454545456" y1="94" x2="439.54545454545456" y2="401" class="vgrid"/><text x="439.54545454545456" y="427" text-anchor="middle" class="axis">50</text>
            <text x="55" y="25" class="axis-title">Primary score ↑</text>
            <line x1="55" y1="389.62962962963087" x2="478" y2="389.62962962963087" class="reference"/>
            <text x="476" y="380.62962962963087" text-anchor="end" class="axis">Official FM · 0.6016</text>
            <path d="M120.87245178181817 220.19405555556048 L103 191" class="leader"/>
            <circle cx="120.87245178181817" cy="220.19405555556048" r="6" class="direct"/>
            <text x="65" y="165" class="point-label">Antigravity direct</text><text x="65" y="185" class="point-sub">Gemini · 0.604580</text>
            <path d="M270.88054185454547 219.07407407407518 L237 263" class="leader"/>
            <circle cx="270.88054185454547" cy="219.07407407407518" r="6" class="direct"/>
            <text x="153" y="285" class="point-label">Codex direct</text><text x="153" y="306" class="point-sub">gpt-5.6-luna</text><text x="153" y="327" class="point-sub">≈0.6046</text>
            <path d="M359.6159667454546 213.38888888889062 L309 177" class="leader"/>
            <path d="M359.6159667454546 206.38888888889062 l7 7 -7 7 -7 -7 Z" class="hetero"/>
            <text x="238" y="130" class="point-label">Heterogeneous</text><text x="238" y="150" class="point-label">agents</text><text x="238" y="170" class="point-sub">Gemini · ≈0.6047</text>
            <path d="M401.4286630545455 184.96296296296782 H448.57389732727273 M401.4286630545455 178.96296296296782 v12 M448.57389732727273 178.96296296296782 v12" class="interval"/>
            <path d="M425.0012801909091 184.96296296296782 L461 283" class="leader"/>
            <path d="M425.0012801909091 176.96296296296782 l8 14 h-16 Z" class="gemini"/>
            <text x="482" y="305" text-anchor="end" class="point-label">Gemini-only</text><text x="482" y="325" text-anchor="end" class="point-label">SciOdyssey</text><text x="482" y="345" text-anchor="end" class="point-sub">Cycle 2 · 0.6052</text>
            <path d="M426.0104389818182 143.10294444444799 L461 79" class="leader"/>
            <circle cx="426.0104389818182" cy="143.10294444444799" r="8" fill="#20aa85"/>
            <text x="479" y="49" text-anchor="end" class="point-label submitted">SciOdyssey submission</text><text x="479" y="70" text-anchor="end" class="point-sub">0.605936 · verified</text>
            <text x="265" y="458" text-anchor="middle" class="axis-title">Total LLM tokens (millions)</text>
            <text x="265" y="480" text-anchor="middle" class="point-sub">Input + output, including cache reads</text>
          </svg>
        </figure>
        <div class="p-chart-note">* Comparative exploration across distinct agent setups under KuaiRand-Pure benchmark constraints.</div>
      </section>

      <section class="p-section p-results-panel">
        <div class="p-kicker">SCORE BREAKDOWN · VERIFIED SUBMISSION</div>
        <div class="p-results">
        <h3>What survived the run.</h3>
        <table class="p-score-table">
          <thead><tr><th>Metric</th><th>Reproduced FM</th><th>SciOdyssey</th><th>Absolute Δ</th></tr></thead>
          <tbody>
            <tr class="p-primary"><th>Primary</th><td>0.6016310</td><td>0.6059363</td><td>+0.0043053</td></tr>
            <tr><th>GAUC</th><td>0.6671070</td><td>0.6728421</td><td>+0.0057351</td></tr>
            <tr><th>nDCG@5</th><td>0.5361550</td><td>0.5390304</td><td>+0.0028754</td></tr>
          </tbody>
        </table>
        <div class="p-model">Primary = mean(GAUC, nDCG@5). Final recipe: 46 categorical features × eight-seed FM ensemble · NumPy / CPU.</div>
        <div class="p-run-strip"><div><strong>4</strong><span>autonomous<br />cycles</span></div><div><strong>13</strong><span>named<br />experiments</span></div><div><strong>0</strong><span>manual scientific<br />interventions*</span></div></div>
        <div class="p-proof">7 Full evaluations · 0 GPU-hours · 170,588 prediction rows<br />passed the unchanged Starter Kit alignment checker.</div>
        <div class="p-run-note">* 100% autonomous execution throughout the retained submission record.</div>
        </div>
      </section>

      <section class="p-section p-insights-section">
        <div class="p-kicker">04 / RUN OBSERVATIONS</div>
        <div class="p-insights">
          <h3>Observed behavior, not just a score.</h3>
          <div class="p-observation-grid">
            <div class="p-observation p-recovery"><strong>Recovery</strong><span>After evaluation, NumPy float32 values broke serialization. The Scientist repaired the writer; META retained the evidence for the next trajectory.</span></div>
            <div class="p-observation p-audit"><strong>Audit</strong><span>Reviews caught leakage and metric issues early. META audits empirical claims against artifacts before promoting State.</span></div>
            <div class="p-observation p-rotation"><strong>Reset the context. Rotate the prior.</strong><span>Gemini-only SciOdyssey already reached 0.6052. The best retained run reached 0.6059363 while rotating GPT and Gemini across fresh Scientist trajectories.</span></div>
          </div>
        </div>
        <div class="p-limit"><strong>Evidence boundary.</strong> The architecture worked with one model; model diversity was part of the best observed run, not an isolated ablation.</div>
      </section>
    </div>
  </main>

  <section class="p-section p-entry p-experience" aria-label="End-to-end research workflow">
    <div class="p-entry-heading"><div><div class="p-kicker">05 / HOW TO USE IT</div><h2>Start your journey.</h2></div><span>Paper shows the evidence. The website shows the experience.</span></div>
    <div class="p-entry-grid">
      <div class="p-entry-context">
        <div class="p-entry-files">
          <div><code>task.md</code><strong>What to solve</strong><span>Objectives · constraints · evaluation</span></div>
          <div><code>PERSONAL.md</code><strong>How you want it solved</strong><span>Preferences · research style · priorities</span></div>
        </div>
        <div class="p-entry-path"><span>Define the task</span><b>→</b><span>Delegate research</span><b>→</b><span>Review evidence</span></div>
      </div>
      <div class="p-entry-terminal" aria-label="Illustrative natural-language input in a coding agent; not an executed command">
        <div class="p-entry-bar"><span class="p-window-dots" aria-hidden="true"><i></i><i></i><i></i></span><span>Coding agent</span><small>EXAMPLE INPUT</small></div>
        <div class="p-entry-prompt"><span class="p-prompt-mark" aria-hidden="true">›</span><div>Use the research-agent skill.<br />Follow task.md and PERSONAL.md.<br />Let me review the results and evidence.<span class="p-caret" aria-hidden="true"></span></div></div>
      </div>
    </div>
  </section>
  <footer class="p-footer">
    <a href="https://github.com/zc6600/research-agent-kuairand">github.com/zc6600/research-agent-kuairand ↗</a>
    <div class="p-team">Chen Zhu · Zhou Ziyu · Shilin Xu · GE GAO · Jiran Li</div>
    <div class="p-source">Sources: slides/slides.md · docs/ARCHITECTURE.md · docs/FINAL_REPORT.md §§3–5 · Code, report, ledger and checked output in repository.</div>
  </footer>
</div>
<style>
@import '../../styles/poster.css';
.poster-page .p-design-section { margin-top: 25px; }
.poster-page .p-design-section h2 { margin-bottom: 15px; }
.poster-page .p-design-core { margin-bottom: 15px; }
.poster-page .p-design-core .p-boundary { margin-bottom: 12px; }
.poster-page .p-eval-anchor { display: grid; grid-template-columns: 210px 1fr; gap: 18px; align-items: center; margin: 14px 0 8px; padding: 13px 15px; background: #f4faf8; border: 1px solid #d7e9e1; border-left: 5px solid #20aa85; }
.poster-page .p-eval-anchor strong { color: #178c6d; font-size: 43px; line-height: 1; font-weight: 500; letter-spacing: -1.5px; }
.poster-page .p-eval-anchor b { display: block; color: var(--p-ink); font-size: 18px; line-height: 1.35; font-weight: 600; }
.poster-page .p-eval-anchor span { display: block; margin-top: 3px; color: var(--p-muted); font-size: 15px; line-height: 1.35; }
.poster-page .p-insights-section .p-observation-grid { grid-template-columns: 1fr 1fr; gap: 14px; }
.poster-page .p-observation.p-rotation { grid-column: 1 / -1; border-color: var(--p-blue); display: grid; grid-template-columns: 235px 1fr; gap: 14px; align-items: start; }
.poster-page .p-observation.p-rotation strong { color: #248aac; }
.poster-page .p-observation.p-rotation span { margin-top: 0; }
</style>
<!--
[Sources]
- ../../../video/out/films/sciodyssey-keynote-film.mp4 (terminal and coding-agent sequences), ../../../video/src/compositions/keynote/scenes/AgentJourney.tsx, and ../../../video/src/compositions/keynote/keynote.css — restrained light window, input prompt and blue caret. Prompt is an interaction example, not a captured session, executed command or vendor-specific API.
- ../../slides.md, "One Agent. Any ML Task. End to End." — task.md (objectives, constraints, evaluation), PERSONAL.md (preferences, research style, priorities); autonomous by default and supervisable by design. General-purpose intent is not a cross-task validation claim.
- ../../slides.md — main presentation and insights/recovery appendices; motivation, entry contracts, open-world actions, memory, serial and parallel handoff, results, audit trail, limitations.
- ../../../docs/ARCHITECTURE.md — responsibility boundaries, memory layers, optional State, fresh Scientist, META audits and deterministic runtime.
- ../../../docs/FINAL_REPORT.md §5.3 — Antigravity 8,564,976 / 0.6045803; three-hour Codex Luna 28,069,574 / approximately 0.6046 (provisional); heterogeneous 39,607,277 / approximately 0.6047; Gemini-only Cycle 2 45,043,916–51,173,911 / 0.6052; retained submission 48,240,128 / 0.6059363.
- ../../../competition_archive/kuairand-pure/reports/gpt-5.6-luna-3h-goal-baseline.md — three-hour run, not earlier shorter control.
- ../../../docs/FINAL_REPORT.md Submission Snapshot and §5.1 — Primary 0.6059363 (+0.0043363); GAUC 0.6728421 (+0.0054421); nDCG@5 0.5390304 (+0.0033304). Retained eight-seed, 46-field FM; 4 cycles, 13 named experiments, 7 Full evaluations, 0 post-launch manual scientific interventions, 0 GPU-hours, 170,588 checked rows.
- ../../../docs/FINAL_REPORT.md §§3.4, 4.2, 5.4–5.5 — parallel capability, serialization recovery, validity audits. Parallel breadth is not presented as the established cause of canonical performance.
The Gemini-only interval is accounting uncertainty, not statistical uncertainty; its point is the interval midpoint. All scores are public validation. Raw reports remain available; curated memory is fallible.
-->