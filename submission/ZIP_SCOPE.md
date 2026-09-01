# TechJam submission bundle scope

This directory is packaged as the compact supplemental bundle for TikTok
TechJam 2026, Problem 2 (KuaiRand-Pure). It is intentionally kept well below
the 35 MB attachment limit supplied for the submission form.

The current Problem 2 statement does not require a video. The public repository
provides the full written report and dashboard screenshots for asynchronous
review.

This compact bundle contains `research-agent-kuairand/`: the runnable submitted
implementation, KuaiRand-Pure task contract and Starter Kit, retained E001-E013
research record, checked final prediction file, evidence, diffs, telemetry, and
resource accounting. The full report and figures remain in the public
repository and are not duplicated here.

The bundle deliberately does not contain raw KuaiRand data, virtual
environments, caches, credentials, or the large generated prediction/log
files from exploratory research worlds. Those artifacts are not needed to
reproduce the submitted recipe and are preserved separately in the public
repository when their provenance is relevant.

The retained run used 4 autonomous META–Scientist cycles out of the
50-iteration cap, with 13 named E001–E013 experiments (7 Full evaluations),
1h 55m 29s agent wall-clock, 48,240,128 total input+output tokens including
cache-read input, and 0 GPU-hours.

Start with `research-agent-kuairand/README.md`. For the complete project context,
use the root README and `docs/FINAL_REPORT.md` in the public repository.
