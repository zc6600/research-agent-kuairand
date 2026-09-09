<template>
  <div class="embedded-token-chart" aria-label="Architecture comparison with aligned Gemini model family">
    <svg class="token-chart" viewBox="0 0 1150 300" role="img" aria-labelledby="embedded-token-chart-title embedded-token-chart-desc">
      <title id="embedded-token-chart-title">Architecture ablation bar chart</title>
      <desc id="embedded-token-chart-desc">Bar chart comparing Direct Antigravity at 0.6045803, Antigravity with delegated subagents at about 0.6047000, and Meta-Scientist over Antigravity at 0.6052000.</desc>
      <rect class="chart-paper" x="0" y="0" width="1150" height="300" rx="18" />
      <text class="chart-kicker" x="96" y="30">Architecture ablation · same Gemini-family comparison</text>
      <text class="chart-note" x="1054" y="30" text-anchor="end">Zoomed y-axis</text>

      <rect class="chart-plot" x="96" y="50" width="958" height="166" rx="5" />
      <g class="chart-grid">
        <line x1="96" y1="198" x2="1054" y2="198" />
        <line x1="96" y1="161" x2="1054" y2="161" />
        <line x1="96" y1="124" x2="1054" y2="124" />
        <line x1="96" y1="87" x2="1054" y2="87" />
        <line x1="96" y1="50" x2="1054" y2="50" />
      </g>

      <g class="chart-y-labels">
        <text x="72" y="202">0.6045</text>
        <text x="72" y="165">0.6047</text>
        <text x="72" y="128">0.6049</text>
        <text x="72" y="91">0.6051</text>
        <text x="72" y="54">0.6053</text>
      </g>

      <g class="bars">
        <rect class="bar bar-blue" x="198" y="183" width="96" height="31" rx="12" />
        <rect class="bar bar-orange" x="527" y="161" width="96" height="53" rx="12" />
        <rect class="bar bar-purple" x="856" y="68" width="96" height="146" rx="12" />
      </g>

      <g class="bar-labels">
        <text class="label-main" x="246" y="112" text-anchor="middle">Direct AGY</text>
        <text class="label-score" x="246" y="135" text-anchor="middle">0.6045803</text>
        <text class="label-meta" x="246" y="154" text-anchor="middle">single agent</text>

        <text class="label-main" x="575" y="89" text-anchor="middle">AGY + subagents</text>
        <text class="label-score" x="575" y="112" text-anchor="middle">≈0.6047000</text>
        <text class="label-meta" x="575" y="131" text-anchor="middle">delegated control</text>

        <text class="label-main label-retained" x="904" y="38" text-anchor="middle">Meta-Scientist + AGY</text>
        <text class="label-score label-retained" x="904" y="61" text-anchor="middle">0.6052000</text>
        <text class="label-meta label-retained" x="904" y="239" text-anchor="middle">persistent memory</text>
      </g>

      <g class="axis-labels">
        <text x="246" y="262" text-anchor="middle">direct agent</text>
        <text x="575" y="262" text-anchor="middle">delegated subagents</text>
        <text x="904" y="262" text-anchor="middle">Meta-Scientist layer</text>
        <text class="axis-title axis-y" x="24" y="134" transform="rotate(-90 24 134)">Primary score</text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.embedded-token-chart { width: 100%; margin: 0; border: 1px solid #e6e8eb; border-radius: 14px; overflow: hidden; background: #fff; }
.token-chart { display: block; width: 100%; height: auto; max-height: 222px; }
.chart-paper { fill: #fff; }
.chart-plot { fill: #fbfcfd; stroke: #e4e8ec; stroke-width: 1; }
.chart-grid line { stroke: #e3e7eb; stroke-width: 1; }
.chart-kicker { fill: #7d858d; font-size: 15px; font-weight: 750; letter-spacing: .8px; text-transform: uppercase; }
.chart-note { fill: #a0a7ae; font-size: 13px; font-weight: 700; }
.chart-y-labels text, .axis-labels > text:not(.axis-title) { fill: #7d858d; font-size: 15px; }
.axis-title { fill: #171b20; font-size: 15px; font-weight: 750; text-anchor: middle; }
.bar { stroke: #fff; stroke-width: 2; }
.bar-blue { fill: #5d7fbd; }
.bar-orange { fill: #e98238; }
.bar-purple { fill: #a66cff; }
.label-main { fill: #171b20; font-size: 17px; font-weight: 780; }
.label-score { fill: #3f4750; font-size: 20px; font-weight: 820; letter-spacing: -.5px; }
.label-meta { fill: #626b74; font-size: 14px; }
.label-retained { fill: #7f4de8; }
</style>
