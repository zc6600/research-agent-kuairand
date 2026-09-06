import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, MicroLabel, Surface, Trace, V2World} from '../v2-components';
import {V2C, camera, fadeInOut, p, springIn} from '../v2-motion';

type CapabilityProps = {
  slot: 'state' | 'evidence' | 'parallel' | 'resume';
  eyebrow: string;
  title: string;
  detail: string;
  color: string;
  start: number;
};

const Capability: React.FC<CapabilityProps> = ({slot, eyebrow, title, detail, color, start}) => {
  const frame = useCurrentFrame();
  const enter = springIn(frame, start, 0.88);
  return (
    <div className={`v2-capability v2-capability-${slot}`} style={{...enter, borderColor: `${color}88`}}>
      <div className="v2-capability-eyebrow"><Dot color={color} size={8} glow /> <span>{eyebrow}</span></div>
      <strong>{title}</strong>
      <small>{detail}</small>
    </div>
  );
};

/** Product overview: introduce the durable world before showing the terminal. */
export const V2ProductMapScene: React.FC = () => {
  const frame = useCurrentFrame();
  const map = p(frame, 45, 190);
  const cameraScale = camera(frame, [0, 290, 750], [0.95, 1, 1.055]);
  return (
    <Surface tone="light">
      <AbsoluteFill className="v2-scene-root">
        <div className="v2-capability-header" style={{opacity: fadeInOut(frame, 0, 750, 22)}}>
          <MicroLabel color="#7c92a9" start={2}>THE PRODUCT / A WORLD AROUND YOUR AGENT</MicroLabel>
          <h2>Give the search<br /><span>somewhere to go.</span></h2>
          <p>SciOdyssey keeps the question, the evidence, and the next move in one durable research world.</p>
        </div>
        <div className="v2-capability-kicker" style={{opacity: p(frame, 22, 56)}}>RESEARCH AGENT / PERSISTENT CONTEXT</div>
        <svg className="v2-capability-canvas" viewBox="0 0 1920 1080" preserveAspectRatio="none" style={{scale: cameraScale}}>
          <Trace d="M960 524 C801 448 668 257 446 205" color={V2C.green} start={46} duration={100} width={2} opacity={map} />
          <Trace d="M960 524 C1135 424 1285 318 1502 292" color={V2C.blue} start={62} duration={106} width={2} opacity={map} />
          <Trace d="M960 524 C1148 595 1306 715 1506 787" color={V2C.violet} start={80} duration={110} width={2} opacity={map} />
          <Trace d="M960 524 C787 602 641 729 430 790" color={V2C.orange} start={96} duration={116} width={2} opacity={map} />
          <circle cx="960" cy="524" r={30 + p(frame, 80, 180) * 12} fill="none" stroke={V2C.green} strokeWidth="1" opacity={map * 0.32} />
          <circle cx="960" cy="524" r="7" fill={V2C.green} opacity={map} />
        </svg>
        <V2World className="v2-capability-world" size={244} start={32} color={V2C.green} label="THE RESEARCH WORLD" detail="state · evidence · next action" />
        <Capability slot="state" eyebrow="01 / STATE" title="Keep the thread." detail="What happened, what matters, what comes next." color={V2C.green} start={58} />
        <Capability slot="evidence" eyebrow="02 / EVIDENCE" title="Make claims checkable." detail="Artifacts and metrics stay attached to the move." color={V2C.blue} start={82} />
        <Capability slot="parallel" eyebrow="03 / PARALLEL" title="Open the search." detail="Explore alternatives without losing the origin." color={V2C.violet} start={106} />
        <Capability slot="resume" eyebrow="04 / RESUME" title="Return to the unfinished node." detail="The next session starts with a world already in motion." color={V2C.orange} start={130} />
        <div className="v2-capability-footer" style={{opacity: fadeInOut(frame, 260, 750, 24)}}>
          <Dot color={V2C.green} size={7} glow />
          <span>QUESTION</span><i>→</i><span>STATE</span><i>→</i><span>EVIDENCE</span><i>→</i><span>NEXT ACTION</span>
        </div>
      </AbsoluteFill>
    </Surface>
  );
};
