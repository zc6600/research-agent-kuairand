<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { onSlideEnter, onSlideLeave, useNav } from '@slidev/client'

const { isPrintMode } = useNav()
const phase = ref(0)
const playing = ref(false)
let timers: number[] = []

// SciOdyssey: 7 Full evaluations across 4 cycles
const points = [
  { id: 'E003', score: 0.6016310, reveal: 1 },
  { id: 'E004', score: 0.6016310, reveal: 1 },
  { id: 'E007', score: 0.6030889, reveal: 2 },
  { id: 'E008', score: 0.6040901, reveal: 2 },
  { id: 'E009', score: 0.6044289, reveal: 3 },
  { id: 'E012', score: 0.6054846, reveal: 4 },
  { id: 'E013', score: 0.6059363, reveal: 5 },
]

// Codex: All 11 real cycles from CODEX_GOAL_BENCHMARK.json (baseline_runs)
const codexPoints = [
  { id: 'C1', cycle: 1, score: 0.6014688, x: 76, reveal: 1 },
  { id: 'C2', cycle: 2, score: 0.6018191, x: 154, reveal: 1 },
  { id: 'C3', cycle: 3, score: 0.6037582, x: 232, reveal: 2 },
  { id: 'C4', cycle: 4, score: 0.6033237, x: 310, reveal: 2 },
  { id: 'C5', cycle: 5, score: 0.6038590, x: 388, reveal: 2 },
  { id: 'C6', cycle: 6, score: 0.6036605, x: 466, reveal: 2 },
  { id: 'C7', cycle: 7, score: 0.6042327, x: 544, reveal: 3 },
  { id: 'C8', cycle: 8, score: 0.6044533, x: 623, reveal: 4 },
  { id: 'C9', cycle: 9, score: 0.6040408, x: 701, reveal: 4 },
  { id: 'C10', cycle: 10, score: 0.6038737, x: 780, reveal: 5 },
  { id: 'C11', cycle: 11, score: 0.5934564, x: 858, reveal: 5 },
]

const cycles = [
  { label: 'Cycle 1', range: 'E001–E004', title: 'Establish a valid baseline', detail: 'Reject weak target encoding; retain a recoverable 15-field FM.', score: '0.6016310', color: 'blue', reveal: 1 },
  { label: 'Cycle 2', range: 'E005–E008', title: 'Expand the representation', detail: '38 fields plus a 5-seed ensemble breaks the 0.6016 plateau.', score: '0.6040901', color: 'orange', reveal: 2 },
  { label: 'Cycle 3', range: 'E009', title: 'Reduce optimization variance', detail: 'Eight-seed ensemble stabilizes variance and expands the frontier.', score: '0.6044289', color: 'purple', reveal: 3 },
  { label: 'Cycle 4', range: 'E010–E013', title: 'Retain the strongest recipe', detail: '46 feature interactions plus an 8-seed FM ensemble reaches the final score.', score: '0.6059363', color: 'aqua', reveal: 4 },
]

const chart = { left: 58, right: 882, top: 25, bottom: 158, min: 0.6013, max: 0.6061 }
const xCoords = [76, 142, 302, 394, 558, 724, 858]
const clipWidths = [0, 223, 476, 641, 795, 920]

const plotted = computed(() => points.map((point, index) => ({
  ...point,
  x: xCoords[index],
  y: chart.bottom - ((point.score - chart.min) / (chart.max - chart.min)) * (chart.bottom - chart.top),
})))

const codexPlotted = computed(() => codexPoints.map(point => {
  const normalizedY = chart.bottom - ((point.score - chart.min) / (chart.max - chart.min)) * (chart.bottom - chart.top)
  return {
    ...point,
    y: Math.min(chart.bottom, normalizedY),
  }
}))

const codexFullPath = computed(() => codexPlotted.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x} ${p.y}`).join(' '))
const codexClipWidth = computed(() => clipWidths[phase.value])
const baselineY = computed(() => chart.bottom - ((0.6016 - chart.min) / (chart.max - chart.min)) * (chart.bottom - chart.top))

const segmentPath = (index: number) => {
  const a = plotted.value[index]
  const b = plotted.value[index + 1]
  return `M${a.x} ${a.y} L${b.x} ${b.y}`
}

const clearTimers = () => {
  timers.forEach(timer => window.clearTimeout(timer))
  timers = []
  playing.value = false
}

const play = () => {
  clearTimers()
  if (isPrintMode.value || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    phase.value = 5
    return
  }
  phase.value = 0
  playing.value = true
  ;[1, 2, 3, 4, 5].forEach((value, index) => {
    timers.push(window.setTimeout(() => {
      phase.value = value
      if (value === 5) playing.value = false
    }, 350 + index * 560))
  })
}

onMounted(play)
onSlideEnter(play)
onSlideLeave(clearTimers)
onBeforeUnmount(clearTimers)
</script>

<template>
  <div class="evaluation-trajectory">
    <div class="trajectory-topline">
      <div class="trajectory-legend">
        <span class="legend-item is-sciodyssey"><i class="legend-line"></i><i class="legend-dot"></i> SciOdyssey (Our agent)</span>
        <span class="legend-item is-codex"><i class="legend-line is-dashed"></i><i class="legend-dot"></i> Direct Codex (gpt-5.6-luna)</span>
        <button v-if="!isPrintMode" class="trajectory-replay" :disabled="playing" @click.stop="play">↻ Replay</button>
      </div>
      <div class="trajectory-final-score">
        <span class="mono">E013 / FINAL</span>
        <strong>0.6059363</strong>
        <small>+0.00148 vs Codex peak · +0.00434 vs reference</small>
      </div>
    </div>

    <svg class="trajectory-chart" viewBox="0 0 920 176" role="img" aria-label="Public-validation Primary score comparison: SciOdyssey rises monotonically to 0.6059363 while Codex runs 11 cycles, peaks at 0.6044533, and regresses">
      <defs>
        <clipPath id="codex-clip">
          <rect x="0" y="0" :width="codexClipWidth" height="176" class="codex-clip-rect" />
        </clipPath>
      </defs>

      <line :x1="chart.left" :x2="chart.right" :y1="baselineY" :y2="baselineY" class="trajectory-baseline" />
      <text x="280" :y="baselineY - 7" class="trajectory-baseline-label">official reference · 0.601600</text>
      <line :x1="chart.left" :x2="chart.right" :y1="chart.bottom" :y2="chart.bottom" class="trajectory-axis" />
      <g class="trajectory-cycle-guides">
        <line x1="223" y1="26" x2="223" y2="158" />
        <line x1="476" y1="26" x2="476" y2="158" />
        <line x1="641" y1="26" x2="641" y2="158" />
      </g>

      <!-- Codex dashed line (11 real cycles, subtle light grey, animated via clip-path) -->
      <path
        :d="codexFullPath"
        class="trajectory-codex-line"
        clip-path="url(#codex-clip)"
      />

      <!-- SciOdyssey segments (solid hero blue) -->
      <g class="trajectory-segments">
        <path
          v-for="(_, index) in points.slice(0, -1)"
          :key="`segment-${index}`"
          :d="segmentPath(index)"
          pathLength="1"
          class="trajectory-segment"
          :class="{ revealed: phase >= points[index + 1].reveal }"
        />
      </g>

      <!-- Codex points & labels (11 real cycles, light grey below nodes) -->
      <g v-for="point in codexPlotted" :key="`codex-${point.id}`" class="trajectory-codex-point" :class="{ revealed: phase >= point.reveal, peak: point.id === 'C8' }">
        <circle :cx="point.x" :cy="point.y" :r="point.id === 'C8' ? 4.5 : 2.6" />
        <text :x="point.x" :y="point.id === 'C11' ? point.y + 11 : point.y + 12" text-anchor="middle">{{ point.id }}</text>
      </g>

      <!-- SciOdyssey points & labels (above nodes) -->
      <g v-for="point in plotted" :key="point.id" class="trajectory-point" :class="{ revealed: phase >= point.reveal, final: point.id === 'E013' }">
        <circle :cx="point.x" :cy="point.y" :r="point.id === 'E013' ? 7 : 4.5" />
        <text :x="point.x" :y="point.y - 13" text-anchor="middle">{{ point.id }}</text>
      </g>

      <!-- SciOdyssey final callout -->
      <g class="trajectory-final-callout" :class="{ revealed: phase >= 5 }">
        <path d="M858 24 L858 8 L708 8" />
        <text x="702" y="6" text-anchor="end">final retained checkpoint · 0.60594</text>
      </g>

      <!-- Codex peak callout at C8 (clean vertical stem) -->
      <g class="trajectory-codex-callout" :class="{ revealed: phase >= 4 }">
        <line x1="623" y1="75" x2="623" y2="114" />
        <text x="623" y="125" text-anchor="middle">Codex peak · 0.60445</text>
      </g>

      <!-- Vertical delta bracket at x=869 (between E013 and Codex peak 0.60445) -->
      <g class="trajectory-delta-bracket" :class="{ revealed: phase >= 5 }">
        <line x1="869" y1="31" x2="869" y2="70" />
        <line x1="865" y1="31" x2="869" y2="31" />
        <line x1="865" y1="70" x2="869" y2="70" />
        <text x="876" y="54" text-anchor="start">+0.00148</text>
      </g>
    </svg>

    <div class="trajectory-cycles">
      <article v-for="cycle in cycles" :key="cycle.label" class="trajectory-cycle" :class="[`is-${cycle.color}`, { revealed: phase >= cycle.reveal }]">
        <div class="trajectory-cycle-head"><span>{{ cycle.label }}</span><small class="mono">{{ cycle.range }}</small></div>
        <strong>{{ cycle.title }}</strong>
        <p>{{ cycle.detail }}</p>
      </article>
    </div>
  </div>
</template>

<style scoped>
.evaluation-trajectory { position: relative; margin-top: 0; color: #33343a; }
.trajectory-topline { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 2px 0 6px; }
.trajectory-legend { display: flex; align-items: center; gap: 20px; font-size: 11.5px; font-weight: 650; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-item.is-sciodyssey { color: var(--blue); }
.legend-item.is-codex { color: #8b98a5; }
.legend-line { width: 16px; height: 2px; border-radius: 1px; display: inline-block; }
.legend-line.is-dashed { width: 18px; height: 0; border-top: 1.5px dashed #b8c2cc; background: transparent; }
.legend-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.is-sciodyssey .legend-line { background: var(--blue); }
.is-sciodyssey .legend-dot { background: var(--blue); }
.is-codex .legend-dot { background: #b8c2cc; width: 4.5px; height: 4.5px; }
.trajectory-final-score { min-width: 185px; text-align: right; }
.trajectory-final-score span { color: var(--blue); font-size: 10px; letter-spacing: 1px; }
.trajectory-final-score strong { display: block; color: var(--blue); font-size: 28px; line-height: 1; letter-spacing: -.8px; margin-top: 2px; }
.trajectory-final-score small { color: #16803b; font-size: 10px; }
.trajectory-chart { display: block; width: 100%; height: 180px; margin-top: 0; overflow: visible; }
.trajectory-chart text { font-family: var(--deck-sans); }
.trajectory-axis { stroke: #e6e6e8; stroke-width: 1; }
.trajectory-baseline { stroke: #b9c8d0; stroke-width: 1; stroke-dasharray: 4 5; }
.trajectory-baseline-label { fill: #82929b; font-size: 10px; }
.trajectory-cycle-guides line { stroke: #eef0f2; stroke-width: 1; stroke-dasharray: 2 5; }

/* SciOdyssey segment styles */
.trajectory-segment { fill: none; stroke: var(--blue); stroke-width: 3; stroke-linecap: round; stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset .62s cubic-bezier(.22,1,.36,1); }
.trajectory-segment.revealed { stroke-dashoffset: 0; }
.trajectory-point { opacity: 0; transition: opacity .35s ease, transform .35s cubic-bezier(.34, 1.56, .64, 1); transform-box: fill-box; transform-origin: center; transform: scale(0.6); }
.trajectory-point.revealed { opacity: 1; transform: scale(1); }
.trajectory-point circle { fill: #fff; stroke: var(--blue); stroke-width: 2; }
.trajectory-point text { fill: #71818b; font-size: 10px; font-weight: 700; }
.trajectory-point.final circle { fill: var(--blue); stroke: var(--blue); }
.trajectory-point.final text { fill: #167aa9; }

/* Codex dashed line & points (Subtle, light grey, non-intrusive) */
.trajectory-codex-line { fill: none; stroke: #b8c2cc; stroke-width: 1.4; stroke-dasharray: 4 4; opacity: 0.85; }
.codex-clip-rect { transition: width .58s cubic-bezier(.22,1,.36,1); }
.trajectory-codex-point { opacity: 0; transition: opacity .35s ease, transform .35s cubic-bezier(.34, 1.56, .64, 1); transform-box: fill-box; transform-origin: center; transform: scale(0.6); }
.trajectory-codex-point.revealed { opacity: 1; transform: scale(1); }
.trajectory-codex-point circle { fill: #fff; stroke: #b0bac5; stroke-width: 1.3; }
.trajectory-codex-point text { fill: #9aa5b1; font-size: 8px; font-weight: 600; }
.trajectory-codex-point.peak circle { fill: #8b98a5; stroke: #8b98a5; }

/* Callouts & Brackets */
.trajectory-final-callout { opacity: 0; transition: opacity .45s ease; }
.trajectory-final-callout.revealed { opacity: 1; }
.trajectory-final-callout path { fill: none; stroke: var(--blue); stroke-width: 1.2; }
.trajectory-final-callout text { fill: #167aa9; font-size: 10px; }

.trajectory-codex-callout { opacity: 0; transition: opacity .45s ease; }
.trajectory-codex-callout.revealed { opacity: 1; }
.trajectory-codex-callout line { stroke: #b8c2cc; stroke-width: 1; stroke-dasharray: 2 3; }
.trajectory-codex-callout text { fill: #8b98a5; font-size: 9.5px; font-weight: 600; }

.trajectory-delta-bracket { opacity: 0; transition: opacity .45s ease; }
.trajectory-delta-bracket.revealed { opacity: 1; }
.trajectory-delta-bracket line { stroke: #16803b; stroke-width: 1.3; }
.trajectory-delta-bracket text { fill: #16803b; font-size: 9.5px; font-weight: 800; font-family: var(--deck-mono); }

/* Cycle cards (Clean, balanced SciOdyssey 4-cycle structure) */
.trajectory-cycles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 4px; }
.trajectory-cycle { min-height: 82px; border-top: 2.5px solid #dfe5e8; border-radius: 0 0 6px 6px; background: #fafbfc; padding: 8px 10px 7px; opacity: .18; transform: translateY(7px); transition: opacity .5s ease, transform .5s cubic-bezier(.22,1,.36,1), border-color .3s ease; }
.trajectory-cycle.revealed { opacity: 1; transform: translateY(0); }
.trajectory-cycle.is-blue { border-color: rgba(56, 189, 248, .75); }
.trajectory-cycle.is-orange { border-color: rgba(255, 135, 63, .75); }
.trajectory-cycle.is-purple { border-color: rgba(166, 108, 255, .7); }
.trajectory-cycle.is-aqua { border-color: rgba(32, 217, 160, .85); background: #f0faf6; }
.trajectory-cycle-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; color: #3d4755; }
.trajectory-cycle-head span { font-size: 13px; font-weight: 800; }
.trajectory-cycle-head small { color: #98a3aa; font-size: 9px; }
.trajectory-cycle strong { display: block; color: #33343a; font-size: 11.5px; line-height: 1.22; margin-top: 3px; }
.trajectory-cycle p { color: #7d7d82; font-size: 9.5px; line-height: 1.25; margin: 3px 0 0; }

.trajectory-replay {
  border: 1px solid #d0dbe2;
  border-radius: 4px;
  background: #f8fafc;
  color: #64748b;
  cursor: pointer;
  font-size: 10.5px;
  font-weight: 600;
  padding: 1px 7px;
  margin-left: 8px;
  line-height: 1.3;
  transition: all .2s ease;
}
.trajectory-replay:hover:not(:disabled) {
  background: #e2e8f0;
  color: #1e293b;
  border-color: #cbd5e1;
}
.trajectory-replay:disabled { opacity: .35; cursor: default; }
.trajectory-replay:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  .trajectory-segment, .trajectory-codex-line, .codex-clip-rect, .trajectory-point, .trajectory-codex-point, .trajectory-final-callout, .trajectory-codex-callout, .trajectory-delta-bracket, .trajectory-cycle { transition: none; }
}
@media print {
  .trajectory-segment { stroke-dashoffset: 0; }
  .codex-clip-rect { width: 920px; }
  .trajectory-point, .trajectory-codex-point, .trajectory-final-callout, .trajectory-codex-callout, .trajectory-delta-bracket, .trajectory-cycle { opacity: 1; transform: none; }
  .trajectory-replay { display: none; }
}
</style>
