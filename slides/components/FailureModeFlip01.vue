<script setup lang="ts">
import { onUnmounted, ref } from "vue"
import { useTalkSteps } from '../composables/useTalkSteps'

const emit = defineEmits<{ insight: [earned: boolean] }>()

const isFlipped = ref(false)
const isCondensed = ref(false)
const isClosing = ref(false)
let closeTimer: ReturnType<typeof setTimeout> | undefined
onUnmounted(() => clearTimeout(closeTimer))

const openFlip = () => {
  clearTimeout(closeTimer)
  isFlipped.value = true
  isClosing.value = false
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

const resetInitial = (e?: MouseEvent) => {
  if (e) e.stopPropagation()
  isClosing.value = false
  isFlipped.value = false
  isCondensed.value = false
  emit('insight', false)
}
useTalkSteps(14, step => {
  clearTimeout(closeTimer)
  isClosing.value = false
  isFlipped.value = step === 1
  isCondensed.value = step >= 2
  emit('insight', isCondensed.value)
})
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
        <span class="failure-mode-label">WORKFLOW</span>
        <span class="flip-icon-chip" title="Click to flip for solution"><i class="i-carbon:rotate-360"></i></span>
      </div>
      <div class="failure-mode-visual failure-graph" aria-label="A fixed workflow hits an error and stops">
        <div class="failure-graph-flow"><span>Observe</span><b>→</b><span>Hypothesize</span><b>→</b><span>Code</span><b>→</b><span>Evaluate</span></div>
        <div class="failure-graph-error"><span class="i-carbon:error-outline"></span><b>ERROR</b></div>
        <div class="failure-graph-dead"><span>↓</span><strong>dead end</strong></div>
      </div>
      <p class="failure-mode-explanation">Fixed recovery paths</p>
      <div class="failure-mode-takeaway"><strong>Unexpected errors need human help.</strong></div>
    </template>

    <!-- Condensed solution card -->
    <template v-else>
      <div class="failure-mode-head">
        <span class="failure-mode-number mono">01</span>
        <span class="failure-mode-label">WORKFLOW</span>
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
      <p class="failure-mode-explanation">Acquire missing tools at runtime.</p>
      <div class="failure-mode-takeaway condensed-takeaway">
        <span class="takeaway-check">✓</span>
        <strong>Building on code agent harness.</strong>
      </div>
      <div class="failure-mode-takeaway condensed-takeaway">
        <span class="takeaway-check">✓</span>
        <strong>Extend with Skills &amp; MCP.</strong>
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
          <span>WORKFLOW</span>
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

      <div class="workflow-comparison">
        <!-- Left Column: Fixed capabilities / Predefined workflow -->
        <section class="workflow-panel workflow-fixed" aria-label="Predefined workflow stops without a recovery tool">
          <div class="workflow-panel-head">
            <div class="workflow-panel-label mono">FIXED CAPABILITIES</div>
            <h3>Predefined workflow</h3>
          </div>

          <div class="workflow-panel-body">
            <!-- Fixed Tool Registry -->
            <div class="wf-card wf-toolbox">
              <div class="wf-card-header">
                <span class="wf-card-title">Fixed tool set</span>
                <span class="wf-card-tag mono">e.g. LangGraph</span>
              </div>
              <div class="wf-tools-grid">
                <div class="wf-tool-item">
                  <i class="i-carbon:tools"></i>
                  <span>Tool A</span>
                </div>
                <div class="wf-tool-item">
                  <i class="i-carbon:tools"></i>
                  <span>Tool B</span>
                </div>
                <div class="wf-tool-item">
                  <i class="i-carbon:tools"></i>
                  <span>Tool C</span>
                </div>
              </div>
            </div>

            <!-- Connector: No fallback path -->
            <div class="wf-fallback-connector">
              <span class="wf-fallback-line"></span>
              <span class="wf-fallback-badge mono">
                <i class="i-carbon:arrow-down"></i>
                <span>No fallback path</span>
              </span>
              <span class="wf-fallback-line"></span>
            </div>

            <!-- Error State -->
            <div class="wf-card wf-error-card">
              <div class="wf-error-content">
                <div class="wf-error-icon-box">
                  <i class="i-carbon:error-outline"></i>
                </div>
                <div class="wf-error-text">
                  <div class="wf-error-title-row">
                    <strong>API fails</strong>
                    <span class="wf-error-badge mono">BLOCKED</span>
                  </div>
                  <p>No recovery tool available.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Outcome footer -->
          <div class="workflow-outcome wf-outcome-fixed">
            <div class="wf-outcome-icon-wrap">
              <i class="i-carbon:stop-outline"></i>
            </div>
            <div class="wf-outcome-text">
              <strong>Run stops.</strong>
              <span>Missing tool. Human help needed.</span>
            </div>
          </div>
        </section>

        <!-- Right Column: Extensible capabilities / Coding-agent harness -->
        <section class="workflow-panel workflow-open" aria-label="Coding agent acquires tools and resumes research">
          <div class="workflow-panel-head">
            <div class="workflow-panel-label mono">EXTENSIBLE CAPABILITIES</div>
            <h3>Coding-agent harness</h3>
          </div>

          <div class="workflow-panel-body">
            <!-- Computer access -->
            <div class="wf-card wf-computer-card">
              <div class="wf-card-header">
                <span class="wf-card-title">Computer access</span>
              </div>
              <div class="wf-resources-grid">
                <div class="wf-resource-item">
                  <i class="i-carbon:terminal"></i>
                  <div><strong>shell</strong><small>git</small></div>
                </div>
                <div class="wf-resource-item">
                  <i class="i-carbon:folder"></i>
                  <div><strong>files</strong><small>docs</small></div>
                </div>
                <div class="wf-resource-item">
                  <i class="i-carbon:earth"></i>
                  <div><strong>browser</strong><small>packages</small></div>
                </div>
              </div>
            </div>

            <!-- Agent Harness + Skills + MCP -->
            <div class="wf-card wf-agent-card">
              <div class="wf-agent-layout">
                <div class="wf-ext-chip">
                  <i class="i-carbon:tools"></i>
                  <span>Skills</span>
                </div>
                <span class="wf-agent-arrow">→</span>
                <div class="wf-agent-core">
                  <i class="i-carbon:bot"></i>
                  <div>
                    <strong>Agent</strong>
                    <small class="mono">CLI / API</small>
                  </div>
                </div>
                <span class="wf-agent-arrow">←</span>
                <div class="wf-ext-chip">
                  <i class="i-carbon:api"></i>
                  <span>MCP</span>
                </div>
              </div>
            </div>

            <!-- Recovery sequence -->
            <div class="wf-recovery-track">
              <div class="wf-step-item">
                <small class="wf-step-num mono">01</small>
                <span class="wf-step-name">Inspect</span>
              </div>
              <span class="wf-step-sep">→</span>
              <div class="wf-step-item">
                <small class="wf-step-num mono">02</small>
                <span class="wf-step-name">Acquire tools</span>
              </div>
              <span class="wf-step-sep">→</span>
              <div class="wf-step-item">
                <small class="wf-step-num mono">03</small>
                <span class="wf-step-name">Retry</span>
              </div>
            </div>
          </div>

          <!-- Outcome footer -->
          <div class="workflow-outcome wf-outcome-open">
            <div class="wf-outcome-icon-wrap">
              <i class="i-carbon:checkmark-outline"></i>
            </div>
            <div class="wf-outcome-text">
              <strong>Research resumes.</strong>
              <span>Acquire tools. Extend what the agent can do.</span>
            </div>
          </div>
        </section>
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
  font-family: var(--deck-mono);
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
  background: rgba(248, 250, 252, 0.98);
  backdrop-filter: blur(12px);
  padding: 28px 46px 26px;
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

.reset-top-btn,
.condense-top-btn {
  display: inline-flex;
  align-items: center;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 11px;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.reset-top-btn {
  gap: 5px;
  padding: 4px 10px;
  color: var(--muted);
}

.reset-top-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: var(--ink);
}

.condense-top-btn {
  gap: 6px;
  padding: 4px 11px;
  color: var(--body);
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

/* Open-world claim heading */
.open-world-claim {
  color: #0f172a;
  font-family: var(--deck-sans);
  font-size: 26px;
  font-weight: 600;
  letter-spacing: -0.7px;
  line-height: 1.16;
  margin: 10px 0 14px;
}

.claim-line {
  color: #0f172a;
  display: block;
  white-space: nowrap;
}

.claim-line-shift {
  margin-left: 24px;
}

.open-highlight {
  display: inline-block;
  font-weight: 700;
}

.orange-open {
  color: #ea580c;
}

.blue-open {
  color: #0284c7;
}

/* Main comparison layout */
.workflow-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 8px;
}

.workflow-panel {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03);
}

.workflow-fixed {
  border-top: 3px solid #e11d48;
}

.workflow-open {
  border-top: 3px solid #0284c7;
}

.workflow-panel-head {
  margin-bottom: 12px;
}

.workflow-panel-label {
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 0.8px;
  margin-bottom: 2px;
}

.workflow-fixed .workflow-panel-label {
  color: #e11d48;
}

.workflow-open .workflow-panel-label {
  color: #0284c7;
}

.workflow-panel h3 {
  color: #0f172a;
  font-family: var(--deck-sans);
  font-size: 19px;
  font-weight: 600;
  letter-spacing: -0.35px;
  line-height: 1.15;
  margin: 0;
}

.workflow-panel-body {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 12px;
  flex: 1;
}

/* Card components inside panels */
.wf-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 9px 11px;
}

.wf-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.wf-card-title {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}

.wf-card-tag {
  font-size: 8.5px;
  color: #94a3b8;
  font-weight: 600;
}

/* Fixed tools grid */
.wf-tools-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.wf-tool-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 4px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #334155;
}

.wf-tool-item i {
  color: #64748b;
  font-size: 13px;
}

/* Fallback connector */
.wf-fallback-connector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 20px;
  position: relative;
}

.wf-fallback-line {
  flex: 1;
  border-top: 1px dashed #fca5a5;
}

.wf-fallback-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 8.5px;
  font-weight: 700;
  color: #e11d48;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 999px;
  padding: 2px 8px;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

.wf-fallback-badge i {
  font-size: 10px;
}

/* Error card */
.wf-error-card {
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-left: 3px solid #e11d48;
  padding: 9px 12px;
}

.wf-error-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.wf-error-icon-box {
  color: #e11d48;
  font-size: 20px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.wf-error-text {
  flex: 1;
  min-width: 0;
}

.wf-error-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.wf-error-title-row strong {
  font-size: 13px;
  font-weight: 700;
  color: #9f1239;
}

.wf-error-badge {
  font-size: 8px;
  font-weight: 700;
  color: #e11d48;
  background: #ffe4e6;
  border: 1px solid #fca5a5;
  border-radius: 4px;
  padding: 1px 5px;
}

.wf-error-text p {
  font-size: 10px;
  color: #881337;
  margin: 2px 0 0;
  line-height: 1.25;
}

/* Right side: Computer access */
.wf-computer-card {
  background: #f0f9ff;
  border-color: #bae6fd;
}

.wf-resources-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.wf-resource-item {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
  padding: 6px 8px;
}

.wf-resource-item i {
  color: #0284c7;
  font-size: 14px;
  flex-shrink: 0;
}

.wf-resource-item div {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.wf-resource-item strong {
  font-size: 11.5px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.1;
}

.wf-resource-item small {
  font-size: 8.5px;
  color: #64748b;
  line-height: 1.1;
}

/* Agent Harness Layout */
.wf-agent-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 7px 10px;
}

.wf-agent-layout {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.wf-ext-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 10.5px;
  font-weight: 700;
  color: #334155;
}

.wf-ext-chip i {
  color: #0284c7;
  font-size: 12px;
}

.wf-agent-arrow {
  color: #0284c7;
  font-size: 13px;
  font-weight: 800;
}

.wf-agent-core {
  display: flex;
  align-items: center;
  gap: 7px;
  background: #f0f9ff;
  border: 1.5px solid #0284c7;
  border-radius: 7px;
  padding: 4px 12px;
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.08);
}

.wf-agent-core i {
  color: #0284c7;
  font-size: 16px;
}

.wf-agent-core strong {
  font-size: 12.5px;
  font-weight: 700;
  color: #0369a1;
  line-height: 1.1;
}

.wf-agent-core small {
  font-size: 8.5px;
  color: #64748b;
  display: block;
}

/* Recovery Track */
.wf-recovery-track {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
  padding: 5px 10px;
}

.wf-step-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.wf-step-num {
  font-size: 8.5px;
  font-weight: 700;
  color: #0284c7;
  background: #e0f2fe;
  padding: 1px 4px;
  border-radius: 3px;
}

.wf-step-name {
  font-size: 10px;
  font-weight: 600;
  color: #0369a1;
}

.wf-step-sep {
  color: #38bdf8;
  font-size: 11px;
}

/* Outcome rows */
.workflow-outcome {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 11px;
  border-radius: 8px;
  margin-top: 8px;
}

.wf-outcome-fixed {
  background: #fff1f2;
  border: 1px solid #fecdd3;
}

.wf-outcome-open {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
}

.wf-outcome-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.wf-outcome-fixed .wf-outcome-icon-wrap {
  color: #e11d48;
  font-size: 20px;
}

.wf-outcome-open .wf-outcome-icon-wrap {
  color: #0284c7;
  font-size: 20px;
}

.wf-outcome-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.wf-outcome-fixed strong {
  color: #be123c;
  font-size: 14.5px;
  font-weight: 750;
  line-height: 1.15;
}

.wf-outcome-open strong {
  color: #0369a1;
  font-size: 14.5px;
  font-weight: 750;
  line-height: 1.15;
}

.wf-outcome-text span {
  color: #64748b;
  font-size: 10px;
  line-height: 1.25;
}
</style>
