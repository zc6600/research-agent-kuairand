# SciOdyssey Product Film — V2 Script

**Working title:** `The Search Continues`<br>
**Product:** SciOdyssey / Research Agent<br>
**Format:** 16:9, 1920×1080, 30fps, exactly 03:00<br>
**Status:** script and visual direction only; V1 remains untouched until this version is approved.

## 1. Creative reset

V1 explains the product as a sequence of pages. V2 should sell the feeling of the product: a question enters a coding-agent session, becomes a living research world, branches into alternatives, and comes back as evidence a human can trust.

The film should feel closer to an Apple product film than to a deck:

- No persistent chapter header, footer, progress bar, or slide-like layout.
- No static comparison table. The comparison happens through a moving before/after state.
- No parallel branch before the viewer understands the basic research loop. Parallel is introduced only after the first path reaches a decision point.
- No long hold on one dashboard. Every interface is a physical object the camera enters, crosses, or leaves.
- Typography is sparse and decisive. The moving system is the hero; copy punctuates the motion.
- The existing keynote is a 26-second piece inside the story, entered through a match cut and exited through its result. It is not presented as another page.

### Logline

> A prompt can start a task. SciOdyssey keeps the search alive — across cycles, agents, branches, and the evidence that makes a result worth keeping.

### Narrative spine

```text
question → run → evidence → one path → parallel search → replaceable agent → proof → resume
```

This order is deliberate. The audience first understands why a persistent research layer exists, then sees how to use it, then sees the keynote demonstrate the loop, and only then sees parallelism and model interchange as extensions of the same world.

## 2. Camera and editorial language

### Camera grammar

- **The camera always follows a subject.** The subject is a cursor, a colored trajectory, a file, a metric, or the human selection point.
- **Use depth, not panels.** Foreground code passes close to lens; the research world sits behind it; evidence comes forward only when earned.
- **Cut on motion.** A typed command becomes a path; a path becomes a graph edge; a graph edge becomes a dashboard rule; a dashboard rule becomes a score line.
- **Use three scales.** Wide world reveal, medium system interaction, extreme macro detail. Avoid the single medium-scale “slide” view.
- **Use speed contrast.** 8–12 frame impacts for keystrokes, branch splits, and result locks; 45–90 frame glides for world reveals and transitions.
- **Keep the eye busy with one dominant motion.** Secondary motion is texture only: grain, tiny pulses, cursor blink, data ticks, or parallax.

### Visual arc

1. **Dark / unfinished:** a question and a stalled session.
2. **White / alive:** SciOdyssey reveals a persistent world.
3. **Blue, violet, and orange:** cycles, evidence, and competing trajectories gain energy.
4. **High-contrast proof:** the result is quiet, legible, and earned.
5. **White / resolved:** the search continues after the film ends.

### Sound arc

The V2 cut needs voiceover and a proper sound pass. The existing keynote score and cues can be used as a temp bed, but they should not be the final mix.

- 00:00: near-silence, one key press, low sub pulse.
- 00:16: hard stop and room tone when the prompt ends.
- 00:31: tonal lift and a clean brand reveal.
- 00:47–01:10: precise typing, disk clicks, restrained rhythmic pulse.
- 01:10–01:36: keynote sound world; let the old film briefly take over.
- 01:36–02:18: tempo and stereo width increase as paths branch and runtimes swap.
- 02:18–02:42: music drops around the score, then resolves on evidence.
- 02:42–03:00: one resume keystroke, warm resolve, final silence after the mark.

## 3. Three-minute script

### 00:00–00:16 — COLD OPEN / A QUESTION ENTERS

**Visual and camera**

1. **00:00–00:04 — extreme macro.** Black field. A cursor blinks inside an empty terminal. The camera is almost inside the phosphor; no logo, no UI frame.
2. **00:04–00:09 — rack focus.** The question types itself one phrase at a time: `CAN A QUESTION KEEP GOING?` The final question mark lands with a physical click.
3. **00:09–00:13 — forward dolly.** The command line appears beneath it and begins to run. The terminal text becomes a luminous blue trajectory; the camera follows the trajectory through `task.md`, an experiment folder, a validation mark, and a small rising metric.
4. **00:13–00:16 — abrupt stop.** The trajectory freezes at `cycle 01 / awaiting next action`. The cursor returns. Hold only long enough for the viewer to feel the interruption.

**Voiceover — English draft**

> Every research project begins with a question. But a prompt is not a research system.

**On-screen copy**

```text
CAN A QUESTION KEEP GOING?
```

**Sound**

One dry keystroke, a low digital motor, three fast data ticks, then a hard mute on the stop.

**Implementation note**

Build this as a continuous macro world, not a terminal card. The path generated here becomes the same path used for the product reveal and the final CTA.

### 00:16–00:31 — THE LIMIT / WHEN THE PROMPT ENDS

**Visual and camera**

1. **00:16–00:20 — locked close-up.** A direct coding-agent session reaches the end of its visible context. The last line fades; the cursor keeps blinking.
2. **00:20–00:25 — pull back through layers.** The terminal window recedes. Behind it, partial code, an evaluation output, and an unconnected note drift apart. They are not shown as “lost data”; they are shown as context with no next handoff.
3. **00:25–00:31 — whip pan to white.** A thin line tries to reconnect the artifacts, misses, and disappears. One phrase arrives on the cut, then dissolves into the next trajectory.

**Voiceover — English draft**

> A prompt can start the work. It cannot keep the search alive. Real research is the trail of decisions, experiments, and evidence behind an answer.

**On-screen copy**

```text
A PROMPT IS A START.
NOT A SYSTEM.
```

**Sound**

Cursor click, short reverse swell, then the sound of the room opening up. No upbeat music yet.

**Implementation note**

Do not imply that Codex, Claude Code, Gemini, or Antigravity are incapable of persistence in every context. The point is the difference between a direct session and an explicit research workflow.

### 00:31–00:47 — PRODUCT REVEAL / SCIODYSSEY

**Visual and camera**

1. **00:31–00:35 — the surviving line reappears.** It comes from the left edge, enters a folder-like aperture marked `research_record/`, and begins rebuilding a small orbiting research world.
2. **00:35–00:40 — orbital reveal.** The camera circles the world. `STATE.yaml`, `RESEARCH_RECORD`, an evidence artifact, and a next-action marker snap into orbit with real depth and shadow.
3. **00:40–00:47 — name reveal in motion.** The orbit contracts into the wordmark. `SCIODYSSEY` is not a centered title card; it is the destination of the trajectory. `RESEARCH AGENT` resolves below it as the camera continues to drift.

**Voiceover — English draft**

> SciOdyssey is the research layer around your coding agent — a durable world for questions, experiments, and evidence.

**On-screen copy**

```text
SCIODYSSEY
RESEARCH AGENT
RESEARCH THAT SURVIVES THE PROMPT.
```

**Sound**

Music enters with a single harmonic lift. Each orbiting artifact gets a soft, pitched tick; the wordmark lands without a whoosh.

**Assets**

Use `research-world-cover.png` as texture/reference, but make the orbit and artifact motion vector-driven so the camera can move through it.

### 00:47–01:10 — FIRST USE / BRING THE QUESTION

This is the onboarding section, but it must play as one action, not three instruction cards. Parallel is intentionally absent here.

**Visual and camera**

1. **00:47–00:52 — handoff to the user.** The camera settles on a project folder. `task.md` is foreground; the research world is breathing behind it. The user’s command is typed into the folder’s terminal aperture.
2. **00:52–00:57 — command becomes motion.** Show the real first-use command at readable scale:

   ```text
   ./scripts/research-agent step \
     --cli codex --target ./project --allow-edits
   ```

   As the command completes, the text itself becomes the camera rail into the project.
3. **00:57–01:03 — one cycle, three handoffs.** A Scientist reads the task and proposes a bounded next move. META writes the process brief and keeps only what survives. Runtime executes the deterministic mechanics. These are close, tactile moments: a file is written, a metric is measured, a report is returned.
4. **01:03–01:07 — return path.** The camera travels back from the result to the project root. A `run` command appears as the next depth level, not as a new page.
5. **01:07–01:10 — user choice.** A human cursor rests on `evidence/` and the line waits. This is the handoff into the keynote excerpt.

**Voiceover — English draft**

> You bring the question. Choose how far to run. SciOdyssey turns each cycle into a handoff, an artifact, and a place to return.

**On-screen copy**

```text
BRING THE QUESTION.
CHOOSE THE DEPTH.
RETURN TO EVIDENCE.
```

**Sound**

Key presses become the rhythm. Every handoff has a distinct, quiet mechanical sound. Keep the user cursor audible so the film remains human.

**Implementation note**

Use `step`, `run`, and `resume` as depth controls in one continuous environment. Do not show a row of three feature cards.

### 01:10–01:36 — THE KEYNOTE CUT / THE IDEA IN MOTION

The old keynote is now a payoff: the audience already knows what it is looking for. The camera enters the existing keynote stage through the `evidence/` marker, then leaves with a retained result.

**Visual and camera**

1. **01:10–01:14 — match cut.** The blue line from the new onboarding sequence becomes the blue line inside the old keynote terminal. The keynote window grows out of the project root, as if it was always inside the world.
2. **01:14–01:20 — terminal movement.** Reuse the real `TerminalJourney`: `step` moves into `run`, then the serial rail advances. Use a close crop first, then a wide reveal; do not expose the whole keynote composition immediately.
3. **01:20–01:25 — evidence.** Reuse `EvidenceJourney`. A result is not a celebration; it is a trace the camera can inspect. Move across the evidence fields with a shallow-focus parallax.
4. **01:25–01:31 — human gate.** Reuse `HumanJourney`. The pointer crosses the choice surface. Let the click create the next cut; the viewer should feel that the human is selecting what survives.
5. **01:31–01:36 — agent handoff.** Reuse `AgentJourney`. `SKILL.md` and the next trajectory come forward. The old window does not fade away; it folds into the next branch node.

**Voiceover — English draft**

> Scientific judgment belongs to the Scientist. What survives belongs to META. Execution stays deterministic. And the decision stays with you.

**On-screen copy**

No chapter label. Use only the small, diegetic labels already inside the keynote: `Terminal`, `Evidence`, `Human review`, `Coding agent`.

**Sound**

Temporarily let the existing keynote score and cues take over, then pull them through a filter as the old window folds into the next shot.

**Implementation note**

Reuse the existing `TerminalJourney`, `EvidenceJourney`, `HumanJourney`, and `AgentJourney` components. Recompose them as moving footage inside a larger camera move; do not simply place the current V1 keynote scene as a centered rectangle.

### 01:36–01:59 — BREADTH / OPEN THE SEARCH

Parallel appears here for the first time, because the audience has now seen one complete path and understands why a second path is meaningful.

**Visual and camera**

1. **01:36–01:41 — decision node.** The retained keynote result becomes a bright dot. The camera pushes into it. A second faint line appears beside the first.
2. **01:41–01:46 — branch impact.** The dot splits into three trajectories with a physical snap. Use a fast dolly and motion blur; the trajectories leave the screen in different directions.
3. **01:46–01:52 — chase the branches.** The camera follows branch `r1b1`, then whips through branch `r1b2`, then lands on `r1b3`. Each branch has its own isolated worktree, code diff, and evidence pulse. The three worlds are alive at the same time.
4. **01:52–01:56 — review orbit.** The branches return to a common review ring. They do not merge into one undifferentiated result.
5. **01:56–01:59 — explicit promotion.** A human cursor selects one branch. The command `parallel-promote` appears only after the selection. The chosen world brightens; the others remain inspectable.

**Voiceover — English draft**

> Once one path is clear, open the search. Run independent branches. Compare the worlds they build. Promote the one you believe in. Nothing merges itself.

**On-screen copy**

```text
WHAT IF ONE PATH ISN'T ENOUGH?

3 ISOLATED WORKTREES
1 HUMAN REVIEW
EXPLICIT PROMOTION
```

**Sound**

One impact for the split, three differently pitched pulses for the branches, then a lower, quieter click for the human promotion.

**Implementation note**

This replaces the V1 “parallel as a feature card” treatment. The branch split must be the visual climax of the middle act.

### 01:59–02:18 — THE RUNTIME / USE THE AGENT YOU TRUST

This is the model comparison, but it is a moving systems comparison rather than a leaderboard.

**Visual and camera**

1. **01:59–02:04 — two worlds.** The screen divides in depth, not with a flat vertical split. On the left, `DIRECT SESSION` runs `PROMPT → ANSWER → CLOSE`. On the right, `SCIODYSSEY` runs `QUESTION → CYCLE → STATE → REVIEW → RESUME`.
2. **02:04–02:10 — runtime swap.** The camera circles the persistent right-hand world. Four agent plates pass through the same runtime port: `CODEX`, `CLAUDE CODE`, `GEMINI CLI`, `Antigravity`. The project files and evidence remain locked to the world, while the active runtime changes.
3. **02:10–02:14 — no ranking.** A small line of copy follows the orbit: `WORKFLOW COMPARISON / NOT A MODEL LEADERBOARD`. The agents do not receive numerical scores.
4. **02:14–02:18 — handoff.** The selected runtime sends a result back into the same `research_record/`. The camera continues forward into the proof section.

**Voiceover — English draft**

> Use the agent you already trust. Codex. Claude Code. Gemini CLI. Antigravity. The runtime can change. The research world does not.

**On-screen copy**

```text
DIRECT SESSION                 SCIODYSSEY ON TOP
PROMPT → ANSWER → CLOSE        QUESTION → STATE → REVIEW → RESUME

THE RUNTIME IS REPLACEABLE.
THE RESEARCH WORLD IS DURABLE.
```

**Sound**

Each runtime swap has a different timbre, but the same underlying pulse continues. This makes the world, not the model, the musical constant.

**Implementation note**

The comparison must be honest: compare workflow boundaries, persistence, handoff, and review. Do not claim universal model superiority without a controlled benchmark.

### 02:18–02:42 — PROOF / FROM OPEN SEARCH TO VERIFIED RESULT

**Visual and camera**

1. **02:18–02:23 — dashboard as landscape.** Enter `dashboard-overview.png` at high scale. Start on a small status field, then perform a slow camera sweep to the run summary. The dashboard is an environment, not a screenshot on a page.
2. **02:23–02:28 — result match cut.** A green validation line in the dashboard becomes the line in `token-score-comparison.png`. The score grows from the baseline marker to the retained result.
3. **02:28–02:33 — evidence ledger.** Pull back to reveal four quiet anchors: `4 AUTONOMOUS CYCLES`, `13 NAMED EXPERIMENTS`, `0 GPU-HOURS`, `PUBLIC VALIDATION`. Bring them forward one at a time along the camera path.
4. **02:33–02:38 — result lock.** The number `0.6059363` lands large for no more than two seconds. Under it: `+0.0043363 vs official reference` and the supporting `GAUC` / `nDCG@5` values.
5. **02:38–02:42 — quiet inspection.** The camera continues past the number into the artifact path. The viewer sees that the result has a source, a metric, and a retained implementation.

**Voiceover — English draft**

> That is the difference between an answer and an evidence trail. In a recorded KuaiRand-Pure run: four cycles, thirteen named experiments, zero GPU-hours — and a primary score of 0.6059363.

**On-screen copy**

```text
EVIDENCE, NOT PROMISES
PRIMARY 0.6059363
+0.0043363 VS OFFICIAL REFERENCE
```

**Sound**

Music drops around the primary score. Let the score-lock have a clean transient, then return to the quiet pulse.

**Assets**

Use the existing `dashboard-overview.png`, `dashboard-result.png`, `dashboard-validation.png`, and `token-score-comparison.png`. Add camera crop, depth, masking, and parallax rather than framing them as static cards.

### 02:42–02:53 — RESUME / THE NEXT DAY

**Visual and camera**

1. **02:42–02:46 — close the window.** The dashboard recedes. The screen goes dark, but the research world remains as a faint line beneath the black.
2. **02:46–02:50 — one keystroke.** The user types:

   ```text
   ./scripts/research-agent resume \
     --cli codex --target ./project --max-cycles 10 --allow-edits
   ```

3. **02:50–02:53 — re-entry.** State, evidence, and the next action reconnect in the same order. The camera does not return to the beginning; it resumes at the unfinished node.

**Voiceover — English draft**

> Close the window. Come back tomorrow. Resume from the state, not from memory.

**On-screen copy**

```text
THE SEARCH IS STILL HERE.
```

**Sound**

Remove the beat for the first half-second of darkness. One key press brings the whole score back.

### 02:53–03:00 — FINAL / START WITH A QUESTION

**Visual and camera**

1. **02:53–02:56 — final orbit.** The reconnected line makes one complete orbit around the research world. All prior colors are present, but the frame is calm.
2. **02:56–02:59 — wordmark.** The line resolves into `SCIODYSSEY`. The camera drifts slightly past center so the mark feels placed in space, not pasted on a card.
3. **02:59–03:00 — last breath.** `RESEARCH AGENT` and the start command remain for the final beat, then the film cuts to white.

**Voiceover — English draft**

> Start with a question. Keep the search.

**On-screen copy**

```text
SCIODYSSEY
RESEARCH AGENT
START WITH A QUESTION. KEEP THE SEARCH.
```

**Sound**

Resolve the score, leave a short tail, then cut the tail cleanly with the image.

## 4. Production packet for V2

### Existing assets to reuse

| Asset | V2 use |
| --- | --- |
| Existing keynote scenes | 26-second in-world excerpt, recomposed as moving footage |
| `research-world-cover.png` | Product reveal texture and orbital world reference |
| `dashboard-overview.png` | Run landscape and status sweep |
| `dashboard-result.png` | Result lock and state inspection |
| `dashboard-validation.png` | Human/evidence validation close-up |
| `token-score-comparison.png` | Score line match cut |
| `research-architecture.png` | Optional deep-focus insert, never a static architecture slide |
| Existing keynote score/cues | Temporary soundtrack and timing reference |

### New assets required for a polished final

1. **Voiceover recording** matching the English draft, with deliberate pauses. A Chinese VO can be substituted without changing the visual timing.
2. **Final music stem** with three clear energy states: cold open, search acceleration, evidence resolve.
3. **Micro sound library:** keyboard, cursor, disk write, branch split, review click, state restore, score lock.
4. **Optional terminal capture pass:** a small set of real terminal/log frames if we want to mix code-rendered motion with authentic product footage.

### Remotion rebuild shape

Keep `SciOdysseyProductFilm` as the approved V1 reference. Build V2 as a separate composition with:

- one continuous camera/world layer for the trajectory;
- ten beat files matching the time ranges above;
- the existing keynote scene components embedded only in beat 05;
- `TransitionSeries` or explicit overlap windows for motion-led cuts, not page fades;
- voiceover, music, and sound effects as independent tracks with frame-based ducking;
- no global chapter chrome; any label must belong to the object being filmed.

## 5. Success criteria

- By 00:31, the viewer understands the problem without seeing a product name.
- By 00:47, the viewer knows what SciOdyssey is.
- By 01:10, the viewer knows how to start a basic run.
- The keynote appears as proof of the loop, not as a separate presentation.
- Parallel first appears only after the first complete path and decision node.
- The model comparison explains replaceable runtimes without making unsupported benchmark claims.
- At least 30 meaningful visual changes occur across the three minutes; no explanatory frame sits unchanged for more than four seconds, except the final mark.
- The final shot leaves the viewer with one action: start with a question.

**Next handoff:** approve this script and visual grammar first; then implement `SciOdysseyProductFilmV2` without modifying the existing V1 composition or rendering another draft until the new beat structure is in place.
