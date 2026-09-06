import React from 'react';
import {Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {COLORS, progress, reveal, revealX} from '../motion';
import {Caption, Hero, Kicker, Metric, ProductFrame, Rule} from '../components';

export const ProductProofScene: React.FC = () => {
  const frame = useCurrentFrame();
  const score = progress(frame, 75, 135);
  const chart = progress(frame, 130, 205);
  return (
    <ProductFrame chapter="09 / EVIDENCE, NOT PROMISES" accent={COLORS.green}>
      <div className="product-proof-copy">
        <div style={reveal(frame, 16, 22, 18)}><Kicker color={COLORS.green}>A RECORDED CASE STUDY / KUAIRAND-PURE</Kicker></div>
        <Hero>From open search<br /><span className="product-muted">to verified result.</span></Hero>
        <Caption>Every claim is tied to an artifact, a metric,<br />and the exact implementation that produced it.</Caption>
        <div className="product-proof-callout" style={reveal(frame, 190, 22, 12)}><span className="product-green-dot" /> public validation · unchanged checker · CPU-only</div>
      </div>
      <div className="product-proof-score" style={{opacity: score, transform: `translateX(${(1 - score) * 24}px)`}}><Kicker color={COLORS.muted}>RETAINED PUBLIC VALIDATION / PRIMARY</Kicker><strong>0.6059363</strong><span><b>+0.0043363</b> absolute improvement vs official reference</span><div className="product-score-line"><i style={{width: `${score * 100}%`}} /></div><small>GAUC 0.6728421 <em>·</em> nDCG@5 0.5390304</small></div>
      <div className="product-proof-metrics">
        <Metric value="4" label="AUTONOMOUS CYCLES" detail="within a 50-iteration cap" color={COLORS.blue} start={96} />
        <Metric value="13" label="NAMED EXPERIMENTS" detail="E001–E013 · 7 full evaluations" color={COLORS.orange} start={116} />
        <Metric value="0" label="GPU-HOURS" detail="NumPy ensemble on CPU" color={COLORS.purple} start={136} />
      </div>
      <div className="product-proof-chart" style={{opacity: chart, transform: `translateY(${(1 - chart) * 18}px)`}}><div className="product-proof-chart-head"><span>measured comparison</span><b>public validation / primary</b></div><Img src={staticFile('assets/token-score-comparison.png')} /><div className="product-proof-chart-caption">Recorded controls and the retained Research Agent result · input + output tokens including cache-read</div></div>
      <div className="product-proof-foot" style={{opacity: progress(frame, 250, 280)}}><Rule color={COLORS.green} start={250} style={{width: 108}} /><span>evidence remains connected to the work</span></div>
    </ProductFrame>
  );
};
