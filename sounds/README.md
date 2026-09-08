# SciOdyssey Voice Assets

This folder stores the approved voice reference and generation profile for SciOdyssey narration.

## Approved default voice

- Provider: AI Voice Generator
- Voice ID: `clear`
- Intended use: English narration for SciOdyssey slides and product videos
- Selection date: 2026-09-08
- Status: **Approved as the default voice for future narration**

## Reference sample

Preview:
https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/1626185d-173a-4706-8bac-a87c5f84c4f6.mp3

Full generated audio page:
https://www.aidocmaker.com/g0/audio?name=a962aee5cbb04cb18a9271ff2ac5b47c

Generation context ID: `a962aee5cbb04cb18a9271ff2ac5b47c`

Reference transcript:

> What if an AI research agent could do more than answer a question? What if it could explore, fail, recover, and keep going — while preserving only the evidence that truly matters? This is SciOdyssey: a long-horizon autonomous machine learning research agent.

## Narration guidance

For future SciOdyssey audio, prefer this `clear` voice and write narration with natural presentation rhythm: short clauses, deliberate pauses, rhetorical questions where appropriate, and explicit emphasis on key claims and metrics. Avoid flat sentence-by-sentence reading.

## Note

The voice-generation connector exposes the generated audio through hosted playback URLs rather than a local binary attachment, so this commit preserves the approved voice profile and its reference audio source. If a local MP3/WAV becomes available later, place it in this folder without changing the approved `clear` voice profile.
