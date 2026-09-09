<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import EvaluationCardBody from './EvaluationCardBody.vue'
import { useTalkSteps } from '../composables/useTalkSteps'

type Card = {
  id: string
  no: string
  kicker: string
  claim: string
  accent: string
  rotate: number
  x: number
  y: number
  scale: number
  z: number
  title: string
  detail: string
  meta: string
}

const selectedId = ref<string | null>(null)

const cards: Card[] = [
  { id: 'result', no: '01', kicker: 'MEASURED RESULT', claim: 'The model got better.', accent: 'var(--green)', rotate: -15, x: 0, y: 30, scale: .96, z: 1, title: 'A retained checkpoint beat the official FM reference.', detail: 'The final E013 checkpoint reached 0.6059363 Primary on public validation, an absolute improvement of +0.0043363 over the official five-field FM reference.', meta: '0.6016000 → 0.6059363 · GAUC 0.6728421 · nDCG@5 0.5390304' },
  { id: 'trajectory', no: '02', kicker: 'SUSTAINED SEARCH', claim: 'The search stayed productive.', accent: 'var(--blue)', rotate: -7, x: 140, y: 8, scale: .96, z: 2, title: 'The score came from a trajectory, not a single lucky edit.', detail: 'Seven Full public-validation evaluations were retained across four autonomous cycles, from a validated baseline to a 46-field, 8-seed FM ensemble.', meta: '4 cycles · 7 Full experiments · E003–E013 retained frontier' },
  { id: 'robustness', no: '03', kicker: 'SELF-HEALING & GATEKEEPING', claim: 'The agent recovered from failure.', accent: 'var(--rose)', rotate: 0, x: 280, y: 0, scale: .96, z: 3, title: 'Autonomous runtime recovery & source-level Meta gatekeeping.', detail: 'The Scientist self-healed serialization crashes in Cycle 1. In one experiment, Meta audited proxy data flow, caught UNK user sampling distortion, and rejected spurious state promotion.', meta: 'Cycle 1 float32 auto-repair · Experiment proxy audit & state rejection · 0 human interventions' },
  { id: 'comparison', no: '04', kicker: 'ARCHITECTURE ABLATION', claim: 'Architecture changes outcomes.', accent: 'var(--purple)', rotate: 7, x: 420, y: 8, scale: .96, z: 4, title: 'Same model family, stronger research organization.', detail: 'Direct Antigravity reached 0.6045803. Antigravity with delegated subagents reached ≈0.6047. Meta-Scientist over Antigravity reached 0.6052 before the mixed-model best run.', meta: 'AGY direct 0.60458 · AGY+subagents ≈0.6047 · Meta+AGY 0.6052 · Best mixed 0.6059363' },
  { id: 'tokenmaxxing', no: '05', kicker: 'RESOURCE ACCOUNTING', claim: 'We are not tokenmaxxing', accent: 'var(--orange)', rotate: 15, x: 560, y: 30, scale: .96, z: 5, title: 'Resource use is part of the evidence, not the thesis.', detail: 'The project-level resource story lives here: ~US$10 subscription-equivalent usage on consumer hardware with zero GPU-hours.', meta: '~US$10 project estimate · 1 × MacBook M2 · 0 GPU-hours · 100% CPU inference' },
]

const selected = computed(() => cards.find(card => card.id === selectedId.value) ?? null)
const talkStep = useTalkSteps(cards.length * 2, step => {
  selectedId.value = step > 0 && step % 2 === 0 ? cards[step / 2 - 1].id : null
})
const dialog = ref<HTMLElement | null>(null)
let trigger: HTMLElement | null = null
const openCard = async (id: string) => {
  trigger = document.activeElement as HTMLElement
  selectedId.value = id
  await nextTick()
  dialog.value?.focus()
}
const closeCard = () => {
  selectedId.value = null
  trigger?.focus()
}
const handleKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' || event.key === 'Tab') event.stopPropagation()
  if (event.key === 'Escape') { event.preventDefault(); closeCard() }
  if (event.key === 'Tab') {
    const controls = Array.from(dialog.value?.querySelectorAll<HTMLElement>('button:not(:disabled), [tabindex="0"], a[href]') ?? [])
    const first = controls[0], last = controls.at(-1)
    if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog.value)) { event.preventDefault(); last?.focus() }
    else if (!event.shiftKey && (document.activeElement === last || document.activeElement === dialog.value)) { event.preventDefault(); first?.focus() }
  }
}
</script>

<template>
  <section class="eval-claim-cards" :class="{ 'has-inspection': selected }" aria-label="Evaluation evidence cards">
    <header class="claim-header" :class="{ dimmed: selected }">
      <div class="section-kicker mono">03 / EVALUATION</div>
      <div class="claim-label mono">CLAIM</div>
      <h1>Our agent can carry a research task to completion.</h1>
      <div class="claim-boundary mono"><span>KUAIRAND-PURE</span><span>FIXED EVALUATOR</span><span>PUBLIC VALIDATION</span></div>
    </header>

    <div class="evidence-hand" :class="{ inspecting: selected }">
      <button
        v-for="(card, index) in cards"
        :key="card.id"
        v-show="talkStep >= index * 2 + 1"
        type="button"
        class="evidence-card"
        :class="[`card-${card.id}`]"
        :style="{ '--accent': card.accent, '--rotate': `${card.rotate}deg`, '--x': `${card.x}px`, '--y': `${card.y}px`, '--scale': card.scale, '--z': card.z }"
        @click.stop="openCard(card.id)"
      >
        <span class="card-meta"><span class="card-no mono">{{ card.no }}</span><span class="card-kicker mono">{{ card.kicker }}</span></span>
        <strong>{{ card.claim }}</strong>
        <span class="card-rule" aria-hidden="true"></span>
        <span class="card-footer mono">OPEN EVIDENCE</span>
      </button>
    </div>

    <div v-if="selected" ref="dialog" class="inspection-layer" role="dialog" aria-modal="true" :aria-label="selected.claim" tabindex="-1" @keydown="handleKey" @click.stop @click.self="closeCard">
      <article class="inspection-card" :class="`inspect-${selected.id}`" :style="{ '--accent': selected.accent }">
        <header class="inspection-heading">
          <button class="inspection-close mono" type="button" @click.stop="closeCard">BACK TO HAND ×</button>
          <div class="inspection-kicker mono">{{ selected.no }} / {{ selected.kicker }}</div>
          <h2>{{ selected.claim }}</h2>
        </header>
        <div class="inspection-content" tabindex="0" aria-label="Card contents" @wheel.stop @touchmove.stop>
          <EvaluationCardBody :card="selected.id" />
        </div>
        <div v-if="selected.id !== 'comparison'" class="inspection-meta mono">{{ selected.meta }}</div>
      </article>
    </div>

    <div class="claim-foot mono">PUBLIC VALIDATION ONLY · HIDDEN-TEST SCORING IS ORGANIZER-CONTROLLED</div>
  </section>
</template>

<style scoped>
.eval-claim-cards {
  position: relative;
  min-height: 560px;
  padding: 0;
  color: var(--ink);
  overflow: hidden;
}

.eval-claim-cards::before {
  content: "";
  position: absolute;
  inset: 88px 0 8px 24%;
  background:
    radial-gradient(circle at 70% 30%, color-mix(in srgb, var(--green) 9%, transparent), transparent 30%),
    radial-gradient(circle at 42% 76%, color-mix(in srgb, var(--blue) 6%, transparent), transparent 38%);
  pointer-events: none;
}

.claim-header {
  position: absolute;
  z-index: 8;
  left: 48px;
  top: 34px;
  right: 42px;
  transition: opacity .42s ease, transform .48s cubic-bezier(.22,1,.36,1);
}
.claim-header.dimmed { opacity: .16; transform: translateY(-4px); }

.section-kicker,
.claim-label,
.claim-boundary,
.card-no,
.card-kicker,
.card-footer,
.inspection-kicker {
  font-size: 10px;
  letter-spacing: 1.35px;
  font-weight: 850;
  text-transform: uppercase;
}
.section-kicker { color: var(--green); }
.claim-label { margin-top: 20px; color: var(--orange); }
.claim-header h1 {
  margin: 9px 0 0;
  max-width: 720px;
  font-size: 34px;
  line-height: 1.06;
  letter-spacing: -1.2px;
  font-weight: 730;
}
.claim-boundary {
  display: flex;
  gap: 15px;
  margin-top: 13px;
  color: #9aa0a6;
  font-size: 8.8px;
}
.claim-boundary span + span::before {
  content: "";
  display: inline-block;
  width: 3px;
  height: 3px;
  margin: 0 13px 2px 0;
  border-radius: 50%;
  background: color-mix(in srgb, var(--green) 56%, #bac2c8);
}

.evidence-hand {
  position: absolute;
  z-index: 4;
  right: 68px;
  top: 197px;
  width: 708px;
  height: 306px;
  perspective: 1400px;
  transition: opacity .42s ease, transform .42s cubic-bezier(.22,1,.36,1);
}
.evidence-hand.inspecting { opacity: .18; transform: translateX(18px) scale(.95); pointer-events: none; }

.evidence-card {
  position: absolute;
  z-index: var(--z);
  left: var(--x);
  top: var(--y);
  width: 148px;
  height: 258px;
  border: 0;
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(255,255,255,1), rgba(250,251,252,.99)),
    radial-gradient(circle at 72% 18%, color-mix(in srgb, var(--accent) 9%, transparent), transparent 45%);
  box-shadow: 0 22px 54px rgba(27, 39, 52, .14), 0 1px 0 rgba(255,255,255,.92) inset;
  transform: translateY(12px) rotate(var(--rotate)) scale(var(--scale));
  transform-origin: 50% 116%;
  color: var(--ink);
  text-align: left;
  padding: 18px 15px 15px;
  cursor: pointer;
  transition: transform .42s cubic-bezier(.22,1,.36,1), box-shadow .42s ease, opacity .35s ease, filter .35s ease;
}
.evidence-card::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid color-mix(in srgb, var(--accent) 30%, var(--line));
  pointer-events: none;
}
.evidence-card:hover,
.evidence-card:focus-visible {
  transform: translateY(-12px) rotate(calc(var(--rotate) * .42)) scale(calc(var(--scale) + .035));
  box-shadow: 0 34px 72px rgba(27, 39, 52, .19), 0 1px 0 rgba(255,255,255,.96) inset;
  outline: none;
  z-index: 30;
}
.card-meta { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
.card-no { color: var(--accent); }
.card-kicker { color: #9aa0a6; font-size: 6.8px; letter-spacing: .68px; text-align: right; }
.evidence-card strong {
  display: block;
  margin-top: 28px;
  width: 118px;
  font-size: 21px;
  line-height: 1.04;
  letter-spacing: -.85px;
  font-weight: 790;
}
.card-result strong { font-size: 22px; }
.card-tokenmaxxing strong { text-align: center; }
.card-rule {
  position: absolute;
  left: 15px;
  right: 15px;
  bottom: 40px;
  height: 2px;
  border-radius: 99px;
  background: linear-gradient(90deg, var(--accent), transparent);
  opacity: .58;
}
.card-footer {
  position: absolute;
  left: 15px;
  bottom: 16px;
  color: color-mix(in srgb, var(--accent) 64%, #8f969b);
  font-size: 7.4px;
  letter-spacing: .8px;
}

:deep(.slidev-vclick-hidden) { opacity: 0; transform: translateY(46px) rotate(var(--rotate)) scale(.88); }

.inspection-layer {
  position: absolute;
  z-index: 20;
  inset: -42px -56px auto;
  height: 551.25px;
  display: grid;
  place-items: center;
  background: rgba(255,255,255,.62);
  backdrop-filter: blur(6px);
}
.inspection-card {
  position: relative; width: 924px; height: 533px; display: flex; flex-direction: column;
  border-radius: 26px; background: #fff; border: 1px solid color-mix(in srgb, var(--accent) 35%, #e6e6e8);
  box-shadow: 0 30px 90px rgba(24,35,47,.18); overflow: hidden;
  animation: inspectIn .28s cubic-bezier(.22,1,.36,1) both;
}
@keyframes inspectIn { from { opacity: 0; transform: translateY(18px) scale(.965); } to { opacity: 1; transform: none; } }
.inspection-heading { flex-shrink: 0; padding: 18px 32px 12px; border-bottom: 1px solid #eef0f2; }
.inspection-kicker { color: var(--accent); }
.inspection-heading h2 { margin: 8px 0 0; width: auto; color: var(--ink); font-size: 26px; line-height: 1.1; letter-spacing: -.8px; font-weight: 790; }
.inspection-close { position: absolute; top: 20px; right: 30px; color: #7d7d82; font-size: 10px; cursor: pointer; }
.inspection-content { min-height: 0; flex: 1; overflow: hidden; padding: 11px 32px 9px; }
.inspection-card.inspect-comparison .inspection-content { padding-bottom: 16px; }
.inspection-meta { flex-shrink: 0; padding: 9px 32px; border-top: 1px solid #eef0f2; color: #7d7d82; font-size: 9px; letter-spacing: .5px; }
.claim-foot { position: absolute; left: 48px; bottom: 17px; color: #a0a5aa; font-size: 8.5px; letter-spacing: .82px; }
.eval-claim-cards.has-inspection { overflow: visible; }
.inspection-layer:focus { outline: none; }
.inspection-close:focus-visible, .inspection-content:focus-visible { outline: 2px solid var(--accent); outline-offset: -3px; }
@media (prefers-reduced-motion: reduce) {
  .claim-header, .evidence-hand, .evidence-card { transition: none; }
  .inspection-card { animation: none; }
}
</style>
