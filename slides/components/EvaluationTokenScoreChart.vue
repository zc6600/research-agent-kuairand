<template>
  <div class="embedded-token-chart" aria-label="Architecture comparison with aligned Gemini model family">
    <svg class="token-chart" viewBox="0 0 1150 300" role="img" aria-labelledby="embedded-token-chart-title embedded-token-chart-desc">
      <title id="embedded-token-chart-title">Architecture comparison with aligned Gemini model family</title>
      <desc id="embedded-token-chart-desc">Direct Antigravity reaches 0.6045803, Antigravity with delegated subagents reaches about 0.6047, and Meta-Scientist over Antigravity reaches 0.6052. The best observed mixed-model full system reaches 0.6059363.</desc>
      <rect class="chart-paper" x="0" y="0" width="1150" height="300" rx="18" />
      <text class="chart-kicker" x="96" y="28">Same model family · stronger research organization</text>
      <rect class="chart-plot" x="96" y="48" width="958" height="166" rx="5" />

      <g class="chart-grid">
        <line x1="96" y1="193" x2="1054" y2="193" />
        <line x1="96" y1="157" x2="1054" y2="157" />
        <line x1="96" y1="121" x2="1054" y2="121" />
        <line x1="96" y1="85" x2="1054" y2="85" />
        <line x1="96" y1="48" x2="1054" y2="48" />
        <line x1="230" y1="48" x2="230" y2="214" />
        <line x1="590" y1="48" x2="590" y2="214" />
        <line x1="930" y1="48" x2="930" y2="214" />
      </g>

      <g class="chart-y-labels">
        <text x="72" y="197">0.6045</text>
        <text x="72" y="161">0.6047</text>
        <text x="72" y="125">0.6049</text>
        <text x="72" y="89">0.6051</text>
        <text x="72" y="52">0.6053</text>
      </g>

      <path class="chart-path" d="M230 178 C350 168, 458 157, 590 151 S785 105, 930 67" />
      <g class="chart-series">
        <circle class="chart-point chart-point-blue" cx="230" cy="178" r="10" />
        <polygon class="chart-point chart-point-orange" points="590,139 606,151 590,163 574,151" />
        <polygon class="chart-point chart-point-purple" points="930,54 946,78 914,78" />
      </g>

      <g class="chart-point-labels">
        <text class="chart-label-main" x="230" y="100" text-anchor="middle">Direct Antigravity</text>
        <text class="chart-label-meta" x="230" y="119" text-anchor="middle">0.6045803 · single agent</text>
        <text class="chart-label-main" x="590" y="82" text-anchor="middle">AGY + subagents</text>
        <text class="chart-label-meta" x="590" y="101" text-anchor="middle">≈0.6047 · delegated control</text>
        <text class="chart-label-main chart-label-retained" x="930" y="37" text-anchor="middle">Meta-Scientist + AGY</text>
        <text class="chart-label-meta chart-label-retained" x="930" y="95" text-anchor="middle">0.6052 · persistent memory</text>
      </g>

      <g class="chart-axis-labels">
        <text x="230" y="238" text-anchor="middle">direct agent</text>
        <text x="590" y="238" text-anchor="middle">delegated subagents</text>
        <text x="930" y="238" text-anchor="middle">Meta-Scientist layer</text>
        <text class="chart-axis-title chart-axis-y" x="24" y="132" transform="rotate(-90 24 132)">Primary score</text>
      </g>

      <g class="best-badge">
        <rect x="730" y="256" width="324" height="30" rx="15" />
        <text x="748" y="276">Best full system: GPT/Gemini rotation · 0.6059363</text>
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
.token-chart { display: block; width: 100%; height: auto; max-height: 222px; }
.chart-paper { fill: #fff; }
.chart-plot { fill: #fbfcfd; stroke: #e4e8ec; stroke-width: 1; }
.chart-grid line { stroke: #e3e7eb; stroke-width: 1; }
.chart-kicker { fill: #7d858d; font-size: 15px; font-weight: 700; letter-spacing: .8px; text-transform: uppercase; }
.chart-y-labels text, .chart-axis-labels > text:not(.chart-axis-title) { fill: #7d858d; font-size: 15px; }
.chart-axis-title { fill: #171b20; font-size: 15px; font-weight: 700; text-anchor: middle; }
.chart-path { fill: none; stroke: #b7bdc6; stroke-width: 2.5; stroke-linecap: round; stroke-dasharray: 6 7; }
.chart-point { stroke: #fff; stroke-width: 3; }
.chart-point-blue { fill: #5d7fbd; }
.chart-point-orange { fill: #e98238; }
.chart-point-purple { fill: #a66cff; }
.chart-label-main { fill: #171b20; font-size: 17px; font-weight: 750; }
.chart-label-meta { fill: #626b74; font-size: 14px; }
.chart-label-retained { fill: #7f4de8; }
.best-badge rect { fill: #f6f1ff; stroke: #d7c3ff; }
.best-badge text { fill: #7f4de8; font-size: 13px; font-weight: 750; }
</style>
