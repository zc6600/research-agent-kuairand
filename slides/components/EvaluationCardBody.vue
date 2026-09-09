<script setup lang="ts">
import EvaluationScoreBars from './EvaluationScoreBars.vue'
import EvaluationTrajectory from './EvaluationTrajectory.vue'
import EvaluationTokenScoreChart from './EvaluationTokenScoreChart.vue'
import EvaluationPerformanceToken from './EvaluationPerformanceToken.vue'
withDefaults(defineProps<{ card: string; resultPage?: 1 | 2 }>(), { resultPage: 1 })
</script>

<template>
  <div class="card-body" :class="`card-body-${card}`">
    <template v-if="card === 'result' && resultPage === 1">
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

    <template v-else-if="card === 'result' && resultPage === 2">
      <EvaluationPerformanceToken />
    </template>

    <template v-else-if="card === 'trajectory'">
      <EvaluationTrajectory />
    </template>

    <template v-else-if="card === 'robustness'">
      <div class="recovery-hero">
        <span class="eyeline">TWO-TIER ROBUSTNESS / EMPIRICAL EVIDENCE</span>
        <strong>Runtime self-healing & code-level Meta gatekeeping.</strong>
        <p>Robust research requires both execution-level crash recovery and epistemic defense against false breakthroughs.</p>
      </div>
      <div class="two-tier-grid">
        <div class="tier-card">
          <div>
            <span class="tier-badge">TIER 1 · SCIENTIST SELF-HEALING</span>
            <h4>Runtime Traceback Auto-Recovery</h4>
            <p class="tier-desc">During Cycle 1, evidence writing failed on <code>numpy.float32</code> metrics. The Scientist parsed the traceback, patched scalar serialization, and completed the rerun without human intervention.</p>
            <div class="recovery-steps-mini"><div><b>01</b><span>Preserve</span></div><div><b>02</b><span>Patch</span></div><div><b>03</b><span>Rerun</span></div></div>
          </div>
          <small class="tier-meta">Cycle 1 telemetry · Zero human intervention · Retained submission</small>
        </div>
        <div class="tier-card">
          <div>
            <span class="tier-badge">TIER 2 · META EPISTEMIC GATEKEEPING</span>
            <h4>Audit Proxy Integrity & Reject Spurious State</h4>
            <p class="tier-desc">In one experiment, the Scientist claimed BPR beat BCE on a medium proxy. META audited <code>system/data.py</code> line-by-line, caught <code>UNK</code> user feature distortion, and blocked State promotion.</p>
            <div class="audit-quote"><em>“medium mode samples complete train-user groups but scores unfiltered validation... no State adoption or promotion is warranted.”</em></div>
          </div>
          <small class="tier-meta">Experiment audit receipt · State boundary guarded</small>
        </div>
      </div>
      <p class="boundary">Empirical receipts archived under <code>docs/evidence/meta_audit/</code> (proxy integrity audit & boundary enforcement).</p>
    </template>

    <template v-else-if="card === 'comparison'">
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
.card-body .boundary { padding-left: 12px; border-left: 2px solid var(--accent); color: #727981; font-size: 11.5px; line-height: 1.42; margin-top: 10px; }
.recovery-hero strong, .token-hero strong { display: block; margin-top: 6px; color: var(--accent); font-size: 25px; line-height: 1.08; letter-spacing: -.7px; }
.recovery-hero p, .token-hero p { max-width: 650px; }
.two-tier-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 12px; }
.tier-card { padding: 12px 14px; border: 1px solid #e6e6e8; border-radius: 12px; background: #fbfcfd; display: flex; flex-direction: column; justify-content: space-between; }
.tier-badge { font-size: 9.5px; font-weight: 800; letter-spacing: 0.8px; color: var(--accent); }
.tier-card h4 { margin: 4px 0 6px; font-size: 13.5px; color: var(--ink); font-weight: 750; }
.tier-desc { font-size: 11.5px; color: #545c64; line-height: 1.35; margin: 0 0 8px; }
.recovery-steps-mini { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 6px 0 8px; text-align: center; background: #f0f2f5; padding: 6px 4px; border-radius: 6px; }
.recovery-steps-mini b { font-size: 10px; color: var(--accent); display: block; }
.recovery-steps-mini span { font-size: 10.5px; color: var(--ink); font-weight: 600; }
.audit-quote { padding: 6px 10px; border-left: 2px solid var(--accent); background: #f3f5f7; border-radius: 0 6px 6px 0; margin: 6px 0 8px; }
.audit-quote em { font-size: 10px; color: #434a52; font-style: italic; line-height: 1.3; display: block; }
.tier-meta { font-size: 9.5px; color: #7d7d82; margin-top: auto; padding-top: 6px; border-top: 1px dashed #e6e6e8; }
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
