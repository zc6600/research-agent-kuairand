<template>
  <div class="embedded-token-chart" aria-label="Public-validation Primary score versus measured total LLM tokens">
    <svg class="token-chart" viewBox="0 0 1150 480" role="img" aria-labelledby="embedded-token-chart-title embedded-token-chart-desc">
      <title id="embedded-token-chart-title">Public-validation Primary score versus measured total LLM tokens</title>
      <desc id="embedded-token-chart-desc">The retained Research Agent result reaches a Primary score of 0.605936 at 48.240 million total LLM tokens, alongside direct-agent controls with different models, budgets, and evidence quality.</desc>
      <rect class="chart-paper" x="0" y="0" width="1150" height="480" rx="18" />
      <text class="chart-inline-title" x="106" y="30">Score versus measured LLM-token investment</text>
      <text class="chart-inline-subtitle" x="106" y="48">Public validation; input + output including cache-read; whole recorded agent system</text>
      <rect class="chart-plot" x="106" y="63" width="966" height="325" rx="4" />
      <g class="chart-grid">
        <line x1="106" y1="359" x2="1072" y2="359" />
        <line x1="106" y1="300" x2="1072" y2="300" />
        <line x1="106" y1="241" x2="1072" y2="241" />
        <line x1="106" y1="182" x2="1072" y2="182" />
        <line x1="106" y1="122" x2="1072" y2="122" />
        <line x1="106" y1="63" x2="1072" y2="63" />
        <line x1="106" y1="63" x2="106" y2="388" />
        <line x1="282" y1="63" x2="282" y2="388" />
        <line x1="457" y1="63" x2="457" y2="388" />
        <line x1="633" y1="63" x2="633" y2="388" />
        <line x1="808" y1="63" x2="808" y2="388" />
        <line x1="984" y1="63" x2="984" y2="388" />
        <line x1="1072" y1="63" x2="1072" y2="388" />
      </g>
      <g class="chart-y-labels">
        <text x="76" y="363">0.602</text>
        <text x="76" y="304">0.603</text>
        <text x="76" y="245">0.604</text>
        <text x="76" y="186">0.605</text>
        <text x="76" y="126">0.606</text>
      </g>
      <line class="chart-reference" x1="106" y1="382" x2="1072" y2="382" />
      <text class="chart-reference-label" x="136" y="376">Official reference 0.601600</text>
      <g class="chart-leaders">
        <line x1="256" y1="207" x2="174" y2="193" />
        <line x1="599" y1="205" x2="587" y2="167" />
        <line x1="802" y1="196" x2="909" y2="140" />
        <line x1="951" y1="170" x2="1035" y2="200" />
        <line x1="953" y1="126" x2="978" y2="96" />
      </g>
      <g class="chart-series">
        <circle class="chart-point chart-point-blue" cx="256" cy="207" r="8" />
        <circle class="chart-point chart-point-blue" cx="599" cy="205" r="8" />
        <polygon class="chart-point chart-point-orange" points="802,188 813,196 802,204 790,196" />
        <line class="chart-range" x1="897" y1="170" x2="1005" y2="170" />
        <line class="chart-range" x1="897" y1="163" x2="897" y2="176" />
        <line class="chart-range" x1="1005" y1="163" x2="1005" y2="176" />
        <polygon class="chart-point chart-point-purple" points="951,161 965,178 937,178" />
        <circle class="chart-point chart-point-green" cx="953" cy="126" r="9" />
      </g>
      <g class="chart-point-labels">
        <text class="chart-label-main" x="174" y="187">AGY</text>
        <text class="chart-label-sub" x="174" y="207">gemini-3.7-flash · direct</text>
        <text class="chart-label-meta" x="174" y="224">8.565M · 0.6045803 · artifact-backed</text>
        <text class="chart-label-main chart-label-right" x="587" y="152">gpt-5.6-luna · direct</text>
        <text class="chart-label-sub chart-label-right" x="587" y="172">28.070M · ≈0.6046 · provisional</text>
        <text class="chart-label-main chart-label-right" x="909" y="121">heterogeneous run</text>
        <text class="chart-label-sub chart-label-right" x="909" y="141">gemini-3.7-flash · 39.607M · ≈0.6047</text>
        <text class="chart-label-main chart-label-right" x="1064" y="215">RA-only · Cycle 2</text>
        <text class="chart-label-sub chart-label-right" x="1064" y="235">gemini-3.7-flash-only · 45.044–51.174M · 0.6052 · E008</text>
        <text class="chart-label-main chart-label-right chart-label-retained" x="1064" y="82">Research Agent submission</text>
        <text class="chart-label-sub chart-label-right chart-label-retained" x="1064" y="102">48.240M · 0.605936 · verified</text>
      </g>
      <g class="chart-axis-labels">
        <text x="106" y="406">0</text>
        <text x="274" y="406">10</text>
        <text x="448" y="406">20</text>
        <text x="624" y="406">30</text>
        <text x="800" y="406">40</text>
        <text x="976" y="406">50</text>
        <text x="1056" y="406">55M</text>
        <text class="chart-axis-title" x="589" y="430">Total LLM tokens (millions)</text>
        <text class="chart-axis-title chart-axis-y" x="20" y="229" transform="rotate(-90 20 229)">Primary score</text>
      </g>
      <g class="chart-legend">
        <circle class="chart-point chart-point-blue" cx="127" cy="454" r="7" />
        <text x="148" y="459">direct model run</text>
        <polygon class="chart-point chart-point-orange" points="367,446 376,452 367,458 358,452" />
        <text x="390" y="459">heterogeneous run</text>
        <polygon class="chart-point chart-point-purple" points="619,447 628,457 610,457" />
        <text x="643" y="459">RA-only sweep</text>
        <circle class="chart-point chart-point-green" cx="854" cy="454" r="7" />
        <text x="875" y="459">retained verified result</text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.embedded-token-chart {
  width: 100%;
  margin: 0;
  border: 1px solid #e6e8eb;
  border-radius: 16px;
  overflow: hidden;
  background: #fff;
}
.token-chart { display: block; width: 100%; height: auto; }
.chart-paper { fill: #fff; }
.chart-plot { fill: #fbfcfd; stroke: #e4e8ec; stroke-width: 1; }
.chart-grid line { stroke: #e3e7eb; stroke-width: 1; }
.chart-inline-title, .chart-label-main, .chart-axis-title { fill: #171b20; }
.chart-inline-title { font-size: 23px; font-weight: 700; }
.chart-inline-subtitle { fill: #7d858d; font-size: 15px; }
.chart-y-labels text, .chart-axis-labels > text:not(.chart-axis-title), .chart-legend text { fill: #7d858d; font-size: 16px; }
.chart-axis-title { font-size: 16px; font-weight: 700; text-anchor: middle; }
.chart-reference { stroke: #b9c1ca; stroke-dasharray: 7 6; stroke-width: 1.5; }
.chart-reference-label { fill: #8a929b; font-size: 15px; }
.chart-leaders line { stroke: #aeb7c1; stroke-width: 1; }
.chart-point { stroke: #fff; stroke-width: 3; }
.chart-point-blue { fill: #5d7fbd; }
.chart-point-orange { fill: #e98238; }
.chart-point-purple { fill: #a66cff; }
.chart-point-green { fill: #16803b; }
.chart-range { fill: none; stroke: #a66cff; stroke-width: 3; }
.chart-label-main { font-size: 17px; font-weight: 700; }
.chart-label-sub { fill: #434a52; font-size: 15px; }
.chart-label-meta { fill: #7d858d; font-size: 13px; }
.chart-label-right { text-anchor: end; }
.chart-label-retained { fill: #16803b; }
.chart-legend .chart-point { stroke-width: 2; }
</style>
