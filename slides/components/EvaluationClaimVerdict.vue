<template>
  <section class="claim-verdict-eval" aria-label="Evaluation claim and evidence verdict">
    <div class="claim-copy">
      <div class="claim-section-kicker mono">04 / EVALUATION</div>
      <div class="claim-label mono">CLAIM</div>
      <h1>An agent can carry a research task to completion.</h1>
      <p class="claim-scope">A tested model, a retained implementation, and inspectable evidence — without scientific intervention after launch.</p>
      <div class="claim-boundary mono">KUAIRAND-PURE · FIXED EVALUATOR · PUBLIC VALIDATION</div>
    </div>

    <div class="verdict-field">
      <div v-click class="verdict-anchor">
        <span class="verdict-label mono">VERDICT</span>
        <strong>Supported</strong>
        <small class="mono">IN THIS RUN</small>
      </div>

      <div v-click class="score-island">
        <span class="island-label mono">RETAINED PRIMARY</span>
        <strong>0.6059363</strong>
        <small><b>+0.0043363</b> vs official FM</small>
      </div>

      <div v-click class="trajectory-island">
        <div class="trajectory-head">
          <span class="island-label mono">RESEARCH TRAJECTORY</span>
          <span class="trajectory-range mono">E003 → E013</span>
        </div>
        <svg viewBox="0 0 500 205" role="img" aria-label="Public-validation Primary score rises from 0.601631 at E003 to 0.6059363 at E013">
          <defs>
            <linearGradient id="verdictFade" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stop-color="var(--blue)" stop-opacity=".25" />
              <stop offset="1" stop-color="var(--green)" stop-opacity=".95" />
            </linearGradient>
          </defs>
          <line x1="18" y1="152" x2="482" y2="152" class="baseline" />
          <text x="18" y="171" class="baseline-label">official FM · 0.601600</text>
          <polyline class="trajectory-glow" points="22,151 84,151 166,112 240,85 320,75 404,47 474,34" />
          <polyline class="trajectory-line" points="22,151 84,151 166,112 240,85 320,75 404,47 474,34" />
          <g class="trajectory-points">
            <circle cx="22" cy="151" r="4" /><circle cx="84" cy="151" r="4" /><circle cx="166" cy="112" r="4" />
            <circle cx="240" cy="85" r="4" /><circle cx="320" cy="75" r="4" /><circle cx="404" cy="47" r="4" />
            <circle class="final-point" cx="474" cy="34" r="7" />
          </g>
          <text x="22" y="194" text-anchor="middle" class="axis-label">C1</text>
          <text x="204" y="194" text-anchor="middle" class="axis-label">C2</text>
          <text x="320" y="194" text-anchor="middle" class="axis-label">C3</text>
          <text x="444" y="194" text-anchor="middle" class="axis-label">C4</text>
          <path d="M474 34 L474 13 L415 13" class="final-leader" />
          <text x="409" y="16" text-anchor="end" class="final-label">final retained</text>
        </svg>
      </div>

      <div v-click class="metric-island cycles-island">
        <span class="metric-value blue">4</span>
        <span class="metric-copy"><b>autonomous cycles</b><small>within a 50-iteration cap</small></span>
      </div>

      <div v-click class="metric-island experiments-island">
        <span class="metric-value orange">13</span>
        <span class="metric-copy"><b>named experiments</b><small>7 full evaluations</small></span>
      </div>

      <div v-click class="metric-island intervention-island">
        <span class="metric-value purple">0</span>
        <span class="metric-copy"><b>manual scientific interventions</b><small>after launch</small></span>
      </div>

      <div v-click class="validity-island">
        <span class="validity-mark">✓</span>
        <div><strong>170,588</strong><small>prediction rows passed the unchanged Starter Kit alignment checker</small></div>
      </div>

      <div class="field-orbit orbit-a" aria-hidden="true"></div>
      <div class="field-orbit orbit-b" aria-hidden="true"></div>
      <div class="field-dot dot-a" aria-hidden="true"></div>
      <div class="field-dot dot-b" aria-hidden="true"></div>
      <div class="field-dot dot-c" aria-hidden="true"></div>
    </div>

    <div class="claim-verdict-foot mono">PUBLIC VALIDATION ONLY · HIDDEN-TEST SCORING IS ORGANIZER-CONTROLLED</div>
  </section>
</template>

<style scoped>
.claim-verdict-eval {
  position: relative;
  min-height: 560px;
  padding: 0;
  color: var(--ink);
  overflow: hidden;
}

.claim-copy {
  position: absolute;
  z-index: 5;
  left: 48px;
  top: 42px;
  width: 350px;
}

.claim-section-kicker,
.claim-label,
.verdict-label,
.island-label {
  font-size: 10px;
  letter-spacing: 1.45px;
  font-weight: 850;
  text-transform: uppercase;
}

.claim-section-kicker { color: var(--green); }
.claim-label { margin-top: 78px; color: var(--orange); }

.claim-copy h1 {
  margin: 16px 0 0;
  max-width: 345px;
  font-size: 45px;
  line-height: .99;
  letter-spacing: -2px;
  font-weight: 790;
}

.claim-scope {
  margin: 27px 0 0;
  width: 315px;
  color: var(--muted);
  font-size: 16px;
  line-height: 1.48;
}

.claim-boundary {
  margin-top: 34px;
  width: 300px;
  color: #9aa0a6;
  font-size: 9px;
  line-height: 1.55;
  letter-spacing: .85px;
}

.verdict-field {
  position: absolute;
  z-index: 2;
  top: 28px;
  right: 22px;
  width: 555px;
  height: 505px;
}

.verdict-field::before {
  content: "";
  position: absolute;
  inset: 48px 28px 34px 18px;
  border-radius: 48% 52% 58% 42% / 48% 42% 58% 52%;
  background:
    radial-gradient(circle at 68% 18%, color-mix(in srgb, var(--green) 9%, transparent), transparent 34%),
    radial-gradient(circle at 38% 58%, color-mix(in srgb, var(--blue) 6%, transparent), transparent 42%);
  pointer-events: none;
}

.verdict-anchor {
  position: absolute;
  z-index: 4;
  left: 24px;
  top: 16px;
}

.verdict-label { color: var(--green); }
.verdict-anchor strong {
  display: block;
  margin-top: 6px;
  color: var(--ink);
  font-size: 40px;
  line-height: 1;
  letter-spacing: -1.9px;
  font-weight: 760;
}
.verdict-anchor small {
  display: block;
  margin-top: 7px;
  color: #9aa0a6;
  font-size: 9px;
  letter-spacing: 1.1px;
}

.score-island {
  position: absolute;
  z-index: 5;
  right: 8px;
  top: 28px;
  width: 285px;
  text-align: right;
}

.score-island .island-label { color: #8f969b; }
.score-island strong {
  display: block;
  margin-top: 7px;
  color: var(--green);
  font-size: 61px;
  line-height: .94;
  letter-spacing: -4px;
  font-weight: 690;
  font-variant-numeric: tabular-nums;
}
.score-island small {
  display: block;
  margin-top: 8px;
  color: var(--muted);
  font-size: 12px;
}
.score-island b { color: #16803b; }

.trajectory-island {
  position: absolute;
  z-index: 3;
  left: 30px;
  top: 130px;
  width: 495px;
  height: 214px;
}
.trajectory-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 20px;
  margin: 0 7px 0 5px;
}
.trajectory-head .island-label { color: var(--blue); }
.trajectory-range { color: #a1a6aa; font-size: 9px; letter-spacing: .7px; }
.trajectory-island svg { display: block; width: 100%; height: 192px; margin-top: 5px; overflow: visible; }
.trajectory-island svg text { font-family: 'Nunito', sans-serif; }
.baseline { stroke: #c8d1d6; stroke-width: 1; stroke-dasharray: 4 5; }
.baseline-label { fill: #93a0a7; font-size: 9px; }
.trajectory-glow { fill: none; stroke: url(#verdictFade); stroke-width: 9; stroke-linecap: round; stroke-linejoin: round; opacity: .09; }
.trajectory-line { fill: none; stroke: url(#verdictFade); stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
.trajectory-points circle { fill: white; stroke: var(--blue); stroke-width: 2; }
.trajectory-points .final-point { fill: var(--green); stroke: white; stroke-width: 2.5; filter: drop-shadow(0 2px 5px rgba(22,128,59,.18)); }
.axis-label { fill: #9aa4aa; font-size: 9px; font-weight: 800; letter-spacing: .7px; }
.final-leader { fill: none; stroke: var(--green); stroke-width: 1.1; }
.final-label { fill: #16803b; font-size: 9px; font-weight: 750; }

.metric-island {
  position: absolute;
  z-index: 6;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 160px;
}
.metric-value {
  font-size: 38px;
  line-height: .86;
  letter-spacing: -2px;
  font-weight: 760;
  font-variant-numeric: tabular-nums;
}
.metric-copy b,
.metric-copy small { display: block; }
.metric-copy b { color: var(--ink); font-size: 11px; line-height: 1.15; }
.metric-copy small { margin-top: 4px; color: #9aa0a6; font-size: 9px; }
.cycles-island { left: 26px; bottom: 84px; }
.experiments-island { left: 212px; bottom: 45px; }
.intervention-island { right: 7px; bottom: 105px; width: 188px; }

.validity-island {
  position: absolute;
  z-index: 6;
  right: 6px;
  bottom: 18px;
  display: flex;
  align-items: center;
  gap: 9px;
  width: 230px;
  padding-top: 8px;
  border-top: 1px solid color-mix(in srgb, var(--green) 24%, var(--line));
}
.validity-mark {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--green) 10%, white);
  color: #16803b;
  font-size: 13px;
  font-weight: 900;
}
.validity-island strong { display: block; color: #16803b; font-size: 18px; line-height: 1; }
.validity-island small { display: block; margin-top: 3px; color: #8f969b; font-size: 8.6px; line-height: 1.25; }

.field-orbit {
  position: absolute;
  z-index: 1;
  border: 1px solid color-mix(in srgb, var(--blue) 12%, transparent);
  border-radius: 50%;
  pointer-events: none;
}
.orbit-a { left: 92px; top: 113px; width: 350px; height: 255px; transform: rotate(-8deg); }
.orbit-b { right: 58px; top: 172px; width: 260px; height: 205px; border-color: color-mix(in srgb, var(--green) 12%, transparent); transform: rotate(12deg); }
.field-dot { position: absolute; z-index: 2; width: 5px; height: 5px; border-radius: 50%; opacity: .6; }
.dot-a { left: 6px; top: 262px; background: var(--blue); }
.dot-b { right: 30px; top: 232px; background: var(--green); }
.dot-c { left: 320px; bottom: 7px; background: var(--orange); }

.claim-verdict-foot {
  position: absolute;
  left: 48px;
  bottom: 17px;
  color: #a0a5aa;
  font-size: 8.5px;
  letter-spacing: .82px;
}

:deep(.slidev-vclick-hidden) {
  opacity: 0;
  transform: translateY(12px) scale(.985);
}

.verdict-anchor,
.score-island,
.trajectory-island,
.metric-island,
.validity-island {
  transition: opacity .52s ease, transform .6s cubic-bezier(.22,1,.36,1);
}

@media (prefers-reduced-motion: reduce) {
  .verdict-anchor,
  .score-island,
  .trajectory-island,
  .metric-island,
  .validity-island { transition: none; }
}
</style>
