import { readFile, writeFile } from 'node:fs/promises'
import { conclusionTargets } from '../composables/conclusions.mjs'

const sourcePath = 'slides.md'
const insertPath = 'snippets/evaluation-claim-verdict.md'
const outputPath = '.generated-slides.md'
const sourceExperienceSlide = '<ExperienceJourney />'
const experienceSlide = '<ExperienceJourneyAudio />'
const conclusionSlide = '<SummaryConclusions />'
const closingSlide = '<ThankYouClosing />'
const questionsSlide = '<QuestionsAndAnswers />'
const evaluationAnchor = '<ModelRotationInsight />'
const finaleAnchor = '<!-- class: agentic-swe-fieldnote-slide -->'
const retiredSlideMarkers = [
  '<div class="visual-kicker orange resources-page-kicker">04 / EVALUATION · RESOURCE ACCOUNTING</div>',
  '<div class="visual-kicker orange">04 / EVALUATION · DIRECT-AGENT COMPARISON</div>',
]

const source = await readFile(sourcePath, 'utf8')
const insert = (await readFile(insertPath, 'utf8')).trim()

function replaceRequired(deck, from, to, label) {
  if (!deck.includes(from)) {
    throw new Error(`Could not find ${label}`)
  }
  return deck.replace(from, to)
}

function slideBounds(deck, slideMarker) {
  const markerIndex = deck.indexOf(slideMarker)
  if (markerIndex === -1) {
    throw new Error(`Could not find slide marker: ${slideMarker}`)
  }

  const slideStart = deck.lastIndexOf('\n---\n', markerIndex)
  const slideEnd = deck.indexOf('\n---\n', markerIndex)

  if (slideStart === -1 || slideEnd === -1) {
    throw new Error(`Could not resolve slide boundaries for: ${slideMarker}`)
  }

  return { slideStart, slideEnd }
}

function removeSlideByMarker(deck, slideMarker) {
  const { slideStart, slideEnd } = slideBounds(deck, slideMarker)
  return `${deck.slice(0, slideStart)}${deck.slice(slideEnd)}`
}

function extractSlideByMarker(deck, slideMarker) {
  const { slideStart, slideEnd } = slideBounds(deck, slideMarker)
  const slide = deck.slice(slideStart, slideEnd)
  const withoutSlide = `${deck.slice(0, slideStart)}${deck.slice(slideEnd)}`
  return { deck: withoutSlide, slide }
}

function retitleToc(deck) {
  deck = replaceRequired(
    deck,
    '    <h1>The run, in four moves</h1>\n    <div class="toc-intro">A single route from the problem to the proof.</div>',
    '    <h1>Outline</h1>\n    <div class="toc-intro">Five sections covering failure modes, system architecture, evaluation, and experience.</div>',
    'TOC title',
  )

  const oldTrack = `<div class="toc-track" aria-label="Talk order">
  <div class="toc-track-line" aria-hidden="true"></div>
  <div class="toc-step toc-step-blue">
    <div class="toc-step-marker"><span class="toc-step-number mono">01</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">PROBLEM</div>
    <strong>Limits of common research approaches</strong>
    <span>Set the task and its failure modes.</span>
  </div>
  <div class="toc-step toc-step-orange">
    <div class="toc-step-marker"><span class="toc-step-number mono">02</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">SYSTEM</div>
    <strong>A system for sustained research</strong>
    <span>Keep experience while resetting the scientist.</span>
  </div>
  <div class="toc-step toc-step-purple">
    <div class="toc-step-marker"><span class="toc-step-number mono">03</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">USER EXPERIENCE</div>
    <strong>Run the research journey</strong>
    <span>Move from task contract to retained state.</span>
  </div>
  <div class="toc-step toc-step-green">
    <div class="toc-step-marker"><span class="toc-step-number mono">04</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">EVALUATION</div>
    <strong>From claim to evidence</strong>
    <span>Measure what survives the run.</span>
  </div>
</div>`

  const newTrack = `<div class="toc-track toc-track-five" aria-label="Talk order">
  <div class="toc-track-line" aria-hidden="true"></div>
  <div class="toc-step toc-step-blue">
    <div class="toc-step-marker"><span class="toc-step-number mono">01</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">PROBLEM</div>
    <strong>Limits of common research approaches</strong>
    <span>Set the task and its failure modes.</span>
  </div>
  <div class="toc-step toc-step-orange">
    <div class="toc-step-marker"><span class="toc-step-number mono">02</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">SYSTEM</div>
    <strong>A system for sustained research</strong>
    <span>Keep evidence while resetting the scientist.</span>
  </div>
  <div class="toc-step toc-step-green">
    <div class="toc-step-marker"><span class="toc-step-number mono">03</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">EVALUATION</div>
    <strong>From claim to evidence</strong>
    <span>Measure what survives the run.</span>
  </div>
  <div class="toc-step toc-step-purple">
    <div class="toc-step-marker"><span class="toc-step-number mono">04</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">FINDINGS</div>
    <strong>What the run taught us</strong>
    <span>Model diversity and branch handoff.</span>
  </div>
  <div class="toc-step toc-step-rose">
    <div class="toc-step-marker"><span class="toc-step-number mono">05</span><span class="toc-step-dot"></span></div>
    <div class="toc-step-label mono">USER EXPERIENCE</div>
    <strong>See the research journey</strong>
    <span>End with the workflow in motion.</span>
  </div>
</div>`

  return replaceRequired(deck, oldTrack, newTrack, 'TOC track')
}

let output = source
output = retitleToc(output)
output = replaceRequired(output, sourceExperienceSlide, experienceSlide, 'experience slide component')

const extracted = extractSlideByMarker(output, experienceSlide)
output = extracted.deck
const extractedConclusions = extractSlideByMarker(output, conclusionSlide)
output = extractedConclusions.deck
const summarySlide = extractedConclusions.slide.replace(/^\n*---\n*/, '').trim()
const extractedClosing = extractSlideByMarker(output, closingSlide)
output = extractedClosing.deck
const thankYouSlide = extractedClosing.slide.replace(/^\n*---\n*/, '').trim()
const extractedQuestions = extractSlideByMarker(output, questionsSlide)
output = extractedQuestions.deck
const qAndASlide = extractedQuestions.slide.replace(/^\n*---\n*/, '').trim()
let userExperienceSlide = extracted.slide.replace(/^\n*---\n*/, '').replace(/\n*---\n*$/, '').trim()
userExperienceSlide = userExperienceSlide
  .replace('03 / UX opens with', '05 / UX finale opens with')
  .replace('Six acts autoplay:', 'Six acts play after clicking the frame:')
  .replace('Hover over the lower right of the demo for pause and replay.', 'Click the frame to play, pause, continue, or replay. Summary, Thank You and Q&A follow the UX sequence.')

for (const slideMarker of retiredSlideMarkers) {
  output = removeSlideByMarker(output, slideMarker)
}

output = replaceRequired(output, evaluationAnchor, `${insert}\n\n---\n\n${evaluationAnchor}`, 'evaluation insertion anchor')
output = replaceRequired(output, finaleAnchor, `${userExperienceSlide}\n\n---\n\n${summarySlide}\n\n---\n\n${thankYouSlide}\n\n---\n\n${qAndASlide}\n\n---\n\n${finaleAnchor}`, 'user-experience finale anchor')

// Apply aliases after rearranging the deck so frontmatter stays with its slide.
for (const [alias, marker] of Object.entries(conclusionTargets)) {
  output = replaceRequired(output, `\n---\n\n${marker}`, `\n---\nrouteAlias: ${alias}\n---\n\n${marker}`, `conclusion destination ${alias}`)
}

await writeFile(outputPath, output.endsWith('\n') ? output : `${output}\n`)
console.log(`Prepared ${outputPath}`)
