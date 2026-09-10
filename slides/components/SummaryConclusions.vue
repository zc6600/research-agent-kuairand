<script setup lang="ts">
import { onSlideEnter, useNav } from '@slidev/client'
import { nextTick, ref } from 'vue'
import { conclusionCards } from '../composables/conclusions.mjs'
import { lastConclusion, useConclusionNavigation } from '../composables/useConclusionNavigation'

const { openConclusion } = useConclusionNavigation()
const { go } = useNav()
const root = ref<HTMLElement>()

onSlideEnter(async () => {
  await nextTick()
  if (lastConclusion.value)
    root.value?.querySelector<HTMLButtonElement>(`[data-conclusion="${lastConclusion.value}"]`)?.focus({ preventScroll: true })
})
</script>

<template>
  <section ref="root" class="conclusion-scatter" aria-label="Summary of research evidence and lessons" @click.stop>
    <div class="conclusion-center">
      <span class="conclusion-brand">SciOdyssey</span>
      <h1>Summary<span>.</span></h1>
      <p>The system. The evidence.<br><span>What we learned.</span></p>
      <span class="conclusion-invitation">Click a card to explore.</span>
      <button type="button" class="summary-finish" @click.stop="go('thank-you')" @keydown.enter.stop @keydown.space.stop>Thank You <span aria-hidden="true">→</span></button>
    </div>

    <button
      v-for="(card, index) in conclusionCards"
      :key="card.id"
      type="button"
      class="conclusion-card"
      :class="`summary-${card.id}`"
      :data-conclusion="card.id"
      :aria-label="`${card.title} Open ${card.label.toLowerCase()}`"
      :style="{
        '--accent': card.accent,
        '--x': `${card.x}px`, '--y': `${card.y}px`,
        '--width': `${card.width}px`, '--height': `${card.height}px`,
        '--tilt': `${card.tilt}deg`, '--order': index,
      }"
      @click.stop="openConclusion(card)"
      @keydown.enter.stop
      @keydown.space.stop
    >
      <span class="conclusion-card-label">{{ card.label }}<span class="conclusion-card-arrow" aria-hidden="true">↗</span></span>
      <span class="summary-card-body">
        <img v-if="card.image" class="summary-image" :src="card.image.startsWith('/') ? card.image : `/assets/summary/${card.image}`" alt="">
        <span v-else-if="card.id === 'diversity'" class="summary-models" aria-hidden="true"><img src="/assets/codex.svg" alt=""><img src="/assets/antigravity-color.svg" alt=""></span>
        <span v-else-if="card.id === 'resources'" class="summary-laptop i-carbon:laptop" aria-hidden="true"></span>
        <span class="summary-card-copy">
          <strong>{{ card.title }}</strong>
          <span v-if="card.emphasis" class="summary-emphasis">{{ card.emphasis }}</span>
          <span v-if="card.note" class="conclusion-card-note">{{ card.note }}</span>
        </span>
      </span>
    </button>
  </section>
</template>

<style scoped>
.conclusion-scatter {
  position: absolute;
  inset: 0;
  isolation: isolate;
  color: var(--ink);
}

.conclusion-center {
  position: absolute;
  inset: 218px 278px auto;
  text-align: center;
}

.conclusion-brand {
  color: #78818b;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 2px;
}

.conclusion-center h1 {
  margin: 7px 0 12px;
  font-family: var(--deck-sans);
  font-size: 66px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: -2px;
}

.conclusion-center h1 span { color: var(--orange); }
.conclusion-center p { margin: 0; font-size: 16px; line-height: 1.5; }
.conclusion-center p span { color: #1683b4; }
.conclusion-invitation { display: block; margin-top: 15px; color: #85878d; font-size: 11px; }
.summary-finish { margin-top: 10px; color: #0284c7; font: 500 11px var(--deck-sans); cursor: pointer; }
.summary-finish span { margin-left: 7px; }
.summary-finish:focus-visible { outline: 2px solid #0284c7; outline-offset: 4px; }

.conclusion-card {
  position: absolute;
  left: var(--x);
  top: var(--y);
  width: var(--width);
  height: var(--height);
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  gap: 7px;
  padding: 11px 13px;
  border: 1px solid color-mix(in srgb, var(--accent) 18%, #e7e8ec);
  border-radius: 11px;
  background: linear-gradient(135deg, #fff 24%, color-mix(in srgb, var(--accent) 6%, white));
  box-shadow: 0 7px 18px #182a4010, 0 1px 3px #182a4005;
  color: var(--ink);
  font-family: var(--deck-sans);
  text-align: left;
  cursor: pointer;
  transform: rotate(var(--tilt));
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
  animation: card-arrive .5s calc(var(--order) * 30ms) backwards;
}

.conclusion-card-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  color: var(--accent);
  font-size: 8px;
  font-weight: 600;
  letter-spacing: 1px;
  line-height: 1;
}

.conclusion-card-arrow { font-size: 14px; line-height: .6; }
.summary-card-body { display: flex; flex: 1; min-height: 0; flex-direction: column; gap: 7px; }
.summary-image { display: block; width: 100%; min-height: 0; height: 67px; object-fit: contain; background: #fff; border-radius: 5px; }
.summary-card-copy { display: flex; flex-direction: column; justify-content: center; gap: 2px; }
.conclusion-card strong, .summary-emphasis { font-size: 17px; font-weight: 600; letter-spacing: -.2px; line-height: 1.12; }
.summary-emphasis { color: var(--accent); }
.conclusion-card-note { color: #727985; font-size: 9px; line-height: 1.25; }
.summary-open-world .summary-image { object-fit: cover; object-position: 50% 30%; }
.summary-principles .summary-image { height: 54px; }
.summary-result .summary-card-body, .summary-resources .summary-card-body, .summary-diversity .summary-card-body, .summary-parallel .summary-card-body { flex-direction: row; align-items: center; gap: 9px; }
.summary-result .summary-image { width: 78px; height: 64px; }
.summary-result strong { color: var(--accent); font-size: 29px; letter-spacing: -1px; }
.summary-result .conclusion-card-note { max-width: 94px; }
.summary-trajectory .summary-card-body { gap: 3px; }
.summary-trajectory .summary-image { height: 35px; }
.summary-trajectory .summary-card-copy { flex-direction: row; justify-content: space-between; align-items: baseline; }
.summary-trajectory strong { color: var(--accent); font-size: 22px; }
.summary-robustness .summary-image { height: 30px; }
.summary-robustness .summary-card-body { gap: 5px; }
.summary-robustness strong, .summary-robustness .summary-emphasis { font-size: 16px; }
.summary-comparison .summary-image { height: 34px; }
.summary-comparison .summary-card-body { gap: 4px; }
.summary-comparison strong { font-size: 15px; }
.summary-comparison .conclusion-card-note { font-size: 8px; }
.summary-resources { gap: 4px; padding-top: 9px; padding-bottom: 9px; }
.summary-laptop { display: block; flex-shrink: 0; width: 32px; height: 32px; color: var(--accent); }
.summary-resources .summary-card-copy { display: grid; grid-template-columns: auto 1fr; gap: 1px 9px; align-items: center; }
.summary-resources strong { grid-row: span 2; font-size: 30px; color: var(--accent); letter-spacing: -1px; }
.summary-resources .summary-emphasis { font-size: 12px; }
.summary-resources .conclusion-card-note { font-size: 8px; }
.summary-models { display: flex; gap: 7px; align-items: center; }
.summary-models img { width: 30px; height: 30px; object-fit: contain; }
.summary-diversity strong { font-size: 17px; }
.summary-parallel { gap: 4px; padding-top: 9px; padding-bottom: 9px; }
.summary-parallel .summary-image { width: 87px; height: 37px; }
.summary-parallel strong, .summary-parallel .summary-emphasis { font-size: 15px; }
.conclusion-card:hover, .conclusion-card:focus-visible {
  z-index: 2;
  transform: translateY(-5px) rotate(0deg) scale(1.035);
  border-color: var(--accent);
  box-shadow: 0 16px 32px #182a4020;
}
.conclusion-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
@keyframes card-arrive {
  from { opacity: 0; translate: 0 10px; }
  to { opacity: 1; translate: 0 0; }
}
@media (prefers-reduced-motion: reduce) {
  .conclusion-card { animation: none; transition: none; }
}
@media print {
  .conclusion-card { animation: none; }
  .conclusion-invitation, .conclusion-card-arrow, .summary-finish { display: none; }
}
</style>
