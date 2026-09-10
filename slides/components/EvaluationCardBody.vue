<script setup lang="ts">
import { computed } from 'vue'
import EvaluationScoreBars from './EvaluationScoreBars.vue'
import EvaluationTrajectory from './EvaluationTrajectory.vue'
import EvaluationTokenScoreChart from './EvaluationTokenScoreChart.vue'

const props = withDefaults(defineProps<{ card: string; comparisonPage?: 0 | 1 }>(), { comparisonPage: 0 })
const emit = defineEmits<{ 'update:comparisonPage': [page: 0 | 1] }>()
const comparisonPage = computed(() => props.comparisonPage)
const selectComparisonPage = (page: 0 | 1) => {
  emit('update:comparisonPage', page)
}
</script>

<template>
  <div class="card-body" :class="`card-body-${card}`">
    <template v-if="card === 'result'">
      <div class="result-summary">
        <div class="result-hero-pane">
          <span class="eyeline mono">PUBLIC-VALIDATION PRIMARY COMPARISON</span>
          <div class="score-contrast-row">
            <div class="score-pill baseline-pill">
              <span class="pill-tag mono">BASELINE</span>
              <strong class="pill-num mono">0.6016310</strong>
              <small class="pill-desc">Reproduced FM</small>
            </div>
            <div class="score-pill-divider">
              <span class="pill-arrow" aria-hidden="true">→</span>
              <span class="pill-gain mono">+0.0043053</span>
              <span class="pill-pct mono">+0.72%</span>
            </div>
            <div class="score-pill ours-pill">
              <span class="pill-tag mono">OUR AGENT</span>
              <strong class="pill-num highlight-num mono">0.6059363</strong>
              <small class="pill-desc">46-field 8-seed FM</small>
            </div>
          </div>
          <div class="model-spec-note">
            <span>46 feature interactions · 8-seed FM ensemble · Rank 16 · NumPy / CPU</span>
          </div>
        </div>
        <EvaluationScoreBars />
      </div>

      <!-- Metric Comparison Table with explicit Delta column -->
      <table class="result-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Reproduced FM Baseline</th>
            <th>Our Agent (SciOdyssey)</th>
            <th class="col-gain">Absolute Gain (Δ)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="metric-name">GAUC</td>
            <td class="mono">0.6671070</td>
            <td class="mono ours-cell">0.6728421</td>
            <td class="mono gain-cell"><strong>+0.0057351</strong> <span class="gain-pct">(+0.86%)</span></td>
          </tr>
          <tr>
            <td class="metric-name">nDCG@5</td>
            <td class="mono">0.5361550</td>
            <td class="mono ours-cell">0.5390304</td>
            <td class="mono gain-cell"><strong>+0.0028754</strong> <span class="gain-pct">(+0.54%)</span></td>
          </tr>
          <tr class="row-primary-win">
            <td class="metric-name"><strong>Primary</strong></td>
            <td class="mono">0.6016310</td>
            <td class="mono ours-cell win-cell"><strong>0.6059363</strong></td>
            <td class="mono gain-cell win-gain"><strong>+0.0043053</strong> <span class="gain-pct">(+0.72%)</span></td>
          </tr>
        </tbody>
      </table>

      <!-- Resource Consumption Strip -->
      <div class="resource-ledger-strip">
        <div class="res-strip-item">
          <span class="res-strip-label mono">COMPUTE</span>
          <strong class="res-strip-val">0 GPU-hours</strong>
          <span class="res-strip-detail">100% CPU NumPy on MacBook M2</span>
        </div>
        <div class="res-strip-item">
          <span class="res-strip-label mono">LLM TOKENS</span>
          <strong class="res-strip-val">48.24M</strong>
          <span class="res-strip-detail">4.02M non-cache across 4 cycles</span>
        </div>
        <div class="res-strip-item">
          <span class="res-strip-label mono">AUTONOMOUS SEARCH</span>
          <strong class="res-strip-val">4 cycles · 13 exps</strong>
          <span class="res-strip-detail">7 Full evaluations · 0 interventions</span>
        </div>
      </div>

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
            @click="selectComparisonPage(0)"
          >
            <span>01</span> ABLATION BENCHMARK
          </button>
          <button
            type="button"
            class="comp-tab-btn"
            :class="{ active: comparisonPage === 1 }"
            role="tab"
            :aria-selected="comparisonPage === 1"
            @click="selectComparisonPage(1)"
          >
            <span>02</span> TRAJECTORY DIVERGENCE
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
          <div class="trajectory-deck-grid">
            <!-- LEFT COLUMN: 01 DIRECT AGENT -->
            <div class="trajectory-col direct-col">
              <div class="trajectory-col-kicker mono">01 · DIRECT AGENT (2h UNBROKEN RUN)</div>
              <h3>Mechanism pivots</h3>
              <div class="trajectory-visual direct-visual">
                <svg class="deck-connections" viewBox="0 0 390 170" preserveAspectRatio="none" aria-hidden="true">
                  <defs>
                    <marker id="deck-arrow-blue" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto" markerUnits="userSpaceOnUse">
                      <path d="M0,1 L5,3 L0,5 Z" fill="#60a5fa" />
                    </marker>
                  </defs>
                  <!-- Bouncing / hopping zigzag lines with arrows -->
                  <line x1="66" y1="106" x2="86" y2="44" stroke="#93c5fd" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#deck-arrow-blue)"></line>
                  <line x1="146" y1="44" x2="166" y2="106" stroke="#93c5fd" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#deck-arrow-blue)"></line>
                  <line x1="220" y1="106" x2="242" y2="44" stroke="#93c5fd" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#deck-arrow-blue)"></line>
                  <line x1="298" y1="44" x2="318" y2="106" stroke="#93c5fd" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#deck-arrow-blue)"></line>
                </svg>

                <div class="deck-node direct-node node-d1">FM<small>0.6016</small></div>
                <div class="deck-node direct-node node-d2">8-field<br>Poly<small>0.6038</small></div>
                <div class="deck-node direct-node node-d3 drop">BPR<br>loss<small>0.6021</small></div>
                <div class="deck-node direct-node node-d4">DeepFM<small>0.60458</small></div>
                <div class="deck-node direct-node node-d5 drop">MT-DeepFM<small>0.6043</small></div>

                <div class="deck-visual-label mono">HORIZONTAL HOPPING · 5 PARADIGMS · NEVER GOES DEEP</div>
              </div>
              <p class="trajectory-copy">Switches model classes when gains stall; confuses variety with exploration.</p>
            </div>

            <!-- RIGHT COLUMN: 03 META-SCIENTIST -->
            <div class="trajectory-col meta-col">
              <div class="trajectory-col-kicker mono">03 · META-SCIENTIST (2 CYCLES · WINNER)</div>
              <h3>Pivot, then vertical deep-dive</h3>
              <div class="trajectory-visual meta-visual">
                <svg class="deck-connections" viewBox="0 0 390 170" preserveAspectRatio="none" aria-hidden="true">
                  <defs>
                    <marker id="deck-arrow-purple" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto" markerUnits="userSpaceOnUse">
                      <path d="M0,1 L5,3 L0,5 Z" fill="#a855f7" />
                    </marker>
                    <marker id="deck-arrow-dive" markerWidth="7" markerHeight="7" refX="3.5" refY="6" orient="auto" markerUnits="userSpaceOnUse">
                      <path d="M1,0 L3.5,5 L6,0 Z" fill="#a855f7" />
                    </marker>
                  </defs>
                  <!-- 1. Horizontal direction pivot arrow -->
                  <line x1="118" y1="36" x2="138" y2="36" stroke="#c084fc" stroke-width="2" marker-end="url(#deck-arrow-purple)"></line>

                  <!-- 2. Vertical dive into mechanism depth -->
                  <line x1="197" y1="58" x2="197" y2="90" stroke="#a855f7" stroke-width="2.5" marker-end="url(#deck-arrow-dive)"></line>

                  <!-- 3. Drive forward to global peak -->
                  <line x1="256" y1="117" x2="274" y2="117" stroke="#a855f7" stroke-width="2" marker-end="url(#deck-arrow-purple)"></line>
                </svg>

                <div class="deck-node meta-node node-m1">
                  <strong>Cycle 1 Explore</strong>
                  <small>FM Baseline · 0.6030</small>
                </div>

                <div class="deck-node meta-node node-m2 pivot-node">
                  <span class="pivot-kicker mono">1. PIVOT</span>
                  <strong>↻ State Handoff</strong>
                  <small>Prunes Noise · Locks DIN</small>
                </div>

                <div class="dive-pill mono">▼ 2. DIVE IN</div>

                <div class="deck-node meta-node node-m3">
                  <strong>E007 Multi-Facet</strong>
                  <small>DIN Architecture · 0.6048</small>
                </div>

                <div class="deck-node meta-node node-m4 winner">
                  <strong class="winner-title mono">E008 ★ WINNER</strong>
                  <span class="winner-name">DIN + Cosine Target</span>
                  <div class="winner-score mono">0.6052000</div>
                </div>

                <div class="deck-visual-label purple mono">PIVOT TO DIN THESIS → DIVE IN TO 0.6052 PEAK</div>
              </div>
              <p class="trajectory-copy">Pivots away from dead ends in Cycle 1, then dives deep into Target Attention to unlock the global optimum.</p>
            </div>
          </div>

          <!-- BOTTOM TAKEAWAY BAR -->
          <div class="trajectory-takeaway-bar">
            <span class="takeaway-badge mono">CORE TAKEAWAY</span>
            <p>Same model family (Gemini 3.7 Flash). In an unbroken context, history triggers reactive pivots; in a Meta-Scientist loop, history provides scientific leverage.</p>
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
.result-summary { display: grid; grid-template-columns: 1.25fr 1fr; gap: 20px; align-items: center; margin-bottom: 2px; }

/* Result Hero Comparison Pane */
.result-hero-pane {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.score-contrast-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 3px;
}
.score-pill {
  flex: 1;
  padding: 8px 12px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
}
.baseline-pill {
  border-color: #e2e8f0;
  background: #f8fafc;
}
.ours-pill {
  border-color: color-mix(in srgb, var(--accent, #16803b) 40%, #cbd5e1);
  background: color-mix(in srgb, var(--accent, #16803b) 7%, #ffffff);
  box-shadow: 0 2px 8px color-mix(in srgb, var(--accent, #16803b) 8%, transparent);
}
.pill-tag {
  font-size: 8.5px;
  letter-spacing: 0.8px;
  font-weight: 600;
  color: #7d8590;
}
.ours-pill .pill-tag {
  color: var(--accent, #16803b);
}
.pill-num {
  font-size: 18px;
  line-height: 1.1;
  letter-spacing: -0.4px;
  color: #475569;
  font-weight: 600;
}
.highlight-num {
  color: var(--accent, #16803b);
  font-size: 20px;
  font-weight: 700;
}
.pill-desc {
  font-size: 9px;
  color: #8c95a0;
}
.score-pill-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}
.pill-arrow {
  font-size: 13px;
  color: #94a3b8;
  line-height: 1;
}
.pill-gain {
  font-size: 10.5px;
  font-weight: 700;
  color: #16803b;
  background: #edf7ee;
  border: 1px solid #c9e8cd;
  padding: 1px 5px;
  border-radius: 4px;
  white-space: nowrap;
}
.pill-pct {
  font-size: 9px;
  font-weight: 600;
  color: #16803b;
}
.model-spec-note {
  font-size: 10px;
  color: #7d8590;
  margin-top: 1px;
}

/* Result Table with Explicit Gain */
.result-table {
  width: 100%;
  border-collapse: collapse;
  margin: 6px 0 6px;
  font-size: 11.5px;
}
.result-table th,
.result-table td {
  padding: 4px 8px;
  text-align: left;
  border-bottom: 1px solid #e6e6e8;
}
.result-table th {
  color: #7d7d82;
  font-size: 9.5px;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.result-table .col-gain {
  color: #16803b;
}
.result-table .ours-cell {
  color: #0369a1;
}
.result-table .gain-cell {
  color: #16803b;
}
.result-table .gain-pct {
  font-size: 9.5px;
  color: #16803b;
  opacity: 0.85;
}
.row-primary-win {
  background: color-mix(in srgb, var(--accent, #16803b) 6%, transparent);
}
.row-primary-win td {
  border-bottom: 1.5px solid color-mix(in srgb, var(--accent, #16803b) 35%, #e6e6e8);
}
.win-cell {
  color: var(--accent, #16803b) !important;
  font-weight: 700;
}
.win-gain {
  font-size: 12px;
  font-weight: 700;
}

/* Resource Ledger Strip */
.resource-ledger-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 7px 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 9px;
  margin-top: 6px;
  margin-bottom: 4px;
}
.res-strip-item {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.res-strip-label {
  font-size: 7.5px;
  letter-spacing: 0.7px;
  color: #8c95a0;
  font-weight: 650;
}
.res-strip-val {
  font-size: 12.5px;
  line-height: 1.2;
  color: var(--ink, #111217);
  font-weight: 700;
}
.res-strip-detail {
  font-size: 9px;
  color: #64748b;
  line-height: 1.2;
}

.card-body table { width: 100%; border-collapse: collapse; margin: 10px 0 0; font-size: 12.5px; }
.card-body th, .card-body td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #e6e6e8; }
.card-body th { color: #7d7d82; font-size: 11px; font-weight: 650; }
.card-body .boundary { padding-left: 12px; border-left: 2px solid var(--accent); color: #727981; font-size: 11px; line-height: 1.35; margin-top: 6px; }
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
  gap: 10px;
  height: 100%;
}
.trajectory-deck-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  align-items: stretch;
}
.trajectory-col {
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  border: 1px solid #e6e8eb;
  background: #fbfcfd;
  padding: 10px 14px 9px;
  box-sizing: border-box;
}
.trajectory-col.direct-col {
  border-top: 3.5px solid #5d7fbd;
}
.trajectory-col.meta-col {
  border-top: 3.5px solid var(--accent);
  background: linear-gradient(180deg, #ffffff, #faf7fe);
  box-shadow: 0 4px 18px rgba(166, 108, 255, 0.06);
}
.trajectory-col-kicker {
  font-size: 8.5px;
  font-weight: 800;
  letter-spacing: .7px;
  color: #7d7d82;
  margin-bottom: 2px;
}
.direct-col .trajectory-col-kicker {
  color: #4a6fa5;
}
.meta-col .trajectory-col-kicker {
  color: var(--accent);
}
.trajectory-col h3 {
  margin: 0 0 7px;
  font-size: 15px;
  font-weight: 750;
  color: var(--ink);
  letter-spacing: -.3px;
  line-height: 1.2;
}
.trajectory-visual {
  position: relative;
  height: 170px;
  background: #ffffff;
  border: 1px solid #eef1f5;
  border-radius: 9px;
  overflow: hidden;
}
.meta-col .trajectory-visual {
  background: #ffffff;
  border-color: #ede6fa;
}
.deck-connections {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}
.deck-node {
  position: absolute;
  z-index: 2;
  background: #ffffff;
  border: 1px solid #d0d7de;
  border-radius: 7px;
  padding: 4px 6px;
  text-align: center;
  font-size: 9.5px;
  font-weight: 700;
  line-height: 1.15;
  color: var(--ink);
  box-shadow: 0 2px 5px rgba(27, 31, 36, 0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}
.deck-node small {
  display: block;
  font-size: 8px;
  font-weight: 600;
  color: #656d76;
  margin-top: 2px;
  font-family: var(--deck-mono);
}
.deck-node.direct-node {
  border-color: #cbd5e1;
}
.deck-node.direct-node.drop {
  border-color: #fca5a5;
  background: #fff8f8;
}
.deck-node.direct-node.drop small {
  color: #dc2626;
}
.deck-node.meta-node {
  border-color: #ddd6fe;
}
.deck-node.meta-node.pivot-node {
  border-color: #c084fc;
  background: #fcfaff;
}
.pivot-kicker {
  font-size: 7px;
  font-weight: 800;
  letter-spacing: .5px;
  color: var(--accent);
  background: rgba(166, 108, 255, 0.12);
  padding: 1px 4px;
  border-radius: 3px;
  margin-bottom: 2px;
  display: inline-block;
}
.deck-node.meta-node.winner {
  border: 1.5px solid var(--accent);
  background: linear-gradient(135deg, #ffffff, #f5edff);
  box-shadow: 0 3px 10px rgba(166, 108, 255, 0.16);
  padding: 3px 5px;
  z-index: 3;
}
.deck-node.meta-node.winner .winner-title {
  font-size: 8.5px;
  font-weight: 800;
  color: var(--accent);
  line-height: 1.1;
}
.deck-node.meta-node.winner .winner-name {
  font-size: 7.8px;
  font-weight: 650;
  color: var(--ink);
  line-height: 1.15;
  white-space: nowrap;
}
.winner-score {
  font-size: 8.5px;
  font-weight: 800;
  color: var(--accent);
  margin-top: 1.5px;
  background: rgba(166, 108, 255, 0.14);
  padding: 1px 5px;
  border-radius: 3px;
  line-height: 1.1;
}
.dive-pill {
  position: absolute;
  z-index: 3;
  left: 50.6%;
  top: 67px;
  font-size: 7.5px;
  font-weight: 800;
  letter-spacing: .5px;
  background: #a855f7;
  color: #ffffff;
  padding: 1.5px 5px;
  border-radius: 4px;
  box-shadow: 0 2px 6px rgba(168, 85, 247, 0.2);
  transform: translateX(-50%);
}

.node-d1 { left: 3%; top: 100px; width: 56px; height: 40px; }
.node-d2 { left: 21%; top: 14px; width: 68px; height: 42px; }
.node-d3 { left: 41%; top: 100px; width: 62px; height: 42px; }
.node-d4 { left: 61%; top: 14px; width: 66px; height: 40px; }
.node-d5 { left: 79%; top: 100px; width: 74px; height: 42px; }

.node-m1 { left: 3.5%; top: 14px; width: 104px; height: 44px; }
.node-m2 { left: 36%; top: 14px; width: 114px; height: 44px; }
.node-m3 { left: 36%; top: 94px; width: 114px; height: 46px; }
.node-m4 { left: 71%; top: 94px; width: 98px; height: 46px; }

.deck-visual-label {
  position: absolute;
  bottom: 6px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: .8px;
  color: #8c959f;
  z-index: 2;
  line-height: 1;
}
.deck-visual-label.purple {
  color: var(--accent);
}
.trajectory-copy {
  margin: 6px 0 0 !important;
  font-size: 10.5px;
  line-height: 1.32;
  color: #57606a;
}
.trajectory-takeaway-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  background: #fdfcff;
  border: 1px solid color-mix(in srgb, var(--accent) 24%, #e6e8eb);
  border-radius: 9px;
}
.takeaway-badge {
  font-size: 7.5px;
  font-weight: 800;
  letter-spacing: .5px;
  color: #ffffff;
  background: var(--accent);
  padding: 2.5px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}
.trajectory-takeaway-bar p {
  margin: 0 !important;
  font-size: 10.5px;
  line-height: 1.32;
  color: #424a53;
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
