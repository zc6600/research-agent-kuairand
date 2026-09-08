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
      <section><h3>Direct-agent comparison</h3><p>Compare the score with the token investment and the strength of the retained evidence.</p>
        <table><thead><tr><th>Run</th><th>Total LLM tokens</th><th>Primary</th><th>Evidence</th></tr></thead><tbody>
          <tr><td>AGY · gemini-3.7-flash</td><td>8.565M</td><td>0.6045803</td><td>Artifact-backed</td></tr>
          <tr><td>gpt-5.6-luna · direct</td><td>28.070M</td><td>≈0.6046</td><td>Provisional</td></tr>
          <tr><td>Heterogeneous run</td><td>39.607M</td><td>≈0.6047</td><td>gemini-3.7-flash</td></tr>
          <tr><td>RA-only · Cycle 2 · E008</td><td>45.044–51.174M</td><td>0.6052</td><td>gemini-3.7-flash-only</td></tr>
          <tr><td>Research Agent submission</td><td>48.240M</td><td><b>0.605936</b></td><td>Verified</td></tr>
        </tbody></table><p class="boundary">Input + output including cache-read input, across the recorded agent system. Runs differ in model, budget, and evidence quality; this is not a controlled causal comparison.</p>
      </section>
    </template>

    <template v-else-if="card === 'trajectory'">
      <EvaluationTrajectory />
      <section><h3>What the search retained</h3><p>Thirteen named experiments included seven Full public-validation evaluations. Medium screens and diagnostics informed the four cycles without replacing the Full evaluator.</p><p>The final checkpoint, E013, retained an 8-seed ensemble with 46 leak-free fields and the unchanged evaluator. The remaining named experiments record the alternatives considered along the way.</p></section>
    </template>

    <template v-else-if="card === 'autonomy'">
      <div class="metric-row"><div><strong>4</strong><span>autonomous cycles</span><small>Within a 50-iteration cap</small></div><div><strong>13</strong><span>named experiments</span><small>E001–E013 · 7 Full evaluations</small></div><div><strong>0</strong><span>manual scientific interventions</span><small>After launch in the retained run</small></div></div>
      <p>Humans built the framework and set up the benchmark. After launch, the agent controlled the scientific decisions and kept an audit trail from experiments to the delivered output.</p>
      <section><h3>Resource use</h3><div class="resource-line"><strong>48.24M</strong><span>LLM tokens including cache reads<br><small>4.02M excluding cache reads</small></span><strong>0</strong><span>GPU-hours<br><small>CPU / NumPy training</small></span></div></section>
      <section><h3>~$10 across the project</h3><p>Estimated subscription-equivalent usage from the first line of code to the final result: coding, debugging, agent runs, and all experiments.</p><div class="two-columns"><div><h4>One GPT Plus + one Gemini Pro</h4><p>Two consumer subscriptions over seven days covered the research loop.</p></div><div><h4>One MacBook M2</h4><p>All development and experiments ran on a single consumer laptop.</p></div></div><p class="boundary">The ~$10 figure is a project-level estimate, not a per-experiment cost. Run telemetry is reported separately; zero GPU-hours does not mean zero LLM cost.</p></section>
    </template>

    <template v-else-if="card === 'validity'">
      <div class="validation-result"><span class="eyeline">UNCHANGED STARTER KIT ALIGNMENT CHECKER</span><strong class="hero-number">170,588</strong><p>prediction rows aligned and passed</p></div>
      <p>The delivered predictions passed the original submission checker. The reported model gains are on public validation; hidden-test scoring remains organizer-controlled.</p>
      <section><h3>A score is not a claim</h3><p>Audits found leakage and sampling mismatches in competing experiments. META can scope the evidence, but it is not a formal verifier.</p></section>
      <section><h3>Limits and next experiments</h3><dl><dt>External validity</dt><dd>One task does not establish generality. Evaluate broader tasks; KuaiRand-1K / 27K bonus benchmarks were not attempted.</dd><dt>Causal attribution</dt><dd>META, State, and reset have not been isolated. Targeted ablations are needed.</dd><dt>Memory quality</dt><dd>Summaries can omit context and anchor future work. Investigate less repeated execution and better retained evidence.</dd></dl><p class="boundary">These are open questions and proposed experiments, not completed features or a committed roadmap.</p></section>
    </template>

    <template v-else-if="card === 'evidence'">
      <div class="record-line"><span>Experiment</span><i>→</i><span>Report</span><i>→</i><span>Retained State</span></div>
      <div class="two-columns lessons"><div><h4>Diversity is a prior</h4><p>META stays on gemini-3.7-flash while Scientist rotates across gpt-5.6-sol, gemini-3.7-flash, and gpt-5.6-luna. This widens priors; it does not prove the gain.</p></div><div><h4>Failure can be evidence</h4><p>After evaluation, NumPy <code>float32</code> values broke serialization. The Scientist fixed the writer, reran, and kept the measurements.</p></div><div><h4>A score is not a claim</h4><p>Leakage and sampling mismatches in competing experiments showed why claims need an audit. META scopes evidence; it is not a formal verifier.</p></div><div><h4>Reset ≠ no anchor</h4><p>Fresh cognition reopens search, but shared summaries can still omit context or anchor future work. Share evidence later than cognition.</p></div></div>
      <p class="boundary">Observed, not proven: Parallel/Synthesis reached Primary 0.6055536 on public validation; the canonical E001–E013 frontier remains 0.6059363.</p>
      <section><h3>Engineering practice</h3><div class="two-columns"><div><h4>Give every agent a branch</h4><p>Keep parallel changes isolated, then review and merge. Conflicts stay local and the main branch stays clean.</p></div><div><h4>Leave the next move in GitHub</h4><p>Issue / prompt → GitHub Action → commit. An agent can work while you are offline; review the change before merging.</p></div></div><p class="boundary">Proposed workflow guidance; GitHub continuation is not a benchmarked system feature.</p></section>
      <section><h3>Open-world research</h3><p>Research needs an open-world coding agent: use existing capabilities, recover when they fail, and add what is missing.</p><dl><dt>Open action space</dt><dd>Shell · files · browser · Git</dd><dt>Self-recovery</dt><dd>Read errors · inspect docs and source · install packages</dd><dt>Runtime extension</dt><dd>MCP · skills · CLI · packages</dd></dl><p>A predefined graph can stop when an API fails and no recovery tool exists. A coding-agent harness can inspect, learn, modify its environment, and retry.</p><p>LangGraph makes a known workflow explicit as nodes and edges. When a capability is missing, leave the graph, inspect, extend, and retry.</p></section>
      <section><h3>Five people. One autonomous research loop.</h3><table><thead><tr><th>Team</th><th>Responsibility</th></tr></thead><tbody><tr><td>Chen Zhu</td><td>Team lead / system · direction, architecture, integration</td></tr><tr><td>Zhou Ziyu</td><td>Modeling / experiments · features, ensembles, evidence review</td></tr><tr><td>Shilin Xu</td><td>Data / metrics · data workflow, contracts, alignment</td></tr><tr><td>GE GAO</td><td>Runtime / reliability · execution, testing, integration support</td></tr><tr><td>Jiran Li</td><td>Evidence / reproducibility · telemetry, documentation, packaging</td></tr></tbody></table></section>
      <section><h3>Keep the experience. Reopen the search.</h3><p>From the configured repository, run one autonomous cycle:</p><pre>./scripts/research-agent step --cli codex \
    --target /absolute/path/to/project --allow-edits</pre><p class="boundary">Requires Git, uv, the Python environment, and an installed, authenticated agent CLI. Replace the target with a real research project path.</p><p class="repo-address">github.com/zc6600/research-agent-kuairand<br><small>Code · Technical report · Experiment ledger · Checked output</small></p></section>
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
