import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {ResearchWorldGlyph, ScientistGlyph} from '../launch/SciOdysseyFilm';
import {V2C, beat, charReveal, draw, linear, p, pulse, slideIn, slideUp, springIn} from './v2-motion';

export function Surface({children, tone = 'light'}: {children: React.ReactNode; tone?: 'light' | 'dark'}) {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill className={`v2-surface v2-surface-${tone}`}>
      <div className="v2-grain" style={{backgroundPosition: `${(frame * 1.7) % 100}% ${((frame * 2.3) % 100)}%`}} />
      <div className="v2-vignette" />
      {children}
    </AbsoluteFill>
  );
}

export function TypeLine({text, start = 0, duration = 36, className = '', color}: {text: string; start?: number; duration?: number; className?: string; color?: string}) {
  const frame = useCurrentFrame();
  const count = charReveal(frame, start, duration, text);
  const reveal = p(frame, start, start + 10);
  return (
    <span className={`v2-type-line ${className}`} style={{opacity: reveal, color, translate: `0px ${(1 - reveal) * 16}px`}}>
      {text.slice(0, count)}
      <i className="v2-caret" style={{opacity: frame < start + duration + 18 ? 1 : 0}} />
    </span>
  );
}

export function Word({children, start = 0, className = '', color}: {children: React.ReactNode; start?: number; className?: string; color?: string}) {
  const frame = useCurrentFrame();
  return <div className={`v2-word ${className}`} style={{...slideUp(frame, start), color}}>{children}</div>;
}

export function MicroLabel({children, color = V2C.muted, start = 0, className = ''}: {children: React.ReactNode; color?: string; start?: number; className?: string}) {
  const frame = useCurrentFrame();
  return <span className={`v2-micro ${className}`} style={{...slideIn(frame, start, 18), color}}>{children}</span>;
}

export function Dot({color = V2C.blue, size = 8, glow = false, style}: {color?: string; size?: number; glow?: boolean; style?: React.CSSProperties}) {
  return <span className={`v2-dot ${glow ? 'v2-dot-glow' : ''}`} style={{width: size, height: size, backgroundColor: color, boxShadow: glow ? `0 0 ${size * 2}px ${color}` : undefined, ...style}} />;
}

export function Trace({d, color = V2C.blue, start = 0, duration = 60, width = 2, opacity = 1, dash = false}: {d: string; color?: string; start?: number; duration?: number; width?: number; opacity?: number; dash?: boolean}) {
  const frame = useCurrentFrame();
  const value = draw(frame, start, duration);
  return <path d={d} fill="none" stroke={color} strokeWidth={width} pathLength="1" strokeDasharray={dash ? '0.018 0.028' : '1'} strokeDashoffset={dash ? 0 : 1 - value} opacity={opacity * Math.min(1, value * 1.8)} vectorEffect="non-scaling-stroke" />;
}

export function TraceDot({x, y, color = V2C.blue, start = 0, duration = 60, r = 7}: {x: number; y: number; color?: string; start?: number; duration?: number; r?: number}) {
  const frame = useCurrentFrame();
  const value = draw(frame, start, duration);
  return <circle cx={x} cy={y} r={r} fill={color} opacity={value} />;
}

export function V2World({size = 280, start = 0, color = V2C.cyan, label, detail, className = '', style}: {size?: number; start?: number; color?: string; label?: string; detail?: string; className?: string; style?: React.CSSProperties}) {
  const frame = useCurrentFrame();
  const entrance = springIn(frame, start, 0.7);
  const orbitRotation = (frame - start) * 0.55;
  const outerPulse = pulse(frame, start, 28, 0.018);
  return (
    <div className={`v2-world ${className}`} style={{width: size, height: size, ...entrance, scale: entrance.scale * outerPulse, ...style}}>
      <div className="v2-world-orbit" style={{rotate: `${orbitRotation}deg`}}>
        <span className="v2-world-ring v2-world-ring-outer" style={{borderColor: color}} />
        <span className="v2-world-ring v2-world-ring-middle" style={{borderColor: V2C.blue}} />
        <span className="v2-world-ring v2-world-ring-inner" style={{borderColor: V2C.violet}} />
        <Dot color={color} size={10} glow style={{position: 'absolute', left: '10%', top: '38%'}} />
        <Dot color={V2C.orange} size={7} style={{position: 'absolute', right: '16%', top: '18%'}} />
        <Dot color={V2C.green} size={8} style={{position: 'absolute', right: '8%', bottom: '25%'}} />
      </div>
      <div className="v2-world-glyph"><ResearchWorldGlyph large /></div>
      {label ? <strong style={{color}}>{label}</strong> : null}
      {detail ? <small>{detail}</small> : null}
    </div>
  );
}

export function V2Scientist({size = 130, color = V2C.violet, start = 0, label, detail, style}: {size?: number; color?: string; start?: number; label?: string; detail?: string; style?: React.CSSProperties}) {
  const frame = useCurrentFrame();
  return (
    <div className="v2-scientist" style={{width: size, ...springIn(frame, start, 0.76), ...style}}>
      <ScientistGlyph color={color} />
      {label ? <strong style={{color}}>{label}</strong> : null}
      {detail ? <small>{detail}</small> : null}
    </div>
  );
}

export function Terminal({title = '~/project', tag = 'LIVE', start = 0, lines = [], className = '', style}: {title?: string; tag?: string; start?: number; lines?: Array<{text: string; tone?: 'plain' | 'blue' | 'violet' | 'green' | 'orange' | 'muted'; delay?: number}>; className?: string; style?: React.CSSProperties}) {
  const frame = useCurrentFrame();
  const enter = p(frame, start, start + 18);
  return (
    <div className={`v2-terminal ${className}`} style={{opacity: enter, scale: 0.985 + enter * 0.015, ...style}}>
      <div className="v2-terminal-bar">
        <span className="v2-terminal-dots"><i /><i /><i /></span>
        <span>{title}</span>
        <b>{tag}</b>
      </div>
      <div className="v2-terminal-body">
        {lines.map((line, index) => {
          const lineStart = start + (line.delay ?? index * 16);
          const reveal = p(frame, lineStart, lineStart + 16);
          return <div className={`v2-terminal-line v2-terminal-line-${line.tone ?? 'plain'}`} key={`${line.text}-${index}`} style={{opacity: reveal, translate: `${(1 - reveal) * 22}px 0px`}}><span className="v2-terminal-prompt">{index === 0 ? '›' : '·'}</span>{line.text}</div>;
        })}
      </div>
    </div>
  );
}

export function FileToken({name, sub, color = V2C.blue, start = 0, className = '', style}: {name: string; sub?: string; color?: string; start?: number; className?: string; style?: React.CSSProperties}) {
  const frame = useCurrentFrame();
  return (
    <div className={`v2-file-token ${className}`} style={{...springIn(frame, start, 0.84), borderColor: `${color}78`, ...style}}>
      <span className="v2-file-icon" style={{color, borderColor: color}} />
      <span><strong>{name}</strong>{sub ? <small>{sub}</small> : null}</span>
    </div>
  );
}

export function ScreenPlane({src, title, tag = 'READ ONLY', color = V2C.green, start = 0, className = '', style, objectPosition = 'center top'}: {src: string; title: string; tag?: string; color?: string; start?: number; className?: string; style?: React.CSSProperties; objectPosition?: string}) {
  const frame = useCurrentFrame();
  const drift = Math.sin((frame - start) / 70) * 0.5;
  return (
    <div className={`v2-screen-plane ${className}`} style={{...springIn(frame, start, 0.88), ...style}}>
      <div className="v2-screen-bar">
        <span className="v2-terminal-dots"><i /><i /><i /></span>
        <span>{title}</span>
        <b style={{color}}>{tag}</b>
      </div>
      <div className="v2-screen-content"><Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition, scale: 1 + drift / 100}} /></div>
    </div>
  );
}

export function MetricToken({value, label, color = V2C.blue, start = 0, className = '', style}: {value: string; label: string; color?: string; start?: number; className?: string; style?: React.CSSProperties}) {
  const frame = useCurrentFrame();
  return <div className={`v2-metric-token ${className}`} style={{...slideUp(frame, start, 26), ...style}}><strong style={{color}}>{value}</strong><span>{label}</span></div>;
}

export function RuntimeChip({name, color, start = 0, active = false, className = '', style}: {name: string; color: string; start?: number; active?: boolean; className?: string; style?: React.CSSProperties}) {
  const frame = useCurrentFrame();
  const enter = springIn(frame, start, 0.82);
  const breathe = active ? 1 + Math.sin((frame - start) / 16) * 0.025 : 1;
  return <div className={`v2-runtime-chip ${className} ${active ? 'is-active' : ''}`} style={{...enter, scale: enter.scale * breathe, borderColor: `${color}99`, color, ...style}}><Dot color={color} size={7} glow={active} /> {name}</div>;
}

export function Pointer({x, y, start = 0, color = V2C.ink, clickAt}: {x: number; y: number; start?: number; color?: string; clickAt?: number}) {
  const frame = useCurrentFrame();
  const arrive = p(frame, start, start + 28);
  const click = clickAt === undefined ? 1 : 1 - beat(frame, clickAt, 10) * 0.14;
  return <svg className="v2-pointer" width="42" height="50" viewBox="0 0 42 50" style={{left: x + (1 - arrive) * 160, top: y + (1 - arrive) * 120, opacity: arrive, scale: click}}><path d="M5 3 L5 39 L15 30 L24 46 L31 42 L22 26 L36 26 Z" fill={color} stroke={color === V2C.ink ? V2C.white : V2C.black} strokeWidth="3" /></svg>;
}

export function KineticCut({frame, at, color = V2C.white}: {frame: number; at: number; color?: string}) {
  const impact = beat(frame, at, 14);
  const sweep = linear(frame, at - 4, at + 18);
  return <div className="v2-kinetic-cut" style={{opacity: impact}}><div style={{backgroundColor: color, scale: `${1 + impact * 0.16} 1`, translate: `${(sweep - 0.5) * 100}px 0px`}} /></div>;
}

export function DiegeticPill({children, color = V2C.muted, start = 0, className = ''}: {children: React.ReactNode; color?: string; start?: number; className?: string}) {
  const frame = useCurrentFrame();
  return <span className={`v2-diegetic-pill ${className}`} style={{...slideIn(frame, start, 18), borderColor: `${color}66`, color}}>{children}</span>;
}
