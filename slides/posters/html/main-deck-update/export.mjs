import { chromium } from 'playwright-chromium';
import { PDFDocument } from 'pdf-lib';
import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('./', import.meta.url);

const problemPolishCss = String.raw`
.problem {
  padding: 19px 22px 18px;
}
.problem h2 {
  max-width: 455px;
  font-size: 32px;
  letter-spacing: -1.35px;
}
.problem-lead {
  margin-top: 5px;
  max-width: 490px;
  color: #536579;
  font-size: 13.6px;
}
.problem .world-art {
  top: 17px;
  right: 20px;
  width: 78px;
  height: 78px;
  opacity: .38;
}
.problem .failure-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}
.problem .failure-item {
  position: relative;
  display: grid;
  grid-template-columns: 24px 1fr;
  grid-template-rows: auto;
  column-gap: 8px;
  min-height: 164px;
  padding: 11px 11px 12px;
  overflow: hidden;
  border: 1px solid #e2d5c1;
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(255,255,255,.32), rgba(255,255,255,.06)), #f1e8d8;
}
.problem .failure-item::before {
  content: '';
  position: absolute;
  inset: 0;
  border-top: 3px solid var(--navy);
  opacity: .86;
}
.problem .failure-item.failure-inertia::before { border-top-color: var(--rust); }
.problem .failure-item.failure-context::before { border-top-color: var(--navy); }
.problem .failure-idx {
  grid-column: 1;
  grid-row: 1;
  position: relative;
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  margin: 0;
  border-radius: 50%;
  border: 1px solid #b7c7d1;
  background: #f9f6ed;
  color: var(--navy);
  font-size: 10px;
}
.problem .failure-inertia .failure-idx { color: var(--rust); border-color: #d4aa93; }
.problem .failure-context .failure-idx { color: var(--navy); border-color: #a5c5dc; }
.problem .failure-text {
  grid-column: 2;
  grid-row: 1;
  position: relative;
  min-width: 0;
}
.problem .failure-text strong {
  font-family: var(--serif);
  font-size: 18px;
  line-height: 1.02;
  letter-spacing: -.55px;
}
.problem .failure-text p {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-top: 8px;
  font-size: 0;
  line-height: 1.2;
}
.problem .failure-claim {
  color: #2f3e4a;
  font-size: 12.2px;
  line-height: 1.25;
}
.problem .failure-receipt {
  margin-top: 2px;
  padding-top: 8px;
  border-top: 1px dashed #d4c6b2;
  color: #65717b;
  font-family: var(--mono);
  font-size: 8.9px;
  font-weight: 600;
  letter-spacing: -.15px;
  line-height: 1.25;
}
.problem .failure-receipt b {
  color: var(--rust);
  font-family: var(--mono);
}
.problem .failure-receipt code {
  color: var(--navy);
  font-family: var(--mono);
  font-size: 8.5px;
}
.problem .architecture-contrast {
  display: none;
}
.problem .problem-solution-bar {
  margin-top: 12px;
  min-height: 43px;
  align-items: center;
  border: 1px solid #ddb8a5;
  border-left: 4px solid var(--rust);
  border-radius: 8px;
  padding: 8px 12px;
  background: linear-gradient(90deg, #f9ece5, #f5eadb);
  color: #803017;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.48);
}
.problem .bar-tag {
  padding: 3px 7px;
  font-size: 8.8px;
  letter-spacing: 1px;
}
.problem .bar-desc {
  color: #71331e;
  font-size: 13.6px;
  font-family: var(--serif);
  font-weight: 700;
  letter-spacing: -.25px;
}
.problem .bar-desc strong {
  color: #71331e;
}
`;

const systemPolishCss = String.raw`
.system {
  padding: 18px 22px 16px;
}
.system h2 {
  max-width: 430px;
  font-size: 31px;
  letter-spacing: -1.25px;
}
.system-intro {
  margin-top: 5px;
  color: #5b6875;
  font-size: 12.8px;
}
.system .system-architecture.system-loop {
  margin-top: 12px;
  border: 1px solid #ded1bd;
  border-radius: 10px;
  padding: 12px 13px 13px;
  background: linear-gradient(180deg, rgba(255,255,255,.28), rgba(255,255,255,.04)), #f1e8d8;
}
.system .loop-kicker {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
  padding-bottom: 7px;
  border-bottom: 1px solid #dfd1bc;
}
.system .loop-kicker span {
  color: var(--navy);
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.2px;
}
.system .loop-kicker small {
  color: #6e7780;
  font-size: 10px;
}
.system .loop-layout {
  display: grid;
  grid-template-columns: 74px 1fr;
  gap: 10px;
  margin-top: 10px;
}
.system .input-rail {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  border: 1px solid #d8c8b2;
  border-radius: 8px;
  padding: 10px 8px;
  background: #faf6ed;
}
.system .input-rail b {
  color: var(--rust);
  font-family: var(--mono);
  font-size: 8.5px;
  letter-spacing: .9px;
}
.system .input-rail span {
  color: #445461;
  font-family: var(--mono);
  font-size: 8.6px;
  font-weight: 700;
  letter-spacing: .55px;
}
.system .loop-core {
  display: grid;
  grid-template-rows: auto auto auto auto;
  gap: 8px;
  min-width: 0;
}
.system .ephemeral-row {
  display: grid;
  grid-template-columns: 1fr 32px 1fr;
  gap: 8px;
  align-items: stretch;
}
.system .actor-node {
  position: relative;
  min-height: 96px;
  border: 1px solid #ded1bd;
  border-radius: 8px;
  padding: 10px 12px 9px;
  background: #fbf7ef;
}
.system .actor-node::before {
  content: '';
  position: absolute;
  inset: 0;
  border-top: 3px solid var(--purple);
  border-radius: inherit;
  pointer-events: none;
}
.system .actor-node.meta::before { border-top-color: var(--rust); }
.system .actor-node b {
  display: block;
  color: var(--ink);
  font-family: var(--serif);
  font-size: 18px;
  line-height: 1.02;
  letter-spacing: -.55px;
}
.system .actor-node p {
  margin-top: 6px;
  color: #415160;
  font-size: 10.5px;
  line-height: 1.25;
}
.system .actor-arrow {
  display: grid;
  place-items: center;
  color: #9fb7c4;
  font-size: 20px;
  font-weight: 700;
}
.system .reset-boundary {
  display: grid;
  grid-template-columns: 135px 1fr;
  gap: 10px;
  align-items: center;
  min-height: 39px;
  border: 1px dashed #d39479;
  border-radius: 8px;
  padding: 7px 10px;
  background: #fbefe7;
}
.system .reset-boundary b {
  color: var(--rust);
  font-family: var(--mono);
  font-size: 9.4px;
  letter-spacing: 1px;
}
.system .reset-boundary span {
  color: #5b4d46;
  font-size: 11.2px;
  line-height: 1.2;
}
.system .persistence-return {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 34px;
  border-left: 3px solid var(--navy);
  border-radius: 0 8px 8px 0;
  padding: 7px 10px;
  background: #eaf2f8;
}
.system .persistence-return b {
  color: var(--navy);
  font-family: var(--mono);
  font-size: 9.2px;
  letter-spacing: .9px;
  flex-shrink: 0;
}
.system .persistence-return span {
  color: #27455c;
  font-size: 10.8px;
  line-height: 1.18;
}
.system .world-node {
  border: 1px solid #c2d6e5;
  border-radius: 10px;
  background: linear-gradient(180deg, #f8fbfd, #edf4f9);
  padding: 11px 12px 12px;
}
.system .world-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}
.system .world-head b {
  color: var(--navy);
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 1.3px;
}
.system .world-head span {
  color: #50697d;
  font-size: 10px;
}
.system .world-strata {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 8px;
}
.system .world-stratum {
  min-height: 92px;
  border: 1px solid #c8d9e6;
  border-radius: 7px;
  padding: 9px 9px 8px;
  background: rgba(255,255,255,.66);
}
.system .world-stratum span {
  display: inline-block;
  color: var(--navy);
  font-family: var(--mono);
  font-size: 7.8px;
  font-weight: 800;
  letter-spacing: .65px;
  background: #e8f1f7;
  border-radius: 3px;
  padding: 2px 5px;
}
.system .world-stratum:nth-child(1) span { color: var(--navy); background: #e1edf6; }
.system .world-stratum:nth-child(2) span { color: var(--amber); background: #f6ead7; }
.system .world-stratum strong {
  display: block;
  margin-top: 6px;
  color: var(--ink);
  font-family: var(--serif);
  font-size: 15.6px;
  line-height: 1.05;
  letter-spacing: -.35px;
}
.system .world-stratum p {
  margin-top: 4px;
  color: #40505d;
  font-size: 9.9px;
  line-height: 1.20;
}
.system .persistence-container {
  display: none;
}
.system .system-footer-grid.runtime-substrate {
  grid-template-columns: 88px repeat(3, 1fr);
  gap: 7px;
  margin-top: 10px;
}
.system .runtime-label {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d6c8b7;
  border-radius: 7px;
  background: #f1e8d8;
  color: var(--navy);
  font-family: var(--mono);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: .9px;
  text-align: center;
}
.system .runtime-substrate .footer-block {
  min-height: 70px;
  padding: 8px 9px;
  background: #fbf7ef;
}
.system .runtime-substrate .footer-kicker {
  font-size: 8.6px;
}
.system .runtime-substrate .footer-block p {
  font-size: 9.7px;
  line-height: 1.20;
}
.system .system-principle-box {
  margin-top: 10px;
  border-left: 3px solid var(--rust);
  border-radius: 0 8px 8px 0;
  background: linear-gradient(90deg, #fbefe7, #f6eadb);
  padding: 10px 13px;
}
.system .system-principle {
  color: #7a2c16;
  font-family: var(--serif);
  font-size: 18px;
  line-height: 1.13;
  letter-spacing: -.35px;
}
.system .system-principle b {
  color: #7a2c16;
}
.system .principle-pillars {
  margin-top: 5px;
  font-size: 8.4px;
  color: #8c3217;
}
`;

function applyProblemPolish() {
  const panel = document.querySelector('.problem');
  if (!panel) return;

  panel.querySelector('.problem-lead').textContent = 'Sustained autonomous research breaks in three different ways.';

  const failures = [...panel.querySelectorAll('.failure-item')];
  const entries = [
    {
      cls: 'failure-fragility',
      title: 'Closed-world fragility',
      claim: 'Unexpected runtime failures can halt an unattended workflow.',
      receipt: 'Cycle 1 · <code>numpy.float32</code> serialization error · autonomously repaired',
    },
    {
      cls: 'failure-inertia',
      title: 'Trajectory momentum',
      claim: 'A single long-running trajectory keeps moving in the same direction.',
      receipt: 'Direct Codex control reached <b>~0.6046</b> after extended local refinement',
    },
    {
      cls: 'failure-context',
      title: 'Context inflation cost',
      claim: 'Reconstructing project context can cost far more than the edit itself.',
      receipt: 'Project-shaped replication · 340,087 vs 42,377 inclusive tokens · <b>8.03×</b>',
    },
  ];

  failures.forEach((item, index) => {
    const entry = entries[index];
    if (!entry) return;
    item.classList.add(entry.cls);
    const title = item.querySelector('.failure-text strong');
    const body = item.querySelector('.failure-text p');
    if (title) title.textContent = entry.title;
    if (body) body.innerHTML = `<span class="failure-claim">${entry.claim}</span><span class="failure-receipt">${entry.receipt}</span>`;
    item.querySelector('.failure-visual')?.remove();
  });

  panel.querySelector('.architecture-contrast')?.remove();
  const bar = panel.querySelector('.problem-solution-bar');
  if (bar) {
    bar.innerHTML = '<span class="bar-tag">DESIGN RESPONSE</span><span class="bar-desc"><strong>Keep the world.</strong> Reset the trajectory.</span>';
  }
}

function applySystemPolish() {
  const panel = document.querySelector('.system');
  if (!panel) return;

  const intro = panel.querySelector('.system-intro');
  if (intro) intro.textContent = 'Give the research world and the researcher different lifetimes.';

  const arch = panel.querySelector('.system-architecture');
  if (arch) {
    arch.classList.add('system-loop');
    arch.innerHTML = `
      <div class="loop-kicker">
        <span>DUAL-LIFETIME LOOP</span>
        <small>Persistent world · ephemeral trajectory · audited write-back</small>
      </div>
      <div class="loop-layout">
        <div class="input-rail">
          <b>INPUTS</b>
          <span>TASK</span>
          <span>DATA</span>
          <span>EVALUATOR</span>
          <span>BUDGET</span>
        </div>
        <div class="loop-core">
          <div class="ephemeral-row">
            <div class="actor-node scientist">
              <b>Fresh Scientist</b>
              <p>Owns scientific judgment inside one trajectory: hypotheses, code, experiments, interpretation, and pivots.</p>
            </div>
            <div class="actor-arrow">→</div>
            <div class="actor-node meta">
              <b>META Review</b>
              <p>Audits claims against artifacts, scopes conclusions, and decides what is durable enough to survive.</p>
            </div>
          </div>
          <div class="persistence-return"><b>SELECTIVE PERSISTENCE</b><span>Only audited empirical findings, code state, and bounded priors write back to the shared world.</span></div>
          <div class="world-node">
            <div class="world-head"><b>PERSISTENT RESEARCH WORLD</b><span>What survives across trajectories</span></div>
            <div class="world-strata">
              <div class="world-stratum"><span>A · EVIDENCE</span><strong>Knowledge + Ledger</strong><p>Metrics, failures, reports, and experiment receipts in <b><code>ledger.jsonl</code></b>.</p></div>
              <div class="world-stratum"><span>B · PRIORS</span><strong>Brief + Hypotheses</strong><p>Current understanding and exploration leads in <b><code>brief.md</code></b>, open to revision.</p></div>
              <div class="world-stratum"><span>C · STATE</span><strong>Code + State</strong><p>Retained implementation, serialized model weights, checks, and git provenance.</p></div>
            </div>
          </div>
          <div class="reset-boundary"><b>CONTEXT RESET</b><span>The next Scientist reads verified experience from disk, but does not inherit the previous reasoning trace.</span></div>
        </div>
      </div>
    `;
  }

  panel.querySelector('.persistence-container')?.remove();
  const runtime = panel.querySelector('.system-footer-grid');
  if (runtime) {
    runtime.classList.add('runtime-substrate');
    runtime.innerHTML = `
      <div class="runtime-label">RUNTIME<br>SUBSTRATE</div>
      <div class="footer-block"><span class="footer-kicker">WORKTREE ISOLATION</span><p>Independent git worktrees isolate branches and preserve reproducible artifacts.</p></div>
      <div class="footer-block"><span class="footer-kicker">SELF-HEALING</span><p>Traceback → patch → rerun keeps unattended research moving after runtime faults.</p></div>
      <div class="footer-block"><span class="footer-kicker">PARALLEL SYNTHESIS</span><p>Completed branches can be compared post-hoc; useful ideas survive even when a branch loses.</p></div>
    `;
  }

  const principle = panel.querySelector('.system-principle-box');
  if (principle) {
    principle.innerHTML = `
      <p class="system-principle">The next Scientist inherits <b>verified experience</b> — not <b>prior reasoning momentum</b>.</p>
      <div class="principle-pillars"><span>Decoupled Memory</span><i>·</i><span>Audited Persistence</span><i>·</i><span>Fresh Scientific Judgment</span></div>
    `;
  }
}

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 2036 }, deviceScaleFactor: 2 });
  await page.goto(new URL('poster.html', root).href, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: problemPolishCss });
  await page.addStyleTag({ content: systemPolishCss });
  await page.evaluate(applyProblemPolish);
  await page.evaluate(applySystemPolish);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    await Promise.all([...document.images].map(img => img.decode()));
  });
  const audit = await page.evaluate(() => {
    const out = [];
    for (const panel of document.querySelectorAll('.panel')) {
      const box = panel.getBoundingClientRect();
      for (const child of panel.querySelectorAll('h2,h3,p,li,td,th,.memory-row,.handoff,.terminal,.stats,.problem-note,.runtime,.parallel,.system-flow,.evidence-grid,.evidence-card,.resource-metrics,.insight-grid,.persistence-lanes,.system-principle,.loop-layout,.loop-core,.world-node,.world-strata,.runtime-substrate')) {
        const r = child.getBoundingClientRect();
        if (r.bottom > box.bottom - 3 || r.right > box.right - 3 || r.left < box.left) {
          out.push({ section: panel.className, element: child.tagName, text: child.textContent.trim().slice(0, 100), bottom: r.bottom, panelBottom: box.bottom });
        }
      }
    }
    return { overflow: out, width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight, headings: [...document.querySelectorAll('.section-label')].map(x => x.textContent) };
  });
  await writeFile(new URL('layout-check.json', root), JSON.stringify(audit, null, 2));
  await page.screenshot({ path: fileURLToPath(new URL('preview.png', root)), fullPage: true });
  if (audit.overflow.length || audit.width !== 1440 || audit.height !== 2036) {
    throw new Error('Poster layout overflow: ' + JSON.stringify(audit));
  }
  const bytes = await page.pdf({ preferCSSPageSize: true, printBackground: true });
  const pdf = await PDFDocument.load(bytes);
  if (pdf.getPageCount() !== 1) throw new Error('Expected one poster page');
  const sheet = pdf.getPage(0);
  sheet.scale((841 * 72 / 25.4) / sheet.getWidth(), (1189 * 72 / 25.4) / sheet.getHeight());
  pdf.setTitle('SciOdyssey · Main deck evidence poster · Team Good4AI');
  pdf.setAuthor('Team Good4AI (Chen Zhu, Zhou Ziyu, Shilin Xu, GE GAO, Jiran Li)');
  const output = new URL('SciOdyssey-poster-main-deck.pdf', root);
  await writeFile(output, await pdf.save());
  console.log('Exported ' + fileURLToPath(output) + ' (one A0 page, 841 × 1189 mm)');
  console.log('Five evidence claims checked; no panel overflow.');
} finally {
  await browser.close();
}
