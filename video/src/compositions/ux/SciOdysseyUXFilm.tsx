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
} from 'remotion';
import {
  C,
  ResearchWorldGlyph,
  ScientistGlyph,
  type FilmProps,
} from '../launch/SciOdysseyFilm';

const motion = (frame: number, delay = 0, distance = 28, duration = 24) => {
  const p = interpolate(frame - delay, [0, duration], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return {opacity: p, transform: `translateY(${(1 - p) * distance}px)`};
};

const springIn = (frame: number, delay = 0, scale = 0.88) => {
  const p = spring({frame: frame - delay, fps: 30, config: {damping: 17, stiffness: 110, mass: 0.8}});
  return {opacity: interpolate(frame - delay, [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}), transform: `scale(${scale + p * (1 - scale)})`};
};

const appear = (frame: number, delay: number, duration = 24) => interpolate(frame - delay, [0, duration], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

function KeynoteFrame({children, className = ''}: {children: React.ReactNode; className?: string}) {
  return <AbsoluteFill className={`keynote-frame ${className}`}>{children}</AbsoluteFill>;
}

function QuietMark({color = C.ink}: {color?: string}) {
  return <div className="quiet-mark" style={{color}}><span className="quiet-mark-dot" style={{backgroundColor: color}} />SCIODYSSEY</div>;
}

function FineLabel({children, color = C.muted, className = ''}: {children: React.ReactNode; color?: string; className?: string}) {
  return <div className={`fine-label ${className}`} style={{color}}>{children}</div>;
}

function BigLine({children, className = '', delay = 0}: {children: React.ReactNode; className?: string; delay?: number}) {
  const frame = useCurrentFrame();
  return <div className={`keynote-big-line ${className}`} style={motion(frame, delay, 34)}>{children}</div>;
}

function DrawnPath({d, color, delay = 0, duration = 70, className = ''}: {d: string; color: string; delay?: number; duration?: number; className?: string}) {
  const frame = useCurrentFrame();
  const progress = appear(frame, delay, duration);
  return <path d={d} className={className} fill="none" stroke={color} pathLength="1" strokeDasharray="1" strokeDashoffset={1 - progress} />;
}

function WorldOrbit({size = 260, delay = 0, className = ''}: {size?: number; delay?: number; className?: string}) {
  const frame = useCurrentFrame();
  const pulse = 1 + Math.sin((frame - delay) / 24) * 0.018;
  return <div className={`world-orbit ${className}`} style={{width: size, height: size, ...springIn(frame, delay), transform: `scale(${pulse})`}}><ResearchWorldGlyph large /></div>;
}

function IntroCinematic() {
  const frame = useCurrentFrame();
  const imageOpacity = interpolate(frame, [0, 70], [0, 0.19], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const field = appear(frame, 35, 110);
  return (
    <KeynoteFrame className="intro-cinematic">
      <Img className="intro-art" src={staticFile('assets/research-world-cover.png')} style={{opacity: imageOpacity, transform: `scale(${1.04 - appear(frame, 0, 300) * 0.02})`}} />
      <QuietMark color={C.blue} />
      <svg className="intro-trajectory-field" viewBox="0 0 1920 1080" aria-hidden="true">
        <DrawnPath d="M-20 610 C300 610 402 394 700 480 S1188 732 1605 405 S1850 315 1980 315" color={C.blue} delay={40} duration={120} />
        <DrawnPath d="M-20 730 C282 730 385 846 680 738 S1152 441 1490 584 S1802 804 1960 728" color={C.orange} delay={58} duration={120} />
        <DrawnPath d="M-30 460 C264 426 480 520 702 635 S1118 572 1450 690 S1780 540 1960 470" color={C.purple} delay={76} duration={120} />
        <circle cx="1595" cy="515" r="8" fill={C.green} opacity={field} />
      </svg>
      <div className="intro-hero">
        <BigLine delay={24}>Research shouldn’t<br /><span className="muted">start over.</span></BigLine>
        <div className="intro-subline" style={motion(frame, 90, 18)}>Autonomous ML discovery through <span className="blue">pure evidence.</span></div>
      </div>
      <WorldOrbit size={360} delay={82} className="intro-world" />
      <div className="intro-endnote" style={motion(frame, 142, 10)}><span>KEEP THE EXPERIENCE</span><span className="blue">REOPEN THE SEARCH</span></div>
    </KeynoteFrame>
  );
}

function BriefField({label, value, color, delay}: {label: string; value: string; color: string; delay: number}) {
  const frame = useCurrentFrame();
  return <div className="brief-row" style={motion(frame, delay, 12)}><span style={{color}}>{label}</span><strong>{value}</strong></div>;
}

function BriefWindow() {
  const frame = useCurrentFrame();
  const active = appear(frame, 112, 28);
  const fields = [
    ['TASK CONTRACT', 'Improve the public validation score', C.blue, 52],
    ['DATA + EVALUATOR', 'Curated view · unchanged checker', C.green, 68],
    ['STARTER BASELINE', 'Reference pipeline · versioned', C.orange, 84],
    ['BUDGET + PERMISSIONS', '50 iterations · allow edits', C.purple, 100],
  ] as const;
  return (
    <div className="brief-window" style={springIn(frame, 35)}>
      <div className="brief-window-top"><span className="window-dot blue-bg" /><div><strong>New research task</strong><small>READY TO LAUNCH</small></div><span className="window-menu">···</span></div>
      <div className="brief-rule" />
      {fields.map(([label, value, color, delay]) => <BriefField key={label} label={label} value={value} color={color} delay={delay} />)}
      <div className="brief-action" style={{opacity: active, transform: `translateY(${(1 - active) * 12}px)`}}><span>launch Scientist</span><b>→</b></div>
    </div>
  );
}

function BriefCinematic() {
  const frame = useCurrentFrame();
  const line = appear(frame, 45, 110);
  return (
    <KeynoteFrame className="brief-cinematic">
      <QuietMark color={C.blue} />
      <div className="brief-copy"><FineLabel color={C.blue}>START WITH A QUESTION</FineLabel><BigLine delay={18}>Give the search<br /><span className="muted">a world to work in.</span></BigLine><p style={motion(frame, 72, 16)}>Task contract. Evaluator. Baseline.<br />A safe place to try.</p></div>
      <BriefWindow />
      <svg className="brief-connector" viewBox="0 0 520 220" aria-hidden="true"><DrawnPath d="M0 110 C170 110 210 68 338 108 S450 140 520 110" color={C.blue} delay={55} duration={92} /><circle cx="520" cy="110" r="7" fill={C.blue} opacity={line} /></svg>
      <FineLabel color={C.muted} className="brief-footnote">explicit context <span className="blue">→</span> new trajectory</FineLabel>
    </KeynoteFrame>
  );
}

function HandoffCinematic() {
  const frame = useCurrentFrame();
  const reset = appear(frame, 90, 34);
  const scientistIn = appear(frame, 132, 30);
  return (
    <KeynoteFrame className="handoff-cinematic">
      <QuietMark color={C.purple} />
      <div className="handoff-title"><FineLabel color={C.purple}>KEEP THE WORLD</FineLabel><BigLine delay={16}>Reopen the<br /><span className="purple">search.</span></BigLine></div>
      <div className="handoff-stage">
        <div className="handoff-world"><WorldOrbit size={300} delay={30} /><FineLabel color={C.green}>RESEARCH WORLD</FineLabel><small>evidence · failures · code</small></div>
        <svg className="handoff-svg" viewBox="0 0 1120 420" aria-hidden="true"><DrawnPath d="M100 210 H1020" color={C.line} delay={28} duration={50} /><DrawnPath d="M105 210 C350 210 410 75 590 205 S820 342 1020 210" color={C.purple} delay={48} duration={110} /></svg>
        <div className="handoff-reset" style={{opacity: reset, transform: `scale(${0.86 + reset * 0.14})`}}><span>↻</span><small>CONTEXT<br />RESET</small></div>
        <div className="handoff-scientist" style={{opacity: scientistIn, transform: `translateY(${(1 - scientistIn) * 24}px)`}}><ScientistGlyph color={C.purple} /><FineLabel color={C.purple}>FRESH SCIENTIST</FineLabel><small>new reasoning trajectory</small></div>
      </div>
      <div className="handoff-tag" style={motion(frame, 174, 12)}><span className="green">inherits experience</span><span className="muted"> / not momentum</span></div>
    </KeynoteFrame>
  );
}

function PathChoice({label, sub, color, x, y, delay}: {label: string; sub: string; color: string; x: number; y: number; delay: number}) {
  const frame = useCurrentFrame();
  return <div className="path-choice" style={{left: x, top: y, ...motion(frame, delay, 18)}}><span className="path-choice-dot" style={{backgroundColor: color}} /><strong style={{color}}>{label}</strong><small>{sub}</small></div>;
}

function PathsCinematic() {
  const frame = useCurrentFrame();
  const paths = appear(frame, 28, 120);
  const recover = appear(frame, 142, 40);
  return (
    <KeynoteFrame className="paths-cinematic">
      <QuietMark color={C.orange} />
      <div className="paths-title"><FineLabel color={C.orange}>CHOOSE YOUR WAY FORWARD</FineLabel><BigLine delay={15}>Different ways.<br /><span className="muted">Same world.</span></BigLine></div>
      <div className="paths-stage">
        <div className="paths-origin" style={springIn(frame, 26)}><ResearchWorldGlyph /><span>one starting point</span></div>
        <svg className="paths-svg" viewBox="0 0 1160 610" aria-hidden="true"><DrawnPath d="M128 302 C280 302 310 120 490 120 H1065" color={C.blue} delay={32} duration={82} /><DrawnPath d="M128 302 H1065" color={C.purple} delay={47} duration={82} /><DrawnPath d="M128 302 C280 302 310 485 490 485 H1065" color={C.orange} delay={62} duration={82} /><circle cx="128" cy="302" r="7" fill={C.green} opacity={paths} /></svg>
        <PathChoice label="START" sub="from a brief" color={C.blue} x={720} y={80} delay={88} />
        <PathChoice label="EXPLORE" sub="in parallel" color={C.purple} x={720} y={262} delay={104} />
        <PathChoice label="RECOVER" sub="when reality breaks" color={C.orange} x={720} y={445} delay={120} />
        <div className="recover-rail" style={{opacity: recover, transform: `translateY(${(1 - recover) * 14}px)`}}><span className="mono">fail</span><b>→</b><span className="mono">inspect</span><b>→</b><span className="mono">learn</span><b>→</b><span className="mono orange">extend</span><b>→</b><span className="mono green">retry</span></div>
      </div>
      <div className="paths-foot" style={motion(frame, 196, 10)}>shell · files · browser · git <span className="muted">/ open action space</span></div>
    </KeynoteFrame>
  );
}

function LedgerLine({time, copy, color, delay}: {time: string; copy: string; color: string; delay: number}) {
  const frame = useCurrentFrame();
  return <div className="ledger-line" style={{...motion(frame, delay, 14), borderColor: `${color}66`}}><span className="ledger-time mono">{time}</span><i style={{backgroundColor: color}} /><span>{copy}</span><b style={{color}}>✓</b></div>;
}

function EvidenceCinematic() {
  const frame = useCurrentFrame();
  const score = appear(frame, 170, 36);
  return (
    <KeynoteFrame className="evidence-cinematic">
      <QuietMark color={C.green} />
      <div className="evidence-title"><FineLabel color={C.green}>VALIDATE WHAT SURVIVES</FineLabel><BigLine delay={15}>Every path leaves<br /><span className="muted">evidence behind.</span></BigLine></div>
      <div className="ledger-window" style={springIn(frame, 35)}>
        <div className="ledger-head"><span className="ledger-check-icon">✓</span><div><strong>Evidence ledger</strong><small>S004 / RETAINED CHECKPOINT</small></div><span className="ledger-verified">verified</span></div>
        <div className="brief-rule" />
        <LedgerLine time="09:14" copy="E001 · baseline reproduced" color={C.blue} delay={62} />
        <LedgerLine time="09:31" copy="E007 · historical features tested" color={C.orange} delay={80} />
        <LedgerLine time="10:02" copy="E013 · 8-seed ensemble retained" color={C.green} delay={98} />
        <div className="ledger-trace mono" style={motion(frame, 124, 9)}>original reports remain available for audit</div>
      </div>
      <div className="evidence-score" style={{opacity: score, transform: `translateX(${(1 - score) * 26}px)`}}><FineLabel color={C.muted}>PUBLIC VALIDATION / PRIMARY</FineLabel><strong>0.6059363</strong><span><b className="green">+0.0043363</b> absolute improvement</span><div className="score-trace"><span style={{width: `${score * 100}%`}} /></div><small>GAUC 0.6728421 <i>·</i> nDCG@5 0.5390304</small></div>
      <div className="evidence-foot mono" style={motion(frame, 212, 8)}>170,588 prediction rows · unchanged alignment checker · 0 GPU-hours</div>
    </KeynoteFrame>
  );
}

function ClosingCinematic() {
  const frame = useCurrentFrame();
  const paths = appear(frame, 35, 130);
  const final = appear(frame, 120, 42);
  return (
    <KeynoteFrame className="closing-cinematic">
      <Img className="closing-art" src={staticFile('assets/research-world-cover.png')} style={{opacity: interpolate(frame, [100, 180], [0, .13], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
      <QuietMark color={C.blue} />
      <svg className="closing-paths" viewBox="0 0 1920 1080" aria-hidden="true"><DrawnPath d="M-80 700 C280 700 430 420 750 540 S1260 780 1620 380 S1860 280 2020 290" color={C.blue} delay={28} duration={120} /><DrawnPath d="M-80 800 C280 800 490 820 780 706 S1260 440 1600 620 S1870 830 2020 780" color={C.orange} delay={50} duration={120} /><DrawnPath d="M-80 590 C280 520 480 610 770 700 S1230 560 1590 740 S1870 610 2020 540" color={C.purple} delay={72} duration={120} /><circle cx="1590" cy="580" r="12" fill={C.green} opacity={paths} /></svg>
      <div className="closing-hero"><BigLine delay={14}>Keep the experience.<br /><span className="blue">Reopen the search.</span></BigLine><p style={motion(frame, 70, 16)}>Different ways of working.<br /><span className="muted">One evidence trail.</span></p></div>
      <div className="closing-proof" style={{opacity: final, transform: `translateY(${(1 - final) * 16}px)`}}><FineLabel color={C.green}>RETAINED PUBLIC VALIDATION</FineLabel><strong>0.6059363</strong><span>research-agent step · ready for a fresh trajectory</span></div>
      <div className="closing-command mono" style={{opacity: final, transform: `translateY(${(1 - final) * 16}px)`}}><span className="muted">$</span> ./scripts/research-agent step --cli codex <span className="muted">↗</span></div>
    </KeynoteFrame>
  );
}

export const SciOdysseyUXFilm: React.FC<FilmProps> = ({voiceOverSrc, musicSrc}) => {
  return (
    <AbsoluteFill className="film-root cinematic-film">
      <Sequence from={0} durationInFrames={330}><IntroCinematic /></Sequence>
      <Sequence from={330} durationInFrames={300}><BriefCinematic /></Sequence>
      <Sequence from={630} durationInFrames={330}><HandoffCinematic /></Sequence>
      <Sequence from={960} durationInFrames={330}><PathsCinematic /></Sequence>
      <Sequence from={1290} durationInFrames={330}><EvidenceCinematic /></Sequence>
      <Sequence from={1620} durationInFrames={270}><ClosingCinematic /></Sequence>
      {voiceOverSrc ? <Audio src={voiceOverSrc} /> : null}
      {musicSrc ? <Audio src={musicSrc} volume={0.18} /> : null}
    </AbsoluteFill>
  );
};
