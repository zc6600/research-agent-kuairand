<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useSlideContext } from '@slidev/client'
import ExecutionDiagram from './ExecutionDiagram.vue'

const { $page, $nav, $renderContext } = useSlideContext()
const active = computed(() => $page.value === $nav.value.currentSlideNo)
const purposeDuration = 3800
const operationDurations = [16000, 12000, 14000, 16000, 16000, 14000]
const durations = operationDurations.map(duration => duration + purposeDuration)
const starts = durations.map((_, index) => durations.slice(0, index).reduce((sum, duration) => sum + duration, 0))
const introDuration = 9000
const demoDuration = durations.reduce((sum, duration) => sum + duration, 0)
const outroStart = introDuration + demoDuration
const total = outroStart + 7400
const elapsed = ref(0)
const playing = ref(true)
const reduced = ref(false)
const staticView = computed(() => $renderContext.value === 'print')
const demoElapsed = computed(() => Math.max(0, Math.min(demoDuration, elapsed.value - introDuration)))
const act = computed(() => starts.findLastIndex(start => demoElapsed.value >= start))
const actTime = computed(() => demoElapsed.value - starts[act.value])
const time = computed(() => Math.max(0, actTime.value - purposeDuration))
const purposes = [
  { title: 'Make it yours.', detail: 'Set the research question and your working constraints.' },
  { title: 'One step.', detail: 'Run one research cycle. Review the evidence before continuing.' },
  { title: 'Let it run.', detail: 'Continue across cycles, with a fresh Scientist each time.' },
  { title: 'Now, explore wider.', detail: 'Explore independent branches, then review what to keep.' },
  { title: 'See what stays.', detail: 'Inspect the retained result and the evidence behind it.' },
  { title: 'Already in your workflow.', detail: 'Use the research-agent skill inside your coding agent.' },
]
const showingPurpose = computed(() => !staticView.value && !reduced.value && actTime.value < purposeDuration)
const purposeStyle = computed(() => ({
  opacity: easeInOut(actTime.value / 700) * (1 - easeInOut((actTime.value - 3100) / 700)),
  transform: `translateY(${(1 - easeInOut(actTime.value / 900)) * 18}px)`,
}))
const easeInOut = (value: number) => {
  const p = Math.max(0, Math.min(1, value))
  return p * p * p * (p * (p * 6 - 15) + 10)
}
const expansion = computed(() => {
  if (reduced.value || staticView.value) return 1
  return easeInOut((elapsed.value - 2400) / 1800) * (1 - easeInOut((elapsed.value - outroStart - 4600) / 2100))
})
const isOutro = computed(() => elapsed.value >= outroStart)
const isBrand = computed(() => !staticView.value && (elapsed.value < introDuration || isOutro.value))
const brandTime = computed(() => isOutro.value ? elapsed.value - outroStart : elapsed.value)
const revealBrand = (start: number) => easeInOut((brandTime.value - start) / 800)
const skillDock = computed(() => easeInOut((time.value - 500) / 1800))
const skillReveal = (start: number) => ({ opacity: easeInOut((time.value - start) / 800), transform: `translateY(${(1 - easeInOut((time.value - start) / 1000)) * 12}px)` })
const harnesses = [
  { name: 'Codex', icon: 'codex' },
  { name: 'Claude Code', icon: 'claude-color' },
  { name: 'OpenCode', icon: 'opencode' },
  { name: 'Antigravity', icon: 'antigravity-color' },
  { name: 'Trae', icon: 'trae-color' },
]
const shellStyle = computed(() => {
  const p = expansion.value
  return {
    transform: `translate(${245 * (1 - p)}px, ${225 * (1 - p)}px) scale(${.5 + .5 * p})`,
  }
})
const labels = ['Edit the brief', 'step', 'run', 'parallel', 'dashboard', 'skill']
const task = '# Research objective\nRank short videos for each user.\n\n# Evaluation\nKuaiRand-Pure · long_view\nPrimary = mean(GAUC, nDCG@5)'
const personal = '# Working preferences\nUse macOS / Apple Silicon + uv.\n\n# Constraints\n≤ 15 minutes per experiment.\nNever print credentials.'
const vimFile = computed(() => time.value < 7400 ? 'task.md' : 'PERSONAL.md')
const vimSource = computed(() => vimFile.value === 'task.md' ? task : personal)
const vimSourceStart = computed(() => vimFile.value === 'task.md' ? 700 : 7400)
const vimText = computed(() => typed(vimSource.value, vimSourceStart.value, 34))
const vimLines = computed(() => vimText.value.split('\n'))
const vimMode = computed(() => {
  if (time.value < 700) return '-- NORMAL --'
  if (time.value < 6500 || (time.value >= 7400 && time.value < 12700)) return '-- INSERT --'
  if (time.value < 7600 || (time.value >= 12700 && time.value < 13300)) return ':w'
  return `"${vimFile.value}" written`
})
const vimStatusMode = computed(() => time.value < 700 ? '-- NORMAL --' : time.value < 6500 || (time.value >= 7400 && time.value < 12700) ? '-- INSERT --' : '-- NORMAL --')
const command = computed(() => `./scripts/research-agent ${labels[act.value]}`)
const options = computed(() => act.value === 1
  ? '--cli codex --target ./project --allow-edits'
  : act.value === 2
    ? '--cli codex --target ./project --max-cycles 4 --allow-edits'
    : act.value === 3
      ? '--cli codex --target ./project --branches 3 --parallelism 3 --keep 1 --allow-edits'
      : act.value === 4
        ? '--target ./project'
        : '')
const typed = (text: string, start: number, speed = 30) => text.slice(0, Math.max(0, Math.floor((time.value - start) / speed)))
const progress = (start: number, duration: number) => Math.max(0, Math.min(1, (time.value - start) / duration))
// Camera poses are [time, focus-x, focus-y, zoom] in the shared scene canvas.
// Each move has a hold on either side so the audience can read the operation.
const cameraTracks = [
  // Keynote rhythm: enter on one readable subject, hold, then return to a composed wide view.
  [[0, 434, 150, 1], [1700, 434, 150, 1], [2700, 434, 165, 1.08], [6500, 434, 165, 1.08], [8200, 434, 178, 1.08], [12600, 434, 178, 1.08], [14500, 434, 150, 1]],
  [[0, 434, 85, 1.02], [2300, 434, 85, 1.02], [3700, 434, 155, 1.04], [9300, 434, 155, 1.04], [11200, 434, 145, 1]],
  [[0, 434, 85, 1.02], [2300, 434, 85, 1.02], [3700, 434, 155, 1.04], [10900, 434, 155, 1.04], [12800, 434, 145, 1]],
  [[0, 434, 85, 1.02], [2300, 434, 85, 1.02], [4000, 434, 175, 1.04], [11500, 434, 175, 1.04], [14000, 434, 155, 1]],
  [[0, 434, 140, 1], [2200, 434, 140, 1], [3600, 434, 160, 1.04], [13000, 434, 160, 1.04], [15000, 434, 140, 1]],
  [[0, 434, 150, 1], [14000, 434, 150, 1]],
]
const camera = computed(() => {
  if (reduced.value || staticView.value) return { transform: 'translate(56px, 34px)' }
  const track = cameraTracks[act.value]
  const next = track.findIndex(pose => pose[0] > time.value)
  const a = track[next < 0 ? track.length - 1 : Math.max(0, next - 1)]
  const b = next < 0 ? a : track[next]
  const p = a === b ? 1 : Math.max(0, Math.min(1, (time.value - a[0]) / (b[0] - a[0])))
  const ease = p * p * p * (p * (p * 6 - 15) + 10)
  const x = a[1] + (b[1] - a[1]) * ease
  const y = a[2] + (b[2] - a[2]) * ease
  const zoom = a[3] + (b[3] - a[3]) * ease
  return { transform: `translate(${490 - x * zoom}px, ${195 - y * zoom}px) scale(${zoom})` }
})
const selectAct = (index: number) => {
  elapsed.value = introDuration + starts[index] + (reduced.value || staticView.value ? durations[index] - 1 : 0)
  playing.value = !reduced.value && !staticView.value
}
const replay = () => {
  if (reduced.value || staticView.value) selectAct(0)
  else { elapsed.value = 0; playing.value = true }
}
const toggle = () => {
  if (elapsed.value >= total) replay()
  else playing.value = !playing.value
}
let frame = 0
let previous = 0
let media: MediaQueryList | undefined
const updateMotion = () => {
  reduced.value = media?.matches ?? false
  if (reduced.value) selectAct(act.value)
}
watch(active, (value) => { if (value) replay() })
onMounted(() => {
  media = window.matchMedia('(prefers-reduced-motion: reduce)')
  updateMotion()
  media.addEventListener('change', updateMotion)
  if (staticView.value) selectAct(0)
  const tick = (now: number) => {
    if (previous && active.value && playing.value && !document.hidden && !staticView.value) {
      elapsed.value = Math.min(total, elapsed.value + Math.max(0, Math.min(now - previous, 100)))
      if (elapsed.value === total) playing.value = false
    }
    previous = now
    frame = requestAnimationFrame(tick)
  }
  frame = requestAnimationFrame(tick)
})
onUnmounted(() => {
  cancelAnimationFrame(frame)
  media?.removeEventListener('change', updateMotion)
})
</script>

<template>
  <section class="experience-journey" :class="{ paused: !playing, reduced, 'is-outro': isOutro, 'is-immersive': expansion > .99 }" :style="{ '--immersion': expansion }" aria-label="SciOdyssey product and research demonstration" @click.stop>
    <div class="chapter-card" :style="{ opacity: 1 - expansion, transform: `translateY(${-24 * expansion}px)` }" :aria-hidden="expansion > .99">
      <div class="chapter-label">03 / USER EXPERIENCE</div>
      <h1>Autonomous by default.<br><span>Supervisable by design.</span></h1>
    </div>
    <div class="terminal-shell" :style="shellStyle">
    <div v-if="isBrand" class="brand-scene">
      <div class="brand-copy" :style="{ opacity: revealBrand(100), transform: `translateY(${(1 - revealBrand(100)) * 16}px)` }">
        <h1>SciOdyssey</h1>
        <p :style="{ opacity: revealBrand(850), transform: `translateY(${(1 - revealBrand(850)) * 12}px)` }">A research layer over your agent harness.</p>
      </div>
      <div v-if="expansion > 0" class="harness-row" aria-label="Supported agent harnesses" :style="{ opacity: easeInOut((expansion - .9) / .1) * revealBrand(isOutro ? 1500 : 4400) }">
        <span class="harness-label">Works with</span>
        <div v-for="harness in harnesses" :key="harness.name" class="harness">
          <div class="harness-icon"><img :src="`/assets/${harness.icon}.svg`" alt="" /></div>
          <span>{{ harness.name }}</span>
        </div>
      </div>
      <div class="brand-caption" :style="{ opacity: revealBrand(3200) }">Your agent. One persistent research world.</div>
    </div>
    <div v-else class="journey-stage">
      <div v-if="showingPurpose" class="purpose-scene" :style="purposeStyle">
        <h2>{{ purposes[act].title }}</h2>
        <p :style="{ opacity: easeInOut((actTime - 650) / 800) }">{{ purposes[act].detail }}</p>
      </div>
      <div v-else class="camera-world" :style="camera">
      <Transition name="scene" mode="out-in">
        <div v-if="act === 0" key="editor" class="editors">
          <div class="vim-editor">
            <div class="vim-tabline">
              <span :class="{ active: vimFile === 'task.md' }">task.md</span>
              <span :class="{ active: vimFile === 'PERSONAL.md' }">PERSONAL.md</span>
              <small>~/sci-odyssey</small>
            </div>
            <div class="vim-buffer">
              <div class="vim-gutter"><span v-for="(_, index) in vimLines" :key="index">{{ String(index + 1).padStart(2, ' ') }}</span></div>
              <pre><code><span v-for="(line, index) in vimLines" :key="`${vimFile}-${index}`" class="vim-line"><span>{{ line }}</span><span v-if="index === vimLines.length - 1 && time < (vimFile === 'task.md' ? 6500 : 12700)" class="vim-cursor">▎</span></span></code></pre>
            </div>
            <div class="vim-statusline"><span>{{ vimStatusMode }}</span><span>{{ vimFile }} · utf-8 · md</span></div>
            <div class="vim-commandline"><span>{{ vimMode === ':w' ? ':w' : '' }}</span><span class="vim-hint">{{ time < 7400 ? 'i  insert' : time < 13300 ? ':w  save' : 'brief ready' }}</span></div>
          </div>
          <div class="brief-ready" :style="{ opacity: progress(13500, 600) }">Both files saved · ready for the agent</div>
        </div>

        <div v-else-if="act > 0 && act < 4" :key="act" class="execution">
          <div class="command-terminal">
            <div class="terminal-dots" aria-hidden="true"><i /><i /><i /></div>
            <div class="command-line"><span class="prompt">❯</span><code>{{ typed(command, 450, 38) }}<span v-if="time > 1700"> \</span></code><span v-if="time < 1700" class="cursor">▎</span></div>
            <div class="command-options">{{ typed(options, 1700, 12) }}</div>
          </div>
          <ExecutionDiagram :act="act" :time="time" />
        </div>

        <div v-else-if="act === 4" key="dashboard" class="dashboard-journey">
          <div class="command-terminal gui-terminal" :style="{ opacity: progress(300, 400) }">
            <div class="terminal-dots" aria-hidden="true"><i /><i /><i /><span>Terminal</span></div>
            <div class="dash-command">
            <span class="prompt">❯</span>
            <code>{{ typed('./scripts/research-agent gui', 450, 42) }}</code>
            <span class="dash-cmd-opts">{{ typed('--target ./project', 1900, 14) }}</span>
            </div>
          </div>
          <div class="dash-window" :style="{ opacity: progress(3200, 900), transform: `translateY(${(1 - Math.min(1, Math.max(0, (time - 3200) / 900))) * 20}px)` }">
            <div class="dash-bar">
              <span class="dash-dot" /><span class="dash-bar-title">Research Agent Dashboard</span><span class="dash-bar-live">read-only</span>
            </div>
            <img src="/assets/dashboard-result.png" class="dash-img" alt="Dashboard: retained checkpoint S004, Primary 0.605936" />
          </div>
          <div class="dash-callout" :style="{ opacity: progress(9000, 700) }">
            <span class="dash-callout-check">✓</span> Retained checkpoint <strong>S004</strong> · Primary <strong class="dash-score">0.605936</strong> · evidence on record
          </div>
        </div>
        <div v-else key="skill" class="skill-scene">
          <div class="agent-bar"><div class="agent-dots"><i /><i /><i /></div><span>Coding agent</span><small>SKILL WORKFLOW</small></div>
          <div class="agent-body">
            <div class="skill-file" :style="{ opacity: progress(0, 500), transform: `translate(${220 * (1 - skillDock)}px, ${34 * (1 - skillDock)}px) scale(${1.4 - .4 * skillDock})` }">
              <svg width="25" height="32" viewBox="0 0 35 43" aria-hidden="true"><path d="M3 2 H22 L32 12 V40 H3 Z M22 2 V12 H32" fill="none" stroke="#428eae" stroke-width="2" /></svg>
              <div><strong>SKILL.md</strong><small>research-agent</small></div>
            </div>
            <div class="skill-prompt" :style="skillReveal(2800)">{{ typed('Use the research-agent skill.', 2900, 65) }}</div>
            <div class="skill-request" :style="skillReveal(5400)">Explore in parallel. Let me review what to keep.</div>
            <div class="skill-response" :style="skillReveal(7900)"><span>✳</span><div>Research workflow, connected.<small>Task, memory and evidence stay with the project.</small></div></div>
            <div class="skill-files" :style="skillReveal(10500)">task.md <i /> research_record/ <i /> system/</div>
          </div>
        </div>
      </Transition>
      </div>
    </div>
    </div>
    <!-- Act jump controls — outside terminal-shell so they're always visible -->
    <nav class="journey-controls" aria-label="Demonstration playback" @keydown.stop>
      <div class="act-dots" role="tablist" aria-label="Jump to act">
        <button
          v-for="(label, i) in ['edit', 'step', 'run', 'parallel', 'dashboard', 'skill']"
          :key="i"
          class="act-dot"
          :class="{ active: !isBrand && act === i }"
          :aria-label="`Jump to ${label}`"
          :title="label"
          role="tab"
          :aria-selected="!isBrand && act === i"
          @click="selectAct(i)"
        />
      </div>
      <div class="controls-divider" aria-hidden="true" />
      <button class="playback" :aria-label="playing ? 'Pause demonstration' : 'Play demonstration'" @click="toggle">{{ playing ? 'Ⅱ' : '▶' }}</button>
      <button class="playback" aria-label="Replay demonstration" @click="replay">↺</button>
    </nav>
    <div v-if="isOutro" class="chapter-exit" :style="{ opacity: 1 - expansion }">
      <button @click="replay">↺ Replay UX</button>
      <button class="continue-button" @click="$nav.nextSlide()">Evaluation <span>→</span></button>
    </div>
  </section>
</template>

<style scoped>
.experience-journey { position: absolute; inset: 0; color: #111217; overflow: hidden; background: radial-gradient(ellipse at 15% 5%, #e0edff, transparent 65%), radial-gradient(ellipse at 95% 90%, #fff4d1, transparent 65%), #fff; }
.experience-journey::before { content: ''; position: absolute; inset: 0; background: #fcfdff; opacity: var(--immersion); }
.chapter-card { position: absolute; top: 40px; left: 56px; right: 56px; text-align: center; }
.chapter-label { color: #ff873f; font-size: 15px; font-weight: 800; letter-spacing: 3px; }
.chapter-card h1 { margin: 14px 0 8px !important; font-size: 36px; line-height: 1.25; letter-spacing: -.8px; }
.chapter-card h1 span { color: #77808d; }
.brand-scene { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; padding-top: 43px; background: radial-gradient(ellipse at 50% 70%, #eaf2ff99, transparent 65%), #fcfdff; }
.brand-copy { text-align: center; margin-top: 100px; }
.brand-copy h1 { font-size: 66px; font-weight: 800; letter-spacing: -3px; line-height: 1.1; margin: 0 !important; }
.brand-copy p { font-size: 23px; color: #77808d; margin: 19px 0 0; letter-spacing: -.4px; }
.harness-row { position: absolute; top: 330px; display: flex; align-items: center; gap: 24px; }
.harness-label { font-size: 12px; color: #98a0ad; margin-right: 2px; }
.harness { display: flex; align-items: center; gap: 7px; font-size: 12px; font-weight: 600; color: #68717e; }
.harness-icon { width: 19px; height: 19px; display: grid; place-items: center; }
.harness-icon img { width: 19px; height: 19px; object-fit: contain; }
.brand-caption { position: absolute; top: 400px; color: #98a0ad; font-size: 12px; letter-spacing: .6px; }
.skill-scene { margin: 0 12px; height: 374px; border: 1px solid #e7e9ec; border-radius: 13px; background: white; overflow: hidden; box-shadow: 0 10px 30px #23354c06; font-family: 'Nunito', sans-serif; }
.agent-bar { height: 30px; border-bottom: 1px solid #eff0f2; background: #fcfcfd; display: flex; align-items: center; justify-content: space-between; padding: 0 17px; color: #a6aab0; font-size: 11px; }
.agent-bar small { font-size: 8px; letter-spacing: 1px; }
.agent-dots { display: flex; gap: 5px; width: 90px; }
.agent-dots i { width: 6px; height: 6px; border: 1px solid #d8dce1; border-radius: 50%; }
.agent-body { position: relative; padding: 26px 42px; }
.skill-file { display: flex; align-items: center; gap: 13px; transform-origin: left top; }
.skill-file strong { font-size: 20px; font-weight: 600; }
.skill-file small { display: block; font-size: 11px; color: #a1a5ac; margin-top: 2px; }
.skill-prompt { margin-top: 32px; min-height: 34px; font-size: 25px; letter-spacing: -.6px; }
.skill-request { margin-top: 8px; font-size: 25px; letter-spacing: -.7px; white-space: nowrap; }
.skill-response { display: flex; gap: 15px; margin-top: 34px; font-size: 20px; }
.skill-response > span { color: #5595af; font-size: 25px; }
.skill-response small { display: block; margin-top: 7px; color: #a1a5ac; font-size: 14px; }
.skill-files { display: flex; align-items: center; gap: 14px; margin: 18px 0 0 37px; color: #9ca7b1; font: 9px ui-monospace, monospace; }
.skill-files i { width: 3px; height: 3px; background: #b8c6ce; border-radius: 50%; }
.gui-terminal { padding: 10px 16px 12px; }
.gui-terminal .terminal-dots { align-items: center; margin-bottom: 4px; }
.gui-terminal .terminal-dots span { margin-left: 8px; font-size: 9px; color: #9aa4b2; }
.is-outro .journey-controls { right: 50%; transform: translateX(50%); }
.terminal-shell { position: absolute; top: 0; left: 0; width: 980px; height: 551.25px; transform-origin: 0 0; overflow: hidden; will-change: transform; }
.journey-stage { position: absolute; top: 45px; left: 0; right: 0; height: 450px; overflow: hidden; mask-image: linear-gradient(to bottom, transparent, black 3%, black 97%, transparent); }
.purpose-scene { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 56px 25px; }
.purpose-scene h2 { margin: 0 !important; font-size: 55px; font-weight: 700; line-height: 1.15; letter-spacing: -1.8px; }
.purpose-scene p { margin: 23px 0 0; max-width: 720px; color: #8b929c; font-size: 21px; line-height: 1.5; letter-spacing: -.3px; }
.camera-world { position: absolute; top: 0; left: 0; width: 868px; min-height: 300px; transform-origin: 0 0; will-change: transform; }
.editors { padding: 7px 72px 0; }
.vim-editor { height: 308px; background: #fbfcfe; color: #3d4755; font: 14px/1.8 ui-monospace, SFMono-Regular, Menlo, monospace; box-shadow: 0 20px 45px #23354c0d; }
.vim-tabline { height: 31px; display: flex; align-items: center; gap: 18px; padding: 0 16px; background: #eef2f7; border-bottom: 1px solid #dfe5ed; color: #95a0ae; font-size: 11px; }
.vim-tabline span { padding: 4px 8px 5px; }
.vim-tabline span.active { color: #111217; background: #fbfcfe; }
.vim-tabline small { margin-left: auto; color: #a0a9b6; font-size: 10px; }
.vim-buffer { display: grid; grid-template-columns: 52px 1fr; height: 219px; overflow: hidden; }
.vim-gutter { padding: 15px 12px 0 0; text-align: right; color: #a1aab6; user-select: none; border-right: 1px solid #edf0f4; }
.vim-gutter span, .vim-line { display: block; min-height: 25px; }
.vim-buffer pre { margin: 0; padding: 15px 20px; white-space: pre-wrap; background: transparent !important; overflow: hidden; }
.vim-buffer code { background: none; font: inherit; }
.vim-line { white-space: pre; }
.vim-cursor { color: #38bdf8; animation: caret .8s steps(1) infinite; }
.vim-statusline { height: 27px; display: flex; align-items: center; justify-content: space-between; padding: 0 14px; background: #394655; color: #fff; font-size: 10px; }
.vim-commandline { height: 31px; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; color: #566273; font-size: 11px; }
.vim-hint { color: #9aa4b2; }
.cursor { color: #38bdf8; animation: caret .8s steps(1) infinite; }
.brief-ready { text-align: center; font: 11px ui-monospace, monospace; color: #87909d; margin-top: 18px; }
.command-terminal { padding: 15px 23px 17px; border: 1px solid #c3ccd8; border-radius: 11px; background: #fff; box-shadow: 0 10px 30px #23354c0a; }
.terminal-dots { display: flex; gap: 6px; margin-bottom: 10px; }
.terminal-dots i { width: 7px; height: 7px; border-radius: 50%; background: #ff6058; }
.terminal-dots i:nth-child(2) { background: #ffbd2e; }
.terminal-dots i:nth-child(3) { background: #28c840; }
.command-line { display: flex; align-items: center; gap: 13px; min-height: 45px; }
.command-line code { font: 25px ui-monospace, monospace; letter-spacing: -.8px; color: #111217; background: none; }
.prompt { color: #38bdf8; font-size: 30px; }
.command-options { min-height: 20px; font: 11px/1.7 ui-monospace, monospace; color: #7d8590; padding-left: 29px; white-space: nowrap; }
.journey-controls { position: absolute; bottom: 18px; right: 24px; display: flex; align-items: center; gap: 8px; opacity: 0.55; transition: opacity .2s; z-index: 10; }
.journey-controls:hover, .journey-controls:focus-within, .paused .journey-controls { opacity: 1; }
.journey-controls button { border: 0; padding: 5px; font: 16px 'Nunito', sans-serif; color: #87909c; background: transparent; cursor: pointer; }
.journey-controls button:focus-visible, .chapter-exit button:focus-visible { outline: 2px solid #38bdf8; outline-offset: 3px; }
.act-dots { display: flex; align-items: center; gap: 7px; }
.journey-controls .act-dot { width: 8px; height: 8px; border-radius: 50%; background: #c8d0da; border: 0; padding: 0; cursor: pointer; transition: background .2s, transform .15s; flex-shrink: 0; }
.journey-controls .act-dot:hover { background: #8a96a8; transform: scale(1.3); }
.journey-controls .act-dot.active { background: #38bdf8; transform: scale(1.25); }
.controls-divider { width: 1px; height: 14px; background: #d4dae2; margin: 0 2px; }
.chapter-exit { position: absolute; bottom: 23px; left: 56px; right: 56px; display: flex; justify-content: space-between; }
.chapter-exit button { border: 0; background: none; font: 12px 'Nunito', sans-serif; color: #788596; cursor: pointer; padding: 7px 0; }
.chapter-exit .continue-button { font-weight: 800; color: #111217; }
.continue-button span { margin-left: 14px; color: #ff873f; }
.scene-enter-active, .scene-leave-active { transition: opacity .4s, transform .4s cubic-bezier(.2,.7,.2,1); }
.scene-enter-from { opacity: 0; transform: translateY(18px) scale(.98); }
.scene-leave-to { opacity: 0; transform: translateY(-12px) scale(1.015); }
@keyframes caret { 50% { opacity: 0; } }
.paused .cursor { animation-play-state: paused; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition: none !important; animation: none !important; } }
@media print { .journey-controls { display: none; } }
/* Act 4 – dashboard journey */
.dashboard-journey { padding: 10px 56px 0; display: flex; flex-direction: column; gap: 10px; }
.dash-command { display: flex; align-items: baseline; gap: 10px; font: 18px ui-monospace, monospace; color: #111217; will-change: opacity; }
.dash-command code { color: #111217; background: none; font: inherit; letter-spacing: -.5px; }
.dash-cmd-opts { font-size: 13px; color: #7d8590; }
.dash-window { border: 1px solid #dce2ea; border-radius: 10px; overflow: hidden; box-shadow: 0 8px 32px #23354c10; background: #fff; will-change: opacity, transform; }
.dash-bar { height: 32px; display: flex; align-items: center; gap: 9px; padding: 0 14px; background: #f4f6f9; border-bottom: 1px solid #e4e8ef; }
.dash-dot { width: 8px; height: 8px; border-radius: 50%; background: #20b68d; flex-shrink: 0; }
.dash-bar-title { font: 11px 'Nunito', sans-serif; color: #3d4755; flex: 1; }
.dash-bar-live { font: 10px ui-monospace, monospace; color: #20b68d; border: 1px solid #20b68d44; border-radius: 4px; padding: 2px 6px; }
.dash-img { display: block; width: 100%; height: 225px; object-fit: cover; object-position: center top; }
.dash-callout { font: 12px 'Nunito', sans-serif; color: #698075; display: flex; align-items: center; gap: 6px; }
.dash-callout-check { color: #20b68d; font-size: 14px; font-weight: 800; }
.dash-callout strong { color: #3d4755; }
.dash-score { color: #269b7d !important; }
</style>
