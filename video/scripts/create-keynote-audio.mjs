// Original, deterministic placeholder score and interaction cues. No source samples.
// Regenerate with npm run audio:keynote; replace either track via composition props.
import {mkdirSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

const rate = 44100;
const duration = 72;
const size = rate * duration;
const folder = fileURLToPath(new URL('../public/audio/keynote/', import.meta.url));
mkdirSync(folder, {recursive: true});

function wav(name, left, right) {
  const data = Buffer.alloc(44 + size * 4);
  data.write('RIFF', 0); data.writeUInt32LE(data.length - 8, 4);
  data.write('WAVEfmt ', 8); data.writeUInt32LE(16, 16);
  data.writeUInt16LE(1, 20); data.writeUInt16LE(2, 22);
  data.writeUInt32LE(rate, 24); data.writeUInt32LE(rate * 4, 28);
  data.writeUInt16LE(4, 32); data.writeUInt16LE(16, 34);
  data.write('data', 36); data.writeUInt32LE(size * 4, 40);
  let peak = 0;
  for (let i = 0; i < size; i++) {
    const edge = Math.min(1, i / (rate * 1.2), (size - 1 - i) / (rate * 2.2));
    const a = left[i] * edge;
    const b = right[i] * edge;
    peak = Math.max(peak, Math.abs(a), Math.abs(b));
    data.writeInt16LE(Math.round(Math.max(-1, Math.min(1, a)) * 32767), 44 + i * 4);
    data.writeInt16LE(Math.round(Math.max(-1, Math.min(1, b)) * 32767), 46 + i * 4);
  }
  if (peak >= 1) throw new Error(`Clipping in ${name}: ${peak}`);
  writeFileSync(`${folder}/${name}.wav`, data);
  console.log(`${name}: ${duration}s stereo PCM, peak ${peak.toFixed(4)}`);
}

const left = new Float32Array(size);
const right = new Float32Array(size);
const chords = [
  [0, 17, [130.813, 195.998, 246.942]],
  [15, 12, [146.832, 195.998, 246.942]],
  [25, 12, [164.814, 220, 261.626]],
  [35, 13, [130.813, 195.998, 261.626]],
  [46, 11, [146.832, 220, 293.665]],
  [55, 11, [164.814, 195.998, 246.942]],
  [64, 8, [130.813, 195.998, 261.626]],
];
for (const [start, length, frequencies] of chords) {
  for (let i = 0; i < length * rate && i + start * rate < size; i++) {
    const t = i / rate;
    const envelope = Math.min(1, t / 2, (length - t) / 2) ** 2 * 0.025;
    frequencies.forEach((hz, index) => {
      const tone = Math.sin(2 * Math.PI * hz * t) + 0.12 * Math.sin(4 * Math.PI * hz * t);
      left[i + start * rate] += tone * envelope * (0.8 + index * 0.1);
      right[i + start * rate] += (Math.sin(2 * Math.PI * hz * t + 0.12) + 0.12 * Math.sin(4 * Math.PI * hz * t)) * envelope * (1 - index * 0.1);
    });
  }
}
// A light, evenly spaced pulse grows with autonomous execution and pauses for judgment.
for (let beat = 0; beat < 51; beat++) {
  const start = 15.4 + beat * 0.6;
  const hz = [523.251, 587.33, 659.255, 783.991][beat % 4];
  for (let j = 0; j < rate * 0.6; j++) {
    const t = j / rate;
    const k = Math.round(start * rate) + j;
    const v = Math.sin(2 * Math.PI * hz * t) * Math.min(1, t / 0.008) * Math.exp(-t * 10) * 0.014;
    left[k] += v * (beat % 2 ? 0.75 : 1);
    right[k] += v * (beat % 2 ? 1 : 0.75);
  }
}
wav('score', left, right);

left.fill(0); right.fill(0);
let seed = 82491;
function noise() { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 2147483648 - 1; }
for (const start of [6.08, 6.25, 6.44, 6.66, 16.32, 16.5, 16.68, 26.4, 26.6, 26.8, 48.1, 48.3, 48.5, 48.7, 48.9, 49.1, 58, 58.3, 58.6, 58.9]) {
  for (let j = 0; j < rate * 0.035; j++) {
    const t = j / rate;
    const v = noise() * Math.exp(-t * 165) * 0.055;
    const k = Math.round(start * rate) + j;
    left[k] += v; right[k] += v;
  }
}
for (const start of [10.1, 13, 18.2, 23.7, 28.2, 34, 41.8, 53, 60.8, 66.5]) {
  for (let j = 0; j < rate * 0.8; j++) {
    const t = j / rate;
    const v = (Math.sin(2 * Math.PI * 783.991 * t) + 0.35 * Math.sin(2 * Math.PI * 1174.66 * t)) * Math.min(1, t / 0.006) * Math.exp(-t * 7) * 0.036;
    const k = Math.round(start * rate) + j;
    left[k] += v; right[k] += v * 0.9;
  }
}
wav('cues', left, right);
