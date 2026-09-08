import { readFile, writeFile } from 'node:fs/promises'

const sourcePath = 'slides.md'
const insertPath = 'snippets/evaluation-claim-verdict.md'
const outputPath = '.generated-slides.md'
const marker = '<div class="visual-kicker orange">04 / EVALUATION · PUBLIC-VALIDATION RESULT</div>'

const source = await readFile(sourcePath, 'utf8')
const insert = (await readFile(insertPath, 'utf8')).trim()

if (!source.includes(marker)) {
  throw new Error(`Could not find insertion marker: ${marker}`)
}

const output = source.replace(marker, `${insert}\n\n---\n\n${marker}`)

await writeFile(outputPath, output.endsWith('\n') ? output : `${output}\n`)
console.log(`Prepared ${outputPath}`)
