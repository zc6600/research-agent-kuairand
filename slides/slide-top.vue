<script setup lang="ts">
import { useSlideContext } from '@slidev/client'
import { useConclusionNavigation } from './composables/useConclusionNavigation'

const { canReturn, returnToConclusions } = useConclusionNavigation()
const { $renderContext, $slidev, $page, $nav } = useSlideContext()
</script>

<template>
  <button
    v-if="canReturn && $page === $nav.currentSlideNo && ['slide', 'presenter'].includes($renderContext)"
    type="button"
    class="conclusion-return"
    @click.stop="returnToConclusions"
    @keydown.enter.stop
    @keydown.space.stop
  >
    <span aria-hidden="true">↙</span> Back to Summary
  </button>
  <footer class="deck-footer">
    <span><i></i> RESEARCH AGENT <span class="footer-dim">/ FIELD NOTES 2026</span></span>
    <span>{{ String($slidev.nav.currentPage).padStart(2, '0') }} <span class="footer-dim">/ {{ String($slidev.nav.total).padStart(2, '0') }}</span></span>
  </footer>
</template>

<style scoped>
.conclusion-return {
  position: absolute;
  z-index: 100;
  right: 18px;
  bottom: 12px;
  padding: 7px 12px;
  border: 1px solid #dce2e8;
  border-radius: 8px;
  background: #fffffff2;
  box-shadow: 0 3px 12px #172b4010;
  color: #46576a;
  font: 700 11px var(--deck-sans);
  cursor: pointer;
}
.conclusion-return span { margin-right: 5px; color: #0284c7; }
.conclusion-return:hover { border-color: #0284c7; color: #0284c7; }
.conclusion-return:focus-visible { outline: 2px solid #0284c7; outline-offset: 3px; }
@media print { .conclusion-return { display: none; } }
</style>
