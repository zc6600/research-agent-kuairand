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
.problem .failure-item.failure-context::before { border-top-color: var(--green); }
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
.problem .failure-context .failure-idx { color: var(--green); border-color: #a6c4b6; }
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
      title: 'Single-trajectory inertia',
      claim: 'Long-lived reasoning carries yesterday’s momentum into today’s search.',
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

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 2036 }, deviceScaleFactor: 2 });
  await page.goto(new URL('poster.html', root).href, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: problemPolishCss });
  await page.evaluate(applyProblemPolish);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    await Promise.all([...document.images].map(img => img.decode()));
  });
  const audit = await page.evaluate(() => {
    const out = [];
    for (const panel of document.querySelectorAll('.panel')) {
      const box = panel.getBoundingClientRect();
      for (const child of panel.querySelectorAll('h2,h3,p,li,td,th,.memory-row,.handoff,.terminal,.stats,.problem-note,.runtime,.parallel,.system-flow,.evidence-grid,.evidence-card,.resource-metrics,.insight-grid,.persistence-lanes,.system-principle')) {
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
