<template>
  <svg class="resource-scatter" viewBox="0 0 1994 854" role="img" aria-label="Score vs token investment: original chart layout">
    <text x="1960" y="50" text-anchor="end" class="cost">~$10 cost　 1 × M2　 0 GPU-hr　 1h 5m</text>
    <text x="1960" y="92" text-anchor="end" class="subtitle">KuaiRand-Pure · Public validation · Inclusive input+output tokens</text>
    <g class="grid">
      <path d="M228 265H1799 M228 363H1799 M228 459H1799 M228 555H1799 M228 651H1799"/>
      <path d="M228 169V699 M514 169V699 M799 169V699 M1085 169V699 M1370 169V699 M1656 169V699 M1799 169V699"/>
    </g>
    <g class="ticks">
      <text x="177" y="274" text-anchor="end">0.606</text><text x="177" y="372" text-anchor="end">0.605</text>
      <text x="177" y="468" text-anchor="end">0.604</text><text x="177" y="564" text-anchor="end">0.603</text><text x="177" y="660" text-anchor="end">0.602</text>
      <text x="228" y="731">0</text><text x="498" y="731">10</text><text x="783" y="731">20</text><text x="1069" y="731">30</text><text x="1354" y="731">40</text><text x="1640" y="731">50</text><text x="1773" y="731">55M</text>
    </g>
    <text x="90" y="437" transform="rotate(-90 90 437)" class="axis-title">Primary score</text>
    <text x="1196" y="765" text-anchor="middle" class="axis-title">Total LLM tokens (millions)</text>
    <path d="M228 688H1799" class="reference"/>
    <text x="252" y="688" class="reference-label">Official reference 0.601600</text>
    <g class="leaders"><path d="M471 403V473 M920 349L1030 401 M1360 350V385 M1602 360V415"/></g>
    <g class="direct">
      <circle cx="471" cy="403" r="12"/><circle cx="1030" cy="401" r="12"/>
      <text x="340" y="500" class="name">Antigravity</text>
      <text x="340" y="524" class="value">8.565M · 0.6045803</text>
      <text x="340" y="544" class="detail">gemini-3.7-flash · direct</text>
      <text x="656" y="300" class="name">Codex (gpt-5.6-luna)</text>
      <text x="656" y="324" class="value">28.070M · 0.6044533</text>
      <text x="656" y="344" class="detail">direct run · provisional ≈0.6046</text>
    </g>
    <g class="heterogeneous">
      <path d="M1360 373l17 12-17 12-17-12z"/>
      <text x="1203" y="300" class="name">heterogeneous run</text>
      <text x="1203" y="324" class="value">39.607M · ≈0.6047</text>
      <text x="1203" y="344" class="detail">gemini-3.7-flash multi-branch</text>
    </g>
    <g class="meta">
      <path d="M1514 343H1690 M1514 330V356 M1690 330V356" class="range"/>
      <path d="M1602 327l23 31h-46z"/>
      <text x="1454" y="441" class="name">SciOdyssey with Antigravity</text>
      <text x="1454" y="465" class="value">45.04–51.17M · 0.60520</text>
      <text x="1454" y="485" class="detail">gemini-3.7-flash-only (E008)</text>
    </g>
    <g class="retained">
      <circle cx="1605" cy="271" r="11" class="verified"/>
      <text x="1454" y="200" class="name">★ SciOdyssey submission</text>
      <text x="1454" y="224" class="value">48.240M · 0.6059363</text>
      <text x="1454" y="244" class="detail retained-detail">retained verified submission</text>
    </g>
    <g class="legend">
      <circle cx="160" cy="806" r="10" class="direct"/><text x="185" y="815">direct run (AGY / Codex)</text>
      <path d="M567 797l13 9-13 9-13-9z" class="heterogeneous"/><text x="594" y="815">heterogeneous run</text>
      <path d="M917 795l14 18h-28z" class="meta"/><text x="946" y="815">SciOdyssey with Antigravity</text>
      <circle cx="1370" cy="806" r="10" class="retained"/><text x="1396" y="815">retained verified result (0.605936)</text>
    </g>
  </svg>
</template>
<style scoped>
.resource-scatter { display:block; margin:0; padding:0; border:0; border-radius:0; background:transparent; box-shadow:none; overflow:visible; font-family:var(--deck-sans); }
.kicker {fill:var(--green);font-size:29px;font-weight:750;letter-spacing:3px}
.title {fill:var(--ink);font-size:48px;font-weight:750;letter-spacing:-1.2px}
.cost {fill:var(--orange);font-size:25px;font-weight:700}
.subtitle {fill:#718090;font-size:23px;letter-spacing:.6px}
.grid {stroke:#d9e1e8;stroke-width:1.3;fill:none}
.ticks {fill:#586b7a;font-size:26px;font-weight:600;font-variant-numeric:tabular-nums}
.axis-title {fill:var(--ink);font-size:29px;font-weight:700}
.reference {stroke:#94a5b6;stroke-width:2;stroke-dasharray:8 6;fill:none}
.reference-label {fill:#637585;font-size:24px;font-weight:600}
.leaders {stroke:#96a7b6;stroke-width:2;stroke-dasharray:4 4;fill:none}
.direct {fill:#369ac6}.heterogeneous {fill:var(--orange)}.meta {fill:var(--purple)}.retained {fill:var(--green)}
.name {font-size:24px;font-weight:750}
.value {fill:#425463;font-size:22px;font-weight:650;font-variant-numeric:tabular-nums}
.detail {fill:#748393;font-size:20px;font-weight:550}
.retained-detail {fill:var(--green)}
.range {stroke:var(--purple);stroke-width:3;fill:none}
.verified {fill:none;stroke:var(--green);stroke-width:7}
.legend {fill:#586b7a;font-size:24px;font-weight:600}
</style>
