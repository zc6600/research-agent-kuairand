# Keynote comparison cut

Independent 72-second Remotion composition: `SciOdysseyKeynoteFilm`.
Creative script: [`../../../scripts/keynote-v1.md`](../../../scripts/keynote-v1.md).

The persistent window in `SciOdysseyKeynoteFilm.tsx` owns camera framing and geometry.
`scenes/` owns terminal operations, recorded evidence, human choice, agent integration,
and the bookends. `components.tsx` contains typed commands and window primitives;
`motion.ts` contains deterministic timing, colors, and optional narration subtitles.
All selectors are prefixed with `kn-`; existing UX effects are not edited.

Run from `video/`:

```sh
npm run dev
npm run render:keynote
```

Studio: select `SciOdysseyKeynoteFilm` to compare with `SciOdysseyUXWorkflowFilm`.
MP4: `out/films/sciodyssey-keynote-film.mp4`.
Stills: `out/previews/keynote/`.

Props: `soundDesign` defaults to true; `showSubtitles` defaults to false.
Optional `voiceOverSrc`, `musicSrc`, `soundEffectsSrc` accept media URLs and override
the corresponding track. No recorded voice-over is included. Local media belongs
in `public/`; use `staticFile()` when passing a local asset from code.

`npm run audio:keynote` regenerates the original synthesized score and cue WAVs in
`public/audio/keynote/`. The generator uses fixed timing and seeded noise, contains
no external samples, and checks for clipping. This is placeholder sound design for
comparing pacing; replace it when finishing the film.

Dashboard frames use the existing screenshots unmodified; the final metric close-up
re-typesets the exact displayed value `0.605936` as sharp vector text.
They are labeled as a recorded public-validation case, not results from the
illustrative parallel workflow. Agent UI is a labeled interaction concept.
