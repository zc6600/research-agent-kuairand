<script setup lang="ts">
import { onSlideLeave, useNav } from '@slidev/client'
import { ref } from 'vue'
import { insightDefinitions, insightSynthesis } from '../composables/insightSynthesis'

const root = ref<HTMLElement>()
const { nextSlide } = useNav()
const earned = (index: number) => index === 0
  ? insightSynthesis.learned.workflow
  : index === 3 ? insightSynthesis.learned.tree : insightSynthesis.learned.single

function captureOrigins() {
  const slide = root.value?.closest('.slidev-layout') as HTMLElement | null
  if (!slide) return
  const bounds = slide.getBoundingClientRect()
  const scale = bounds.width / slide.offsetWidth
  insightSynthesis.origins = Array.from(root.value!.querySelectorAll('.insight-chip')).map(el => {
    const box = el.getBoundingClientRect()
    return { x: (box.x - bounds.x) / scale, y: (box.y - bounds.y) / scale, width: box.width / scale, height: box.height / scale }
  })
}

function buildSystem() {
  captureOrigins()
  nextSlide()
}

onSlideLeave(captureOrigins)
</script>

<template>
  <section ref="root" class="problem-insights">
    <div class="failure-modes-grid failure-modes-focused">
      <FailureModeFlip01 @insight="insightSynthesis.learned.workflow = $event" />
      <SingleTrajectoryFlip @insight="insightSynthesis.learned.single = $event" />
      <TreeSearchFlip @insight="insightSynthesis.learned.tree = $event" />
    </div>
    <div class="insight-collection" @click.stop>
      <span v-for="(insight, index) in insightDefinitions" :key="insight.id"
        class="insight-chip" :class="{ earned: earned(index) }" :style="{ '--insight-color': insight.color }">
        <i aria-hidden="true"></i>{{ insight.label }}
      </span>
      <button class="insight-build" @click="buildSystem">Build the system <span aria-hidden="true">→</span></button>
    </div>
  </section>
</template>

<style scoped>
.insight-collection { display: grid; grid-template-columns: repeat(4, 1fr) auto; gap: 12px; align-items: center; border-top: 1px solid var(--line); margin-top: 24px; padding-top: 17px; }
.insight-chip { display: inline-flex; align-items: center; gap: 7px; font-size: 13px; font-weight: 500; color: var(--muted); height: 32px; transition: color .6s ease, translate .6s cubic-bezier(.22,1,.36,1); }
.insight-chip i { width: 5px; height: 5px; border-radius: 50%; background: var(--insight-color); opacity: .3; transition: opacity .6s, box-shadow .6s; }
.insight-chip.earned { color: var(--ink); translate: 0 -2px; }
.insight-chip.earned i { opacity: 1; box-shadow: 0 0 0 4px color-mix(in srgb, var(--insight-color) 12%, transparent); }
.insight-build { border: 0; background: none; cursor: pointer; font: inherit; font-size: 12px; color: var(--ink); padding: 7px 0 7px 12px; white-space: nowrap; }
.insight-build span { display: inline-block; margin-left: 5px; transition: transform .2s; }
.insight-build:hover span { transform: translateX(3px); }
.insight-build:focus-visible { outline: 2px solid var(--blue); outline-offset: 4px; }
@media (prefers-reduced-motion: reduce) { .insight-chip, .insight-chip i, .insight-build span { transition: none; } }
</style>
