<script setup lang="ts">
import { ref } from 'vue'
import EvaluationScoreBars from './EvaluationScoreBars.vue'
import EvaluationTrajectory from './EvaluationTrajectory.vue'
import EvaluationTokenScoreChart from './EvaluationTokenScoreChart.vue'

defineProps<{ card: string }>()
const comparisonPage = ref(0)
</script>

<template>
  <div class="card-body" :class="`card-body-${card}`">
    <template v-if="card === 'result'">
      <div class="result-summary">
        <div>
          <span class="eyeline">PUBLIC-VALIDATION PRIMARY</span>
          <strong class="hero-number">0.6059363</strong>
          <p><b>+0.0043363</b> over the official five-field FM</p>
          <small>46 categorical feature interactions · 8-seed FM · rank 16 · NumPy / CPU</small>
        </div>
        <EvaluationScoreBars />
      </div>
      <table>
        <thead><tr><th>Metric</th><th>Official FM</th><th>Our agent</th></tr></thead>
        <tbody><tr><td>GAUC</td><td>0.6674000</td><td>0.6728421</td></tr><tr><td>nDCG@5</td><td>0.5357000</td><td>0.5390304</td></tr><tr><td>Primary</td><td>0.6016000</td><td><b>0.6059363</b></td></tr></tbody>
      </table>
      <p class="boundary">Primary = mean(GAUC, nDCG@5). Verified on the official validation split following challenge protocol.</p>
    </template>

    <template v-else-if="card === 'trajectory'">
      <EvaluationTrajectory />
    </template>

    <template v-else-if="card === 'robustness'">
      <p class="robustness-intro">
        Autonomous research requires both <b>execution-level crash recovery</b> and <b>epistemic defense</b> against false breakthroughs.
      </p>

      <div class="two-tier-grid">
        <div class="tier-card">
          <div class="tier-head">
            <span class="tier-badge">TIER 1 · RUNTIME SELF-HEALING</span>
            <h4>Crash Auto-Recovery</h4>
            <span class="tier-subhead">Execution-level resilience</span>
          </div>

          <div class="tier-flow">
            <div class="flow-item">
              <span class="flow-label">Failure</span>
              <p>Cycle 1 evidence writing crashed on <code>numpy.float32</code> serialization.</p>
            </div>
            <div class="flow-item">
              <span class="flow-label">Action</span>
              <p>Scientist parsed traceback, auto-patched scalar helper, and reran cleanly.</p>
            </div>
            <div class="flow-item result">
              <span class="flow-label">Outcome</span>
              <p><b>0 human bugfixes</b> · Unattended rerun succeeded · Telemetry preserved.</p>
            </div>
          </div>
        </div>

        <div class="tier-card">
          <div class="tier-head">
            <span class="tier-badge">TIER 2 · META GATEKEEPING</span>
            <h4>Spurious State Rejection</h4>
            <span class="tier-subhead">Epistemic validity defense</span>
          </div>

          <div class="tier-flow">
            <div class="flow-item">
              <span class="flow-label">False Claim</span>
              <p>Scientist claimed BPR beat baseline on a medium proxy evaluation.</p>
            </div>
            <div class="flow-item">
              <span class="flow-label">Action</span>
              <p>META audited <code>system/data.py</code> line-by-line, detecting <code>UNK</code> user leakage.</p>
            </div>
            <div class="flow-item result">
              <span class="flow-label">Outcome</span>
              <p><b>Promotion blocked</b> · Filtered validation guarded · Zero contaminated state.</p>
            </div>
          </div>
        </div>
      </div>

      <p class="boundary">Audited empirical receipts archived under <code>docs/evidence/meta_audit/</code>.</p>
    </template>

    <template v-else-if="card === 'comparison'">
      <div class="comparison-tab-bar">
        <div class="comparison-tabs mono" role="tablist">
          <button
            type="button"
            class="comp-tab-btn"
            :class="{ active: comparisonPage === 0 }"
            role="tab"
            :aria-selected="comparisonPage === 0"
            @click="comparisonPage = 0"
          >
            <span>01</span> ABLATION BENCHMARK
          </button>
          <button
            type="button"
            class="comp-tab-btn"
            :class="{ active: comparisonPage === 1 }"
            role="tab"
            :aria-selected="comparisonPage === 1"
            @click="comparisonPage = 1"
          >
            <span>02</span> WHY IT WON · 01 vs 03 STORY
          </button>
        </div>
        <span class="comparison-tab-hint mono">
          {{ comparisonPage === 0 ? 'GEMINI 3.7 FLASH ABLATION' : 'HISTORY SHAPES SEARCH · CASE STUDY' }}
        </span>
      </div>

      <template v-if="comparisonPage === 0">
        <div class="comparison-intro">
          <p>Keep Gemini 3.7 Flash in the comparison and change only the research organization: direct agent → delegated subagents → Meta-Scientist over Antigravity.</p>
        </div>

        <div class="architecture-progress">
          <div class="arch-step">
            <span class="arch-label">01 · DIRECT Antigravity</span>
            <strong>Antigravity</strong>
            <div class="arch-score">0.6045803</div>
            <p>Single-agent 2h run.</p>
          </div>
          <span class="arch-arrow">→</span>
          <div class="arch-step">
            <span class="arch-label">02 · SUBAGENTS</span>
            <strong>Antigravity + delegated subagents</strong>
            <div class="arch-score">0.6047213</div>
            <p>Broader delegation, no persistent Meta layer.</p>
          </div>
          <span class="arch-arrow">→</span>
          <div class="arch-step winner">
            <span class="arch-label">03 · META-SCIENTIST</span>
            <strong>Meta-Scientist + Antigravity</strong>
            <div class="arch-score">0.6052000</div>
            <p>Persistent world memory + fresh Scientist reset.</p>
          </div>
        </div>

        <div class="comparison-chart-shell">
          <EvaluationTokenScoreChart />
        </div>
      </template>

      <template v-else>
        <div class="comp-story-container">
          <!-- TOP HERO COMPARISON -->
          <div class="story-h2h-grid">
            <div class="h2h-card h2h-direct">
              <div class="h2h-card-top">
                <span class="h2h-badge mono">01 · DIRECT AGENT (SINGLE TRAJECTORY)</span>
                <span class="h2h-duration mono">2h UNBROKEN RUN</span>
              </div>
              <div class="h2h-score-row">
                <strong class="h2h-score">0.6045803</strong>
                <span class="h2h-regime-pill blue mono">HORIZONTAL HOPPING</span>
              </div>
              <div class="h2h-pipeline mono">
                <span>FM</span>
                <i>→</i>
                <span>8-Field</span>
                <i>→</i>
                <span>BPR</span>
                <i>→</i>
                <span>DeepFM</span>
                <i>→</i>
                <span>MT-DeepFM</span>
              </div>
            </div>

            <div class="story-vs-divider">
              <span class="mono">VS</span>
              <small class="mono">+0.00062</small>
            </div>

            <div class="h2h-card h2h-meta">
              <div class="h2h-card-top">
                <span class="h2h-badge purple mono">03 · META-SCIENTIST (PERSISTENT LOOP)</span>
                <span class="h2h-duration purple mono">2-CYCLE HANDOFF · RESET</span>
              </div>
              <div class="h2h-score-row">
                <strong class="h2h-score purple">0.6052000</strong>
                <span class="h2h-regime-pill purple mono">VERTICAL DEEP-DIVE</span>
                <span class="h2h-gauc-badge mono">GAUC 0.6725</span>
              </div>
              <div class="h2h-pipeline mono purple-flow">
                <span>Cycle 1 Seq Thesis</span>
                <i>→</i>
                <span>E007 Multi-Facet</span>
                <i>→</i>
                <span class="peak-exp">E008 Item DIN (Peak)</span>
                <i>→</i>
                <span>E009 DualSeq</span>
              </div>
            </div>
          </div>

          <!-- 3 DETAILED AT-A-GLANCE COLUMNS -->
          <div class="story-pillars-grid">
            <!-- PILLAR 1: SEARCH & HYPOTHESIS -->
            <div class="story-pillar">
              <div class="pillar-header">
                <span class="pillar-num mono">01 / TRAJECTORY</span>
                <h5>Search & Hypothesis Depth</h5>
              </div>
              <div class="pillar-body">
                <div class="contrast-row direct">
                  <span class="row-label mono">01 DIRECT</span>
                  <div class="fact-list">
                    <div class="fact-item">
                      <span class="fact-tag">Pattern</span>
                      <span><b>Horizontal Hopping:</b> Abandoned model after 1 trial if gains stalled</span>
                    </div>
                    <div class="fact-item">
                      <span class="fact-tag">Depth</span>
                      <span>5 disjoint architectures, superficial hyperparameter tuning</span>
                    </div>
                  </div>
                </div>
                <div class="contrast-row meta">
                  <span class="row-label mono">03 META</span>
                  <div class="fact-list">
                    <div class="fact-item">
                      <span class="fact-tag">Pattern</span>
                      <span><b>Vertical DIN Tuning:</b> Grounded in verified sequence dynamics</span>
                    </div>
                    <div class="fact-item">
                      <span class="fact-tag">Receipt</span>
                      <span><b>E007</b> (Facets) → <b>E008</b> (Cosine Annealing) → <b>E009</b> (DualSeq)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- PILLAR 2: CODE INTEGRITY & AUDIT -->
            <div class="story-pillar">
              <div class="pillar-header">
                <span class="pillar-num mono">02 / CODE AUDIT</span>
                <h5>Technical Debt & Verification</h5>
              </div>
              <div class="pillar-body">
                <div class="contrast-row direct">
                  <span class="row-label mono">01 DIRECT</span>
                  <div class="fact-list">
                    <div class="fact-item">
                      <span class="fact-tag bug">Bug #1</span>
                      <span><b>Cross-user BPR:</b> Paired pos/neg items across different users</span>
                    </div>
                    <div class="fact-item">
                      <span class="fact-tag bug">Bug #2</span>
                      <span><b>Target Leakage:</b> Global mean stats computed across full split</span>
                    </div>
                    <div class="fact-item">
                      <span class="fact-tag bug">Bug #3</span>
                      <span><b>Modulo Weekday:</b> Distorted cyclical time representation</span>
                    </div>
                  </div>
                </div>
                <div class="contrast-row meta">
                  <span class="row-label mono">03 META</span>
                  <div class="fact-list">
                    <div class="fact-item">
                      <span class="fact-tag verified">Clean Reset</span>
                      <span>Fresh Scientist wrote leak-free, mathematically verified layers</span>
                    </div>
                    <div class="fact-item">
                      <span class="fact-tag verified">Gatekeeping</span>
                      <span>Meta audited proxy data flow; blocked spurious state promotion</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- PILLAR 3: HISTORY MECHANISM -->
            <div class="story-pillar">
              <div class="pillar-header">
                <span class="pillar-num mono">03 / MECHANISM</span>
                <h5>History Shapes Search</h5>
              </div>
              <div class="pillar-body">
                <div class="contrast-row direct">
                  <span class="row-label mono">01 DIRECT</span>
                  <div class="fact-list">
                    <div class="fact-item">
                      <span class="fact-tag">Nature</span>
                      <span><b>Context as Baggage:</b> Dirty scripts & failed traces clog attention</span>
                    </div>
                    <div class="fact-item">
                      <span class="fact-tag">Effect</span>
                      <span>Anchoring inertia: Model trapped in repetitive local patching</span>
                    </div>
                  </div>
                </div>
                <div class="contrast-row meta">
                  <span class="row-label mono">03 META</span>
                  <div class="fact-list">
                    <div class="fact-item">
                      <span class="fact-tag">Nature</span>
                      <span><b>Context as Leverage:</b> <em>“Inherit evidence, not momentum”</em></span>
                    </div>
                    <div class="fact-item">
                      <span class="fact-tag">Effect</span>
                      <span>Durable State preserved externally; fresh context explores boldly</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- FULL-WIDTH BOTTOM TAKEAWAY -->
          <div class="story-takeaway-full">
            <span class="takeaway-pill mono">CORE TAKEAWAY</span>
            <p>Same model family (Gemini 3.7 Flash). In an unbroken context, history acts as cognitive baggage; in a Meta-Scientist loop, history is externalized scientific leverage.</p>
          </div>
        </div>
      </template>
    </template>

    <template v-else-if="card === 'tokenmaxxing'">
      <div class="token-hero">
        <span class="eyeline">PROJECT-LEVEL RESOURCE ACCOUNTING</span>
        <div class="token-hero-box">
          <div class="token-hero-left"><strong class="token-amount">~$10</strong><span class="token-caption">Total project cost</span></div>
          <div class="token-hero-right"><p class="token-thesis">Subscription-equivalent usage from first line of code to final result.</p><div class="token-tags"><span>coding</span><i>·</i><span>debugging</span><i>·</i><span>agent loops</span><i>·</i><span>all 11 experiments</span></div></div>
        </div>
      </div>
      <div class="resource-cards three-cards">
        <div><span class="resource-label">MODEL</span><strong>One GPT Plus + One Gemini Pro for 7 days</strong><p>Two consumer subscriptions covered the entire autonomous research loop.</p></div>
        <div><span class="resource-label">HARDWARE</span><strong>1 × MacBook M2</strong><p>All development, feature engineering, and validation ran on one consumer laptop.</p></div>
        <div><span class="resource-label">COMPUTE</span><strong>0 GPU-hours</strong><p>100% CPU NumPy training and inference; zero cloud GPU clusters required.</p></div>
      </div>
      <p class="boundary">Performance came from the autonomous research loop, not an expensive compute budget.</p>
    </template>
  </div>
</template>

<style scoped>
.card-body { color: #434a52; font-size: 13px; line-height: 1.42; }
.card-body p { margin: 7px 0; }
.card-body h4 { margin: 0 0 5px; color: var(--ink); font-size: 14px; font-weight: 750; }
.card-body small { color: #7d7d82; font-size: 10.5px; }
.eyeline { font-size: 10px; letter-spacing: 1px; color: #7d7d82; }
.hero-number { display: block; font-size: 40px; line-height: 1.1; letter-spacing: -1.6px; color: var(--accent); }
.result-summary { display: grid; grid-template-columns: 1.1fr 1fr; gap: 24px; align-items: center; }
.card-body table { width: 100%; border-collapse: collapse; margin: 10px 0 0; font-size: 12.5px; }
.card-body th, .card-body td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #e6e6e8; }
.card-body th { color: #7d7d82; font-size: 11px; font-weight: 650; }
.card-body .boundary { padding-left: 12px; border-left: 2px solid var(--accent); color: #727981; font-size: 11.5px; line-height: 1.42; margin-top: 8px; }
.token-hero strong { display: block; margin-top: 6px; color: var(--accent); font-size: 25px; line-height: 1.08; letter-spacing: -.7px; }
.token-hero p { max-width: 650px; }

.robustness-intro { margin: 0 0 14px; color: #5a646e; font-size: 13.5px; line-height: 1.38; max-width: 860px; }
.robustness-intro b { color: var(--ink); font-weight: 700; }
.two-tier-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 10px; }
.tier-card { padding: 13px 15px; border: 1px solid #e4e7eb; border-radius: 12px; background: #fbfcfd; display: flex; flex-direction: column; gap: 10px; }
.tier-head { border-bottom: 1px solid #edf0f3; padding-bottom: 7px; }
.tier-badge { font-family: var(--mono); font-size: 9px; font-weight: 700; letter-spacing: 0.8px; color: var(--accent); }
.tier-card h4 { margin: 2px 0 1px; font-size: 14.5px; color: var(--ink); font-weight: 750; letter-spacing: -0.2px; }
.tier-subhead { display: block; font-size: 10.5px; color: #838c96; }
.tier-flow { display: flex; flex-direction: column; gap: 7px; }
.flow-item { display: grid; grid-template-columns: 78px 1fr; align-items: baseline; gap: 8px; font-size: 11.5px; line-height: 1.32; padding: 6px 9px; border-radius: 6px; background: #f5f7f9; }
.flow-item.result { background: #edf6f0; border: 1px solid #d0e8d7; }
.flow-label { font-family: var(--mono); font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #6a7480; }
.flow-item.result .flow-label { color: #247346; }
.flow-item p { margin: 0; color: #434c56; }
.flow-item.result p { color: #1a4f30; }
.flow-item code { font-family: var(--mono); font-size: 10.5px; padding: 1px 4px; background: rgba(0,0,0,0.05); border-radius: 3px; }
.comparison-intro { margin-bottom: 10px; }
.comparison-intro p { margin: 0 0 8px; max-width: 900px; color: #7f878f; font-size: 12.2px; line-height: 1.32; }
.architecture-progress { display: grid; grid-template-columns: 1fr 34px 1fr 34px 1.05fr; gap: 8px; align-items: stretch; margin: 8px 0 14px; }
.arch-step { min-height: 94px; padding: 10px 12px; border: 1px solid #e6e6e8; border-radius: 12px; background: #fbfcfd; }
.arch-step.winner { border-color: color-mix(in srgb, var(--accent) 55%, #e6e6e8); background: linear-gradient(180deg, #ffffff, #fbf9ff); box-shadow: 0 2px 10px rgba(0,0,0,.035); }
.arch-label { display: block; font-size: 8.5px; font-weight: 700; letter-spacing: .85px; color: #7d7d82; }
.arch-step.winner .arch-label { color: var(--accent); }
.arch-step strong { display: block; margin-top: 4px; color: var(--ink); font-size: 12px; line-height: 1.15; }
.arch-score { margin: 3px 0 2px; color: #434a52; font-size: 24px; line-height: 1; font-weight: 700; letter-spacing: -.85px; }
.arch-step.winner .arch-score { color: var(--accent); font-size: 25px; }
.arch-step p { margin: 0; color: #8c949c; font-size: 9.6px; line-height: 1.22; }
.arch-arrow { display: grid; place-items: center; color: #c6cbd0; font-size: 21px; font-weight: 750; }
.comparison-chart-shell { margin-top: 0; }
.comparison-tab-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f0f2f5;
}
.comparison-tabs {
  display: flex;
  gap: 4px;
  background: #f1f3f6;
  padding: 3px;
  border-radius: 8px;
}
.comp-tab-btn {
  border: 0;
  background: none;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 750;
  color: #7d7d82;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all .2s cubic-bezier(.22,1,.36,1);
}
.comp-tab-btn span {
  opacity: .55;
  font-size: 9px;
}
.comp-tab-btn.active {
  background: #fff;
  color: var(--accent);
  box-shadow: 0 2px 6px rgba(0,0,0,.08);
}
.comp-tab-btn.active span {
  opacity: 1;
  color: var(--accent);
}
.comparison-tab-hint {
  font-size: 9px;
  color: #9aa0a6;
  letter-spacing: .75px;
}
.comp-story-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.story-h2h-grid {
  display: grid;
  grid-template-columns: 1fr 34px 1fr;
  align-items: stretch;
  gap: 8px;
}
.h2h-card {
  padding: 8px 11px;
  border: 1px solid #e6e6e8;
  border-radius: 12px;
  background: #fbfcfd;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.h2h-card.h2h-meta {
  border-color: color-mix(in srgb, var(--accent) 55%, #e6e6e8);
  background: linear-gradient(180deg, #ffffff, #fbf9ff);
  box-shadow: 0 2px 10px rgba(166,108,255,.05);
}
.h2h-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.h2h-badge {
  font-size: 8.5px;
  font-weight: 750;
  color: #5d7fbd;
  letter-spacing: .5px;
}
.h2h-badge.purple {
  color: var(--accent);
}
.h2h-duration {
  font-size: 8px;
  color: #9aa0a6;
  letter-spacing: .4px;
}
.h2h-duration.purple {
  color: color-mix(in srgb, var(--accent) 70%, #9aa0a6);
}
.h2h-score-row {
  display: flex;
  align-items: center;
  gap: 7px;
}
.h2h-score {
  font-size: 21px;
  font-weight: 800;
  color: #434a52;
  letter-spacing: -.7px;
  line-height: 1;
}
.h2h-score.purple {
  color: var(--accent);
}
.h2h-regime-pill {
  font-size: 7.8px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: .4px;
}
.h2h-regime-pill.blue {
  background: #ebf1fa;
  color: #4d6ea6;
}
.h2h-regime-pill.purple {
  background: #f1e9fe;
  color: var(--accent);
}
.h2h-gauc-badge {
  font-size: 8px;
  font-weight: 750;
  color: #7d848e;
  margin-left: auto;
}
.h2h-pipeline {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 8.5px;
  color: #555d66;
  background: #f4f6f9;
  padding: 3px 7px;
  border-radius: 6px;
  overflow: hidden;
  white-space: nowrap;
}
.h2h-pipeline i {
  font-style: normal;
  color: #b0b8c0;
}
.h2h-pipeline.purple-flow {
  background: #f7f3fd;
  color: #4f3b78;
}
.h2h-pipeline .peak-exp {
  font-weight: 800;
  color: var(--accent);
  background: rgba(166,108,255,.14);
  padding: 1px 4px;
  border-radius: 3px;
}
.story-vs-divider {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #b0b8c0;
}
.story-vs-divider span {
  font-size: 11px;
  font-weight: 800;
}
.story-vs-divider small {
  font-size: 7.5px;
  color: var(--accent);
  font-weight: 750;
}
.story-pillars-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.story-pillar {
  padding: 7px 9px;
  border: 1px solid #eef0f3;
  border-radius: 10px;
  background: #fbfcfd;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.pillar-header {
  display: flex;
  flex-direction: column;
}
.pillar-num {
  font-size: 7.5px;
  font-weight: 800;
  letter-spacing: .6px;
  color: #8c949c;
}
.story-pillar h5 {
  margin: 1px 0 0;
  font-size: 10.5px;
  font-weight: 750;
  color: var(--ink);
  line-height: 1.2;
}
.pillar-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.contrast-row {
  padding: 4px 6px;
  border-radius: 6px;
  background: #f4f6f8;
}
.contrast-row.direct {
  border-left: 2px solid #5d7fbd;
}
.contrast-row.meta {
  background: #f7f3fd;
  border-left: 2px solid var(--accent);
}
.row-label {
  display: block;
  font-size: 7.5px;
  font-weight: 800;
  margin-bottom: 2px;
}
.contrast-row.direct .row-label {
  color: #5d7fbd;
}
.contrast-row.meta .row-label {
  color: var(--accent);
}
.fact-list {
  display: flex;
  flex-direction: column;
  gap: 2.5px;
}
.fact-item {
  font-size: 9.1px;
  color: #4a5159;
  line-height: 1.22;
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.fact-item b {
  color: var(--ink);
}
.fact-tag {
  font-size: 6.8px;
  font-weight: 800;
  text-transform: uppercase;
  padding: 0px 3px;
  border-radius: 2px;
  background: #e2e6eb;
  color: #5a626a;
  flex-shrink: 0;
  line-height: 1.3;
}
.contrast-row.meta .fact-tag {
  background: #ebdffd;
  color: #6a3ab2;
}
.fact-tag.bug {
  background: #fee2e2;
  color: #b91c1c;
}
.fact-tag.verified {
  background: #dcfce7;
  color: #15803d;
}
.story-takeaway-full {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 6px 12px;
  border-radius: 8px;
  background: #fbf9fe;
  border: 1px solid color-mix(in srgb, var(--accent) 22%, #e6e6e8);
}
.takeaway-pill {
  font-size: 7.5px;
  font-weight: 800;
  color: #fff;
  background: var(--accent);
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: .5px;
  flex-shrink: 0;
}
.story-takeaway-full p {
  margin: 0 !important;
  font-size: 9.6px;
  color: #4a5159;
  line-height: 1.3;
}
.token-hero-box { display: flex; align-items: center; gap: 26px; margin-top: 8px; padding: 14px 22px; background: #fdfaf6; border: 1px solid color-mix(in srgb, var(--accent) 24%, #e6e6e8); border-radius: 14px; }
.token-hero-left { display: flex; flex-direction: column; align-items: flex-start; flex-shrink: 0; }
.token-amount { font-size: 42px; line-height: 1; color: var(--accent); letter-spacing: -1.4px; font-weight: 800; }
.token-caption { font-size: 10px; font-weight: 750; color: #7d7d82; letter-spacing: .6px; margin-top: 4px; text-transform: uppercase; }
.token-hero-right { flex: 1; border-left: 1px solid color-mix(in srgb, var(--accent) 20%, #e6e6e8); padding-left: 22px; }
.token-thesis { margin: 0 !important; font-size: 15px; font-weight: 700; color: var(--ink); line-height: 1.35; }
.token-tags { display: flex; align-items: center; gap: 7px; margin-top: 6px; font-size: 11px; color: #6b7280; font-family: var(--deck-mono); }
.token-tags i { font-style: normal; color: #c4c7cc; }
.resource-cards.three-cards { display: grid; grid-template-columns: 1.15fr 1fr 1fr; gap: 14px; margin-top: 16px; }
.resource-cards > div { padding: 15px 16px 13px; border: 1px solid #e6e6e8; border-radius: 14px; background: #fbfcfd; display: flex; flex-direction: column; }
.resource-label { display: block; color: var(--accent); font-size: 9.5px; font-weight: 800; letter-spacing: 1.1px; }
.resource-cards strong { display: block; margin-top: 5px; color: var(--ink); font-size: 14px; line-height: 1.25; font-weight: 750; }
.resource-cards p { margin: 6px 0 0; color: #727981; font-size: 11.5px; line-height: 1.35; }
.card-body-tokenmaxxing { height: 100%; display: flex; flex-direction: column; }
.card-body-tokenmaxxing .token-hero-box { min-height: 104px; }
.card-body-tokenmaxxing .resource-cards.three-cards { flex: 1; min-height: 158px; }
.card-body-tokenmaxxing .resource-cards > div { justify-content: center; padding: 19px 16px 17px; }
.card-body-tokenmaxxing .boundary { margin-top: auto; padding-top: 14px; }
.record-line { display: flex; gap: 20px; align-items: center; margin-bottom: 22px; font-size: 22px; font-weight: 700; color: var(--accent); }
.record-line i { font-style: normal; color: #b4bac1; }
.card-body dl { display: grid; grid-template-columns: 145px 1fr; gap: 14px 18px; }
.card-body dt { font-weight: 750; color: var(--ink); }
.card-body dd { margin: 0; }
.card-body pre { padding: 16px; background: #f5f7f9; border-radius: 10px; font-size: 12px; white-space: pre-wrap; }
.repo-address { font-weight: 700; }
</style>
