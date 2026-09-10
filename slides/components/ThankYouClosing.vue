<script setup lang="ts">
import { useNav } from '@slidev/client'
const { go } = useNav()
</script>

<template>
  <section class="thank-you-closing" aria-label="Thank you">
    <img src="/assets/research-world-cover.png" alt="" class="closing-art">
    <div class="closing-copy">
      <div class="closing-brand">SciOdyssey</div>
      <h1>Thank you<span>.</span></h1>
      <p>Autonomous by default.<br><span>Supervisable by design.</span></p>
    </div>
    <nav class="closing-navigation" aria-label="Closing navigation">
      <button type="button" class="closing-summary" @click.stop="go('summary')" @keydown.enter.stop @keydown.space.stop>↙ Back to Summary</button>
      <button type="button" class="closing-questions" @click.stop="go('qa')" @keydown.enter.stop @keydown.space.stop>Q&amp;A <span aria-hidden="true">→</span></button>
    </nav>
  </section>
</template>

<style scoped>
.thank-you-closing { position: absolute; inset: 0; display: grid; place-items: center; overflow: hidden; }
.closing-art { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: .3; }
.closing-copy { position: relative; text-align: center; transform: translateY(-8px); }
.closing-brand { margin-bottom: 20px; color: #6e7c8b; font-size: 17px; font-weight: 500; letter-spacing: 3px; }
.closing-copy h1 { margin: 0 0 24px; color: var(--ink); font-size: 100px; font-weight: 500; letter-spacing: -2px; line-height: 1; }
.closing-copy h1 span { color: var(--orange); }
.closing-copy p { margin: 0; font-size: 20px; line-height: 1.5; }
.closing-copy p span { color: #1683b4; }
.closing-navigation { position: absolute; left: 50%; bottom: 35px; transform: translateX(-50%); display: flex; align-items: center; gap: 30px; }
.closing-navigation button { font: 500 11px var(--deck-sans); cursor: pointer; }
.closing-summary { color: #8b939c; }
.closing-questions { color: #0284c7; }
.closing-questions span { margin-left: 7px; }
.closing-summary:hover { color: #0284c7; }
.closing-navigation button:focus-visible { outline: 2px solid #0284c7; outline-offset: 5px; }
@media print { .closing-navigation { display: none; } }
</style>
