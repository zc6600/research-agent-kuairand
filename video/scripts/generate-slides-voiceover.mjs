import { readFile, writeFile, mkdir, mkdtemp } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';

// Usage: node video/scripts/generate-slides-voiceover.mjs [--dry-run]
// Outputs are always written to a fresh directory; existing audio is preserved.
async function main() {
  const args = process.argv.slice(2);
  if (args.some(arg => arg !== '--dry-run')) throw new Error('Usage: generate-slides-voiceover.mjs [--dry-run]');
  const script = JSON.parse(await readFile(new URL('./slides-ux-voiceover-en.json', import.meta.url), 'utf8'));
  const { cues, duration } = script;
  if (!Number.isFinite(duration) || duration <= 0 || !Array.isArray(cues) || !cues.length) throw new Error('Invalid timeline');
  let previousEnd = 0;
  const ids = new Set();
  for (const cue of cues) {
    if (!Number.isFinite(cue.start) || !Number.isFinite(cue.end) || cue.start < previousEnd || cue.end <= cue.start || cue.end > duration || !cue.text?.trim() || !/^\d+$/.test(cue.id) || ids.has(cue.id)) {
      throw new Error(`Invalid or overlapping cue: ${cue.id}`);
    }
    ids.add(cue.id);
    previousEnd = cue.end;
  }
  if (args.includes('--dry-run')) {
    for (const cue of cues) console.log(`${cue.id} | ${cue.start.toFixed(1)}–${cue.end.toFixed(1)}s | ${cue.text}`);
    console.log(`Validated ${cues.length} cues across ${duration}s. No API calls or files created.`);
    return;
  }
  if (!process.env.OPENAI_API_KEY) throw new Error('Set OPENAI_API_KEY in your local shell first. Do not paste your key into chat.');
  for (const tool of ['ffmpeg', 'ffprobe']) execFileSync(tool, ['-version'], { stdio: 'ignore' });
  const root = fileURLToPath(new URL('../out/audio/', import.meta.url));
  await mkdir(root, { recursive: true });
  const output = await mkdtemp(join(root, 'slides-ux-en-'));
  console.log(`Output: ${output}`);
  const report = [];
  const inputs = [];
  for (const cue of cues) {
    console.log(`Generating ${cue.id}/${cues.length}...`);
    const response = await fetch('https://api.openai.com/v1/audio/speech', {
      method: 'POST',
      headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: script.model,
        voice: process.env.TTS_VOICE || script.voice,
        input: cue.text,
        instructions: script.instructions,
        response_format: 'wav',
      }),
      signal: AbortSignal.timeout(120000),
    });
    if (!response.ok) throw new Error(`Speech API returned HTTP ${response.status}. Completed clips remain in ${output}. Check API access, billing, and rate limits.`);
    const file = join(output, `${cue.id}.wav`);
    await writeFile(file, Buffer.from(await response.arrayBuffer()), { flag: 'wx' });
    const seconds = Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file], { encoding: 'utf8' }).trim());
    if (!Number.isFinite(seconds) || seconds <= 0) throw new Error(`Invalid audio duration: ${file}`);
    report.push({ ...cue, actualDuration: seconds, fits: seconds <= cue.end - cue.start });
    await writeFile(join(output, 'timing-report.json'), JSON.stringify(report, null, 2));
    inputs.push('-i', file);
  }
  const overruns = report.filter(cue => !cue.fits);
  if (overruns.length) throw new Error(`Cues ${overruns.map(c => c.id).join(', ')} exceed their time slots. All clips are preserved in ${output}; shorten those lines or align them manually. No final track was mixed.`);
  const filters = cues.map((cue, i) => `[${i}:a]aresample=48000,aformat=channel_layouts=mono,adelay=${Math.round(cue.start * 1000)}:all=1[a${i}]`);
  filters.push(`${cues.map((_, i) => `[a${i}]`).join('')}amix=inputs=${cues.length}:normalize=0,apad,atrim=duration=${duration}[voice]`);
  const final = join(output, 'voiceover.wav');
  execFileSync('ffmpeg', ['-v', 'error', '-n', ...inputs, '-filter_complex', filters.join(';'), '-map', '[voice]', '-ar', '48000', '-c:a', 'pcm_s16le', final], { stdio: 'inherit' });
  console.log(`Ready: ${final}\nPlace at 00:00 of the matching ${duration}s animation. Listen and check sync before exporting.`);
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
