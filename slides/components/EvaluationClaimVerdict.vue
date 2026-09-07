<template>
  <section class="claim-verdict-eval" aria-label="Evaluation claim and verdict">
    <div class="claim-copy">
      <div class="claim-section-kicker mono">04 / EVALUATION</div>
      <div class="claim-label mono">CLAIM</div>
      <h1>Can an agent carry a research task to completion?</h1>
      <p class="claim-scope">On KuaiRand-Pure, under a fixed evaluator and public-validation boundary.</p>
      <div class="claim-criteria" aria-label="Completion criteria">
        <span>Research autonomously</span>
        <span>Produce a valid artifact</span>
        <span>Improve the measured objective</span>
      </div>
    </div>

    <div class="verdict-rail" aria-hidden="true">
      <span class="rail-dot rail-dot-top"></span>
      <span class="rail-line"></span>
      <span class="rail-dot rail-dot-bottom"></span>
    </div>

    <div class="verdict-area">
      <div v-click class="verdict-panel">
        <div class="verdict-label mono">VERDICT</div>
        <div class="verdict-word">Supported</div>
        <div class="verdict-scope mono">in this run</div>
      </div>

      <div v-click class="score-proof">
        <div class="score-proof-kicker mono">RETAINED PUBLIC VALIDATION / PRIMARY</div>
        <div class="score-proof-number">0.6059363</div>
        <div class="score-proof-delta"><strong>+0.0043363</strong> vs official FM reference</div>
      </div>

      <div class="evidence-strip">
        <div v-click class="evidence-item evidence-result">
          <span class="evidence-index mono">01</span>
          <div><strong>Result</strong><small>0.6016000 → 0.6059363</small></div>
        </div>
        <div v-click class="evidence-item evidence-autonomy">
          <span class="evidence-index mono">02</span>
          <div><strong>Autonomy</strong><small>4 cycles · 13 experiments · 0 interventions</small></div>
        </div>
        <div v-click class="evidence-item evidence-validity">
          <span class="evidence-index mono">03</span>
          <div><strong>Validity</strong><small>170,588 predictions · unchanged checker</small></div>
        </div>
      </div>
    </div>

    <div class="claim-verdict-foot mono">Public validation only · hidden-test scoring is organizer-controlled</div>
  </section>
</template>

<style scoped>
.claim-verdict-eval {
  position: relative;
  min-height: 560px;
  padding: 10px 20px 0;
  color: var(--ink);
  overflow: hidden;
}

.claim-verdict-eval::before {
  content: "";
  position: absolute;
  inset: 42px 43% 38px 50px;
  border-radius: 999px;
  background: radial-gradient(circle at 18% 18%, color-mix(in srgb, var(--green) 10%, transparent), transparent 62%);
  opacity: .75;
  pointer-events: none;
}

.claim-copy {
  position: absolute;
  z-index: 2;
  left: 54px;
  top: 62px;
  width: 405px;
}

.claim-section-kicker {
  color: var(--green);
  font-size: 12px;
  letter-spacing: 1.35px;
  font-weight: 800;
  text-transform: uppercase;
}

.claim-label,
.verdict-label,
.score-proof-kicker {
  color: var(--muted);
  font-size: 11px;
  letter-spacing: 1.55px;
  font-weight: 800;
  text-transform: uppercase;
}

.claim-label {
  margin-top: 70px;
  color: var(--orange);
}

.claim-copy h1 {
  margin: 18px 0 0;
  max-width: 390px;
  font-size: 47px;
  line-height: .98;
  letter-spacing: -2.1px;
  font-weight: 780;
}

.claim-scope {
  margin: 30px 0 0;
  width: 340px;
  color: var(--muted);
  font-size: 18px;
  line-height: 1.45;
}

.claim-criteria {
  display: grid;
  gap: 11px;
  margin-top: 34px;
  width: 330px;
}

.claim-criteria span {
  position: relative;
  padding-left: 22px;
  color: var(--ink);
  font-size: 15px;
  font-weight: 700;
}

.claim-criteria span::before {
  content: "";
  position: absolute;
  left: 0;
  top: .68em;
  width: 9px;
  height: 2px;
  border-radius: 10px;
  background: var(--green);
}

.verdict-rail {
  position: absolute;
  z-index: 1;
  left: 485px;
  top: 120px;
  width: 54px;
  height: 356px;
}

.rail-line {
  position: absolute;
  left: 26px;
  top: 14px;
  width: 1px;
  height: 328px;
  background: linear-gradient(to bottom, transparent, color-mix(in srgb, var(--green) 55%, transparent), transparent);
}

.rail-dot {
  position: absolute;
  left: 21px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  border: 1px solid color-mix(in srgb, var(--green) 68%, transparent);
  background: white;
  box-shadow: 0 0 0 7px color-mix(in srgb, var(--green) 10%, transparent);
}

.rail-dot-top { top: 0; }
.rail-dot-bottom { bottom: 0; }

.verdict-area {
  position: absolute;
  z-index: 2;
  top: 72px;
  right: 48px;
  width: 405px;
}

.verdict-panel {
  padding-top: 40px;
}

.verdict-word {
  margin-top: 13px;
  color: var(--green);
  font-size: 70px;
  line-height: .92;
  letter-spacing: -3.5px;
  font-weight: 760;
  text-transform: none;
}

.verdict-scope {
  margin-top: 12px;
  color: var(--muted);
  font-size: 12px;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}

.score-proof {
  margin-top: 36px;
  padding-top: 28px;
  border-top: 1px solid var(--line);
}

.score-proof-number {
  margin-top: 10px;
  color: var(--ink);
  font-size: 61px;
  line-height: 1;
  letter-spacing: -3.7px;
  font-weight: 660;
  font-variant-numeric: tabular-nums;
}

.score-proof-delta {
  margin-top: 12px;
  color: var(--muted);
  font-size: 15px;
}

.score-proof-delta strong {
  color: var(--green);
}

.evidence-strip {
  display: grid;
  gap: 10px;
  margin-top: 30px;
}

.evidence-item {
  display: grid;
  grid-template-columns: 34px 1fr;
  align-items: center;
  min-height: 48px;
  padding: 10px 0;
  border-top: 1px solid color-mix(in srgb, var(--line) 72%, transparent);
}

.evidence-index {
  color: var(--green);
  font-size: 12px;
  font-weight: 900;
}

.evidence-item strong {
  display: block;
  font-size: 15px;
  line-height: 1.15;
}

.evidence-item small {
  display: block;
  margin-top: 5px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.35;
}

.evidence-result .evidence-index { color: var(--green); }
.evidence-autonomy .evidence-index { color: var(--blue); }
.evidence-validity .evidence-index { color: var(--purple); }

.claim-verdict-foot {
  position: absolute;
  left: 54px;
  bottom: 18px;
  color: var(--muted);
  font-size: 10px;
  letter-spacing: .75px;
  text-transform: uppercase;
}

:deep(.slidev-vclick-hidden) {
  opacity: 0;
  transform: translateX(20px);
}

.verdict-panel,
.score-proof,
.evidence-item {
  transition: opacity .55s ease, transform .55s cubic-bezier(.22,1,.36,1);
}

@media (prefers-reduced-motion: reduce) {
  .verdict-panel,
  .score-proof,
  .evidence-item {
    transition: none;
  }
}
</style>
