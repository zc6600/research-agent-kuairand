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
import '../../shared/styles.css';

export type FilmProps = {
  voiceOverSrc?: string;
  musicSrc?: string;
};

export const C = {
  ink: '#111217',
  body: '#33343a',
  muted: '#7d7d82',
  line: '#e6e6e8',
  blue: '#38bdf8',
  blueDeep: '#1476b5',
  orange: '#ff873f',
  rose: '#ff5c78',
  purple: '#a66cff',
  green: '#16803b',
  aqua: '#20d9a0',
  paper: '#fbfcfb',
};

const easeOut = (value: number) => 1 - Math.pow(1 - value, 3);

function reveal(frame: number, delay = 0, distance = 28, duration = 20) {
  const p = easeOut(interpolate(frame - delay, [0, duration], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return {opacity: p, transform: `translateY(${(1 - p) * distance}px)`};
}

function scaleIn(frame: number, delay = 0, duration = 28) {
  const p = spring({frame: frame - delay, fps: 30, config: {damping: 16, stiffness: 120, mass: 0.8}});
  return {opacity: interpolate(frame - delay, [0, 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}), transform: `scale(${0.94 + p * 0.06})`};
}

function draw(frame: number, delay = 0, duration = 34) {
  return interpolate(frame - delay, [0, duration], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
}

const Text: React.FC<React.PropsWithChildren<{className?: string; style?: React.CSSProperties}>> = ({children, className = '', style}) => (
  <div className={className} style={style}>{children}</div>
);

export const Eyebrow: React.FC<{children: React.ReactNode; color?: string}> = ({children, color = C.muted}) => (
  <div className="eyebrow" style={{color}}>{children}</div>
);

const Rule: React.FC<{style?: React.CSSProperties}> = ({style}) => <div className="rule" style={style} />;

function FilmChrome({scene, total = 8}: {scene: string; total?: number}) {
  const frame = useCurrentFrame();
  const sceneNumber = Number(scene.split('/')[0]);
  const progress = interpolate(frame, [0, 180], [0.05, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <>
      <div className="chrome-top">
        <span><i className="status-dot" /> SCIODYSSEY <span className="chrome-dim">/ FIELD NOTES 2026</span></span>
        <span className="mono chrome-scene">{scene.padStart(2, '0')} / {String(total).padStart(2, '0')}</span>
      </div>
      <div className="chrome-progress" style={{transform: `scaleX(${progress})`}} />
      <div className="chrome-bottom">
        <span className="mono">AUTONOMOUS ML RESEARCH</span>
        <span className="chrome-dim">PURE EVIDENCE / SELECTIVE PERSISTENCE</span>
      </div>
      <div className="page-corner corner-tl" />
      <div className="page-corner corner-br" />
    </>
  );
}

export function Scene({children, scene, className = '', total = 8}: {children: React.ReactNode; scene: string; className?: string; total?: number}) {
  return <AbsoluteFill className={`scene ${className}`}><FilmChrome scene={scene} total={total} />{children}</AbsoluteFill>;
}

export function WordReveal({children, className = '', delay = 0}: {children: React.ReactNode; className?: string; delay?: number}) {
  const frame = useCurrentFrame();
  return <div className={className} style={reveal(frame, delay)}>{children}</div>;
}

export function AccentLine({color = C.blue, width = 120, delay = 0, className = ''}: {color?: string; width?: number; delay?: number; className?: string}) {
  const frame = useCurrentFrame();
  const p = interpolate(frame - delay, [0, 22], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div className={`accent-line ${className}`} style={{backgroundColor: color, width: width * p}} />;
}

export function Metric({value, label, detail, color = C.blue, delay = 0, small = false}: {value: string; label: string; detail?: string; color?: string; delay?: number; small?: boolean}) {
  const frame = useCurrentFrame();
  return (
    <div className={`metric ${small ? 'metric-small' : ''}`} style={reveal(frame, delay, 18)}>
      <div className="mono metric-label" style={{color}}>{label}</div>
      <div className="metric-value" style={{color}}>{value}</div>
      {detail && <div className="metric-detail">{detail}</div>}
    </div>
  );
}

export function Pill({children, color = C.blue, delay = 0}: {children: React.ReactNode; color?: string; delay?: number}) {
  const frame = useCurrentFrame();
  return <div className="pill" style={{...scaleIn(frame, delay), borderColor: `${color}66`, color}}>{children}</div>;
}

export function Arrow({color = C.line, direction = 'right', delay = 0}: {color?: string; direction?: 'right' | 'down' | 'left'; delay?: number}) {
  const frame = useCurrentFrame();
  const p = interpolate(frame - delay, [0, 22], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rotation = direction === 'down' ? 90 : direction === 'left' ? 180 : 0;
  return <div className="arrow" style={{color, opacity: p, transform: `rotate(${rotation}deg) translateX(${(1 - p) * -12}px)`}}>→</div>;
}

function LabNode({label, sub, color = C.blue, delay = 0, className = ''}: {label: string; sub?: string; color?: string; delay?: number; className?: string}) {
  const frame = useCurrentFrame();
  return (
    <div className={`lab-node ${className}`} style={{...scaleIn(frame, delay), borderColor: `${color}70`, backgroundColor: `${color}0d`}}>
      <span className="node-mark" style={{color, borderColor: color}} />
      <div><strong>{label}</strong>{sub && <small>{sub}</small>}</div>
    </div>
  );
}

export function ResearchWorldGlyph({large = false, delay = 0}: {large?: boolean; delay?: number}) {
  const frame = useCurrentFrame();
  const pulse = 1 + Math.sin((frame - delay) / 22) * 0.025;
  return (
    <div className={`world-glyph ${large ? 'world-glyph-large' : ''}`} style={{...scaleIn(frame, delay), transform: `scale(${pulse})`}}>
      {[0, 1, 2].map((ring) => <div key={ring} className="world-ring" style={{inset: ring * 15, opacity: 0.2 + (2 - ring) * 0.12, borderColor: ring === 1 ? C.blue : C.aqua}} />)}
      <div className="world-core" />
      <span className="world-particle p1" /><span className="world-particle p2" /><span className="world-particle p3" />
    </div>
  );
}

export function ScientistGlyph({color = C.purple, delay = 0}: {color?: string; delay?: number}) {
  const frame = useCurrentFrame();
  return (
    <div className="scientist-glyph" style={{...scaleIn(frame, delay), color}}>
      <div className="scientist-head" />
      <div className="scientist-body" />
      <div className="scientist-flask"><i /><b /></div>
    </div>
  );
}

function IntroScene() {
  const frame = useCurrentFrame();
  const coverOpacity = interpolate(frame, [0, 40], [0, 0.28], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <Scene scene="01">
      <Img src={staticFile('assets/research-world-cover.png')} className="cover-image" style={{opacity: coverOpacity, transform: `scale(${1.03 - interpolate(frame, [0, 180], [0, 0.02], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})})`}} />
      <div className="intro-layout">
        <WordReveal delay={16}><Eyebrow color={C.blue}>AUTONOMOUS ML RESEARCH / TECHJAM 2026</Eyebrow></WordReveal>
        <WordReveal className="intro-title" delay={36}>Research Agent</WordReveal>
        <WordReveal className="intro-subtitle" delay={58}>Autonomous ML discovery through <span className="blue">pure evidence.</span></WordReveal>
        <AccentLine delay={82} color={C.blue} width={220} />
        <div className="intro-tags">
          <Pill delay={98} color={C.blue}>PERSISTENT WORLD</Pill>
          <Pill delay={108} color={C.purple}>FRESH SCIENTIST</Pill>
          <Pill delay={118} color={C.orange}>EVIDENCE FIRST</Pill>
        </div>
      </div>
      <div className="intro-mark" style={{opacity: interpolate(frame, [28, 100], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        <svg viewBox="0 0 760 760" aria-hidden="true">
          <path className="intro-path p-blue" d="M0 322 C190 322 210 250 340 314 S550 370 676 370" style={{strokeDashoffset: 1 - interpolate(frame, [30, 100], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
          <path className="intro-path p-orange" d="M0 444 C170 444 240 500 360 432 S550 378 676 370" style={{strokeDashoffset: 1 - interpolate(frame, [42, 110], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
          <path className="intro-path p-purple" d="M80 640 C228 598 240 530 388 487 S570 389 676 370" style={{strokeDashoffset: 1 - interpolate(frame, [56, 124], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
          <g transform="translate(676 370)"><ResearchWorldGlyph large delay={75} /></g>
        </svg>
      </div>
    </Scene>
  );
}

function BasinDiagram() {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [30, 170], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const dash = 1 - progress;
  return (
    <div className="basin-diagram">
      <svg viewBox="0 0 810 610" preserveAspectRatio="none" aria-hidden="true">
        <line x1="0" y1="505" x2="810" y2="505" stroke={C.line} strokeWidth="1" />
        <line x1="0" y1="270" x2="810" y2="270" stroke={C.line} strokeWidth="1" strokeDasharray="4 12" />
        <path d="M10 122 C138 42 182 170 265 144 S342 70 403 182 S498 355 600 274 S735 210 800 319" fill="none" stroke={C.orange} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={dash} />
        <path d="M8 436 C124 392 166 492 251 414 S346 307 421 390 S516 490 601 326 S733 245 800 319" fill="none" stroke={C.rose} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={Math.max(0, dash - .12)} />
        <path d="M8 278 C128 294 190 237 275 310 S384 414 464 345 S567 245 639 317 S726 337 800 319" fill="none" stroke={C.blue} strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={Math.max(0, dash - .24)} />
        <circle cx="800" cy="319" r="12" fill={C.paper} stroke={C.green} strokeWidth="4" />
        <circle cx="800" cy="319" r="28" fill="none" stroke={C.green} strokeOpacity=".22" />
      </svg>
      <div className="basin-label basin-label-top" style={reveal(frame, 88, 12)}><span className="orange">LONG CONTEXT</span><strong>Experience carries momentum.</strong><small>Knowledge + commitment to the current direction</small></div>
      <div className="basin-label basin-label-bottom" style={reveal(frame, 110, 12)}><span className="rose">NAIVE RESTART</span><strong>A fresh start loses progress.</strong><small>Relearn the evaluator. Repeat failures.</small></div>
      <div className="basin-end-label" style={reveal(frame, 148, 10)}><span>same search basin</span></div>
    </div>
  );
}

function ProblemScene() {
  const frame = useCurrentFrame();
  return (
    <Scene scene="02">
      <div className="problem-layout">
        <div className="problem-copy">
          <WordReveal delay={14}><Eyebrow color={C.orange}>01 / THE FAILURE MODE</Eyebrow></WordReveal>
          <WordReveal className="scene-title problem-title" delay={34}>More experiments.<br /><span className="muted">The same search basin.</span></WordReveal>
          <Rule style={{width: 180, marginTop: 42}} />
          <WordReveal className="problem-question" delay={74}>How do we inherit experience<br />and reopen the search?</WordReveal>
        </div>
        <BasinDiagram />
      </div>
    </Scene>
  );
}

function ThesisScene() {
  const frame = useCurrentFrame();
  const split = interpolate(frame, [86, 140], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <Scene scene="03">
      <div className="thesis-layout">
        <div className="thesis-copy">
          <WordReveal delay={16}><Eyebrow>02 / THE CORE IDEA</Eyebrow></WordReveal>
          <WordReveal className="thesis-title" delay={36}>Preserve the<br /><span className="green">research world.</span><br /><span className="purple">Reset the researcher.</span></WordReveal>
          <WordReveal className="thesis-caption" delay={84}>Pass evidence, failures, and code to a fresh Scientist.</WordReveal>
        </div>
        <div className="thesis-visual">
          <div className="thesis-world" style={{...reveal(frame, 44, 18), transform: `translateX(${(1 - split) * -18}px)`}}>
            <ResearchWorldGlyph large delay={55} />
            <div className="thesis-label"><span className="green">RESEARCH WORLD</span><small>persists across trajectories</small></div>
          </div>
          <div className="thesis-boundary" style={{height: `${split * 410}px`, opacity: split}}><span>CONTEXT RESET</span></div>
          <div className="thesis-scientist" style={{...reveal(frame, 115, 18), transform: `translateX(${split * 18}px)`}}>
            <ScientistGlyph delay={126} />
            <div className="thesis-label"><span className="purple">FRESH SCIENTIST</span><small>inherits experience, not momentum</small></div>
          </div>
        </div>
      </div>
    </Scene>
  );
}

type SystemColumnProps = {title: string; color: string; children: React.ReactNode; delay: number; className?: string};

function SystemColumn({title, color, children, delay, className = ''}: SystemColumnProps) {
  const frame = useCurrentFrame();
  return (
    <div className={`system-column ${className}`} style={{...reveal(frame, delay, 24), borderColor: `${color}70`}}>
      <div className="system-column-title" style={{color}}>{title}</div>
      <div className="system-column-body">{children}</div>
    </div>
  );
}

function SystemScene() {
  const frame = useCurrentFrame();
  const runtimeP = interpolate(frame, [188, 256], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <Scene scene="04" className="system-scene">
      <div className="system-header">
        <WordReveal delay={12}><Eyebrow color={C.blue}>03 / SEPARATION OF RESPONSIBILITIES</Eyebrow></WordReveal>
        <WordReveal className="scene-title" delay={30}>Two scientific roles. <span className="muted">One safe runtime.</span></WordReveal>
      </div>
      <div className="system-flow">
        <SystemColumn title="ENVIRONMENT" color={C.blue} delay={50}>
          <LabNode label="Task contract" sub="objective + protocol" color={C.blue} delay={70} />
          <LabNode label="Data + evaluator" sub="approved view + metrics" color={C.blue} delay={80} />
          <LabNode label="Starter baseline" sub="initial code + reference" color={C.blue} delay={90} />
          <LabNode label="Budget + permissions" sub="constraints + actions" color={C.blue} delay={100} />
        </SystemColumn>
        <Arrow color={C.blue} delay={102} />
        <SystemColumn title="RESEARCH WORLD" color={C.green} delay={74} className="system-world">
          <div className="world-section" style={reveal(frame, 102, 8)}><span className="mono">A / VERIFIED</span><b>Evidence ledger</b><small>facts · results · failures · provenance</small></div>
          <div className="world-section" style={reveal(frame, 112, 8)}><span className="mono">B / CURATED</span><b>Research brief</b><small>current understanding + open questions</small></div>
          <div className="world-section" style={reveal(frame, 122, 8)}><span className="mono">C / IMPLEMENTATION</span><b>State + code</b><small>retained system · versioned state</small></div>
          <div className="persist-label" style={{opacity: interpolate(frame, [146, 172], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>what persists across trajectories</div>
        </SystemColumn>
        <div className="reset-column" style={reveal(frame, 124, 18)}>
          <div className="reset-orbit"><span>↻</span></div>
          <strong>CONTEXT<br />RESET</strong>
          <small>No previous<br />reasoning trajectory</small>
        </div>
        <Arrow color={C.purple} delay={144} />
        <SystemColumn title="FRESH SCIENTIST" color={C.purple} delay={142} className="scientist-column">
          <ScientistGlyph delay={156} />
          <strong className="system-hero-title">Scientist</strong>
          <small className="system-hero-subtitle">owns scientific judgment</small>
          <Rule style={{margin: '18px 0 10px', background: '#dfd5f8'}} />
          <ul><li>reads the research world</li><li>forms hypotheses</li><li>runs experiments</li><li>interprets evidence</li></ul>
          <Pill color={C.purple} delay={188}>inherits experience, not momentum</Pill>
        </SystemColumn>
        <Arrow color={C.rose} delay={180} />
        <SystemColumn title="META REVIEW" color={C.rose} delay={176} className="meta-column">
          <div className="meta-shield">✓</div>
          <strong className="system-hero-title">META</strong>
          <small className="system-hero-subtitle rose-text">owns what survives</small>
          <Rule style={{margin: '18px 0 10px', background: '#ffd2d2'}} />
          <ul><li>audits claim ↔ evidence validity</li><li>scopes conclusions</li><li>maintains shared memory</li><li>crystallizes State</li></ul>
        </SystemColumn>
      </div>
      <div className="runtime-band" style={{opacity: runtimeP, transform: `translateY(${(1 - runtimeP) * 18}px)`}}>
        <strong style={{color: C.orange}}>Runtime — deterministic mechanics</strong>
        <div className="runtime-items"><span>workspace isolation</span><span>runner + evaluator</span><span>logging</span><span>artifact capture</span><span>state operations</span></div>
      </div>
    </Scene>
  );
}

function HandoffLoop() {
  const frame = useCurrentFrame();
  const loopProgress = interpolate(frame, [42, 188], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <Scene scene="05">
      <div className="loop-header">
        <WordReveal delay={14}><Eyebrow color={C.orange}>04 / THE HANDOFF LOOP</Eyebrow></WordReveal>
        <WordReveal className="scene-title" delay={30}>Each cycle leaves a world to build on.</WordReveal>
      </div>
      <div className="loop-stage">
        <svg className="loop-lines" viewBox="0 0 1600 500" preserveAspectRatio="none" aria-hidden="true">
          <path d="M165 210 H455 M545 210 H835 M925 210 H1215" fill="none" stroke={C.line} strokeWidth="2" />
          <path d="M1295 260 V405 H155 V260" fill="none" stroke={C.rose} strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - loopProgress} />
        </svg>
        <div className="loop-node node-world" style={reveal(frame, 48, 16)}><ResearchWorldGlyph /><strong>WORLD</strong><small>evidence + state</small></div>
        <Arrow color={C.blue} delay={72} />
        <div className="loop-node node-scientist" style={reveal(frame, 74, 16)}><ScientistGlyph /><strong>SCIENTIST</strong><small>hypothesis + experiment</small></div>
        <Arrow color={C.purple} delay={96} />
        <div className="loop-node node-evidence" style={reveal(frame, 98, 16)}><div className="evidence-stack"><Pill color={C.blue} delay={112}>metrics</Pill><Pill color={C.orange} delay={120}>failures</Pill><Pill color={C.green} delay={128}>code</Pill></div><strong>EVIDENCE</strong><small>report the result</small></div>
        <Arrow color={C.rose} delay={124} />
        <div className="loop-node node-meta" style={reveal(frame, 122, 16)}><div className="meta-shield small-shield">✓</div><strong>META</strong><small>audit · scope · preserve</small></div>
        <div className="loop-return" style={{opacity: loopProgress}}><span>SELECTIVE PERSISTENCE</span><small>updated world → fresh Scientist</small></div>
      </div>
      <WordReveal className="loop-footer" delay={156}><span className="green">Audit, compress, preserve</span> <span className="muted">→ updated world → fresh Scientist</span></WordReveal>
    </Scene>
  );
}

function MemoryTree() {
  const frame = useCurrentFrame();
  const items = [
    ['evidence & provenance', C.blue],
    ['verified knowledge', C.green],
    ['current research state', C.aqua],
    ['fallible priors', C.purple],
    ['State + implementation', C.orange],
  ];
  return (
    <div className="memory-tree">
      <div className="tree-root" style={reveal(frame, 24, 12)}><span className="mono">research world</span></div>
      <div className="tree-branch-line" />
      {items.map(([label, color], index) => (
        <div className="tree-item" key={label as string} style={{...reveal(frame, 44 + index * 16, 10), borderColor: `${color as string}77`}}>
          <span style={{backgroundColor: color as string}} />
          <span>{label as string}</span>
        </div>
      ))}
      <div className="tree-raw" style={reveal(frame, 142, 8)}><span className="mono">↳ original reports remain available for audit</span></div>
    </div>
  );
}

function Branches() {
  const frame = useCurrentFrame();
  const branches = [
    ['A', C.blue, 'Scientist A', 'world A'],
    ['B', C.purple, 'Scientist B', 'world B'],
    ['C', C.orange, 'Scientist C', 'world C'],
  ];
  return (
    <div className="branches-visual">
      <div className="branch-root" style={reveal(frame, 30, 12)}><ResearchWorldGlyph /><span>one starting point</span></div>
      <svg viewBox="0 0 620 430" preserveAspectRatio="none" aria-hidden="true">
        {branches.map((_, index) => <path key={index} d={`M120 200 C210 200 235 ${110 + index * 90} 305 ${110 + index * 90} H580`} fill="none" stroke={branches[index][1]} strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - interpolate(frame - (48 + index * 16), [0, 54], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />)}
      </svg>
      <div className="branch-outputs">
        {branches.map(([key, color, scientist, world], index) => <div key={key} className="branch-output" style={{...reveal(frame, 78 + index * 16, 12), borderColor: `${color}70`}}><b style={{color}}>{key}</b><span>{scientist} <i>→</i> {world}</span></div>)}
      </div>
      <div className="branch-caption" style={reveal(frame, 148, 8)}>isolated worktrees · review after completion</div>
    </div>
  );
}

function MemoryScene() {
  return (
    <Scene scene="06">
      <div className="memory-layout">
        <div className="memory-copy">
          <WordReveal delay={14}><Eyebrow color={C.green}>05 / MEMORY ON DISK</Eyebrow></WordReveal>
          <WordReveal className="scene-title" delay={32}>Keep facts distinct<br /><span className="muted">from intuition.</span></WordReveal>
          <WordReveal className="memory-note" delay={68}>Facts have evidence.<br />Priors can be overturned.<br />Code can be picked up again.</WordReveal>
          <AccentLine color={C.green} delay={98} width={130} />
          <WordReveal className="memory-parallel-kicker" delay={128}><Eyebrow color={C.purple}>06 / PARALLEL BREADTH</Eyebrow></WordReveal>
          <WordReveal className="memory-parallel-title" delay={146}>One starting point.<br /><span className="purple">Independent answers.</span></WordReveal>
        </div>
        <div className="memory-visual"><MemoryTree /><Branches /></div>
      </div>
    </Scene>
  );
}

function EvidenceChart() {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [52, 146], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const points = [
    {x: 180, y: 300, color: C.blue, label: 'official FM', shape: 'circle'},
    {x: 420, y: 262, color: C.blue, label: 'direct', shape: 'circle'},
    {x: 620, y: 244, color: C.orange, label: 'separate run', shape: 'diamond'},
    {x: 780, y: 210, color: C.green, label: 'verified retained', shape: 'dot'},
  ];
  return (
    <div className="evidence-chart">
      <svg viewBox="0 0 930 460" aria-hidden="true">
        {[72, 164, 256, 348].map((y) => <line key={y} x1="70" y1={y} x2="890" y2={y} stroke={C.line} strokeWidth="1" />)}
        {[70, 270, 470, 670, 870].map((x) => <line key={x} x1={x} y1="56" x2={x} y2="360" stroke={C.line} strokeWidth="1" />)}
        <line x1="70" y1="360" x2="890" y2="360" stroke={C.muted} strokeWidth="1" />
        <line x1="70" y1="334" x2="890" y2="334" stroke={C.muted} strokeWidth="2" strokeDasharray="7 10" opacity=".65" />
        <text x="740" y="326" className="chart-small">Official reference 0.601600</text>
        {points.map((point, index) => {
          const q = interpolate(frame - (64 + index * 14), [0, 45], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const x = 70 + (point.x - 70) * q;
          const y = 360 - (360 - point.y) * q;
          return <g key={point.label} opacity={q * p}>
            {point.shape === 'diamond' ? <rect x={x - 11} y={y - 11} width="22" height="22" fill={C.paper} stroke={point.color} strokeWidth="4" transform={`rotate(45 ${x} ${y})`} /> : <circle cx={x} cy={y} r={point.shape === 'dot' ? 13 : 11} fill={point.shape === 'dot' ? point.color : C.paper} stroke={point.color} strokeWidth="4" />}
            {index === 3 && <><line x1={x - 4} y1={y - 17} x2="710" y2="120" stroke={point.color} /><text x="500" y="98" className="chart-label">Research Agent submission</text><text x="500" y="120" className="chart-small">48.240M total · 0.605936 · verified</text></>}
          </g>;
        })}
      </svg>
      <div className="chart-axis axis-y">PUBLIC-VALIDATION PRIMARY</div>
      <div className="chart-axis axis-x mono">MEASURED TOKEN INVESTMENT →</div>
    </div>
  );
}

function ValidationScene() {
  const frame = useCurrentFrame();
  const bar = interpolate(frame, [44, 130], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <Scene scene="07">
      <div className="validation-header">
        <WordReveal delay={14}><Eyebrow color={C.green}>07 / KUAIRAND-PURE · PUBLIC VALIDATION</Eyebrow></WordReveal>
        <WordReveal className="scene-title" delay={32}>Autonomous research. <span className="muted">Measured gains.</span></WordReveal>
      </div>
      <div className="validation-main">
        <div className="score-block">
          <div className="mono score-kicker" style={reveal(frame, 48, 12)}>PRIMARY / RESEARCH AGENT</div>
          <div className="score-number" style={{...reveal(frame, 64, 16), color: C.green}}>0.6059363</div>
          <div className="score-delta" style={reveal(frame, 88, 12)}><span className="green">+0.0043363</span> <span className="muted">absolute improvement</span></div>
          <div className="score-bar"><div className="score-bar-base" /><div className="score-bar-fill" style={{width: `${bar * 100}%`}} /><span className="score-bar-label">public validation / unchanged Starter Kit alignment</span></div>
          <div className="metric-grid">
            <Metric value="0.6728421" label="GAUC" color={C.blue} delay={112} small />
            <Metric value="0.5390304" label="nDCG@5" color={C.orange} delay={124} small />
            <Metric value="8 × 46" label="ENSEMBLE" color={C.purple} delay={136} detail="seeds × categorical fields" small />
          </div>
        </div>
        <div className="chart-block">
          <EvidenceChart />
          <div className="chart-caption">Measured token investment, public-validation score, and the verified retained result.</div>
        </div>
      </div>
    </Scene>
  );
}

function DashboardPanel({delay = 0}: {delay?: number}) {
  const frame = useCurrentFrame();
  return (
    <div className="dashboard-panel" style={scaleIn(frame, delay)}>
      <div className="dashboard-top"><span className="dashboard-icon">★</span><strong>Retained Validation Result</strong><span className="dashboard-badge">retained checkpoint</span></div>
      <Rule />
      <div className="dashboard-meta"><span className="mono">S004 / SCORE-BEARING CHECKPOINT</span><span>8-seed ensemble · 46-field Factorization Machine</span></div>
      <div className="dashboard-metrics"><div><span>GAUC</span><b>0.672842</b></div><div><span>nDCG@5</span><b>0.539030</b></div><div><span>Primary</span><b className="green">0.605936</b></div><div><span>Delta vs baseline</span><b>+0.004336</b></div></div>
      <div className="dashboard-evidence mono">Evidence · system/evidence/cycle4-fm-rich46-ensemble8-full.json</div>
    </div>
  );
}

function ClosingScene() {
  const frame = useCurrentFrame();
  return (
    <Scene scene="08">
      <Sequence from={0} durationInFrames={190}>
        <div className="closing-layer" style={{opacity: interpolate(frame, [140, 170], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        <div className="audit-layout">
          <div className="audit-copy">
            <WordReveal delay={14}><Eyebrow color={C.orange}>08 / AUTONOMY WITH AN AUDIT TRAIL</Eyebrow></WordReveal>
            <WordReveal className="scene-title" delay={32}>An audit trail<br /><span className="muted">from experiment to output.</span></WordReveal>
            <WordReveal className="audit-note" delay={72}>Reproducible evidence. Open questions.<br /><span className="muted">The retained result stays connected to what made it.</span></WordReveal>
            <AccentLine color={C.orange} width={140} delay={106} />
          </div>
          <div className="audit-stats">
            <Metric value="4" label="AUTONOMOUS CYCLES" detail="within a 50-iteration cap" color={C.blue} delay={54} />
            <Metric value="13" label="NAMED EXPERIMENTS" detail="E001–E013 · 7 full evaluations" color={C.orange} delay={74} />
            <Metric value="0" label="MANUAL INTERVENTIONS" detail="after launch · 0 GPU-hours" color={C.rose} delay={94} />
            <div className="audit-foot mono" style={reveal(frame, 118, 8)}>170,588 prediction rows · unchanged alignment checker</div>
          </div>
        </div>
        </div>
      </Sequence>
      <Sequence from={160} durationInFrames={135}>
        <div className="closing-layer" style={{opacity: interpolate(frame, [160, 185, 260, 295], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        <div className="checkpoint-layout">
          <div className="checkpoint-heading"><Eyebrow color={C.purple}>RETAINED CHECKPOINT</Eyebrow><span>A durable state makes the gain inspectable.</span></div>
          <DashboardPanel delay={12} />
        </div>
        </div>
      </Sequence>
      <Sequence from={260} durationInFrames={70}>
        <div className="closing-layer" style={{opacity: interpolate(frame, [260, 280, 300, 330], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        <div className="questions-layout">
          <Eyebrow color={C.green}>EVIDENCE BOUNDARY</Eyebrow>
          <div className="questions-title">Reproducible evidence.<br /><span className="muted">Open questions.</span></div>
          <div className="questions-row"><Pill color={C.green} delay={12}>broader tasks</Pill><Pill color={C.green} delay={26}>targeted ablations</Pill><Pill color={C.green} delay={40}>memory quality</Pill></div>
        </div>
        </div>
      </Sequence>
      <div className="closing-layout" style={{opacity: interpolate(frame, [330, 360], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}), transform: `translateY(${(1 - interpolate(frame, [330, 360], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})) * 24}px)`}}>
        <Eyebrow color={C.blue}>START A FRESH TRAJECTORY</Eyebrow>
        <div className="closing-title">Keep the experience.<br /><span className="blue">Reopen the search.</span></div>
        <div className="terminal"><span className="muted"># one autonomous cycle</span><br /><span className="green">$</span> ./scripts/research-agent step --cli codex \<br />&nbsp;&nbsp;--target /absolute/path/to/project --allow-edits</div>
        <div className="closing-meta mono">github.com/zc6600/research-agent-kuairand <span className="blue">↗</span></div>
      </div>
    </Scene>
  );
}

export const SciOdysseyFilm: React.FC<FilmProps> = ({voiceOverSrc, musicSrc}) => {
  return (
    <AbsoluteFill className="film-root">
      <Sequence from={0} durationInFrames={180}><IntroScene /></Sequence>
      <Sequence from={180} durationInFrames={240}><ProblemScene /></Sequence>
      <Sequence from={420} durationInFrames={180}><ThesisScene /></Sequence>
      <Sequence from={600} durationInFrames={360}><SystemScene /></Sequence>
      <Sequence from={960} durationInFrames={270}><HandoffLoop /></Sequence>
      <Sequence from={1230} durationInFrames={270}><MemoryScene /></Sequence>
      <Sequence from={1500} durationInFrames={360}><ValidationScene /></Sequence>
      <Sequence from={1860} durationInFrames={390}><ClosingScene /></Sequence>
      {voiceOverSrc ? <Audio src={voiceOverSrc} /> : null}
      {musicSrc ? <Audio src={musicSrc} volume={0.18} /> : null}
    </AbsoluteFill>
  );
};
