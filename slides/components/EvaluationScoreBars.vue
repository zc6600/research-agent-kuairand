<script setup lang="ts">
// Order matches table: GAUC, nDCG@5, Primary
const data = [
  { name: 'GAUC', base: '0.6674', ours: '0.6728', delta: '+0.0054', hBase: 78, hOurs: 94 },
  { name: 'nDCG@5', base: '0.5282', ours: '0.5390', delta: '+0.0108', hBase: 44, hOurs: 60 },
  { name: 'Primary', base: '0.6016', ours: '0.6059', delta: '+0.0043', hBase: 62, hOurs: 78 }
]
const groundY = 115
</script>

<template>
  <div class="bars-widget">
    <div class="bars-legend">
      <span class="legend-chip"><i class="chip-dot dot-gray" /> Official</span>
      <span class="legend-chip"><i class="chip-dot dot-blue" /> Ours</span>
    </div>
    <svg viewBox="0 0 255 138" class="bars-svg" role="img" aria-label="Metric comparison">
      <!-- Ground line -->
      <line x1="8" :y1="groundY" x2="248" :y2="groundY" stroke="#e6e6e8" stroke-width="1" />

      <g v-for="(item, idx) in data" :key="item.name" :transform="`translate(${14 + idx * 80}, 0)`">
        <!-- Baseline bar -->
        <rect
          x="0"
          :y="groundY - item.hBase"
          width="18"
          :height="item.hBase"
          rx="3"
          fill="#e2e8f0"
        />
        <text
          x="9"
          :y="groundY - item.hBase - 4"
          text-anchor="middle"
          class="txt-base"
        >
          {{ item.base }}
        </text>

        <!-- Ours bar -->
        <rect
          x="23"
          :y="groundY - item.hOurs"
          width="18"
          :height="item.hOurs"
          rx="3"
          fill="#38bdf8"
        />
        <text
          x="32"
          :y="groundY - item.hOurs - 4"
          text-anchor="middle"
          class="txt-ours"
        >
          {{ item.ours }}
        </text>

        <!-- Delta -->
        <text
          x="32"
          :y="groundY - item.hOurs - 14"
          text-anchor="middle"
          class="txt-delta"
        >
          {{ item.delta }}
        </text>

        <!-- Label -->
        <text
          x="20"
          :y="groundY + 16"
          text-anchor="middle"
          class="txt-name"
        >
          {{ item.name }}
        </text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.bars-widget {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.bars-legend {
  display: flex;
  justify-content: center;
  gap: 14px;
  font-size: 11px;
  font-family: 'Nunito', sans-serif;
  color: var(--muted, #7d7d82);
  margin-bottom: 6px;
  width: 100%;
}

.legend-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.chip-dot {
  width: 7px;
  height: 7px;
  border-radius: 2px;
  display: inline-block;
}

.dot-gray {
  background: #e2e8f0;
}

.dot-blue {
  background: #38bdf8;
}

.bars-svg {
  display: block;
  width: 100%;
  height: auto;
  max-width: 255px;
  overflow: visible;
}

.txt-base {
  font-family: 'Fira Code', monospace;
  font-size: 8.5px;
  fill: #8e95a0;
  font-weight: 500;
}

.txt-ours {
  font-family: 'Fira Code', monospace;
  font-size: 9px;
  fill: #0284c7;
  font-weight: 700;
}

.txt-delta {
  font-family: 'Fira Code', monospace;
  font-size: 8px;
  fill: #16803b;
  font-weight: 700;
}

.txt-name {
  font-family: 'Nunito', sans-serif;
  font-size: 11px;
  font-weight: 700;
  fill: var(--ink, #111217);
}
</style>
