<script setup lang="ts">
import { onSlideEnter, onSlideLeave, useNav } from '@slidev/client'
import { nextTick, onBeforeUnmount, ref } from 'vue'

// Presentation-only choreography. Content stays visible without JavaScript,
// in print, and with reduced motion. Existing click sequences own their timing.
const marker = ref<HTMLElement>()
const { isPrintMode } = useNav()
let generation = 0
const animations = new Set<Animation>()

function settle() {
  generation++
  animations.forEach(animation => animation.cancel())
  animations.clear()
}

function enter(element: Element, delay: number, duration = 760, distance = 14) {
  const animation = element.animate([
    { opacity: 0, translate: `0 ${distance}px` },
    { opacity: 1, translate: '0 0' },
  ], { duration, delay, easing: 'cubic-bezier(.22,1,.36,1)', fill: 'backwards' })
  animations.add(animation)
  animation.finished.then(() => {
    animation.cancel()
    animations.delete(animation)
  }).catch(() => {})
}

async function reveal() {
  settle()
  const current = generation
  await nextTick()
  if (current !== generation || isPrintMode.value
    || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  const slide = marker.value?.closest('.slidev-layout')
  if (!slide || slide.closest('.disable-view-transition')) return

  const title = slide.querySelector('.cover-title, h1, .closing')
  const kicker = slide.querySelector('.visual-kicker, .eyebrow')
  if (kicker) enter(kicker, 0, 500, 0)
  if (title) enter(title, 80, 900, 18)

  // Animate evidence as a whole so axes, numbers, and caveats keep their meaning.
  // Do not animate the architecture: InsightArchitecture owns that shared transition.
  const groups = [
    '.lead', '.cover-meta', '.narrative-route', '.narrative-roles > .role',
    '.failure-modes-focused > .failure-mode', '.insight-collection',
    '.memory', '.memory + .rule', '.entry-lede', '.entry-inputs > *', '.entry-footer',
    '.score > *', '.stats > *', '.resource-hero', '.resource-support',
    '.token-chart-wrap', '.insight-lede', '.insight-grid > *',
    '.fieldnote-lede', '.fieldnote-grid > *', '.terminal',
  ]
  const candidates = Array.from(slide.querySelectorAll(groups.join(',')))
  const targets = candidates.filter(element =>
    !element.closest('.slidev-vclick-target, .slidev-vclick-hidden, .insight-architecture')
    && !candidates.some(parent => parent !== element && parent.contains(element)),
  )
  targets.forEach((element, index) => enter(element, 200 + Math.min(index, 6) * 95))

  const art = slide.querySelector('.cover-art')
  if (art) {
    const animation = art.animate([
      { transform: 'scale(1.045)', opacity: .25 },
      { transform: 'scale(1)', opacity: .48 },
    ], { duration: 2000, easing: 'cubic-bezier(.22,1,.36,1)' })
    animations.add(animation)
    animation.finished.then(() => animations.delete(animation)).catch(() => {})
  }
}

onSlideEnter(reveal)
onSlideLeave(settle)
onBeforeUnmount(settle)
</script>

<template><span ref="marker" class="keynote-motion" aria-hidden="true"></span></template>

<style>
.keynote-motion { display: none; }

/* Scoped to the main deck's explicit markers, not posters or variant decks. */
.slidev-layout:has(.keynote-motion) {
  --muted: #656b75;
  background: radial-gradient(ellipse at 0% 0%, #edf5fc 0%, transparent 52%),
    radial-gradient(ellipse at 100% 100%, #f5f0fa 0%, transparent 46%), #fbfcfd;
  font-family: 'Avenir Next', 'Helvetica Neue', Arial, 'PingFang SC', sans-serif;
  -webkit-font-smoothing: antialiased;
}

.slidev-layout:has(.keynote-motion) h1 {
  font-weight: 500;
  letter-spacing: -1.2px;
  line-height: 1.15;
}

.slidev-layout:has(.keynote-motion) .visual-kicker {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1.45px;
}

.slidev-layout:has(.keynote-motion) .lead { font-weight: 400; color: #555d68; }
.slidev-layout:has(.keynote-motion) .note { color: #656b75; }
.slidev-layout:has(.keynote-motion) .big-number { font-weight: 500; letter-spacing: -3px; font-variant-numeric: tabular-nums; }

.slidev-layout.cover:has(.keynote-motion) .cover-title {
  max-width: 690px;
  margin-top: 44px;
  font-weight: 500;
  letter-spacing: -2px;
}
.slidev-layout.cover:has(.keynote-motion) .cover-title .product-name {
  font-size: 78px;
  line-height: 1.05;
  letter-spacing: -4px;
  margin-bottom: 22px;
}
.slidev-layout.cover:has(.keynote-motion) .cover-title .product-description {
  font-size: 32px;
  line-height: 1.2;
  letter-spacing: -1px;
}
.slidev-layout.cover:has(.keynote-motion) .cover-art { opacity: .48; }
.slidev-layout.cover:has(.keynote-motion) .cover-meta { font-size: 11px; font-weight: 600; letter-spacing: 1px; }
.slidev-layout.cover:has(.keynote-motion) .narrative-route { font-size: 12px; color: #656b75; }

.slidev-layout:has(.keynote-motion) .failure-modes-focused > .failure-mode {
  box-shadow: 0 18px 42px -24px rgba(22, 36, 61, .25), 0 2px 7px rgba(22, 36, 61, .035);
}
.slidev-layout:has(.keynote-motion) .closing {
  font-weight: 500;
  letter-spacing: -2px;
}

@media print {
  .slidev-layout:has(.keynote-motion) { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
</style>
