import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, MicroLabel, Surface, Terminal, Trace, TraceDot} from '../v2-components';
import {V2C, camera, linear, p, pulse} from '../v2-motion';

export const V2ColdOpenScene: React.FC = () => {
  const frame = useCurrentFrame();
  const question = p(frame, 2, 24);
  const path = p(frame, 48, 182);
  const stop = 1 - p(frame, 356, 385);
  const cameraScale = camera(frame, [0, 120, 310, 480], [1, 1.02, 1.04, 1.13]);
  const node = linear(frame, 58, 194);
  const nodeX = 140 + node * 1260;
  const nodeY = 755 - Math.sin(node * Math.PI) * 340;
  return (
    <Surface tone="dark">
      <AbsoluteFill className="v2-scene-root">
      <div className="v2-cold-question" style={{opacity: question * stop, translate: `0px ${(1 - question) * 28}px`}}>
        <MicroLabel color="#718198" start={0}>A QUESTION ENTERS</MicroLabel>
        <h1><span>CAN A</span><br />QUESTION<br /><span>KEEP GOING?</span></h1>
        <p>The prompt is only the first move.<br />The search is everything after it.</p>
      </div>
      <div className="v2-cold-micro" style={{opacity: p(frame, 44, 68) * stop}}>
        <Dot color={V2C.cyan} size={7} glow /> <span>NO TITLE / NO DECK / JUST THE QUESTION</span>
      </div>
      <svg className="v2-cold-path" viewBox="0 0 1920 1080" preserveAspectRatio="none" style={{scale: cameraScale}}>
        <Trace d="M138 764 C360 742 467 529 716 498 C930 471 1008 659 1211 562 C1392 475 1430 310 1763 274" color={V2C.blue} start={48} duration={142} width={4} opacity={0.9} />
        <Trace d="M138 764 C360 742 467 529 716 498 C930 471 1008 659 1211 562 C1392 475 1430 310 1763 274" color={V2C.cyan} start={48} duration={142} width={1} opacity={0.72} />
        <Trace d="M144 798 C392 798 551 671 754 652 C1004 628 1157 808 1330 670 C1505 531 1546 431 1785 421" color={V2C.violet} start={72} duration={168} width={1.5} opacity={0.45} />
        <circle cx={nodeX} cy={nodeY} r={10 + pulse(frame, 60, 17, 0.25)} fill={V2C.cyan} opacity={path * stop} />
        <circle cx={nodeX} cy={nodeY} r="23" fill="none" stroke={V2C.cyan} strokeWidth="1" opacity={path * stop * 0.35} />
        <TraceDot x={1763} y={274} color={V2C.orange} start={180} duration={26} r={6} />
      </svg>
      <Terminal
        className="v2-cold-terminal"
        title="~/research-project"
        tag="RUNNING"
        start={35}
        lines={[
          {text: '$ ./scripts/research-agent step', tone: 'blue', delay: 20},
          {text: '  --cli codex --target ./project --allow-edits', tone: 'muted', delay: 42},
          {text: '  › cycle 01 / reading task.md', tone: 'plain', delay: 72},
          {text: '  › awaiting next action', tone: 'orange', delay: 104},
        ]}
        style={{scale: camera(frame, [0, 130, 330, 480], [0.86, 0.96, 1.02, 1.18]), translate: `${camera(frame, [0, 480], [0, -175])}px ${camera(frame, [0, 480], [30, -62])}px`, opacity: stop}}
      />
      <div className="v2-cold-readout" style={{opacity: p(frame, 198, 224) * stop}}>
        <span>cycle 01</span><b> / awaiting next action</b>
      </div>
      </AbsoluteFill>
    </Surface>
  );
};
