import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {ResearchWorldGlyph, ScientistGlyph} from '../launch/SciOdysseyFilm';
import {COLORS, draw, progress, reveal, scaleIn} from './motion';

export function ProductFrame({
  chapter,
  accent = COLORS.blue,
  children,
  mode = 'light',
}: {
  chapter: string;
  accent?: string;
  children: React.ReactNode;
  mode?: 'light' | 'dark';
}) {
  const frame = useCurrentFrame();
  const chrome = progress(frame, 0, 22);
  return (
    <AbsoluteFill className={`product-frame product-frame-${mode}`}>
      <div className="product-grid" />
      <div className="product-chrome product-chrome-top" style={{opacity: chrome}}>
        <span><i className="product-brand-dot" style={{backgroundColor: accent}} /> SCIODYSSEY <b>/</b> RESEARCH AGENT</span>
        <span className="product-chrome-chapter">{chapter}</span>
      </div>
      <div className="product-chrome-line" style={{backgroundColor: accent, transform: `scaleX(${progress(frame, 0, 100)})`}} />
      <div className="product-chrome product-chrome-bottom" style={{opacity: chrome}}>
        <span>OPEN-WORLD ML RESEARCH</span>
        <span>THE EXPERIENCE PERSISTS</span>
      </div>
      <div className="product-corner product-corner-tl" style={{borderColor: `${accent}66`}} />
      <div className="product-corner product-corner-br" style={{borderColor: `${accent}66`}} />
      {children}
    </AbsoluteFill>
  );
}

export function Kicker({children, color = COLORS.muted}: {children: React.ReactNode; color?: string}) {
  return <div className="product-kicker" style={{color}}>{children}</div>;
}

export function Hero({children, className = '', style}: {children: React.ReactNode; className?: string; style?: React.CSSProperties}) {
  const frame = useCurrentFrame();
  return <div className={`product-hero ${className}`} style={{...reveal(frame, 16, 28, 32), ...style}}>{children}</div>;
}

export function Caption({children, className = '', style}: {children: React.ReactNode; className?: string; style?: React.CSSProperties}) {
  const frame = useCurrentFrame();
  return <p className={`product-caption ${className}`} style={{...reveal(frame, 70, 24, 16), ...style}}>{children}</p>;
}

export function DrawnPath({d, color, start = 0, duration = 70, width = 2, opacity = 1}: {d: string; color: string; start?: number; duration?: number; width?: number; opacity?: number}) {
  const frame = useCurrentFrame();
  return <path d={d} fill="none" stroke={color} strokeWidth={width} pathLength="1" strokeDasharray="1" strokeDashoffset={1 - draw(frame, start, duration)} opacity={opacity} vectorEffect="non-scaling-stroke" />;
}

export function Dot({color, size = 8, style}: {color: string; size?: number; style?: React.CSSProperties}) {
  return <span className="product-dot" style={{width: size, height: size, backgroundColor: color, ...style}} />;
}

export function World({size = 190, color = COLORS.green, start = 0, label, detail}: {size?: number; color?: string; start?: number; label?: string; detail?: string}) {
  const frame = useCurrentFrame();
  const pulse = 1 + Math.sin((frame - start) / 26) * 0.018;
  const entrance = scaleIn(frame, start);
  return (
    <div className="product-world-wrap" style={{width: size, height: size, opacity: entrance.opacity, transform: `${entrance.transform} scale(${pulse})`}}>
      <div className="product-world-halo" style={{borderColor: `${color}35`}} />
      <ResearchWorldGlyph large />
      {label ? <strong style={{color}}>{label}</strong> : null}
      {detail ? <small>{detail}</small> : null}
    </div>
  );
}

export function Scientist({size = 150, color = COLORS.purple, start = 0, label, detail}: {size?: number; color?: string; start?: number; label?: string; detail?: string}) {
  const frame = useCurrentFrame();
  return (
    <div className="product-scientist-wrap" style={{width: size, ...scaleIn(frame, start)}}>
      <ScientistGlyph color={color} />
      {label ? <strong style={{color}}>{label}</strong> : null}
      {detail ? <small>{detail}</small> : null}
    </div>
  );
}

export function ProductLogo({accent = COLORS.blue, inverse = false}: {accent?: string; inverse?: boolean}) {
  return <div className={`product-logo ${inverse ? 'product-logo-inverse' : ''}`}><Dot color={accent} size={8} /> <span>SCIODYSSEY</span></div>;
}

export function WindowBar({title, tag, color = COLORS.blue}: {title: string; tag?: string; color?: string}) {
  return (
    <div className="product-window-bar">
      <span className="product-window-dots"><i /><i /><i /></span>
      <span className="product-window-title">{title}</span>
      {tag ? <span className="product-window-tag" style={{color}}>{tag}</span> : null}
    </div>
  );
}

export function TerminalCard({
  title = '~/project · terminal',
  lines,
  color = COLORS.blue,
  start = 0,
  className = '',
}: {
  title?: string;
  lines: Array<{text: string; tone?: 'normal' | 'accent' | 'success' | 'muted'; delay?: number}>;
  color?: string;
  start?: number;
  className?: string;
}) {
  const frame = useCurrentFrame();
  return (
    <div className={`product-terminal-card ${className}`} style={scaleIn(frame, start)}>
      <WindowBar title={title} tag="LIVE" color={color} />
      <div className="product-terminal-body">
        {lines.map((line, index) => {
          const p = progress(frame, start + (line.delay ?? index * 14), start + (line.delay ?? index * 14) + 20);
          return <div key={`${line.text}-${index}`} className={`product-terminal-line product-terminal-${line.tone ?? 'normal'}`} style={{opacity: p, transform: `translateX(${(1 - p) * 18}px)`}}><span className="product-terminal-caret">{index === 0 ? '›' : ' '}</span>{line.text}</div>;
        })}
      </div>
    </div>
  );
}

export function ProductScreenshot({src, className = '', title = 'Research Agent Dashboard', tag = 'READ-ONLY', start = 0, color = COLORS.green, objectPosition = 'center top'}: {src: string; className?: string; title?: string; tag?: string; start?: number; color?: string; objectPosition?: string}) {
  const frame = useCurrentFrame();
  return (
    <div className={`product-screenshot ${className}`} style={scaleIn(frame, start)}>
      <WindowBar title={title} tag={tag} color={color} />
      <Img src={staticFile(src)} style={{width: '100%', height: 'calc(100% - 48px)', objectFit: 'cover', objectPosition}} />
    </div>
  );
}

export function FeatureCard({number, title, detail, color, start = 0, active = false, className = ''}: {number: string; title: string; detail: string; color: string; start?: number; active?: boolean; className?: string}) {
  const frame = useCurrentFrame();
  const p = progress(frame, start, start + 24);
  return (
    <div className={`product-feature-card ${active ? 'is-active' : ''} ${className}`} style={{opacity: p, transform: `translate3d(${(1 - p) * 26}px, 0, 0)`, borderColor: `${color}77`}}>
      <span className="product-feature-number" style={{color}}>{number}</span>
      <div><strong>{title}</strong><small>{detail}</small></div>
    </div>
  );
}

export function MiniPill({children, color = COLORS.blue, start = 0}: {children: React.ReactNode; color?: string; start?: number}) {
  const frame = useCurrentFrame();
  return <span className="product-mini-pill" style={{...scaleIn(frame, start, 0.86), color, borderColor: `${color}66`}}>{children}</span>;
}

export function Metric({value, label, detail, color = COLORS.blue, start = 0, className = ''}: {value: string; label: string; detail?: string; color?: string; start?: number; className?: string}) {
  const frame = useCurrentFrame();
  return <div className={`product-metric ${className}`} style={reveal(frame, start, 24, 14)}><span className="product-metric-label" style={{color}}>{label}</span><strong style={{color}}>{value}</strong>{detail ? <small>{detail}</small> : null}</div>;
}

export function Rule({color = COLORS.line, start = 0, style}: {color?: string; start?: number; style?: React.CSSProperties}) {
  const frame = useCurrentFrame();
  return <div className="product-rule" style={{backgroundColor: color, transform: `scaleX(${progress(frame, start, start + 30)})`, ...style}} />;
}

export function ImagePlate({src, className = '', style, start = 0, objectPosition = 'center'}: {src: string; className?: string; style?: React.CSSProperties; start?: number; objectPosition?: string}) {
  const frame = useCurrentFrame();
  return <div className={`product-image-plate ${className}`} style={{...scaleIn(frame, start), ...style}}><Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition}} /></div>;
}

export function FilmImage({src, className = '', start = 0}: {src: string; className?: string; start?: number}) {
  const frame = useCurrentFrame();
  return <Img src={staticFile(src)} className={`product-film-image ${className}`} style={{opacity: progress(frame, start, start + 40)}} />;
}
