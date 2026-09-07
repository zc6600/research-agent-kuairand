<script setup lang="ts">
import { ref } from "vue"

const emit = defineEmits<{ insight: [earned: boolean] }>()

const isFlipped = ref(false)
const isCondensed = ref(false)
const isClosing = ref(false)
const reversePage = ref(0)
const reversePageCount = 2
const parallelClick = ref(0)
const parallelClickCount = 1

const openFlip = () => {
  isFlipped.value = true
  isClosing.value = false
  reversePage.value = 0
  parallelClick.value = 0
}

const condenseCard = () => {
  isClosing.value = true
  setTimeout(() => {
    isFlipped.value = false
    isClosing.value = false
    isCondensed.value = true
    emit('insight', true)
  }, 360)
}

const advanceReversePage = () => {
  if (reversePage.value === 1) {
    if (parallelClick.value < parallelClickCount) {
      parallelClick.value += 1
    } else {
      condenseCard()
    }
    return
  }
  if (reversePage.value < reversePageCount - 1) {
    reversePage.value += 1
    parallelClick.value = 0
    return
  }
  condenseCard()
}

const goToReversePage = (page: number) => {
  reversePage.value = page
  parallelClick.value = 0
}

const resetInitial = (event?: MouseEvent) => {
  if (event) event.stopPropagation()
  isClosing.value = false
  isFlipped.value = false
  isCondensed.value = false
  emit('insight', false)
  reversePage.value = 0
  parallelClick.value = 0
}
</script>

<template>
  <div
    class="failure-mode failure-mode-tree tree-search-flip-card"
    :class="{ 'is-condensed-mode': isCondensed }"
    @click="openFlip"
  >
    <template v-if="!isCondensed">
      <div class="failure-mode-head">
        <span class="failure-mode-number mono">03</span>
        <span class="failure-mode-label">TREE SEARCH</span>
        <span class="tree-search-flip-icon" title="Click to flip"><i class="i-carbon:rotate-360"></i></span>
      </div>
      <div class="failure-mode-visual tree-search-mini-visual" aria-label="Each tree-search child rereads context before making one feature edit">
        <div class="tree-search-mini-flow mono">
          <span>read</span><b>→</b><span class="edit">edit</span><b>→</b><span class="stop">stop</span>
        </div>
        <div class="tree-search-mini-branches" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
        <div class="tree-search-mini-caption mono">one edit / one exit</div>
      </div>
      <p class="failure-mode-explanation">Repeated context reads</p>
      <div class="failure-mode-takeaway"><strong>Each small edit pays the reading cost.</strong></div>
    </template>

    <template v-else>
      <div class="failure-mode-head">
        <span class="failure-mode-number mono">03</span>
        <span class="failure-mode-label">TREE SEARCH</span>
        <button class="tree-search-check-badge" title="Click to reset" @click.stop="resetInitial">
          <span class="badge-check">✓</span>
          <span class="badge-reset"><i class="i-carbon:undo"></i></span>
        </button>
      </div>
      <div class="failure-mode-visual tree-search-condensed-visual" aria-label="Reuse exploration context and spend branches on different edits">
        <div class="tree-search-condensed-flow mono"><span>READ ONCE</span><b>→</b><span>BRANCH EDITS</span></div>
        <div class="tree-search-condensed-note">Persist the read. Vary the hypothesis.</div>
      </div>
      <p class="failure-mode-explanation">Reuse context across experiments.</p>
      <div class="failure-mode-takeaway tree-search-condensed-takeaway"><span>✓</span><strong>Raise task granularity.</strong></div>
      <div class="failure-mode-takeaway tree-search-condensed-takeaway"><span>✓</span><strong>Parallelize across branches.</strong></div>
    </template>
  </div>

  <div
    v-if="isFlipped"
    class="tree-search-card-back-overlay"
    :class="{ 'is-closing': isClosing }"
    @click="advanceReversePage"
  >
    <div class="tree-search-card-back-inner" :class="{ 'inner-closing': isClosing }">
      <div class="tree-search-card-back-header" @click.stop>
        <div class="visual-kicker rose tree-search-card-back-kicker">
          <span class="tree-search-card-back-tag mono"><i class="i-carbon:rotate-360"></i> CARD 03 · REVERSE</span>
          <span class="tree-search-kicker-sep">/</span>
          <span>TREE SEARCH</span>
        </div>
        <div class="ts-reverse-tabs mono" role="tablist" aria-label="Card 03 reverse pages">
          <button
            class="ts-reverse-tab"
            :class="{ 'is-active': reversePage === 0 }"
            role="tab"
            :aria-selected="reversePage === 0"
            @click.stop="goToReversePage(0)"
          >
            <span>01</span><b>TOKEN COST</b>
          </button>
          <button
            class="ts-reverse-tab"
            :class="{ 'is-active': reversePage === 1 }"
            role="tab"
            :aria-selected="reversePage === 1"
            @click.stop="goToReversePage(1)"
          >
            <span>02</span><b>PARALLEL</b>
          </button>
        </div>
        <div class="tree-search-back-actions">
          <button class="tree-search-reset-btn mono" title="Reset to initial problem" @click="resetInitial">
            <i class="i-carbon:undo"></i>
            <span>RESET</span>
          </button>
          <button class="tree-search-condense-btn mono" @click="condenseCard">
            <span class="tree-search-check-mark">✓</span>
            <span>CONDENSE</span>
            <span class="i-carbon:minimize"></span>
          </button>
        </div>
      </div>

      <div class="ts-reverse-page" :key="reversePage">
        <template v-if="reversePage === 0">
          <div class="tree-search-back-claim">
            <span>Repeated reads <strong>consume the budget</strong></span>
          </div>

          <div class="tree-search-evidence-grid">
            <section class="tree-search-evidence-block tree-search-measured-block">
              <div class="tree-search-evidence-kicker mono">MEASURED ONE-EDIT A/B</div>
              <h2><strong>8.0×</strong> read / edit cost</h2>
              <div class="tree-search-bar-chart" aria-label="Read-only 340 thousand tokens versus write-only 42 thousand tokens">
                <div class="tree-search-chart-row">
                  <span class="tree-search-chart-label mono">READ ONLY</span>
                  <span class="tree-search-chart-bar"><i></i></span>
                  <strong class="mono">340K</strong>
                </div>
                <div class="tree-search-chart-row tree-search-chart-write">
                  <span class="tree-search-chart-label mono">WRITE ONLY</span>
                  <span class="tree-search-chart-bar"><i></i></span>
                  <strong class="mono">42K</strong>
                </div>
              </div>
              <p>10 files read / 1 line edited</p>
            </section>

            <section class="tree-search-evidence-block tree-search-ablation-block">
              <div class="tree-search-evidence-kicker mono">ABLATION PROJECTION · N=8</div>
              <h2><strong>4.5×</strong> projected total cost</h2>
              <div class="tree-search-bar-chart" aria-label="Rereading for eight children costs 3.06 million tokens versus 0.68 million when reading once">
                <div class="tree-search-chart-row">
                  <span class="tree-search-chart-label mono">REREAD ×8</span>
                  <span class="tree-search-chart-bar"><i></i></span>
                  <strong class="mono">3.06M</strong>
                </div>
                <div class="tree-search-chart-row tree-search-chart-reuse">
                  <span class="tree-search-chart-label mono">READ ONCE</span>
                  <span class="tree-search-chart-bar"><i></i></span>
                  <strong class="mono">0.68M</strong>
                </div>
              </div>
              <p>Reread every child / reuse the first read</p>
            </section>
          </div>

          <div class="tree-search-cost-comparison" aria-label="Two ways to run eight edits: reread context each time or reuse the initial read">
            <div class="tree-search-cost-method tree-search-cost-repeat"><strong>Reread context for every branch</strong><span>8 context reads + 8 edits</span></div>
            <div class="tree-search-cost-vs">vs</div>
            <div class="tree-search-cost-method"><strong>Reuse context across branches</strong><span>1 context read + 8 edits</span></div>
          </div>

          <div class="tree-search-evidence-footnote mono">
            <span>KuaiRand · Gemini 3.7 Flash · tokens include cache reads</span>
            <span>8-child costs are projected from measured arms.</span>
          </div>
        </template>

        <template v-else>
          <div class="ts-parallel-page">
            <div class="ts-parallel-claim">
              <span>One starting point. <strong>Independent answers.</strong></span>
            </div>

            <div class="ts-parallel-svg-wrap">
              <svg viewBox="0 0 1000 390" preserveAspectRatio="xMidYMid meet" role="img" aria-label="One research world, three isolated scientist worktrees, one reviewer">
                <defs>
                  <marker id="ts-arrow-a" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#2fb3e8" /></marker>
                  <marker id="ts-arrow-b" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#ff873f" /></marker>
                  <marker id="ts-arrow-c" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#ef5b5b" /></marker>
                </defs>
                <g class="ts-stage-label" text-anchor="middle">
                  <text x="112" y="30">01 / SHARED START</text>
                  <text x="495" y="30">02 / PARALLEL EXPLORATION</text>
                  <text x="883" y="30" :class="{ 'ts-vhidden': parallelClick < 1 }">03 / REVIEW</text>
                </g>
                <!-- Connections stop at card edges, keeping the text area clear. -->
                <path class="ts-branch-rail ts-rail-a" d="M150 205 C225 205 233 110 310 110" pathLength="1" />
                <path class="ts-branch-rail ts-rail-b" d="M150 205 H310" pathLength="1" />
                <path class="ts-branch-rail ts-rail-c" d="M150 205 C225 205 233 300 310 300" pathLength="1" />
                <g class="ts-world">
                  <circle cx="112" cy="205" r="38" class="ts-world-ring" />
                  <circle cx="112" cy="205" r="22" class="ts-world-globe" />
                  <ellipse cx="112" cy="205" rx="9" ry="22" class="ts-world-globe" />
                  <path d="M90 205 H134 M94 193 H130 M94 217 H130" class="ts-world-globe" />
                  <text x="112" y="270" text-anchor="middle" class="ts-node-title">Research world</text>
                  <text x="112" y="292" text-anchor="middle" class="ts-node-sub">Shared context</text>
                </g>
                <g v-for="(scientist, index) in ['A', 'B', 'C']" :key="scientist"
                  class="ts-sci-card" :class="`ts-sci-${scientist.toLowerCase()}`" :transform="`translate(310 ${70 + index * 95})`">
                  <rect class="ts-card-surface" width="370" height="80" rx="14" />
                  <path class="ts-card-accent" d="M1 23 V57" />
                  <circle cx="32" cy="30" r="5" class="ts-card-dot" />
                  <text x="49" y="37" class="ts-card-name">Scientist {{ scientist }}</text>
                  <text x="49" y="60" class="ts-card-detail">Isolated worktree</text>
                  <rect class="ts-branch-badge" x="283" y="24" width="66" height="32" rx="7" />
                  <text x="316" y="45" text-anchor="middle" class="ts-card-branch">r1b{{ index + 1 }}</text>
                </g>
                <!-- Each branch retains its color all the way to the reviewer. -->
                <g class="ts-merge" :class="{ 'ts-merge-visible': parallelClick >= 1 }">
                  <path class="ts-merge-rail ts-merge-a" d="M680 110 H722 C790 110 785 180 840 192" pathLength="1" marker-end="url(#ts-arrow-a)" />
                  <path class="ts-merge-rail ts-merge-b" d="M680 205 H837" pathLength="1" marker-end="url(#ts-arrow-b)" />
                  <path class="ts-merge-rail ts-merge-c" d="M680 300 H722 C790 300 785 230 840 218" pathLength="1" marker-end="url(#ts-arrow-c)" />
                </g>
                <g class="ts-reviewer" :class="{ 'ts-reviewer-visible': parallelClick >= 1 }">
                  <circle cx="883" cy="205" r="43" class="ts-reviewer-halo" />
                  <circle cx="883" cy="205" r="32" class="ts-reviewer-ring" />
                  <path d="M869 205 l9 9 19 -22" class="ts-reviewer-check" />
                  <text x="883" y="270" text-anchor="middle" class="ts-node-title">Reviewer</text>
                  <text x="883" y="292" text-anchor="middle" class="ts-node-sub">Merge · Check</text>
                </g>
              </svg>
            </div>

            <div class="ts-parallel-takeaway">
              <span>Explore in isolated worktrees.</span>
              <span :class="{ 'ts-vhidden': parallelClick < 1 }">Review after completion.</span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Tab navigation ── */
.ts-reverse-tabs {
  display: flex;
  gap: 4px;
  align-items: center;
}

.ts-reverse-tab {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 7px;
  color: var(--muted);
  cursor: pointer;
  font-size: 10px;
  letter-spacing: 0.5px;
  padding: 3px 9px;
  transition: all 0.15s ease;
}

.ts-reverse-tab span { color: #cbd5e1; }
.ts-reverse-tab b { font-weight: 700; }

.ts-reverse-tab.is-active {
  background: rgba(255, 92, 120, 0.07);
  border-color: rgba(255, 92, 120, 0.35);
  color: var(--rose);
}

.ts-reverse-tab:not(.is-active):hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: var(--ink);
}

/* ── Page container ── */
.ts-reverse-page {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  animation: tsPageIn 0.28s ease-out both;
}

@keyframes tsPageIn {
  from { opacity: 0; translate: 0 8px; }
  to   { opacity: 1; translate: 0 0; }
}

/* ── Parallel page ── */
.ts-parallel-page {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  gap: 14px;
}
.ts-parallel-claim {
  font-size: 26px;
  font-weight: 500;
  color: var(--ink);
  letter-spacing: -0.5px;
  line-height: 1.15;
  margin: 26px 0 0;
}
.ts-parallel-claim strong { color: var(--blue); font-weight: 600; }
.ts-parallel-svg-wrap { flex: 1; min-height: 0; position: relative; }
.ts-parallel-svg-wrap svg { display: block; position: absolute; inset: 0; width: 100%; height: 100%; }
.ts-stage-label {
  fill: #788694;
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 1.3px;
}
@keyframes tsRailDraw {
  from { opacity: 0; stroke-dashoffset: 1; }
  to { opacity: 0.85; stroke-dashoffset: 0; }
}
.ts-branch-rail {
  fill: none;
  stroke-linecap: round;
  stroke-dasharray: 1;
  stroke-width: 2.5;
  animation: tsRailDraw 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.ts-rail-a { stroke: #2fb3e8; }
.ts-rail-b { stroke: #ff873f; animation-delay: 0.12s; }
.ts-rail-c { stroke: #ef5b5b; animation-delay: 0.24s; }
.ts-world-ring { fill: #f0faff; stroke: #c6eafa; stroke-width: 1.5; }
.ts-world-globe { fill: none; stroke: #2baee2; stroke-width: 1.6; }
.ts-node-title { fill: var(--ink); font-size: 19px; font-weight: 600; }
.ts-node-sub { fill: #788694; font-size: 14px; }
.ts-sci-a { --branch-color: #2fb3e8; --branch-tint: #edf9fe; --branch-border: #c7e9f7; }
.ts-sci-b { --branch-color: #f18440; --branch-tint: #fff5ec; --branch-border: #f4ddca; }
.ts-sci-c { --branch-color: #eb6269; --branch-tint: #fff1f2; --branch-border: #f1d4d7; }
.ts-card-surface { fill: #fff; stroke: var(--branch-border); stroke-width: 1.4; }
.ts-card-accent { fill: none; stroke: var(--branch-color); stroke-width: 3; stroke-linecap: round; }
.ts-card-dot { fill: var(--branch-color); }
.ts-card-name { fill: var(--ink); font-size: 21px; font-weight: 600; }
.ts-card-detail { fill: #788694; font-size: 13px; }
.ts-branch-badge { fill: var(--branch-tint); }
.ts-card-branch { fill: var(--branch-color); font-family: 'Fira Code', monospace; font-size: 15px; font-weight: 500; }
.ts-merge-rail {
  fill: none;
  stroke-linecap: round;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  stroke-width: 2.5;
  opacity: 0;
  transition: opacity 0.25s ease, stroke-dashoffset 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.ts-merge-a { stroke: #2fb3e8; }
.ts-merge-b { stroke: #ff873f; }
.ts-merge-c { stroke: #ef5b5b; }
.ts-merge-visible .ts-merge-rail { opacity: 0.85; stroke-dashoffset: 0; }
.ts-reviewer { opacity: 0; transition: opacity 0.4s ease, translate 0.4s ease; translate: 0 6px; }
.ts-reviewer-visible { opacity: 1; translate: 0 0; }
.ts-reviewer-halo { fill: #f0faff; stroke: #d7effa; stroke-width: 1; }
.ts-reviewer-ring { fill: #fff; stroke: #2fb3e8; stroke-width: 2; }
.ts-reviewer-check { fill: none; stroke: #2fb3e8; stroke-linecap: round; stroke-linejoin: round; stroke-width: 3; }
.ts-parallel-takeaway {
  display: flex;
  gap: 8px;
  align-items: center;
  border-top: 1px solid var(--line);
  padding-top: 12px;
  font-size: 15px;
  color: var(--body);
  font-weight: 500;
  flex-wrap: wrap;
}
.ts-parallel-takeaway span { transition: opacity 0.35s ease; }
.ts-parallel-takeaway span + span::before { content: "·"; margin-right: 8px; color: #aebcc8; }
.ts-vhidden { opacity: 0; pointer-events: none; }
@media (prefers-reduced-motion: reduce) {
  .ts-branch-rail { animation: none; opacity: 0.85; stroke-dashoffset: 0; }
  .ts-merge-rail, .ts-reviewer, .ts-parallel-takeaway span { transition: none; }
}


.tree-search-flip-card {
  cursor: pointer;
  position: relative;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.tree-search-flip-card:hover {
  border-color: var(--rose);
  box-shadow: 0 16px 36px -4px rgba(255, 92, 120, 0.16), 0 6px 16px -2px rgba(15, 23, 42, 0.06);
  transform: translateY(-3px);
}

.tree-search-flip-icon {
  align-items: center;
  background: rgba(255, 92, 120, 0.09);
  border: 1px solid rgba(255, 92, 120, 0.28);
  border-radius: 50%;
  color: var(--rose);
  display: inline-flex;
  flex-shrink: 0;
  font-size: 10px;
  height: 18px;
  justify-content: center;
  margin-left: auto;
  transition: all 0.2s ease;
  width: 18px;
}

.tree-search-flip-card:hover .tree-search-flip-icon {
  background: var(--rose);
  box-shadow: 0 2px 6px rgba(255, 92, 120, 0.32);
  color: #ffffff;
  transform: rotate(180deg);
}

.tree-search-mini-visual {
  align-items: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}

.tree-search-mini-flow {
  align-items: center;
  display: flex;
  gap: 7px;
  justify-content: center;
  width: 100%;
}

.tree-search-mini-flow span {
  border: 1px solid #e3e5e8;
  border-radius: 3px;
  box-sizing: border-box;
  color: var(--muted);
  font-size: 9px;
  line-height: 1;
  padding: 7px 8px;
}

.tree-search-mini-flow .edit {
  border-color: rgba(255, 92, 120, 0.52);
  color: var(--rose);
}

.tree-search-mini-flow .stop {
  border-color: rgba(255, 92, 120, 0.32);
  color: var(--rose);
}

.tree-search-mini-flow b {
  color: #b8bbc0;
  font-size: 10px;
  font-weight: 400;
}

.tree-search-mini-branches {
  align-items: flex-end;
  display: flex;
  gap: 16px;
  height: 19px;
  justify-content: center;
  position: relative;
  width: 68%;
}

.tree-search-mini-branches::before {
  border-top: 1px solid rgba(255, 92, 120, 0.35);
  content: '';
  left: 0;
  position: absolute;
  right: 0;
  top: 2px;
}

.tree-search-mini-branches i {
  background: #ffffff;
  border: 1px solid #bec3c8;
  border-radius: 50%;
  height: 7px;
  position: relative;
  width: 7px;
}

.tree-search-mini-branches i:nth-child(2) {
  border-color: var(--rose);
  box-shadow: 0 0 0 3px rgba(255, 92, 120, 0.10);
}

.tree-search-mini-caption {
  color: var(--muted);
  font-size: 8px;
  letter-spacing: .35px;
}

.tree-search-check-badge {
  align-items: center;
  background: var(--rose);
  border: none;
  border-radius: 50%;
  color: #ffffff;
  cursor: pointer;
  display: inline-flex;
  flex-shrink: 0;
  height: 18px;
  justify-content: center;
  margin-left: auto;
  transition: all 0.2s ease;
  width: 18px;
}

.tree-search-check-badge:hover {
  background: #e44366;
  box-shadow: 0 3px 8px rgba(255, 92, 120, 0.38);
  transform: scale(1.18);
}

.tree-search-check-badge .badge-check {
  font-size: 11px;
  font-weight: 800;
}

.tree-search-check-badge .badge-reset {
  display: none;
  font-size: 10px;
}

.tree-search-check-badge:hover .badge-check {
  display: none;
}

.tree-search-check-badge:hover .badge-reset {
  display: flex;
}

.tree-search-condensed-visual {
  align-items: stretch;
  background: rgba(255, 241, 244, 0.72);
  border: 1px dashed rgba(255, 92, 120, 0.35);
  border-radius: 9px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 9px;
  height: 93px;
  justify-content: center;
  margin: 10px 0 12px;
  padding: 10px 12px;
}

.tree-search-condensed-flow {
  align-items: center;
  color: var(--muted);
  display: flex;
  font-size: 10px;
  gap: 7px;
  justify-content: space-between;
}

.tree-search-condensed-flow b {
  color: var(--rose);
  font-size: 12px;
  font-weight: 400;
}

.tree-search-condensed-note {
  color: var(--rose);
  font-size: 10px;
  text-align: center;
}

.tree-search-condensed-takeaway {
  align-items: flex-start;
  display: flex;
  gap: 6px;
}

.tree-search-condensed-takeaway > span {
  color: var(--rose);
  font-size: 14px;
  font-weight: 800;
  line-height: 1.1;
}

/* Embedded reverse page, following Card 01's full-slide overlay pattern. */
.tree-search-card-back-overlay {
  animation: treeSearchOverlayFade .3s ease-out forwards;
  backdrop-filter: blur(14px);
  background: rgba(255, 255, 255, .96);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  height: 100%;
  left: 0;
  padding: 30px 48px 22px;
  perspective: 1200px;
  position: absolute;
  top: 0;
  width: 100%;
  z-index: 100;
}

.tree-search-card-back-overlay.is-closing {
  animation: treeSearchOverlayFadeOut .35s ease-in forwards;
}

@keyframes treeSearchOverlayFade {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes treeSearchOverlayFadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

.tree-search-card-back-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  transform-style: preserve-3d;
  animation: treeSearchFlipIn .42s cubic-bezier(.16, 1, .3, 1) forwards;
}

.tree-search-card-back-inner.inner-closing {
  animation: treeSearchFlipOut .35s cubic-bezier(.7, 0, .84, 0) forwards;
}

@keyframes treeSearchFlipIn {
  0% { opacity: 0; transform: perspective(1200px) rotateY(-85deg) scale(.9); }
  65% { transform: perspective(1200px) rotateY(6deg) scale(1.01); }
  100% { opacity: 1; transform: perspective(1200px) rotateY(0deg) scale(1); }
}

@keyframes treeSearchFlipOut {
  0% { opacity: 1; transform: perspective(1200px) rotateY(0deg) scale(1); }
  100% { opacity: 0; transform: perspective(1200px) rotateY(80deg) scale(.9); }
}

.tree-search-card-back-header {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 2px;
}

.tree-search-card-back-kicker {
  align-items: center;
  display: inline-flex;
  gap: 7px;
  margin-bottom: 0;
}

.tree-search-card-back-tag {
  align-items: center;
  background: rgba(255, 92, 120, .10);
  border: 1px solid rgba(255, 92, 120, .28);
  border-radius: 999px;
  color: var(--rose);
  display: inline-flex;
  font-size: 10px;
  font-weight: 700;
  gap: 4px;
  letter-spacing: .8px;
  padding: 2px 8px;
}

.tree-search-kicker-sep {
  color: rgba(255, 92, 120, .6);
}

.tree-search-back-actions {
  align-items: center;
  display: flex;
  gap: 8px;
}

.tree-search-reset-btn,
.tree-search-condense-btn {
  align-items: center;
  background: #ffffff;
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

.tree-search-reset-btn { color: var(--muted); }
.tree-search-condense-btn { color: var(--body); gap: 6px; padding: 4px 11px; }
.tree-search-condense-btn .tree-search-check-mark { color: var(--rose); font-weight: 700; }

.tree-search-reset-btn:hover,
.tree-search-condense-btn:hover {
  background: rgba(255, 241, 244, .75);
  border-color: var(--rose);
  color: var(--rose);
}

.tree-search-back-claim {
  color: var(--ink);
  display: flex;
  flex-direction: column;
  font-size: 32px;
  font-weight: 500;
  letter-spacing: -1.1px;
  line-height: 1.08;
  margin-top: 24px;
}

.tree-search-back-claim strong {
  color: var(--rose);
  font-weight: 600;
}

.tree-search-back-claim-shift {
  color: var(--muted);
  font-size: 18px;
  font-weight: 400;
  letter-spacing: -.25px;
  margin-left: 24px;
  margin-top: 7px;
}

.tree-search-evidence-grid {
  display: grid;
  gap: 42px;
  grid-template-columns: 1fr 1fr;
  margin-top: 31px;
}

.tree-search-evidence-block {
  border-top: 2px solid var(--rose);
  padding-top: 12px;
}

.tree-search-ablation-block { border-top-color: #b6bcc4; }

.tree-search-evidence-kicker {
  color: var(--muted);
  font-size: 10px;
  letter-spacing: 1px;
}

.tree-search-evidence-block h2 {
  color: var(--ink);
  font-size: 20px;
  font-weight: 500;
  letter-spacing: -.75px;
  line-height: 1.1;
  margin: 11px 0 0;
}

.tree-search-evidence-block h2 strong {
  display: block;
  color: var(--rose);
  font-size: 46px;
  font-weight: 500;
  line-height: 1.1;
  margin-bottom: 8px;
}

.tree-search-ablation-block h2 strong { color: var(--ink); }

.tree-search-bar-chart {
  margin-top: 27px;
}

.tree-search-chart-row {
  align-items: center;
  display: grid;
  gap: 12px;
  grid-template-columns: 94px 1fr 65px;
  margin-top: 12px;
}

.tree-search-chart-label {
  color: var(--muted);
  font-size: 11px;
  white-space: nowrap;
}

.tree-search-chart-bar {
  background: #f1f3f5;
  height: 16px;
  position: relative;
}

.tree-search-chart-bar i {
  background: var(--rose);
  display: block;
  height: 100%;
  width: 100%;
}

.tree-search-chart-write .tree-search-chart-bar i {
  background: #bec3c8;
  width: 12%;
}

.tree-search-chart-reuse .tree-search-chart-bar i {
  background: #bec3c8;
  width: 22%;
}

.tree-search-chart-row strong {
  color: var(--body);
  font-size: 12px;
  font-weight: 500;
  text-align: right;
}

.tree-search-evidence-block p {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.35;
  margin: 22px 0 0;
  max-width: 94%;
}

.tree-search-ablation-callout {
  align-items: baseline;
  display: flex;
  gap: 13px;
  margin-top: 21px;
}

.tree-search-ablation-callout strong {
  color: var(--rose);
  font-family: 'Fira Code', monospace;
  font-size: 27px;
  font-weight: 500;
}

.tree-search-ablation-callout span {
  color: var(--muted);
  font-size: 13px;
}

.tree-search-cost-comparison {
  align-items: center;
  border-bottom: 1px solid var(--line);
  border-top: 1px solid var(--line);
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr 34px 1fr;
  margin-top: 31px;
  padding: 16px 0;
}

.tree-search-cost-method {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tree-search-cost-method strong {
  color: var(--ink);
  font-size: 19px;
  font-weight: 500;
  line-height: 1.25;
}

.tree-search-cost-method span {
  color: var(--body);
  font-size: 15px;
}

.tree-search-cost-repeat strong { color: #c43b59; }
.tree-search-cost-vs { color: var(--muted); font-size: 13px; text-align: center; }

.tree-search-evidence-footnote {
  align-items: flex-end;
  color: #8d949c;
  display: flex;
  font-size: 9px;
  justify-content: space-between;
  letter-spacing: .15px;
  line-height: 1.25;
  margin-top: auto;
  padding-top: 13px;
}

.tree-search-evidence-footnote span:last-child {
  text-align: right;
}
</style>
