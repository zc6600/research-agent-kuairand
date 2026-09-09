<template>
  <section class="performance-token-evidence" aria-label="Performance versus token evidence">
    <figure>
      <img src="/assets/token-score-comparison.png" alt="Public-validation Primary score compared with measured total LLM tokens. The retained result reaches 0.605936 at 48.240 million tokens, above the official reference of 0.601600." />
    </figure>
  </section>
</template>

<style scoped>
.performance-token-evidence { height: 100%; }
figure { display: grid; height: 100%; margin: 0; place-items: center; }
img { display: block; max-height: 100%; max-width: 100%; object-fit: contain; }
</style>
