import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {COLORS, draw, progress, reveal, revealX} from '../motion';
import {Caption, DrawnPath, Hero, Kicker, ProductFrame, Rule, World} from '../components';

export const ProductProblemScene: React.FC = () => {
  const frame = useCurrentFrame();
  const basin = progress(frame, 80, 190);
  const pulse = 1 + Math.sin(frame / 18) * 0.025;
  return (
    <ProductFrame chapter="02 / THE PROBLEM" accent={COLORS.orange}>
      <div className="product-problem-copy">
        <div style={reveal(frame, 16, 22, 18)}><Kicker color={COLORS.orange}>THE WORK BETWEEN PROMPTS</Kicker></div>
        <Hero>One prompt ends.<br /><span className="product-muted">Research shouldn’t.</span></Hero>
        <Caption>Models can write the next experiment.<br />The hard part is keeping the scientific thread.</Caption>
        <Rule color={COLORS.orange} start={108} style={{width: 140, marginTop: 34}} />
        <div className="product-problem-note" style={reveal(frame, 130, 22, 12)}>A long trajectory remembers everything — including its own momentum.</div>
      </div>
      <div className="product-problem-map" style={{transform: `scale(${pulse})`}}>
        <svg viewBox="0 0 1030 600" aria-hidden="true">
          <line x1="55" y1="292" x2="975" y2="292" stroke={COLORS.line} strokeWidth="2" />
          <DrawnPath d="M55 292 C230 292 222 120 390 120 S590 450 750 292 S880 292 975 292" color={COLORS.orange} start={30} duration={110} width={3} />
          <DrawnPath d="M55 292 C200 292 230 475 392 475 S590 110 750 292" color={COLORS.rose} start={65} duration={110} width={3} opacity={0.82} />
          <circle cx="975" cy="292" r="16" fill={COLORS.paper} stroke={COLORS.rose} strokeWidth="4" />
          <circle cx="975" cy="292" r="31" fill="none" stroke={COLORS.rose} strokeOpacity=".2" strokeWidth="2" />
        </svg>
        <div className="product-problem-label product-problem-long" style={revealX(frame, 116, 22, 20)}><span style={{color: COLORS.orange}}>LONG TRAJECTORY</span><strong>Context accumulates.</strong><small>Hypotheses, detours, unfinished commitments</small></div>
        <div className="product-problem-label product-problem-restart" style={revealX(frame, 144, 22, 20)}><span style={{color: COLORS.rose}}>NAIVE RESTART</span><strong>Progress disappears.</strong><small>Relearn the evaluator. Repeat the failure.</small></div>
        <div className="product-problem-world" style={{opacity: basin, transform: `translateY(${(1 - basin) * 16}px)`}}><World size={160} color={COLORS.green} start={80} /><span>the missing layer</span></div>
        <div className="product-problem-end" style={{opacity: progress(frame, 165, 200)}}><span className="product-green-dot" /> same search basin</div>
      </div>
      <div className="product-problem-footer" style={{opacity: progress(frame, 185, 215)}}>What should survive: the evidence — not the unfinished thought.</div>
    </ProductFrame>
  );
};
