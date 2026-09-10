<template>
  <div class="architecture-diagram research-system-diagram" aria-label="Research Agent system architecture">
    <div class="architecture-main">
      <div class="arch-column arch-environment">
        <div class="arch-area-title">Environment</div>
        <div class="arch-panel">
          <div class="arch-card"><span class="arch-icon blue i-carbon:document"></span><div><strong>Task contract</strong></div></div>
          <div class="arch-card"><span class="arch-icon blue i-carbon:data-base"></span><div><strong>Curated data + evaluator</strong></div></div>
          <div class="arch-card"><span class="arch-icon blue i-carbon:code"></span><div><strong>Starter baseline</strong></div></div>
          <div class="arch-card"><span class="arch-icon blue i-carbon:locked"></span><div><strong>Budget + permissions</strong></div></div>
        </div>
      </div>
      <div class="arch-arrow blue">→</div>
      <div class="arch-column arch-world">
        <div class="arch-area-title">Research World</div>
        <div class="arch-panel">
          <div class="world-lane"><div class="world-lane-label">A · VERIFIED / EVIDENCE</div><div class="world-items"><div class="world-item"><span class="arch-icon green i-carbon:checkmark-outline"></span><strong>Verified knowledge</strong></div><div class="world-item"><span class="arch-icon green i-carbon:document"></span><strong>Evidence ledger</strong></div></div></div>
          <div class="world-lane"><div class="world-lane-label">B · CURATED / REVISABLE</div><div class="world-items"><div class="world-item"><span class="arch-icon green i-carbon:document"></span><strong>Research brief</strong></div><div class="world-item"><span class="arch-icon green i-carbon:idea"></span><strong>Working priors</strong></div></div></div>
          <div class="world-lane"><div class="world-lane-label">C · IMPLEMENTATION</div><div class="world-items"><div class="world-item"><span class="arch-icon green i-carbon:data-base"></span><strong>Implementation State</strong></div></div></div>
          <div class="arch-persist">What persists across trajectories</div>
        </div>
      </div>
      <div class="arch-reset"><span class="arch-reset-icon i-carbon:reset"></span><strong>CONTEXT<br>RESET</strong></div>
      <div class="arch-column arch-scientist">
        <div class="arch-area-title">Fresh Scientist</div>
        <div class="arch-panel">
          <div class="arch-role-heading">
            <span class="arch-hero-icon purple i-carbon:chemistry"></span>
            <strong class="arch-hero-title">Scientist</strong>
            <small class="arch-hero-subtitle">owns scientific judgment</small>
          </div>
          <div class="arch-divider"></div>
          <ul class="arch-list purple-list"><li>reads the research world</li><li>forms hypotheses</li><li>runs experiments</li><li>interprets evidence</li><li>writes a report</li></ul>
          <div class="arch-callout purple-callout">inherits experience,<br>not momentum</div>
        </div>
      </div>
      <div class="arch-arrow rose">→</div>
      <div class="arch-column arch-meta">
        <div class="arch-area-title">META Review</div>
        <div class="arch-panel">
          <div class="arch-role-heading">
            <span class="arch-hero-icon rose i-carbon:security"></span>
            <strong class="arch-hero-title">META</strong>
            <small class="arch-hero-subtitle">owns what survives</small>
          </div>
          <div class="arch-divider"></div>
          <ul class="arch-list rose-list"><li>audits claim ↔ evidence validity</li><li>scopes conclusions</li><li>maintains shared research memory</li><li>crystallizes retained implementation into State</li></ul>
        </div>
      </div>
    </div>
    <div class="architecture-handoff"><span></span><strong>Selective persistence / trajectory handoff</strong><span></span></div>
    <div class="runtime-band">
      <strong class="runtime-title">Coding-agent harness + runtime</strong>
      <div class="runtime-items">
        <div><span class="runtime-icon orange i-carbon:workspace"></span><span>Workspace<br>isolation</span></div>
        <div><span class="runtime-icon orange i-carbon:play"></span><span>Runner +<br>evaluator</span></div>
        <div><span class="runtime-icon orange i-carbon:document"></span><span>Logging</span></div>
        <div><span class="runtime-icon orange i-carbon:folder"></span><span>Artifact<br>capture</span></div>
        <div><span class="runtime-icon orange i-carbon:data-base"></span><span>State<br>operations</span></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:global(.slidev-layout:has(.research-system-diagram)) {
  padding: 28px 40px 26px;
}

:global(.slidev-layout:has(.research-system-diagram) .visual-kicker) {
  margin-bottom: 12px;
}

:global(.slidev-layout:has(.research-system-diagram) h1) {
  font-size: 34px;
  font-weight: 550;
  line-height: 1.2;
  letter-spacing: -0.6px;
  margin: 0 0 24px;
}

.research-system-diagram.architecture-diagram {
  margin-top: 0;
  --system-blue: #0284c7;
  --system-green: #258549;
  --system-purple: #8b5ccc;
  --system-rose: #d95571;
}

.research-system-diagram .architecture-main {
  display: grid;
  grid-template-columns: 150px 22px 240px 58px minmax(0, 1fr) 22px minmax(0, 1fr);
  gap: 4px;
  align-items: stretch;
}

.research-system-diagram .arch-column { min-width: 0; }
.research-system-diagram .arch-environment { --module-color: var(--system-blue); }
.research-system-diagram .arch-world { --module-color: var(--system-green); }
.research-system-diagram .arch-scientist { --module-color: var(--system-purple); }
.research-system-diagram .arch-meta { --module-color: var(--system-rose); }

.research-system-diagram .arch-area-title {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--module-color);
  font-size: 12px;
  font-weight: 500;
  line-height: 1.2;
  margin: 0 0 10px;
}

.research-system-diagram .arch-area-title::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--module-color);
}

.research-system-diagram .arch-panel {
  height: 264px;
  padding: 14px 12px;
  border: 1px solid #e0e5eb;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.94);
  justify-content: flex-start;
}

.research-system-diagram .arch-environment .arch-panel {
  padding: 18px 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  justify-content: center;
}

.research-system-diagram .arch-environment .arch-card {
  min-height: 44px;
  padding: 8px 8px;
  gap: 8px;
  border: 1px solid rgba(148, 190, 223, 0.35);
  background: rgba(255, 255, 255, 0.65);
  border-radius: 8px;
}

.research-system-diagram .arch-card + .arch-card { margin-top: 8px; }
.research-system-diagram .arch-card strong { font-size: 11px; font-weight: 500; line-height: 1.3; }
.research-system-diagram .arch-icon { font-size: 19px; color: var(--module-color); }

.research-system-diagram .arch-world .arch-panel {
  padding: 16px 14px 12px;
  border-color: #b8d9c3;
  background: linear-gradient(155deg, #f3fbf5, #ffffff 58%);
  box-shadow: 0 8px 26px -16px rgba(30, 85, 49, 0.24);
}

.research-system-diagram .world-lane {
  padding: 12px 0;
  border-bottom: 1px solid #dfebe2;
}

.research-system-diagram .world-lane:first-child { padding-top: 0; }
.research-system-diagram .world-lane:nth-child(3) { border-bottom: 0; }

.research-system-diagram .world-lane-label {
  color: var(--system-green);
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 0.4px;
  line-height: 1.2;
  text-align: left;
  margin-bottom: 10px;
}

.research-system-diagram .world-items { gap: 8px; }
.research-system-diagram .world-item { font-size: 11px; line-height: 1.25; gap: 7px; }
.research-system-diagram .world-item strong { color: #4f6258; font-weight: 500; }
.research-system-diagram .world-lane:nth-child(3) .world-items { grid-template-columns: 1fr; }

.research-system-diagram .arch-persist {
  margin-top: auto;
  padding: 8px 0 0;
  border: 0;
  border-top: 1px solid #dfebe2;
  border-radius: 0;
  background: transparent;
  font-size: 10px;
  line-height: 1.25;
  color: var(--system-green);
  text-align: left;
}

.research-system-diagram .arch-scientist .arch-panel {
  border-color: #d5c7eb;
  background: linear-gradient(160deg, #faf7ff, #ffffff 45%);
}

.research-system-diagram .arch-meta .arch-panel {
  border-color: #ead0d5;
  background: linear-gradient(160deg, #fff8fa, #ffffff 45%);
}

.research-system-diagram .arch-role-heading {
  display: grid;
  grid-template-columns: 30px minmax(0, 1fr);
  align-items: center;
  gap: 2px 8px;
  min-height: 48px;
}

.research-system-diagram .arch-hero-icon {
  grid-row: span 2;
  font-size: 28px;
  margin: 0;
  color: var(--module-color);
}

.research-system-diagram .arch-hero-title {
  font-size: 21px;
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.3px;
  text-align: left;
  margin: 0;
}

.research-system-diagram .arch-hero-subtitle {
  font-size: 9px;
  font-weight: 400;
  line-height: 1.3;
  text-align: left;
  color: var(--module-color);
  margin: 0;
}

.research-system-diagram .arch-divider { margin: 10px 0 8px; border-color: #e9e4f2; }
.research-system-diagram .arch-meta .arch-divider { border-color: #f0e1e5; }
.research-system-diagram .arch-list { margin: 0; padding: 0 0 0 13px; }
.research-system-diagram .arch-list li { font-size: 11px; font-weight: 400; line-height: 1.4; margin: 0 0 8px; color: #465268; }
.research-system-diagram .arch-list li::before { color: var(--module-color); left: -12px; }

.research-system-diagram .arch-callout {
  border: 0;
  border-radius: 6px;
  background: #f4effb;
  color: #7952af;
  padding: 7px 5px;
  font-size: 10px;
  font-weight: 500;
  line-height: 1.3;
}

.research-system-diagram .arch-arrow {
  position: relative;
  align-self: center;
  top: 12px;
  font-size: 22px;
  font-weight: 400;
}
.research-system-diagram .arch-arrow.blue { color: #7ab5d6; }
.research-system-diagram .arch-arrow.rose { color: #d9889a; }

.research-system-diagram .arch-reset {
  position: relative;
  align-self: center;
  align-items: center;
  height: auto;
  padding: 0;
  margin-top: 20px;
  border: 0;
  border-radius: 0;
  background: transparent;
  gap: 6px;
}

.research-system-diagram .arch-reset::before {
  content: '';
  position: absolute;
  top: 14px;
  left: 0;
  right: 0;
  border-top: 1px solid #c7b6e1;
}

.research-system-diagram .arch-reset::after {
  content: '';
  position: absolute;
  width: 5px;
  height: 5px;
  right: 1px;
  top: 12px;
  border-top: 1px solid #b19acb;
  border-right: 1px solid #b19acb;
  transform: rotate(45deg);
}

.research-system-diagram .arch-reset-icon {
  position: relative;
  width: 28px;
  height: 28px;
  font-size: 19px;
  margin: 0;
  color: #987ab9;
}

.research-system-diagram .arch-reset strong {
  font-size: 8px;
  font-weight: 500;
  line-height: 1.5;
  letter-spacing: 0.25px;
  color: #8b799f;
}

/* Return the retained research world to the next fresh trajectory. */
.research-system-diagram .architecture-handoff {
  position: relative;
  height: 43px;
  margin: 0 96px 0 300px;
  padding-top: 17px;
  box-sizing: border-box;
  color: var(--system-rose);
  justify-content: center;
  font-size: 10px;
  line-height: 1.2;
  gap: 0;
}

.research-system-diagram .architecture-handoff::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 26px;
  border: 1px solid #df9baa;
  border-top: 0;
  border-radius: 0 0 9px 9px;
}

.research-system-diagram .architecture-handoff::after {
  content: '';
  position: absolute;
  top: 2px;
  left: -2px;
  width: 5px;
  height: 5px;
  border-left: 1px solid #df9baa;
  border-top: 1px solid #df9baa;
  transform: rotate(45deg);
}

.research-system-diagram .architecture-handoff strong {
  position: relative;
  z-index: 1;
  padding: 0 9px;
  background: #fffdfa;
  font-weight: 500;
}
.research-system-diagram .architecture-handoff span { display: none; }

.research-system-diagram .runtime-band {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 16px;
  align-items: center;
  min-height: 54px;
  margin: 0;
  padding: 10px 14px;
  border: 1px solid #e5e5e3;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.7);
}

.research-system-diagram .runtime-title {
  font-size: 11px;
  font-weight: 500;
  line-height: 1.4;
  text-align: left;
  color: #ae743e;
}

.research-system-diagram .runtime-items { margin: 0; gap: 10px; }
.research-system-diagram .runtime-items > div {
  justify-content: flex-start;
  gap: 6px;
  min-height: 30px;
  padding: 0 0 0 10px;
  border: 0;
  border-left: 1px solid #e9e6e1;
  border-radius: 0;
  background: transparent;
  font-size: 9.5px;
  font-weight: 400;
  line-height: 1.25;
  color: #67707c;
}
.research-system-diagram .runtime-icon { font-size: 18px; color: #c39469; }
</style>
