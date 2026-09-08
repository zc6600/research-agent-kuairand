#!/usr/bin/env bash
set -euo pipefail

VIDEO="${1:-experience-journey-html-1080p.mp4}"
AUDIO="${2:-SciOdyssey_ExperienceJourney_aligned_voice.wav}"
OUT="${3:-SciOdyssey_ExperienceJourney_HTML_Gwyneth_Final_1080p.mp4}"

# Preserve the already-rendered HTML video bitstream exactly.
# Only the audio is encoded to AAC for MP4 compatibility.
ffmpeg -y \
  -i "$VIDEO" \
  -i "$AUDIO" \
  -map 0:v:0 \
  -map 1:a:0 \
  -c:v copy \
  -c:a aac -b:a 256k -ar 48000 -ac 2 \
  -t 127.2 \
  -movflags +faststart \
  "$OUT"

ffprobe -v error \
  -show_entries format=duration:stream=codec_name,codec_type,width,height,sample_rate,channels \
  -of default=noprint_wrappers=1 \
  "$OUT"
