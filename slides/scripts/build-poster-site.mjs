import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const slidesRoot = fileURLToPath(new URL('../', import.meta.url))
const postersRoot = path.join(slidesRoot, 'posters')
const distRoot = path.join(postersRoot, 'dist')
const mainDeckRoot = path.join(postersRoot, 'html', 'main-deck-update')
const voyageRoot = path.join(postersRoot, 'html', 'voyage')

const journeySpacingCss = String.raw`
.journey .journey-steps {
  justify-content: center;
  gap: 8px;
  padding: 8px 5px 6px;
  font-size: 9.5px;
}
.journey .journey-steps .step-item {
  white-space: nowrap;
}
.journey .journey-steps .step-sep {
  flex: 0 0 auto;
  opacity: .78;
}
`

await rm(distRoot, { recursive: true, force: true })
await mkdir(distRoot, { recursive: true })

function extractPolishCss(exportSource) {
  return [...exportSource.matchAll(/const\s+\w*PolishCss\s*=\s*String\.raw`([\s\S]*?)`;/g)]
    .map(match => match[1].trim())
    .filter(Boolean)
    .join('\n\n')
}

function extractPolishFunctions(exportSource) {
  const matches = [...exportSource.matchAll(/function\s+(apply[A-Za-z0-9_]*Polish)\s*\(\)\s*\{/g)]
  if (!matches.length) return { source: '', names: [] }

  const browserMarker = exportSource.indexOf('\nconst browser =', matches.at(-1).index)
  const blocks = matches.map((match, index) => {
    const start = match.index
    const end = index + 1 < matches.length ? matches[index + 1].index : browserMarker
    if (start == null || end == null || end < 0) {
      throw new Error(`Could not extract ${match[1]} from main-deck export.mjs`)
    }
    return exportSource.slice(start, end).trim()
  })

  return {
    source: blocks.join('\n\n'),
    names: matches.map(match => match[1]),
  }
}

async function copyAssets(sourceRoot, targetRoot) {
  await cp(path.join(sourceRoot, 'assets'), path.join(targetRoot, 'assets'), {
    recursive: true,
  })
  await cp(path.join(sourceRoot, 'poster.css'), path.join(targetRoot, 'poster.css'))
}

async function buildLatestPoster() {
  let html = await readFile(path.join(mainDeckRoot, 'poster.html'), 'utf8')
  const exportSource = await readFile(path.join(mainDeckRoot, 'export.mjs'), 'utf8')
  const exportPolishCss = extractPolishCss(exportSource)
  const polishCss = [exportPolishCss, journeySpacingCss.trim()].filter(Boolean).join('\n\n')
  const polishFunctions = extractPolishFunctions(exportSource)

  if (polishCss) {
    html = html.replace(
      '</head>',
      `<style id="poster-export-polish">\n${polishCss}\n</style>\n</head>`,
    )
  }

  if (polishFunctions.source) {
    const calls = polishFunctions.names.map(name => `${name}();`).join('\n')
    html = html.replace(
      '</body>',
      `<script id="poster-export-polish-runtime">\n${polishFunctions.source}\n\n${calls}\n</script>\n</body>`,
    )
  }

  await copyAssets(mainDeckRoot, distRoot)
  await writeFile(path.join(distRoot, 'index.html'), html)
}

async function buildVoyagePoster() {
  const target = path.join(distRoot, 'voyage')
  await mkdir(target, { recursive: true })
  await copyAssets(voyageRoot, target)
  const html = await readFile(path.join(voyageRoot, 'poster.html'), 'utf8')
  await writeFile(path.join(target, 'index.html'), html)
}

async function buildVersionsIndex() {
  const target = path.join(distRoot, 'versions')
  await mkdir(target, { recursive: true })

  const revision = process.env.CF_PAGES_COMMIT_SHA || process.env.GITHUB_SHA || process.env.COMMIT_SHA || ''
  const shortRevision = revision ? revision.slice(0, 7) : 'current build'
  const generatedAt = new Date().toISOString()

  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SciOdyssey Poster Versions</title>
<style>
  :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  * { box-sizing: border-box; }
  body { margin: 0; min-height: 100vh; background: #f6f3ed; color: #17212b; display: grid; place-items: center; padding: 36px; }
  main { width: min(920px, 100%); }
  .eyebrow { font: 700 12px/1 ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: 1.6px; color: #b94020; }
  h1 { margin: 12px 0 8px; font: 750 clamp(38px, 7vw, 68px)/.95 Georgia, "Times New Roman", serif; letter-spacing: -2px; }
  .lede { max-width: 680px; color: #66717b; font-size: 18px; line-height: 1.5; }
  .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-top: 34px; }
  a { display: block; min-height: 180px; padding: 24px; border: 1px solid #d9cebd; border-radius: 18px; background: #fffdf8; color: inherit; text-decoration: none; box-shadow: 0 8px 28px rgba(40, 30, 20, .05); }
  a:hover { border-color: #9daab3; transform: translateY(-2px); }
  .tag { font: 750 11px/1 ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: 1px; color: #0b456b; }
  h2 { margin: 16px 0 8px; font-size: 25px; }
  p { margin: 0; color: #65717b; line-height: 1.45; }
  footer { margin-top: 22px; color: #8c949a; font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace; }
  @media (max-width: 680px) { .grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<main>
  <div class="eyebrow">SCIODYSSEY / POSTER BUILDS</div>
  <h1>Poster versions.</h1>
  <p class="lede">The root URL always points to the latest technical-handout build. Older visual directions stay available here for comparison.</p>
  <div class="grid">
    <a href="/">
      <span class="tag">LATEST</span>
      <h2>Main deck update</h2>
      <p>Current technical handout, including the latest Problem and System refinements.</p>
    </a>
    <a href="/voyage/">
      <span class="tag">ARCHIVE / VOYAGE</span>
      <h2>Voyage</h2>
      <p>The earlier voyage-style HTML poster preserved as a stable comparison build.</p>
    </a>
  </div>
  <footer>Revision ${shortRevision} · generated ${generatedAt}</footer>
</main>
</body>
</html>`

  await writeFile(path.join(target, 'index.html'), html)
}

await buildLatestPoster()
await buildVoyagePoster()
await buildVersionsIndex()

console.log('Built poster site:')
console.log(`  latest   -> ${path.join(distRoot, 'index.html')}`)
console.log(`  voyage   -> ${path.join(distRoot, 'voyage', 'index.html')}`)
console.log(`  versions -> ${path.join(distRoot, 'versions', 'index.html')}`)
