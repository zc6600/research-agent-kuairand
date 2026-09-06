import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, MicroLabel, Surface, Trace, V2World} from '../v2-components';
import {V2C, camera, p, pulse} from '../v2-motion';

export const V2FinalScene: React.FC = () => {
  const frame = useCurrentFrame();
  const reveal = p(frame, 0, 58);
  // Hold the end card through the final frame so the product promise lands cleanly.
  const final = p(frame, 0, 18);
  const line = p(frame, 42, 151);
  const cameraScale = camera(frame, [0, 150, 210], [1, 1.04, 1.08]);
  return (
    <Surface tone="light">
      <AbsoluteFill className="v2-scene-root">
        <svg className="v2-final-path" viewBox="0 0 1920 1080" preserveAspectRatio="none" style={{scale: cameraScale}}>
          <Trace d="M48 865 C332 857 468 716 688 634 C902 554 1088 616 1258 493 C1423 373 1511 267 1880 229" color={V2C.blue} start={34} duration={124} width={4} opacity={line} />
          <Trace d="M52 906 C353 905 530 843 763 804 C1005 762 1187 868 1393 696 C1556 560 1631 448 1884 448" color={V2C.violet} start={55} duration={124} width={1.5} opacity={line * .5} />
          <Trace d="M72 832 C309 773 492 484 721 466 C983 446 1112 610 1321 485 C1506 374 1611 210 1880 205" color={V2C.orange} start={78} duration={113} width={1.5} opacity={line * .5} />
          <circle cx="1880" cy="229" r={9 * pulse(frame, 120, 16, .35)} fill={V2C.green} opacity={line} />
        </svg>
        <div className="v2-final-copy" style={{opacity: final, translate: `${(1 - reveal) * -30}px 0px`}}>
          <MicroLabel color="#8494aa" start={2}>THE SEARCH CONTINUES</MicroLabel>
          <h1>Start with a<br /><span>question.</span></h1>
        </div>
        <V2World className="v2-final-world" size={322} start={34} color={V2C.green} />
        <div className="v2-final-command" style={{opacity: p(frame, 91, 127)}}><span>$ ./scripts/research-agent </span><b>step</b><span> --cli codex --target ./project</span></div>
        <div className="v2-final-mark" style={{opacity: p(frame, 120, 151)}}><Dot color={V2C.green} size={8} glow /> <span>SCIODYSSEY</span></div>
      </AbsoluteFill>
    </Surface>
  );
};
