<template>
  <section class="research-insight-page model-diversity-page">
    <div class="visual-kicker purple">04 / INSIGHTS · MODEL DIVERSITY</div>
    <h1>Model diversity breaks search plateaus</h1>
    <p class="insight-deck">Alternating GPT and Gemini combines depth and breadth within one shared research world.</p>

    <!-- TOP SECTION: TWO COMPLEMENTARY SEARCH STYLES -->
    <div class="roles-grid">
      <!-- GPT CARD: DEPTH -->
      <article class="role-card card-blue">
        <div class="role-header">
          <div class="role-title-row">
            <span class="role-badge badge-blue mono">01 · DEPTH</span>
            <span class="model-tag mono">GPT 5.6</span>
          </div>
          <h3>Deepen & optimize proven paths</h3>
          <p class="role-subtitle">Disciplined step-by-step exploitation and hyperparameter refinement.</p>
        </div>
        <div class="role-visual">
          <svg viewBox="0 0 280 60" class="search-tree" role="img" aria-label="Depth search diagram">
            <!-- Quiet / Pruned branches -->
            <path class="edge-quiet" d="M 30 30 L 95 14 M 95 30 L 160 16 M 160 44 L 225 30" />
            <circle class="node-quiet" cx="95" cy="14" r="4" />
            <circle class="node-quiet" cx="160" cy="16" r="4" />
            <circle class="node-quiet" cx="225" cy="30" r="4" />
            <!-- Active Depth Path -->
            <path class="edge-blue" d="M 30 30 L 95 44 L 160 44 L 225 44" />
            <circle class="node-blue" cx="30" cy="30" r="5" />
            <circle class="node-blue" cx="95" cy="44" r="5" />
            <circle class="node-blue" cx="160" cy="44" r="5" />
            <circle class="node-blue-end" cx="225" cy="44" r="7" />
          </svg>
        </div>
      </article>

      <!-- GEMINI CARD: BREADTH -->
      <article class="role-card card-purple">
        <div class="role-header">
          <div class="role-title-row">
            <span class="role-badge badge-purple mono">02 · BREADTH</span>
            <span class="model-tag mono">Gemini 3.7</span>
          </div>
          <h3>Open new architectural mechanisms</h3>
          <p class="role-subtitle">Broad hypothesis exploration, mechanism pivots, and candidate screening.</p>
        </div>
        <div class="role-visual">
          <svg viewBox="0 0 280 60" class="search-tree" role="img" aria-label="Breadth search diagram">
            <!-- Parallel Exploratory Branches -->
            <path class="edge-purple" d="M 30 30 L 100 12 L 225 12" />
            <path class="edge-purple" d="M 30 30 L 100 24 L 225 24" />
            <path class="edge-purple" d="M 30 30 L 100 36 L 225 36" />
            <path class="edge-purple" d="M 30 30 L 100 48 L 225 48" />
            <circle class="node-purple" cx="30" cy="30" r="5" />
            <circle class="node-purple" cx="100" cy="12" r="4.5" />
            <circle class="node-purple" cx="100" cy="24" r="4.5" />
            <circle class="node-purple" cx="100" cy="36" r="4.5" />
            <circle class="node-purple" cx="100" cy="48" r="4.5" />
            <circle class="node-purple-end" cx="225" cy="12" r="5.5" />
            <circle class="node-purple-end" cx="225" cy="24" r="5.5" />
            <circle class="node-purple-end" cx="225" cy="36" r="5.5" />
            <circle class="node-purple-end" cx="225" cy="48" r="5.5" />
          </svg>
        </div>
      </article>
    </div>

    <!-- BOTTOM SECTION: THE RELAY SEQUENCE & MEASURED RESULT -->
    <div class="outcome-container">
      <!-- LEFT: 4-CYCLE RELAY -->
      <div class="relay-panel">
        <div class="panel-caption mono">RETAINED 4-CYCLE ROTATION SEQUENCE</div>
        <div class="relay-track">
          <!-- Step 1 -->
          <div class="relay-step step-blue">
            <div class="step-badge mono">CYCLE 01</div>
            <strong class="step-model">GPT 5.6</strong>
            <span class="step-desc">FM Baseline</span>
          </div>
          <span class="relay-arrow">→</span>
          <!-- Step 2 -->
          <div class="relay-step step-purple">
            <div class="step-badge mono">CYCLE 02</div>
            <strong class="step-model">Gemini 3.7</strong>
            <span class="step-desc">Target DIN</span>
          </div>
          <span class="relay-arrow">→</span>
          <!-- Step 3 -->
          <div class="relay-step step-blue">
            <div class="step-badge mono">CYCLE 03</div>
            <strong class="step-model">GPT 5.6</strong>
            <span class="step-desc">Feature Eng</span>
          </div>
          <span class="relay-arrow">→</span>
          <!-- Step 4 -->
          <div class="relay-step step-purple">
            <div class="step-badge mono">CYCLE 04</div>
            <strong class="step-model">Gemini 3.7</strong>
            <span class="step-desc">Ensemble</span>
          </div>
        </div>
        <!-- Shared Memory Bar -->
        <div class="memory-ribbon">
          <span class="memory-icon">↻</span>
          <span class="memory-text mono">Shared Research Memory · Maintained by META across all resets</span>
        </div>
      </div>

      <!-- RIGHT: HEAD-TO-HEAD EVIDENCE -->
      <div class="evidence-panel">
        <div class="panel-caption mono">PUBLIC-VALIDATION PRIMARY</div>
        <div class="score-cards">
          <div class="score-card baseline-score">
            <span class="score-label">Gemini-only</span>
            <strong class="score-value mono">0.6052</strong>
            <span class="score-sub">Cycle 2 plateau</span>
          </div>
          <div class="score-card winner-score">
            <div class="score-tag-row">
              <span class="score-label">GPT + Gemini</span>
              <span class="delta-badge mono">+0.0007</span>
            </div>
            <strong class="score-value mono">0.6059</strong>
            <span class="score-sub green">Retained peak submission</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.research-insight-page.model-diversity-page {
  height: 475px;
  display: flex;
  flex-direction: column;
  color: var(--ink, #111217);
}

.model-diversity-page h1 {
  font-size: 30px;
  font-weight: 750;
  letter-spacing: -0.8px;
  line-height: 1.15;
  margin: 10px 0 4px;
}

.model-diversity-page .insight-deck {
  font-size: 14px;
  line-height: 1.35;
  color: #64748b;
  margin: 0 0 12px;
}

/* TOP CARDS: 2 SEARCH STYLES */
.roles-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 12px;
}

.role-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--line, #e2e8f0);
  border-radius: 12px;
  padding: 11px 16px 10px;
  box-shadow: 0 4px 14px -2px rgba(15, 23, 42, 0.04);
  display: flex;
  flex-direction: column;
}

.card-blue { border-top: 3.5px solid var(--blue, #38bdf8); }
.card-purple { border-top: 3.5px solid var(--purple, #a66cff); }

.role-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.role-badge {
  font-size: 9px;
  font-weight: 750;
  letter-spacing: 0.8px;
}

.badge-blue { color: #0284c7; }
.badge-purple { color: #7e22ce; }

.model-tag {
  font-size: 9.5px;
  color: #64748b;
  background: #f1f5f9;
  padding: 1.5px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.role-header h3 {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 3px;
  color: var(--ink, #111217);
  letter-spacing: -0.2px;
}

.role-subtitle {
  font-size: 11px;
  color: #64748b;
  margin: 0 0 6px;
  line-height: 1.3;
}

.role-visual {
  height: 48px;
  display: flex;
  align-items: center;
}

.search-tree {
  width: 100%;
  height: 48px;
}

.edge-quiet { stroke: #cbd5e1; stroke-width: 1.5; stroke-dasharray: 3 3; fill: none; }
.edge-blue { stroke: #0284c7; stroke-width: 2.2; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.edge-purple { stroke: #a855f7; stroke-width: 2.2; fill: none; stroke-linecap: round; stroke-linejoin: round; }

.node-quiet { fill: #f8fafc; stroke: #94a3b8; stroke-width: 1.5; }
.node-blue { fill: #ffffff; stroke: #0284c7; stroke-width: 2; }
.node-blue-end { fill: #0284c7; stroke: #ffffff; stroke-width: 2; }
.node-purple { fill: #ffffff; stroke: #a855f7; stroke-width: 2; }
.node-purple-end { fill: #9333ea; stroke: #ffffff; stroke-width: 2; }

/* BOTTOM SECTION: RELAY + EVIDENCE */
.outcome-container {
  display: grid;
  grid-template-columns: 1.28fr 0.72fr;
  gap: 16px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--line, #e2e8f0);
  border-top: 3.5px solid var(--green, #16803b);
  border-radius: 14px;
  padding: 13px 18px 12px;
  box-shadow: 0 6px 18px -2px rgba(15, 23, 42, 0.05);
}

.panel-caption {
  font-size: 8.5px;
  font-weight: 750;
  letter-spacing: 0.8px;
  color: #64748b;
  margin-bottom: 8px;
}

/* RELAY TRACK */
.relay-panel {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.relay-track {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.relay-step {
  flex: 1;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 6px 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.step-blue {
  border-color: #bae6fd;
  background: #f0f9ff;
}

.step-blue .step-model {
  color: #0284c7;
}

.step-purple {
  border-color: #e9d5ff;
  background: #faf5ff;
}

.step-purple .step-model {
  color: #7e22ce;
}

.step-badge {
  font-size: 8px;
  color: #64748b;
  font-weight: 700;
}

.step-model {
  font-size: 13px;
  font-weight: 750;
}

.step-desc {
  font-size: 9.5px;
  color: #475569;
}

.relay-arrow {
  color: #94a3b8;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.memory-ribbon {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding-top: 7px;
  border-top: 1px dashed #cbd5e1;
  color: #64748b;
}

.memory-icon {
  color: var(--purple, #a66cff);
  font-size: 14px;
  font-weight: bold;
}

.memory-text {
  font-size: 10px;
  letter-spacing: 0.2px;
}

/* EVIDENCE PANEL */
.evidence-panel {
  display: flex;
  flex-direction: column;
  border-left: 1px solid #e2e8f0;
  padding-left: 16px;
}

.score-cards {
  display: grid;
  grid-template-columns: 1fr 1.25fr;
  gap: 10px;
  align-items: stretch;
  height: 100%;
}

.score-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.baseline-score .score-value {
  color: #64748b;
  font-size: 24px;
  font-weight: 750;
  line-height: 1.1;
}

.winner-score {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.winner-score .score-value {
  color: var(--green, #16803b);
  font-size: 26px;
  font-weight: 800;
  line-height: 1.1;
}

.score-tag-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
}

.score-label {
  font-size: 10px;
  color: #64748b;
  font-weight: 600;
}

.delta-badge {
  font-size: 8.5px;
  background: #dcfce7;
  color: #15803d;
  padding: 1px 4px;
  border-radius: 4px;
  font-weight: 750;
}

.score-sub {
  font-size: 9px;
  color: #94a3b8;
  margin-top: 2px;
}

.score-sub.green {
  color: #16803b;
  font-weight: 600;
}
</style>
