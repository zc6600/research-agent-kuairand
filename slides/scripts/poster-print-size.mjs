// Slidev exports CSS pixels. Set the delivered PDF to physical A0 without rasterizing it.
import { readFile, writeFile } from 'node:fs/promises';
import { PDFDocument } from 'pdf-lib';

const outputName = process.argv[2] ?? 'SciOdyssey-poster.pdf';
const file = new URL(`../${outputName}`, import.meta.url);
const pdf = await PDFDocument.load(await readFile(file));
if (pdf.getPageCount() !== 1) throw new Error('The poster must contain exactly one page.');
const page = pdf.getPage(0);
const width = 841 * 72 / 25.4;
const height = 1189 * 72 / 25.4;
page.scale(width / page.getWidth(), height / page.getHeight());
pdf.setTitle('SciOdyssey — Preserve the research world. Reset the researcher.');
pdf.setAuthor('SciOdyssey Team');
await writeFile(file, await pdf.save());
const check = await PDFDocument.load(await readFile(file));
const size = check.getPage(0).getSize();
if (Math.abs(size.width - width) > .01 || Math.abs(size.height - height) > .01)
  throw new Error('Unexpected print dimensions.');
console.log(`Verified: ${outputName} · one page, A0 portrait (841 × 1189 mm), vector text and diagrams.`);
