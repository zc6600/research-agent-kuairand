import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, FileToken, MicroLabel, Surface, Trace, V2World} from '../v2-components';
import {V2C, camera, p} from '../v2-motion';

export const V2RevealScene: React.FC = () => {
  const frame = useCurrentFrame();
  const name = p(frame, 12, 64);
  const line = p(frame, 34, 154);
  const cameraScale = camera(frame, [0, 160, 420], [1.04, 1, 1.08]);
  return (
    <Surface tone="light">
      <AbsoluteFill className="v2-scene-root">
        <div className="v2-reveal-copy" style={{opacity: name, translate: `${(1 - name) * -34}px 0px`}}>
          <MicroLabel color={V2C.deepBlue} start={4}>A PERSISTENT WORLD FOR OPEN RESEARCH</MicroLabel>
          <h1><span>SCI</span>ODYSSEY</h1>
          <div className="v2-reveal-tagline">The research layer<br />around your agent.</div>
        </div>
        <svg className="v2-reveal-path" viewBox="0 0 1920 1080" preserveAspectRatio="none" style={{scale: cameraScale}}>
          <Trace d="M80 832 C330 808 487 734 682 602 C888 462 1062 493 1247 407 C1439 319 1521 372 1808 286" color={V2C.blue} start={34} duration={120} width={3} opacity={line} />
          <Trace d="M60 877 C358 881 518 790 759 751 C1021 708 1220 789 1392 657 C1530 551 1604 537 1810 542" color={V2C.violet} start={52} duration={125} width={1.5} opacity={line * 0.48} />
          <Trace d="M118 793 C362 729 482 499 728 475 C1000 449 1107 589 1314 487 C1498 398 1585 246 1802 252" color={V2C.orange} start={72} duration={112} width={1.5} opacity={line * 0.48} />
          <circle cx="1810" cy="286" r="8" fill={V2C.green} opacity={line} />
        </svg>
        <V2World className="v2-reveal-world" size={302} start={36} color={V2C.green} label="THE RESEARCH WORLD" detail="state · evidence · next action" />
        <FileToken className="v2-reveal-artifact-1" name="STATE.yaml" sub="what survives" color={V2C.green} start={80} />
        <FileToken className="v2-reveal-artifact-2" name="evidence/" sub="what can be checked" color={V2C.blue} start={102} />
        <div className="v2-reveal-bottom" style={{opacity: p(frame, 108, 138)}}><Dot color={V2C.green} size={7} glow /> <span>SCIODYSSEY / RESEARCH AGENT</span><i>·</i><span>THE SEARCH CONTINUES</span></div>
      </AbsoluteFill>
    </Surface>
  );
};
