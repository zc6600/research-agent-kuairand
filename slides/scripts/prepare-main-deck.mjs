import { readFile, writeFile } from 'node:fs/promises'

const sourcePath = 'slides.md'
const insertPath = 'snippets/evaluation-claim-verdict.md'
const outputPath = '.generated-slides.md'
const marker = '<div class="visual-kicker orange">04 / EVALUATION · PUBLIC-VALIDATION RESULT</div>'
const retiredSlideMarkers = [
  '<div class="visual-kicker orange resources-page-kicker">04 / EVALUATION · RESOURCE ACCOUNTING</div>',
  '<div class="visual-kicker orange">04 / EVALUATION · DIRECT-AGENT COMPARISON</div>',
]

const source = await readFile(sourcePath, 'utf8')
const insert = (await readFile(insertPath, 'utf8')).trim()

if (!source.includes(marker)) {
  throw new Error(`Could not find insertion marker: ${marker}`)
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

let output = source.replace(marker, `${insert}\n\n---\n\n${marker}`)
for (const slideMarker of retiredSlideMarkers) {
  output = removeSlideByMarker(output, slideMarker)
}

await writeFile(outputPath, output.endsWith('\n') ? output : `${output}\n`)
console.log(`Prepared ${outputPath}`)
