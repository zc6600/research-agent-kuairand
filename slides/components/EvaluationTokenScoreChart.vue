<template>
  <div class="embedded-token-chart" aria-label="Public-validation Primary score versus measured total LLM tokens">
    <svg class="token-chart" viewBox="0 0 1150 330" role="img" aria-labelledby="embedded-token-chart-title embedded-token-chart-desc">
      <title id="embedded-token-chart-title">Public-validation Primary score versus measured total LLM tokens</title>
      <desc id="embedded-token-chart-desc">The retained Research Agent result reaches a Primary score of 0.605936 at 48.240 million total LLM tokens, alongside direct-agent controls.</desc>
      <rect class="chart-paper" x="0" y="0" width="1150" height="330" rx="18" />
      <rect class="chart-plot" x="106" y="28" width="966" height="224" rx="4" />
      <g class="chart-grid">
        <line x1="106" y1="232" x2="1072" y2="232" />
        <line x1="106" y1="191" x2="1072" y2="191" />
        <line x1="106" y1="151" x2="1072" y2="151" />
        <line x1="106" y1="110" x2="1072" y2="110" />
        <line x1="106" y1="69" x2="1072" y2="69" />
        <line x1="106" y1="28" x2="1072" y2="28" />
        <line x1="106" y1="28" x2="106" y2="252" />
        <line x1="282" y1="28" x2="282" y2="252" />
        <line x1="457" y1="28" x2="457" y2="252" />
        <line x1="633" y1="28" x2="633" y2="252" />
        <line x1="808" y1="28" x2="808" y2="252" />
        <line x1="984" y1="28" x2="984" y2="252" />
        <line x1="1072" y1="28" x2="1072" y2="252" />
      </g>
      <g class="chart-y-labels">
        <text x="76" y="236">0.602</text>
        <text x="76" y="195">0.603</text>
        <text x="76" y="155">0.604</text>
        <text x="76" y="114">0.605</text>
        <text x="76" y="73">0.606</text>
      </g>
      <line class="chart-reference" x1="106" y1="248" x2="1072" y2="248" />
      <text class="chart-reference-label" x="136" y="243">Official reference 0.601600</text>
      <g class="chart-leaders">
        <line x1="256" y1="135" x2="174" y2="122" />
        <line x1="599" y1="133" x2="587" y2="98" />
        <line x1="802" y1="123" x2="905" y2="75" />
        <line x1="951" y1="105" x2="1038" y2="128" />
        <line x1="953" y1="74" x2="978" y2="49" />
      </g>
      <g class="chart-series">
        <circle class="chart-point chart-point-blue" cx="256" cy="135" r="8" />
        <circle class="chart-point chart-point-blue" cx="599" cy="133" r="8" />
        <polygon class="chart-point chart-point-orange" points="802,115 813,123 802,131 790,123" />
        <line class="chart-range" x1="897" y1="105" x2="1005" y2="105" />
        <line class="chart-range" x1="897" y1="98" x2="897" y2="111" />
        <line class="chart-range" x1="1005" y1="98" x2="1005" y2="111" />
        <polygon class="chart-point chart-point-purple" points="951,96 965,113 937,113" />
        <circle class="chart-point chart-point-green" cx="953" cy="74" r="9" />
      </g>
      <g class="chart-point-labels">
        <text class="chart-label-main" x="174" y="116">Antigravity direct</text>
        <text class="chart-label-meta" x="174" y="134">8.565M · 0.6045803</text>
        <text class="chart-label-main chart-label-right" x="587" y="84">Codex direct</text>
        <text class="chart-label-meta chart-label-right" x="587" y="102">28.070M · 0.6044533</text>
        <text class="chart-label-main chart-label-right" x="905" y="61">heterogeneous run</text>
        <text class="chart-label-meta chart-label-right" x="905" y="79">39.607M · ≈0.6047</text>
        <text class="chart-label-main chart-label-right" x="1064" y="143">SciOdyssey with AGY</text>
        <text class="chart-label-meta chart-label-right" x="1064" y="161">45.04–51.17M · 0.6052</text>
        <text class="chart-label-main chart-label-right chart-label-retained" x="1064" y="36">SciOdyssey submission</text>
        <text class="chart-label-meta chart-label-right chart-label-retained" x="1064" y="54">48.240M · 0.605936</text>
      </g>
      <g class="chart-axis-labels">
        <text x="106" y="274">0</text>
        <text x="274" y="274">10</text>
        <text x="448" y="274">20</text>
        <text x="624" y="274">30</text>
        <text x="800" y="274">40</text>
        <text x="976" y="274">50</text>
        <text x="1056" y="274">55M</text>
        <text class="chart-axis-title" x="589" y="301">Total LLM tokens (millions)</text>
        <text class="chart-axis-title chart-axis-y" x="20" y="140" transform="rotate(-90 20 140)">Primary score</text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.embedded-token-chart {
  width: 100%;
  margin: 0;
  border: 1px solid #e6e8eb;
  border-radius: 14px;
  overflow: hidden;
  background: #fff;
}
.token-chart { display: block; width: 100%; height: auto; max-height: 232px; }
.chart-paper { fill: #fff; }
.chart-plot { fill: #fbfcfd; stroke: #e4e8ec; stroke-width: 1; }
.chart-grid line { stroke: #e3e7eb; stroke-width: 1; }
.chart-label-main, .chart-axis-title { fill: #171b20; }
.chart-y-labels text, .chart-axis-labels > text:not(.chart-axis-title) { fill: #7d858d; font-size: 15px; }
.chart-axis-title { font-size: 15px; font-weight: 700; text-anchor: middle; }
.chart-reference { stroke: #b9c1ca; stroke-dasharray: 7 6; stroke-width: 1.5; }
.chart-reference-label { fill: #8a929b; font-size: 13px; }
.chart-leaders line { stroke: #aeb7c1; stroke-width: 1; }
.chart-point { stroke: #fff; stroke-width: 3; }
.chart-point-blue { fill: #5d7fbd; }
.chart-point-orange { fill: #e98238; }
.chart-point-purple { fill: #a66cff; }
.chart-point-green { fill: #16803b; }
.chart-range { fill: none; stroke: #a66cff; stroke-width: 3; }
.chart-label-main { font-size: 16px; font-weight: 700; }
.chart-label-meta { fill: #626b74; font-size: 14px; }
.chart-label-right { text-anchor: end; }
.chart-label-retained { fill: #16803b; }
</style>
