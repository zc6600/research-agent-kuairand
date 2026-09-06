import React from 'react';
import {useCurrentFrame} from 'remotion';
import {AgentJourney} from '../../keynote/scenes/AgentJourney';
import {EvidenceJourney} from '../../keynote/scenes/EvidenceJourney';
import {HumanJourney} from '../../keynote/scenes/HumanJourney';
import {TerminalJourney} from '../../keynote/scenes/TerminalJourney';
import {WindowBar as KeynoteWindowBar} from '../../keynote/components';
import '../../keynote/keynote.css';
import {COLORS, camera, progress, reveal, visible} from '../motion';
import {Kicker, ProductFrame} from '../components';

/**
 * A short, real cut from the keynote film. The existing journey scenes are
 * deliberately reused here so the product film and keynote share one visual
 * language rather than becoming two unrelated demos.
 */
export const ProductKeynoteScene: React.FC = () => {
  const frame = useCurrentFrame();
  const oldFrame = frame + 130;
  const stageScale = camera(frame, [0, 90, 260, 410, 550, 700, 850], [1.03, 1.03, 0.98, 0.92, 1.06, 1.18, 1.02]);
  const stageWidth = camera(frame, [0, 260, 410, 550, 700], [1370, 1370, 1500, 1420, 1320]);
  const stageHeight = camera(frame, [0, 260, 410, 550, 700], [500, 500, 630, 610, 560]);
  const stageTop = camera(frame, [0, 260, 410, 550, 700], [330, 330, 255, 265, 300]);
  const windowFrame = frame < 390 ? 200 : frame < 530 ? 1150 : frame < 620 ? 1500 : 1720;
  const stageOpacity = progress(frame, 0, 22) * (1 - progress(frame, 845, 900));
  return (
    <ProductFrame chapter="05 / THE KEYNOTE CUT" accent={COLORS.purple}>
      <div className="product-keynote-copy" style={{...reveal(frame, 12, 24, 20), opacity: progress(frame, 12, 36) * (1 - progress(frame, 800, 860))}}>
        <Kicker color={COLORS.purple}>THE IDEA IN MOTION</Kicker>
        <h2>Same world.<br /><span>New trajectory.</span></h2>
        <p>Watch one question become a bounded cycle,<br />a parallel search, and a human decision.</p>
      </div>
      <div className="product-keynote-label" style={{opacity: progress(frame, 50, 90) * (1 - progress(frame, 820, 870))}}>previous keynote / excerpt</div>
      <div className="product-keynote-root kn-root" style={{opacity: stageOpacity}}>
        <div className="kn-stage product-keynote-stage" style={{left: (1920 - stageWidth) / 2, top: stageTop, width: stageWidth, height: stageHeight, scale: stageScale, boxShadow: `0 ${22 + (stageScale - 1) * 70}px ${70 + (stageScale - 1) * 95}px rgba(22,34,48,.11), 0 3px 9px rgba(22,34,48,.03)`}}>
          <KeynoteWindowBar frame={windowFrame} />
          <div className="kn-stage-body">
            <div style={{opacity: visible(frame, 0, 430, 26)}}><TerminalJourney frame={oldFrame} /></div>
            <div style={{opacity: visible(frame, 390, 535, 24)}}><EvidenceJourney frame={frame + 680} /></div>
            <div style={{opacity: visible(frame, 500, 650, 24)}}><HumanJourney frame={frame + 905} /></div>
            <div style={{opacity: visible(frame, 625, 830, 24)}}><AgentJourney frame={frame + 1040} /></div>
          </div>
        </div>
      </div>
      <div className="product-keynote-note" style={{opacity: progress(frame, 690, 730)}}><span className="product-purple-dot" /> the interface is a window into the protocol</div>
    </ProductFrame>
  );
};
