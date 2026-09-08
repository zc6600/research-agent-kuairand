<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { onSlideEnter, onSlideLeave, useNav } from '@slidev/client'

const { isPrintMode } = useNav()
const phase = ref(0)
const playing = ref(false)
let timers: number[] = []

const points = [
  { id: 'E003', score: 0.6016310, reveal: 1 },
  { id: 'E004', score: 0.6016310, reveal: 1 },
  { id: 'E007', score: 0.6030889, reveal: 2 },
  { id: 'E008', score: 0.6040901, reveal: 2 },
  { id: 'E009', score: 0.6044289, reveal: 3 },
  { id: 'E012', score: 0.6054846, reveal: 4 },
  { id: 'E013', score: 0.6059363, reveal: 5 },
]

const cycles = [
  { label: 'Cycle 1', range: 'E001–E004', title: 'Establish a valid baseline', detail: 'Reject weak target encoding; retain a recoverable 15-field FM.', score: '0.6016310', color: 'blue', reveal: 1 },
  { label: 'Cycle 2', range: 'E005–E008', title: 'Expand the representation', detail: '38 fields plus a 5-seed ensemble breaks the 0.6016 plateau.', score: '0.6040901', color: 'orange', reveal: 2 },
  { label: 'Cycle 3', range: 'E009', title: 'Reduce optimization variance', detail: 'Eight seeds improve the frontier, but only by a modest amount.', score: '0.6044289', color: 'purple', reveal: 3 },
  { label: 'Cycle 4', range: 'E010–E013', title: 'Retain the strongest recipe', detail: '46 leak-free fields plus an 8-seed FM ensemble reaches the final score.', score: '0.6059363', color: 'aqua', reveal: 4 },
]

const chart = { left: 58, right: 882, top: 25, bottom: 158, min: 0.6013, max: 0.6061 }
const plotted = computed(() => points.map((point, index) => ({
  ...point,
  x: [76, 142, 302, 394, 558, 724, 858][index],
  y: chart.bottom - ((point.score - chart.min) / (chart.max - chart.min)) * (chart.bottom - chart.top),
})))
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
      <div>
        <span class="trajectory-kicker mono">FULL PUBLIC VALIDATION / RETAINED CHECKPOINTS</span>
        <p>Seven Full evaluations across four autonomous cycles.</p>
      </div>
      <div class="trajectory-final-score">
        <span class="mono">E013 / FINAL</span>
        <strong>0.6059363</strong>
        <small>+0.0043363 vs official reference</small>
      </div>
    </div>

    <svg class="trajectory-chart" viewBox="0 0 920 210" role="img" aria-label="Public-validation Primary score rises from 0.601631 at E003 to 0.6059363 at E013 across four autonomous cycles">
      <line :x1="chart.left" :x2="chart.right" :y1="baselineY" :y2="baselineY" class="trajectory-baseline" />
      <text :x="chart.left" :y="baselineY - 8" class="trajectory-baseline-label">official reference · 0.601600</text>
      <line :x1="chart.left" :x2="chart.right" :y1="chart.bottom" :y2="chart.bottom" class="trajectory-axis" />
      <g class="trajectory-cycle-guides">
        <line x1="223" y1="30" x2="223" y2="178" />
        <line x1="476" y1="30" x2="476" y2="178" />
        <line x1="641" y1="30" x2="641" y2="178" />
      </g>
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
      <g v-for="point in plotted" :key="point.id" class="trajectory-point" :class="{ revealed: phase >= point.reveal, final: point.id === 'E013' }">
        <circle :cx="point.x" :cy="point.y" :r="point.id === 'E013' ? 7 : 4.5" />
        <text :x="point.x" :y="point.y - 13" text-anchor="middle">{{ point.id }}</text>
      </g>
      <g class="trajectory-final-callout" :class="{ revealed: phase >= 5 }">
        <path d="M858 37 L858 10 L708 10" />
        <text x="702" y="8" text-anchor="end">final retained checkpoint</text>
      </g>
      <text x="76" y="190" text-anchor="middle" class="trajectory-axis-label">C1</text>
      <text x="348" y="190" text-anchor="middle" class="trajectory-axis-label">C2</text>
      <text x="558" y="190" text-anchor="middle" class="trajectory-axis-label">C3</text>
      <text x="791" y="190" text-anchor="middle" class="trajectory-axis-label">C4</text>
    </svg>

    <div class="trajectory-cycles">
      <article v-for="cycle in cycles" :key="cycle.label" class="trajectory-cycle" :class="[`is-${cycle.color}`, { revealed: phase >= cycle.reveal }]">
        <div class="trajectory-cycle-head"><span>{{ cycle.label }}</span><small class="mono">{{ cycle.range }}</small></div>
        <strong>{{ cycle.title }}</strong>
        <p>{{ cycle.detail }}</p>
        <div class="trajectory-cycle-score"><span class="mono">FULL PRIMARY</span><b>{{ cycle.score }}</b></div>
      </article>
    </div>

    <div class="trajectory-foot">
      <span>Unchanged <code>starter_kit/evaluate.py</code></span>
      <span>124,909 public-validation rows · 22,377 users</span>
      <button v-if="!isPrintMode" class="trajectory-replay" :disabled="playing" @click.stop="play">↻ Replay</button>
    </div>
  </div>
</template>

<style scoped>
.evaluation-trajectory { position: relative; margin-top: 0; color: #33343a; }
.trajectory-topline { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; }
.trajectory-kicker { color: #7d7d82; font-size: 10px; letter-spacing: 1.25px; }
.trajectory-topline p { margin: 5px 0 0; color: #7d7d82; font-size: 13px; }
.trajectory-final-score { min-width: 185px; text-align: right; }
.trajectory-final-score span { color: var(--blue); font-size: 10px; letter-spacing: 1px; }
.trajectory-final-score strong { display: block; color: var(--blue); font-size: 29px; line-height: 1; letter-spacing: -.8px; margin-top: 2px; }
.trajectory-final-score small { color: #16803b; font-size: 10px; }
.trajectory-chart { display: block; width: 100%; height: 195px; margin-top: 2px; overflow: visible; }
.trajectory-chart text { font-family: 'Nunito', sans-serif; }
.trajectory-axis { stroke: #e6e6e8; stroke-width: 1; }
.trajectory-baseline { stroke: #b9c8d0; stroke-width: 1; stroke-dasharray: 4 5; }
.trajectory-baseline-label { fill: #82929b; font-size: 10px; }
.trajectory-cycle-guides line { stroke: #eef0f2; stroke-width: 1; stroke-dasharray: 2 5; }
.trajectory-segment { fill: none; stroke: var(--blue); stroke-width: 3; stroke-linecap: round; stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset .62s cubic-bezier(.22,1,.36,1); }
.trajectory-segment.revealed { stroke-dashoffset: 0; }
.trajectory-point { opacity: 0; transition: opacity .35s ease, transform .35s ease; transform-box: fill-box; transform-origin: center; }
.trajectory-point.revealed { opacity: 1; }
.trajectory-point circle { fill: #fff; stroke: var(--blue); stroke-width: 2; }
.trajectory-point text { fill: #71818b; font-size: 10px; font-weight: 700; }
.trajectory-point.final circle { fill: var(--blue); stroke: var(--blue); }
.trajectory-point.final text { fill: #167aa9; }
.trajectory-final-callout { opacity: 0; transition: opacity .45s ease; }
.trajectory-final-callout.revealed { opacity: 1; }
.trajectory-final-callout path { fill: none; stroke: var(--blue); stroke-width: 1.2; }
.trajectory-final-callout text { fill: #167aa9; font-size: 10px; }
.trajectory-axis-label { fill: #9ba5aa; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
.trajectory-cycles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 13px; margin-top: -2px; }
.trajectory-cycle { min-height: 89px; border-top: 2px solid #dfe5e8; padding: 7px 9px 5px; opacity: .18; transform: translateY(7px); transition: opacity .5s ease, transform .5s cubic-bezier(.22,1,.36,1), border-color .3s ease; }
.trajectory-cycle.revealed { opacity: 1; transform: translateY(0); }
.trajectory-cycle.is-blue { border-color: rgba(56, 189, 248, .56); }
.trajectory-cycle.is-orange { border-color: rgba(255, 135, 63, .56); }
.trajectory-cycle.is-purple { border-color: rgba(166, 108, 255, .46); }
.trajectory-cycle.is-aqua { border-color: rgba(32, 217, 160, .72); background: #f2fbf8; }
.trajectory-cycle-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; color: #3d4755; }
.trajectory-cycle-head span { font-size: 13px; font-weight: 800; }
.trajectory-cycle-head small { color: #98a3aa; font-size: 9px; }
.trajectory-cycle strong { display: block; color: #33343a; font-size: 12px; line-height: 1.2; margin-top: 4px; }
.trajectory-cycle p { color: #7d7d82; font-size: 10px; line-height: 1.25; margin: 3px 0 0; }
.trajectory-cycle-score { display: flex; align-items: baseline; justify-content: space-between; gap: 5px; margin-top: 5px; }
.trajectory-cycle-score span { color: #9aa5ab; font-size: 8px; letter-spacing: .8px; }
.trajectory-cycle-score b { color: #3d4755; font-size: 12px; }
.trajectory-cycle.is-aqua .trajectory-cycle-score b { color: #16803b; }
.trajectory-foot { display: flex; align-items: center; gap: 18px; border-top: 1px solid #e6e6e8; margin-top: 4px; padding-top: 5px; color: #8a949a; font-size: 10px; }
.trajectory-foot code { color: #536d78; font-family: 'Fira Code', monospace; font-size: 9px; }
.trajectory-foot span:nth-child(2) { margin-left: auto; }
.trajectory-replay { border: 0; background: transparent; color: #7d7d82; cursor: pointer; font: inherit; padding: 0 2px; }
.trajectory-replay:disabled { opacity: .35; cursor: default; }
.trajectory-replay:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  .trajectory-segment, .trajectory-point, .trajectory-final-callout, .trajectory-cycle { transition: none; }
}
@media print {
  .trajectory-segment { stroke-dashoffset: 0; }
  .trajectory-point, .trajectory-final-callout, .trajectory-cycle { opacity: 1; transform: none; }
  .trajectory-replay { display: none; }
}
</style>
