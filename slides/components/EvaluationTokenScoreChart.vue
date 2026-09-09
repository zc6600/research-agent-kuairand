<template>
  <div class="embedded-token-chart" aria-label="Architecture comparison with aligned Gemini model family">
    <svg class="token-chart" viewBox="0 0 1150 280" role="img" aria-label="Architecture ablation bar chart" aria-describedby="embedded-token-chart-desc">
      <desc id="embedded-token-chart-desc">Bar chart comparing Direct Antigravity at 0.6045803, Antigravity with delegated subagents at 0.6047213, and Meta-Scientist over Antigravity at 0.6052000.</desc>
      <rect class="chart-paper" x="0" y="0" width="1150" height="280" rx="18" />

      <rect class="chart-plot" x="96" y="36" width="958" height="240" rx="5" />
      <g class="chart-grid">
        <line x1="96" y1="250" x2="1054" y2="250" />
        <line x1="96" y1="197" x2="1054" y2="197" />
        <line x1="96" y1="143" x2="1054" y2="143" />
        <line x1="96" y1="90" x2="1054" y2="90" />
        <line x1="96" y1="36" x2="1054" y2="36" />
      </g>

      <g class="chart-y-labels">
        <text x="88" y="254" text-anchor="end">0.6045000</text>
        <text x="88" y="201" text-anchor="end">0.6047000</text>
        <text x="88" y="147" text-anchor="end">0.6049000</text>
        <text x="88" y="94" text-anchor="end">0.6051000</text>
        <text x="88" y="40" text-anchor="end">0.6053000</text>
      </g>

      <g class="bars">
        <rect class="bar bar-blue" x="198" y="228" width="96" height="46" rx="12" />
        <rect class="bar bar-orange" x="527" y="191" width="96" height="83" rx="12" />
        <rect class="bar bar-purple" x="856" y="62" width="96" height="212" rx="12" />
      </g>

      <g class="bar-labels">
        <text class="label-main" x="246" y="126" text-anchor="middle">Direct Antigravity</text>
        <text class="label-score" x="246" y="159" text-anchor="middle">0.6045803</text>

        <text class="label-main" x="575" y="92" text-anchor="middle">Antigravity + subagents</text>
        <text class="label-score" x="575" y="126" text-anchor="middle">0.6047213</text>

        <text class="label-main label-retained" x="904" y="19" text-anchor="middle">Meta-Scientist + Antigravity</text>
        <text class="label-score label-retained" x="904" y="52" text-anchor="middle">0.6052000</text>
      </g>

      <g class="axis-labels">
        <text class="axis-title axis-y" x="24" y="156" transform="rotate(-90 24 156)">Primary score</text>
      </g>

    </svg>
  </div>
</template>

<style scoped>
.embedded-token-chart { width: 100%; margin: 0; border: 1px solid #e6e8eb; border-radius: 14px; overflow: hidden; background: #fff; }
.token-chart { display: block; width: 100%; height: auto; max-height: none; }
.chart-paper { fill: #fff; }
.chart-plot { fill: #fcfdfe; stroke: #f1f3f5; stroke-width: 1; }
.chart-grid line { stroke: #f2f4f6; stroke-width: 1; }
.chart-y-labels text { fill: #a3aab2; font-size: 15px; }
.axis-title { fill: #a0a8b0; font-size: 15px; font-weight: 700; text-anchor: middle; }
.bar { stroke: #fff; stroke-width: 2; }
.bar-blue { fill: #5d7fbd; }
.bar-orange { fill: #e98238; }
.bar-purple { fill: #a66cff; }
.label-main { fill: #171b20; font-size: 17px; font-weight: 700; }
.label-score { fill: #3f4750; font-size: 20px; font-weight: 700; letter-spacing: -.5px; }
.label-retained { fill: #7f4de8; }
</style>
