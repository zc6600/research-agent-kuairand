<script setup lang="ts">
import { computed, ref } from 'vue'

type EvidenceCard = {
  id: string
  number: string
  claim: string
  kicker: string
  accent: string
  rotate: number
  x: number
  y: number
  scale: number
  detailTitle: string
  detailCopy: string
  detailMeta: string
}

const selectedId = ref<string | null>(null)

const cards: EvidenceCard[] = [
  {
    id: 'result',
    number: '01',
    claim: 'The model improved.',
    kicker: 'PUBLIC VALIDATION',
    accent: 'var(--green)',
    rotate: -16,
    x: 0,
    y: 58,
    scale: .96,
    detailTitle: 'A retained checkpoint beat the official FM reference.',
    detailCopy: 'The final E013 checkpoint reached 0.6059363 Primary on public validation, an absolute improvement of +0.0043363 over the official five-field FM reference.',
    detailMeta: '0.6016000 → 0.6059363 · GAUC 0.6728421 · nDCG@5 0.5390304',
  },
  {
    id: 'trajectory',
    number: '02',
    claim: 'The search sustained itself.',
    kicker: 'RESEARCH LOOP',
    accent: 'var(--blue)',
    rotate: -8,
    x: 92,
    y: 30,
    scale: 1,
    detailTitle: 'The score came from a trajectory, not a single lucky edit.',
    detailCopy: 'Seven Full public-validation evaluations were retained across four autonomous cycles, from a validated baseline to a 46-field, 8-seed FM ensemble.',
    detailMeta: '4 cycles · 13 named experiments · E003–E013 retained frontier',
  },
  {
    id: 'autonomy',
    number: '03',
    claim: 'It ran without scientific intervention.',
    kicker: 'AUTONOMY',
    accent: 'var(--purple)',
    rotate: 0,
    x: 196,
    y: 12,
    scale: 1.04,
    detailTitle: 'After launch, the research loop kept control of the scientific moves.',
    detailCopy: 'The retained run completed four autonomous cycles with zero manual scientific interventions after launch. Humans built the framework; the run carried the research decisions.',
    detailMeta: '0 manual scientific interventions · 0 GPU-hours · CPU / NumPy training',
  },
  {
    id: 'validity',
    number: '04',
    claim: 'The output survived the boundary.',
    kicker: 'VALID ARTIFACT',
    accent: 'var(--orange)',
    rotate: 8,
    x: 302,
    y: 31,
    scale: 1,
    detailTitle: 'The delivered file passed the unchanged Starter Kit alignment checker.',
    detailCopy: 'The final predictions were checked against the original evaluator boundary: 170,588 prediction rows aligned and passed the submission checker.',
    detailMeta: '170,588 checked predictions · unchanged checker · organizer-controlled hidden test',
  },
  {
    id: 'evidence',
    number: '05',
    claim: 'The evidence stayed inspectable.',
    kicker: 'AUDIT TRAIL',
    accent: 'var(--rose)',
    rotate: 16,
    x: 402,
    y: 62,
    scale: .96,
    detailTitle: 'The final answer remained tied to experiments, reports, and retained state.',
    detailCopy: 'SciOdyssey did not only return a score. It left a research record: named experiments, cycle reports, retained implementation state, and scoped claims.',
    detailMeta: 'experiment → report → retained State · claim ↔ evidence audit',
  },
]

const selected = computed(() => cards.find(card => card.id === selectedId.value) ?? null)

function openCard(id: string) {
  selectedId.value = id
}

function closeCard() {
  selectedId.value = null
}
</script>

<template>
  <section class="claim-verdict-eval" aria-label="Evaluation claim and evidence cards">
    <div class="claim-copy" :class="{ dimmed: selected }">
      <div class="claim-section-kicker mono">04 / EVALUATION</div>
      <div class="claim-label mono">CLAIM</div>
      <h1>Can an agent carry a research task to completion?</h1>
      <p class="claim-scope">A tested model, a retained implementation, and inspectable evidence.</p>
      <div class="claim-boundary mono">KUAIRAND-PURE · FIXED EVALUATOR · PUBLIC VALIDATION</div>
    </div>

    <div class="evidence-hand" :class="{ inspecting: selected }" aria-label="A fanned hand of evidence cards">
      <button
        v-for="card in cards"
        :key="card.id"
        v-click
        class="evidence-card"
        :class="[`card-${card.id}`, { muted: selected && selected.id !== card.id, active: selected && selected.id === card.id }]"
        :style="{
          '--accent': card.accent,
          '--rotate': `${card.rotate}deg`,
          '--x': `${card.x}px`,
          '--y': `${card.y}px`,
          '--scale': card.scale,
        }"
        type="button"
        @click.stop="openCard(card.id)"
      >
        <span class="card-topline"><span class="card-number mono">{{ card.number }}</span><span class="card-kicker mono">{{ card.kicker }}</span></span>
        <strong>{{ card.claim }}</strong>

        <span class="card-visual result-visual" v-if="card.id === 'result'">
          <svg viewBox="0 0 210 112" aria-hidden="true">
            <line x1="14" y1="83" x2="195" y2="83" class="mini-baseline" />
            <polyline points="15,82 42,82 70,68 104,55 136,51 166,35 194,27" class="mini-line" />
            <circle cx="194" cy="27" r="5" class="mini-final" />
            <text x="16" y="102">0.6016</text><text x="194" y="18" text-anchor="end">0.605936</text>
          </svg>
        </span>

        <span class="card-visual trajectory-visual" v-else-if="card.id === 'trajectory'">
          <span class="cycle-row"><i>C1</i><b></b><i>C2</i><b></b><i>C3</i><b></b><i>C4</i></span>
          <span class="cycle-count"><b>13</b><small>experiments</small></span>
        </span>

        <span class="card-visual autonomy-visual" v-else-if="card.id === 'autonomy'">
          <span class="zero">0</span>
          <span class="zero-caption">manual scientific interventions</span>
        </span>

        <span class="card-visual validity-visual" v-else-if="card.id === 'validity'">
          <span class="receipt-check">✓</span>
          <span><b>170,588</b><small>checked rows</small></span>
        </span>

        <span class="card-visual evidence-visual" v-else>
          <span>experiment</span><b>→</b><span>report</span><b>→</b><span>State</span>
        </span>

        <span class="card-footer mono">OPEN EVIDENCE ↗</span>
      </button>
    </div>

    <div v-if="selected" class="inspection-layer" @click.self="closeCard">
      <article class="inspection-card" :class="`inspect-${selected.id}`" :style="{ '--accent': selected.accent }">
        <button class="inspection-close mono" type="button" @click.stop="closeCard">← BACK TO HAND</button>
        <div class="inspection-kicker mono">{{ selected.number }} / {{ selected.kicker }}</div>
        <h2>{{ selected.claim }}</h2>
        <p>{{ selected.detailTitle }}</p>

        <div class="inspection-visual inspection-result" v-if="selected.id === 'result'">
          <div class="score-before"><span class="mono">OFFICIAL FM</span><b>0.6016000</b></div>
          <svg viewBox="0 0 520 180" aria-hidden="true">
            <line x1="28" y1="132" x2="492" y2="132" class="inspect-baseline" />
            <polyline points="32,130 94,130 176,95 250,72 332,62 416,35 488,23" class="inspect-line" />
            <circle cx="488" cy="23" r="9" class="inspect-final" />
            <text x="32" y="158">E003</text><text x="488" y="17" text-anchor="end">E013</text>
          </svg>
          <div class="score-after"><span class="mono">SCIODYSSEY</span><b>0.6059363</b><small>+0.0043363</small></div>
        </div>

        <div class="inspection-visual inspection-trajectory" v-else-if="selected.id === 'trajectory'">
          <div class="inspect-cycles"><span>C1</span><i></i><span>C2</span><i></i><span>C3</span><i></i><span>C4</span></div>
          <div class="inspect-experiments"><b>13</b><span>named experiments</span><small>E001–E013 · 7 Full evaluations</small></div>
        </div>

        <div class="inspection-visual inspection-autonomy" v-else-if="selected.id === 'autonomy'">
          <div class="autonomy-zero">0</div>
          <div class="autonomy-copy"><strong>manual scientific interventions</strong><span>after launch, across the retained run</span></div>
        </div>

        <div class="inspection-visual inspection-validity" v-else-if="selected.id === 'validity'">
          <div class="validity-receipt"><span>✓</span><b>170,588</b><small>prediction rows passed</small></div>
          <div class="validity-lines"><i></i><i></i><i></i><strong>unchanged Starter Kit alignment checker</strong></div>
        </div>

        <div class="inspection-visual inspection-evidence" v-else>
          <div class="evidence-chain"><span>experiment</span><i></i><span>cycle report</span><i></i><span>retained State</span></div>
          <div class="audit-stamp mono">CLAIM ↔ EVIDENCE</div>
        </div>

        <div class="inspection-copy">{{ selected.detailCopy }}</div>
        <div class="inspection-meta mono">{{ selected.detailMeta }}</div>
      </article>
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

.claim-verdict-eval::before {
  content: "";
  position: absolute;
  inset: 34px 18px 18px 42%;
  background:
    radial-gradient(circle at 68% 35%, color-mix(in srgb, var(--green) 10%, transparent), transparent 32%),
    radial-gradient(circle at 35% 72%, color-mix(in srgb, var(--blue) 8%, transparent), transparent 38%);
  pointer-events: none;
}

.claim-copy {
  position: absolute;
  z-index: 4;
  left: 48px;
  top: 44px;
  width: 355px;
  transition: opacity .42s ease, transform .48s cubic-bezier(.22,1,.36,1);
}
.claim-copy.dimmed { opacity: .18; transform: translateX(-8px); }

.claim-section-kicker,
.claim-label,
.card-number,
.card-kicker,
.inspection-kicker,
.card-footer {
  font-size: 10px;
  letter-spacing: 1.35px;
  font-weight: 850;
  text-transform: uppercase;
}
.claim-section-kicker { color: var(--green); }
.claim-label { margin-top: 80px; color: var(--orange); }
.claim-copy h1 {
  margin: 16px 0 0;
  max-width: 350px;
  font-size: 45px;
  line-height: .99;
  letter-spacing: -2.05px;
  font-weight: 790;
}
.claim-scope {
  margin: 28px 0 0;
  width: 315px;
  color: var(--muted);
  font-size: 16px;
  line-height: 1.48;
}
.claim-boundary {
  margin-top: 34px;
  width: 310px;
  color: #9aa0a6;
  font-size: 9px;
  line-height: 1.55;
  letter-spacing: .85px;
}

.evidence-hand {
  position: absolute;
  z-index: 3;
  right: 18px;
  top: 50px;
  width: 558px;
  height: 448px;
  perspective: 1200px;
  transform: translateX(0);
  transition: opacity .42s ease, transform .42s cubic-bezier(.22,1,.36,1);
}
.evidence-hand.inspecting { opacity: .2; transform: translateX(12px) scale(.96); pointer-events: none; }

.evidence-card {
  position: absolute;
  left: var(--x);
  top: var(--y);
  width: 185px;
  height: 292px;
  border: 0;
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.98), rgba(250,251,252,.94)),
    radial-gradient(circle at 70% 24%, color-mix(in srgb, var(--accent) 18%, transparent), transparent 38%);
  box-shadow: 0 18px 44px rgba(27, 39, 52, .11), 0 1px 0 rgba(255,255,255,.9) inset;
  transform: translateY(18px) rotate(var(--rotate)) scale(var(--scale));
  transform-origin: 50% 106%;
  color: var(--ink);
  text-align: left;
  padding: 19px 17px 16px;
  cursor: pointer;
  transition: transform .42s cubic-bezier(.22,1,.36,1), box-shadow .42s ease, opacity .35s ease, filter .35s ease;
}
.evidence-card::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid color-mix(in srgb, var(--accent) 34%, var(--line));
  pointer-events: none;
}
.evidence-card:hover,
.evidence-card:focus-visible {
  transform: translateY(-2px) rotate(calc(var(--rotate) * .58)) scale(calc(var(--scale) + .025));
  box-shadow: 0 28px 58px rgba(27, 39, 52, .16), 0 1px 0 rgba(255,255,255,.95) inset;
  outline: none;
  z-index: 30;
}
.evidence-card.muted { opacity: .25; filter: grayscale(.28); }
.evidence-card.active { z-index: 35; }

.card-topline { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.card-number { color: var(--accent); }
.card-kicker { color: #9aa0a6; font-size: 8px; letter-spacing: .95px; }
.evidence-card > strong {
  display: block;
  margin-top: 18px;
  width: 142px;
  font-size: 22px;
  line-height: 1.04;
  letter-spacing: -.8px;
  font-weight: 790;
}
.card-visual { display: block; position: absolute; left: 17px; right: 17px; bottom: 43px; height: 96px; }
.card-footer { position: absolute; left: 17px; bottom: 18px; color: color-mix(in srgb, var(--accent) 68%, #8f969b); font-size: 8.4px; letter-spacing: .9px; }

.result-visual svg { width: 100%; height: 100%; overflow: visible; }
.result-visual text { fill: #9099a0; font-size: 10px; font-family: 'Nunito', sans-serif; font-weight: 750; }
.mini-baseline { stroke: #d7dde1; stroke-width: 1; stroke-dasharray: 3 4; }
.mini-line { fill: none; stroke: var(--accent); stroke-width: 3.2; stroke-linecap: round; stroke-linejoin: round; }
.mini-final { fill: var(--accent); stroke: white; stroke-width: 2; }
.trajectory-visual { display: grid; align-content: center; gap: 12px; }
.cycle-row { display: flex; align-items: center; gap: 7px; color: #6e7780; font-size: 10px; font-weight: 850; }
.cycle-row i { display: grid; place-items: center; width: 27px; height: 27px; border-radius: 50%; background: color-mix(in srgb, var(--accent) 10%, white); color: var(--accent); font-style: normal; }
.cycle-row b { display: block; width: 14px; height: 1px; background: color-mix(in srgb, var(--accent) 35%, #dce1e5); }
.cycle-count b { display: block; color: var(--accent); font-size: 36px; line-height: .9; letter-spacing: -1.3px; }
.cycle-count small { display: block; margin-top: 4px; color: #8d969d; font-size: 10px; }
.autonomy-visual { display: grid; align-content: center; }
.zero { color: var(--accent); font-size: 82px; line-height: .78; letter-spacing: -5px; font-weight: 720; }
.zero-caption { color: #8d969d; font-size: 10px; line-height: 1.25; width: 120px; }
.validity-visual { display: flex; align-items: center; gap: 11px; }
.receipt-check { display: grid; place-items: center; width: 46px; height: 46px; border-radius: 50%; background: color-mix(in srgb, var(--accent) 11%, white); color: var(--accent); font-size: 24px; font-weight: 900; }
.validity-visual b { display: block; color: var(--accent); font-size: 25px; letter-spacing: -1px; line-height: 1; }
.validity-visual small { display: block; margin-top: 5px; color: #8d969d; font-size: 10px; }
.evidence-visual { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 7px; align-items: center; color: #7e8790; font-size: 9px; font-weight: 800; }
.evidence-visual span { display: grid; place-items: center; min-height: 34px; border-radius: 12px; background: color-mix(in srgb, var(--accent) 8%, white); }
.evidence-visual b { color: var(--accent); }

:deep(.slidev-vclick-hidden) { opacity: 0; transform: translateY(38px) rotate(var(--rotate)) scale(.9); }

.inspection-layer {
  position: absolute;
  z-index: 20;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(255,255,255,.62);
  backdrop-filter: blur(6px);
}
.inspection-card {
  position: relative;
  width: 705px;
  height: 466px;
  border-radius: 30px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.98), rgba(250,251,252,.95)),
    radial-gradient(circle at 74% 26%, color-mix(in srgb, var(--accent) 12%, transparent), transparent 38%);
  box-shadow: 0 34px 90px rgba(24, 35, 47, .18);
  padding: 34px 38px;
  overflow: hidden;
  animation: inspectIn .28s cubic-bezier(.22,1,.36,1) both;
}
.inspection-card::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid color-mix(in srgb, var(--accent) 34%, var(--line));
  pointer-events: none;
}
@keyframes inspectIn {
  from { opacity: 0; transform: translateY(18px) scale(.965) rotate(-1.5deg); }
  to { opacity: 1; transform: translateY(0) scale(1) rotate(0); }
}
.inspection-close {
  position: absolute;
  right: 30px;
  top: 25px;
  border: 0;
  background: transparent;
  color: #8b939a;
  font-size: 9px;
  letter-spacing: 1px;
  cursor: pointer;
}
.inspection-kicker { color: var(--accent); }
.inspection-card h2 {
  margin: 18px 0 0;
  width: 390px;
  font-size: 39px;
  line-height: 1.02;
  letter-spacing: -1.75px;
  font-weight: 790;
}
.inspection-card > p {
  margin: 18px 0 0;
  width: 410px;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.45;
}
.inspection-visual {
  position: absolute;
  right: 36px;
  top: 96px;
  width: 230px;
  height: 220px;
}
.inspection-copy {
  position: absolute;
  left: 38px;
  right: 330px;
  bottom: 78px;
  color: #6f7780;
  font-size: 14px;
  line-height: 1.45;
}
.inspection-meta {
  position: absolute;
  left: 38px;
  right: 38px;
  bottom: 33px;
  padding-top: 13px;
  border-top: 1px solid color-mix(in srgb, var(--accent) 22%, var(--line));
  color: #89919a;
  font-size: 9px;
  letter-spacing: .8px;
}
.inspection-result { width: 300px; right: 30px; top: 92px; }
.inspection-result svg { position: absolute; left: -18px; top: 44px; width: 300px; height: 112px; }
.inspect-baseline { stroke: #d2dade; stroke-dasharray: 4 5; }
.inspect-line { fill: none; stroke: var(--accent); stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
.inspect-final { fill: var(--accent); stroke: white; stroke-width: 3; }
.inspection-result text { fill: #8e979f; font: 800 13px 'Nunito', sans-serif; }
.score-before span,
.score-after span { display: block; color: #9aa0a6; font-size: 9px; letter-spacing: 1px; }
.score-before b { color: #7a838a; font-size: 23px; }
.score-after { position: absolute; right: 0; bottom: 2px; text-align: right; }
.score-after b { display: block; color: var(--accent); font-size: 34px; letter-spacing: -1.7px; }
.score-after small { color: #16803b; }
.inspect-cycles { display: flex; align-items: center; gap: 9px; margin-top: 34px; }
.inspect-cycles span { display: grid; place-items: center; width: 42px; height: 42px; border-radius: 50%; background: color-mix(in srgb, var(--accent) 10%, white); color: var(--accent); font-size: 13px; font-weight: 900; }
.inspect-cycles i { width: 18px; height: 1px; background: color-mix(in srgb, var(--accent) 38%, #d7dde1); }
.inspect-experiments { margin-top: 34px; }
.inspect-experiments b { display: block; color: var(--accent); font-size: 72px; line-height: .85; letter-spacing: -4px; }
.inspect-experiments span { display: block; margin-top: 8px; font-weight: 850; }
.inspect-experiments small { display: block; color: #8e979f; margin-top: 5px; }
.autonomy-zero { color: var(--accent); font-size: 138px; line-height: .8; letter-spacing: -8px; font-weight: 720; }
.autonomy-copy strong { display: block; width: 190px; font-size: 18px; line-height: 1.08; }
.autonomy-copy span { display: block; margin-top: 8px; color: #8e979f; font-size: 12px; }
.validity-receipt { display: grid; justify-items: center; margin-top: 5px; }
.validity-receipt span { display: grid; place-items: center; width: 54px; height: 54px; border-radius: 50%; color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, white); font-size: 28px; font-weight: 900; }
.validity-receipt b { display: block; margin-top: 16px; color: var(--accent); font-size: 43px; letter-spacing: -2.2px; }
.validity-receipt small { color: #8e979f; }
.validity-lines { margin: 19px auto 0; width: 180px; }
.validity-lines i { display: block; height: 6px; margin: 7px 0; border-radius: 99px; background: color-mix(in srgb, var(--accent) 12%, #edf0f2); }
.validity-lines strong { display: block; margin-top: 13px; font-size: 12px; line-height: 1.25; text-align: center; }
.evidence-chain { display: grid; gap: 8px; margin-top: 22px; }
.evidence-chain span { display: grid; place-items: center; height: 43px; border-radius: 14px; background: color-mix(in srgb, var(--accent) 8%, white); color: #5f6870; font-weight: 850; }
.evidence-chain i { width: 1px; height: 14px; background: color-mix(in srgb, var(--accent) 35%, #d6dde2); justify-self: center; }
.audit-stamp { position: absolute; right: 3px; bottom: 0; color: var(--accent); font-size: 10px; letter-spacing: 1px; }

.claim-verdict-foot {
  position: absolute;
  left: 48px;
  bottom: 17px;
  color: #a0a5aa;
  font-size: 8.5px;
  letter-spacing: .82px;
}

@media (prefers-reduced-motion: reduce) {
  .claim-copy,
  .evidence-hand,
  .evidence-card,
  .verdict-anchor,
  .score-island,
  .trajectory-island,
  .metric-island,
  .validity-island { transition: none; }
  .inspection-card { animation: none; }
}
</style>
