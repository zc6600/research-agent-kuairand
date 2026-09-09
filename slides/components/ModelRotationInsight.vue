<template>
  <section class="research-insight-page model-diversity-page">
    <div class="visual-kicker purple">04 / FINDINGS · MODEL DIVERSITY</div>
    <h1>Model diversity can help break search plateaus.</h1>
    <p class="insight-deck">
      Different model families brought complementary search tendencies into the same persistent research world.
    </p>

    <div class="finding-grid">
      <article class="role-card card-blue">
        <div class="role-title-row">
          <span class="role-badge badge-blue mono">GPT 5.6 · DEPTH</span>
          <span class="model-tag mono">exploitation</span>
        </div>
        <h3>Deepen proven paths</h3>
        <p>Disciplined local refinement: feature cleanup, hyperparameter tuning, and careful exploitation.</p>
        <svg viewBox="0 0 280 68" class="search-pattern" role="img" aria-label="Depth-oriented search path">
          <path class="edge-quiet" d="M32 34 L82 16 M82 34 L132 17 M132 50 L186 35" />
          <path class="edge-blue" d="M32 34 L82 50 L132 50 L186 50 L238 50" />
          <circle class="node-blue" cx="32" cy="34" r="5" />
          <circle class="node-blue" cx="82" cy="50" r="5" />
          <circle class="node-blue" cx="132" cy="50" r="5" />
          <circle class="node-blue" cx="186" cy="50" r="5" />
          <circle class="node-blue-end" cx="238" cy="50" r="7" />
        </svg>
      </article>

      <article class="role-card card-purple">
        <div class="role-title-row">
          <span class="role-badge badge-purple mono">GEMINI 3.7 · BREADTH</span>
          <span class="model-tag mono">exploration</span>
        </div>
        <h3>Open new mechanisms</h3>
        <p>Broad hypothesis exploration: representation changes, mechanism pivots, and candidate screening.</p>
        <svg viewBox="0 0 280 68" class="search-pattern" role="img" aria-label="Breadth-oriented search pattern">
          <path class="edge-purple" d="M32 34 L104 13 L236 13" />
          <path class="edge-purple" d="M32 34 L104 27 L236 27" />
          <path class="edge-purple" d="M32 34 L104 41 L236 41" />
          <path class="edge-purple" d="M32 34 L104 55 L236 55" />
          <circle class="node-purple" cx="32" cy="34" r="5" />
          <circle class="node-purple" cx="104" cy="13" r="4.5" />
          <circle class="node-purple" cx="104" cy="27" r="4.5" />
          <circle class="node-purple" cx="104" cy="41" r="4.5" />
          <circle class="node-purple" cx="104" cy="55" r="4.5" />
          <circle class="node-purple-end" cx="236" cy="13" r="5.5" />
          <circle class="node-purple-end" cx="236" cy="27" r="5.5" />
          <circle class="node-purple-end" cx="236" cy="41" r="5.5" />
          <circle class="node-purple-end" cx="236" cy="55" r="5.5" />
        </svg>
      </article>
    </div>

    <div class="outcome-container">
      <div class="relay-panel">
        <div class="panel-caption mono">OBSERVED RETAINED ROTATION</div>
        <div class="relay-track">
          <div class="relay-step step-blue"><span class="step-badge mono">CYCLE 01</span><strong>GPT 5.6</strong><span>FM baseline</span></div>
          <span class="relay-arrow">→</span>
          <div class="relay-step step-purple"><span class="step-badge mono">CYCLE 02</span><strong>Gemini 3.7</strong><span>Target DIN</span></div>
          <span class="relay-arrow">→</span>
          <div class="relay-step step-blue"><span class="step-badge mono">CYCLE 03</span><strong>GPT 5.6</strong><span>Feature eng</span></div>
          <span class="relay-arrow">→</span>
          <div class="relay-step step-purple"><span class="step-badge mono">CYCLE 04</span><strong>Gemini 3.7</strong><span>Ensemble</span></div>
        </div>
        <div class="memory-ribbon mono">↻ Same research world · META retained evidence across resets</div>
      </div>

      <div class="evidence-panel">
        <div class="panel-caption mono">PUBLIC-VALIDATION PRIMARY</div>
        <div class="score-cards">
          <div class="score-card baseline-score"><span>Gemini-only</span><strong class="mono">0.6052</strong><small>single-family run</small></div>
          <div class="score-card winner-score"><span>GPT + Gemini</span><strong class="mono">0.6059</strong><small>retained peak</small></div>
        </div>
      </div>
    </div>

    <p class="finding-boundary">
      Finding, not isolated causality: the run suggests model rotation can widen the search when the research world stays shared.
    </p>
  </section>
</template>

<style scoped>
.research-insight-page.model-diversity-page {
  color: var(--ink, #111217);
  display: flex;
  flex-direction: column;
  height: 475px;
}

.model-diversity-page h1 {
  font-size: 30px;
  font-weight: 750;
  letter-spacing: -0.8px;
  line-height: 1.12;
  margin: 10px 0 4px;
}

.insight-deck {
  color: #64748b;
  font-size: 14px;
  line-height: 1.35;
  margin: 0 0 12px;
}

.finding-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr 1fr;
  margin-bottom: 12px;
}

.role-card {
  background: rgba(255, 255, 255, .96);
  border: 1px solid var(--line, #e2e8f0);
  border-radius: 12px;
  box-shadow: 0 4px 14px -2px rgba(15, 23, 42, .04);
  padding: 11px 16px 10px;
}

.card-blue { border-top: 3.5px solid var(--blue, #38bdf8); }
.card-purple { border-top: 3.5px solid var(--purple, #a66cff); }

.role-title-row {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.role-badge {
  font-size: 9px;
  font-weight: 750;
  letter-spacing: .8px;
}
.badge-blue { color: #0284c7; }
.badge-purple { color: #7e22ce; }

.model-tag {
  background: #f1f5f9;
  border-radius: 4px;
  color: #64748b;
  font-size: 9.5px;
  font-weight: 600;
  padding: 1.5px 6px;
}

.role-card h3 {
  color: var(--ink, #111217);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -.2px;
  margin: 0 0 3px;
}

.role-card p {
  color: #64748b;
  font-size: 11px;
  line-height: 1.3;
  margin: 0 0 6px;
}

.search-pattern { height: 48px; width: 100%; }
.edge-quiet { fill: none; stroke: #cbd5e1; stroke-dasharray: 3 3; stroke-width: 1.5; }
.edge-blue { fill: none; stroke: #0284c7; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.2; }
.edge-purple { fill: none; stroke: #a855f7; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.2; }
.node-blue, .node-purple { fill: #fff; stroke-width: 2; }
.node-blue { stroke: #0284c7; }
.node-purple { stroke: #a855f7; }
.node-blue-end { fill: #0284c7; stroke: #fff; stroke-width: 2; }
.node-purple-end { fill: #9333ea; stroke: #fff; stroke-width: 2; }

.outcome-container {
  background: rgba(255, 255, 255, .96);
  border: 1px solid var(--line, #e2e8f0);
  border-radius: 14px;
  border-top: 3.5px solid var(--green, #16803b);
  box-shadow: 0 6px 18px -2px rgba(15, 23, 42, .05);
  display: grid;
  gap: 16px;
  grid-template-columns: 1.28fr .72fr;
  padding: 13px 18px 12px;
}

.panel-caption {
  color: #64748b;
  font-size: 8.5px;
  font-weight: 750;
  letter-spacing: .8px;
  margin-bottom: 8px;
}

.relay-track {
  align-items: center;
  display: flex;
  gap: 6px;
  justify-content: space-between;
}

.relay-step {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 1px;
  padding: 6px 8px;
  text-align: center;
}
.step-blue { background: #f0f9ff; border-color: #bae6fd; }
.step-purple { background: #faf5ff; border-color: #e9d5ff; }
.step-blue strong { color: #0284c7; }
.step-purple strong { color: #7e22ce; }
.step-badge { color: #64748b; font-size: 8px; font-weight: 700; }
.relay-step strong { font-size: 13px; font-weight: 750; }
.relay-step span:last-child { color: #475569; font-size: 9.5px; }
.relay-arrow { color: #94a3b8; font-size: 14px; font-weight: 700; }
.memory-ribbon { border-top: 1px dashed #cbd5e1; color: #64748b; font-size: 10px; margin-top: 8px; padding-top: 7px; }

.evidence-panel { border-left: 1px solid #e2e8f0; display: flex; flex-direction: column; padding-left: 16px; }
.score-cards { align-items: stretch; display: grid; gap: 10px; grid-template-columns: 1fr 1.25fr; height: 100%; }
.score-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; padding: 6px 10px; }
.score-card span { color: #64748b; font-size: 10px; font-weight: 600; }
.score-card strong { color: #64748b; font-size: 24px; font-weight: 750; line-height: 1.1; }
.score-card small { color: #94a3b8; font-size: 9px; margin-top: 2px; }
.winner-score { background: #f0fdf4; border-color: #bbf7d0; }
.winner-score strong { color: var(--green, #16803b); font-size: 26px; font-weight: 800; }
.winner-score small { color: #15803d; }

.finding-boundary { color: #7b838d; font-size: 11px; line-height: 1.35; margin: 9px 0 0; }
</style>
