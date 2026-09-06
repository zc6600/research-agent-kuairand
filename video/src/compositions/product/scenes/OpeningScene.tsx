import React from 'react';
import {Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {COLORS, draw, progress, reveal} from '../motion';
import {Caption, DrawnPath, Hero, Kicker, ProductFrame, ProductLogo, World} from '../components';

export const ProductOpeningScene: React.FC = () => {
  const frame = useCurrentFrame();
  const artOpacity = interpolate(frame, [0, 70], [0, 0.18], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const fieldOpacity = progress(frame, 34, 130);
  return (
    <ProductFrame chapter="01 / MEET SCIODYSSEY" accent={COLORS.blue}>
      <Img className="product-opening-art" src={staticFile('assets/research-world-cover.png')} style={{opacity: artOpacity, transform: `scale(${1.05 - progress(frame, 0, 450) * 0.025})`}} />
      <svg className="product-opening-field" viewBox="0 0 1920 1080" aria-hidden="true" style={{opacity: fieldOpacity}}>
        <DrawnPath d="M-50 700 C250 700 420 430 740 520 S1270 760 1590 380 S1850 280 1980 300" color={COLORS.blue} start={30} duration={135} width={2.5} />
        <DrawnPath d="M-60 805 C270 805 470 830 770 700 S1240 450 1590 610 S1850 840 1980 780" color={COLORS.orange} start={54} duration={135} width={2.5} />
        <DrawnPath d="M-50 575 C250 520 470 620 760 700 S1220 570 1580 740 S1840 610 1980 550" color={COLORS.purple} start={78} duration={135} width={2.5} />
        <circle cx="1590" cy="570" r="10" fill={COLORS.green} opacity={progress(frame, 100, 145)} />
      </svg>
      <div className="product-opening-copy">
        <div style={reveal(frame, 14, 24, 18)}><Kicker color={COLORS.blue}>OPEN-WORLD ML RESEARCH / A NEW PRODUCT</Kicker></div>
        <Hero className="product-opening-hero">Meet <span className="product-blue">SciOdyssey.</span><br /><span className="product-muted">Research that keeps going.</span></Hero>
        <Caption>Research Agent for the work that does not fit inside one prompt.<br />Autonomous exploration, externalized memory, human judgment.</Caption>
        <div className="product-opening-command mono" style={{...reveal(frame, 116, 22, 12), opacity: progress(frame, 116, 138)}}><span className="product-muted">$</span> ./scripts/research-agent <b>step</b> <span className="product-muted">--cli codex</span></div>
      </div>
      <div className="product-opening-world" style={{opacity: progress(frame, 70, 108), transform: `translateY(${(1 - progress(frame, 70, 120)) * 22}px)`}}>
        <World size={310} color={COLORS.green} start={74} />
        <div className="product-opening-world-label"><Kicker color={COLORS.green}>THE RESEARCH WORLD</Kicker><span>evidence · failures · code</span></div>
      </div>
      <div className="product-opening-mark" style={{opacity: progress(frame, 150, 180)}}><ProductLogo accent={COLORS.blue} /><span>Automate the repetition.<br /><b>Keep the judgment.</b></span></div>
    </ProductFrame>
  );
};
