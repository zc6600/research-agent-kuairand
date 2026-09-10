<template>
  <div class="philosophy-container">
    <p class="philosophy-lead">Practical disciplines that make autonomous ML research grounded, robust, and cost-effective.</p>

    <div class="philosophy-grid">
      <!-- Card 1: Targeted EDA -->
      <article class="philosophy-card card-blue">
        <div class="card-header">
          <span class="card-number mono">01</span>
          <span class="card-tag mono">DATA BOUNDARY</span>
          <span class="card-file mono">EXPLORE.md</span>
        </div>
        <h3>Ground the data, skip the ritual</h3>
        <div class="card-core-rule">Explore only what affects the model</div>
        <div class="card-body">
          <div class="card-item">
            <strong>Skip useless data dumps:</strong> Don't print giant tables that clutter context without helping decisions.
          </div>
          <div class="card-item">
            <strong>Check leaks before training:</strong> Verify time splits and feature cutoffs to avoid fake high scores.
          </div>
        </div>
      </article>

      <!-- Card 2: Engineering Before Experiment -->
      <article class="philosophy-card card-orange">
        <div class="card-header">
          <span class="card-number mono">02</span>
          <span class="card-tag mono">EXECUTION FOUNDATION</span>
          <span class="card-file mono">ENGINEERING.md</span>
        </div>
        <h3>Engineering before experiment</h3>
        <div class="card-core-rule">Scripts, tooling & limits make the agent robust</div>
        <div class="card-body">
          <div class="card-item">
            <strong>Build solid scripts first:</strong> Write modular entrypoints, fast diagnostics, and self-healing tools before modeling.
          </div>
          <div class="card-item">
            <strong>Estimate compute & runtime:</strong> Record CPU/GPU, memory, and task duration in <code>ENGINEERING.md</code> to prevent OOM and timeouts.
          </div>
        </div>
      </article>

      <!-- Card 3: Faithful Hypothesis Gate -->
      <article class="philosophy-card card-rose">
        <div class="card-header">
          <span class="card-number mono">03</span>
          <span class="card-tag mono">RESOURCE CONTROL</span>
          <span class="card-file mono">OPTIMIZE.md</span>
        </div>
        <h3>Test ideas cheap and early</h3>
        <div class="card-core-rule">Screen fast on small runs, protect full budget</div>
        <div class="card-body">
          <div class="card-item">
            <strong>Use gates to fail fast:</strong> Quickly drop weak ideas on small tests; never waste full training to rescue them.
          </div>
          <div class="card-item">
            <strong>Keep small tests realistic:</strong> Small runs must keep true data grouping (like user groups), or scores mislead.
          </div>
        </div>
      </article>

      <!-- Card 4: Cognitive Intuition & Self-Evolution -->
      <article class="philosophy-card card-purple">
        <div class="card-header">
          <span class="card-number mono">04</span>
          <span class="card-tag mono">SELF-EVOLUTION</span>
          <span class="card-file mono">INTUITION.md</span>
        </div>
        <h3>Learn like a human researcher</h3>
        <div class="card-core-rule">Self-evolution through high-level memory</div>
        <div class="card-body">
          <div class="card-item">
            <strong>Clear the execution noise:</strong> Wipe verbose terminal logs on resets so the agent stays fresh without context bloat.
          </div>
          <div class="card-item">
            <strong>Pass down high-level intuition:</strong> Save key rules and lessons in <code>INTUITION.md</code> to inherit experience, not momentum.
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.philosophy-container {
  display: flex;
  flex-direction: column;
}

.philosophy-lead {
  font-size: 13px;
  line-height: 1.35;
  color: var(--muted, #7d7d82);
  margin: -6px 0 10px;
}

.philosophy-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 16px;
}

.philosophy-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--line, #e6e6e8);
  border-radius: 12px;
  box-shadow: 0 4px 14px -2px rgba(15, 23, 42, 0.05);
  display: flex;
  flex-direction: column;
  padding: 10px 14px 10px;
  box-sizing: border-box;
}

.card-blue { border-top: 3px solid var(--blue, #38bdf8); }
.card-orange { border-top: 3px solid var(--orange, #ff873f); }
.card-rose { border-top: 3px solid var(--rose, #ff5c78); }
.card-purple { border-top: 3px solid var(--purple, #a66cff); }

.card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 9.5px;
  line-height: 1;
  margin-bottom: 4px;
}

.card-number {
  font-weight: 800;
  font-size: 10.5px;
}

.card-blue .card-number { color: var(--blue, #38bdf8); }
.card-orange .card-number { color: var(--orange, #ff873f); }
.card-rose .card-number { color: var(--rose, #ff5c78); }
.card-purple .card-number { color: var(--purple, #a66cff); }

.card-tag {
  font-size: 9px;
  font-weight: 750;
  letter-spacing: 0.6px;
  color: var(--muted, #7d7d82);
}

.card-file {
  margin-left: auto;
  font-size: 9px;
  color: #64748b;
  background: #f1f5f9;
  padding: 1.5px 5px;
  border-radius: 4px;
  font-weight: 500;
}

.philosophy-card h3 {
  font-size: 15px;
  font-weight: 750;
  line-height: 1.2;
  margin: 0 0 5px;
  color: var(--ink, #111217);
  letter-spacing: -0.25px;
}

.card-core-rule {
  align-self: flex-start;
  font-size: 10px;
  font-weight: 650;
  padding: 2px 7px;
  border-radius: 4px;
  margin-bottom: 7px;
  letter-spacing: 0.1px;
}

.card-blue .card-core-rule { background: #e0f2fe; color: #0284c7; }
.card-orange .card-core-rule { background: #ffedd5; color: #ea580c; }
.card-rose .card-core-rule { background: #ffe4e6; color: #e11d48; }
.card-purple .card-core-rule { background: #f3e8ff; color: #9333ea; }

.card-body {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.card-item {
  font-size: 11px;
  line-height: 1.35;
  color: #475569;
}

.card-item strong {
  color: var(--ink, #111217);
  font-weight: 700;
  font-size: 11px;
}
</style>
