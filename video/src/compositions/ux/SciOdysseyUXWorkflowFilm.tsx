import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {
  C,
  ResearchWorldGlyph,
  ScientistGlyph,
  type FilmProps,
} from '../launch/SciOdysseyFilm';
import './SciOdysseyUXWorkflowFilm.css';

type MotionStyle = React.CSSProperties;

const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

function reveal(frame: number, delay = 0, duration = 24) {
  return interpolate(frame - delay, [0, duration], [0, 1], clamp);
}

function lift(frame: number, delay = 0, distance = 24, duration = 26): MotionStyle {
  const p = reveal(frame, delay, duration);
  return {opacity: p, transform: `translateY(${(1 - p) * distance}px)`};
}

function springStyle(frame: number, fps: number, delay = 0, from = 0.92): MotionStyle {
  const p = spring({frame: frame - delay, fps, config: {damping: 19, stiffness: 115, mass: 0.75}});
  return {
    opacity: interpolate(frame - delay, [0, 12], [0, 1], clamp),
    transform: `scale(${from + p * (1 - from)})`,
  };
}

function OpsFrame({children, className = ''}: {children: React.ReactNode; className?: string}) {
  return <AbsoluteFill className={`ops-frame ${className}`}>{children}</AbsoluteFill>;
}

function QuietMark({color = C.ink}: {color?: string}) {
  return (
    <div className="ops-mark" style={{color}}>
      <span className="ops-mark-dot" style={{backgroundColor: color}} />
      SCIODYSSEY
    </div>
  );
}

function FineLabel({children, color = C.muted, className = ''}: {children: React.ReactNode; color?: string; className?: string}) {
  return <div className={`ops-fine-label ${className}`} style={{color}}>{children}</div>;
}

function HeroLine({children, delay = 0, className = ''}: {children: React.ReactNode; delay?: number; className?: string}) {
  const frame = useCurrentFrame();
  return <div className={`ops-hero-line ${className}`} style={lift(frame, delay, 34, 30)}>{children}</div>;
}

function DrawnPath({d, color, delay = 0, duration = 80, opacity = 1}: {d: string; color: string; delay?: number; duration?: number; opacity?: number}) {
  const frame = useCurrentFrame();
  const progress = reveal(frame, delay, duration);
  return <path d={d} fill="none" stroke={color} strokeWidth={2.2} pathLength="1" strokeDasharray="1" strokeDashoffset={1 - progress} opacity={opacity} />;
}

function Orbit({size = 220, delay = 0, color = C.blue}: {size?: number; delay?: number; color?: string}) {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pulse = 1 + Math.sin((frame - delay) / (fps * 0.8)) * 0.018;
  return (
    <div className="ops-orbit" style={{width: size, height: size, ...springStyle(frame, fps, delay), transform: `scale(${pulse})`}}>
      <div className="ops-orbit-ring" style={{borderColor: color}} />
      <ResearchWorldGlyph large />
    </div>
  );
}

function TerminalLine({children, delay, tone = 'normal', active = false}: {children: React.ReactNode; delay: number; tone?: 'normal' | 'muted' | 'success' | 'accent'; active?: boolean}) {
  const frame = useCurrentFrame();
  const p = reveal(frame, delay, 17);
  const color = tone === 'success' ? C.green : tone === 'accent' ? C.blueDeep : tone === 'muted' ? '#89909e' : '#313944';
  return (
    <div className={`ops-terminal-line ${active ? 'is-active' : ''}`} style={{opacity: p, color}}>
      <span className="ops-terminal-caret">{active ? '›' : ' '}</span>
      <span className="ops-terminal-text" style={{clipPath: `inset(0 ${Math.max(0, (1 - p) * 100)}% 0 0)`}}>{children}</span>
    </div>
  );
}

function TerminalWindow({title, children, className = '', delay = 0}: {title: string; children: React.ReactNode; className?: string; delay?: number}) {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div className={`ops-terminal ${className}`} style={springStyle(frame, fps, delay)}>
      <div className="ops-terminal-top">
        <span className="ops-terminal-dot" />
        <span>{title}</span>
        <span className="ops-terminal-menu">···</span>
      </div>
      <div className="ops-terminal-body">{children}</div>
    </div>
  );
}

function AgentContext() {
  const frame = useCurrentFrame();
  return (
    <div className="ops-agent-context" style={lift(frame, 64, 22, 30)}>
      <div className="ops-agent-header">
        <span className="ops-agent-icon">✦</span>
        <div><strong>coding agent</strong><small>context loaded</small></div>
        <span className="ops-agent-live">live</span>
      </div>
      <div className="ops-context-rule" />
      <div className="ops-context-file ops-context-file-main"><span className="ops-file-icon">▱</span><strong>SKILL.md</strong><small>research-agent</small></div>
      <div className="ops-context-tree">
        <div><span>↳</span> AGENTS.md</div>
        <div><span>↳</span> task.md</div>
        <div><span>↳</span> research_record/</div>
        <div><span>↳</span> SYSTEM_CONTRACT.md</div>
      </div>
      <div className="ops-context-note"><span className="ops-green-dot" /> role contract injected <i>·</i> safe boundary</div>
    </div>
  );
}

function WorkflowOpening() {
  const frame = useCurrentFrame();
  const field = reveal(frame, 28, 150);
  return (
    <OpsFrame className="ops-opening">
      <QuietMark color={C.blue} />
      <Img className="ops-opening-art" src={staticFile('assets/research-world-cover.png')} style={{opacity: interpolate(frame, [0, 70], [0, 0.16], clamp), transform: `scale(${1.04 - reveal(frame, 0, 300) * 0.018})`}} />
      <svg className="ops-opening-field" viewBox="0 0 1920 1080" aria-hidden="true">
        <DrawnPath d="M-30 710 C240 710 410 416 704 526 S1180 768 1570 398 S1840 290 1980 322" color={C.blue} delay={22} duration={135} />
        <DrawnPath d="M-25 810 C260 810 470 842 760 702 S1230 432 1582 612 S1848 840 1980 792" color={C.orange} delay={42} duration={135} />
        <DrawnPath d="M-20 586 C270 520 484 630 760 704 S1214 580 1586 744 S1850 622 1980 560" color={C.purple} delay={62} duration={135} />
        <circle cx="1580" cy="570" r="11" fill={C.green} opacity={field} />
      </svg>
      <div className="ops-opening-copy">
        <FineLabel color={C.blue}>A RESEARCH WORKFLOW, NOT A FIXED PATH</FineLabel>
        <HeroLine delay={18}>Start with a question.<br /><span className="ops-muted">Choose what happens next.</span></HeroLine>
        <p style={lift(frame, 74, 15, 24)}>Terminal, coding agent, dashboard.<br />One research world underneath.</p>
      </div>
      <div className="ops-opening-world" style={lift(frame, 68, 25, 34)}><Orbit size={330} delay={78} color={C.green} /><FineLabel color={C.green}>RESEARCH WORLD</FineLabel></div>
      <div className="ops-opening-rail" style={lift(frame, 150, 10, 20)}><span>step</span><i>·</i><span>run</span><i>·</i><span>parallel</span><i>·</i><span>resume</span></div>
    </OpsFrame>
  );
}

function SkillInAgent() {
  const frame = useCurrentFrame();
  return (
    <OpsFrame className="ops-skill-scene">
      <QuietMark color={C.purple} />
      <div className="ops-skill-copy">
        <FineLabel color={C.purple}>THE SKILL IS THE ENTRY POINT</FineLabel>
        <HeroLine delay={15}>Give the agent<br /><span className="ops-muted">a research world.</span></HeroLine>
        <p style={lift(frame, 68, 15, 26)}>Drop the protocol into the coding agent.<br />The repo becomes an instrument panel.</p>
      </div>
      <TerminalWindow title="~/project · terminal" className="ops-skill-terminal" delay={34}>
        <TerminalLine delay={54} active><span className="ops-blue">$</span> codex</TerminalLine>
        <TerminalLine delay={74} tone="accent">/skills/research-agent</TerminalLine>
        <TerminalLine delay={94} tone="success">✓ loaded SKILL.md</TerminalLine>
        <TerminalLine delay={114} tone="muted">  task · evaluator · memory · state</TerminalLine>
        <TerminalLine delay={134} tone="success">✓ target context injected</TerminalLine>
      </TerminalWindow>
      <AgentContext />
      <div className="ops-skill-link" style={{opacity: reveal(frame, 132, 26)}}><span />skill → runtime boundary</div>
    </OpsFrame>
  );
}

type Mode = {command: string; description: string; color: string; delay: number; output: string};

function ModeRow({mode, active}: {mode: Mode; active?: boolean}) {
  const frame = useCurrentFrame();
  const p = reveal(frame, mode.delay, 22);
  return (
    <div className={`ops-mode-row ${active ? 'is-active' : ''}`} style={{opacity: p, transform: `translateX(${(1 - p) * 30}px)`, borderColor: active ? `${mode.color}88` : `${mode.color}42`}}>
      <span className="ops-mode-signal" style={{backgroundColor: mode.color}} />
      <div className="ops-mode-main"><code style={{color: mode.color}}>{mode.command}</code><small>{mode.description}</small></div>
      <span className="ops-mode-output">{mode.output}</span>
    </div>
  );
}

function ChoiceScene() {
  const frame = useCurrentFrame();
  const modes: Mode[] = [
    {command: 'step', description: 'one bounded cycle · control returns', color: C.blue, delay: 38, output: 'META → Scientist'},
    {command: 'run', description: 'continue within a cycle budget', color: C.purple, delay: 66, output: 'cycle 1 → 4'},
    {command: 'resume', description: 'reconstruct the world after interruption', color: C.orange, delay: 94, output: 'world restored'},
  ];
  return (
    <OpsFrame className="ops-choice-scene">
      <QuietMark color={C.blue} />
      <div className="ops-choice-copy">
        <FineLabel color={C.blue}>SAME SKILL. DIFFERENT DEPTH.</FineLabel>
        <HeroLine delay={14}>You choose the<br /><span className="ops-muted">operating mode.</span></HeroLine>
        <p style={lift(frame, 66, 14, 24)}>Automate one experiment.<br />Or let the loop run.</p>
      </div>
      <div className="ops-modes" style={lift(frame, 26, 18, 26)}>
        {modes.map((mode, index) => <ModeRow key={mode.command} mode={mode} active={index === 0} />)}
        <div className="ops-mode-command" style={lift(frame, 132, 11, 20)}><span className="ops-prompt">$</span> ./scripts/research-agent <b className="ops-blue">step</b> --cli codex --allow-edits</div>
      </div>
      <div className="ops-choice-bottom" style={lift(frame, 174, 10, 20)}><span className="ops-green-dot" /> every mode writes back to the same externalized research world</div>
    </OpsFrame>
  );
}

type Branch = {id: string; label: string; detail: string; color: string; delay: number};

function BranchCard({branch}: {branch: Branch}) {
  const frame = useCurrentFrame();
  const p = reveal(frame, branch.delay, 24);
  return (
    <div className="ops-branch-card" style={{opacity: p, transform: `translateX(${(1 - p) * 22}px)`, borderColor: `${branch.color}70`}}>
      <span className="ops-branch-badge" style={{color: branch.color, borderColor: `${branch.color}70`}}>{branch.id}</span>
      <div><strong>{branch.label}</strong><small>{branch.detail}</small></div>
      <span className="ops-branch-status" style={{color: branch.color}}>done</span>
    </div>
  );
}

function ParallelScene() {
  const frame = useCurrentFrame();
  const branchDraw = reveal(frame, 34, 104);
  const review = reveal(frame, 168, 28);
  const branches: Branch[] = [
    {id: 'r1b1', label: 'Scientist A', detail: 'independent worktree', color: C.blue, delay: 78},
    {id: 'r1b2', label: 'Scientist B', detail: 'independent worktree', color: C.purple, delay: 96},
    {id: 'r1b3', label: 'Scientist C', detail: 'independent worktree', color: C.orange, delay: 114},
  ];
  return (
    <OpsFrame className="ops-parallel-scene">
      <QuietMark color={C.orange} />
      <div className="ops-parallel-copy">
        <FineLabel color={C.orange}>WHEN ONE PATH IS NOT ENOUGH</FineLabel>
        <HeroLine delay={14}>Open the search<br /><span className="ops-muted">in parallel.</span></HeroLine>
        <p style={lift(frame, 66, 14, 24)}>Independent Scientists.<br />One inherited research world.</p>
      </div>
      <TerminalWindow title="~/project · terminal" className="ops-parallel-terminal" delay={30}>
        <TerminalLine delay={52} active><span className="ops-blue">$</span> ./scripts/research-agent parallel</TerminalLine>
        <TerminalLine delay={72}>  --branches 3 --parallelism 3</TerminalLine>
        <TerminalLine delay={92}>  --keep 1 --allow-edits</TerminalLine>
        <TerminalLine delay={112} tone="success">→ prepared 3 isolated worktrees</TerminalLine>
        <TerminalLine delay={132} tone="muted">  post-hoc reviewer waiting</TerminalLine>
      </TerminalWindow>
      <div className="ops-parallel-map">
        <div className="ops-parallel-origin" style={springStyle(frame, 30, 28)}><Orbit size={126} delay={38} color={C.green} /><span>R0 · research world</span></div>
        <svg viewBox="0 0 800 500" aria-hidden="true"><DrawnPath d="M110 250 C260 250 300 94 455 94 H730" color={C.blue} delay={42} duration={80} /><DrawnPath d="M110 250 H730" color={C.purple} delay={56} duration={80} /><DrawnPath d="M110 250 C260 250 300 406 455 406 H730" color={C.orange} delay={70} duration={80} /><circle cx="110" cy="250" r="8" fill={C.green} opacity={branchDraw} /></svg>
        <div className="ops-branch-list">{branches.map((branch) => <BranchCard key={branch.id} branch={branch} />)}</div>
        <div className="ops-reviewer" style={{opacity: review, transform: `translateY(${(1 - review) * 14}px)`}}><span className="ops-reviewer-icon">⌁</span><strong>Reviewer</strong><small>compare worlds · select explicitly</small><b>r1b2</b></div>
      </div>
      <div className="ops-parallel-note" style={lift(frame, 200, 9, 18)}><span className="ops-orange-dot" /> branches do not share a live reasoning context</div>
    </OpsFrame>
  );
}

function DashboardWindow({src, className = '', delay = 0, objectPosition = 'center top'}: {src: string; className?: string; delay?: number; objectPosition?: string}) {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div className={`ops-dashboard-window ${className}`} style={springStyle(frame, fps, delay)}>
      <div className="ops-dashboard-bar"><span className="ops-dashboard-dot" /><span className="ops-dashboard-title">Research Agent Dashboard</span><span className="ops-dashboard-live">read-only</span></div>
      <Img src={staticFile(src)} style={{width: '100%', height: 'calc(100% - 42px)', objectFit: 'cover', objectPosition}} />
    </div>
  );
}

function DashboardScene() {
  const frame = useCurrentFrame();
  const second = reveal(frame, 126, 30);
  return (
    <OpsFrame className="ops-dashboard-scene">
      <QuietMark color={C.green} />
      <div className="ops-dashboard-copy">
        <FineLabel color={C.green}>A WINDOW INTO THE WORLD</FineLabel>
        <HeroLine delay={15}>See the run<br /><span className="ops-muted">as it unfolds.</span></HeroLine>
        <p style={lift(frame, 66, 14, 24)}>Status. State. Activity.<br />Evidence and the score that survived.</p>
        <div className="ops-dashboard-command" style={lift(frame, 112, 9, 20)}><span className="ops-prompt">$</span> ./scripts/research-agent gui <span className="ops-muted">--target ./project</span></div>
      </div>
      <DashboardWindow src="assets/dashboard-overview.png" className="ops-dashboard-overview" delay={28} />
      <DashboardWindow src="assets/dashboard-validation.png" className="ops-dashboard-validation" delay={138} objectPosition="center 34%" />
      <div className="ops-dashboard-callout" style={{opacity: second, transform: `translateY(${(1 - second) * 10}px)`}}><span className="ops-green-dot" /> retained checkpoint <b>S004</b><i>·</i> primary <b>0.605936</b></div>
    </OpsFrame>
  );
}

function HumanChoiceScene() {
  const frame = useCurrentFrame();
  const pointer = interpolate(frame, [74, 140], [0, 1], clamp);
  const promote = reveal(frame, 160, 28);
  return (
    <OpsFrame className="ops-human-scene">
      <QuietMark color={C.rose} />
      <div className="ops-human-copy">
        <FineLabel color={C.rose}>AUTOMATION HAS A PAUSE BUTTON</FineLabel>
        <HeroLine delay={14}>Human when it<br /><span className="ops-rose">matters.</span></HeroLine>
        <p style={lift(frame, 66, 14, 24)}>Inspect a branch. Compare the evidence.<br />Promote only what you choose.</p>
      </div>
      <div className="ops-human-review" style={springStyle(frame, 30, 34)}>
        <div className="ops-review-head"><span className="ops-reviewer-icon">⌁</span><div><strong>Parallel review</strong><small>P8F0A12C · 3 completed worlds</small></div><span className="ops-needs-human">needs human</span></div>
        <div className="ops-review-rule" />
        <div className="ops-review-branches">
          {['r1b1', 'r1b2', 'r1b3'].map((branch, index) => <div key={branch} className={`ops-review-branch ${index === 1 ? 'selected' : ''}`}><span className="ops-review-radio" style={{borderColor: index === 1 ? C.purple : '#c6cad2', backgroundColor: index === 1 ? C.purple : 'transparent'}} /><b>{branch}</b><small>{index === 1 ? 'complementary evidence' : 'candidate world'}</small><span className="ops-review-score">{['.6041', '.6059', '.6038'][index]}</span></div>)}
        </div>
        <div className="ops-review-actions"><span>inspect</span><span>compare</span><b>promote r1b2 →</b></div>
        <div className="ops-human-cursor" style={{left: `${28 + pointer * 250}px`, top: `${240 + pointer * 40}px`, opacity: pointer}}><span /><small>operator</small></div>
      </div>
      <div className="ops-promote-command" style={{opacity: promote, transform: `translateY(${(1 - promote) * 12}px)`}}><span className="ops-prompt">$</span> ./scripts/research-agent <b className="ops-rose">parallel-promote</b> --branch r1b2 <span className="ops-muted">--allow-edits</span></div>
      <div className="ops-human-foot" style={lift(frame, 194, 9, 18)}><span className="ops-rose-dot" /> selection is explicit · branch code is never merged automatically</div>
    </OpsFrame>
  );
}

function WorkflowClosing() {
  const frame = useCurrentFrame();
  const paths = reveal(frame, 24, 120);
  const final = reveal(frame, 118, 32);
  return (
    <OpsFrame className="ops-closing">
      <QuietMark color={C.blue} />
      <Img className="ops-closing-art" src={staticFile('assets/research-world-cover.png')} style={{opacity: interpolate(frame, [80, 170], [0, 0.13], clamp)}} />
      <svg className="ops-closing-field" viewBox="0 0 1920 1080" aria-hidden="true">
        <DrawnPath d="M-40 710 C280 710 430 420 750 540 S1260 780 1620 380 S1860 280 2020 290" color={C.blue} delay={22} duration={120} />
        <DrawnPath d="M-40 810 C280 810 490 820 780 706 S1260 440 1600 620 S1870 830 2020 780" color={C.orange} delay={42} duration={120} />
        <DrawnPath d="M-30 590 C280 520 480 610 770 700 S1230 560 1590 740 S1870 610 2020 540" color={C.purple} delay={62} duration={120} />
        <circle cx="1590" cy="580" r="12" fill={C.green} opacity={paths} />
      </svg>
      <div className="ops-closing-copy"><FineLabel color={C.blue}>RESEARCH AGENT</FineLabel><HeroLine delay={14}>Automate the repetition.<br /><span className="ops-blue">Keep the judgment.</span></HeroLine><p style={lift(frame, 70, 14, 24)}>A free research loop.<br /><span className="ops-muted">One world. Many ways forward.</span></p></div>
      <div className="ops-closing-rail" style={{opacity: final}}><span>step</span><i>·</i><span>run</span><i>·</i><span>parallel</span><i>·</i><span>dashboard</span><i>·</i><span>human choice</span></div>
      <div className="ops-closing-proof" style={{opacity: final, transform: `translateY(${(1 - final) * 12}px)`}}><span className="ops-green-dot" /> evidence remains <b>0.6059363</b></div>
    </OpsFrame>
  );
}

export const SciOdysseyUXWorkflowFilm: React.FC<FilmProps> = ({voiceOverSrc, musicSrc}) => {
  return (
    <AbsoluteFill className="film-root cinematic-film">
      <Sequence from={0} durationInFrames={270}><WorkflowOpening /></Sequence>
      <Sequence from={270} durationInFrames={330}><SkillInAgent /></Sequence>
      <Sequence from={600} durationInFrames={330}><ChoiceScene /></Sequence>
      <Sequence from={930} durationInFrames={390}><ParallelScene /></Sequence>
      <Sequence from={1320} durationInFrames={330}><DashboardScene /></Sequence>
      <Sequence from={1650} durationInFrames={360}><HumanChoiceScene /></Sequence>
      <Sequence from={2010} durationInFrames={240}><WorkflowClosing /></Sequence>
      {voiceOverSrc ? <Audio src={voiceOverSrc} /> : null}
      {musicSrc ? <Audio src={musicSrc} volume={0.18} /> : null}
    </AbsoluteFill>
  );
};
