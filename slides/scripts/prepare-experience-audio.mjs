import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
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

const audioVersion = createHash('sha256').update(await readFile(sourceAudioPath)).digest('hex').slice(0, 12)
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
  `let playbackRequest = 0
let pendingSeek: number | null = null
const applyPendingSeek = () => {
  const audio = narration.value
  if (pendingSeek === null || !audio || audio.readyState === 0) return
  audio.currentTime = pendingSeek / 1000
  pendingSeek = null
}
const seekTo = (value: number) => {
  elapsed.value = Math.max(0, Math.min(total, value))
  pendingSeek = elapsed.value
  applyPendingSeek()
}
const markAudioUnavailable = () => {
  audioAvailable.value = false
}
const syncFromNarration = () => {
  if (!shouldUseNarration.value || !narration.value) return false
  applyPendingSeek()
  if (pendingSeek !== null) return true
  elapsed.value = Math.max(0, Math.min(total, narration.value.currentTime * 1000))
  if (elapsed.value >= total) playing.value = false
  return true
}
const playNarration = async () => {
  if (!active.value || reduced.value || staticView.value) return
  const request = ++playbackRequest
  awaitingStart.value = false
  playing.value = true
  if (!shouldUseNarration.value || !narration.value) return
  try {
    applyPendingSeek()
    narration.value.muted = false
    narration.value.volume = 1
    await narration.value.play()
    if (request !== playbackRequest) return
    playing.value = active.value && !reduced.value && !staticView.value
  } catch (error) {
    if (request !== playbackRequest) return
    // Pausing/seeking during play() is cancellation, not a failed audio asset.
    if (error instanceof DOMException && error.name === 'AbortError') {
      playing.value = false
      return
    }
    if (error instanceof DOMException && error.name === 'NotAllowedError') {
      playing.value = false
      awaitingStart.value = true
      return
    }
    console.warn('Falling back to silent ExperienceJourney playback.', error)
    markAudioUnavailable()
  }
}
const pauseNarration = () => {
  playbackRequest++
  narration.value?.pause()
  syncFromNarration()
  playing.value = false
}
const selectAct = (index: number) => {
  pauseNarration()
  seekTo(introDuration + starts[index] + (reduced.value || staticView.value ? durations[index] - 1 : 0))
  if (!reduced.value && !staticView.value) void playNarration()
}
const replay = () => {
  if (reduced.value || staticView.value) {
    selectAct(0)
    return
  }
  pauseNarration()
  seekTo(0)
  void playNarration()
}
const toggle = () => {
  if (elapsed.value >= total) replay()
  else if (playing.value) pauseNarration()
  else void playNarration()
}
const resetToStart = () => {
  pauseNarration()
  seekTo(0)
  awaitingStart.value = !reduced.value && !staticView.value
}
const handleNarrationEnded = () => {
  playbackRequest++
  elapsed.value = total
  playing.value = false
}
const handleNarrationPause = () => {
  syncFromNarration()
  playing.value = false
}
const handleVisibilityChange = () => {
  if (document.hidden) pauseNarration()
}
const handleJourneyClick = () => {
  if (staticView.value || reduced.value) return
  if (awaitingStart.value || elapsed.value >= total) replay()
  else toggle()
}`,
  'playback control block',
)

source = replaceRequired(
  source,
  `watch(active, (value) => { if (value) replay() })`,
  `watch(active, (value) => {\n  if (value) resetToStart()\n  else pauseNarration()\n})`,
  'active slide watcher',
)

source = replaceRequired(
  source,
  `  if (staticView.value) selectAct(0)\n  const tick = (now: number) => {\n    if (previous && active.value && playing.value && !document.hidden && !staticView.value) {\n      elapsed.value = Math.min(total, elapsed.value + Math.max(0, Math.min(now - previous, 100)))\n      if (elapsed.value === total) playing.value = false\n    }`,
  `  if (staticView.value) selectAct(0)\n  narration.value?.addEventListener('ended', handleNarrationEnded)\n  document.addEventListener('visibilitychange', handleVisibilityChange)\n  const tick = (now: number) => {\n    if (previous && active.value && playing.value && !document.hidden && !staticView.value) {\n      if (!syncFromNarration()) {\n        elapsed.value = Math.min(total, elapsed.value + Math.max(0, Math.min(now - previous, 100)))\n      }\n      if (elapsed.value === total) playing.value = false\n    }`,
  'animation tick block',
)

source = replaceRequired(
  source,
  `onUnmounted(() => {\n  cancelAnimationFrame(frame)\n  media?.removeEventListener('change', updateMotion)\n})`,
  `onUnmounted(() => {\n  cancelAnimationFrame(frame)\n  pauseNarration()\n  document.removeEventListener('visibilitychange', handleVisibilityChange)\n  narration.value?.removeEventListener('ended', handleNarrationEnded)\n  media?.removeEventListener('change', updateMotion)\n})`,
  'unmount cleanup block',
)

source = replaceRequired(
  source,
  `<section class="experience-journey" :class="{ paused: !playing, reduced, 'is-outro': isOutro, 'is-immersive': expansion > .99 }" :style="{ '--immersion': expansion }" aria-label="SciOdyssey product and research demonstration" @click.stop>`,
  `<section class="experience-journey" :class="{ paused: !playing, reduced, 'awaiting-start': awaitingStart, 'is-outro': isOutro, 'is-immersive': expansion > .99 }" :style="{ '--immersion': expansion }" aria-label="SciOdyssey product and research demonstration" title="Click to play or pause" @click.stop="handleJourneyClick">\n    <audio ref="narration" src="/media/experience-journey-voice.wav?v=${audioVersion}" preload="auto" @loadedmetadata="applyPendingSeek" @timeupdate="syncFromNarration" @seeked="syncFromNarration" @pause="handleNarrationPause" @error="markAudioUnavailable" />`,
  'template root section',
)

source = replaceRequired(
  source,
  `@keyframes caret { 50% { opacity: 0; } }`,
  `.experience-journey { cursor: pointer; }\n.experience-journey button,\n.experience-journey a { cursor: pointer; }\n.journey-controls { display: none !important; }\n.awaiting-start .terminal-shell { filter: none; }\n@keyframes caret { 50% { opacity: 0; } }`,
  'click playback styles',
)

await mkdir(new URL('../public/media/', import.meta.url), { recursive: true })
await copyFile(sourceAudioPath, publicAudioPath)
await writeFile(outputPath, source.endsWith('\n') ? source : `${source}\n`)
console.log(`Prepared ${fileURLToPath(outputPath).replace(`${here}/../`, '')}`)
console.log(`Prepared ${fileURLToPath(publicAudioPath).replace(`${here}/../`, '')}`)
