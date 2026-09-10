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
    if (handoffClick.value < handoffClickCount) handoffClick.value += 1
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

      <div class="trajectory-mini-visual" aria-label="A single long-running trajectory keeps moving in the same direction">
        <div class="trajectory-mini-track"></div>
        <div class="trajectory-mini-step step-1"></div>
        <div class="trajectory-mini-step step-2"></div>
        <div class="trajectory-mini-step step-3 current"></div>
        <div class="trajectory-mini-step step-4"></div>
        <div class="trajectory-mini-arrow">→</div>
        <div class="trajectory-mini-star">★ <small>different idea</small></div>
        <div class="trajectory-mini-caption mono">trajectory momentum</div>
      </div>

      <p class="failure-mode-explanation trajectory-peer-problems">
        <span>Trajectory momentum</span>
        <span>Errors can persist</span>
      </p>
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
        <div class="trajectory-condensed-line"><span>momentum</span><i></i><span>fresh search</span></div>
        <div class="trajectory-condensed-tags"><span>trajectory momentum</span><span>fresh context</span></div>
      </div>
      <p class="failure-mode-explanation">Fresh reasoning. Audited evidence.</p>
      <div class="failure-mode-takeaway trajectory-condensed-takeaway"><span>✓</span><strong>Reset momentum.</strong></div>
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
          <button class="trajectory-reverse-tab" :class="{ 'is-active': reversePage === 0 }" role="tab" :aria-selected="reversePage === 0" @click.stop="goToReversePage(0)">
            <span>01</span><b>MOMENTUM</b>
          </button>
          <button class="trajectory-reverse-tab" :class="{ 'is-active': reversePage === 1 }" role="tab" :aria-selected="reversePage === 1" @click.stop="goToReversePage(1)">
            <span>02</span><b>VALIDITY</b>
          </button>
          <button class="trajectory-reverse-tab" :class="{ 'is-active': reversePage === 2 }" role="tab" :aria-selected="reversePage === 2" @click.stop="goToReversePage(2)">
            <span>03</span><b>HANDOFF</b>
          </button>
        </div>
        <div class="trajectory-back-actions">
          <button class="trajectory-reset-btn mono" title="Reset to initial problem" @click="resetInitial">
            <i class="i-carbon:undo"></i><span>RESET</span>
          </button>
          <button class="trajectory-condense-btn mono" @click="condenseCard">
            <span class="trajectory-check-mark">✓</span><span>CONDENSE</span><span class="i-carbon:minimize"></span>
          </button>
        </div>
      </div>

      <div class="trajectory-reverse-page" :key="reversePage">
        <template v-if="reversePage === 0">
          <div class="trajectory-back-claim">
            <span>Long trajectories accumulate <strong>trajectory momentum.</strong></span>
          </div>

          <div class="momentum-analogy" aria-label="Tool-loop analogy for research momentum">
            <div class="momentum-analogy-row">
              <span class="momentum-analogy-label mono">ACTION LEVEL</span>
              <div class="momentum-chain mono"><span>tool</span><b>→</b><span>tool</span><b>→</b><span>tool</span><b>→</b><span>tool</span></div>
            </div>
            <div class="momentum-analogy-divider" aria-hidden="true"></div>
            <div class="momentum-analogy-row">
              <span class="momentum-analogy-label mono">RESEARCH LEVEL</span>
              <div class="momentum-chain mono research-chain">
                <span class="chain-pill chain-tune">tune → tune</span>
                <span class="chain-or">or</span>
                <span class="chain-pill chain-pivot">pivot → pivot</span>
              </div>
            </div>
            <div class="momentum-analogy-divider" aria-hidden="true"></div>
            <div class="momentum-analogy-summary">
              <span class="summary-tag mono">TRAJECTORY INERTIA</span>
              <strong>Same momentum, at a longer horizon.</strong>
            </div>
          </div>

          <div class="trajectory-back-grid">
            <div class="trajectory-back-column codex-back-column">
              <div class="trajectory-back-column-kicker mono">CODEX · INERTIAL EXPLOITATION</div>
              <h2>Hyper-tuning momentum</h2>
              <div class="trajectory-back-visual codex-back-visual">
                <div class="back-momentum-band"></div>
                <div class="back-codex-line"></div>
                <div class="back-codex-node back-node-start">pointwise<small>FM</small></div>
                <div class="back-codex-node back-node-core">pairwise<small>FM</small></div>
                <div class="back-codex-node back-node-detail back-node-rank">rank</div>
                <div class="back-codex-node back-node-detail back-node-lr">lr</div>
                <div class="back-codex-node back-node-detail back-node-sampling">sampling</div>
                <div class="back-codex-node back-node-detail back-node-negatives">negatives</div>
                <div class="back-visual-label mono">STUCK IN LOCAL PARAMETER BASIN</div>
              </div>
              <p class="trajectory-back-copy">Endless parameter tuning without questioning whether the representation has hit an information bottleneck.</p>
            </div>

            <div class="trajectory-back-column gemini-back-column">
              <div class="trajectory-back-column-kicker mono">GEMINI · INERTIAL EXPLORATION</div>
              <h2>Pivoting momentum</h2>
              <div class="trajectory-back-visual gemini-back-visual">
                <svg class="gemini-back-connections" viewBox="0 0 424 168" preserveAspectRatio="none" aria-hidden="true">
                  <line x1="55" y1="96" x2="78" y2="58"></line>
                  <line x1="176" y1="58" x2="174" y2="98"></line>
                  <line x1="226" y1="98" x2="252" y2="58"></line>
                  <line x1="317" y1="58" x2="306" y2="98"></line>
                </svg>
                <div class="back-pivot-node back-pivot-node-1">FM</div>
                <div class="back-pivot-node back-pivot-node-2">8-field<br>representation</div>
                <div class="back-pivot-node back-pivot-node-3">BPR<br>loss</div>
                <div class="back-pivot-node back-pivot-node-4">DeepFM</div>
                <div class="back-pivot-node back-pivot-node-5">MT-DeepFM<br>+ EMA</div>
                <div class="back-visual-label mono">ERRATIC DRIFT WITHOUT ROOT DIAGNOSIS</div>
              </div>
              <p class="trajectory-back-copy">Constant mechanism pivots without diagnosis: hopping between architectures is trial-and-error momentum, not scientific discovery.</p>
            </div>
          </div>

          <div class="trajectory-scientist-takeaway">
            <span class="takeaway-icon i-carbon:idea"></span>
            <div class="takeaway-body">
              <strong class="takeaway-headline">A true scientist will neither blindly dive nor blindly pivot:</strong>
              <span class="takeaway-text">They diagnose the bottleneck from audited evidence first, and adapt their research method accordingly.</span>
            </div>
          </div>
        </template>

        <template v-else-if="reversePage === 1">
          <div class="trajectory-validity-page">
            <div class="trajectory-validity-claim">
              <span class="trajectory-validity-setup">The experiment runs.</span>
              <strong>The conclusion may still be wrong.</strong>
            </div>
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
          </div>
        </template>

        <template v-else>
          <div class="trajectory-handoff-page">
            <div class="trajectory-handoff-claim">
              <span><strong>Fresh reasoning.</strong> <strong class="handoff-review-title">Independent review.</strong></span>
            </div>

            <div class="cycle-map trajectory-handoff-cycle-map" aria-label="Handoff sequence from task to fresh Scientist, evidence, META review, and updated research world">
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

              <div class="cycle-node cycle-world-node" :class="{ 'is-loop-returned': handoffClick >= 4 }">
                <div class="cycle-world-visual-stage" aria-hidden="true">
                  <div class="cycle-node-visual cycle-task-visual" :class="{ 'cycle-stage-hidden': handoffClick >= 4 }"><span class="cycle-node-icon blue i-carbon:document"></span></div>
                  <div class="cycle-node-visual cycle-world-visual" :class="{ 'cycle-stage-hidden': handoffClick < 4 }">
                    <span class="cycle-world-ring world-ring-outer"></span><span class="cycle-world-ring world-ring-middle"></span><span class="cycle-world-ring world-ring-inner"></span><span class="cycle-world-core"></span>
                    <i class="cycle-particle particle-blue"></i><i class="cycle-particle particle-orange"></i><i class="cycle-particle particle-purple"></i>
                  </div>
                </div>
                <div class="cycle-node-text-stage">
                  <div class="cycle-node-text-inner cycle-task-text" :class="{ 'cycle-stage-hidden': handoffClick >= 4 }"><strong class="cycle-task-title mono">Task.md</strong><small>Initial problem &amp; constraints</small></div>
                  <div class="cycle-node-text-inner cycle-world-text" :class="{ 'cycle-stage-hidden': handoffClick < 4 }"><strong>Research world</strong><small>Preserved evidence &amp; code</small></div>
                </div>
              </div>

              <div class="cycle-node cycle-scientist-node" :class="{ 'trajectory-handoff-vclick-hidden': handoffClick < 1 }">
                <div class="cycle-node-visual cycle-scientist-visual"><span class="cycle-node-icon purple i-carbon:chemistry"></span></div>
                <strong>Fresh Scientist</strong><small>Break trajectory momentum</small>
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
                <strong>Preserve experience. Reset momentum.</strong><small>Updated world, fresh Scientist</small>
              </div>
            </div>

            <div class="cycle-explain trajectory-handoff-cycle-explain" :class="{ 'trajectory-handoff-vclick-hidden': handoffClick < 4 }">
              <div class="handoff-response handoff-response-search">
                <span class="handoff-response-label">01 / TRAJECTORY MOMENTUM</span>
                <strong>A fresh Scientist reopens the search.</strong>
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
.trajectory-check-badge { background: var(--blue); border: none; color: #fff; cursor: pointer; font-size: 11px; font-weight: 800; }
.trajectory-flip-card:hover .trajectory-flip-icon { background: var(--blue); color: #fff; transform: rotate(180deg); }

.trajectory-mini-visual { box-sizing: border-box; height: 93px; margin: 12px 0 11px; overflow: hidden; position: relative; }
.trajectory-mini-track { border-top: 1px solid rgba(56, 189, 248, .55); left: 10%; position: absolute; right: 13%; top: 50px; transform: rotate(-5deg); }
.trajectory-mini-step { background: #fff; border: 1px solid #b8d8e8; border-radius: 50%; height: 10px; position: absolute; top: 45px; width: 10px; }
.trajectory-mini-step.current { background: var(--blue); border-color: var(--blue); box-shadow: 0 0 0 5px rgba(56, 189, 248, .14); height: 14px; top: 43px; width: 14px; }
.step-1 { left: 12%; } .step-2 { left: 31%; } .step-3 { left: 50%; } .step-4 { left: 69%; }
.trajectory-mini-arrow { color: var(--blue); font-size: 22px; font-weight: 700; position: absolute; right: 8%; top: 35px; }
.trajectory-mini-star { color: var(--blue); font-size: 18px; line-height: 1; position: absolute; right: 6%; top: 4px; }
.trajectory-mini-star small { color: var(--muted); font-family: var(--deck-mono); font-size: 9px; letter-spacing: .15px; margin-left: 3px; vertical-align: 3px; }
.trajectory-mini-caption { bottom: 4px; color: var(--muted); font-size: 10px; left: 0; letter-spacing: .5px; position: absolute; right: 0; text-align: center; }

.trajectory-condensed-visual { background: rgba(239, 246, 255, .7); border: 1px dashed rgba(56, 189, 248, .38); border-radius: 9px; box-sizing: border-box; display: flex; flex-direction: column; gap: 9px; margin: 10px 0 12px; padding: 10px 12px; }
.trajectory-condensed-line { align-items: center; color: var(--muted); display: flex; font-family: var(--deck-mono); font-size: 10px; justify-content: space-between; }
.trajectory-condensed-line i { border-top: 1px solid var(--blue); flex: 0 0 44px; }
.trajectory-condensed-tags { display: flex; gap: 6px; }
.trajectory-condensed-tags span { background: #fff; border: 1px solid rgba(56, 189, 248, .3); border-radius: 6px; color: #167aa9; font-size: 9px; padding: 3px 7px; }
.trajectory-condensed-takeaway { display: flex; gap: 6px; }
.trajectory-condensed-takeaway > span { color: var(--blue); font-weight: 800; }

.trajectory-card-back-overlay { animation: trajectoryOverlayFade .3s ease-out forwards; backdrop-filter: blur(14px); background: rgba(248, 250, 252, .96); box-sizing: border-box; cursor: pointer; display: flex; flex-direction: column; height: 100%; left: 0; padding: 32px 48px 24px; perspective: 1200px; position: absolute; top: 0; width: 100%; z-index: 100; }
.trajectory-card-back-overlay.is-closing { animation: trajectoryOverlayFadeOut .35s ease-in forwards; }
@keyframes trajectoryOverlayFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes trajectoryOverlayFadeOut { from { opacity: 1; } to { opacity: 0; } }
.trajectory-card-back-inner { animation: trajectoryCardFlipIn .42s cubic-bezier(.16, 1, .3, 1) forwards; cursor: default; display: flex; flex-direction: column; height: 100%; transform-style: preserve-3d; }
.trajectory-card-back-inner.inner-closing { animation: trajectoryCardFlipOut .35s cubic-bezier(.7, 0, .84, 0) forwards; }
@keyframes trajectoryCardFlipIn { 0% { opacity: 0; transform: perspective(1200px) rotateY(-85deg) scale(.9); } 65% { transform: perspective(1200px) rotateY(6deg) scale(1.01); } 100% { opacity: 1; transform: perspective(1200px) rotateY(0deg) scale(1); } }
@keyframes trajectoryCardFlipOut { 0% { opacity: 1; transform: perspective(1200px) rotateY(0deg) scale(1); } 100% { opacity: 0; transform: perspective(1200px) rotateY(80deg) scale(.9); } }

.trajectory-card-back-header { align-items: center; display: flex; justify-content: space-between; margin-bottom: 2px; }
.trajectory-card-back-kicker { align-items: center; display: inline-flex; gap: 7px; margin-bottom: 0; }
.trajectory-card-back-tag { background: rgba(37, 99, 235, .1); border: 1px solid rgba(37, 99, 235, .28); border-radius: 999px; color: #167aa9; display: inline-flex; font-size: 10px; font-weight: 700; gap: 4px; letter-spacing: .8px; padding: 2px 8px; }
.trajectory-kicker-sep { color: #93c5fd; }
.trajectory-reverse-tabs { align-items: center; display: flex; gap: 10px; margin-left: auto; margin-right: 14px; }
.trajectory-reverse-tab { align-items: baseline; background: transparent; border: 0; border-bottom: 1px solid transparent; color: var(--muted); cursor: pointer; display: inline-flex; font-family: inherit; font-size: 10px; gap: 5px; letter-spacing: .5px; padding: 4px 2px 5px; transition: color .15s ease, border-color .15s ease; }
.trajectory-reverse-tab > span { color: #b4b7bd; }
.trajectory-reverse-tab > b { font-weight: 500; }
.trajectory-reverse-tab:hover, .trajectory-reverse-tab.is-active { border-bottom-color: var(--blue); color: #167aa9; }
.trajectory-reverse-tab.is-active > span { color: var(--blue); }
.trajectory-back-actions { align-items: center; display: flex; gap: 8px; }
.trajectory-reset-btn, .trajectory-condense-btn { align-items: center; background: #fff; border: 1px solid var(--line); border-radius: 8px; cursor: pointer; display: inline-flex; font-size: 11px; gap: 5px; letter-spacing: .5px; padding: 4px 10px; transition: all .15s ease; }
.trajectory-reset-btn { color: var(--muted); }
.trajectory-condense-btn { color: var(--body); gap: 6px; padding: 4px 11px; }
.trajectory-condense-btn .trajectory-check-mark { color: var(--blue); font-weight: 700; }
.trajectory-reset-btn:hover { background: #f1f5f9; color: var(--ink); }
.trajectory-condense-btn:hover { background: #eff6ff; border-color: var(--blue); color: var(--blue); }

.trajectory-reverse-page { animation: trajectoryReversePageIn .22s ease-out both; cursor: pointer; display: flex; flex: 1; flex-direction: column; min-height: 0; }
@keyframes trajectoryReversePageIn { from { opacity: .35; transform: translateX(8px); } to { opacity: 1; transform: translateX(0); } }
.trajectory-back-claim { color: var(--ink); display: flex; flex-direction: column; font-family: var(--deck-sans); font-size: 27px; font-weight: 500; letter-spacing: -1px; line-height: 1.1; margin-top: 10px; }
.trajectory-back-claim strong { color: var(--blue); font-weight: 700; }
.trajectory-validity-claim, .trajectory-handoff-claim { color: var(--ink); display: flex; flex-direction: column; font-family: var(--deck-sans); font-size: 32px; font-weight: 500; letter-spacing: -1.1px; line-height: 1.08; margin-top: 24px; }
.trajectory-handoff-claim strong { color: var(--blue); font-weight: 700; }
.trajectory-handoff-page .trajectory-handoff-claim .handoff-review-title { color: #7542be; }

.momentum-analogy { align-items: center; background: #fff; border: 1px solid #d8ebf8; border-radius: 12px; box-shadow: 0 4px 16px rgba(56, 189, 248, .07); display: flex; justify-content: space-between; margin-top: 10px; padding: 8px 18px; }
.momentum-analogy-row { align-items: center; display: flex; gap: 10px; }
.momentum-analogy-label { color: #8a9bab; font-size: 8.5px; font-weight: 800; letter-spacing: .8px; white-space: nowrap; }
.momentum-chain { align-items: center; color: #4c6474; display: flex; font-size: 10.5px; gap: 5px; min-width: 0; white-space: nowrap; }
.momentum-chain span { background: #f4f8fb; border: 1px solid #d9e8f2; border-radius: 999px; padding: 2px 7px; }
.momentum-chain b { color: #9ab8cb; font-size: 9px; }
.research-chain .chain-tune { background: #fff7ed; border-color: #fed7aa; color: #c2410c; font-weight: 600; }
.research-chain .chain-pivot { background: #eff6ff; border-color: #bfdbfe; color: #1d4ed8; font-weight: 600; }
.research-chain .chain-or { background: none; border: none; color: #94a3b8; font-size: 10px; font-style: italic; padding: 0 2px; }
.momentum-analogy-divider { background: #e2e8f0; height: 26px; width: 1px; }
.momentum-analogy-summary { display: flex; flex-direction: column; gap: 2px; }
.momentum-analogy-summary .summary-tag { color: #0284c7; font-size: 8px; font-weight: 800; letter-spacing: .8px; }
.momentum-analogy-summary strong { color: #167aa9; font-size: 13px; font-weight: 700; letter-spacing: -.2px; white-space: nowrap; }

.trajectory-back-grid { display: grid; gap: 24px; grid-template-columns: 1fr 1fr; margin-top: 12px; }
.trajectory-back-column { min-width: 0; }
.codex-back-column { border-top: 2px solid var(--orange); }
.gemini-back-column { border-top: 2px solid var(--blue); }
.trajectory-back-column-kicker { font-size: 9.5px; letter-spacing: 1px; margin-top: 8px; }
.codex-back-column .trajectory-back-column-kicker { color: #c15d22; }
.gemini-back-column .trajectory-back-column-kicker { color: #158ac0; }
.trajectory-back-column h2 { color: var(--ink); font-size: 21px; font-weight: 600; letter-spacing: -.6px; line-height: 1.1; margin: 4px 0 0; }
.trajectory-back-visual { height: 152px; margin-top: 8px; overflow: hidden; position: relative; }
.codex-back-visual { background: rgba(255, 247, 237, .45); border-left: 1px solid rgba(255, 135, 63, .26); border-right: 1px solid rgba(255, 135, 63, .26); }
.back-momentum-band { border: 1px solid rgba(255, 135, 63, .45); border-radius: 999px; height: 64px; left: 6%; position: absolute; top: 40px; transform: rotate(-4deg); width: 88%; }
.back-momentum-band::after { border-top: 1px dashed rgba(255, 135, 63, .35); content: ''; left: 34px; position: absolute; right: 34px; top: 31px; }
.back-codex-line { border-top: 1px solid rgba(255, 135, 63, .55); left: 5%; position: absolute; right: 5%; top: 78px; }
.back-codex-node { align-items: center; background: rgba(255,255,255,.94); border: 1px solid rgba(255,135,63,.7); border-radius: 50%; box-sizing: border-box; color: #a84e1b; display: flex; flex-direction: column; font-size: 10px; height: 42px; justify-content: center; position: absolute; text-align: center; width: 42px; z-index: 1; }
.back-codex-node small { color: var(--muted); font-family: var(--deck-mono); font-size: 8.5px; }
.back-node-start { height: 54px; left: 0; top: 52px; width: 54px; }
.back-node-core { background: #fff8f1; border-color: var(--orange); box-shadow: 0 0 0 4px rgba(255, 135, 63, .1); height: 58px; left: 19%; top: 47px; width: 58px; }
.back-node-rank { left: 40%; top: 29px; }
.back-node-lr { left: 54%; top: 65px; }
.back-node-sampling { left: 67%; top: 29px; width: 50px; }
.back-node-negatives { left: 81%; top: 65px; width: 50px; }
.back-visual-label { bottom: 5px; font-size: 8.5px; left: 0; letter-spacing: .75px; position: absolute; right: 0; text-align: center; }
.codex-back-column .back-visual-label { color: #c15d22; }
.gemini-back-visual { border-left: 1px solid rgba(56, 189, 248, .25); border-right: 1px solid rgba(56, 189, 248, .25); }
.gemini-back-connections { height: 100%; left: 0; overflow: visible; pointer-events: none; position: absolute; shape-rendering: geometricPrecision; top: 0; width: 100%; z-index: 1; }
.gemini-back-connections line { fill: none; stroke: rgba(56, 189, 248, .68); stroke-linecap: round; stroke-width: 1; vector-effect: non-scaling-stroke; }
.back-pivot-node { align-items: center; background: #fff; border: 1px solid rgba(56, 189, 248, .72); border-radius: 8px; box-sizing: border-box; color: #167aa9; display: flex; font-size: 10px; justify-content: center; line-height: 1.1; min-height: 40px; padding: 4px 7px; position: absolute; text-align: center; z-index: 2; }
.back-pivot-node-1 { left: 2%; top: 88px; width: 58px; }
.back-pivot-node-2 { left: 18%; top: 19px; width: 98px; }
.back-pivot-node-3 { left: 41%; top: 88px; width: 66px; }
.back-pivot-node-4 { left: 59%; top: 19px; width: 68px; }
.back-pivot-node-5 { left: 72%; top: 88px; width: 92px; }
.gemini-back-column .back-visual-label { bottom: 4px; color: #158ac0; z-index: 3; }
.trajectory-back-copy { color: var(--muted); font-size: 13px; line-height: 1.32; margin: 6px 0 0; max-width: 98%; }

.trajectory-scientist-takeaway { align-items: center; background: linear-gradient(90deg, #f0fdf4 0%, #f8fafc 100%); border: 1px solid #bbf7d0; border-radius: 10px; box-shadow: 0 2px 8px rgba(22, 128, 61, .06); display: flex; gap: 12px; margin-top: 11px; padding: 8px 16px; }
.trajectory-scientist-takeaway .takeaway-icon { color: #16a34a; flex-shrink: 0; font-size: 18px; }
.trajectory-scientist-takeaway .takeaway-body { align-items: baseline; display: flex; flex-wrap: wrap; gap: 8px; font-size: 12.5px; line-height: 1.35; }
.trajectory-scientist-takeaway .takeaway-headline { color: #15803d; font-size: 12.5px; font-weight: 750; letter-spacing: -.2px; }
.trajectory-scientist-takeaway .takeaway-text { color: #334155; font-weight: 500; }

.trajectory-validity-page, .trajectory-handoff-page { display: flex; flex: 1; flex-direction: column; min-height: 0; }
.trajectory-validity-page .trajectory-validity-claim { gap: 8px; margin-bottom: 0; }
.trajectory-validity-claim .trajectory-validity-setup { color: var(--ink); font-size: 25px; letter-spacing: -.5px; }
.trajectory-validity-page .trajectory-validity-claim strong { color: #c43b59; font-size: 40px; letter-spacing: -1.3px; line-height: 1.1; }
.trajectory-validity-evidence-label { color: var(--muted); font-size: 10px; letter-spacing: .8px; margin-top: 26px; }
.trajectory-validity-page .single-agent-mistake-cases { gap: 32px; margin-top: 10px; }
.trajectory-validity-page .single-agent-mistake-case { background: none; border-left: 0; border-top: 2px solid var(--rose); box-shadow: none; min-height: 175px; padding: 16px 0; }
.trajectory-validity-page .single-agent-mistake-case-kicker { color: var(--muted); }
.trajectory-validity-page .trajectory-validity-error { color: var(--ink); font-size: 23px; font-weight: 500; letter-spacing: -.5px; line-height: 1.2; margin: 10px 0 4px; }
.trajectory-validity-page .single-agent-mistake-case-row { grid-template-columns: 60px 1fr; padding-top: 10px; margin-top: 12px; }
.trajectory-validity-page .single-agent-mistake-case-row strong { font-size: 18px; font-weight: 500; }
.trajectory-validity-page .audit-finding strong, .trajectory-validity-page .audit-finding > span { color: #c43b59; }
.trajectory-validity-page .single-agent-mistake-case-note { margin-top: 14px; font-size: 14px; }

.trajectory-handoff-cycle-map { cursor: pointer; margin-top: 20px; }
.trajectory-handoff-page .cycle-node strong { color: #20232b; font-family: inherit; font-size: 16px; font-weight: 600; letter-spacing: -.2px; }
.trajectory-handoff-page .cycle-node small { color: #454b55; font-size: 13px; font-weight: 500; line-height: 1.35; margin-top: 6px; white-space: normal; }
.trajectory-handoff-page .cycle-world-visual-stage { height: 70px; margin: 0 auto 9px; position: relative; width: 70px; }
.trajectory-handoff-page .cycle-world-visual-stage .cycle-node-visual { height: 70px; inset: 0; margin: 0; position: absolute; transition: opacity .45s ease, transform .45s cubic-bezier(.22, 1, .36, 1); width: 70px; }
.trajectory-handoff-page .cycle-task-visual { background: #f0f7ff; border: 1px solid #bae0fd; border-radius: 50%; box-shadow: 0 4px 14px rgba(56, 189, 248, .12); }
.trajectory-handoff-page .cycle-task-visual .cycle-node-icon { color: #167aa9; font-size: 34px; }
.trajectory-handoff-page .cycle-node-text-stage { height: 48px; position: relative; width: 100%; }
.trajectory-handoff-page .cycle-node-text-inner { inset: 0; position: absolute; transition: opacity .45s ease, transform .45s cubic-bezier(.22, 1, .36, 1); }
.trajectory-handoff-page .cycle-task-title { color: #167aa9; font-family: var(--deck-mono, monospace); font-size: 15px; font-weight: 600; letter-spacing: -.3px; }
.trajectory-handoff-page .cycle-stage-hidden { opacity: 0 !important; pointer-events: none !important; transform: scale(.88) translateY(4px); }
.trajectory-handoff-page .cycle-node.is-loop-returned .cycle-world-visual { filter: drop-shadow(0 0 10px rgba(255, 92, 120, .28)); }
.trajectory-handoff-page .evidence-line { color: #454b55; font-family: inherit; font-size: 11px; font-weight: 500; letter-spacing: 0; }
.trajectory-handoff-page .cycle-loop-label > strong { color: #a82c48; font-family: inherit; font-size: 15px; font-weight: 600; letter-spacing: 0; }
.trajectory-handoff-page .cycle-loop-label > small { color: #454b55; font-size: 13px; font-weight: 500; }
.trajectory-handoff-page .trajectory-handoff-cycle-explain { gap: 32px; margin-top: 14px; padding-top: 16px; }
.handoff-response { display: flex; flex-direction: column; gap: 8px; }
.handoff-response-label { font-size: 12px; font-weight: 600; letter-spacing: .5px; }
.handoff-response-search .handoff-response-label { color: #167aa9; }
.handoff-response-validity .handoff-response-label { color: #7542be; }
.handoff-response > strong { color: #20232b; font-size: 19px; font-weight: 500; line-height: 1.25; letter-spacing: -.3px; }
.trajectory-handoff-cycle-map .cycle-path-progress { opacity: 0 !important; stroke-dasharray: 1; stroke-dashoffset: 1; transition: opacity .24s ease, stroke-dashoffset .72s cubic-bezier(.22, 1, .36, 1); }
.trajectory-handoff-cycle-map .cycle-path-progress.trajectory-handoff-progress-visible { opacity: .9 !important; stroke-dashoffset: 0; }
.trajectory-handoff-cycle-map .cycle-node, .trajectory-handoff-cycle-map .cycle-loop-label, .trajectory-handoff-cycle-explain { transition: opacity .52s ease, translate .52s cubic-bezier(.22, 1, .36, 1); }
.trajectory-handoff-vclick-hidden { opacity: 0; pointer-events: none; translate: 0 14px; }
.trajectory-handoff-cycle-explain.trajectory-handoff-vclick-hidden { opacity: 0; translate: 0 14px; }
</style>
