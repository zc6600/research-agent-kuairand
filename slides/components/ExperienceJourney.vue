<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useSlideContext } from '@slidev/client'
import ExecutionDiagram from './ExecutionDiagram.vue'
import narrationTimeline from '../../video/experience-journey-delivery/subtitle-cues.json'

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
  { title: 'Start your journey.', detail: 'Set the research question and your working constraints.' },
  { title: 'One step.', detail: 'Run one research cycle. Review the evidence before continuing.' },
  { title: 'Let it run.', detail: 'Continue across cycles, with a fresh Scientist each time.' },
  { title: 'Now, explore wider.', detail: 'Explore independent branches, then review what to keep.' },
  { title: 'See what stays.', detail: 'Inspect the retained result and the evidence behind it.' },
  { title: 'Already in your workflow.', detail: 'Use the research-agent skill inside your coding agent.' },
]
type SubtitleCue = { id: string; start: number; end: number; text: string }
const subtitleCues: SubtitleCue[] = narrationTimeline.cues.map(cue => ({
  id: cue.id, start: cue.start * 1000, end: cue.end * 1000, text: cue.text,
}))
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
const subtitle = computed(() => {
  if (staticView.value || reduced.value) return null
  return subtitleCues.find(cue => elapsed.value >= cue.start && elapsed.value < cue.end) ?? null
})
const isOutro = computed(() => elapsed.value >= outroStart)
const isBrand = computed(() => !staticView.value && (elapsed.value < introDuration || isOutro.value))
const sceneOpacity = computed(() => reduced.value || staticView.value ? 1
  : easeInOut(time.value / 750) * (1 - easeInOut((time.value - operationDurations[act.value] + 500) / 500)))
const sceneNames = ['Research brief', 'One research cycle', 'Continuous research', 'Parallel exploration', 'Retained evidence', 'Your coding agent']
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
    borderRadius: `${28 * (1 - p)}px`,
    boxShadow: `0 ${24 * (1 - p)}px ${80 * (1 - p)}px rgba(35, 53, 76, ${.12 * (1 - p)})`,
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
  [[0, 434, 175, 1], [1700, 434, 175, 1], [3000, 434, 175, 1.035], [6500, 434, 175, 1.035], [8500, 434, 180, 1.035], [12600, 434, 180, 1.035], [14500, 434, 175, 1]],
  [[0, 434, 125, 1.02], [2300, 434, 125, 1.02], [4000, 434, 188, .98], [10000, 434, 188, .98], [11200, 434, 185, .98]],
  [[0, 434, 125, 1.02], [2300, 434, 125, 1.02], [4000, 434, 188, .98], [12000, 434, 188, .98], [13200, 434, 185, .98]],
  [[0, 434, 125, 1.02], [2300, 434, 125, 1.02], [4200, 434, 185, .98], [14000, 434, 185, .98], [15000, 434, 185, .98]],
  [[0, 434, 175, 1], [2200, 434, 175, 1], [4400, 434, 180, 1.015], [13000, 434, 180, 1.015], [15000, 434, 180, 1]],
  [[0, 434, 180, .985], [2600, 434, 180, 1], [14000, 434, 180, 1]],
]
const camera = computed(() => {
  if (reduced.value || staticView.value) return { transform: 'translate(56px, 15px)' }
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
      <div class="chapter-label">05 / USER EXPERIENCE</div>
      <h1>Autonomous by default.<br><span>Supervisable by design.</span></h1>
    </div>
    <div class="terminal-shell" :style="shellStyle">
    <div v-if="isBrand" class="brand-scene">
      <div class="brand-rule" :style="{ transform: `scaleX(${revealBrand(250)})`, opacity: revealBrand(250) }" aria-hidden="true" />
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
    </div>
    <template v-else>
    <div v-if="!showingPurpose" class="scene-heading" :style="{ opacity: sceneOpacity }"><span class="scene-heading-index">{{ String(act + 1).padStart(2, '0') }}</span><span>{{ purposes[act].title }}</span><small>{{ sceneNames[act] }}</small></div>
    <div class="journey-stage">
      <div v-if="showingPurpose" class="purpose-scene" :style="purposeStyle">
        <div class="purpose-index">{{ String(act + 1).padStart(2, '0') }} <span>/</span> {{ sceneNames[act] }}</div>
        <h2>{{ purposes[act].title }}</h2>
        <p :style="{ opacity: easeInOut((actTime - 650) / 800) }">{{ purposes[act].detail }}</p>
      </div>
      <div v-else class="camera-world" :style="{ ...camera, opacity: sceneOpacity }">
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
              <pre><code><span v-for="(line, index) in vimLines" :key="`${vimFile}-${index}`" class="vim-line" :class="{ 'vim-heading': line.startsWith('#'), 'vim-current': index === vimLines.length - 1 }"><span>{{ line }}</span><span v-if="index === vimLines.length - 1 && time < (vimFile === 'task.md' ? 6500 : 12700)" class="vim-cursor">▎</span></span></code></pre>
            </div>
            <div class="vim-statusline"><span>{{ vimStatusMode }}</span><span>{{ vimFile }} · utf-8 · md</span></div>
            <div class="vim-commandline"><span>{{ vimMode === ':w' ? ':w' : '' }}</span><span class="vim-hint">{{ time < 7400 ? 'i  insert' : time < 13300 ? ':w  save' : 'brief ready' }}</span></div>
          </div>
          <div class="brief-ready" :style="{ opacity: progress(13500, 600) }"><span>✓</span> Both files saved <i /> ready for the agent</div>
        </div>

        <div v-else-if="act > 0 && act < 4" :key="act" class="execution">
          <div class="command-terminal">
            <div class="terminal-dots" aria-hidden="true"><i /><i /><i /><span>Terminal</span><small>~/sci-odyssey</small></div>
            <div class="command-line"><span class="prompt">❯</span><code><span class="command-path">{{ typed(command, 450, 38).slice(0, 25) }}</span><span class="command-verb">{{ typed(command, 450, 38).slice(25) }}</span><span v-if="time > 1700"> \</span></code><span v-if="time < 1700" class="cursor">▎</span></div>
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
            <img src="/assets/dashboard-result.png" class="dash-img" alt="Dashboard: retained validation result" />
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
            <div class="skill-response" :style="skillReveal(7500)"><span>✳</span><div>Research workflow, connected.<small>Task, memory and evidence stay with the project.</small></div></div>
            <div class="skill-files" :style="skillReveal(10500)">task.md <i /> research_record/ <i /> system/</div>
          </div>
        </div>
      </Transition>
      </div>
    </div>
    </template>
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
          @click.stop="selectAct(i)"
        />
      </div>
      <div class="controls-divider" aria-hidden="true" />
      <button class="playback" :aria-label="playing ? 'Pause demonstration' : 'Play demonstration'" @click.stop="toggle">{{ playing ? 'Ⅱ' : '▶' }}</button>
      <button class="playback" aria-label="Replay demonstration" @click.stop="replay">↺</button>
    </nav>
    <Transition name="subtitle-fade" mode="out-in">
      <div v-if="subtitle" :key="subtitle.id" class="journey-subtitle" aria-live="polite">{{ subtitle.text }}</div>
    </Transition>
    <div class="film-progress" aria-hidden="true"><span :style="{ transform: `scaleX(${elapsed / total})` }" /></div>
    <div v-if="isOutro" class="chapter-exit" :style="{ opacity: 1 - expansion }">
      <button @click.stop="replay">↺ Replay UX</button>
      <button class="continue-button" @click.stop="$nav.nextSlide()">Summary <span>→</span></button>
    </div>
  </section>
</template>

<style scoped>
.experience-journey { --ux-ink: #20242b; --ux-muted: #7b828d; --ux-blue: #298bb6; --ux-line: #e5e9ee; --ux-font: var(--demo-sans); position: absolute; inset: 0; color: var(--ux-ink); overflow: hidden; font-family: var(--ux-font); font-weight: 400; -webkit-font-smoothing: antialiased; background: radial-gradient(ellipse at 12% 0%, #e4effb, transparent 66%), radial-gradient(ellipse at 100% 100%, #fcf4e5, transparent 60%), #fafbfd; }
.experience-journey *, .experience-journey *::before, .experience-journey *::after { box-sizing: border-box; }
.experience-journey::before { content: ''; position: absolute; inset: 0; background: #fcfdfe; opacity: var(--immersion); }
.chapter-card { position: absolute; top: 40px; left: 56px; right: 56px; text-align: center; }
.chapter-label { color: #be814c; font-size: 11px; font-weight: 600; letter-spacing: 2.6px; }
.chapter-card h1 { margin: 20px 0 8px !important; font-size: 34px; font-weight: 550; line-height: 1.24; letter-spacing: -1px; }
.chapter-card h1 span { color: #8a9099; }
.terminal-shell { position: absolute; top: 0; left: 0; width: 980px; height: 551.25px; transform-origin: 0 0; overflow: hidden; will-change: transform; background: #fcfdfe; }
.brand-scene { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; background: radial-gradient(ellipse at 50% 45%, #edf5fb65, transparent 60%), #fcfdfe; }
.brand-rule { position: absolute; top: 118px; width: 34px; height: 2px; border-radius: 2px; background: #7cbbd6; }
.brand-copy { text-align: center; margin-top: 151px; }
.brand-copy h1 { color: #20242b; font-size: 67px; font-weight: 600; letter-spacing: -3.4px; line-height: 1.1; margin: 0 !important; }
.brand-copy p { font-size: 22px; font-weight: 400; color: #7c838d; margin: 19px 0 0; letter-spacing: -.55px; }
.harness-row { position: absolute; top: 334px; display: flex; align-items: center; gap: 23px; padding-top: 20px; border-top: 1px solid #e8edf2; }
.harness-label { font-size: 11px; color: #8a929d; margin-right: 3px; }
.harness { display: flex; align-items: center; gap: 7px; font-size: 11px; font-weight: 500; color: #69727e; }
.harness-icon, .harness-icon img { width: 17px; height: 17px; }
.harness-icon { display: grid; place-items: center; }
.harness-icon img { object-fit: contain; }
.brand-caption { position: absolute; top: 433px; color: #89929e; font-size: 11px; letter-spacing: .15px; }
.scene-heading { position: absolute; top: 31px; left: 56px; right: 56px; display: flex; align-items: center; gap: 11px; font-size: 16px; font-weight: 500; letter-spacing: -.3px; }
.scene-heading-index { font: 10px var(--deck-mono); color: var(--ux-blue); }
.scene-heading small { margin-left: auto; font-size: 10px; font-weight: 400; letter-spacing: .3px; color: #8e97a3; }
.journey-stage { position: absolute; top: 76px; left: 0; right: 0; height: 420px; overflow: hidden; }
.purpose-scene { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 56px 51px; }
.purpose-index { margin-bottom: 24px; font-size: 10px; font-weight: 500; letter-spacing: 1.4px; text-transform: uppercase; color: #668fa6; }
.purpose-index span { margin: 0 10px; color: #c9d3dc; }
.purpose-scene h2 { margin: 0 !important; font-size: 53px; font-weight: 550; line-height: 1.15; letter-spacing: -2.3px; }
.purpose-scene p { margin: 22px 0 0; max-width: 640px; color: #818994; font-size: 20px; font-weight: 400; line-height: 1.55; letter-spacing: -.4px; }
.camera-world { position: absolute; top: 0; left: 0; width: 868px; min-height: 300px; transform-origin: 0 0; will-change: transform, opacity; }
.editors { padding: 7px 66px 0; }
.vim-editor { height: 315px; border: 1px solid #dfe5eb; border-radius: 12px; overflow: hidden; background: #fff; color: #465260; font: 14px/1.8 var(--deck-mono); box-shadow: 0 12px 36px #23354c0a, 0 2px 4px #23354c03; }
.vim-tabline { height: 36px; display: flex; align-items: center; gap: 12px; padding: 0 16px; background: #f7f9fb; border-bottom: 1px solid #e6ebf0; color: #8c99a8; font-size: 11px; }
.vim-tabline span { padding: 9px 9px 8px; border-bottom: 2px solid transparent; }
.vim-tabline span.active { color: #317f9f; border-color: #65afcd; background: #fff; }
.vim-tabline small { margin-left: auto; color: #99a3af; font-size: 9px; }
.vim-buffer { display: grid; grid-template-columns: 48px 1fr; height: 222px; overflow: hidden; }
.vim-gutter { padding: 15px 12px 0 0; text-align: right; color: #b2bdc8; user-select: none; border-right: 1px solid #f0f3f6; }
.vim-gutter span, .vim-line { display: block; min-height: 25px; }
.vim-buffer pre { margin: 0; padding: 15px 18px; white-space: pre-wrap; background: transparent !important; overflow: hidden; font: inherit; }
.vim-buffer code { background: none; font: inherit; }
.vim-line { white-space: pre; }
.vim-heading { color: #42839e; }
.vim-current { background: #f5f9fc; }
.vim-cursor { color: #428fad; animation: caret 1s steps(1) infinite; }
.vim-statusline { height: 27px; display: flex; align-items: center; justify-content: space-between; padding: 0 14px; background: #edf3f7; color: #6b8496; font-size: 9px; border-top: 1px solid #e3eaf0; }
.vim-commandline { height: 28px; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; color: #566273; font-size: 10px; }
.vim-hint { color: #96a2af; }
.experience-journey .cursor { display: inline-block; color: #428fad; animation: caret 1s steps(1) infinite; }
.brief-ready { display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 11px; color: #7b8997; margin-top: 18px; }
.brief-ready > span { color: #359e89; }
.brief-ready i { width: 3px; height: 3px; background: #c2cdd6; border-radius: 50%; }
.command-terminal { padding: 0 23px 17px; border: 1px solid #dce3ea; border-radius: 12px; background: #fff; box-shadow: 0 10px 30px #23354c08, 0 2px 3px #23354c03; }
.terminal-dots { display: flex; align-items: center; gap: 6px; height: 33px; margin: 0 -23px 9px; padding: 0 16px; background: #f8fafb; border-bottom: 1px solid #e9edf2; border-radius: 12px 12px 0 0; }
.terminal-dots i { width: 6px; height: 6px; border: 1px solid #c3cdd7; border-radius: 50%; background: transparent; }
.terminal-dots span { margin-left: 9px; color: #7e8b99; font-size: 10px; }
.terminal-dots small { margin-left: auto; color: #9aa5b1; font: 9px var(--deck-mono); }
.command-line { display: flex; align-items: center; gap: 13px; min-height: 37px; }
.command-line code { font: 24px var(--deck-mono); letter-spacing: -.8px; color: #8f9ba8; background: none; }
.command-path { color: #465260; }
.command-verb { color: #2887ac; font-weight: 600; }
.prompt { color: #549dbc; font-size: 26px; }
.command-options { min-height: 20px; font: 11px/1.7 var(--deck-mono); color: #83909e; padding-left: 29px; white-space: nowrap; }
.dashboard-journey { padding: 0 38px; display: flex; flex-direction: column; gap: 12px; }
.gui-terminal { padding: 0 16px 11px; }
.gui-terminal .terminal-dots { margin: 0 -16px 7px; }
.dash-command { display: flex; align-items: baseline; gap: 10px; font: 17px var(--deck-mono); color: #465260; }
.dash-command code { color: inherit; background: none; font: inherit; letter-spacing: -.5px; }
.dash-cmd-opts { font-size: 12px; color: #8794a2; }
.dash-window { border: 1px solid #dce4ea; border-radius: 11px; overflow: hidden; box-shadow: 0 12px 32px #23354c08; background: #fff; will-change: opacity, transform; }
.dash-bar { height: 29px; display: flex; align-items: center; gap: 8px; padding: 0 14px; background: #f8fafb; border-bottom: 1px solid #e8edf1; }
.dash-dot { width: 5px; height: 5px; border-radius: 50%; background: #47a58d; }
.dash-bar-title { font-size: 10px; color: #778592; flex: 1; }
.dash-bar-live { font: 9px var(--deck-mono); color: #67a591; }
.dash-img { display: block; width: 100%; height: 215px; object-fit: cover; object-position: center top; }
.skill-scene { margin: 0 12px; height: 374px; border: 1px solid #dfe5eb; border-radius: 12px; background: white; overflow: hidden; box-shadow: 0 12px 36px #23354c08; }
.agent-bar { height: 31px; border-bottom: 1px solid #e9edf2; background: #f8fafb; display: flex; align-items: center; justify-content: space-between; padding: 0 17px; color: #8793a0; font-size: 10px; }
.agent-bar small { font-size: 8px; letter-spacing: 1px; }
.agent-dots { display: flex; gap: 6px; width: 90px; }
.agent-dots i { width: 6px; height: 6px; border: 1px solid #c3cdd7; border-radius: 50%; }
.agent-body { position: relative; padding: 25px 42px; }
.skill-file { display: flex; align-items: center; gap: 13px; transform-origin: left top; }
.skill-file strong { font-size: 20px; font-weight: 500; letter-spacing: -.4px; }
.skill-file small { display: block; font-size: 11px; color: #929da9; margin-top: 3px; }
.skill-prompt { margin-top: 31px; min-height: 34px; font-size: 25px; letter-spacing: -.7px; }
.skill-request { margin-top: 8px; font-size: 25px; letter-spacing: -.8px; white-space: nowrap; }
.skill-response { display: flex; gap: 15px; margin-top: 32px; font-size: 20px; letter-spacing: -.4px; }
.skill-response > span { color: #5595af; font-size: 25px; }
.skill-response small { display: block; margin-top: 8px; color: #87939f; font-size: 14px; letter-spacing: -.15px; }
.skill-files { display: flex; align-items: center; gap: 15px; margin: 19px 0 0 37px; color: #94a0ac; font: 9px var(--deck-mono); }
.skill-files i { width: 32px; height: 1px; background: #c4dce7; }
.journey-controls { position: absolute; bottom: 17px; right: 28px; display: flex; align-items: center; gap: 10px; opacity: .25; transition: opacity .2s; z-index: 10; }
.journey-controls:hover, .journey-controls:focus-within, .paused .journey-controls { opacity: 1; }
.journey-controls button { border: 0; padding: 5px; font: 14px var(--ux-font); color: #8c98a5; background: transparent; cursor: pointer; }
.journey-controls button:focus-visible, .chapter-exit button:focus-visible { outline: 2px solid #65afcd; outline-offset: 4px; }
.act-dots { display: flex; align-items: center; gap: 9px; }
.journey-controls .act-dot { position: relative; width: 6px; height: 6px; border-radius: 9px; background: #bdc8d2; padding: 0; transition: width .25s, background .2s; }
.journey-controls .act-dot::before { content: ''; position: absolute; inset: -7px -4px; }
.journey-controls .act-dot:hover { background: #728a9d; }
.journey-controls .act-dot.active { width: 20px; background: #69abc7; }
.controls-divider { width: 1px; height: 12px; background: #dce3e9; margin: 0 2px; }
.chapter-exit { position: absolute; bottom: 21px; left: 56px; right: 56px; display: flex; justify-content: space-between; }
.chapter-exit button { border: 0; background: none; font: 11px var(--ux-font); color: #7c8a98; cursor: pointer; padding: 7px 0; }
.chapter-exit .continue-button { font-weight: 600; color: #3f4e5c; }
.continue-button span { margin-left: 12px; color: #be814c; }
.is-outro .journey-controls { right: 50%; transform: translateX(50%); }
.journey-subtitle { position: absolute; z-index: 11; left: 50%; bottom: 40px; width: min(780px, calc(100% - 112px)); margin: 0; padding: 9px 20px; border: 0; border-radius: 9px; background: transparent; box-shadow: none; color: #000; text-align: center; font-size: 17px; font-weight: 700; line-height: 1.35; letter-spacing: -.15px; white-space: normal; overflow-wrap: anywhere; transform: translateX(-50%); pointer-events: none; }
.subtitle-fade-enter-active, .subtitle-fade-leave-active { transition: opacity .18s ease, transform .18s ease; }
.subtitle-fade-enter-from, .subtitle-fade-leave-to { opacity: 0; transform: translateX(-50%) translateY(5px); }
.film-progress { position: absolute; bottom: 0; left: 0; right: 0; height: 2px; background: #e9eff4; }
.film-progress span { display: block; width: 100%; height: 100%; transform-origin: left; background: #8cbbcf; }
.scene-enter-active, .scene-leave-active { transition: opacity .4s, transform .4s cubic-bezier(.2,.7,.2,1); }
.scene-enter-from { opacity: 0; transform: translateY(10px); }
.scene-leave-to { opacity: 0; transform: translateY(-6px); }
@keyframes caret { 50% { opacity: 0; } }
.paused .cursor, .paused .vim-cursor { animation-play-state: paused; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition: none !important; animation: none !important; } }
@media print { .journey-controls, .film-progress { display: none; } }
</style>
