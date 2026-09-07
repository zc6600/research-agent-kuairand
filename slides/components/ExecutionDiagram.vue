<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ act: number; time: number }>()
const progress = (start: number, duration: number) => Math.max(0, Math.min(1, (props.time - start) / duration))
const rail = computed(() => progress(3300, props.act === 1 ? 5500 : 7500))
const labels = computed(() => props.act === 1 ? ['META', 'Scientist', 'Evidence', 'Your turn'] : ['Cycle 1', 'Cycle 2', 'Cycle 3', 'Cycle 4'])
const details = ['Scope the next question', 'Run the experiment', 'Audit & retain', 'Inspect the result']
const colors = ['#38bdf8', '#a66cff', '#ff873f']
const cycleReveal = (index: number) => progress(3300 + index * 2500, 550)
const cycleActive = (index: number) => {
  const start = 3300 + index * 2500
  const end = index === 3 ? 14000 : start + 2500
  return props.time >= start && props.time < end
}
</script>

<template>
  <div class="execution-diagram" :style="{ opacity: progress(2900, 500) }">
    <svg v-if="act < 3" viewBox="0 0 868 260" role="img" :aria-label="act === 1 ? 'One research cycle returns control after retaining evidence' : 'Four cycles; each starts with a fresh Scientist, then META audits and updates the research world'">
      <text v-if="act === 2" x="434" y="18" text-anchor="middle" class="run-caption">RUN · up to four bounded cycles</text>
      <path d="M90 60 H765" stroke="#e0e5ec" stroke-width="2" />
      <path d="M90 60 H765" stroke="#38bdf8" stroke-width="3" pathLength="1" stroke-dasharray="1" :stroke-dashoffset="1 - rail" />
      <circle v-if="act === 2" :cx="90 + rail * 675" cy="60" r="6" fill="#1476b5" :style="{ opacity: progress(3300, 400) }" />
      <g v-for="(x, i) in [90, 315, 540, 765]" :key="x">
        <circle :cx="x" cy="60" r="14" :fill="rail >= i / 3 ? '#e5f6fe' : '#f5f7fa'" :stroke="rail >= i / 3 ? '#38bdf8' : '#dce2ea'" stroke-width="2" />
        <text v-if="rail >= 1 || rail > (i + .2) / 3" :x="x" y="66" text-anchor="middle" class="check">✓</text>
        <text :x="x" y="112" text-anchor="middle" :class="['node-label', { 'run-node-label': act === 2 }]" :style="{ opacity: rail >= i / 3 ? 1 : .4 }">{{ labels[i] }}</text>
        <!-- act 1: detail labels below each node -->
        <g v-if="act === 1">
          <text :x="x" y="141" text-anchor="middle" class="node-detail">{{ details[i] }}</text>
        </g>
        <!-- act 2: each completed cycle materializes as one loop below its node -->
        <g v-if="act === 2" class="run-cycle-loop" :style="{ opacity: cycleReveal(i) * .74 }">
          <circle :cx="x" cy="165" r="30" fill="white" stroke="#e7eef2" stroke-width="1.25" />
          <circle :cx="x" cy="165" r="30" fill="none" stroke="#9ed5e5" stroke-width="2" pathLength="1" stroke-dasharray="1" :stroke-dashoffset="1 - cycleReveal(i)" stroke-linecap="round" />
          <circle v-if="cycleActive(i)" :cx="x" cy="165" r="35" fill="none" stroke="#b7e2ec" stroke-width="1" :style="{ opacity: .16 + progress(3300 + i * 2500, 700) * .1 }" />
          <text :x="x" y="174" text-anchor="middle" class="loop-glyph">↻</text>
        </g>
      </g>
      <text v-if="act === 2" x="434" y="224" text-anchor="middle" class="run-flow-note" :style="{ opacity: progress(3300, 600) }">Fresh Scientist → META audit → updated research world</text>
      <text x="434" :y="act === 1 ? 217 : 250" text-anchor="middle" class="result" :style="{ opacity: progress(act === 1 ? 10800 : 12400, 600) }">{{ act === 1 ? '✓ Evidence retained. Control returned.' : '✓ Four audited cycles advanced one shared research world.' }}</text>
    </svg>
    <svg v-else-if="act === 3" viewBox="0 0 868 250" role="img" aria-label="Three independent Scientists branch from one research world and converge on a Reviewer">
      <g v-for="(y, i) in [40, 115, 190]" :key="y">
        <path :d="`M70 115 C180 115 180 ${y} 265 ${y} H570 C670 ${y} 680 115 790 115`" fill="none" stroke="#e0e5ec" stroke-width="2" />
        <path :d="`M70 115 C180 115 180 ${y} 265 ${y} H570 C670 ${y} 680 115 790 115`" fill="none" :stroke="colors[i]" stroke-width="3" pathLength="1" stroke-dasharray="1" :stroke-dashoffset="1 - progress(3400 + i * 450, 7200)" />
        <g :style="{ opacity: progress(3300 + i * 250, 650) }">
          <rect x="265" :y="y - 24" width="305" height="48" rx="12" fill="white" stroke="#dfe5ed" />
          <circle cx="284" :cy="y" r="4" :fill="colors[i]" />
          <text x="300" :y="y + 6" class="branch-label">Scientist {{ String.fromCharCode(65 + i) }}</text>
          <text x="550" :y="y + 5" text-anchor="end" class="node-detail">{{ time > 10000 + i * 450 ? '✓ complete' : `r1b${i + 1}` }}</text>
        </g>
      </g>
      <circle cx="70" cy="115" r="12" fill="#38bdf8" />
      <text x="70" y="152" text-anchor="middle" class="node-detail">Research world</text>
      <circle cx="790" cy="115" r="12" :fill="time > 11800 ? '#20b68d' : '#cdd3dc'" />
      <circle cx="790" cy="115" :r="20 + progress(11800, 1000) * 8" fill="none" stroke="#20b68d" :style="{ opacity: progress(11800, 1000) * .4 }" />
      <text x="790" y="152" text-anchor="middle" class="node-detail">Reviewer</text>
      <text x="434" y="241" text-anchor="middle" class="parallel-result" :style="{ opacity: progress(12700, 600) }">Branches reviewed · adopt explicitly with parallel-promote</text>
    </svg>
    <div v-else class="dashboard-act" :style="{ opacity: progress(2900, 500) }">
      <div class="dashboard-window" :style="{ opacity: progress(3800, 900), transform: `translateY(${(1 - Math.min(1, Math.max(0, (time - 3800) / 900))) * 16}px)` }">
        <div class="dashboard-bar">
          <span class="dashboard-dot" />
          <span class="dashboard-title">Research Agent Dashboard</span>
          <span class="dashboard-live">read-only</span>
        </div>
        <img src="/assets/dashboard-result.png" class="dashboard-img" alt="Research Agent Dashboard showing retained validation result S004 with Primary score 0.605936" />
      </div>
      <div class="dashboard-caption" :style="{ opacity: progress(8000, 600) }">
        <span class="dashboard-check">✓</span> Retained checkpoint S004 · Primary <strong>0.605936</strong> · evidence on record
      </div>
    </div>
  </div>
</template>

<style scoped>
.execution-diagram { margin-top: 28px; }
svg { display: block; width: 868px; height: 260px; overflow: visible; }
svg text { font-family: 'Nunito', sans-serif; font-size: 14px; fill: #111217; }
svg .node-label { font-size: 21px; font-weight: 700; }
svg .run-node-label { font-size: 18px; font-weight: 600; }
svg .node-detail { font-size: 12px; fill: #7e8998; }
svg .branch-label { font-size: 17px; }
svg .check { font-size: 17px; fill: #29a4dc; }
svg .result { font-size: 17px; fill: #269b7d; }
svg .parallel-result { font-size: 13px; fill: #698075; }
svg .run-caption { font-size: 12px; fill: #7e8998; }
svg .loop-glyph { font-size: 24px; font-weight: 500; fill: #5a9bb0; }
svg .run-flow-note { font-size: 11px; fill: #7e8998; }
.dashboard-act { display: flex; flex-direction: column; align-items: center; gap: 10px; padding-top: 4px; }
.dashboard-window { width: 740px; border: 1px solid #dce2ea; border-radius: 10px; overflow: hidden; box-shadow: 0 8px 28px #23354c0d; background: #fff; will-change: opacity, transform; }
.dashboard-bar { height: 34px; display: flex; align-items: center; gap: 10px; padding: 0 14px; background: #f4f6f9; border-bottom: 1px solid #e4e8ef; }
.dashboard-dot { width: 8px; height: 8px; border-radius: 50%; background: #20b68d; flex-shrink: 0; }
.dashboard-title { font: 11px 'Nunito', sans-serif; color: #3d4755; flex: 1; }
.dashboard-live { font: 10px ui-monospace, monospace; color: #20b68d; border: 1px solid #20b68d44; border-radius: 4px; padding: 2px 6px; }
.dashboard-img { display: block; width: 100%; height: 190px; object-fit: cover; object-position: center top; }
.dashboard-caption { font: 12px 'Nunito', sans-serif; color: #698075; display: flex; align-items: center; gap: 6px; }
.dashboard-check { color: #20b68d; font-weight: 800; }
.dashboard-caption strong { color: #269b7d; }
</style>
