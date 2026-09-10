// Stable destinations survive slide reordering and Slidev's production build.
export const conclusionTargets = {
  summary: '<SummaryConclusions />',
  'thank-you': '<ThankYouClosing />',
  qa: '<QuestionsAndAnswers />',
  system: '<div class="visual-kicker">02 / SYSTEM · DESIGN</div>',
  principles: '<div class="visual-kicker orange">02 / SYSTEM · RESEARCH PHILOSOPHY</div>',
  evaluation: '<EvaluationClaimCards />',
  diversity: '<ModelRotationInsight />',
  parallel: '<ParallelResearchInsight />',
  engineering: '<!-- class: agentic-swe-fieldnote-slide -->',
  'open-world': '<!-- class: open-world-slide -->',
}

export const conclusionCards = [
  { id: 'system', label: 'SYSTEM', title: 'Persistent world.', emphasis: 'Fresh scientist.', image: 'system.png', route: 'system', accent: '#0284c7', x: 30, y: 19, width: 210, height: 154, tilt: -4 },
  { id: 'principles', label: 'RESEARCH DISCIPLINE', title: 'Ground the data.', emphasis: 'Test cheaply.', image: 'principles.png', route: 'principles', accent: '#dc7130', x: 267, y: 37, width: 210, height: 146, tilt: 3 },
  { id: 'open-world', label: 'OPEN-WORLD RESEARCH', title: 'Open action space.', emphasis: 'Room to adapt.', image: '/assets/research-globe.png', route: 'open-world', accent: '#a052d5', x: 503, y: 16, width: 210, height: 150, tilt: -3 },
  { id: 'engineering', label: 'ENGINEERING', title: 'Isolate changes.', emphasis: 'Review, then merge.', image: 'engineering.png', route: 'engineering', accent: '#07886a', x: 740, y: 36, width: 210, height: 150, tilt: 4 },
  { id: 'result', label: 'MEASURED RESULT', title: '0.6059', note: 'Public-validation Primary', image: 'result.png', route: 'evaluation', clicks: 2, accent: '#16803b', x: 28, y: 204, width: 226, height: 106, tilt: -3 },
  { id: 'trajectory', label: 'SUSTAINED SEARCH', title: '4 cycles', note: '7 Full evaluations', image: 'trajectory.png', route: 'evaluation', clicks: 4, accent: '#0284c7', x: 45, y: 338, width: 226, height: 102, tilt: 4 },
  { id: 'robustness', label: 'RECOVERY & REVIEW', title: 'Self-healing.', emphasis: 'Audited evidence.', image: 'robustness.png', route: 'evaluation', clicks: 6, accent: '#dd486b', x: 739, y: 214, width: 211, height: 100, tilt: 3 },
  { id: 'comparison', label: 'AGENT COMPARISON', title: 'Organization matters', note: 'Direct agent vs. META-Scientist', image: 'comparison.png', route: 'evaluation', clicks: 8, accent: '#9350d7', x: 727, y: 344, width: 222, height: 96, tilt: -4 },
  { id: 'resources', label: 'CONSUMER HARDWARE', title: '~$10', note: 'Project estimate', emphasis: '0 GPU-hours', route: 'evaluation', clicks: 11, accent: '#d97832', x: 103, y: 471, width: 226, height: 65, tilt: -3 },
  { id: 'diversity', label: 'MODEL DIVERSITY', title: 'Depth + breadth', note: 'GPT + Gemini', route: 'diversity', accent: '#9657dc', x: 365, y: 453, width: 245, height: 80, tilt: 2 },
  { id: 'parallel', label: 'PARALLEL RESEARCH', title: 'Losing branch.', emphasis: 'Useful knowledge.', image: 'parallel.png', route: 'parallel', accent: '#16803b', x: 650, y: 468, width: 269, height: 70, tilt: -2 },
]
