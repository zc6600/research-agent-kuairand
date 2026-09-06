# 01 — Editorial Contrast

An independent Slidev variant of the SciOdyssey deck.

## Design direction

- Keeps the shared Slidev template contract: 16:9 canvas, Avenir Next / Fira Code, white ground, orange-led accent language, and the existing chapter/kicker system.
- Uses an editorial / Swiss composition inside that system: asymmetric columns, shared left baselines, stronger type scale, quiet hairline rules, and fewer ornamental containers.
- Lets the content provide the variation: the entry slide treats `task.md` and `PERSONAL.md` as two aligned briefs; architecture uses the persistence boundary as the visual hinge; branching and evidence use a single orange path to mark the retained decision.
- Keeps the research claims and examples from `README.md`, `docs/project_story.md`, and `docs/FINAL_REPORT.md`. Reference copies used while making this variant live in `reference/`.

## Run

```bash
npm install
npm run dev
npm run build
```

The variant is intentionally self-contained. It does not import the main deck's stylesheet at runtime and does not modify `slides/slides.md` or `slides/styles/theme.css`.
