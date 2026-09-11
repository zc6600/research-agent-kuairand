import { test } from 'node:test'
import assert from 'node:assert/strict'
import { alignNarration } from './align-slides-voiceover.mjs'

test('omits the spoken slate, joins complete phrases and places silence between cues', () => {
  const source = Buffer.alloc(6 * 48000 * 2)
  for (let second = 0; second < 6; second++) {
    for (let i = second * 48000; i < (second + 1) * 48000; i++) source.writeInt16LE(second + 1, i * 2)
  }
  const output = alignNarration(source, { duration: 8, cues: [
    { id: 'intro', start: 1, end: 4, sourceSegments: [[2, 3], [4, 5]], joinPause: .2 },
    { id: 'next', start: 5, end: 7, sourceSegments: [[5, 6]] },
  ] })
  const sample = time => output.readInt16LE(Math.round(time * 48000) * 2)
  assert.equal(output.length, 8 * 48000 * 2)
  for (const time of [0, .999, 2, 2.199, 3.2, 4.999, 6, 7.999]) assert.equal(sample(time), 0)
  for (const time of [1, 1.999]) assert.equal(sample(time), 3)
  for (const time of [2.2, 3.199]) assert.equal(sample(time), 5)
  for (const time of [5, 5.999]) assert.equal(sample(time), 6)
})

test('rejects overflow and bad source boundaries instead of cutting words', () => {
  const source = Buffer.alloc(4 * 48000 * 2)
  assert.throws(() => alignNarration(source, {duration: 4, cues: [
    {id: 'short', start: 0, end: 1, sourceSegments: [[1, 3]]},
  ]}), /exceeds cue short/)
  assert.throws(() => alignNarration(source, {duration: 4, cues: [
    {id: 'outside', start: 0, end: 3, sourceSegments: [[3, 5]]},
  ]}), /Invalid source interval/)
  assert.throws(() => alignNarration(source, {duration: 4, cues: [
    {id: 'first', start: 0, end: 2, sourceSegments: [[0, 1]]},
    {id: 'overlap', start: 1, end: 3, sourceSegments: [[1, 2]]},
  ]}), /Invalid cue window/)
})
