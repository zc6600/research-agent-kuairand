# SciOdyssey project website

A standalone, dependency-free introduction to **Long-Horizon Autonomous ML Research**. The website is redesigned from the current `slides/slides.md` and its components, with the slide deck's three capabilities—**Robust, Supervisable, Broad Search**—as the entry point.

## Preview locally

From the repository root:

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory website
```

Open <http://localhost:8080>. Any static host can serve `website/`; no build, package installation, API keys, or backend is required.

## Visual identity

SciOdyssey uses a cool white, navy, and electric-blue palette, geometric sans-serif typography, and a custom branching S-path mark shared by the header and favicon. Supported harnesses are identified by name in a separate compatibility row.

## Content and interactions

- Three interactive capability scenes: runtime recovery, supervision, independent parallel search.
- The ML experimentation loop and expandable failure-mode insights.
- An interactive system map: Research World, Scientist, META, and harness/runtime.
- Six user-controlled walkthrough acts: define, step, run, parallel, dashboard, skill.
- Research-cycle inspection, exact validation metrics, score/token comparisons, and a resource ledger.
- Model depth/breadth exploration and parallel-branch evidence inspection.
- Setup-command copying and mobile navigation.

Demos illustrate the workflow; they do not run research commands or connect to live telemetry. All fonts and assets are local. Tabs support arrow keys, Home, and End; disclosure buttons support keyboard use; motion follows the system's reduced-motion preference.

## Source of truth

- `../slides/slides.md`: product framing, scope, resource accounting, and direct-agent score/token comparison.
- `../slides/components/ProblemInsights.vue` and its three card components: fixed recovery paths, momentum and validity, and repeated context costs.
- `../slides/components/ExperienceJourney.vue`: six-act user experience.
- `../slides/components/EvaluationTrajectory.vue` and `EvaluationCardBody.vue`: retained cycle and validation metrics.
- `../slides/components/ModelRotationInsight.vue` and `ParallelResearchInsight.vue`: qualified findings.
- `../README.md`: executable setup commands, lifecycle semantics, and team links.

The retained result, Gemini-only comparator, and reconstructed parallel study are distinct records. Public-validation metrics must not be labeled hidden-test scores. The ~$10 project estimate must stay separate from run-level token telemetry. Keep these boundaries when updating copy.

The custom vector mark is `assets/brand-mark.svg`. The hero artwork comes from `slides/public/assets/research-world-cover.png`. Previously copied agent icons and their license file remain available in `assets/`; the compatibility row uses text labels.

## Primary links

- Repository: <https://github.com/zc6600/research-agent-kuairand>
- Slide deck: <https://slides.sciodyssey.zc6600.wiki>
- Final report: <https://github.com/zc6600/research-agent-kuairand/blob/main/docs/FINAL_REPORT.md>
