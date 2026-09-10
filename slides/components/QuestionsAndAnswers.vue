<script setup lang="ts">
import { useNav } from '@slidev/client'
const { go } = useNav()
</script>

<template>
  <section class="questions-page" aria-label="Questions and answers">
    <div class="questions-copy">
      <div class="questions-brand">SciOdyssey</div>
      <h1>Q<span>&amp;</span>A</h1>
      <p>Let's discuss.</p>
    </div>
    <button type="button" class="questions-summary" @click.stop="go('summary')" @keydown.enter.stop @keydown.space.stop>
      <span aria-hidden="true">↙</span> Explore the evidence
    </button>
  </section>
</template>

<style scoped>
.questions-page { position: absolute; inset: 0; display: grid; place-items: center; }
.questions-copy { text-align: center; transform: translateY(-8px); }
.questions-brand { margin-bottom: 20px; color: #6e7c8b; font-size: 17px; font-weight: 500; letter-spacing: 3px; }
.questions-copy h1 { margin: 0 0 20px; color: var(--ink); font-size: 112px; font-weight: 400; line-height: 1; letter-spacing: 1px; }
.questions-copy h1 span { padding: 0 9px; color: #56b1d5; }
.questions-copy p { margin: 0; color: #78818b; font-size: 20px; font-weight: 400; }
.questions-summary { position: absolute; left: 50%; bottom: 35px; transform: translateX(-50%); color: #768593; font: 500 11px var(--deck-sans); cursor: pointer; }
.questions-summary span { margin-right: 5px; color: #0284c7; }
.questions-summary:hover { color: #0284c7; }
.questions-summary:focus-visible { outline: 2px solid #0284c7; outline-offset: 5px; }
@media print { .questions-summary { display: none; } }
</style>
