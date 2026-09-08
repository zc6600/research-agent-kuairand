<template>
  <section class="model-rotation-insight" aria-label="Model rotation insight">
    <div class="rotation-copy">
      <div class="rotation-label mono">INSIGHT 01</div>
      <h2>Reset the context.<br />Rotate the prior.</h2>
      <p>
        The meta-scientist architecture already worked with one model. The best retained run came when fresh Scientists rotated across GPT and Gemini.
      </p>
      <div class="rotation-boundary mono">BEST OBSERVED RUN · NOT A CONTROLLED MODEL-DIVERSITY ABLATION</div>
    </div>

    <div class="rotation-stage" aria-hidden="true">
      <div class="world-core">
        <span class="mono">RESEARCH WORLD</span>
        <strong>persistent evidence</strong>
      </div>

      <div class="track track-single">
        <div class="track-caption mono">ARCHITECTURE WORKS</div>
        <div class="agent-pill gemini-pill">Gemini Scientist</div>
        <div class="track-line"></div>
        <div class="score-card single-score">
          <span class="mono">single-model SciOdyssey</span>
          <strong>0.6052</strong>
        </div>
      </div>

      <div class="track track-mixed">
        <div class="track-caption mono">BEST RUN</div>
        <div class="agent-pill gpt-pill pill-a">GPT</div>
        <div class="agent-pill gemini-pill pill-b">Gemini</div>
        <div class="agent-pill gpt-pill pill-c">GPT</div>
        <svg viewBox="0 0 460 160" role="img" aria-label="Rotating scientist models feed into the same research world">
          <path class="rotation-path" d="M52 120 C150 22 302 22 406 120" />
          <path class="rotation-path faint" d="M86 121 C174 74 282 74 370 121" />
          <path class="rotation-arrow" d="M397 111 l17 11 -19 8" />
        </svg>
        <div class="score-card best-score">
          <span class="mono">mixed Scientist trajectories</span>
          <strong>0.6059363</strong>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.model-rotation-insight {
  border-top: 1px solid var(--line);
  display: grid;
  grid-column: 1 / -1;
  grid-template-columns: .82fr 1.18fr;
  gap: 30px;
  min-height: 286px;
  padding: 16px 0 18px;
}

.rotation-copy {
  align-self: center;
}

.rotation-label,
.rotation-boundary {
  color: var(--blue);
  font-size: 9px;
  font-weight: 850;
  letter-spacing: 1.2px;
}

.rotation-copy h2 {
  color: var(--ink);
  font-size: 37px;
  font-weight: 760;
  letter-spacing: -1.8px;
  line-height: .98;
  margin: 9px 0 13px;
}

.rotation-copy p {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.36;
  margin: 0 0 15px;
  max-width: 330px;
}

.rotation-boundary {
  color: var(--rose);
  line-height: 1.25;
}

.rotation-stage {
  position: relative;
  min-height: 260px;
}

.world-core {
  position: absolute;
  left: 50%;
  top: 92px;
  transform: translateX(-50%);
  width: 152px;
  height: 94px;
  border: 1px solid color-mix(in srgb, var(--green) 42%, var(--line));
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(255,255,255,.96), rgba(244,251,247,.9));
  box-shadow: 0 18px 42px rgba(25, 42, 34, .12);
  display: grid;
  place-content: center;
  text-align: center;
  z-index: 5;
}

.world-core span {
  color: var(--green);
  font-size: 9px;
  font-weight: 850;
  letter-spacing: 1px;
}

.world-core strong {
  color: var(--ink);
  font-size: 15px;
  line-height: 1.05;
  margin-top: 5px;
}

.track {
  position: absolute;
  border: 1px solid var(--line);
  border-radius: 22px;
  background: rgba(255,255,255,.76);
}

.track-single {
  left: 0;
  top: 22px;
  width: 210px;
  height: 210px;
}

.track-mixed {
  right: 0;
  top: 0;
  width: 336px;
  height: 236px;
  border-color: color-mix(in srgb, var(--purple) 22%, var(--line));
  background:
    radial-gradient(circle at 28% 24%, color-mix(in srgb, var(--blue) 10%, transparent), transparent 34%),
    radial-gradient(circle at 78% 28%, color-mix(in srgb, var(--purple) 10%, transparent), transparent 38%),
    rgba(255,255,255,.83);
}

.track-caption {
  position: absolute;
  left: 18px;
  top: 14px;
  color: #a0a4aa;
  font-size: 8.5px;
  font-weight: 850;
  letter-spacing: 1.1px;
}

.agent-pill {
  position: absolute;
  z-index: 6;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: white;
  box-shadow: 0 11px 26px rgba(18, 30, 43, .10);
  color: var(--ink);
  font-size: 12px;
  font-weight: 750;
  padding: 8px 12px;
  white-space: nowrap;
}

.gemini-pill {
  border-color: color-mix(in srgb, var(--purple) 35%, var(--line));
  color: var(--purple);
}

.gpt-pill {
  border-color: color-mix(in srgb, var(--blue) 35%, var(--line));
  color: var(--blue);
}

.track-single .agent-pill {
  left: 28px;
  top: 70px;
}

.pill-a { left: 38px; top: 74px; }
.pill-b { left: 135px; top: 36px; }
.pill-c { right: 42px; top: 74px; }

.track-line {
  position: absolute;
  left: 104px;
  top: 105px;
  width: 94px;
  height: 1.5px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--purple) 50%, transparent), transparent);
}

.track-mixed svg {
  position: absolute;
  left: 16px;
  top: 54px;
  width: 304px;
  height: 112px;
  overflow: visible;
}

.rotation-path {
  fill: none;
  stroke: color-mix(in srgb, var(--purple) 52%, var(--blue));
  stroke-width: 2.3;
  stroke-linecap: round;
}

.rotation-path.faint {
  opacity: .22;
  stroke-width: 1.6;
}

.rotation-arrow {
  fill: color-mix(in srgb, var(--purple) 58%, var(--blue));
}

.score-card {
  position: absolute;
  z-index: 7;
  border-radius: 18px;
  background: var(--ink);
  box-shadow: 0 20px 42px rgba(15, 23, 42, .18);
  color: white;
  padding: 13px 16px;
}

.score-card span {
  color: rgba(255,255,255,.66);
  display: block;
  font-size: 8px;
  letter-spacing: .8px;
  margin-bottom: 5px;
  text-transform: uppercase;
}

.score-card strong {
  color: white;
  font-size: 28px;
  font-weight: 650;
  letter-spacing: -1.4px;
  line-height: 1;
}

.single-score {
  bottom: 19px;
  left: 28px;
}

.best-score {
  right: 28px;
  bottom: 22px;
  background: linear-gradient(135deg, #121826, color-mix(in srgb, var(--purple) 42%, #121826));
}
</style>
