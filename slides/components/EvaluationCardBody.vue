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

          <div class="tier-foot mono">Cycle 1 telemetry · Zero human intervention · Retained submission</div>
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

          <div class="tier-foot mono">Experiment audit receipt · State boundary guarded · UNK leak blocked</div>
        </div>
      </div>

      <p class="boundary">Empirical receipts preserved: runtime self-healing telemetry and independent code-level proxy audits.</p>
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
            <span>02</span> TRAJECTORY DIVERGENCE · 01 vs 03
          </button>
        </div>
        <span class="comparison-tab-hint mono">
          {{ comparisonPage === 0 ? 'GEMINI 3.7 FLASH ABLATION' : 'HISTORY SHAPES SEARCH · TRAJECTORY COMPARISON' }}
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
          <div class="arch-score">0.6046</div>
            <p>Single-agent 2h run.</p>
          </div>
          <span class="arch-arrow">→</span>
          <div class="arch-step">
            <span class="arch-label">02 · SUBAGENTS</span>
            <strong>Antigravity + delegated subagents</strong>
          <div class="arch-score">0.6047</div>
            <p>Broader delegation, no persistent Meta layer.</p>
          </div>
          <span class="arch-arrow">→</span>
          <div class="arch-step winner">
            <span class="arch-label">03 · META-SCIENTIST</span>
            <strong>Meta-Scientist + Antigravity</strong>
          <div class="arch-score">0.6052</div>
            <p>Persistent world memory + fresh Scientist reset.</p>
          </div>
        </div>

        <div class="comparison-chart-shell">
          <EvaluationTokenScoreChart />
        </div>
      </template>

      <template v-else>
        <div class="comp-story-container">
          <!-- TWO-COLUMN FACTUAL TRAJECTORY BREAKDOWN -->
          <div class="factual-h2h-grid">
            <!-- 01 DIRECT FACTUAL TRAJECTORY -->
            <div class="factual-card direct-card">
              <div class="factual-card-header">
                <div>
                  <span class="factual-badge blue mono">01 · DIRECT AGENT TRAJECTORY</span>
                  <h4>Horizontal Paradigm Hopping</h4>
                </div>
                <div class="factual-score-box">
                  <strong class="mono">0.6045803</strong>
                  <small class="mono">2h UNBROKEN RUN</small>
                </div>
              </div>

              <div class="factual-steps">
                <div class="step-row">
                  <span class="step-idx mono">01</span>
                  <div class="step-info">
                    <strong>FM Baseline</strong>
                    <span>5-field tabular reference baseline</span>
                  </div>
                  <span class="step-metric mono">0.6016000</span>
                </div>
                <div class="step-row">
                  <span class="step-idx mono">02</span>
                  <div class="step-info">
                    <strong>8-Field Interaction</strong>
                    <span>Cross-features added; gains quickly plateaued</span>
                  </div>
                  <span class="step-metric mono">0.6038000</span>
                </div>
                <div class="step-row pivot">
                  <span class="step-idx mono">03</span>
                  <div class="step-info">
                    <strong>BPR Pairwise Ranking</strong>
                    <span>Plateaued → abandoned FM entirely; pivoted to ranking</span>
                  </div>
                  <span class="step-metric drop mono">0.6021000</span>
                </div>
                <div class="step-row pivot">
                  <span class="step-idx mono">04</span>
                  <div class="step-info">
                    <strong>DeepFM Neural Net</strong>
                    <span>BPR dropped → abandoned ranking; pivoted to MLP/neural</span>
                  </div>
                  <span class="step-metric mono">0.6045803</span>
                </div>
                <div class="step-row pivot">
                  <span class="step-idx mono">05</span>
                  <div class="step-info">
                    <strong>Multi-Task DeepFM</strong>
                    <span>DeepFM plateaued → added multi-task heads; regressed</span>
                  </div>
                  <span class="step-metric drop mono">0.6043000</span>
                </div>
              </div>

              <div class="factual-card-footer blue">
                <span class="foot-tag mono">FACT</span>
                <span>Pivoted across 5 disjoint model classes in 2h. Zero hyperparameter or learning rate tuning.</span>
              </div>
            </div>

            <!-- 03 META-SCIENTIST FACTUAL TRAJECTORY -->
            <div class="factual-card meta-card">
              <div class="factual-card-header">
                <div>
                  <span class="factual-badge purple mono">03 · META-SCIENTIST TRAJECTORY</span>
                  <h4>Vertical DIN Deep-Dive</h4>
                </div>
                <div class="factual-score-box">
                  <strong class="mono purple">0.6052000</strong>
                  <small class="mono purple">2 CYCLES · RESET</small>
                </div>
              </div>

              <div class="factual-steps">
                <div class="step-row">
                  <span class="step-idx purple mono">C1</span>
                  <div class="step-info">
                    <strong>Sequence Signal Confirmed</strong>
                    <span>User watch sequence proven dominant driver</span>
                  </div>
                  <span class="step-metric purple mono">SIGNAL</span>
                </div>
                <div class="step-row handoff">
                  <span class="step-idx purple mono">↻</span>
                  <div class="step-info">
                    <strong>Meta Handoff + Fresh Reset</strong>
                    <span>Insight saved in <code>State.md</code>; fresh Scientist</span>
                  </div>
                  <span class="step-metric purple mono">RESET</span>
                </div>
                <div class="step-row">
                  <span class="step-idx purple mono">E7</span>
                  <div class="step-info">
                    <strong>Multi-Facet DIN</strong>
                    <span>Target Attention over video, author & tags</span>
                  </div>
                  <span class="step-metric purple mono">0.6048100</span>
                </div>
                <div class="step-row peak">
                  <span class="step-idx purple mono">E8</span>
                  <div class="step-info">
                    <strong>Item DIN + Cosine Anneal</strong>
                    <span>Item sequence pooling & LR decay (Peak)</span>
                  </div>
                  <span class="step-metric peak mono">0.6052000</span>
                </div>
                <div class="step-row">
                  <span class="step-idx purple mono">E9</span>
                  <div class="step-info">
                    <strong>DualSeq Attention</strong>
                    <span>Decoupled short vs long-term sequence</span>
                  </div>
                  <span class="step-metric purple mono">GAUC 0.6725</span>
                </div>
              </div>

              <div class="factual-card-footer purple">
                <span class="foot-tag purple mono">FACT</span>
                <span>Locked onto 1 proven hypothesis. 4 disciplined iterations pushing Target Attention from coarse to fine.</span>
              </div>
            </div>
          </div>

          <!-- SUMMARY BAR: WHY HISTORY SHAPES SEARCH -->
          <div class="factual-summary-box">
            <div class="summary-head mono">
              <span class="summary-label">SUMMARY</span>
              <strong>HOW HISTORY SHAPES SEARCH</strong>
            </div>
            <div class="summary-body">
              <div class="summary-side">
                <span class="side-pill blue mono">01 DIRECT AGENT</span>
                <p><b>Context as Cognitive Baggage:</b> In an unbroken thread, past failure traces create cognitive inertia. Stalled gains prompt frantic jumps to new model classes rather than diagnosing bottlenecks.</p>
              </div>
              <div class="summary-divider"></div>
              <div class="summary-side">
                <span class="side-pill purple mono">03 META-SCIENTIST</span>
                <p><b>Context as Scientific Leverage:</b> Externalizing memory into <code>State.md</code> frees the fresh Scientist from historical code debt, enabling focused, vertical refinement to peak score.</p>
              </div>
            </div>
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

.card-body-robustness {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.robustness-intro { margin: 0 0 11px; color: #5a646e; font-size: 13.5px; line-height: 1.38; max-width: 860px; }
.robustness-intro b { color: var(--ink); font-weight: 700; }
.card-body-robustness .two-tier-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; flex: 1; margin-bottom: 8px; }
.card-body-robustness .tier-card { padding: 14px 17px 12px; border: 1px solid #e4e7eb; border-radius: 14px; background: #fbfcfd; display: flex; flex-direction: column; justify-content: space-between; }
.tier-head { border-bottom: 1px solid #edf0f3; padding-bottom: 7px; }
.tier-badge { font-family: var(--mono); font-size: 9px; font-weight: 700; letter-spacing: 0.8px; color: var(--accent); }
.tier-card h4 { margin: 3px 0 1px; font-size: 15px; color: var(--ink); font-weight: 750; letter-spacing: -0.2px; }
.tier-subhead { display: block; font-size: 10.5px; color: #838c96; }
.tier-flow { display: flex; flex-direction: column; gap: 7px; margin: 6px 0; }
.flow-item { display: grid; grid-template-columns: 82px 1fr; align-items: baseline; gap: 8px; font-size: 11.5px; line-height: 1.32; padding: 6px 9px; border-radius: 6px; background: #f5f7f9; }
.flow-item.result { background: #edf6f0; border: 1px solid #d0e8d7; }
.flow-label { font-family: var(--mono); font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #6a7480; }
.flow-item.result .flow-label { color: #247346; }
.flow-item p { margin: 0; color: #434c56; }
.flow-item.result p { color: #1a4f30; }
.flow-item code { font-family: var(--mono); font-size: 10.5px; padding: 1px 4px; background: rgba(0,0,0,0.05); border-radius: 3px; }
.tier-foot { font-size: 8.8px; color: #8c949e; letter-spacing: 0.35px; padding-top: 7px; border-top: 1px dashed #e6e9ed; }
.card-body-robustness .boundary { margin-top: auto; padding-top: 8px; }
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
  gap: 7px;
}
.factual-h2h-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 10px;
  align-items: stretch;
  width: 100%;
  box-sizing: border-box;
}
.factual-card {
  padding: 8px 11px 7px;
  border: 1px solid #e6e6e8;
  border-radius: 12px;
  background: #fbfcfd;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
  box-sizing: border-box;
}
.factual-card.direct-card {
  border-color: #dbe4f0;
}
.factual-card.meta-card {
  border-color: color-mix(in srgb, var(--accent) 45%, #e6e6e8);
  background: linear-gradient(180deg, #ffffff, #fcfaff);
  box-shadow: 0 2px 10px rgba(166,108,255,.05);
}
.factual-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
  padding-bottom: 4px;
  border-bottom: 1px solid #eef1f4;
}
.factual-badge {
  font-size: 8px;
  font-weight: 800;
  letter-spacing: .5px;
  display: block;
}
.factual-badge.blue {
  color: #5d7fbd;
}
.factual-badge.purple {
  color: var(--accent);
}
.factual-card-header h4 {
  margin: 1px 0 0;
  font-size: 11.5px;
  font-weight: 750;
  color: var(--ink);
}
.factual-score-box {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.factual-score-box strong {
  font-size: 16px;
  font-weight: 800;
  color: #434a52;
  letter-spacing: -.5px;
  line-height: 1.1;
}
.factual-score-box strong.purple {
  color: var(--accent);
}
.factual-score-box small {
  font-size: 7.5px;
  font-weight: 750;
  color: #9aa0a6;
  letter-spacing: .4px;
}
.factual-score-box small.purple {
  color: color-mix(in srgb, var(--accent) 70%, #9aa0a6);
}
.factual-steps {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin: 2px 0 4px;
}
.step-row {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 3px 6px;
  background: #f4f6f8;
  border-radius: 6px;
}
.direct-card .step-row {
  border-left: 2px solid #5d7fbd;
}
.direct-card .step-row.pivot {
  border-left-color: #e98238;
}
.meta-card .step-row {
  background: #f7f3fd;
  border-left: 2px solid color-mix(in srgb, var(--accent) 60%, transparent);
}
.meta-card .step-row.handoff {
  background: #f1eafe;
  border-left-color: var(--accent);
}
.meta-card .step-row.peak {
  background: #eedeff;
  border-left: 2.5px solid var(--accent);
  box-shadow: 0 1px 4px rgba(166,108,255,.12);
}
.step-idx {
  font-size: 7.5px;
  font-weight: 800;
  color: #5d7fbd;
  width: 14px;
  flex-shrink: 0;
  text-align: center;
}
.step-idx.purple {
  color: var(--accent);
}
.step-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: baseline;
  gap: 5px;
}
.step-info strong {
  font-size: 9.6px;
  font-weight: 750;
  color: var(--ink);
  white-space: nowrap;
}
.step-info span {
  font-size: 8.5px;
  color: #727981;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.step-info code {
  font-size: 8px;
  background: rgba(0,0,0,.04);
  padding: 0 2px;
  border-radius: 2px;
}
.step-metric {
  font-size: 8.5px;
  font-weight: 750;
  color: #4a5159;
  flex-shrink: 0;
}
.step-metric.drop {
  color: #d9534f;
}
.step-metric.purple {
  color: #6e40b8;
}
.step-metric.peak {
  font-size: 9.5px;
  font-weight: 800;
  color: var(--accent);
}
.factual-card-footer {
  display: flex;
  align-items: baseline;
  gap: 5px;
  padding: 3px 6px;
  border-radius: 5px;
  font-size: 8.4px;
  line-height: 1.25;
}
.factual-card-footer.blue {
  background: #ebf1fa;
  color: #3b5a88;
}
.factual-card-footer.purple {
  background: #f3ecfe;
  color: #563391;
}
.foot-tag {
  font-size: 7px;
  font-weight: 800;
  padding: 1px 4px;
  border-radius: 3px;
  background: #5d7fbd;
  color: #fff;
  flex-shrink: 0;
}
.foot-tag.purple {
  background: var(--accent);
}
.factual-summary-box {
  padding: 7px 12px;
  border-radius: 10px;
  background: #fbf9fe;
  border: 1px solid color-mix(in srgb, var(--accent) 24%, #e6e6e8);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.summary-head {
  display: flex;
  align-items: center;
  gap: 7px;
}
.summary-label {
  font-size: 7px;
  font-weight: 800;
  color: #fff;
  background: var(--accent);
  padding: 1px 5px;
  border-radius: 3px;
  letter-spacing: .5px;
}
.summary-head strong {
  font-size: 8.5px;
  font-weight: 800;
  color: var(--accent);
  letter-spacing: .6px;
}
.summary-body {
  display: grid;
  grid-template-columns: 1fr 1px 1fr;
  align-items: center;
  gap: 12px;
}
.summary-divider {
  height: 100%;
  background: color-mix(in srgb, var(--accent) 18%, #e6e6e8);
}
.summary-side {
  display: flex;
  align-items: flex-start;
  gap: 7px;
}
.side-pill {
  font-size: 7px;
  font-weight: 800;
  padding: 1.5px 5px;
  border-radius: 3px;
  flex-shrink: 0;
  letter-spacing: .4px;
  margin-top: 1px;
}
.side-pill.blue {
  background: #ebf1fa;
  color: #4d6ea6;
}
.side-pill.purple {
  background: #f1e9fe;
  color: var(--accent);
}
.summary-side p {
  margin: 0 !important;
  font-size: 9.3px;
  color: #4a5159;
  line-height: 1.3;
}
.summary-side b {
  color: var(--ink);
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
