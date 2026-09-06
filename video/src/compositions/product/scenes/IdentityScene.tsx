import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, draw, progress, reveal, revealX, scaleIn} from '../motion';
import {Caption, DrawnPath, Hero, Kicker, ProductFrame, Scientist, World} from '../components';

function RoleCard({title, detail, color, icon, start}: {title: string; detail: string; color: string; icon: React.ReactNode; start: number}) {
  const frame = useCurrentFrame();
  return <div className="product-role-card" style={{...scaleIn(frame, start, 0.9), borderColor: `${color}70`}}><div className="product-role-icon" style={{color, backgroundColor: `${color}12`}}>{icon}</div><strong style={{color}}>{title}</strong><small>{detail}</small></div>;
}

export const ProductIdentityScene: React.FC = () => {
  const frame = useCurrentFrame();
  const flow = progress(frame, 86, 180);
  return (
    <ProductFrame chapter="03 / WHAT SCIODYSSEY IS" accent={COLORS.green}>
      <div className="product-identity-copy">
        <div style={reveal(frame, 16, 22, 18)}><Kicker color={COLORS.green}>A PRODUCT LAYER, NOT A NEW MODEL</Kicker></div>
        <Hero>A research layer<br /><span className="product-muted">around your agent.</span></Hero>
        <Caption>SciOdyssey gives coding agents a longer-lived world to work in —<br />with clear boundaries for cognition, evidence, and execution.</Caption>
      </div>
      <div className="product-identity-stage">
        <svg className="product-identity-lines" viewBox="0 0 1500 450" aria-hidden="true">
          <DrawnPath d="M208 224 H470 C545 224 568 118 650 118 H820" color={COLORS.green} start={30} duration={70} width={2.5} />
          <DrawnPath d="M208 224 H470 C545 224 568 330 650 330 H820" color={COLORS.purple} start={48} duration={70} width={2.5} />
          <DrawnPath d="M820 118 H1080 C1145 118 1160 224 1220 224" color={COLORS.blue} start={86} duration={70} width={2.5} />
          <DrawnPath d="M820 330 H1080 C1145 330 1160 224 1220 224" color={COLORS.rose} start={105} duration={70} width={2.5} />
          <circle cx={208} cy="224" r="8" fill={COLORS.green} opacity={flow} />
          <circle cx={1220} cy="224" r="8" fill={COLORS.blue} opacity={flow} />
        </svg>
        <div className="product-identity-world"><World size={190} color={COLORS.green} start={28} label="RESEARCH WORLD" detail="persists across trajectories" /></div>
        <div className="product-identity-top"><RoleCard title="Scientist" detail="owns scientific judgment" color={COLORS.purple} icon="✦" start={72} /></div>
        <div className="product-identity-bottom"><RoleCard title="META" detail="owns what survives" color={COLORS.rose} icon="✓" start={96} /></div>
        <div className="product-identity-runtime"><RoleCard title="Runtime" detail="owns deterministic mechanics" color={COLORS.orange} icon="⌁" start={122} /></div>
        <div className="product-identity-reset" style={{...reveal(frame, 170, 24, 14)}}><span>↻</span><strong>CONTEXT RESET</strong><small>fresh reasoning<br />inherits experience</small></div>
      </div>
      <div className="product-identity-footer" style={reveal(frame, 205, 24, 10)}><span className="product-green-dot" /> the system preserves the science, not the trajectory</div>
    </ProductFrame>
  );
};
