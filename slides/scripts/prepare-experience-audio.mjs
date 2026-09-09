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
  `<section class="experience-journey" :class="{ paused: !playing, reduced, 'awaiting-start': awaitingStart, 'is-outro': isOutro, 'is-immersive': expansion > .99 }" :style="{ '--immersion': expansion }" aria-label="SciOdyssey product and research demonstration" @click.stop>\n    <audio ref="narration" src="/media/experience-journey-voice.wav" preload="auto" @error="markAudioUnavailable" />`,
  'template root section',
)

source = replaceRequired(
  source,
  `    <!-- Act jump controls — outside terminal-shell so they're always visible -->`,
  `    <button v-if="awaitingStart && !staticView && !reduced" class="journey-start-frame" type="button" aria-label="Play narrated experience" :title="audioAvailable ? 'Play with sound' : 'Audio unavailable · silent preview'" @click.stop="replay">\n      <span aria-hidden="true">▶</span>\n    </button>\n    <!-- Act jump controls — outside terminal-shell so they're always visible -->`,
  'frame start control',
)

source = replaceRequired(
  source,
  `@keyframes caret { 50% { opacity: 0; } }`,
  `.journey-start-frame { position: absolute; left: 245px; top: 225px; z-index: 39; width: 490px; height: 276px; display: grid; place-items: center; border: 0; border-radius: 14px; background: transparent; color: var(--ux-blue); cursor: pointer; font-family: var(--ux-font); }\n.journey-start-frame::before { content: ''; position: absolute; inset: 0; border-radius: inherit; border: 1px solid rgba(124, 187, 214, .26); background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.12)); opacity: 0; transition: opacity .18s ease; }\n.journey-start-frame span { display: grid; place-items: center; width: 54px; height: 54px; padding-left: 4px; border: 1px solid #d9e5ec; border-radius: 999px; background: rgba(255,255,255,.92); box-shadow: 0 18px 46px rgba(35, 53, 76, .13); font-size: 22px; transform: translateY(2px); transition: transform .18s ease, box-shadow .18s ease; }\n.journey-start-frame:hover::before, .journey-start-frame:focus-visible::before { opacity: 1; }\n.journey-start-frame:hover span, .journey-start-frame:focus-visible span { transform: translateY(0) scale(1.04); box-shadow: 0 24px 54px rgba(35, 53, 76, .17); }\n.journey-start-frame:focus-visible { outline: 2px solid #65afcd; outline-offset: 4px; }\n.awaiting-start .journey-controls { opacity: 1; }\n@keyframes caret { 50% { opacity: 0; } }`,
  'start frame styles',
)

await mkdir(new URL('../public/media/', import.meta.url), { recursive: true })
await copyFile(sourceAudioPath, publicAudioPath)
await writeFile(outputPath, source.endsWith('\n') ? source : `${source}\n`)
console.log(`Prepared ${fileURLToPath(outputPath).replace(`${here}/../`, '')}`)
console.log(`Prepared ${fileURLToPath(publicAudioPath).replace(`${here}/../`, '')}`)
