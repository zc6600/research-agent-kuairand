<template>
  <div class="philosophy-container">
    <p class="philosophy-lead">Practical disciplines that make autonomous ML research grounded, robust, and cost-effective.</p>

    <div class="philosophy-list">
      <article class="philosophy-row card-blue">
        <div class="principle-mark">
          <span class="card-number mono">01</span>
          <svg viewBox="0 0 48 42" fill="none" aria-hidden="true">
            <path class="diagram-muted" d="M7 5v7m8-7v7m9-7v7m9-7v7m8-7v7" />
            <path d="M5 17h38L29 30v7H19v-7L5 17Z" />
            <path d="m20 24 3 3 6-6" />
          </svg>
        </div>
        <div class="principle-heading">
          <div class="card-header">
            <span class="card-tag mono">DATA BOUNDARY</span>
            <span class="card-file mono">EXPLORE.md</span>
          </div>
          <h3>Ground the data, skip the ritual</h3>
          <div class="card-core-rule">Explore only what affects the model</div>
        </div>
        <div class="card-item">
          <strong>Skip useless data dumps:</strong> Don't print giant tables that clutter context without helping decisions.
        </div>
        <div class="card-item">
          <strong>Check leaks before training:</strong> Verify time splits and feature cutoffs to avoid fake high scores.
        </div>
      </article>

      <article class="philosophy-row card-orange">
        <div class="principle-mark">
          <span class="card-number mono">02</span>
          <svg viewBox="0 0 48 42" fill="none" aria-hidden="true">
            <path class="diagram-muted" d="M4 37h40M10 33v4m28-4v4" />
            <rect x="7" y="5" width="34" height="27" rx="4" />
            <path d="M7 12h34m-24 6-4 4 4 4m14-8 4 4-4 4m-5-9-4 10" />
          </svg>
        </div>
        <div class="principle-heading">
          <div class="card-header">
            <span class="card-tag mono">EXECUTION FOUNDATION</span>
            <span class="card-file mono">ENGINEERING.md</span>
          </div>
          <h3>Engineering before experiment</h3>
          <div class="card-core-rule">Scripts, tooling & limits make the agent robust</div>
        </div>
        <div class="card-item">
          <strong>Build solid scripts first:</strong> Write modular entrypoints, fast diagnostics, and self-healing tools before modeling.
        </div>
        <div class="card-item">
          <strong>Estimate compute & runtime:</strong> Record CPU/GPU, memory, and task duration in <code>ENGINEERING.md</code> to prevent OOM and timeouts.
        </div>
      </article>

      <article class="philosophy-row card-rose">
        <div class="principle-mark">
          <span class="card-number mono">03</span>
          <svg viewBox="0 0 48 42" fill="none" aria-hidden="true">
            <path class="diagram-muted" d="M4 9h10M4 21h10M4 33h10" />
            <path d="M18 5v32m0-16h23m-6-6 6 6-6 6" />
            <path class="diagram-muted" d="m25 7 4 4m0-4-4 4m0 20 4 4m0-4-4 4" />
            <circle cx="9" cy="21" r="3" class="diagram-fill" />
          </svg>
        </div>
        <div class="principle-heading">
          <div class="card-header">
            <span class="card-tag mono">RESOURCE CONTROL</span>
            <span class="card-file mono">OPTIMIZE.md</span>
          </div>
          <h3>Test ideas cheap and early</h3>
          <div class="card-core-rule">Screen fast on small runs, protect full budget</div>
        </div>
        <div class="card-item">
          <strong>Use gates to fail fast:</strong> Quickly drop weak ideas on small tests; never waste full training to rescue them.
        </div>
        <div class="card-item">
          <strong>Keep small tests realistic:</strong> Small runs must keep true data grouping (like user groups), or scores mislead.
        </div>
      </article>

      <article class="philosophy-row card-purple">
        <div class="principle-mark">
          <span class="card-number mono">04</span>
          <svg viewBox="0 0 48 42" fill="none" aria-hidden="true">
            <path class="diagram-muted" d="M9 16a16 16 0 0 1 28-5l3 4M39 26A16 16 0 0 1 11 31l-3-4" />
            <path d="m40 8v7h-7M8 34v-7h7" />
            <path d="M19 12h10l3 3v16H16V15l3-3Z" />
            <path d="M21 18h6m-6 5h6m-6 4h4" />
          </svg>
        </div>
        <div class="principle-heading">
          <div class="card-header">
            <span class="card-tag mono">SELF-EVOLUTION</span>
            <span class="card-file mono">INTUITION.md</span>
          </div>
          <h3>Learn like a human researcher</h3>
          <div class="card-core-rule">Self-evolution through high-level memory</div>
        </div>
        <div class="card-item">
          <strong>Clear the execution noise:</strong> Wipe verbose terminal logs on resets so the agent stays fresh without context bloat.
        </div>
        <div class="card-item">
          <strong>Pass down high-level intuition:</strong> Save key rules and lessons in <code>INTUITION.md</code> to inherit experience, not momentum.
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
:global(.slidev-layout:has(.philosophy-container)) {
  padding: 28px 56px 34px;
}

:global(.slidev-layout:has(.philosophy-container) .visual-kicker) {
  margin-bottom: 12px;
}

:global(.slidev-layout:has(.philosophy-container) h1) {
  font-size: 34px;
  font-weight: 550;
  line-height: 1.2;
  letter-spacing: -0.6px;
  margin: 0 0 10px;
}

.philosophy-container {
  display: flex;
  flex-direction: column;
}

.philosophy-container .philosophy-lead {
  font-size: 12px;
  line-height: 1.4;
  color: #727d8d;
  margin: 0 0 17px;
}

.philosophy-list {
  display: grid;
  gap: 8px;
}

.philosophy-row {
  display: grid;
  grid-template-columns: 46px 238px minmax(0, 1fr) minmax(0, 1fr);
  align-items: center;
  column-gap: 18px;
  min-height: 84px;
  padding: 10px 14px 10px 10px;
  box-sizing: border-box;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 10px;
  background: linear-gradient(90deg, var(--principle-wash), rgba(255, 255, 255, 0.9) 35%);
}

.card-blue { --principle-accent: #0284c7; --principle-wash: #edf8ff; }
.card-orange { --principle-accent: #dc652c; --principle-wash: #fff5ec; }
.card-rose { --principle-accent: #df4e70; --principle-wash: #fff0f3; }
.card-purple { --principle-accent: #9258cf; --principle-wash: #f6f0ff; }

.principle-mark {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--principle-accent);
}

.card-number {
  font-size: 12px;
  line-height: 1;
  font-weight: 500;
  letter-spacing: 1px;
}

.principle-mark svg {
  width: 38px;
  height: 34px;
  stroke: currentColor;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.diagram-muted { opacity: 0.38; }
.diagram-fill { fill: var(--principle-wash); }

.principle-heading {
  min-width: 0;
}

.card-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 5px;
  white-space: nowrap;
}

.card-tag {
  font-size: 8px;
  font-weight: 500;
  letter-spacing: 0.5px;
  line-height: 1.15;
  color: var(--principle-accent);
}

.card-file {
  font-size: 8px;
  font-weight: 400;
  line-height: 1.15;
  color: #8992a0;
}

.philosophy-row h3 {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.23;
  margin: 0 0 5px;
  color: var(--ink, #111217);
  letter-spacing: -0.3px;
}

.card-core-rule {
  font-size: 10.4px;
  font-weight: 500;
  line-height: 1.35;
  color: var(--principle-accent);
}

.card-item {
  min-width: 0;
  align-self: center;
  font-size: 11px;
  font-weight: 400;
  line-height: 1.42;
  color: #536175;
}

.card-item strong {
  display: block;
  color: #253346;
  font-weight: 600;
  font-size: 11px;
  line-height: 1.3;
  margin-bottom: 5px;
}

.card-item code {
  font-size: 9.6px;
  padding: 0 2px;
  color: #536175;
  background: rgba(148, 163, 184, 0.09);
  border-radius: 3px;
}
</style>
