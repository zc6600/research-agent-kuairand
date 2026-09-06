<template>
  <footer class="deck-footer">
    <span><i></i> RESEARCH AGENT <span class="footer-dim">/ FIELD NOTES 2026</span></span>
    <span>{{ String($slidev.nav.currentPage).padStart(2, '0') }} <span class="footer-dim">/ {{ String($slidev.nav.total).padStart(2, '0') }}</span></span>
  </footer>
</template>
