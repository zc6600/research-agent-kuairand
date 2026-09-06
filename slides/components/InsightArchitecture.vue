<script setup lang="ts">
import { onSlideEnter, onSlideLeave, useNav } from '@slidev/client'
import { nextTick, onBeforeUnmount, ref } from 'vue'
import { insightDefinitions, insightSynthesis } from '../composables/insightSynthesis'

const root = ref<HTMLElement>()
const running = ref(false)
const landing = ref(false)
const { isPrintMode } = useNav()
let run = 0
let animations: Animation[] = []

function finish() {
  run++
  animations.forEach(animation => animation.cancel())
  animations = []
  running.value = false
  landing.value = false
}

function motion(el: Element, frames: Keyframe[], options: KeyframeAnimationOptions) {
  const animation = el.animate(frames, { fill: 'both', easing: 'cubic-bezier(.22,1,.36,1)', ...options })
  animations.push(animation)
  return animation.finished.catch(() => {})
}

async function reveal() {
  finish()
  if (isPrintMode.value || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  const thisRun = run
  running.value = true
  await nextTick()
  const slide = root.value?.closest('.slidev-layout') as HTMLElement | null
  if (!slide || thisRun !== run) return finish()
  const box = slide.getBoundingClientRect()
  const scale = box.width / slide.offsetWidth
  const tokens = Array.from(root.value!.querySelectorAll('.synthesis-token'))
  const content = root.value!.querySelector('.synthesis-content')!
  const position = (x: number, y: number, width: number, height: number) => ({ left: `${x}px`, top: `${y}px`, width: `${width}px`, height: `${height}px` })

  // Carry the four source labels up into a single, quiet composition.
  await Promise.all(tokens.map((token, index) => {
    const origin = insightSynthesis.origins[index] ?? { x: 56 + index * 181, y: 476, width: 165, height: 32 }
    return motion(token, [
      { ...position(origin.x, origin.y, origin.width, origin.height), opacity: 0, fontSize: '13px' },
      { ...position(65 + index * 214, 226, 208, 56), opacity: 1, fontSize: '19px' },
    ], { duration: 900, delay: index * 75 })
  }))
  if (thisRun !== run) return

  // Hold the insights, then let their destination modules emerge underneath.
  await motion(content, [{ opacity: 0 }, { opacity: .16 }], { duration: 550, delay: 350 })
  if (thisRun !== run) return
  landing.value = true

  await Promise.all(tokens.map((token, index) => {
    const target = root.value!.querySelector(insightDefinitions[index].target)!
    const targetBox = target.getBoundingClientRect()
    const width = Math.max(130, Math.min(210, targetBox.width / scale))
    const x = (targetBox.x - box.x) / scale + (targetBox.width / scale - width) / 2
    const y = (targetBox.y - box.y) / scale
    const title = target.querySelector('.arch-area-title, .runtime-title')
    if (title) motion(title, [
      { opacity: 0 },
      { opacity: 0, offset: .82 },
      { opacity: 1 },
    ], { duration: 1350, delay: index * 100 })
    motion(target, [
      { filter: 'brightness(1)', transform: 'translateY(8px)' },
      { filter: 'brightness(1.04)', transform: 'translateY(0)' },
    ], { duration: 1000, delay: index * 100 })
    return motion(token, [
      { left: `${65 + index * 214}px`, top: '226px', width: '208px', height: '56px', opacity: 1, fontSize: '19px' },
      { ...position(x, y, width, 28), opacity: 1, fontSize: '14px', offset: .75 },
      { ...position(x, y, width, 28), opacity: 0, fontSize: '14px' },
    ], { duration: 1350, delay: index * 100 })
  }).concat(motion(content, [{ opacity: .16 }, { opacity: 1 }], { duration: 1500, delay: 150 })))
  if (thisRun === run) finish()
}

onSlideEnter((_to, from) => { if (from === 3) reveal() })
onSlideLeave(finish)
onBeforeUnmount(finish)
</script>

<template>
  <div ref="root" class="insight-architecture" :class="{ 'is-synthesizing': running }">
    <button v-if="!isPrintMode" class="synthesis-replay" @click.stop="reveal" :disabled="running" aria-label="Replay insight-to-system animation">↻ Replay</button>
    <div class="synthesis-content"><slot /></div>
    <div v-if="running" class="synthesis-stage" @click.stop="finish" aria-label="Insights becoming the system. Click to finish the animation.">
      <div v-for="insight in insightDefinitions" :key="insight.id" class="synthesis-token" :style="{ '--insight-color': insight.color }">
        <i></i><span>{{ landing ? insight.destination : insight.label }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.synthesis-replay { position: absolute; right: 56px; top: 27px; border: 0; background: none; color: var(--muted); font-family: inherit; font-size: 10px; cursor: pointer; padding: 5px; z-index: 5; }
.synthesis-replay:disabled { opacity: .3; cursor: default; }
.synthesis-replay:focus-visible { outline: 2px solid var(--blue); }
.is-synthesizing .synthesis-content { opacity: 0; }
.synthesis-stage { position: absolute; inset: 0; z-index: 10; cursor: pointer; }
.synthesis-token { position: absolute; display: flex; align-items: center; justify-content: center; gap: 9px; border-radius: 14px; color: var(--ink); background: rgba(255,255,255,.96); box-shadow: 0 12px 40px rgba(25,35,60,.06); font-weight: 500; white-space: nowrap; }
.synthesis-token i { width: 6px; height: 6px; flex: 0 0 auto; border-radius: 50%; background: var(--insight-color); }
@media print { .synthesis-replay, .synthesis-stage { display: none; } .synthesis-content { opacity: 1 !important; } }
</style>
