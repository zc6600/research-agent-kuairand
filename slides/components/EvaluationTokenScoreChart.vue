<template>
  <div class="embedded-token-chart" aria-label="Public-validation Primary score versus measured total LLM tokens">
    <svg class="token-chart" viewBox="0 0 1000 620" role="img" aria-labelledby="embedded-token-chart-title embedded-token-chart-desc">
      <title id="embedded-token-chart-title">Public-validation Primary score versus measured total LLM tokens</title>
      <desc id="embedded-token-chart-desc">The retained Research Agent result reaches a Primary score of 0.605936 at 48.240 million total LLM tokens, alongside direct-agent controls with different models, budgets, and evidence quality.</desc>
      <rect class="chart-paper" x="0" y="0" width="1000" height="620" rx="18" />
      <text class="chart-inline-title" x="92" y="34">Score versus measured LLM-token investment</text>
      <text class="chart-inline-subtitle" x="92" y="58">Public validation; input + output including cache-read; whole recorded agent system</text>
      <rect class="chart-plot" x="92" y="82" width="840" height="420" rx="4" />
      <g class="chart-grid">
        <line x1="92" y1="464" x2="932" y2="464" />
        <line x1="92" y1="388" x2="932" y2="388" />
        <line x1="92" y1="311" x2="932" y2="311" />
        <line x1="92" y1="235" x2="932" y2="235" />
        <line x1="92" y1="158" x2="932" y2="158" />
        <line x1="92" y1="82" x2="932" y2="82" />
        <line x1="92" y1="82" x2="92" y2="502" />
        <line x1="245" y1="82" x2="245" y2="502" />
        <line x1="397" y1="82" x2="397" y2="502" />
        <line x1="550" y1="82" x2="550" y2="502" />
        <line x1="703" y1="82" x2="703" y2="502" />
        <line x1="856" y1="82" x2="856" y2="502" />
        <line x1="932" y1="82" x2="932" y2="502" />
      </g>
      <g class="chart-y-labels">
        <text x="78" y="469">0.602</text>
        <text x="78" y="393">0.603</text>
        <text x="78" y="316">0.604</text>
        <text x="78" y="240">0.605</text>
        <text x="78" y="163">0.606</text>
      </g>
      <line class="chart-reference" x1="92" y1="494" x2="932" y2="494" />
      <text class="chart-reference-label" x="118" y="488">Official reference 0.601600</text>
      <g class="chart-leaders">
        <line x1="223" y1="267" x2="151" y2="249" />
        <line x1="521" y1="265" x2="510" y2="216" />
        <line x1="697" y1="253" x2="790" y2="181" />
        <line x1="827" y1="219" x2="900" y2="259" />
        <line x1="829" y1="163" x2="850" y2="124" />
      </g>
      <g class="chart-series">
        <circle class="chart-point chart-point-blue" cx="223" cy="267" r="8" />
        <circle class="chart-point chart-point-blue" cx="521" cy="265" r="8" />
        <polygon class="chart-point chart-point-orange" points="697,243 707,253 697,263 687,253" />
        <line class="chart-range" x1="780" y1="219" x2="874" y2="219" />
        <line class="chart-range" x1="780" y1="210" x2="780" y2="228" />
        <line class="chart-range" x1="874" y1="210" x2="874" y2="228" />
        <polygon class="chart-point chart-point-purple" points="827,208 839,230 815,230" />
        <circle class="chart-point chart-point-green" cx="829" cy="163" r="9" />
      </g>
      <g class="chart-point-labels">
        <text class="chart-label-main" x="151" y="242">AGY</text>
        <text class="chart-label-sub" x="151" y="258">gemini-3.7-flash · direct</text>
        <text class="chart-label-meta" x="151" y="274">8.565M · 0.6045803 · artifact-backed</text>
        <text class="chart-label-main chart-label-right" x="510" y="196">gpt-5.6-luna · direct</text>
        <text class="chart-label-sub chart-label-right" x="510" y="212">28.070M · ≈0.6046 · provisional</text>
        <text class="chart-label-main chart-label-right" x="790" y="156">heterogeneous run</text>
        <text class="chart-label-sub chart-label-right" x="790" y="172">gemini-3.7-flash · 39.607M · ≈0.6047</text>
        <text class="chart-label-main chart-label-right" x="925" y="274">RA-only · Cycle 2</text>
        <text class="chart-label-sub chart-label-right" x="925" y="290">gemini-3.7-flash-only · 45.044–51.174M · 0.6052 · E008</text>
        <text class="chart-label-main chart-label-right chart-label-retained" x="925" y="108">Research Agent submission</text>
        <text class="chart-label-sub chart-label-right chart-label-retained" x="925" y="124">48.240M · 0.605936 · verified</text>
      </g>
      <g class="chart-axis-labels">
        <text x="92" y="522">0</text>
        <text x="238" y="522">10</text>
        <text x="390" y="522">20</text>
        <text x="543" y="522">30</text>
        <text x="696" y="522">40</text>
        <text x="849" y="522">50</text>
        <text x="918" y="522">55M</text>
        <text class="chart-axis-title" x="512" y="548">Total LLM tokens (millions)</text>
        <text class="chart-axis-title chart-axis-y" x="22" y="296" transform="rotate(-90 22 296)">Primary score</text>
      </g>
      <g class="chart-legend">
        <circle class="chart-point chart-point-blue" cx="110" cy="584" r="6" />
        <text x="124" y="589">direct model run</text>
        <polygon class="chart-point chart-point-orange" points="267,578 274,584 267,590 260,584" />
        <text x="282" y="589">heterogeneous run</text>
        <polygon class="chart-point chart-point-purple" points="431,577 439,591 423,591" />
        <text x="447" y="589">RA-only sweep</text>
        <circle class="chart-point chart-point-green" cx="584" cy="584" r="6" />
        <text x="598" y="589">retained verified result</text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.embedded-token-chart {
  width: 100%;
  margin: 2px 0 12px;
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
.chart-inline-title { font-size: 17px; font-weight: 700; }
.chart-inline-subtitle { fill: #7d858d; font-size: 12px; }
.chart-y-labels text, .chart-axis-labels > text:not(.chart-axis-title), .chart-legend text { fill: #7d858d; font-size: 12px; }
.chart-axis-title { font-size: 13px; text-anchor: middle; }
.chart-reference { stroke: #b9c1ca; stroke-dasharray: 7 6; stroke-width: 1.5; }
.chart-reference-label { fill: #8a929b; font-size: 12px; }
.chart-leaders line { stroke: #aeb7c1; stroke-width: 1; }
.chart-point { stroke: #fff; stroke-width: 3; }
.chart-point-blue { fill: #5d7fbd; }
.chart-point-orange { fill: #e98238; }
.chart-point-purple { fill: #a66cff; }
.chart-point-green { fill: #16803b; }
.chart-range { fill: none; stroke: #a66cff; stroke-width: 3; }
.chart-label-main { font-size: 13px; font-weight: 700; }
.chart-label-sub { fill: #434a52; font-size: 11px; }
.chart-label-meta { fill: #7d858d; font-size: 10px; }
.chart-label-right { text-anchor: end; }
.chart-label-retained { fill: #16803b; }
.chart-legend .chart-point { stroke-width: 2; }
</style>
