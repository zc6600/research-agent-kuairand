<script setup lang="ts">
// Order matches table: GAUC, nDCG@5, Primary
const data = [
  { name: 'GAUC', base: '0.6674', ours: '0.6728', delta: '+0.0054', hBase: 78, hOurs: 94 },
  { name: 'nDCG@5', base: '0.5357', ours: '0.5390', delta: '+0.0033', hBase: 50, hOurs: 60 },
  { name: 'Primary', base: '0.6016', ours: '0.6059', delta: '+0.0043', hBase: 62, hOurs: 78 }
]
const groundY = 118
</script>

<template>
  <div class="bars-widget">
    <div class="bars-legend">
      <span class="legend-chip"><i class="chip-dot dot-gray" /> Official</span>
      <span class="legend-chip"><i class="chip-dot dot-blue" /> Ours</span>
    </div>
    <svg viewBox="0 0 255 142" class="bars-svg" role="img" aria-label="Metric comparison">
      <!-- Ground line -->
      <line x1="8" :y1="groundY" x2="246" :y2="groundY" stroke="#e6e6e8" stroke-width="1" />

      <g v-for="(item, idx) in data" :key="item.name" :transform="`translate(${14 + idx * 80}, 0)`">
        <!-- Baseline bar -->
        <rect
          x="0"
          :y="groundY - item.hBase"
          width="17"
          :height="item.hBase"
          rx="3"
          fill="#e2e8f0"
        />
        <text
          x="8.5"
          :y="groundY - item.hBase - 4"
          text-anchor="middle"
          class="txt-base"
        >
          {{ item.base }}
        </text>

        <!-- Ours bar (gap widened from 5px to 14px to eliminate text collision) -->
        <rect
          x="31"
          :y="groundY - item.hOurs"
          width="17"
          :height="item.hOurs"
          rx="3"
          fill="#38bdf8"
        />
        <text
          x="39.5"
          :y="groundY - item.hOurs - 4"
          text-anchor="middle"
          class="txt-ours"
        >
          {{ item.ours }}
        </text>

        <!-- Delta -->
        <text
          x="39.5"
          :y="groundY - item.hOurs - 14"
          text-anchor="middle"
          class="txt-delta"
        >
          {{ item.delta }}
        </text>

        <!-- Label -->
        <text
          x="24"
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
  padding-top: 2px;
}

.bars-legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  font-size: 11px;
  font-family: var(--deck-sans);
  color: var(--muted, #7d7d82);
  margin-bottom: 8px;
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
  background: #cbd5e1;
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
  font-family: var(--deck-mono);
  font-size: 8px;
  fill: #64748b;
  font-weight: 500;
  letter-spacing: -0.2px;
}

.txt-ours {
  font-family: var(--deck-mono);
  font-size: 8.5px;
  fill: #0284c7;
  font-weight: 600;
  letter-spacing: -0.2px;
}

.txt-delta {
  font-family: var(--deck-mono);
  font-size: 7.5px;
  fill: #16803b;
  font-weight: 600;
  letter-spacing: -0.1px;
}

.txt-name {
  font-family: var(--deck-sans);
  font-size: 11px;
  font-weight: 600;
  fill: var(--ink, #111217);
}
</style>
