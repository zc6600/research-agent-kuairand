import { readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const slidesRoot = fileURLToPath(new URL('../', import.meta.url));
const fromSlides = (relativePath) => resolve(slidesRoot, relativePath);

const requiredFiles = [
  'exports/current/SciOdyssey-main.pdf',
  'exports/current/SciOdyssey-poster.pdf',
  'exports/current/SciOdyssey-poster-editorial.pdf',
  'exports/current/SciOdyssey-poster-evidence.pdf',
  'exports/current/SciOdyssey-poster-type.pdf',
  'posters/slidev/poster.md',
  'posters/slidev/poster-editorial.md',
  'posters/slidev/poster-evidence.md',
  'posters/slidev/poster-type.md',
  'posters/html/voyage/poster.html',
  'posters/html/main-deck-update/poster.html',
];

const archivedEditionFiles = [
  'exports/archive/editions/3d/SciOdyssey-3d.pdf',
  'exports/archive/editions/voyage/SciOdyssey-voyage.pdf',
  'archive/editions/3d/slides.md',
  'archive/editions/voyage/slides.md',
];

const missing = requiredFiles.filter((relativePath) => !existsSync(fromSlides(relativePath)));
const missingArchivedEditions = archivedEditionFiles.filter((relativePath) => !existsSync(fromSlides(relativePath)));
const archiveEntries = await readdir(fromSlides('exports/archive/main-explorations'));
const rootEntries = await readdir(slidesRoot, { withFileTypes: true });
const unexpectedRootPdfs = rootEntries
  .filter((entry) => entry.isFile() && entry.name.endsWith('.pdf') && entry.name !== 'research-agent.pdf')
  .map((entry) => entry.name);

if (missing.length || missingArchivedEditions.length || !archiveEntries.length || unexpectedRootPdfs.length) {
  if (missing.length) console.error(`Missing expected paths:\n${missing.map((path) => `- ${path}`).join('\n')}`);
  if (missingArchivedEditions.length) console.error(`Missing archived edition paths:\n${missingArchivedEditions.map((path) => `- ${path}`).join('\n')}`);
  if (!archiveEntries.length) console.error('Archive directory is empty: exports/archive/main-explorations/');
  if (unexpectedRootPdfs.length) console.error(`Unexpected root PDFs:\n${unexpectedRootPdfs.map((path) => `- ${path}`).join('\n')}`);
  process.exitCode = 1;
} else {
  console.log(`OK: ${requiredFiles.length} current paths, ${archivedEditionFiles.length} archived edition paths, ${archiveEntries.length} archived exports, no unexpected root PDFs.`);
}
