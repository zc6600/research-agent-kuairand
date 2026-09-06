---
theme: default
title: "SciOdyssey: Runtime Storyboard"
info: |
  A runtime storyboard of Research Agent. Sources: README.md, docs/project_story.md, docs/FINAL_REPORT.md, competitions/kuairand/task.md, and PERSONAL.md.
author: Research Agent
colorSchema: light
aspectRatio: 16/9
canvasWidth: 980
transition: fade
drawings:
  persist: false
fonts:
  sans: Avenir Next
  mono: Fira Code
  provider: none
mdc: true
---

<div class="eyebrow">AUTONOMOUS ML RESEARCH / RUNTIME STORYBOARD</div>

<img class="cover-art" src="/assets/research-world-cover.png" alt="" aria-hidden="true">

<div class="hero cover-title"><span>SciOdyssey:</span><span>Runtime Storyboard</span></div>

<div class="lead">A live run from <span class="blue">task.md</span> to a validation-best checkpoint.</div>

<div class="cover-meta mono"><span>READ</span><span>ACT</span><span>VERIFY</span><span>RETAIN</span></div>

<!--
The deck is a compact runtime view of the Research Agent loop: externalized research memory persists while Scientist reasoning is reset at trajectory boundaries.
[Sources]
- ../../../README.md — introduction and serial loop
- ../../../docs/project_story.md — project framing
-->

---
class: runtime-entry
---

<div class="visual-kicker orange">01 / BOOT · READ</div>
<div class="runtime-spine"><span class="runtime-status active blue"><i></i>READ</span><span class="runtime-status"><i></i>ACT</span><span class="runtime-status"><i></i>VERIFY</span><span class="runtime-status"><i></i>RETAIN</span></div>

# The run starts by reading the contract.

<div class="runtime-lede">Before a Scientist changes code, the runtime loads the task, operator constraints, and scoring authority.</div>

<div class="runtime-entry-grid">
  <div class="runtime-brief">
    <div class="runtime-file mono"><span class="runtime-index orange">01</span><span>task.md</span><span class="runtime-state">READY</span></div>
    <h2>What to solve.</h2>
    <p>Rank short videos for each user and interaction context.</p>
    <small class="mono">KuaiRand-Pure · long_view · GAUC + nDCG@5</small>
  </div>
  <div class="runtime-brief">
    <div class="runtime-file mono"><span class="runtime-index blue">02</span><span>PERSONAL.md</span><span class="runtime-state">READY</span></div>
    <h2>How to work.</h2>
    <p>macOS / Apple Silicon, uv, ≤ 15 min per experiment.</p>
    <small class="mono">never print credentials</small>
  </div>
</div>

<div class="runtime-command"><span class="mono orange">COMMAND / STEP</span><pre>./scripts/research-agent step \
  --cli codex --target /absolute/path/to/project --allow-edits</pre></div>

<!--
The example task and personal constraints come directly from the repository contract. The command is the documented bounded cycle entry point.
[Sources]
- ../../../competitions/kuairand/task.md — challenge target, label, metrics, and evaluation rules
- ../../../PERSONAL.md — runtime facts and experiment constraint
- ../../../README.md — Quick start and step command
-->

---
class: runtime-load
---

<div class="visual-kicker blue">02 / LOAD · READ</div>
<div class="runtime-spine"><span class="runtime-status active blue"><i></i>READ</span><span class="runtime-status"><i></i>ACT</span><span class="runtime-status"><i></i>VERIFY</span><span class="runtime-status"><i></i>RETAIN</span></div>

# Experience enters as files, not unfinished thought.

<div class="runtime-load-grid">
  <div class="runtime-world-tree">
    <div class="runtime-tree-label mono blue">RESEARCH WORLD / PERSISTENT</div>
    <pre>research world
├─ evidence &amp; provenance
├─ verified knowledge
├─ current research state
├─ fallible priors
└─ State + implementation</pre>
  </div>
  <div class="runtime-readout">
    <div class="runtime-read-row"><span class="runtime-dot blue"></span><span class="mono">READ</span><strong>facts with evidence</strong></div>
    <div class="runtime-read-row"><span class="runtime-dot orange"></span><span class="mono">READ</span><strong>negative results and failures</strong></div>
    <div class="runtime-read-row"><span class="runtime-dot green"></span><span class="mono">READ</span><strong>reusable implementation</strong></div>
    <div class="runtime-read-note">A fresh Scientist inherits experience without inheriting the previous reasoning trajectory.</div>
  </div>
</div>

<div class="runtime-transition mono"><span>WORLD</span><b>→</b><span class="blue">FRESH SCIENTIST</span><b>→</b><span>NEW REASONING</span></div>

<!--
The tree is a conceptual map of the research world, not a literal directory listing.
[Sources]
- ../../../README.md — Research memory and fresh Scientist framing
- ../../../docs/project_story.md — persistent world / reset researcher distinction
-->

---
class: runtime-act
---

<div class="visual-kicker green">03 / RUN · ACT</div>
<div class="runtime-spine"><span class="runtime-status"><i></i>READ</span><span class="runtime-status active orange"><i></i>ACT</span><span class="runtime-status"><i></i>VERIFY</span><span class="runtime-status"><i></i>RETAIN</span></div>

# The Scientist turns constraints into experiments.

<div class="runtime-track">
  <div class="runtime-track-step"><span class="runtime-step-no mono blue">01</span><strong>INSPECT</strong><small>data · evaluator · code</small></div>
  <b>→</b>
  <div class="runtime-track-step"><span class="runtime-step-no mono orange">02</span><strong>HYPOTHESIZE</strong><small>choose a scientific question</small></div>
  <b>→</b>
  <div class="runtime-track-step"><span class="runtime-step-no mono rose">03</span><strong>IMPLEMENT</strong><small>modify · train · recover</small></div>
  <b>→</b>
  <div class="runtime-track-step"><span class="runtime-step-no mono purple">04</span><strong>EVALUATE</strong><small>interpret the evidence</small></div>
</div>

<div class="runtime-command runtime-command-wide"><span class="mono blue">LIFECYCLE / CONTROL SURFACE</span><pre>init  →  step  →  run  →  resume</pre></div>

<div class="runtime-callout"><span class="mono green">OWNER / SCIENTIST</span><span>scientific judgment, coding, experiments, interpretation</span></div>

<!--
This compresses the documented autonomous research lifecycle and the Scientist's responsibility. It does not impose a mandatory scientific workflow on the runtime.
[Sources]
- ../../../README.md — lifecycle and architecture
- ../../../docs/FINAL_REPORT.md — autonomous task and Scientist responsibilities
-->

---
class: runtime-verify
---

<div class="visual-kicker orange">04 / CHECK · VERIFY</div>
<div class="runtime-spine"><span class="runtime-status"><i></i>READ</span><span class="runtime-status"><i></i>ACT</span><span class="runtime-status active orange"><i></i>VERIFY</span><span class="runtime-status"><i></i>RETAIN</span></div>

# A metric counts only when the evaluator contract says it does.

<div class="runtime-contract">
  <div class="runtime-contract-row"><span class="mono blue">LABEL</span><strong>long_view</strong><small>fixed prediction label</small></div>
  <div class="runtime-contract-row"><span class="mono orange">PRIMARY</span><strong>mean(GAUC, nDCG@5)</strong><small>organizer evaluator</small></div>
  <div class="runtime-contract-row"><span class="mono rose">FULL</span><strong>124,909 public-validation rows</strong><small>hidden test is organizer-controlled</small></div>
  <div class="runtime-contract-row"><span class="mono purple">STOP</span><strong>3 Full evaluations with Δprimary ≤ 0.002</strong><small>Smoke / Medium are neutral</small></div>
</div>

<div class="runtime-evidence-snippet"><span class="mono">starter_kit/evaluate.py</span><span class="green">→ unchanged scoring semantics</span><span class="muted">→ public validation only during development</span></div>

<!--
The evaluator semantics, row count, hidden-test boundary, and convergence rule are fixed by the challenge contract and final report.
[Sources]
- ../../../competitions/kuairand/task.md — authoritative label, split, metrics, and convergence rule
- ../../../docs/FINAL_REPORT.md — evaluator authority and validation boundary
-->

---
class: runtime-trace
---

<div class="visual-kicker purple">05 / TRACE · VERIFY</div>
<div class="runtime-spine"><span class="runtime-status"><i></i>READ</span><span class="runtime-status"><i></i>ACT</span><span class="runtime-status active purple"><i></i>VERIFY</span><span class="runtime-status"><i></i>RETAIN</span></div>

# The E001–E013 record turns search into an auditable run.

<div class="runtime-ledger">
  <div class="runtime-ledger-row"><span class="mono blue">E001</span><strong>screen</strong><span>target-encoding variants rejected</span><span class="runtime-chip">MEDIUM</span></div>
  <div class="runtime-ledger-row"><span class="mono orange">E003</span><strong>recover</strong><span>rich FM established a valid checkpoint</span><span class="runtime-chip">FULL</span></div>
  <div class="runtime-ledger-row"><span class="mono rose">E008</span><strong>ensemble</strong><span>five-seed FM became the stronger baseline</span><span class="runtime-chip">FULL</span></div>
  <div class="runtime-ledger-row"><span class="mono purple">E013</span><strong>retain</strong><span>eight-seed 46-field FM selected</span><span class="runtime-chip runtime-chip-final">FULL</span></div>
</div>

<div class="runtime-trace-footer"><span><strong>13</strong> named experiments</span><span><strong>7</strong> Full evaluations</span><span><strong>0</strong> post-launch manual scientific interventions</span></div>

<!--
The ledger events and counts are a compressed, audience-facing rendering of the canonical E001–E013 trajectory.
[Sources]
- ../../../docs/FINAL_REPORT.md — sections 4.1, 5.1, and 6.3
- ../../../README.md — retained trajectory summary
-->

---
class: runtime-handoff
---

<div class="visual-kicker rose">06 / HANDOFF · RETAIN</div>
<div class="runtime-spine"><span class="runtime-status"><i></i>READ</span><span class="runtime-status"><i></i>ACT</span><span class="runtime-status"><i></i>VERIFY</span><span class="runtime-status active rose"><i></i>RETAIN</span></div>

# The handoff moves evidence forward and cognition back to zero.

<div class="runtime-handoff-spine">
  <div class="runtime-handoff-step read"><span class="mono">READ</span><strong>fresh Scientist</strong><small>opens the research world</small></div>
  <b>→</b>
  <div class="runtime-handoff-step act"><span class="mono">ACT</span><strong>Scientist</strong><small>chooses the science</small></div>
  <b>→</b>
  <div class="runtime-handoff-step verify"><span class="mono">VERIFY</span><strong>META</strong><small>audits claim ↔ evidence</small></div>
  <b>→</b>
  <div class="runtime-handoff-step retain"><span class="mono">RETAIN</span><strong>research world</strong><small>preserve · scope · hand off</small></div>
</div>

<div class="runtime-runtime-band"><span class="mono orange">RUNTIME / SYSTEM LIFETIME</span><span>workspace isolation</span><span>cancellation</span><span>provenance</span><span>State integrity</span></div>

<div class="runtime-handoff-note">META owns what survives. Runtime owns deterministic mechanics. Neither replaces the Scientist's scientific judgment.</div>

<!--
This is the core system storyboard requested: a clean four-stage status spine rather than an orbit. META audits and preserves; Runtime enforces mechanics.
[Sources]
- ../../../README.md — architecture, serial loop, and ownership boundaries
- ../../../docs/FINAL_REPORT.md — META evidence-governance role and Runtime responsibilities
-->

---
class: runtime-reset
---

<div class="visual-kicker blue">07 / RESET · READ</div>
<div class="runtime-spine"><span class="runtime-status active blue"><i></i>READ</span><span class="runtime-status"><i></i>ACT</span><span class="runtime-status"><i></i>VERIFY</span><span class="runtime-status"><i></i>RETAIN</span></div>

# Selective persistence breaks the momentum loop.

<div class="runtime-reset-grid">
  <div class="runtime-reset-column retain-column">
    <div class="mono green">PERSISTS ACROSS TRAJECTORIES</div>
    <ul><li>metrics and provenance</li><li>failed experiments</li><li>original reports</li><li>reusable implementation</li></ul>
  </div>
  <div class="runtime-reset-arrow">→ <span class="mono rose">CONTEXT RESET</span> →</div>
  <div class="runtime-reset-column reset-column">
    <div class="mono rose">STARTS FRESH</div>
    <ul><li>an independent reasoning trajectory</li><li>room to challenge inherited framing</li><li>experience, not momentum</li></ul>
  </div>
</div>

<div class="runtime-bottom-line">The world keeps the evidence. The Scientist gets a new chance to search.</div>

<!--
The persistence/reset distinction is the project's central design thesis. Compression is lossy, so raw evidence remains available for audit.
[Sources]
- ../../../README.md — Why fresh Scientists? and Research memory
- ../../../docs/FINAL_REPORT.md — trajectory failure and evidence boundary
-->

---
class: runtime-result
---

<div class="visual-kicker green">08 / RESULT · RETAIN</div>
<div class="runtime-spine"><span class="runtime-status"><i></i>READ</span><span class="runtime-status"><i></i>ACT</span><span class="runtime-status"><i></i>VERIFY</span><span class="runtime-status active green"><i></i>RETAIN</span></div>

# The live run retained the validation-best checkpoint.

<div class="runtime-result-grid">
  <div class="runtime-score-table">
    <div class="runtime-score-head"><span></span><span>GAUC</span><span>nDCG@5</span><span>PRIMARY</span></div>
    <div class="runtime-score-row"><strong>Official five-field FM</strong><span>0.6674000</span><span>0.5357000</span><span>0.6016000</span></div>
    <div class="runtime-score-row final"><strong>Research Agent submission</strong><span>0.6728421</span><span>0.5390304</span><span>0.6059363</span></div>
    <div class="runtime-score-row delta"><strong>Δ vs reference</strong><span>+0.0054421</span><span>+0.0033304</span><span>+0.0043363</span></div>
  </div>
  <div class="runtime-result-status">
    <div class="mono rose">E013 / FULL / SELECTED</div>
    <strong>CONVERGENCE 3 / 3</strong>
    <p>4 autonomous META–Scientist cycles out of the 50-iteration cap.</p>
    <p>0 GPU-hours · 48,240,128 total tokens including cache-read input.</p>
  </div>
</div>

<div class="runtime-result-note">The checkpoint was selected from public validation only; the final submission CSV contains 170,588 rows and passed the unchanged Starter Kit alignment checker.</div>

<!--
All scores and resource counts are the canonical retained E001–E013 result.
[Sources]
- ../../../README.md — result table and retained trajectory summary
- ../../../docs/FINAL_REPORT.md — Submission Snapshot and convergence sections
-->

---
class: runtime-replay
---

<div class="visual-kicker orange">09 / REPLAY · RETAIN</div>
<div class="runtime-spine"><span class="runtime-status"><i></i>READ</span><span class="runtime-status"><i></i>ACT</span><span class="runtime-status"><i></i>VERIFY</span><span class="runtime-status active orange"><i></i>RETAIN</span></div>

# A retained result is also a runnable artifact.

<div class="runtime-replay-grid">
  <div class="runtime-command runtime-reproduction"><span class="mono orange">REPRODUCTION / PINNED ENVIRONMENT</span><pre>cd submission/research-agent-kuairand
uv run --python 3.12.11 --with numpy==2.5.2 \
  python system/ensemble_46.py \
  --seeds 0 1 2 3 4 5 6 7 --k 16 --lr 0.001 \
  --l2 1e-5 --full --submission final/research-agent-test.csv \
  --output final/research-agent-run.json</pre></div>
  <div class="runtime-replay-proof">
    <div class="mono blue">ARTIFACT CHECK</div>
    <strong>170,588 rows</strong><span>Starter Kit alignment checker passed</span>
    <strong>CPU / NumPy</strong><span>0 GPU-hours</span>
    <div class="runtime-replay-close">Preserve the research world.<br><span class="rose">Reset the researcher.</span></div>
  </div>
</div>

<!--
The reproduction command, pinned versions, output row count, checker result, and CPU-only implementation are documented project facts.
[Sources]
- ../../../README.md — reproduction command and final output
- ../../../docs/FINAL_REPORT.md — reproducibility and resource accounting
-->
