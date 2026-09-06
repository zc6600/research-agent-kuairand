# SciOdyssey · Research voyage poster

Independent A0 portrait poster following the supplied WeChat reference: warm ivory, Prussian blue and burnt sienna, serif headings, maritime illustration and six bordered sections.

- Open `poster.html` for editable HTML/CSS source.
- Print `SciOdyssey-poster-voyage.pdf` at A0 (841 × 1189 mm).
- Share `SciOdyssey-poster-voyage.png` as a high-resolution image.
- Rebuild from this directory with `node export.mjs` after installing the existing dependencies in `slides/`.
- `preview.png` and `layout-check.json` are local QA outputs, ignored by Git.

Content and data: `../../poster.md`, `../../../docs/ARCHITECTURE.md` and `../../../docs/FINAL_REPORT.md` §§3–5. The comparison chart preserves the measured token counts, score qualifiers and accounting interval from the existing poster. It does not imply causality or statistical significance.

Typography: Arial for body text and Georgia for editorial headings; Menlo for the example input. PDF text and the comparison chart remain vector content. The hero is a generated editorial illustration, not a photograph of an actual research event. It was created with the built-in image generation tool. The exact prompt is stored in `assets/prompt.txt`.

This poster does not replace the original poster or the presentation variants.

To regenerate the shareable PNG after exporting:

```sh
gs -q -dSAFER -dBATCH -dNOPAUSE -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -sDEVICE=png16m -r96 -sOutputFile=SciOdyssey-poster-voyage.png SciOdyssey-poster-voyage.pdf
```
