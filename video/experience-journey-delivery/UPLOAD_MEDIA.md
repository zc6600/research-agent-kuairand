# Add the original media files without recompression

The metadata and timing files in this folder are already committed. Add these exact binary files to this same folder **without transcoding or recompression**:

1. `SciOdyssey_ExperienceJourney_HTML_Gwyneth_Final_1080p.mp4`
   - 9,650,230 bytes
   - 127.2 s · 1920×1080 · 30 fps · H.264 + AAC
   - SHA-256: `2af83d8f8854266ce660107c83600fb97964d054308ddc21e61d36c31e998010`
2. `SciOdyssey.m4a`
   - 842,779 bytes
   - 98.453333 s
   - SHA-256: `4b4ed4efb6b34fee6814f093a381953902e1e2891204b999d070a1c5e0375f7a`
3. `SciOdyssey_ExperienceJourney_aligned_voice.wav` (optional but recommended as the editable audio master)
   - 12,211,244 bytes
   - 127.2 s
   - SHA-256: `f310df3c08761eb69a21a498cf2c8ad7fb424cb80d971831b51a329baadb0e86`

All three files are below GitHub's normal 100 MB Git object limit. Uploading/copying the original files as-is does not reduce video or audio quality.

After upload, verify from the repository root:

```bash
cd video/experience-journey-delivery
sha256sum -c SHA256SUMS.txt
```

The final MP4 should be archived byte-for-byte; do not run it through another video encoder just to upload it.
