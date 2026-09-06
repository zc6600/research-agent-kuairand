import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, MicroLabel, Surface, Trace, V2World} from '../v2-components';
import {V2C, fadeInOut, p, springIn} from '../v2-motion';

const Branch: React.FC<{label: string; id: string; color: string; start: number; selected?: boolean}> = ({label, id, color, start, selected = false}) => {
  const frame = useCurrentFrame();
  const enter = springIn(frame, start, 0.86);
  const selectedScale = selected ? 1 + Math.sin((frame - start) / 15) * 0.018 : 1;
  return (
    <div className={`v2-branch v2-branch-${id.slice(-1)}`} style={{...enter, scale: enter.scale * selectedScale, borderColor: `${color}bb`, boxShadow: selected ? `0 0 0 5px ${color}18, 0 22px 48px ${color}22` : undefined}}>
      <Dot color={color} size={10} glow={selected} />
      <strong>{label}</strong>
      <span style={{color}}>{id}</span>
      <small>{selected ? 'selected / retain' : 'isolated / inspect'}</small>
    </div>
  );
};

export const V2ParallelScene: React.FC = () => {
  const frame = useCurrentFrame();
  const split = p(frame, 26, 108);
  const review = p(frame, 300, 394);
  const promote = p(frame, 474, 535);
  const selected = promote;
  return (
    <Surface tone="light">
      <AbsoluteFill className="v2-scene-root">
        <div className="v2-parallel-copy" style={{opacity: fadeInOut(frame, 0, 540, 26)}}>
          <MicroLabel color={V2C.orange} start={3}>BREADTH / AFTER THE FIRST PATH</MicroLabel>
          <h2>Open the<br /><span>search.</span></h2>
          <p>When one trajectory reaches a decision, explore the alternatives without losing the world that produced them.</p>
        </div>
        <svg className="v2-parallel-canvas" viewBox="0 0 1920 1080" preserveAspectRatio="none">
          <Trace d="M840 520 C1010 520 1106 292 1350 292" color={V2C.blue} start={26} duration={120} width={3} opacity={split} />
          <Trace d="M840 520 C1010 520 1114 447 1399 447" color={V2C.violet} start={38} duration={130} width={3} opacity={split} />
          <Trace d="M840 520 C1010 520 1106 602 1350 602" color={V2C.orange} start={50} duration={142} width={3} opacity={split} />
          <Trace d="M1350 292 C1510 292 1580 520 1724 520" color={V2C.blue} start={294} duration={96} width={2} opacity={review} />
          <Trace d="M1399 447 C1531 447 1590 520 1724 520" color={V2C.violet} start={310} duration={96} width={2} opacity={review} />
          <Trace d="M1350 602 C1510 602 1590 520 1724 520" color={V2C.orange} start={326} duration={96} width={2} opacity={review} />
          <circle cx="840" cy="520" r="14" fill={V2C.green} opacity={split} />
          <circle cx="1724" cy="520" r={16 + review * 10} fill="none" stroke={V2C.green} strokeWidth="2" opacity={review * 0.55} />
          <circle cx="1724" cy="520" r="8" fill={V2C.green} opacity={review} />
        </svg>
        <V2World className="v2-parallel-origin" size={150} start={8} color={V2C.green} />
        <Branch label="Scientist A" id="r1b1" color={V2C.blue} start={66} />
        <Branch label="Scientist B" id="r1b2" color={V2C.violet} start={80} selected={selected > 0.5} />
        <Branch label="Scientist C" id="r1b3" color={V2C.orange} start={94} />
        <div className="v2-parallel-review" style={{opacity: review, scale: .94 + review * .06}}><Dot color={V2C.green} size={7} glow /> <b>POST-HOC REVIEW</b><span> / compare the worlds</span></div>
        <div className="v2-parallel-command" style={{opacity: promote, translate: `0px ${(1 - promote) * 16}px`}}><span>$ ./scripts/research-agent </span><b>parallel-promote</b><span> --branch r1b2</span></div>
        <div className="v2-parallel-bottom" style={{opacity: p(frame, 475, 510)}}><Dot color={V2C.violet} size={7} /> nothing merges itself</div>
      </AbsoluteFill>
    </Surface>
  );
};
