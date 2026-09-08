# SciOdyssey ExperienceJourney delivery package

This folder packages the approved narration setup and the exact subtitle timing used for the Slidev `ExperienceJourney` demo.

## Source of truth

- Slide deck: `slides/slides.md`
- HTML/Vue animation: `slides/components/ExperienceJourney.vue`
- Matching narration script: `video/scripts/slides-ux-voiceover-en.md`
- Nominal animation duration: **127.2 s**

The narration is aligned to the subtitle cues already embedded in `ExperienceJourney.vue`; no extra black subtitle bar should be added.

## Approved voice

- Provider: **Speechify**
- Voice: **Gwyneth Paltrow**
- Locale: **en-US**
- Speed: **1.0x**
- Style: clear, natural, calm product walkthrough; presentation-friendly, not an advertising read

See `voice-profile.md` for details.

## Media files

The intended media filenames are:

- `SciOdyssey_ExperienceJourney_HTML_Gwyneth_Final_1080p.mp4`
  - final 1920×1080, 30 fps H.264 + AAC delivery
  - duration: 127.2 s
  - SHA-256: `2af83d8f8854266ce660107c83600fb97964d054308ddc21e61d36c31e998010`
- `SciOdyssey.m4a`
  - uploaded source narration used for alignment
  - duration: 98.453333 s
  - SHA-256: `4b4ed4efb6b34fee6814f093a381953902e1e2891204b999d070a1c5e0375f7a`
- `SciOdyssey_ExperienceJourney_aligned_voice.wav`
  - 127.2 s cue-aligned narration master
  - SHA-256: `b8d8e1a3567581269b73905c40d072c296bff190b3c799bb8ed5c3567af60844`

`subtitle-cues.json` records the 19 exact cue windows and text.

## Quality policy

Do **not** recompress an already-rendered final MP4 merely to move or archive it. If the HTML animation is already rendered at the desired resolution, mux the aligned audio with `-c:v copy` so the video bitstream stays unchanged. See `merge-final.sh`.

For the sharpest final submission, render the original Slidev/HTML animation natively at 1920×1080 (or higher) before muxing audio, rather than upscaling a lower-resolution recording.
