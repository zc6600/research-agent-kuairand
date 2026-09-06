# SciOdyssey product film

Remotion compositions and shot scripts that reinterpret the SciOdyssey / Research Agent slides as continuous evidence-driven product stories.

## Requirements

Use Node.js with npm. From this directory, install the exact locked dependency tree:

```bash
npm ci
```

## Preview

```bash
npm run dev
```

Open Remotion Studio and select a composition from the organized groups:

- `SciOdysseyFilm` — launch-film narrative
- `SciOdysseyUXFilm` — existing UX-led cut
- `SciOdysseyUXWorkflowFilm` — terminal-first workflow cut; the existing UX cut remains intact
- `SciOdysseyKeynoteFilm` — independent 72-second camera-led comparison cut
- `SciOdysseyProductFilm` — first 3-minute product-film cut
- `SciOdysseyProductFilmV2` — camera-led 3-minute product film with the keynote embedded in the story

To verify the source without rendering a full film:

```bash
npm run build
npx tsc --noEmit
npm run render:still
```

Generated bundles, previews, and rendered films are ignored by Git; source scripts, compositions, assets, and replaceable audio remain in the repository.

## Render

```bash
npm run render
```

The 75-second H.264 master is written to `out/films/sciodyssey-film.mp4`.

To render the keynote-style UX cut:

```bash
npm run render:ux
```

The video is written to `out/films/sciodyssey-ux-film.mp4`.

The composition accepts optional `voiceOverSrc` and `musicSrc` props in `FilmProps`; audio can be added later without changing the scene structure.

To render the terminal-first workflow cut:

```bash
npm run render:ux-workflow
```

The video is written to `out/films/sciodyssey-ux-workflow-film.mp4`.

To render the new camera-led comparison cut:

```bash
npm run render:keynote
```

The video is written to `out/films/sciodyssey-keynote-film.mp4`.
Read the [shot script](scripts/keynote-v1.md) and [composition notes](src/compositions/keynote/README.md).
The new cut includes replaceable synthesized sound design; voice-over is scripted but not recorded.

To render the first product-film cut:

```bash
npm run render:product
```

The video is written to `out/films/sciodyssey-product-film.mp4`.

To render the V2 product film:

```bash
npm run render:product-v2
```

The video is written to `out/films/sciodyssey-product-film-v2.mp4`.
Read the [V2 revision script](src/compositions/product/SciOdysseyProductFilmV2RevisionScript.md). The V2 cut starts with the product surface, keeps one white visual world, places the keynote after the capability overview, and moves the terminal walkthrough to the final third. Dark contrast is reserved for terminal and evidence objects. Existing keynote footage remains available as its own composition.

## Folder layout

```text
src/
  compositions/
    launch/       # original launch-film composition
    ux/           # existing UX cut + terminal-first workflow cut
    keynote/      # independent camera-led comparison cut and scenes
  shared/         # shared visual system and base styles
public/assets/    # dashboard and research visual assets
public/audio/     # replaceable audio, grouped by composition
scripts/          # shot scripts and asset generation
out/
  films/          # rendered video masters
  previews/       # frame stills grouped by composition
```
