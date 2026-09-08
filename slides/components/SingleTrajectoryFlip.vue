<script setup lang="ts">
import { onUnmounted, ref } from "vue"
import { useTalkSteps } from '../composables/useTalkSteps'

const emit = defineEmits<{ insight: [earned: boolean] }>()

const isFlipped = ref(false)
const isCondensed = ref(false)
const isClosing = ref(false)
let closeTimer: ReturnType<typeof setTimeout> | undefined
onUnmounted(() => clearTimeout(closeTimer))
const reversePage = ref(0)
const reversePageCount = 3
const handoffClick = ref(0)
const handoffClickCount = 4

const openFlip = () => {
  clearTimeout(closeTimer)
  isFlipped.value = true
  isClosing.value = false
  reversePage.value = 0
  handoffClick.value = 0
}

const condenseCard = () => {
  isClosing.value = true
  clearTimeout(closeTimer)
  closeTimer = setTimeout(() => {
    isFlipped.value = false
    isClosing.value = false
    isCondensed.value = true
    emit('insight', true)
  }, 360)
}

const advanceReversePage = () => {
  if (reversePage.value === 2) {
    if (handoffClick.value < handoffClickCount) {
      handoffClick.value += 1
    }
    return
  }

  if (reversePage.value < reversePageCount - 1) {
    reversePage.value += 1
    handoffClick.value = 0
    return
  }

  condenseCard()
}

const goToReversePage = (page: number) => {
  reversePage.value = page
  handoffClick.value = 0
}

const resetInitial = (event?: MouseEvent) => {
  if (event) event.stopPropagation()
  isClosing.value = false
  isFlipped.value = false
  isCondensed.value = false
  emit('insight', false)
  reversePage.value = 0
  handoffClick.value = 0
}
useTalkSteps(14, step => {
  clearTimeout(closeTimer)
  isClosing.value = false
  isFlipped.value = step >= 3 && step <= 9
  isCondensed.value = step >= 10
  reversePage.value = step <= 3 ? 0 : step === 4 ? 1 : 2
  handoffClick.value = Math.max(0, Math.min(4, step - 5))
  emit('insight', isCondensed.value)
})
</script>

<template>
  <div
    class="failure-mode failure-mode-trajectory trajectory-flip-card"
    :class="{ 'is-condensed-mode': isCondensed }"
    @click="openFlip"
  >
    <template v-if="!isCondensed">
      <div class="failure-mode-head">
        <span class="failure-mode-number mono">02</span>
        <span class="failure-mode-label">SINGLE AGENT</span>
        <span class="trajectory-flip-icon" title="Click to flip"><i class="i-carbon:rotate-360"></i></span>
      </div>
      <div class="trajectory-mini-visual" aria-label="A single agent searches inside a history-shaped basin">
        <div class="trajectory-mini-orbit"></div>
        <div class="trajectory-mini-line"><i></i><i></i><i class="current"></i><i></i><i></i></div>
        <div class="trajectory-mini-star">★ <small>better idea</small></div>
        <div class="trajectory-mini-caption mono">same basin</div>
      </div>
      <p class="failure-mode-explanation trajectory-peer-problems"><span>History shapes search</span><span>Errors can persist</span></p>
    </template>

    <template v-else>
      <div class="failure-mode-head">
        <span class="failure-mode-number mono">02</span>
        <span class="failure-mode-label">SINGLE AGENT</span>
        <button class="trajectory-check-badge" title="Click to reset" @click.stop="resetInitial">
          <span>✓</span>
        </button>
      </div>
      <div class="trajectory-condensed-visual">
        <div class="trajectory-condensed-line"><span>last frame</span><i></i><span>next move</span></div>
        <div class="trajectory-condensed-tags"><span>history-shaped</span><span>single path</span></div>
      </div>
      <p class="failure-mode-explanation">Fresh reasoning. Audited evidence.</p>
      <div class="failure-mode-takeaway trajectory-condensed-takeaway"><span>✓</span><strong>Reopen search.</strong></div>
      <div class="failure-mode-takeaway trajectory-condensed-takeaway"><span>✓</span><strong>Check the science.</strong></div>
    </template>
  </div>

  <div
    v-if="isFlipped"
    class="trajectory-card-back-overlay"
    :class="{ 'is-closing': isClosing }"
    @click="advanceReversePage"
  >
    <div class="trajectory-card-back-inner" :class="{ 'inner-closing': isClosing }">
      <div class="trajectory-card-back-header" @click.stop>
        <div class="visual-kicker blue trajectory-card-back-kicker">
          <span class="trajectory-card-back-tag mono"><i class="i-carbon:rotate-360"></i> CARD 02 · REVERSE</span>
          <span class="trajectory-kicker-sep">/</span>
          <span>SINGLE AGENT</span>
        </div>
        <div class="trajectory-reverse-tabs mono" role="tablist" aria-label="Card 02 reverse pages">
          <button
            class="trajectory-reverse-tab"
            :class="{ 'is-active': reversePage === 0 }"
            role="tab"
            :aria-selected="reversePage === 0"
            @click.stop="goToReversePage(0)"
          >
            <span>01</span><b>SEARCH</b>
          </button>
          <button
            class="trajectory-reverse-tab"
            :class="{ 'is-active': reversePage === 1 }"
            role="tab"
            :aria-selected="reversePage === 1"
            @click.stop="goToReversePage(1)"
          >
            <span>02</span><b>VALIDITY</b>
          </button>
          <button
            class="trajectory-reverse-tab"
            :class="{ 'is-active': reversePage === 2 }"
            role="tab"
            :aria-selected="reversePage === 2"
            @click.stop="goToReversePage(2)"
          >
            <span>03</span><b>HANDOFF</b>
          </button>
        </div>
        <div class="trajectory-back-actions">
          <button class="trajectory-reset-btn mono" title="Reset to initial problem" @click="resetInitial">
            <i class="i-carbon:undo"></i>
            <span>RESET</span>
          </button>
          <button class="trajectory-condense-btn mono" @click="condenseCard">
            <span class="trajectory-check-mark">✓</span>
            <span>CONDENSE</span>
            <span class="i-carbon:minimize"></span>
          </button>
        </div>
      </div>

      <div class="trajectory-reverse-page" :key="reversePage">
        <template v-if="reversePage === 0">
          <div class="trajectory-back-claim">
            <span>History shapes <strong>search</strong></span>
          </div>

          <div class="trajectory-back-grid">
            <div class="trajectory-back-column codex-back-column">
              <div class="trajectory-back-column-kicker mono">CODEX</div>
              <h2>Local refinement</h2>
              <div class="trajectory-back-visual codex-back-visual">
                <div class="back-basin-orbit"></div>
                <div class="back-codex-line"></div>
                <div class="back-codex-node back-node-start">pointwise<small>FM</small></div>
                <div class="back-codex-node back-node-core">pairwise<small>FM</small></div>
                <div class="back-codex-node back-node-detail back-node-rank">rank</div>
                <div class="back-codex-node back-node-detail back-node-lr">lr</div>
                <div class="back-codex-node back-node-detail back-node-sampling">sampling</div>
                <div class="back-codex-node back-node-detail back-node-negatives">negatives</div>
                <div class="back-visual-label mono">ONE BASIN</div>
              </div>
              <p class="trajectory-back-copy">Tunes details within the same approach.</p>
            </div>

          <div class="trajectory-back-column gemini-back-column">
            <div class="trajectory-back-column-kicker mono">GEMINI</div>
            <h2>Mechanism pivots</h2>
            <div class="trajectory-back-visual gemini-back-visual">
            <svg class="gemini-back-connections" viewBox="0 0 424 184" preserveAspectRatio="none" aria-hidden="true">
              <line x1="55" y1="108" x2="78" y2="72"></line>
              <line x1="176" y1="72" x2="174" y2="110"></line>
              <line x1="226" y1="110" x2="252" y2="70"></line>
              <line x1="317" y1="70" x2="306" y2="111"></line>
            </svg>
            <div class="back-pivot-node back-pivot-node-1">FM</div>
            <div class="back-pivot-node back-pivot-node-2">8-field<br>representation</div>
            <div class="back-pivot-node back-pivot-node-3">BPR<br>loss</div>
                <div class="back-pivot-node back-pivot-node-4">DeepFM</div>
                <div class="back-pivot-node back-pivot-node-5">MT-DeepFM<br>+ EMA</div>
                <div class="back-visual-label mono">CHANGING MECHANISMS</div>
              </div>
              <p class="trajectory-back-copy">Switches approaches before sustained tuning.</p>
            </div>
          </div>

          <div class="trajectory-back-takeaway"><strong>New ideas can still inherit earlier assumptions.</strong><span>Two observed runs. Descriptive, not causal.</span></div>
        </template>

        <template v-else-if="reversePage === 1">
          <div class="trajectory-validity-page">
            <div class="trajectory-validity-claim">
              <span class="trajectory-validity-setup">The experiment runs.</span>
              <strong>The conclusion may still be wrong.</strong>
            </div>
            <p class="trajectory-validity-lead">Execution alone cannot tell you whether the science is sound.</p>
            <div class="trajectory-validity-evidence-label mono">REAL GEMINI EXPERIMENTS · ERRORS FOUND BY INDEPENDENT AUDIT</div>

            <div class="single-agent-mistake-cases">
              <div class="single-agent-mistake-case">
                <div class="single-agent-mistake-case-kicker mono">BPR OBJECTIVE</div>
                <h3 class="trajectory-validity-error">Wrong objective</h3>
                <div class="single-agent-mistake-case-row"><span>CLAIM</span><strong>within-user BPR</strong></div>
                <div class="single-agent-mistake-case-row audit-finding"><span>AUDIT</span><strong>cross-user pairing</strong></div>
                <div class="single-agent-mistake-case-note">The code does not test the claimed mechanism.</div>
              </div>
              <div class="single-agent-mistake-case">
                <div class="single-agent-mistake-case-kicker mono">TARGET STATISTICS</div>
                <h3 class="trajectory-validity-error">Leaked labels</h3>
                <div class="single-agent-mistake-case-row"><span>CLAIM</span><strong>dense target statistics</strong></div>
                <div class="single-agent-mistake-case-row audit-finding"><span>AUDIT</span><strong>self / future-label leakage</strong></div>
                <div class="single-agent-mistake-case-note">Apparent gains cannot establish a valid improvement.</div>
              </div>
            </div>

            <div class="trajectory-validity-scope">Source: FINAL_REPORT §5.4, audited branches. These findings do not invalidate every Gemini result.</div>
          </div>
        </template>

        <template v-else>
          <div class="trajectory-handoff-page">
            <div class="trajectory-handoff-claim">
              <span><strong>Fresh reasoning.</strong> <strong class="handoff-review-title">Independent review.</strong></span>
            </div>

            <div class="cycle-map trajectory-handoff-cycle-map" aria-label="Four-click handoff sequence: world, Scientist, evidence, and META return an updated world to a fresh Scientist">
              <svg class="cycle-map-lines" viewBox="0 0 1000 300" preserveAspectRatio="none" aria-hidden="true">
                <defs>
                  <marker id="trajectory-cycle-arrow-neutral" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#c8d0d9" /></marker>
                  <marker id="trajectory-cycle-arrow-blue" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#38bdf8" /></marker>
                  <marker id="trajectory-cycle-arrow-orange" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#ff873f" /></marker>
                  <marker id="trajectory-cycle-arrow-purple" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#a66cff" /></marker>
                  <marker id="trajectory-cycle-arrow-rose" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#ff5c78" /></marker>
                </defs>
                <path d="M126 146 C210 146 235 58 318 58" fill="none" stroke="#cfd6de" stroke-width="2" marker-end="url(#trajectory-cycle-arrow-neutral)" />
                <path d="M382 58 C480 58 510 146 604 146" fill="none" stroke="#cfd6de" stroke-width="2" marker-end="url(#trajectory-cycle-arrow-neutral)" />
                <path d="M674 146 C760 146 790 58 872 58" fill="none" stroke="#cfd6de" stroke-width="2" marker-end="url(#trajectory-cycle-arrow-neutral)" />
                <path d="M904 93 C956 120 930 222 720 236 C470 250 185 234 128 174" fill="none" stroke="#ff5c78" stroke-opacity=".2" stroke-width="2" marker-end="url(#trajectory-cycle-arrow-rose)" />
                <path class="cycle-path-progress cycle-path-blue" :class="{ 'trajectory-handoff-progress-visible': handoffClick >= 1 }" d="M126 146 C210 146 235 58 318 58" fill="none" stroke="#38bdf8" stroke-width="3" pathLength="1" marker-end="url(#trajectory-cycle-arrow-blue)" />
                <path class="cycle-path-progress cycle-path-orange" :class="{ 'trajectory-handoff-progress-visible': handoffClick >= 2 }" d="M382 58 C480 58 510 146 604 146" fill="none" stroke="#ff873f" stroke-width="3" pathLength="1" marker-end="url(#trajectory-cycle-arrow-orange)" />
                <path class="cycle-path-progress cycle-path-purple" :class="{ 'trajectory-handoff-progress-visible': handoffClick >= 3 }" d="M674 146 C760 146 790 58 872 58" fill="none" stroke="#a66cff" stroke-width="3" pathLength="1" marker-end="url(#trajectory-cycle-arrow-purple)" />
                <path class="cycle-path-progress cycle-path-rose" :class="{ 'trajectory-handoff-progress-visible': handoffClick >= 4 }" d="M904 93 C956 120 930 222 720 236 C470 250 185 234 128 174" fill="none" stroke="#ff5c78" stroke-width="3" pathLength="1" marker-end="url(#trajectory-cycle-arrow-rose)" />
              </svg>
              <div class="cycle-node cycle-world-node">
                <div class="cycle-node-visual cycle-world-visual" aria-hidden="true"><span class="cycle-world-ring world-ring-outer"></span><span class="cycle-world-ring world-ring-middle"></span><span class="cycle-world-ring world-ring-inner"></span><span class="cycle-world-core"></span><i class="cycle-particle particle-blue"></i><i class="cycle-particle particle-orange"></i><i class="cycle-particle particle-purple"></i></div>
                <strong>Research world</strong><small>Preserved evidence &amp; code</small>
              </div>
              <div class="cycle-node cycle-scientist-node" :class="{ 'trajectory-handoff-vclick-hidden': handoffClick < 1 }">
                <div class="cycle-node-visual cycle-scientist-visual"><span class="cycle-node-icon purple i-carbon:chemistry"></span></div>
                <strong>Fresh Scientist</strong><small>Revisit prior assumptions</small>
              </div>
              <div class="cycle-node cycle-evidence-node" :class="{ 'trajectory-handoff-vclick-hidden': handoffClick < 2 }">
                <div class="cycle-node-visual cycle-evidence-visual"><span class="evidence-line"><i class="blue-dot"></i>metrics</span><span class="evidence-line"><i class="orange-dot"></i>failures</span><span class="evidence-line"><i class="green-dot"></i>code</span></div>
                <strong>Experiment evidence</strong><small>Claims alongside code</small>
              </div>
              <div class="cycle-node cycle-meta-node" :class="{ 'trajectory-handoff-vclick-hidden': handoffClick < 3 }">
                <div class="cycle-node-visual cycle-meta-visual"><span>✓</span></div>
                <strong>Independent META</strong><small>Check claims against code</small>
              </div>
              <div class="cycle-loop-label" :class="{ 'trajectory-handoff-vclick-hidden': handoffClick < 4 }">
                <strong>Preserve evidence. Reopen reasoning.</strong><small>Updated world, fresh Scientist</small>
              </div>
            </div>

            <div class="cycle-explain trajectory-handoff-cycle-explain" :class="{ 'trajectory-handoff-vclick-hidden': handoffClick < 4 }">
              <div class="handoff-response handoff-response-search">
                <span class="handoff-response-label">01 / HISTORY-SHAPED SEARCH</span>
                <strong>A fresh Scientist revisits assumptions.</strong>
              </div>
              <div class="handoff-response handoff-response-validity">
                <span class="handoff-response-label">02 / SCIENTIFIC ERRORS</span>
                <strong>Independent review checks the science.</strong>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.trajectory-flip-card {
  cursor: pointer;
  position: relative;
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}

.trajectory-flip-card:hover {
  border-color: var(--blue);
  box-shadow: 0 16px 36px -4px rgba(14, 165, 233, .16), 0 6px 16px -2px rgba(15, 23, 42, .06);
  transform: translateY(-3px);
}

.trajectory-flip-icon,
.trajectory-check-badge {
  align-items: center;
  background: rgba(37, 99, 235, .08);
  border: 1px solid rgba(37, 99, 235, .25);
  border-radius: 50%;
  color: var(--blue);
  display: inline-flex;
  font-size: 10px;
  height: 18px;
  justify-content: center;
  margin-left: auto;
  transition: all .2s ease;
  width: 18px;
}

.trajectory-check-badge {
  background: var(--blue);
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
}

.trajectory-flip-card:hover .trajectory-flip-icon {
  background: var(--blue);
  color: #fff;
  transform: rotate(180deg);
}

.trajectory-mini-visual {
  box-sizing: border-box;
  height: 93px;
  margin: 12px 0 11px;
  overflow: hidden;
  position: relative;
}

.trajectory-mini-orbit {
  border: 1px solid rgba(56, 189, 248, .42);
  border-radius: 0 0 50% 50%;
  bottom: 17px;
  height: 58px;
  left: 6%;
  position: absolute;
  transform: perspective(80px) rotateX(4deg);
  width: 87%;
}

.trajectory-mini-line {
  align-items: center;
  bottom: 33px;
  display: flex;
  justify-content: space-between;
  left: 11%;
  position: absolute;
  transform: rotate(-4deg);
  width: 78%;
}

.trajectory-mini-line::before {
  background: #cfd2d6;
  content: '';
  height: 1px;
  left: 0;
  position: absolute;
  right: 0;
  top: 50%;
  z-index: 0;
}

.trajectory-mini-line i {
  background: #fff;
  border: 1px solid #bec3c8;
  border-radius: 50%;
  height: 9px;
  position: relative;
  width: 9px;
  z-index: 1;
}

.trajectory-mini-line i.current {
  background: var(--blue);
  border-color: var(--blue);
  height: 13px;
  width: 13px;
}

.trajectory-mini-star {
  color: var(--blue);
  font-size: 18px;
  line-height: 1;
  position: absolute;
  right: 9%;
  top: 3px;
}

.trajectory-mini-star small {
  color: var(--muted);
  font-family: 'Fira Code', 'SFMono-Regular', Consolas, monospace;
  font-size: 9px;
  letter-spacing: .15px;
  margin-left: 3px;
  vertical-align: 3px;
}

.trajectory-mini-caption {
  bottom: 4px;
  color: var(--muted);
  font-size: 10px;
  left: 0;
  letter-spacing: .5px;
  position: absolute;
  right: 0;
  text-align: center;
}

.trajectory-condensed-visual {
  background: rgba(239, 246, 255, .7);
  border: 1px dashed rgba(56, 189, 248, .38);
  border-radius: 9px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin: 10px 0 12px;
  padding: 10px 12px;
}

.trajectory-condensed-line {
  align-items: center;
  color: var(--muted);
  display: flex;
  font-family: 'Fira Code', monospace;
  font-size: 10px;
  justify-content: space-between;
}

.trajectory-condensed-line i {
  border-top: 1px solid var(--blue);
  flex: 0 0 44px;
}

.trajectory-condensed-tags {
  display: flex;
  gap: 6px;
}

.trajectory-condensed-tags span {
  background: #fff;
  border: 1px solid rgba(56, 189, 248, .3);
  border-radius: 6px;
  color: #167aa9;
  font-size: 9px;
  padding: 3px 7px;
}

.trajectory-condensed-takeaway {
  display: flex;
  gap: 6px;
}

.trajectory-condensed-takeaway > span {
  color: var(--blue);
  font-weight: 800;
}

/* Full-slide overlay, matching the interaction pattern used by FailureModeFlip01. */
.trajectory-card-back-overlay {
  animation: trajectoryOverlayFade .3s ease-out forwards;
  backdrop-filter: blur(14px);
  background: rgba(248, 250, 252, .96);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  height: 100%;
  left: 0;
  padding: 32px 48px 24px;
  perspective: 1200px;
  position: absolute;
  top: 0;
  width: 100%;
  z-index: 100;
  cursor: pointer;
}

.trajectory-card-back-overlay.is-closing { animation: trajectoryOverlayFadeOut .35s ease-in forwards; }

@keyframes trajectoryOverlayFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes trajectoryOverlayFadeOut { from { opacity: 1; } to { opacity: 0; } }

.trajectory-card-back-inner {
  animation: trajectoryCardFlipIn .42s cubic-bezier(.16, 1, .3, 1) forwards;
  cursor: default;
  display: flex;
  flex-direction: column;
  height: 100%;
  transform-style: preserve-3d;
}

.trajectory-card-back-inner.inner-closing { animation: trajectoryCardFlipOut .35s cubic-bezier(.7, 0, .84, 0) forwards; }

@keyframes trajectoryCardFlipIn {
  0% { opacity: 0; transform: perspective(1200px) rotateY(-85deg) scale(.9); }
  65% { transform: perspective(1200px) rotateY(6deg) scale(1.01); }
  100% { opacity: 1; transform: perspective(1200px) rotateY(0deg) scale(1); }
}

@keyframes trajectoryCardFlipOut {
  0% { opacity: 1; transform: perspective(1200px) rotateY(0deg) scale(1); }
  100% { opacity: 0; transform: perspective(1200px) rotateY(80deg) scale(.9); }
}

.trajectory-card-back-header {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 2px;
}

.trajectory-reverse-tabs {
  align-items: center;
  display: flex;
  gap: 10px;
  margin-left: auto;
  margin-right: 14px;
}

.trajectory-reverse-tab {
  align-items: baseline;
  background: transparent;
  border: 0;
  border-bottom: 1px solid transparent;
  color: var(--muted);
  cursor: pointer;
  display: inline-flex;
  font-family: inherit;
  font-size: 10px;
  gap: 5px;
  letter-spacing: .5px;
  padding: 4px 2px 5px;
  transition: color .15s ease, border-color .15s ease;
}

.trajectory-reverse-tab > span {
  color: #b4b7bd;
}

.trajectory-reverse-tab > b {
  font-weight: 500;
}

.trajectory-reverse-tab:hover,
.trajectory-reverse-tab.is-active {
  border-bottom-color: var(--blue);
  color: #167aa9;
}

.trajectory-reverse-tab.is-active > span {
  color: var(--blue);
}

.trajectory-reverse-page {
  cursor: pointer;
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
  animation: trajectoryReversePageIn .22s ease-out both;
}

@keyframes trajectoryReversePageIn {
  from { opacity: .35; transform: translateX(8px); }
  to { opacity: 1; transform: translateX(0); }
}

.trajectory-validity-page {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
}

.trajectory-validity-claim {
  color: var(--ink);
  display: flex;
  flex-direction: column;
  font-size: 31px;
  font-weight: 400;
  letter-spacing: -1px;
  line-height: 1.08;
  margin: 22px 0 7px;
}

.trajectory-validity-claim strong {
  color: var(--blue);
  font-weight: 500;
}

.trajectory-validity-claim span + span {
  color: var(--muted);
  font-size: 17px;
  letter-spacing: -.2px;
  margin-top: 5px;
}

.trajectory-handoff-page {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
}

.trajectory-handoff-claim {
  color: var(--ink);
  display: flex;
  flex-direction: column;
  font-size: 31px;
  font-weight: 400;
  letter-spacing: -1px;
  line-height: 1.08;
  margin: 22px 0 7px;
}

.trajectory-handoff-claim strong {
  color: var(--blue);
  font-weight: 500;
}

.trajectory-handoff-claim span + span {
  color: var(--muted);
  font-size: 17px;
  letter-spacing: -.2px;
  margin-top: 5px;
}

.trajectory-handoff-cycle-map {
  cursor: pointer;
  margin-top: 20px;
}

.trajectory-handoff-page .trajectory-handoff-claim strong { color: #167aa9; }
.trajectory-handoff-page .trajectory-handoff-claim .handoff-review-title { color: #7542be; }

.trajectory-handoff-page .cycle-node > strong {
  color: #20232b;
  font-family: inherit;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -.2px;
}

.trajectory-handoff-page .cycle-node > small {
  color: #454b55;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.35;
  margin-top: 6px;
  white-space: normal;
}

.trajectory-handoff-page .evidence-line {
  color: #454b55;
  font-family: inherit;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0;
}

.trajectory-handoff-page .cycle-loop-label > strong {
  color: #a82c48;
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0;
}

.trajectory-handoff-page .cycle-loop-label > small {
  color: #454b55;
  font-size: 13px;
  font-weight: 500;
}

.trajectory-handoff-page .trajectory-handoff-cycle-explain {
  gap: 32px;
  margin-top: 14px;
  padding-top: 16px;
}

.handoff-response { display: flex; flex-direction: column; gap: 8px; }
.handoff-response-label { font-size: 12px; font-weight: 600; letter-spacing: .5px; }
.handoff-response-search .handoff-response-label { color: #167aa9; }
.handoff-response-validity .handoff-response-label { color: #7542be; }
.handoff-response > strong { color: #20232b; font-size: 19px; font-weight: 500; line-height: 1.25; letter-spacing: -.3px; }

.trajectory-handoff-cycle-map .cycle-path-progress {
  opacity: 0 !important;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  transition: opacity .24s ease, stroke-dashoffset .72s cubic-bezier(.22, 1, .36, 1);
}

.trajectory-handoff-cycle-map .cycle-path-progress.trajectory-handoff-progress-visible {
  opacity: .9 !important;
  stroke-dashoffset: 0;
}

.trajectory-handoff-cycle-map .cycle-node,
.trajectory-handoff-cycle-map .cycle-loop-label,
.trajectory-handoff-cycle-explain {
  transition: opacity .52s ease, translate .52s cubic-bezier(.22, 1, .36, 1);
}

.trajectory-handoff-vclick-hidden {
  opacity: 0;
  pointer-events: none;
  translate: 0 14px;
}

.trajectory-handoff-cycle-explain.trajectory-handoff-vclick-hidden {
  opacity: 0;
  translate: 0 14px;
}

.trajectory-card-back-kicker {
  align-items: center;
  display: inline-flex;
  gap: 7px;
  margin-bottom: 0;
}

.trajectory-card-back-tag {
  background: rgba(37, 99, 235, .1);
  border: 1px solid rgba(37, 99, 235, .28);
  border-radius: 999px;
  color: #167aa9;
  display: inline-flex;
  font-size: 10px;
  font-weight: 700;
  gap: 4px;
  letter-spacing: .8px;
  padding: 2px 8px;
}

.trajectory-kicker-sep { color: #93c5fd; }

.trajectory-back-actions {
  align-items: center;
  display: flex;
  gap: 8px;
}

.trajectory-reset-btn,
.trajectory-condense-btn {
  align-items: center;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  font-size: 11px;
  gap: 5px;
  letter-spacing: .5px;
  padding: 4px 10px;
  transition: all .15s ease;
}

.trajectory-reset-btn { color: var(--muted); }
.trajectory-condense-btn { color: var(--body); gap: 6px; padding: 4px 11px; }
.trajectory-condense-btn .trajectory-check-mark { color: var(--blue); font-weight: 700; }
.trajectory-reset-btn:hover { background: #f1f5f9; color: var(--ink); }
.trajectory-condense-btn:hover { background: #eff6ff; border-color: var(--blue); color: var(--blue); }

.trajectory-back-claim {
  color: var(--ink);
  display: flex;
  flex-direction: column;
  font-size: 29px;
  font-weight: 400;
  letter-spacing: -1px;
  line-height: 1.1;
  margin-top: 24px;
}

.trajectory-back-claim strong { color: var(--blue); font-weight: 500; }
.trajectory-back-claim-shift { color: var(--muted); font-size: 18px; letter-spacing: -.25px; margin-top: 7px; }

.trajectory-back-grid {
  display: grid;
  gap: 36px;
  grid-template-columns: 1fr 1fr;
  margin-top: 25px;
}

.trajectory-back-column { min-width: 0; }
.codex-back-column { border-top: 2px solid var(--orange); }
.gemini-back-column { border-top: 2px solid var(--blue); }

.trajectory-back-column-kicker {
  font-size: 10px;
  letter-spacing: 1px;
  margin-top: 11px;
}

.codex-back-column .trajectory-back-column-kicker { color: #c15d22; }
.gemini-back-column .trajectory-back-column-kicker { color: #158ac0; }

.trajectory-back-column h2 {
  color: var(--ink);
  font-size: 25px;
  font-weight: 500;
  letter-spacing: -.7px;
  line-height: 1.05;
  margin: 7px 0 0;
}

.trajectory-back-visual {
  height: 184px;
  margin-top: 13px;
  overflow: hidden;
  position: relative;
}

.codex-back-visual {
  background: rgba(255, 247, 237, .45);
  border-left: 1px solid rgba(255, 135, 63, .26);
  border-right: 1px solid rgba(255, 135, 63, .26);
}

.back-basin-orbit {
  border: 1px solid rgba(255, 135, 63, .45);
  border-radius: 50%;
  height: 105px;
  left: 7%;
  position: absolute;
  top: 27px;
  transform: rotate(-6deg);
  width: 86%;
}

.back-basin-orbit::after {
  border: 1px dashed rgba(255, 135, 63, .3);
  border-radius: 50%;
  content: '';
  inset: 13px 22px;
  position: absolute;
  transform: rotate(14deg);
}

.back-codex-line {
  border-top: 1px solid rgba(255, 135, 63, .55);
  left: 5%;
  position: absolute;
  right: 5%;
  top: 96px;
}

.back-codex-node {
  align-items: center;
  background: rgba(255, 255, 255, .94);
  border: 1px solid rgba(255, 135, 63, .7);
  border-radius: 50%;
  box-sizing: border-box;
  color: #a84e1b;
  display: flex;
  flex-direction: column;
  font-size: 11px;
  height: 48px;
  justify-content: center;
  position: absolute;
  text-align: center;
  width: 48px;
  z-index: 1;
}

.back-codex-node small {
  color: var(--muted);
  font-family: 'Fira Code', monospace;
  font-size: 9px;
}

.back-node-start { height: 64px; left: 0; top: 68px; width: 64px; }
.back-node-core { background: #fff8f1; border-color: var(--orange); box-shadow: 0 0 0 5px rgba(255, 135, 63, .1); height: 68px; left: 19%; top: 61px; width: 68px; }
.back-node-rank { left: 40%; top: 39px; }
.back-node-lr { left: 54%; top: 78px; }
.back-node-sampling { left: 67%; top: 40px; width: 56px; }
.back-node-negatives { left: 81%; top: 78px; width: 56px; }

.back-visual-label {
  bottom: 9px;
  color: #c15d22;
  font-size: 9px;
  left: 0;
  letter-spacing: .75px;
  position: absolute;
  right: 0;
  text-align: center;
}

.gemini-back-visual {
  border-left: 1px solid rgba(56, 189, 248, .25);
  border-right: 1px solid rgba(56, 189, 248, .25);
}

.gemini-back-connections {
  height: 100%;
  left: 0;
  overflow: visible;
  pointer-events: none;
  position: absolute;
  shape-rendering: geometricPrecision;
  top: 0;
  width: 100%;
  z-index: 1;
}

.gemini-back-connections line {
  fill: none;
  stroke: rgba(56, 189, 248, .68);
  stroke-linecap: round;
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}

.back-pivot-node {
  align-items: center;
  background: #fff;
  border: 1px solid rgba(56, 189, 248, .72);
  border-radius: 9px;
  box-sizing: border-box;
  color: #167aa9;
  display: flex;
  font-size: 11px;
  justify-content: center;
  line-height: 1.1;
  min-height: 47px;
  padding: 7px 9px;
  position: absolute;
  text-align: center;
  z-index: 2;
}

.back-pivot-node-1 { left: 2%; top: 107px; width: 64px; }
.back-pivot-node-2 { left: 18%; top: 28px; width: 106px; }
.back-pivot-node-3 { left: 41%; top: 107px; width: 72px; }
.back-pivot-node-4 { left: 59%; top: 27px; width: 74px; }
.back-pivot-node-5 { left: 72%; top: 107px; width: 100px; }

.gemini-back-column .back-visual-label {
  bottom: 4px;
  color: #158ac0;
  z-index: 3;
}

.trajectory-back-copy {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.3;
  margin: 10px 0 0;
  max-width: 94%;
}

.trajectory-back-takeaway {
  align-items: baseline;
  border-top: 1px solid var(--line);
  display: flex;
  gap: 12px;
  margin-top: 22px;
  padding-top: 12px;
}

.trajectory-back-takeaway strong {
  color: var(--ink);
  font-size: 17px;
  font-weight: 600;
}

.trajectory-back-takeaway span { color: var(--muted); font-size: 10px; }

.trajectory-back-claim,
.trajectory-validity-claim,
.trajectory-handoff-claim {
  font-size: 32px;
  font-weight: 500;
  margin-top: 24px;
}

.trajectory-back-grid { margin-top: 32px; }
.trajectory-back-takeaway { margin-top: auto; justify-content: space-between; }
.trajectory-back-takeaway strong { font-weight: 500; }

.trajectory-validity-page .trajectory-validity-claim {
  gap: 8px;
  margin-bottom: 0;
}
.trajectory-validity-claim .trajectory-validity-setup {
  color: var(--ink);
  font-size: 25px;
  letter-spacing: -.5px;
}
.trajectory-validity-page .trajectory-validity-claim strong {
  color: #c43b59;
  font-size: 40px;
  letter-spacing: -1.3px;
  line-height: 1.1;
}
.trajectory-validity-page .trajectory-validity-lead {
  color: var(--body);
  font-size: 17px;
  line-height: 1.35;
  margin: 14px 0 0;
}
.trajectory-validity-evidence-label {
  color: var(--muted);
  font-size: 10px;
  letter-spacing: .8px;
  margin-top: 26px;
}
.trajectory-validity-page .single-agent-mistake-cases { gap: 32px; margin-top: 10px; }
.trajectory-validity-page .single-agent-mistake-case {
  background: none;
  border-left: 0;
  border-top: 2px solid var(--rose);
  box-shadow: none;
  min-height: 175px;
  padding: 16px 0;
}
.trajectory-validity-page .single-agent-mistake-case:nth-child(2) { border-top-color: var(--rose); }
.trajectory-validity-page .single-agent-mistake-case-kicker { color: var(--muted); }
.trajectory-validity-page .trajectory-validity-error {
  color: var(--ink);
  font-size: 23px;
  font-weight: 500;
  letter-spacing: -.5px;
  line-height: 1.2;
  margin: 10px 0 4px;
}
.trajectory-validity-page .single-agent-mistake-case-row { grid-template-columns: 60px 1fr; padding-top: 10px; margin-top: 12px; }
.trajectory-validity-page .single-agent-mistake-case-row strong { font-size: 18px; font-weight: 500; }
.trajectory-validity-page .audit-finding strong,
.trajectory-validity-page .audit-finding > span { color: #c43b59; }
.trajectory-validity-page .single-agent-mistake-case-note { margin-top: 14px; font-size: 14px; }
.trajectory-validity-scope { color: var(--muted); font-size: 10px; margin-top: auto; padding-top: 12px; }
</style>
