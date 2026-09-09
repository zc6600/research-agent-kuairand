import { chromium } from 'playwright-chromium';
import { PDFDocument } from 'pdf-lib';
import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('./', import.meta.url);
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 2036 }, deviceScaleFactor: 2 });
  await page.goto(new URL('poster.html', root).href, { waitUntil: 'networkidle' });
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
