// Terminal-native edition of the SciOdyssey deck.
//
// The browser/PDF deck remains the source of visual layout. This file keeps
// the same narrative and evidence, but expresses each slide as compact
// terminal primitives so it remains readable in an ANSI-only session.

export const deckMeta = {
  title: "SciOdyssey: Long-Horizon Autonomous ML Research Agent",
  author: "SciOdyssey",
  source: "slides/slides.md",
};

export const slides = [
  {
    chapter: "COVER",
    kicker: "AUTONOMOUS ML RESEARCH / TECHJAM 2026",
    title: ["SciOdyssey:", "Long-Horizon Autonomous", "ML Research Agent"],
    accent: "blue",
    blocks: [
      { kind: "lead", text: "Autonomous ML discovery through pure evidence." },
      { kind: "flow", items: ["PERSISTENT WORLD", "FRESH SCIENTIST", "EVIDENCE FIRST"], tone: "green" },
      { kind: "text", text: "Problem  >  Motivation  >  System  >  Experience  >  Evaluation  >  Insights", tone: "muted" },
    ],
    note: "The terminal edition condenses the 24-slide Slidev deck into a text-first presentation. Source: slides/slides.md.",
  },
  {
    chapter: "01 / PROBLEM",
    kicker: "THE RESEARCH TASK",
    title: "Can an agent carry a research task to completion?",
    accent: "orange",
    blocks: [
      { kind: "lead", text: "Turn a task contract into a tested model, a reproducible implementation, and evidence another researcher can inspect." },
      {
        kind: "steps",
        items: [
          { label: "EXPLORE", text: "Choose hypotheses, write code, run experiments." },
          { label: "RECOVER", text: "Handle failures and revise unsuccessful ideas." },
          { label: "DELIVER", text: "Retain a valid model and the evidence behind it." },
        ],
      },
      { kind: "callout", label: "TEST CASE", text: "KuaiRand-Pure short-video ranking · fixed evaluator · public-validation boundary", tone: "muted" },
    ],
    note: "The benchmark is a concrete validation case; broader task generality remains unproven. Source: README.md and competitions/kuairand/task.md.",
  },
  {
    chapter: "01 / PROBLEM",
    kicker: "FAILURE MODES",
    title: "Why current research agents fall short",
    accent: "orange",
    blocks: [
      { kind: "lead", text: "Three obstacles to sustained autonomous research." },
      {
        kind: "steps",
        items: [
          { label: "01  CLOSED-WORLD", text: "A fixed workflow hits an unexpected error and reaches a dead end." },
          { label: "02  SINGLE TRAJECTORY", text: "A long-lived context carries yesterday's momentum into today's search." },
          { label: "03  REPEATED READING", text: "Reconstructing context costs more than the edit, so the agent rereads." },
        ],
      },
      { kind: "callout", label: "DESIGN RESPONSE", text: "Open-world actions · independent trajectories · evidence that survives", tone: "blue" },
    ],
    note: "This is a synthesis of the project's design pressures, not a universal claim about all research agents. Source: README.md, docs/project_story.md, and docs/FINAL_REPORT.md.",
  },
  {
    chapter: "02 / MOTIVATION",
    kicker: "OPEN-WORLD RESEARCH",
    title: "Research is an open-world task",
    accent: "blue",
    blocks: [
      { kind: "lead", text: "We need an open-world coding agent that can act, inspect, and extend its environment." },
      { kind: "flow", label: "OPEN ACTION SPACE", items: ["SHELL", "FILES", "BROWSER", "GIT"], tone: "blue" },
      { kind: "flow", label: "SELF-RECOVERY", items: ["READ ERRORS", "INSPECT DOCS", "READ SOURCE", "INSTALL"], tone: "orange" },
      { kind: "flow", label: "RUNTIME EXTENSION", items: ["MCP", "SKILLS", "CLI", "PACKAGES"], tone: "rose" },
      { kind: "callout", label: "WORKFLOW EXAMPLE", text: "Known graph  >  inspect  >  extend  >  retry", tone: "green" },
    ],
    note: "LangGraph is used as a concrete known-workflow example. The open-world framing is adapted from the talk track. Source: slides/slides.md and LangGraph documentation.",
  },
  {
    chapter: "02 / MOTIVATION",
    kicker: "TWO DIFFERENT LIFETIMES",
    title: "Preserve the research world",
    accent: "green",
    blocks: [
      { kind: "quote", text: "Preserve the research world.\nReset the researcher." },
      { kind: "flow", items: ["EVIDENCE", "FAILURES", "CODE", "FRESH SCIENTIST"], tone: "green" },
      { kind: "text", text: "A fresh Scientist inherits experience without continuing its predecessor's unfinished reasoning.", tone: "muted" },
    ],
    note: "Resets happen at trajectory boundaries; productive inquiry can continue within a trajectory. Source: README.md.",
  },
  {
    chapter: "03 / SYSTEM",
    kicker: "RESPONSIBILITIES",
    title: "Two scientific roles. One safe runtime.",
    accent: "blue",
    blocks: [
      {
        kind: "steps",
        items: [
          { label: "SCIENTIST", text: "Hypothesize · code · test · interpret\nOne trajectory", tone: "green" },
          { label: "META", text: "Audit · preserve · hand off\nAcross trajectories", tone: "rose" },
          { label: "RUNTIME", text: "Isolation · cancellation · invariants\nSystem lifetime", tone: "orange" },
        ],
      },
      { kind: "callout", label: "BOUNDARY", text: "Scientist chooses the science · META maintains the world · Runtime enforces mechanics", tone: "muted" },
    ],
    note: "Scientific authority is separate from persistence authority. META does not choose the next hypothesis, model, feature, or experiment. Source: README.md and docs/ARCHITECTURE.md.",
  },
  {
    chapter: "03 / SYSTEM",
    kicker: "PERSISTENCE BOUNDARY",
    title: "The persistence boundary is explicit",
    accent: "blue",
    blocks: [
      {
        kind: "diagram",
        tone: "blue",
        lines: [
          "[ ENVIRONMENT ]  >  [ RESEARCH WORLD ]  >  [ FRESH SCIENTIST ]",
          "       task / data              evidence / State              judgment",
          "                                      |",
          "                                      v",
          "                                 [ META REVIEW ]",
          "                                      |",
          "                                      +-- audit > scope > preserve",
        ],
      },
      { kind: "text", text: "Runtime: workspace isolation · runner/evaluator · logs · artifacts · State operations", tone: "orange" },
      { kind: "callout", label: "SELECTIVE PERSISTENCE", text: "What survives is explicit. Previous hidden reasoning does not cross the boundary.", tone: "green" },
    ],
    note: "State captures a retained implementation and its evidence identity, not the entire chronology. Source: docs/ARCHITECTURE.md and docs/FINAL_REPORT.md.",
  },
  {
    chapter: "03 / SYSTEM",
    kicker: "THE HANDOFF LOOP",
    title: "Each cycle leaves a world to build on",
    accent: "orange",
    blocks: [
      {
        kind: "diagram",
        tone: "orange",
        lines: [
          "WORLD  >  SCIENTIST  >  EVIDENCE  >  META",
          "  ^                                      |",
          "  +---------- selective persistence -----+",
        ],
      },
      { kind: "flow", label: "PERSISTS", items: ["METRICS", "CODE", "FAILURES", "REPORTS"], tone: "green" },
      { kind: "flow", label: "RESTARTS", items: ["AN INDEPENDENT REASONING TRAJECTORY"], tone: "purple" },
    ],
    note: "State crystallization is optional; a handoff does not require creating a new State every time. Source: README.md and docs/FINAL_REPORT.md sections 3.1–3.3.",
  },
  {
    chapter: "03 / SYSTEM",
    kicker: "RESEARCH MEMORY",
    title: "Keep facts distinct from intuition",
    accent: "green",
    blocks: [
      {
        kind: "tree",
        lines: [
          "research world",
          "├── evidence + provenance",
          "├── verified knowledge",
          "├── current research State",
          "├── fallible priors",
          "└── State + implementation",
        ],
      },
      { kind: "callout", label: "BUILT TO BE RE-EXAMINED", text: "Facts have evidence. Priors can be overturned. Code can be picked up again.", tone: "green" },
      { kind: "text", text: "Original Scientist reports remain available for audit.", tone: "muted" },
    ],
    note: "The tree shows information categories, not a literal directory layout. Compression is lossy, so raw evidence remains available. Source: README.md and docs/FINAL_REPORT.md.",
  },
  {
    chapter: "03 / SYSTEM",
    kicker: "PARALLEL EXPLORATION",
    title: "One starting point. Independent answers.",
    accent: "blue",
    blocks: [
      {
        kind: "diagram",
        tone: "blue",
        lines: [
          "                 research world R0",
          "                 /       |       \\",
          "                /        |        \\",
          "       Scientist A  Scientist B  Scientist C",
          "          r1b1          r1b2          r1b3",
          "                \\        |        /",
          "                 \\       |       /",
          "                   post-hoc reviewer",
        ],
      },
      { kind: "flow", items: ["ISOLATE", "EXPLORE", "REVIEW", "EXPLICITLY ADOPT"], tone: "purple" },
      { kind: "text", text: "Branches do not share a live reasoning context. Optional synthesis shares reference evidence after review.", tone: "muted" },
    ],
    note: "Parallel breadth is a framework capability, not the claimed cause of the final benchmark gain. Source: README.md and docs/FINAL_REPORT.md section 3.4.",
  },
  {
    chapter: "04 / EXPERIENCE",
    kicker: "DEFINE THE TASK",
    title: "Start with the task and working constraints",
    accent: "orange",
    blocks: [
      {
        kind: "steps",
        items: [
          { label: "01  task.md", text: "What to solve\nObjectives · constraints · evaluation\nKuaiRand-Pure · long_view · GAUC + nDCG@5" },
          { label: "02  PERSONAL.md", text: "How you want it solved\nPreferences · research style · priorities\nmacOS / Apple Silicon · uv · no credentials" },
        ],
      },
      { kind: "callout", label: "OPERATING CONTRACT", text: "Autonomous by default. Supervisable by design.", tone: "orange" },
    ],
    note: "The operator defines the objective and constraints; the agent chooses and executes the experiments. Source: README.md, docs/project_story.md, and competitions/kuairand/task.md.",
  },
  {
    chapter: "04 / EXPERIENCE",
    kicker: "THE RESEARCH TRAJECTORY",
    title: "Evidence changed the next experiment",
    accent: "orange",
    blocks: [
      {
        kind: "timeline",
        items: [
          { label: "E001", text: "Screen historical target encodings; reject weak variants." },
          { label: "E003", text: "Establish a valid rich-FM checkpoint · Full 0.6016310." },
          { label: "E008", text: "Retain a five-seed, 38-field FM ensemble · Full 0.6040901." },
          { label: "E013", text: "Select the eight-seed, 46-field FM ensemble · Full 0.6059363." },
        ],
      },
      { kind: "text", text: "Four autonomous cycles. Medium screens ideas; Full evaluations support retained score claims.", tone: "muted" },
    ],
    note: "This is the canonical submission trajectory, distinct from the later SciOdyssey with Antigravity (E008 DIN) experiment. Source: docs/FINAL_REPORT.md section 4.1 and the E001–E013 ledger.",
  },
  {
    chapter: "04 / EXPERIENCE",
    kicker: "RECOVERY IN THE RUN",
    title: "An evaluation failure became a recoverable step",
    accent: "orange",
    blocks: [
      {
        kind: "diagram",
        tone: "orange",
        lines: [
          "train + evaluate",
          "      |",
          "      v",
          "evidence writer  -- NumPy float32 -->  JSON serialization error",
          "      |                                      |",
          "      +----------- cast scalar <------------+",
          "                         |",
          "                         v",
          "                 rerun + retain evidence",
        ],
      },
      { kind: "callout", label: "OBSERVED RECOVERY", text: "The Scientist diagnosed the writer, modified the code, reran, and kept the measurements.", tone: "green" },
      { kind: "text", text: "No human selected this repair. This is one observed case, not a guarantee for every failure.", tone: "muted" },
    ],
    note: "Cycle 1 completed training and evaluation, then failed while writing evidence because NumPy scalars were not JSON serializable. Source: docs/FINAL_REPORT.md section 4.2 and cycle-1.md.",
  },
  {
    chapter: "04 / EXPERIENCE",
    kicker: "INSPECT THE RESULT",
    title: "A retained State keeps the evidence inspectable",
    accent: "purple",
    blocks: [
      {
        kind: "tree",
        lines: [
          "S004  RETAINED STATE",
          "├── STATE.yaml                 implementation identity",
          "├── system/ensemble_46.py     eight-seed FM ensemble",
          "├── system/evidence/           raw measurements",
          "├── research_record/           ledger + reports",
          "└── final/research-agent-run.json",
        ],
      },
      { kind: "callout", label: "CHECKPOINT", text: "Inspect the retained implementation and the evidence behind the score.", tone: "purple" },
      { kind: "text", text: "Retained validation checkpoint · evidence path · reproducible implementation.", tone: "muted" },
    ],
    note: "The browser deck shows the dashboard screenshot. The terminal edition replaces that image with the evidence path so the checkpoint remains readable without an image protocol. Source: docs/project_story.md and docs/dashboard/2.png.",
  },
  {
    chapter: "05 / EVALUATION",
    kicker: "PUBLIC-VALIDATION RESULT",
    title: "Autonomous research. Measured gains.",
    accent: "orange",
    blocks: [
      { kind: "table", headers: ["METRIC", "OFFICIAL FM", "OURS"], rows: [["GAUC", "0.6674000", "0.6728421"], ["nDCG@5", "0.5357000", "0.5390304"], ["PRIMARY", "0.6016000", "0.6059363"]], tone: "green" },
      { kind: "bar", label: "PRIMARY", value: "0.6059363", delta: "+0.0043363 absolute" },
      { kind: "text", text: "46 categorical features × 8-seed FM ensemble · NumPy / CPU · public validation only", tone: "muted" },
    ],
    note: "Primary = mean(GAUC, nDCG@5). Hidden-test scoring is organizer-controlled. Final model uses rank k=16. Source: README.md and docs/FINAL_REPORT.md.",
  },
  {
    chapter: "05 / EVALUATION",
    kicker: "AUTONOMY AND AUDITABILITY",
    title: "An audit trail from experiment to output",
    accent: "blue",
    blocks: [
      { kind: "metrics", items: [{ value: "4", label: "AUTONOMOUS CYCLES", detail: "within 50-iteration cap" }, { value: "13", label: "NAMED EXPERIMENTS", detail: "E001–E013 · 7 Full" }, { value: "0", label: "MANUAL SCIENTIFIC INTERVENTIONS", detail: "after launch · 0 GPU-hours" }] },
      { kind: "callout", label: "CHECKED OUTPUT", text: "170,588 prediction rows passed the unchanged Starter Kit alignment checker.", tone: "green" },
      { kind: "text", text: "Measured LLM tokens: 48.24M including cache reads · 4.02M excluding cache reads.", tone: "muted" },
    ],
    note: "Zero manual scientific interventions applies after launch in the retained run. Zero GPU-hours does not mean zero LLM cost. Source: docs/FINAL_REPORT.md and submit-check.txt.",
  },
  {
    chapter: "05 / EVALUATION",
    kicker: "RESOURCE ACCOUNTING",
    title: "Resource use is part of the evidence",
    accent: "orange",
    blocks: [
      { kind: "quote", text: "~$10 project-level subscription estimate" },
      {
        kind: "steps",
        items: [
          { label: "MODEL", text: "One GPT Plus + one Gemini Pro for 7 days." },
          { label: "COMPUTE", text: "One MacBook M2. CPU training. 0 GPU-hours." },
        ],
      },
      { kind: "text", text: "The estimate covers coding, debugging, agent runs, and all experiments. LLM usage remains a separate cost.", tone: "muted" },
    ],
    note: "~$10 is the requested subscription-equivalent accounting for the project, not cost per experiment. Source: docs/project_story.md, README.md, and the project resource accounting.",
  },
  {
    chapter: "05 / EVALUATION",
    kicker: "DIRECT-AGENT COMPARISON",
    title: "Compare scores alongside their evidence",
    accent: "orange",
    blocks: [
      { kind: "table", headers: ["RUN", "PRIMARY", "TOKENS"], rows: [["Official reference", "0.6016000", "—"], ["Antigravity direct", "0.6045803", "8.565M"], ["Luna direct", "≈0.6046", "28.070M"], ["Heterogeneous", "≈0.6047", "39.607M"], ["SciOdyssey w/ Antigravity", "0.6052", "45–51M"], ["SciOdyssey submission", "0.6059363", "48.240M"]], tone: "green" },
      { kind: "text", text: "One recorded run per condition; model, budget, and evidence quality differ. This is not a controlled causal comparison.", tone: "muted" },
    ],
    note: "The comparison uses measured total input + output tokens including cache-read input. Source: docs/FINAL_REPORT.md section 5.3 and the archived control reports.",
  },
  {
    chapter: "06 / INSIGHTS",
    kicker: "WHAT THE RUN TAUGHT US",
    title: "The run taught us more than the final score",
    accent: "purple",
    blocks: [
      {
        kind: "steps",
        items: [
          { label: "01  DIVERSITY", text: "A prior worth testing, not proof of causality." },
          { label: "02  VALIDITY", text: "A score needs evidence, scope, and audit." },
          { label: "03  FAILURE", text: "A broken writer can become a recoverable step." },
          { label: "04  RESET", text: "Fresh cognition can still be anchored by summaries." },
        ],
      },
      { kind: "callout", label: "OBSERVED, NOT PROVEN", text: "Parallel/Synthesis: 0.6055536 · canonical E001–E013 frontier: 0.6059363", tone: "orange" },
    ],
    note: "This slide synthesizes model diversity, validity audits, recovery, parallel search, and selective persistence. Source: docs/FINAL_REPORT.md sections 3.4–3.5, 4.2, 5.4–5.5, and 6.",
  },
  {
    chapter: "06 / INSIGHTS",
    kicker: "LIMITS AND NEXT EXPERIMENTS",
    title: "Reproducible evidence. Open questions.",
    accent: "purple",
    blocks: [
      {
        kind: "steps",
        items: [
          { label: "01  GENERALITY", text: "One task does not establish broad external validity." },
          { label: "02  ATTRIBUTION", text: "META, State, and reset are not isolated variables." },
          { label: "03  MEMORY", text: "Summaries can lose context and anchor future work." },
        ],
      },
      { kind: "callout", label: "NEXT QUESTIONS", text: "Broader tasks · targeted ablations · less repeated execution", tone: "green" },
      { kind: "text", text: "KuaiRand-1K and KuaiRand-27K bonus benchmarks were not attempted.", tone: "muted" },
    ],
    note: "These are documented limitations and proposed directions, not completed features or a committed roadmap. Source: README.md.",
  },
  {
    chapter: "06 / INSIGHTS",
    kicker: "ENGINEERING PRACTICE",
    title: "A clean repo. A continuous agent.",
    accent: "orange",
    blocks: [
      {
        kind: "diagram",
        tone: "orange",
        lines: [
          "main  (clean trunk)",
          "├── agent A / branch  --\\",
          "├── agent B / branch  ----> review > merge",
          "└── agent C / branch  --/",
        ],
      },
      { kind: "flow", label: "UNATTENDED CONTINUATION", items: ["ISSUE / PROMPT", "GITHUB ACTION", "COMMIT", "REVIEW"], tone: "blue" },
      { kind: "text", text: "Proposed workflow guidance. GitHub continuation is not a benchmarked system feature.", tone: "muted" },
    ],
    note: "This field note distills an Agentic SWE workflow suggestion: isolate changes and make unattended work reviewable. Source: slides/slides.md.",
  },
  {
    chapter: "06 / INSIGHTS",
    kicker: "KEEP EXPERIENCE, REOPEN SEARCH",
    title: "Keep the experience. Reopen the search.",
    accent: "blue",
    blocks: [
      {
        kind: "code",
        lines: [
          "# From the configured repo, run one autonomous cycle",
          "$ ./scripts/research-agent step --cli codex \\",
          "    --target /absolute/path/to/project --allow-edits",
        ],
      },
      { kind: "text", text: "github.com/zc6600/research-agent-kuairand", tone: "blue" },
      { kind: "callout", label: "HANDOFF", text: "Code · technical report · experiment ledger · checked output", tone: "green" },
    ],
    note: "The command is display text and does not execute. Prerequisites are in the repository Quick start. Source: README.md.",
  },
  {
    chapter: "APPENDIX",
    kicker: "THE TEAM",
    title: "Five people. One autonomous research loop.",
    accent: "orange",
    blocks: [
      {
        kind: "team",
        items: [
          ["CZ", "Chen Zhu", "TEAM LEAD / SYSTEM", "direction · architecture · integration"],
          ["ZZ", "Zhou Ziyu", "MODELING / EXPERIMENTS", "features · ensembles · evidence review"],
          ["SX", "Shilin Xu", "DATA / METRICS", "data workflow · contracts · alignment"],
          ["GG", "GE GAO", "RUNTIME / RELIABILITY", "execution · testing · integration support"],
          ["JL", "Jiran Li", "EVIDENCE / REPRODUCIBILITY", "telemetry · documentation · packaging"],
        ],
      },
      { kind: "text", text: "Overlapping responsibilities · shared world · every handoff kept the research moving.", tone: "muted" },
    ],
    note: "Team names and responsibilities are drawn from documented team contributions. Source: README.md and docs/FINAL_REPORT.md section 6.4.",
  },
  {
    chapter: "APPENDIX",
    kicker: "CAPABILITY RECOVERY",
    title: "The difference is recoverability",
    accent: "orange",
    blocks: [
      {
        kind: "table",
        headers: ["BOUNDED GRAPH", "OPEN HARNESS"],
        rows: [
          ["fixed tool set", "shell · files · docs · browser"],
          ["API fails", "inspect error"],
          ["no recovery tool", "modify environment"],
          ["dead end", "retry with new capability"],
        ],
        tone: "blue",
      },
      { kind: "flow", label: "RECOVERY LOOP", items: ["FAIL", "INSPECT", "LEARN", "MODIFY", "RETRY"], tone: "green" },
      { kind: "text", text: "The comparison describes two capability models, not a claim that every failure is recoverable.", tone: "muted" },
    ],
    note: "The comparison contrasts a predefined graph with a coding-agent harness that can inspect and modify its environment. Source: slides/slides.md appendix.",
  },
];

