import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, MicroLabel, RuntimeChip, Surface, Trace, V2World} from '../v2-components';
import {V2C, fadeInOut, p, pulse} from '../v2-motion';

export const V2RuntimeScene: React.FC = () => {
  const frame = useCurrentFrame();
  const right = p(frame, 18, 75);
  const compare = p(frame, 80, 148);
  const swap = p(frame, 164, 268);
  const active = Math.min(3, Math.floor(Math.max(0, frame - 174) / 32));
  const worldPulse = pulse(frame, 150, 23, 0.025);
  return (
    <Surface tone="light">
      <AbsoluteFill className="v2-scene-root">
        <div className="v2-runtime-title" style={{opacity: fadeInOut(frame, 0, 540, 26)}}>
          <MicroLabel color={V2C.deepBlue} start={3}>THE RUNTIME / KEEP YOUR AGENT</MicroLabel>
          <h2>Use the agent<br /><span>you trust.</span></h2>
          <p>Different runtimes. One durable research world.</p>
        </div>
        <div className="v2-runtime-left" style={{opacity: compare, translate: `${(1 - compare) * -90}px 0px`, scale: .98 + compare * .02}}>
          <h3>DIRECT SESSION</h3>
          <div className="v2-runtime-sequence"><span>PROMPT</span> → ANSWER → CLOSE</div>
          <div className="v2-runtime-tail">context ends with the window</div>
        </div>
        <div className="v2-runtime-right" style={{opacity: right, translate: `${(1 - right) * 120}px 0px`, scale: .92 + right * .08}}>
          <h3>SCIODYSSEY ON TOP</h3>
          <div className="v2-runtime-sequence"><span>QUESTION</span> → CYCLE → STATE<br /><span>REVIEW</span> → RESUME</div>
          <div className="v2-runtime-right-rule" style={{scale: `${right} 1`}} />
          <div className="v2-runtime-right-foot"><Dot color={V2C.green} size={7} glow /> the world persists</div>
        </div>
        <svg className="v2-runtime-links" viewBox="0 0 1920 1080" preserveAspectRatio="none">
          <Trace d="M1441 316 C1300 380 1240 427 1174 484" color={V2C.blue} start={70} duration={70} width={1.5} opacity={right * .42} dash />
          <Trace d="M1600 350 C1451 389 1275 448 1174 484" color={V2C.violet} start={100} duration={70} width={1.5} opacity={right * .42} dash />
          <Trace d="M1430 736 C1320 665 1260 577 1174 484" color={V2C.orange} start={150} duration={70} width={1.5} opacity={right * .42} dash />
          <circle cx="1174" cy="484" r={18 * worldPulse} fill="none" stroke={V2C.green} opacity={right * .7} />
        </svg>
        <V2World className="v2-runtime-world" size={146} start={88} color={V2C.green} />
        <RuntimeChip className="v2-runtime-chip-1" name="Codex" color={V2C.blue} start={82} active={active === 0} />
        <RuntimeChip className="v2-runtime-chip-2" name="Claude Code" color={V2C.violet} start={112} active={active === 1} />
        <RuntimeChip className="v2-runtime-chip-3" name="Gemini CLI" color={V2C.orange} start={142} active={active === 2} />
        <RuntimeChip className="v2-runtime-chip-4" name="AGY" color={V2C.green} start={172} active={active === 3} />
        <div className="v2-runtime-caption" style={{opacity: swap}}><span>WORKFLOW COMPARISON</span><b> / NOT A MODEL LEADERBOARD</b></div>
        <div className="v2-runtime-bottom" style={{opacity: p(frame, 275, 314)}}><Dot color={V2C.green} size={7} glow /> <span>THE RUNTIME CAN CHANGE.</span><strong>THE WORLD DOES NOT.</strong></div>
      </AbsoluteFill>
    </Surface>
  );
};
