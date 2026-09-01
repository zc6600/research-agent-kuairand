# TechJam submission bundle scope

This directory is packaged as the compact supplemental bundle for TikTok
TechJam 2026, Problem 2 (KuaiRand-Pure). It is intentionally kept well below
the 35 MB attachment limit supplied for the submission form.

The current Problem 2 statement does not require a video; the detailed report
and dashboard screenshots in this bundle are the primary asynchronous
presentation. A short video remains optional/recommended if the Devpost form
or judging workflow later asks for one.

The bundle contains the runnable Research Agent implementation, the
KuaiRand-Pure task contract and starter evaluator, the final report and
figures, the retained E001-E013 research record, the checked final prediction
file, compact baseline comparisons, and the measured token/GPU accounting.

The bundle deliberately does not contain raw KuaiRand data, virtual
environments, caches, credentials, or the large generated prediction/log
files from exploratory research worlds. Those artifacts are not needed to
reproduce the submitted recipe and are preserved separately in the public
repository when their provenance is relevant.

The retained run used 4 autonomous META–Scientist cycles out of the
50-iteration cap, with 13 named E001–E013 experiments (7 Full evaluations),
1h 55m 29s agent wall-clock, 6,833,808 non-cache input+output tokens, and
0 GPU-hours.

For the complete submission context, start with `README.md` at the bundle
root, then read `docs/FINAL_REPORT.md` and
`submission/research-agent-kuairand/README.md`.
