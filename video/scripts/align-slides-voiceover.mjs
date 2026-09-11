import { execFileSync } from 'node:child_process'
import { readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const sampleRate = 48000
const bytesPerSample = 2

// Source intervals are measured in the decoded recording, not inferred from
// text length. Keep the voice at 1x and leave silence after each complete cue.
export function alignNarration(source, timeline) {
  const frame = seconds => Math.round(seconds * sampleRate)
  const output = Buffer.alloc(frame(timeline.duration) * bytesPerSample)
  let previousEnd = 0
  let previousSourceEnd = 0
  for (const cue of timeline.cues) {
    if (!(cue.start >= previousEnd && cue.end > cue.start && cue.end <= timeline.duration)) {
      throw new Error(`Invalid cue window: ${cue.id}`)
    }
    if (!cue.sourceSegments?.length) throw new Error(`Missing source intervals: ${cue.id}`)
    let cursor = frame(cue.start)
    for (const [index, [start, end]] of cue.sourceSegments.entries()) {
      if (!(start >= previousSourceEnd && end > start && frame(end) * bytesPerSample <= source.length)) {
        throw new Error(`Invalid source interval: ${cue.id}`)
      }
      if (index) cursor += frame(cue.joinPause ?? 0)
      const length = frame(end) - frame(start)
      if (cursor + length > frame(cue.end)) throw new Error(`Narration exceeds cue ${cue.id}; adjust pauses without clipping speech`)
      source.copy(output, cursor * bytesPerSample, frame(start) * bytesPerSample, frame(end) * bytesPerSample)
      cursor += length
      previousSourceEnd = end
    }
    previousEnd = cue.end
  }
  return output
}

function wav(pcm) {
  const header = Buffer.alloc(44)
  header.write('RIFF', 0)
  header.writeUInt32LE(36 + pcm.length, 4)
  header.write('WAVEfmt ', 8)
  header.writeUInt32LE(16, 16)
  header.writeUInt16LE(1, 20)
  header.writeUInt16LE(1, 22)
  header.writeUInt32LE(sampleRate, 24)
  header.writeUInt32LE(sampleRate * bytesPerSample, 28)
  header.writeUInt16LE(bytesPerSample, 32)
  header.writeUInt16LE(16, 34)
  header.write('data', 36)
  header.writeUInt32LE(pcm.length, 40)
  return Buffer.concat([header, pcm])
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const delivery = new URL('../experience-journey-delivery/', import.meta.url)
  const timeline = JSON.parse(await readFile(new URL('subtitle-cues.json', delivery), 'utf8'))
  const source = execFileSync('ffmpeg', [
    '-v', 'error', '-i', fileURLToPath(new URL('SciOdyssey.m4a', delivery)),
    '-f', 's16le', '-ar', String(sampleRate), '-ac', '1', '-',
  ], { maxBuffer: 32 * 1024 * 1024 })
  const output = new URL('SciOdyssey_ExperienceJourney_aligned_voice.wav', delivery)
  await writeFile(output, wav(alignNarration(source, timeline)))
  console.log(`Aligned ${timeline.cues.length} complete cues at 1x across ${timeline.duration}s: ${fileURLToPath(output)}`)
}
