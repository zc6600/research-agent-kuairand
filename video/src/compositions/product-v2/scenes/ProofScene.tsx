import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, MetricToken, MicroLabel, ScreenPlane, Surface, Trace} from '../v2-components';
import {V2C, camera, fadeInOut, p} from '../v2-motion';

export const V2ProofScene: React.FC = () => {
  const frame = useCurrentFrame();
  const proof = p(frame, 14, 66);
  const score = p(frame, 112, 188);
  const chart = p(frame, 195, 310);
  const cameraScale = camera(frame, [0, 180, 480, 720], [1, 1.05, 1.02, 1.12]);
  return (
    <Surface tone="light">
      <AbsoluteFill className="v2-scene-root">
        <div className="v2-proof-copy" style={{opacity: fadeInOut(frame, 0, 720, 26)}}>
          <MicroLabel color={V2C.green} start={4}>PROOF / WHAT SURVIVES</MicroLabel>
          <h2>From open<br /><span>search to proof.</span></h2>
          <p>Every claim points back to an artifact, a metric, and the implementation that produced it.</p>
        </div>
        <ScreenPlane className="v2-proof-screen" src="assets/dashboard-overview.png" title="Research Dashboard" tag="LIVE STATE" color={V2C.green} start={22} style={{scale: cameraScale, translate: `${camera(frame, [0, 720], [20, -50])}px ${camera(frame, [0, 720], [10, -12])}px`}} />
        <ScreenPlane className="v2-proof-screen-2" src="assets/token-score-comparison.png" title="Validation / score trace" tag="PUBLIC" color={V2C.blue} start={185} objectPosition="center center" />
        <div className="v2-proof-score" style={{opacity: score, scale: .9 + score * .1}}>
          <span>PRIMARY</span>
          <strong>0.6059363</strong>
          <small>+0.0043363 vs official reference</small>
        </div>
        <svg className="v2-proof-line" viewBox="0 0 1920 1080" preserveAspectRatio="none">
          <Trace d="M690 840 C930 798 980 739 1160 728 C1334 717 1457 770 1766 622" color={V2C.green} start={118} duration={150} width={3} opacity={chart} />
          <Trace d="M690 840 C930 798 980 739 1160 728 C1334 717 1457 770 1766 622" color={V2C.blue} start={150} duration={130} width={1} opacity={chart * .55} />
          <circle cx="1766" cy="622" r="7" fill={V2C.green} opacity={chart} />
        </svg>
        <MetricToken className="v2-proof-metric-1" value="4" label="autonomous cycles" color={V2C.blue} start={220} />
        <MetricToken className="v2-proof-metric-2" value="13" label="named experiments" color={V2C.orange} start={238} />
        <MetricToken className="v2-proof-metric-3" value="0" label="GPU-hours" color={V2C.violet} start={256} />
        <div className="v2-proof-callout" style={{opacity: p(frame, 288, 328)}}><Dot color={V2C.green} size={7} glow /> <span>public validation · unchanged checker · retained implementation</span></div>
        <div className="v2-proof-footer" style={{opacity: proof}}><span>KuaiRand-Pure</span><i> / </i><span>evidence, not promises</span></div>
      </AbsoluteFill>
    </Surface>
  );
};
