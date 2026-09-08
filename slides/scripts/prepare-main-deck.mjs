import { readFile, writeFile } from 'node:fs/promises'

const sourcePath = 'slides.md'
const insertPath = 'snippets/evaluation-claim-verdict.md'
const outputPath = '.generated-slides.md'
const insertAfter = '<ExperienceJourney />'
const retiredSlideMarkers = [
  '<div class="visual-kicker orange resources-page-kicker">04 / EVALUATION · RESOURCE ACCOUNTING</div>',
  '<div class="visual-kicker orange">04 / EVALUATION · DIRECT-AGENT COMPARISON</div>',
]

const oldInsight = `<div class="insight-item">
    <span class="insight-index blue">01</span>
    <div><strong>Different agents search differently.</strong><p>Recorded runs took different routes: local refinement, mechanism pivots, and broader search. Heterogeneous Scientists turn those search styles into a broader exploration prior.</p></div>
  </div>`

const newInsight = `<div class="insight-item">
    <span class="insight-index blue">01</span>
    <div><strong>Reset the context. Rotate the prior.</strong><p>Gemini-only SciOdyssey already reached 0.6052 Primary. The best retained run reached 0.6059363 while rotating GPT and Gemini across fresh Scientist trajectories. The architecture works with one model; model diversity may broaden the search further.</p></div>
  </div>`

const source = await readFile(sourcePath, 'utf8')
const insert = (await readFile(insertPath, 'utf8')).trim()

if (!source.includes(insertAfter)) {
  throw new Error(`Could not find insertion anchor: ${insertAfter}`)
}

function removeSlideByMarker(deck, slideMarker) {
  const markerIndex = deck.indexOf(slideMarker)
  if (markerIndex === -1) {
    throw new Error(`Could not find slide marker to retire: ${slideMarker}`)
  }

  const slideStart = deck.lastIndexOf('\n---\n', markerIndex)
  const slideEnd = deck.indexOf('\n---\n', markerIndex)

  if (slideStart === -1 || slideEnd === -1) {
    throw new Error(`Could not resolve slide boundaries for: ${slideMarker}`)
  }

  return `${deck.slice(0, slideStart)}${deck.slice(slideEnd)}`
}

function replaceRequired(deck, from, to, label) {
  if (!deck.includes(from)) {
    throw new Error(`Could not find required ${label} block`)
  }
  return deck.replace(from, to)
}

let output = source.replace(insertAfter, `${insertAfter}\n\n---\n\n${insert}`)
for (const slideMarker of retiredSlideMarkers) {
  output = removeSlideByMarker(output, slideMarker)
}
output = replaceRequired(output, oldInsight, newInsight, 'model-diversity insight')

await writeFile(outputPath, output.endsWith('\n') ? output : `${output}\n`)
console.log(`Prepared ${outputPath}`)
