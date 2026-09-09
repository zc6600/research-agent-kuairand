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
  `const seekTo = (value: number) => {\n  const clamped = Math.max(0, Math.min(total, value))\n  elapsed.value = clamped\n  if (shouldUseNarration.value && narration.value) {\n    narration.value.currentTime = clamped / 1000\n  }\n}\nconst markAudioUnavailable = () => {\n  audioAvailable.value = false\n}\nconst syncFromNarration = () => {\n  if (!shouldUseNarration.value || !narration.value) return false\n  elapsed.value = Math.max(0, Math.min(total, narration.value.currentTime * 1000))\n  if (elapsed.value >= total) playing.value = false\n  return true\n}\nconst playNarration = async () => {\n  awaitingStart.value = false\n  if (!shouldUseNarration.value || !narration.value) {\n    playing.value = !reduced.value && !staticView.value\n    return\n  }\n  try {\n    narration.value.muted = false\n    narration.value.volume = 1\n    await narration.value.play()\n    playing.value = true\n  } catch (error) {\n    console.warn('Falling back to silent ExperienceJourney playback.', error)\n    audioAvailable.value = false\n    playing.value = !reduced.value && !staticView.value\n  }\n}\nconst pauseNarration = () => {\n  narration.value?.pause()\n  playing.value = false\n}\nconst selectAct = (index: number) => {\n  seekTo(introDuration + starts[index] + (reduced.value || staticView.value ? durations[index] - 1 : 0))\n  if (reduced.value || staticView.value) {\n    playing.value = false\n    return\n  }\n  void playNarration()\n}\nconst replay = () => {\n  if (reduced.value || staticView.value) {\n    selectAct(0)\n    return\n  }\n  seekTo(0)\n  void playNarration()\n}\nconst toggle = () => {\n  if (elapsed.value >= total) {\n    replay()\n    return\n  }\n  if (playing.value) pauseNarration()\n  else void playNarration()\n}\nconst resetToStart = () => {\n  narration.value?.pause()\n  seekTo(0)\n  playing.value = false\n  awaitingStart.value = !reduced.value && !staticView.value\n}\nconst handleNarrationEnded = () => {\n  elapsed.value = total\n  playing.value = false\n}\nconst handleJourneyClick = () => {\n  if (staticView.value || reduced.value) return\n  if (awaitingStart.value || elapsed.value >= total) {\n    replay()\n    return\n  }\n  toggle()\n}`,
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
  `<section class="experience-journey" :class="{ paused: !playing, reduced, 'awaiting-start': awaitingStart, 'is-outro': isOutro, 'is-immersive': expansion > .99 }" :style="{ '--immersion': expansion }" aria-label="SciOdyssey product and research demonstration" title="Click to play or pause" @click.stop="handleJourneyClick">\n    <audio ref="narration" src="/media/experience-journey-voice.wav" preload="auto" @error="markAudioUnavailable" />`,
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
