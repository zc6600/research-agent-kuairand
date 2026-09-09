import { chromium } from 'playwright-chromium';
import { PDFDocument } from 'pdf-lib';
import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const stem = 'SciOdyssey_HD_三问题_1234567顺序版';
const root = new URL('./', import.meta.url);
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1120, height: 2400 }, deviceScaleFactor: 2 });
  await page.goto(new URL(stem + '.html', root).href, { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'screen' });
  await page.addStyleTag({ content: 'html,body,.site-shell{margin:0!important;padding:0!important;min-height:0!important;background:white!important}.toolbar{display:none!important}.poster{width:1080px!important;margin:0!important;box-shadow:none!important}' });
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(image => image.decode()));
  });
  const audit = await page.evaluate(() => {
    const overflow = [];
    for (const panel of document.querySelectorAll('.panel')) {
      const box = panel.getBoundingClientRect();
      for (const child of panel.querySelectorAll('h3,h4,p,table,.failure-grid,.design-response,.runtime,.stats,.cycle-summary,.terminal,.insight-grid')) {
        const rect = child.getBoundingClientRect();
        if (rect.bottom > box.bottom - 2 || rect.right > box.right + 1 || rect.left < box.left - 1) overflow.push({ panel: panel.className, text: child.textContent.slice(0,80) });
      }
    }
    return { overflow, missingImages: [...document.images].filter(image => !image.naturalWidth).length };
  });
  if (audit.overflow.length || audit.missingImages) throw new Error(JSON.stringify(audit));
  const box = await page.locator('.poster').boundingBox();
  const raw = await page.pdf({ width: box.width + 'px', height: (Math.ceil(box.height) + 2) + 'px', printBackground: true, preferCSSPageSize: false, margin: { top:0,right:0,bottom:0,left:0 } });
  const source = await PDFDocument.load(raw);
  if (source.getPageCount() !== 1) throw new Error('Source poster must have one page');
  const pdf = await PDFDocument.create();
  const [embedded] = await pdf.embedPdf(raw);
  const sheet = pdf.addPage([594 * 72 / 25.4, 841 * 72 / 25.4]);
  const scale = Math.min(sheet.getWidth()/embedded.width,sheet.getHeight()/embedded.height);
  const width = embedded.width*scale, height = embedded.height*scale;
  sheet.drawPage(embedded,{x:(sheet.getWidth()-width)/2,y:(sheet.getHeight()-height)/2,width,height});
  pdf.setTitle('SciOdyssey - Latest main deck - A1');
  const output = fileURLToPath(new URL(stem + '.pdf',root));
  await writeFile(output,await pdf.save());
  execFileSync('gs',['-q','-dSAFER','-dBATCH','-dNOPAUSE','-sDEVICE=png16m','-r150','-dTextAlphaBits=4','-dGraphicsAlphaBits=4','-sOutputFile='+fileURLToPath(new URL(stem+'.png',root)),output]);
  console.log(JSON.stringify({pages:pdf.getPageCount(),millimeters:[594,841],layout:audit,vector:true}));
} finally {
  await browser.close();
}
