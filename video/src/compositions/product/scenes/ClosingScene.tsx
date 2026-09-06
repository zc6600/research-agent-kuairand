import React from 'react';
import {Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {COLORS, progress, reveal} from '../motion';
import {DrawnPath, Hero, Kicker, ProductFrame, ProductLogo, World} from '../components';

export const ProductClosingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const art = interpolate(frame, [70, 190], [0, 0.14], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const paths = progress(frame, 28, 152);
  const final = progress(frame, 180, 230);
  return (
    <ProductFrame chapter="10 / START YOUR ODYSSEY" accent={COLORS.blue}>
      <Img className="product-closing-art" src={staticFile('assets/research-world-cover.png')} style={{opacity: art}} />
      <svg className="product-closing-field" viewBox="0 0 1920 1080" aria-hidden="true">
        <DrawnPath d="M-50 710 C260 710 430 430 760 540 S1260 780 1610 380 S1860 280 2010 300" color={COLORS.blue} start={24} duration={122} width={2.5} />
        <DrawnPath d="M-50 810 C280 810 480 835 780 706 S1260 450 1600 620 S1860 835 2010 780" color={COLORS.orange} start={48} duration={122} width={2.5} />
        <DrawnPath d="M-50 585 C270 520 485 620 770 700 S1230 560 1590 740 S1860 620 2010 550" color={COLORS.purple} start={72} duration={122} width={2.5} />
        <circle cx="1590" cy="575" r="11" fill={COLORS.green} opacity={paths} />
      </svg>
      <div className="product-closing-copy">
        <div style={reveal(frame, 18, 22, 18)}><Kicker color={COLORS.blue}>RESEARCH AGENT / SCIODYSSEY</Kicker></div>
        <Hero>Keep the experience.<br /><span className="product-blue">Reopen the search.</span></Hero>
        <p className="product-closing-lead" style={reveal(frame, 76, 24, 16)}>Automate the repetition.<br /><span>Keep the judgment.</span></p>
      </div>
      <div className="product-closing-world" style={{opacity: progress(frame, 108, 158), transform: `translateY(${(1 - progress(frame, 108, 165)) * 18}px)`}}><World size={300} color={COLORS.green} start={112} /><div><Kicker color={COLORS.green}>ONE WORLD</Kicker><span>many ways forward</span></div></div>
      <div className="product-closing-rail" style={{opacity: final}}><span>brief</span><i>·</i><span>step</span><i>·</i><span>run</span><i>·</i><span>parallel</span><i>·</i><span>review</span></div>
      <div className="product-closing-cta" style={{opacity: final, transform: `translateY(${(1 - final) * 16}px)`}}><div className="mono"><span className="product-muted">$</span> ./scripts/research-agent <b>step</b> --cli codex --allow-edits</div><div className="product-closing-brand"><ProductLogo accent={COLORS.blue} /><span>Start with a question.</span></div></div>
    </ProductFrame>
  );
};
