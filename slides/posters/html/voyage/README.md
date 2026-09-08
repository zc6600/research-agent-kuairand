# SciOdyssey · Research voyage poster

Independent A0 portrait poster following the supplied WeChat reference: warm ivory, Prussian blue and burnt sienna, serif headings, maritime illustration and six bordered sections.

- Open `poster.html` for editable HTML/CSS source.
- Print `SciOdyssey-poster-voyage.pdf` at A0 (841 × 1189 mm).
- Share `SciOdyssey-poster-voyage.png` as a high-resolution image.
- Rebuild from this directory with `node export.mjs` after installing the existing dependencies in `slides/`.
- `preview.png` and `layout-check.json` are local QA outputs, ignored by Git.

Content and data: `../../slidev/poster.md`, `../../../../docs/ARCHITECTURE.md` and `../../../../docs/FINAL_REPORT.md` §§3–5. The comparison chart preserves the measured token counts, score qualifiers and accounting interval from the existing poster. It does not imply causality or statistical significance.

Typography: Times New Roman for the narrow editorial headings, Arial for the wordmark, Arial Narrow for compact body copy and labels, SignPainter for the handwritten signature, and Menlo for the example input. PDF text and the comparison chart remain vector content.

The revised composition matches the reference's header and section proportions, including the globe vignette, handwritten signature, blue/red line icons, subtle paper texture and white result inset. The header, globe and paper are generated illustrations made with the built-in image tool. The revised prompts are in `assets/prompts-v2.txt`; `assets/prompt.txt` records the first draft. Carbon icons come from the existing `@iconify-json/carbon` dependency (IBM, Apache-2.0).

The scatter plot uses the unchanged measured token counts and public-validation scores, with a tighter plotting area to match the reference. The Cycle-2 token interval is an accounting bound, and the Codex point remains provisional. “Any ML task” expresses the interface's intended scope, not evidence of validation across tasks.

This poster does not replace the original poster or the presentation variants.

To regenerate the shareable PNG after exporting:

```sh
gs -q -dSAFER -dBATCH -dNOPAUSE -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -sDEVICE=png16m -r96 -sOutputFile=SciOdyssey-poster-voyage.png SciOdyssey-poster-voyage.pdf
```
