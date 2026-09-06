import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {COLORS, progress, reveal, revealX} from '../motion';
import {Caption, Hero, Kicker, ProductFrame, ProductScreenshot, Rule} from '../components';

export const ProductDashboardScene: React.FC = () => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [110, 250, 390], [1, 1.13, 1.02], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const result = progress(frame, 180, 235);
  return (
    <ProductFrame chapter="06 / OBSERVE THE RUN" accent={COLORS.green}>
      <div className="product-dashboard-copy">
        <div style={reveal(frame, 16, 22, 18)}><Kicker color={COLORS.green}>A WINDOW INTO THE WORLD</Kicker></div>
        <Hero>See the run.<br /><span className="product-muted">Keep the proof.</span></Hero>
        <Caption>Status, activity, State, evidence.<br />The dashboard makes an autonomous run legible.</Caption>
        <div className="product-dashboard-command" style={reveal(frame, 150, 22, 12)}><span className="product-muted">$</span> ./scripts/research-agent <b>gui</b> <span className="product-muted">--target ./project</span></div>
      </div>
      <div className="product-dashboard-stage" style={{transform: `scale(${zoom})`}}>
        <ProductScreenshot src="assets/dashboard-overview.png" className="product-dashboard-overview" start={30} />
        <ProductScreenshot src="assets/dashboard-result.png" className="product-dashboard-result" title="Retained Validation Result" tag="RETAINED" start={178} color={COLORS.green} />
        <div className="product-dashboard-focus" style={{opacity: result, transform: `translateY(${(1 - result) * 16}px)`}}><span className="product-green-dot" /> retained checkpoint <b>S004</b><i>·</i> primary <b>0.605936</b></div>
      </div>
      <div className="product-dashboard-foot" style={{opacity: progress(frame, 260, 300)}}><Rule color={COLORS.green} start={260} style={{width: 94}} /><span>read-only by design</span><i>·</i><span>artifacts stay connected</span></div>
    </ProductFrame>
  );
};
