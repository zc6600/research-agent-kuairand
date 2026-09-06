import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {AgentJourney} from '../../keynote/scenes/AgentJourney';
import {EvidenceJourney} from '../../keynote/scenes/EvidenceJourney';
import {HumanJourney} from '../../keynote/scenes/HumanJourney';
import {WindowBar as KeynoteWindowBar} from '../../keynote/components';
import '../../keynote/keynote.css';
import {MicroLabel, Surface, Trace} from '../v2-components';
import {V2C, camera, fadeInOut, p} from '../v2-motion';

export const V2KeynoteCutScene: React.FC = () => {
  const frame = useCurrentFrame();
  const stageOpacity = fadeInOut(frame, 0, 840, 22);
  const stageScale = camera(frame, [0, 160, 310, 475, 625, 840], [1.16, 1.08, 1.02, 1.12, 0.98, 1.22]);
  const stageWidth = camera(frame, [0, 260, 475, 625, 840], [1580, 1680, 1490, 1710, 1240]);
  const stageHeight = camera(frame, [0, 260, 475, 625, 840], [620, 650, 628, 690, 510]);
  const stageTop = camera(frame, [0, 260, 475, 625, 840], [282, 239, 264, 214, 336]);
  const stageLeft = camera(frame, [0, 310, 625, 840], [170, 120, 105, 360]);
  const windowFrame = frame < 330 ? 1120 : frame < 570 ? 1500 : 1720;
  return (
    <Surface tone="light">
      <AbsoluteFill className="v2-scene-root">
        <div className="v2-keynote-caption" style={{opacity: fadeInOut(frame, 20, 810, 26), translate: `${p(frame, 20, 44) * -15}px 0px`}}>
          <MicroLabel color="#7e8b9d" start={0}>THE IDEA IN MOTION</MicroLabel>
          <strong>One question.<br /><span>A living trajectory.</span></strong>
        </div>
        <div className="v2-keynote-root kn-root" style={{opacity: stageOpacity}}>
          <div className="kn-stage v2-keynote-stage" style={{left: stageLeft, top: stageTop, width: stageWidth, height: stageHeight, scale: stageScale, rotate: '0deg', boxShadow: `0 ${28 + (stageScale - 1) * 55}px ${92 + (stageScale - 1) * 105}px rgba(0,0,0,.27)`}}>
            <KeynoteWindowBar frame={windowFrame} />
            <div className="kn-stage-body">
              <div style={{opacity: fadeInOut(frame, 0, 350, 24)}}><EvidenceJourney frame={frame + 1080} /></div>
              <div style={{opacity: fadeInOut(frame, 310, 570, 24)}}><HumanJourney frame={frame + 1095} /></div>
              <div style={{opacity: fadeInOut(frame, 530, 840, 24)}}><AgentJourney frame={frame + 1135} /></div>
              <div style={{opacity: fadeInOut(frame, 592, 840, 24)}}><AgentJourney frame={frame + 1040} /></div>
            </div>
          </div>
        </div>
        <svg className="v2-keynote-signal" viewBox="0 0 1920 1080" preserveAspectRatio="none">
          <Trace d="M48 919 C337 919 491 891 717 842 C1022 775 1188 846 1404 747 C1598 658 1649 562 1900 557" color={V2C.cyan} start={670} duration={110} width={2} opacity={0.64} />
        </svg>
        <div className="v2-keynote-bottom" style={{opacity: fadeInOut(frame, 740, 840, 28)}}><span>THE WINDOW CLOSES</span><b> / THE WORLD STAYS</b></div>
      </AbsoluteFill>
    </Surface>
  );
};
