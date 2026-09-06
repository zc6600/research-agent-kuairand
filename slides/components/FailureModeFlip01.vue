<script setup lang="ts">
import { ref } from "vue"

const isFlipped = ref(false)
const isCondensed = ref(false)
const isClosing = ref(false)

const openFlip = () => {
  isFlipped.value = true
  isClosing.value = false
}

const condenseCard = () => {
  isClosing.value = true
  setTimeout(() => {
    isFlipped.value = false
    isClosing.value = false
    isCondensed.value = true
  }, 360)
}

const resetInitial = (e?: MouseEvent) => {
  if (e) e.stopPropagation()
  isClosing.value = false
  isFlipped.value = false
  isCondensed.value = false
}
</script>

<template>
  <div
    class="failure-mode failure-mode-closed failure-flip-card"
    :class="{ 'is-condensed-mode': isCondensed }"
    @click="openFlip"
  >
    <!-- Initial problem card -->
    <template v-if="!isCondensed">
      <div class="failure-mode-head">
        <span class="failure-mode-number mono">01</span>
        <span class="failure-mode-label">CLOSED-WORLD WORKFLOW</span>
        <span class="flip-icon-chip" title="Click to flip for solution"><i class="i-carbon:rotate-360"></i></span>
      </div>
      <div class="failure-mode-visual failure-graph" aria-label="A fixed workflow hits an error and stops">
        <div class="failure-graph-flow"><span>Observe</span><b>→</b><span>Hypothesize</span><b>→</b><span>Code</span><b>→</b><span>Evaluate</span></div>
        <div class="failure-graph-error"><span class="i-carbon:error-outline"></span><b>ERROR</b></div>
        <div class="failure-graph-dead"><span>↓</span><strong>dead end</strong></div>
      </div>
      <p class="failure-mode-explanation">Predefined tools and recovery paths cannot handle the unexpected.</p>
      <div class="failure-mode-takeaway"><strong>Unexpected problems require developer intervention.</strong></div>
    </template>

    <!-- Condensed solution card -->
    <template v-else>
      <div class="failure-mode-head">
        <span class="failure-mode-number mono">01</span>
        <span class="failure-mode-label">OPEN-WORLD RECOVERY</span>
        <button class="orange-check-badge mono" title="Click to reset" @click.stop="resetInitial">
          <span class="badge-check">✓</span>
          <span class="badge-reset"><i class="i-carbon:undo"></i></span>
        </button>
      </div>
      <div class="failure-mode-visual condensed-visual" aria-label="Open-world agent recovers from unexpected errors at runtime">
        <div class="condensed-flow">
          <span>Observe</span><b>→</b><span>Code</span><b>→</b><span class="flow-err">Error</span><b>→</b><span class="flow-rec">Recover</span>
        </div>
        <div class="condensed-tags">
          <span class="condensed-pill"><i class="i-carbon:terminal"></i> Coding Harness</span>
          <span class="condensed-pill active"><i class="i-carbon:checkmark-outline"></i> Runtime Tools</span>
        </div>
      </div>
      <p class="failure-mode-explanation">Coding-agent harness acquires skills and modifies environment dynamically.</p>
      <div class="failure-mode-takeaway condensed-takeaway">
        <span class="takeaway-check">✓</span>
        <strong>Unexpected errors become recoverable steps at runtime.</strong>
      </div>
    </template>
  </div>

  <!-- Flipped card back overlay -->
  <div
    v-if="isFlipped"
    class="card-back-overlay"
    :class="{ 'is-closing': isClosing }"
    @click.self="condenseCard"
  >
    <div class="card-back-inner" :class="{ 'inner-closing': isClosing }">
      <div class="card-back-header">
        <div class="visual-kicker orange card-back-kicker">
          <span class="card-back-tag mono"><i class="i-carbon:rotate-360"></i> CARD 01 · REVERSE</span>
          <span class="kicker-sep">/</span>
          <span>CAPABILITY RECOVERY · SOLUTION</span>
        </div>
        <div class="header-actions">
          <button class="reset-top-btn mono" title="Reset to initial problem" @click="resetInitial">
            <i class="i-carbon:undo"></i>
            <span>RESET</span>
          </button>
          <button class="condense-top-btn mono" @click="condenseCard">
            <span class="check-mark">✓</span>
            <span>CONDENSE</span>
            <span class="i-carbon:minimize"></span>
          </button>
        </div>
      </div>

      <div class="open-world-claim">
        <span class="claim-line">Research is an <span class="open-highlight orange-open">open-world</span> task.</span>
        <span class="claim-line claim-line-shift">We need an <span class="open-highlight blue-open">open-world</span> coding agent.</span>
      </div>

      <div class="compare-grid">
        <div class="compare-side failure-side">
          <div class="compare-kicker rose">LangGraph-style orchestration</div>
          <div class="compare-subtitle">predefined graph</div>
          <div class="static-graph">
            <div class="graph-top"><span class="graph-icon rose i-carbon:flow-data"></span><span>fixed tool set</span></div>
            <div class="graph-arrow">↓</div>
            <div class="graph-tools">
              <div class="graph-node"><span class="graph-node-icon rose i-carbon:tools"></span><span>Tool A</span></div>
              <div class="graph-node"><span class="graph-node-icon rose i-carbon:tools"></span><span>Tool B</span></div>
              <div class="graph-node"><span class="graph-node-icon rose i-carbon:tools"></span><span>Tool C</span></div>
            </div>
          </div>
          <div class="compare-failure">
            <div class="failure-step"><span class="failure-icon rose i-carbon:error-outline"></span><span>API fails</span></div>
            <div class="failure-arrow">↓</div>
            <div class="failure-step muted"><span class="failure-icon i-carbon:stop-outline"></span><span>no recovery tool</span></div>
            <div class="failure-arrow">↓</div>
            <div class="dead-end"><span class="failure-icon rose i-carbon:error-outline"></span>DEAD END</div>
          </div>
          <div class="compare-note">Capabilities are bounded by what developers anticipated.</div>
        </div>

        <div class="compare-side recovery-side">
          <div class="compare-kicker blue">Coding-agent harness</div>
          <div class="compare-subtitle">open action space</div>
          <div class="harness-diagram">
            <div class="harness-computer"><span class="harness-icon blue i-carbon:laptop"></span><span>Computer</span></div>
            <div class="harness-arrow">↓</div>
            <div class="harness-paths">
              <div class="harness-path"><div class="harness-node"><span class="harness-icon blue i-carbon:terminal"></span><span>shell</span></div><span class="harness-arrow">↓</span><div class="harness-node"><span class="harness-icon blue i-carbon:branch"></span><span>git</span></div></div>
              <div class="harness-path"><div class="harness-node"><span class="harness-icon blue i-carbon:folder"></span><span>files</span></div><span class="harness-arrow">↓</span><div class="harness-node"><span class="harness-icon blue i-carbon:document"></span><span>docs</span></div></div>
              <div class="harness-path"><div class="harness-node"><span class="harness-icon blue i-carbon:earth"></span><span>browser</span></div><span class="harness-arrow">↓</span><div class="harness-node"><span class="harness-icon blue i-carbon:package"></span><span>packages</span></div></div>
            </div>
            <div class="agent-band"><div class="harness-node"><span class="harness-icon blue i-carbon:tools"></span><span>skills</span></div><div class="agent-core">agent</div><div class="harness-node"><span class="harness-icon blue i-carbon:api"></span><span>MCP</span></div></div>
            <div class="harness-arrow">↓</div>
            <div class="cli-api">CLI / API</div>
          </div>
          <div class="recovery-flow compact"><div class="recovery-sequence"><span>fail</span><b>→</b><span>inspect</span><b>→</b><span>learn</span><b>→</b><span>modify environment</span><b>→</b><span>retry</span></div><div class="recovery-caption">The agent can acquire the missing capability at runtime.</div></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.failure-flip-card {
  cursor: pointer;
  position: relative;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.failure-flip-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 36px -4px rgba(234, 88, 12, 0.16), 0 6px 16px -2px rgba(15, 23, 42, 0.06);
  border-color: #f97316;
}

.flip-icon-chip {
  background: rgba(234, 88, 12, 0.09);
  border: 1px solid rgba(234, 88, 12, 0.28);
  border-radius: 50%;
  color: #ea580c;
  width: 18px;
  height: 18px;
  font-size: 10px;
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.failure-flip-card:hover .flip-icon-chip {
  background: #ea580c;
  color: #ffffff;
  transform: rotate(180deg);
  box-shadow: 0 2px 6px rgba(234, 88, 12, 0.35);
}

.orange-check-badge {
  background: #ea580c;
  border: none;
  border-radius: 50%;
  color: #ffffff;
  width: 18px;
  height: 18px;
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(234, 88, 12, 0.35);
  transition: all 0.2s ease;
}

.orange-check-badge:hover {
  background: #c2410c;
  transform: scale(1.18);
  box-shadow: 0 3px 8px rgba(234, 88, 12, 0.45);
}

.badge-check {
  font-size: 11px;
  font-weight: 800;
  display: block;
}

.badge-reset {
  display: none;
  font-size: 10px;
}

.orange-check-badge:hover .badge-check {
  display: none;
}

.orange-check-badge:hover .badge-reset {
  display: flex;
  align-items: center;
  justify-content: center;
}

.condensed-visual {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 10px 0 12px;
  background: rgba(255, 247, 237, 0.6);
  border: 1px dashed rgba(234, 88, 12, 0.3);
  border-radius: 9px;
  padding: 10px 12px;
}

.condensed-flow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11.5px;
  color: var(--muted);
  font-family: "Fira Code", monospace;
}

.condensed-flow b {
  color: #cbd5e1;
}

.condensed-flow .flow-err {
  color: #f43f5e;
  font-weight: 600;
}

.condensed-flow .flow-rec {
  color: #ea580c;
  font-weight: 600;
}

.condensed-tags {
  display: flex;
  gap: 8px;
  align-items: center;
}

.condensed-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--muted);
  background: #ffffff;
  border: 1px solid var(--line);
  padding: 2px 8px;
  border-radius: 6px;
}

.condensed-pill.active {
  color: #ea580c;
  border-color: rgba(234, 88, 12, 0.35);
  background: #fff7ed;
  font-weight: 500;
}

.condensed-takeaway {
  display: flex;
  align-items: flex-start;
  gap: 6px;
}

.takeaway-check {
  color: #ea580c;
  font-weight: 800;
  font-size: 14px;
  line-height: 1.1;
}

/* Card Back Overlay Inside Slide */
.card-back-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 100;
  background: rgba(248, 250, 252, 0.95);
  backdrop-filter: blur(14px);
  padding: 32px 48px 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  perspective: 1200px;
  animation: overlayFade 0.3s ease-out forwards;
}

.card-back-overlay.is-closing {
  animation: overlayFadeOut 0.35s ease-in forwards;
}

@keyframes overlayFade {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes overlayFadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

.card-back-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  transform-style: preserve-3d;
  animation: cardFlipIn 0.42s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.card-back-inner.inner-closing {
  animation: cardFlipOut 0.35s cubic-bezier(0.7, 0, 0.84, 0) forwards;
}

@keyframes cardFlipIn {
  0% {
    opacity: 0;
    transform: perspective(1200px) rotateY(-85deg) scale(0.9);
  }
  65% {
    transform: perspective(1200px) rotateY(6deg) scale(1.01);
  }
  100% {
    opacity: 1;
    transform: perspective(1200px) rotateY(0deg) scale(1);
  }
}

@keyframes cardFlipOut {
  0% {
    opacity: 1;
    transform: perspective(1200px) rotateY(0deg) scale(1);
  }
  100% {
    opacity: 0;
    transform: perspective(1200px) rotateY(80deg) scale(0.9);
  }
}

.card-back-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
}

.card-back-kicker {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 0;
}

.card-back-tag {
  background: rgba(234, 88, 12, 0.1);
  border: 1px solid rgba(234, 88, 12, 0.28);
  border-radius: 999px;
  color: #ea580c;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.8px;
  padding: 2px 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.kicker-sep {
  color: #fdba74;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reset-top-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 11px;
  letter-spacing: 0.5px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.reset-top-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: var(--ink);
}

.condense-top-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 4px 11px;
  font-size: 11px;
  letter-spacing: 0.5px;
  color: var(--body);
  cursor: pointer;
  transition: all 0.15s ease;
}

.condense-top-btn .check-mark {
  color: #ea580c;
  font-weight: 700;
}

.condense-top-btn:hover {
  background: #fff7ed;
  border-color: #ea580c;
  color: #ea580c;
}
</style>
