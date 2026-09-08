# Poster sources

Poster work is split by implementation type:

- `slidev/` contains the four Slidev sources used by the root `slides/package.json` scripts.
- `html/voyage/` contains the independent Voyage HTML/CSS poster.
- `html/main-deck-update/` contains the independent evidence-focused HTML/CSS poster.

Run the commands from the `slides/` directory:

```bash
npm run poster:export
npm run poster:variants
npm run poster:html:voyage
npm run poster:html:main-deck
```

Slidev PDFs are written to `../exports/current/`. The HTML projects keep their
PDF, preview, and layout QA files beside their editable source files so each
project remains self-contained.
