import React from 'react';
import {spring} from 'remotion';
import {blue, linear, progress, visible} from './motion';

export function Typed({text, frame, start, duration = 54}: {text: string; frame: number; start: number; duration?: number}) {
  const count = Math.floor(linear(frame, start, start + duration) * text.length);
  return <><span>{text.slice(0, count)}</span><span className="kn-caret" style={{opacity: frame < start + duration + 24 ? 1 : 0}} /></>;
}

export function Headline({frame, start, end, children}: {frame: number; start: number; end: number; children: React.ReactNode}) {
  return <div className="kn-headline" style={{opacity: visible(frame, start, end, 22), translate: `0 ${(1 - progress(frame, start, start + 38)) * 28}px`}}>{children}</div>;
}

export function Detail({children, style}: {children: React.ReactNode; style?: React.CSSProperties}) {
  return <div className="kn-detail" style={style}>{children}</div>;
}

export function WindowBar({frame}: {frame: number}) {
  const dashboard = visible(frame, 1070, 1410, 40);
  const agent = progress(frame, 1665, 1695);
  const terminal = Math.max(0, 1 - dashboard - agent);
  const slide = 220;
  const mode = frame < 1090 ? '~/sci-odyssey' : frame < 1410 ? 'READ ONLY' : frame < 1665 ? '~/sci-odyssey' : 'SKILL WORKFLOW';
  return <div className="kn-windowbar">
    <div className="kn-windowdots"><i /><i /><i /></div>
    <span className="kn-windowtitle" style={{opacity: terminal, transform: `translateX(${-slide * (dashboard + agent)}px)`}}>Terminal — research-agent</span>
    <span className="kn-windowtitle" style={{opacity: dashboard, transform: `translateX(${slide * (1 - dashboard)}px)`}}>Research Dashboard</span>
    <span className="kn-windowtitle" style={{opacity: agent, transform: `translateX(${slide * (1 - agent)}px)`}}>Coding agent</span>
    <span className="kn-windowmode">{mode}</span>
  </div>;
}

export function Command({frame, start, verb, options, fontSize = 42}: {frame: number; start: number; verb: string; options: string[]; fontSize?: number}) {
  return <div className="kn-command" style={{opacity: progress(frame, start, start + 14)}}>
    <div style={{fontSize}}><span className="kn-dollar">$ </span><span>./scripts/research-agent </span><span style={{color: blue}}><Typed text={verb} frame={frame} start={start + 12} duration={24} /></span><span style={{opacity: progress(frame, start + 32, start + 54), color: '#a3a6ac'}}>{' \\'}</span></div>
    <div className="kn-options" style={{opacity: progress(frame, start + 32, start + 54)}}>{options.map((option, index) => <div key={option}>{index === 0 ? '  ' : '  '}{option}{index < options.length - 1 ? ' \\' : ''}</div>)}</div>
  </div>;
}

export function Cursor({frame, start, x, y}: {frame: number; start: number; x: number; y: number}) {
  const p = progress(frame, start, start + 50);
  const press = spring({frame: frame - start - 58, fps: 30, config: {damping: 22, stiffness: 160}});
  return <svg viewBox="0 0 42 48" width="42" height="48" className="kn-pointer" style={{left: x + (1 - p) * 160, top: y + (1 - p) * 120, opacity: progress(frame, start, start + 12), scale: frame < start + 58 ? 1 : 0.86 + press * 0.14}}><path d="M5 3 L5 36 L14 28 L22 44 L29 41 L21 25 L34 25 Z" fill="#111217" stroke="white" strokeWidth="3" /></svg>;
}
