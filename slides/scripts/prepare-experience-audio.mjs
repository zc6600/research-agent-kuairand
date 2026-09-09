import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const componentPath = new URL('../components/ExperienceJourney.vue', import.meta.url)
const outputPath = new URL('../components/ExperienceJourneyAudio.vue', import.meta.url)
const sourceAudioPath = new URL('../../video/experience-journey-delivery/SciOdyssey_ExperienceJourney_aligned_voice.wav', import.meta.url)
const publicAudioPath = new URL('../public/media/experience-journey-voice.wav', import.meta.url)

function replaceRequired(source, from, to, label) {
  if (!source.includes(from)) {
    throw new Error(`Could not find ${label} while preparing ExperienceJourneyAudio.vue`)
  }
  return source.replace(from, to)
}

let source = await readFile(componentPath, 'utf8')

source = replaceRequired(
  source,
  `const elapsed = ref(0)\nconst playing = ref(true)\nconst reduced = ref(false)\nconst staticView = computed(() => $renderContext.value === 'print')`,
  `const elapsed = ref(0)\nconst playing = ref(false)\nconst awaitingStart = ref(true)\nconst audioAvailable = ref(true)\nconst narration = ref<HTMLAudioElement | null>(null)\nconst reduced = ref(false)\nconst staticView = computed(() => $renderContext.value === 'print')\nconst shouldUseNarration = computed(() => active.value && !staticView.value && !reduced.value && audioAvailable.value)`,
  'playback state block',
)

source = replaceRequired(
  source,
  `const selectAct = (index: number) => {\n  elapsed.value = introDuration + starts[index] + (reduced.value || staticView.value ? durations[index] - 1 : 0)\n  playing.value = !reduced.value && !staticView.value\n}\nconst replay = () => {\n  if (reduced.value || staticView.value) selectAct(0)\n  else { elapsed.value = 0; playing.value = true }\n}\nconst toggle = () => {\n  if (elapsed.value >= total) replay()\n  else playing.value = !playing.value\n}`,
  `const seekTo = (value: number) => {\n  const clamped = Math.max(0, Math.min(total, value))\n  elapsed.value = clamped\n  if (shouldUseNarration.value && narration.value) {\n    narration.value.currentTime = clamped / 1000\n  }\n}\nconst markAudioUnavailable = () => {\n  audioAvailable.value = false\n}\nconst syncFromNarration = () => {\n  if (!shouldUseNarration.value || !narration.value) return false\n  elapsed.value = Math.max(0, Math.min(total, narration.value.currentTime * 1000))\n  if (elapsed.value >= total) playing.value = false\n  return true\n}\nconst playNarration = async () => {\n  awaitingStart.value = false\n  if (!shouldUseNarration.value || !narration.value) {\n    playing.value = !reduced.value && !staticView.value\n    return\n  }\n  try {\n    narration.value.muted = false\n    narration.value.volume = 1\n    await narration.value.play()\n    playing.value = true\n  } catch (error) {\n    console.warn('Falling back to silent ExperienceJourney playback.', error)\n    audioAvailable.value = false\n    playing.value = !reduced.value && !staticView.value\n  }\n}\nconst pauseNarration = () => {\n  narration.value?.pause()\n  playing.value = false\n}\nconst selectAct = (index: number) => {\n  seekTo(introDuration + starts[index] + (reduced.value || staticView.value ? durations[index] - 1 : 0))\n  if (reduced.value || staticView.value) {\n    playing.value = false\n    return\n  }\n  void playNarration()\n}\nconst replay = () => {\n  if (reduced.value || staticView.value) {\n    selectAct(0)\n    return\n  }\n  seekTo(0)\n  void playNarration()\n}\nconst toggle = () => {\n  if (elapsed.value >= total) {\n    replay()\n    return\n  }\n  if (playing.value) pauseNarration()\n  else void playNarration()\n}\nconst resetToStart = () => {\n  narration.value?.pause()\n  seekTo(0)\n  playing.value = false\n  awaitingStart.value = !reduced.value && !staticView.value\n}\nconst handleNarrationEnded = () => {\n  elapsed.value = total\n  playing.value = false\n}`,
  'playback control block',
)

source = replaceRequired(
  source,
  `watch(active, (value) => { if (value) replay() })`,
  `watch(active, (value) => {\n  if (value) resetToStart()\n  else {\n    narration.value?.pause()\n    playing.value = false\n  }\n})`,
  'active slide watcher',
)

source = replaceRequired(
  source,
  `  if (staticView.value) selectAct(0)\n  const tick = (now: number) => {\n    if (previous && active.value && playing.value && !document.hidden && !staticView.value) {\n      elapsed.value = Math.min(total, elapsed.value + Math.max(0, Math.min(now - previous, 100)))\n      if (elapsed.value === total) playing.value = false\n    }`,
  `  if (staticView.value) selectAct(0)\n  narration.value?.addEventListener('ended', handleNarrationEnded)\n  const tick = (now: number) => {\n    if (previous && active.value && playing.value && !document.hidden && !staticView.value) {\n      if (!syncFromNarration()) {\n        elapsed.value = Math.min(total, elapsed.value + Math.max(0, Math.min(now - previous, 100)))\n      }\n      if (elapsed.value === total) playing.value = false\n    }`,
  'animation tick block',
)

source = replaceRequired(
  source,
  `onUnmounted(() => {\n  cancelAnimationFrame(frame)\n  media?.removeEventListener('change', updateMotion)\n})`,
  `onUnmounted(() => {\n  cancelAnimationFrame(frame)\n  narration.value?.pause()\n  narration.value?.removeEventListener('ended', handleNarrationEnded)\n  media?.removeEventListener('change', updateMotion)\n})`,
  'unmount cleanup block',
)

source = replaceRequired(
  source,
  `<section class="experience-journey" :class="{ paused: !playing, reduced, 'is-outro': isOutro, 'is-immersive': expansion > .99 }" :style="{ '--immersion': expansion }" aria-label="SciOdyssey product and research demonstration" @click.stop>`,
  `<section class="experience-journey" :class="{ paused: !playing, reduced, 'awaiting-start': awaitingStart, 'is-outro': isOutro, 'is-immersive': expansion > .99 }" :style="{ '--immersion': expansion }" aria-label="SciOdyssey product and research demonstration" @click.stop>\n    <audio ref="narration" src="/media/experience-journey-voice.wav" preload="auto" @error="markAudioUnavailable" />\n    <button v-if="awaitingStart && !staticView && !reduced" class="journey-start" type="button" @click.stop="replay">\n      <span>▶</span>\n      <strong>Start Experience</strong>\n      <small>{{ audioAvailable ? 'plays synchronized narration' : 'audio unavailable · silent preview' }}</small>\n    </button>`,
  'template root section',
)

source = replaceRequired(
  source,
  `@keyframes caret { 50% { opacity: 0; } }`,
  `.journey-start { position: absolute; inset: 0; z-index: 40; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; border: 0; background: radial-gradient(ellipse at 50% 42%, rgba(255,255,255,.82), rgba(252,253,254,.94) 58%, rgba(252,253,254,.98)); color: var(--ux-ink); cursor: pointer; font-family: var(--ux-font); }\n.journey-start span { display: grid; place-items: center; width: 74px; height: 74px; border: 1px solid #d9e5ec; border-radius: 999px; background: rgba(255,255,255,.92); box-shadow: 0 18px 48px rgba(35, 53, 76, .13); color: var(--ux-blue); font-size: 28px; padding-left: 4px; }\n.journey-start strong { display: block; font-size: 27px; font-weight: 550; letter-spacing: -.8px; }\n.journey-start small { color: #89929e; font-size: 12px; letter-spacing: .25px; }\n.awaiting-start .journey-controls { opacity: 1; }\n@keyframes caret { 50% { opacity: 0; } }`,
  'start overlay styles',
)

await mkdir(new URL('../public/media/', import.meta.url), { recursive: true })
await copyFile(sourceAudioPath, publicAudioPath)
await writeFile(outputPath, source.endsWith('\n') ? source : `${source}\n`)
console.log(`Prepared ${fileURLToPath(outputPath).replace(`${here}/../`, '')}`)
console.log(`Prepared ${fileURLToPath(publicAudioPath).replace(`${here}/../`, '')}`)
