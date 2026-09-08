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
        <div><span class="eyeline">PUBLIC-VALIDATION PRIMARY</span><strong class="hero-number">0.6059363</strong><p><b>+0.0043363</b> over the official five-field FM</p><small>46 leak-free categorical fields · 8-seed FM · rank 16 · NumPy / CPU</small></div>
        <EvaluationScoreBars />
      </div>
      <table><thead><tr><th>Metric</th><th>Official FM</th><th>Our agent</th></tr></thead><tbody><tr><td>GAUC</td><td>0.6674000</td><td>0.6728421</td></tr><tr><td>nDCG@5</td><td>0.5357000</td><td>0.5390304</td></tr><tr><td>Primary</td><td>0.6016000</td><td><b>0.6059363</b></td></tr></tbody></table>
      <p class="boundary">Primary = mean(GAUC, nDCG@5). Public validation only; hidden-test scoring is organizer-controlled.</p>
      <section><h3>Retained checkpoint</h3><p>E013 kept the strongest valid recipe after seven Full evaluations: a 46-field FM ensemble across eight seeds, evaluated by the unchanged organizer evaluator.</p><div class="two-columns"><div><h4>GAUC</h4><p>0.6728421</p></div><div><h4>nDCG@5</h4><p>0.5390304</p></div></div></section>
    </template>

    <template v-else-if="card === 'trajectory'">
      <EvaluationTrajectory />
      <section><h3>What the search retained</h3><p>Thirteen named experiments included seven Full public-validation evaluations. Medium screens and diagnostics informed the four cycles without replacing the Full evaluator.</p><p>The final checkpoint, E013, retained an 8-seed ensemble with 46 leak-free fields and the unchanged evaluator. The remaining named experiments record the alternatives considered along the way.</p></section>
    </template>

    <template v-else-if="card === 'robustness'">
      <div class="recovery-hero"><span class="eyeline">CYCLE 1 / RECOVERY EVENT</span><strong>Evidence writing failed after evaluation.</strong><p>Training and evaluation had completed, but the evidence writer could not serialize organizer metrics returned as <code>numpy.float32</code>.</p></div>
      <div class="recovery-steps"><div><b>01</b><strong>Preserve</strong><p>Printed measurements stayed in the session output.</p></div><div><b>02</b><strong>Repair</strong><p>The Scientist converted NumPy scalars before JSON serialization.</p></div><div><b>03</b><strong>Rerun</strong><p>The experiment completed again and kept auditable evidence.</p></div></div>
      <section><h3>Where META fits</h3><p>The Scientist owned the code repair. META audited the report against the artifacts and governed what became durable State for the next trajectory.</p><p>No human selected the repair or edited the code. The run recovered its evidence instead of terminating.</p></section>
      <p class="boundary">This is the documented cycle-1 recovery event in <code>research_record/reports/cycle-1.md</code> and <code>docs/FINAL_REPORT.md</code> §4.2.</p>
    </template>

    <template v-else-if="card === 'comparison'">
      <div class="comparison-intro"><span class="eyeline">PUBLIC VALIDATION / RECORDED DIRECT-AGENT CONTROLS</span><p>The retained run sits above the recorded direct Codex control. The chart below is the original P11 evidence figure, moved into this card.</p></div>
      <EvaluationTokenScoreChart />
      <div class="comparison-scores"><div><small>DIRECT CODEX</small><strong>0.6044533</strong><span>provisional control</span></div><i>→</i><div><small>RESEARCH AGENT</small><strong>0.6059363</strong><span>verified retained result</span></div></div>
      <p class="comparison-gain"><b>+0.0014830 Primary</b> above the recorded direct Codex control.</p>
      <p class="boundary">Runs differ in model, budget, and evidence quality. The Codex record remains provisional under its process audit, so this is a recorded control comparison—not a causal proof of architecture superiority.</p>
    </template>

    <template v-else-if="card === 'tokenmaxxing'">
      <div class="token-hero"><span class="eyeline">PROJECT-LEVEL RESOURCE ACCOUNTING</span><strong>~$10</strong><p>subscription-equivalent usage from first line of code to final result</p><small>coding · debugging · agent runs · all experiments</small></div>

      <div class="resource-cards">
        <div><span class="resource-label">MODEL</span><strong>One GPT Plus + One Gemini Pro for 7 days</strong><p>Two consumer subscriptions covered the entire research loop.</p></div>
        <div><span class="resource-label">COMPUTE</span><strong>1 × MacBook M2</strong><p>Development and experiments ran on one consumer laptop.</p></div>
      </div>

      <section class="run-telemetry"><h3>Retained-run telemetry</h3><div class="metric-row"><div><strong>48.240M</strong><span>total tokens</span><small>including cache-read input</small></div><div><strong>4.020M</strong><span>non-cache</span><small>input + output</small></div><div><strong>0</strong><span>GPU-hours</span><small>CPU / NumPy training</small></div></div></section>

      <div class="token-thesis"><span>More tokens were used.</span><strong>That is not our claim.</strong><p>The controls used fewer tokens. Our claim is better research decisions with a verified audit trail—not a token-efficiency frontier and not “more tokens means better.”</p></div>
      <p class="boundary">~$10 is the estimated subscription-equivalent usage across the entire project, not cost per experiment. LLM usage and local compute are reported separately.</p>
    </template>
  </div>
</template>

<style scoped>
.card-body { color: #434a52; font-size: 14px; line-height: 1.5; }
.card-body p { margin: 10px 0; }
.card-body section { margin-top: 25px; padding-top: 20px; border-top: 1px solid #e6e6e8; }
.card-body h3 { margin: 0 0 12px; color: var(--ink); font-size: 21px; font-weight: 750; }
.card-body h4 { margin: 0 0 6px; color: var(--ink); font-size: 16px; font-weight: 750; }
.card-body small { color: #7d7d82; font-size: 11px; }
.eyeline { font-size: 10px; letter-spacing: 1px; color: #7d7d82; }
.hero-number { display: block; font-size: 48px; line-height: 1.15; letter-spacing: -2px; color: var(--accent); }
.result-summary { display: grid; grid-template-columns: 1.1fr 1fr; gap: 28px; align-items: center; }
.card-body table { width: 100%; border-collapse: collapse; margin: 16px 0 0; font-size: 13px; }
.card-body th, .card-body td { text-align: left; padding: 9px 10px; border-bottom: 1px solid #e6e6e8; }
.card-body th { color: #7d7d82; font-size: 11px; font-weight: 650; }
.card-body .boundary { padding-left: 12px; border-left: 2px solid var(--accent); color: #727981; font-size: 12px; line-height: 1.5; margin-top: 16px; }
.recovery-hero strong, .token-hero strong { display: block; margin-top: 8px; color: var(--accent); font-size: 30px; line-height: 1.08; letter-spacing: -.8px; }
.recovery-hero p, .token-hero p { max-width: 650px; }
.recovery-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 24px; }
.recovery-steps > div { padding-top: 12px; border-top: 2px solid color-mix(in srgb, var(--accent) 46%, #e6e6e8); }
.recovery-steps b { display: block; color: var(--accent); font-size: 12px; letter-spacing: 1px; }
.recovery-steps strong { display: block; margin-top: 6px; color: var(--ink); font-size: 16px; }
.recovery-steps p { color: #727981; font-size: 12px; line-height: 1.4; }
.comparison-intro { margin-bottom: 12px; }
.comparison-intro p { color: #646c74; font-size: 13px; }
.comparison-scores { display: grid; grid-template-columns: 1fr auto 1fr; align-items: end; gap: 18px; margin-top: 14px; }
.comparison-scores div { padding-top: 10px; border-top: 2px solid color-mix(in srgb, var(--accent) 44%, #e6e6e8); }
.comparison-scores small, .comparison-scores span { display: block; color: #7d7d82; font-size: 10px; letter-spacing: .75px; }
.comparison-scores strong { display: block; color: var(--accent); font-size: 34px; line-height: 1.05; letter-spacing: -1px; }
.comparison-scores i { padding-bottom: 16px; color: #b8bec4; font-size: 24px; font-style: normal; }
.comparison-gain { margin-top: 10px !important; }
.token-hero { padding-bottom: 5px; }
.token-hero strong { font-size: 58px; letter-spacing: -2.1px; }
.resource-cards { display: grid; grid-template-columns: 1.25fr .75fr; gap: 18px; margin-top: 20px; }
.resource-cards > div { padding: 15px 16px 13px; border: 1px solid #e6e6e8; border-radius: 14px; background: #fbfcfd; }
.resource-label { display: block; color: var(--accent); font-size: 9px; font-weight: 800; letter-spacing: 1.1px; }
.resource-cards strong { display: block; margin-top: 7px; color: var(--ink); font-size: 15px; line-height: 1.25; }
.resource-cards p { margin: 7px 0 0; color: #727981; font-size: 12px; line-height: 1.35; }
.run-telemetry { margin-top: 20px !important; padding-top: 17px !important; }
.metric-row { display: grid; grid-template-columns: 1.15fr 1fr .8fr; gap: 18px; margin-bottom: 8px; }
.metric-row strong { display: block; font-size: 35px; line-height: 1.05; color: var(--accent); letter-spacing: -1.2px; }
.metric-row span, .metric-row small { display: block; }
.metric-row span { margin-top: 5px; font-weight: 750; }
.token-thesis { margin-top: 22px; padding: 16px 18px; border-left: 3px solid var(--accent); background: color-mix(in srgb, var(--accent) 5%, white); }
.token-thesis span { color: #7d7d82; font-size: 12px; }
.token-thesis strong { display: block; margin-top: 2px; color: var(--ink); font-size: 21px; line-height: 1.1; }
.token-thesis p { margin: 8px 0 0; color: #646c74; font-size: 12px; }
.two-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 30px; }
.record-line { display: flex; gap: 20px; align-items: center; margin-bottom: 22px; font-size: 22px; font-weight: 700; color: var(--accent); }
.record-line i { font-style: normal; color: #b4bac1; }
.card-body dl { display: grid; grid-template-columns: 145px 1fr; gap: 14px 18px; }
.card-body dt { font-weight: 750; color: var(--ink); }
.card-body dd { margin: 0; }
.card-body pre { padding: 16px; background: #f5f7f9; border-radius: 10px; font-size: 12px; white-space: pre-wrap; }
.repo-address { font-weight: 700; }
</style>
