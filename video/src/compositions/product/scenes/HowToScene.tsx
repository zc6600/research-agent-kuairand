import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {COLORS, draw, progress, reveal} from '../motion';
import {Caption, DrawnPath, FeatureCard, Hero, Kicker, ProductFrame, Rule} from '../components';

export const ProductHowToScene: React.FC = () => {
  const frame = useCurrentFrame();
  const scan = progress(frame, 60, 285);
  return (
    <ProductFrame chapter="04 / HOW TO USE IT" accent={COLORS.blue}>
      <div className="product-howto-copy">
        <div style={reveal(frame, 16, 22, 18)}><Kicker color={COLORS.blue}>THREE MOVES TO START</Kicker></div>
        <Hero>You bring the<br /><span className="product-muted">question.</span></Hero>
        <Caption>SciOdyssey turns a research brief into an observable,<br />bounded loop you can enter at any depth.</Caption>
      </div>
      <div className="product-howto-rail">
        <svg viewBox="0 0 1450 160" aria-hidden="true"><line x1="70" y1="80" x2="1380" y2="80" stroke={COLORS.line} strokeWidth="2" /><line x1="70" y1="80" x2={70 + 1310 * scan} y2="80" stroke={COLORS.blue} strokeWidth="3" /><circle cx={70 + 1310 * scan} cy="80" r="7" fill={COLORS.blue} /><circle cx="70" cy="80" r="9" fill={COLORS.blue} /><circle cx="725" cy="80" r="9" fill={scan > 0.5 ? COLORS.purple : COLORS.line} /><circle cx="1380" cy="80" r="9" fill={scan > 0.92 ? COLORS.green : COLORS.line} /><DrawnPath d="M70 80 C260 80 295 25 455 25 H600" color={COLORS.blue} start={36} duration={60} width={2} /><DrawnPath d="M725 80 H875 C1000 80 1030 135 1180 135 H1380" color={COLORS.purple} start={105} duration={60} width={2} /></svg>
        <FeatureCard number="01" title="Frame the task" detail="task · evaluator · baseline" color={COLORS.blue} start={40} active />
        <FeatureCard number="02" title="Choose the depth" detail="step · run · parallel" color={COLORS.purple} start={76} />
        <FeatureCard number="03" title="Review what survives" detail="evidence · State · next cycle" color={COLORS.green} start={112} />
      </div>
      <div className="product-howto-command" style={{...reveal(frame, 175, 24, 14), opacity: progress(frame, 175, 199)}}><span className="product-muted">$</span> ./scripts/research-agent <b style={{color: COLORS.purple}}>run</b> --cli codex --max-cycles 4 --allow-edits</div>
      <div className="product-howto-foot" style={{opacity: progress(frame, 220, 248)}}><Rule color={COLORS.blue} start={220} style={{width: 94}} /><span>step for control</span><i>·</i><span>run for continuity</span><i>·</i><span>parallel for breadth</span></div>
    </ProductFrame>
  );
};
