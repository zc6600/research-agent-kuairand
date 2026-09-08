<script setup lang="ts">
import EvaluationScoreBars from './EvaluationScoreBars.vue'
import EvaluationTrajectory from './EvaluationTrajectory.vue'
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
      <section><h3>Where META fits</h3><p>The Scientist owned the code repair. META's role is to audit the report against the artifacts, then crystallize a coherent repaired implementation into recoverable State for the next trajectory.</p><p>No human selected the repair or edited the code. The run recovered its evidence instead of terminating.</p></section>
      <p class="boundary">This is the documented cycle-1 recovery event in <code>research_record/reports/cycle-1.md</code> and <code>docs/FINAL_REPORT.md</code> §4.2.</p>
    </template>

    <template v-else-if="card === 'comparison'">
      <div class="comparison-hero"><span class="eyeline">PUBLIC VALIDATION / DIRECT CODEX GOAL CONTROL</span><div class="comparison-scores"><div><small>DIRECT CODEX</small><strong>0.6044533</strong><span>provisional control</span></div><i>→</i><div><small>RESEARCH AGENT</small><strong>0.6059363</strong><span>verified retained result</span></div></div><p><b>+0.0014830 Primary</b> above the recorded direct Codex control.</p></div>
      <table><thead><tr><th>Metric</th><th>Direct Codex</th><th>Research Agent</th></tr></thead><tbody><tr><td>GAUC</td><td>0.6712471</td><td>0.6728421</td></tr><tr><td>nDCG@5</td><td>0.5376595</td><td>0.5390304</td></tr><tr><td>Primary</td><td>0.6044533</td><td><b>0.6059363</b></td></tr></tbody></table>
      <section><h3>Read the comparison carefully</h3><p>Both results use public validation only. The Codex record is marked provisional because its process audit lists unresolved launcher, provenance, and pair-construction concerns. This is a recorded control comparison, not a causal proof of architecture superiority.</p></section>
    </template>

    <template v-else-if="card === 'tokenmaxxing'">
      <div class="token-hero"><span class="eyeline">P10 / AUTONOMY AND AUDITABILITY</span><strong>48.240M</strong><p>total input + output tokens, including cache-read input</p></div>
      <div class="metric-row"><div><strong>4</strong><span>autonomous cycles</span><small>Within a 50-iteration cap</small></div><div><strong>13</strong><span>named experiments</span><small>E001–E013 · 7 Full evaluations</small></div><div><strong>0</strong><span>manual scientific interventions</span><small>After launch in the retained run</small></div></div>
      <section><h3>Resource use</h3><div class="resource-line"><strong>4.020M</strong><span>non-cache input + output<br><small>48.240M including cache reads</small></span><strong>0</strong><span>GPU-hours<br><small>CPU / NumPy training</small></span></div></section>
      <table><thead><tr><th>Recorded system</th><th>Total tokens</th><th>Primary</th><th>Evidence</th></tr></thead><tbody><tr><td>AGY direct</td><td>8.565M</td><td>0.6045803</td><td>Artifact-backed</td></tr><tr><td>Codex direct</td><td>11.221M</td><td>0.6044533</td><td>Provisional</td></tr><tr><td>Research Agent</td><td>48.240M</td><td><b>0.6059363</b></td><td>Verified</td></tr></tbody></table>
      <p class="boundary">The controls used fewer tokens, and their protocols differ. The defensible claim is a verified retained result with an audit trail, not a token-efficiency frontier or “more tokens means better.”</p>
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
.comparison-scores { display: grid; grid-template-columns: 1fr auto 1fr; align-items: end; gap: 18px; margin-top: 14px; }
.comparison-scores div { padding-top: 10px; border-top: 2px solid color-mix(in srgb, var(--accent) 44%, #e6e6e8); }
.comparison-scores small, .comparison-scores span { display: block; color: #7d7d82; font-size: 10px; letter-spacing: .75px; }
.comparison-scores strong { display: block; color: var(--accent); font-size: 34px; line-height: 1.05; letter-spacing: -1px; }
.comparison-scores i { padding-bottom: 16px; color: #b8bec4; font-size: 24px; font-style: normal; }
.token-hero { padding-bottom: 5px; }
.token-hero strong { font-size: 48px; letter-spacing: -1.8px; }
.metric-row { display: grid; grid-template-columns: 1fr 1fr 1.3fr; gap: 25px; margin-bottom: 22px; }
.metric-row strong { display: block; font-size: 52px; line-height: 1.1; color: var(--accent); }
.metric-row span, .metric-row small { display: block; }
.metric-row span { font-weight: 700; margin: 6px 0; }
.resource-line { display: flex; gap: 22px; align-items: center; }
.resource-line strong { font-size: 34px; color: var(--accent); }
.two-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 30px; }
.record-line { display: flex; gap: 20px; align-items: center; margin-bottom: 22px; font-size: 22px; font-weight: 700; color: var(--accent); }
.record-line i { font-style: normal; color: #b4bac1; }
.card-body dl { display: grid; grid-template-columns: 145px 1fr; gap: 14px 18px; }
.card-body dt { font-weight: 750; color: var(--ink); }
.card-body dd { margin: 0; }
.card-body pre { padding: 16px; background: #f5f7f9; border-radius: 10px; font-size: 12px; white-space: pre-wrap; }
.repo-address { font-weight: 700; }
</style>
