import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, FileToken, MicroLabel, Surface, Terminal, Trace, V2Scientist} from '../v2-components';
import {V2C, camera, p, pulse} from '../v2-motion';

export const V2FirstUseScene: React.FC = () => {
  const frame = useCurrentFrame();
  const journey = p(frame, 40, 360);
  const returnPulse = p(frame, 364, 418);
  const lens = camera(frame, [0, 70, 260, 480], [1.02, 1, 0.985, 1.015]);
  const terminalSettle = camera(frame, [0, 58, 480], [64, 0, 0]);
  const nodePulse = pulse(frame, 130, 25, 0.06);
  return (
    <Surface tone="light">
      <AbsoluteFill className="v2-scene-root">
        <div className="v2-use-copy" style={{scale: lens}}>
          <MicroLabel color={V2C.blue} start={3}>HOW TO USE / ONE COMMAND, ONE STATE</MicroLabel>
          <h2>Give it a<br /><span>bounded task.</span></h2>
          <p>Point your agent at the project. SciOdyssey turns each cycle into state, evidence, and a next action.</p>
        </div>
        <Terminal
          className="v2-use-terminal"
          title="~/research-project"
          tag="STEP 01"
          start={10}
          lines={[
            {text: '$ ./scripts/research-agent step', tone: 'blue', delay: 22},
            {text: '  --cli codex --target ./project --allow-edits', tone: 'muted', delay: 49},
            {text: '  › Scientist / bounded next move', tone: 'violet', delay: 94},
            {text: '  › META / handoff written to State', tone: 'orange', delay: 127},
            {text: '  › Runtime / evidence returned', tone: 'green', delay: 160},
          ]}
          style={{scale: camera(frame, [0, 54, 480], [0.98, 1, 1.015]), translate: `${terminalSettle}px 0px`}}
        />
        <svg className="v2-use-lines" viewBox="0 0 1920 1080" preserveAspectRatio="none">
          <Trace d="M161 602 C393 602 491 601 672 602 C870 602 987 603 1172 602 C1360 601 1461 602 1787 602" color={V2C.blue} start={40} duration={180} width={3} opacity={journey} />
          <Trace d="M161 602 C393 602 491 601 672 602 C870 602 987 603 1172 602 C1360 601 1461 602 1787 602" color={V2C.violet} start={100} duration={180} width={1} opacity={journey * 0.5} />
          <circle cx="161" cy="602" r="8" fill={V2C.blue} opacity={journey} />
          <circle cx="672" cy="602" r={10 * nodePulse} fill={V2C.violet} opacity={journey} />
          <circle cx="1172" cy="602" r={10 * nodePulse} fill={V2C.orange} opacity={journey} />
          <circle cx="1787" cy="602" r="8" fill={V2C.green} opacity={returnPulse} />
        </svg>
        <div className="v2-use-node v2-use-node-1" style={{...((frame < 66) ? {opacity: 0} : {}), scale: 0.96 + p(frame, 66, 94) * 0.04}}>
          <span className="v2-use-node-mark" style={{borderColor: V2C.violet, color: V2C.violet}}>01</span>
          <div><b style={{color: V2C.violet}}>SCIENTIST</b><strong>Bound the move</strong><small>read the task<br />propose one test</small></div>
        </div>
        <div className="v2-use-node v2-use-node-2" style={{opacity: p(frame, 126, 154), scale: 0.96 + p(frame, 126, 154) * 0.04}}>
          <span className="v2-use-node-mark" style={{borderColor: V2C.orange, color: V2C.orange}}>02</span>
          <div><b style={{color: V2C.orange}}>META</b><strong>Keep the thread</strong><small>write the brief<br />retain what matters</small></div>
        </div>
        <div className="v2-use-node v2-use-node-3" style={{opacity: p(frame, 187, 215), scale: 0.96 + p(frame, 187, 215) * 0.04}}>
          <span className="v2-use-node-mark" style={{borderColor: V2C.green, color: V2C.green}}>03</span>
          <div><b style={{color: V2C.green}}>RUNTIME</b><strong>Return evidence</strong><small>execute the code<br />measure the result</small></div>
        </div>
        <FileToken name="task.md" sub="your question" color={V2C.blue} start={42} className="v2-use-file" />
        <div className="v2-use-return" style={{opacity: p(frame, 310, 342) + returnPulse * 0.2}}><Dot color={V2C.green} size={7} glow /> <span>the world is ready for </span><b>run</b><span> · </span><b>resume</b></div>
      </AbsoluteFill>
    </Surface>
  );
};
