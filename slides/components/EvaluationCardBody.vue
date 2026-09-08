<script setup lang="ts">
import EvaluationScoreBars from './EvaluationScoreBars.vue'
import EvaluationTrajectory from './EvaluationTrajectory.vue'
import EvaluationTokenScoreChart from './EvaluationTokenScoreChart.vue'
defineProps<{ card: string }>()
</script>

<template>
  <div class="card-body">
    <template v-if="card === 'result'">
      <div class="result-summary">
        <div><span class="eyeline">PUBLIC-VALIDATION PRIMARY</span><strong class="hero-number">0.6059363</strong><p><b>+0.0043363</b> over the official five-field FM</p><small>46 categorical feature interactions · 8-seed FM · rank 16 · NumPy / CPU</small></div>
        <EvaluationScoreBars />
      </div>
      <table><thead><tr><th>Metric</th><th>Official FM</th><th>Our agent</th></tr></thead><tbody><tr><td>GAUC</td><td>0.6674000</td><td>0.6728421</td></tr><tr><td>nDCG@5</td><td>0.5357000</td><td>0.5390304</td></tr><tr><td>Primary</td><td>0.6016000</td><td><b>0.6059363</b></td></tr></tbody></table>
      <p class="boundary">Primary = mean(GAUC, nDCG@5). Verified on the official validation split following challenge protocol.</p>
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
            <div class="recovery-steps-mini">
              <div><b>01</b><span>Preserve</span></div>
              <div><b>02</b><span>Patch</span></div>
              <div><b>03</b><span>Rerun</span></div>
            </div>
          </div>
          <small class="tier-meta">Cycle 1 telemetry · Zero human intervention · Retained submission</small>
        </div>

        <div class="tier-card">
          <div>
            <span class="tier-badge">TIER 2 · META EPISTEMIC GATEKEEPING</span>
            <h4>Audit Proxy Integrity & Reject Spurious State</h4>
            <p class="tier-desc">In run <code>p021</code>, the Scientist claimed BPR beat BCE on a medium proxy. META audited <code>system/data.py</code> line-by-line, caught that train-user sampling with unfiltered validation created <code>UNK</code> user feature distortion and inverted ranking, and blocked State promotion.</p>
            <div class="audit-quote">
              <em>"medium mode samples complete train-user groups but scores unfiltered validation... falsifying proxy use... no State adoption or promotion is warranted."</em>
            </div>
          </div>
          <small class="tier-meta">p021 audit receipt · review-r1.normalized.json · State boundary guarded</small>
        </div>
      </div>

      <p class="boundary">Empirical receipts archived under <code>docs/evidence/meta_audit/</code> (p021 proxy audit & p006 boundary enforcement).</p>
    </template>

    <template v-else-if="card === 'comparison'">
      <div class="comparison-intro"><span class="eyeline">PUBLIC VALIDATION / RECORDED DIRECT-AGENT CONTROLS</span><p>The retained run demonstrates sustained improvement over the recorded direct Codex control under identical benchmark constraints.</p></div>
      <EvaluationTokenScoreChart />
    </template>

    <template v-else-if="card === 'tokenmaxxing'">
      <div class="token-hero"><span class="eyeline">PROJECT-LEVEL RESOURCE ACCOUNTING</span><strong>~$10</strong><p>subscription-equivalent usage from first line of code to final result</p><small>coding · debugging · agent runs · all experiments</small></div>

      <div class="resource-cards">
        <div><span class="resource-label">MODEL</span><strong>One GPT Plus + One Gemini Pro for 7 days</strong><p>Two consumer subscriptions covered the entire research loop.</p></div>
        <div><span class="resource-label">COMPUTE</span><strong>1 × MacBook M2</strong><p>Development and experiments ran on one consumer laptop.</p></div>
      </div>

      <section class="run-telemetry"><h3>Retained-run telemetry</h3><div class="metric-row"><div><strong>48.240M</strong><span>total tokens</span><small>including cache-read input</small></div><div><strong>4.020M</strong><span>non-cache</span><small>input + output</small></div><div><strong>0</strong><span>GPU-hours</span><small>CPU / NumPy training</small></div></div></section>
    </template>
  </div>
</template>

<style scoped>
.card-body { color: #434a52; font-size: 13px; line-height: 1.42; }
.card-body p { margin: 7px 0; }
.card-body section { margin-top: 16px; padding-top: 13px; border-top: 1px solid #e6e6e8; }
.card-body h3 { margin: 0 0 8px; color: var(--ink); font-size: 18px; font-weight: 750; }
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
.recovery-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 14px; }
.recovery-steps > div { padding-top: 10px; border-top: 2px solid color-mix(in srgb, var(--accent) 46%, #e6e6e8); }
.recovery-steps b { display: block; color: var(--accent); font-size: 11px; letter-spacing: 1px; }
.recovery-steps strong { display: block; margin-top: 5px; color: var(--ink); font-size: 14.5px; }
.recovery-steps p { color: #727981; font-size: 11.5px; line-height: 1.35; }
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
.comparison-intro { margin-bottom: 1px; }
.comparison-intro p { margin: 0; color: #646c74; font-size: 12px; }
.token-hero { padding-bottom: 0; }
.token-hero strong { font-size: 40px; letter-spacing: -1.4px; margin-top: 6px; }
.token-hero p { margin: 8px 0 0; font-size: 13.5px; }
.resource-cards { display: grid; grid-template-columns: 1.25fr .75fr; gap: 18px; margin-top: 16px; }
.resource-cards > div { padding: 14px 16px 12px; border: 1px solid #e6e6e8; border-radius: 14px; background: #fbfcfd; }
.resource-label { display: block; color: var(--accent); font-size: 10px; font-weight: 800; letter-spacing: 1.1px; }
.resource-cards strong { display: block; margin-top: 6px; color: var(--ink); font-size: 15px; line-height: 1.25; }
.resource-cards p { margin: 6px 0 0; color: #727981; font-size: 12px; line-height: 1.35; }
.run-telemetry { margin-top: 16px !important; padding-top: 14px !important; }
.metric-row { display: grid; grid-template-columns: 1.15fr 1fr .8fr; gap: 18px; margin-bottom: 4px; }
.metric-row strong { display: block; font-size: 28px; line-height: 1.05; color: var(--accent); letter-spacing: -.9px; }
.metric-row span, .metric-row small { display: block; }
.metric-row span { margin-top: 5px; font-weight: 750; }
.record-line { display: flex; gap: 20px; align-items: center; margin-bottom: 22px; font-size: 22px; font-weight: 700; color: var(--accent); }
.record-line i { font-style: normal; color: #b4bac1; }
.card-body dl { display: grid; grid-template-columns: 145px 1fr; gap: 14px 18px; }
.card-body dt { font-weight: 750; color: var(--ink); }
.card-body dd { margin: 0; }
.card-body pre { padding: 16px; background: #f5f7f9; border-radius: 10px; font-size: 12px; white-space: pre-wrap; }
.repo-address { font-weight: 700; }
</style>
