import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, FileToken, MicroLabel, Surface, Terminal, Trace} from '../v2-components';
import {V2C, camera, linear, p} from '../v2-motion';

export const V2LimitScene: React.FC = () => {
  const frame = useCurrentFrame();
  const hold = 1 - p(frame, 320, 480);
  const fracture = p(frame, 84, 230);
  const drift = camera(frame, [0, 230, 480], [0, 20, 150]);
  return (
    <Surface tone="dark">
      <AbsoluteFill className="v2-scene-root">
        <div className="v2-limit-session" style={{opacity: hold, translate: `${-drift}px 0px`}}>
          <MicroLabel color="#7d899c" start={0}>THE LIMIT</MicroLabel>
          <h2>When the<br /><span>prompt ends.</span></h2>
          <p>Context is still moving — code, metrics, decisions — but the session has no next handoff.</p>
        </div>
        <Terminal
          className="v2-limit-terminal"
          title="~/research-project"
          tag="SESSION ENDED"
          start={14}
          lines={[
            {text: '$ agent · final response', tone: 'blue', delay: 16},
            {text: '  › implementation written', tone: 'green', delay: 48},
            {text: '  › validation pending', tone: 'orange', delay: 80},
            {text: '  › connection closed', tone: 'muted', delay: 112},
          ]}
          style={{opacity: hold * (1 - p(frame, 206, 272)), translate: `${-drift * 0.35}px 0px`}}
        />
        <svg className="v2-limit-lines" viewBox="0 0 1920 1080" preserveAspectRatio="none">
          <Trace d="M1042 372 C1194 355 1228 320 1410 310" color={V2C.rose} start={88} duration={80} width={2} opacity={fracture * hold} dash />
          <Trace d="M1000 651 C1170 604 1200 477 1451 500" color={V2C.orange} start={116} duration={78} width={2} opacity={fracture * hold} dash />
          <Trace d="M1042 760 C1183 742 1296 817 1596 741" color={V2C.violet} start={142} duration={84} width={2} opacity={fracture * hold} dash />
          <circle cx="1042" cy="372" r="6" fill={V2C.rose} opacity={fracture * hold} />
          <circle cx="1000" cy="651" r="6" fill={V2C.orange} opacity={fracture * hold} />
          <circle cx="1042" cy="760" r="6" fill={V2C.violet} opacity={fracture * hold} />
        </svg>
        <FileToken className="v2-limit-artifact v2-limit-artifact-1" name="evaluation.json" sub="metric / waiting" color={V2C.rose} start={86} />
        <FileToken className="v2-limit-artifact v2-limit-artifact-2" name="notes.md" sub="decision / orphaned" color={V2C.orange} start={125} />
        <FileToken className="v2-limit-artifact v2-limit-artifact-3" name="next-action" sub="not assigned" color={V2C.violet} start={160} />
        <div className="v2-limit-stamp" style={{opacity: p(frame, 205, 225) * hold, scale: 0.94 + p(frame, 205, 225) * 0.06}}>NO NEXT HANDOFF</div>
        <div className="v2-limit-bottom" style={{opacity: p(frame, 225, 252) * hold}}><Dot color={V2C.rose} size={7} /> <span>the work can continue</span><b> / the context cannot</b></div>
        <div className="v2-limit-wash" style={{opacity: p(frame, 337, 479)}} />
      </AbsoluteFill>
    </Surface>
  );
};
