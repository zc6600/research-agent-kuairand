import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, draw, progress, reveal, revealX, scaleIn} from '../motion';
import {Caption, DrawnPath, Hero, Kicker, ProductFrame, Rule, Scientist, World} from '../components';

type Branch = {id: string; title: string; detail: string; color: string; y: number; start: number};

const branches: Branch[] = [
  {id: 'r1b1', title: 'Scientist A', detail: 'feature interactions', color: COLORS.blue, y: 118, start: 76},
  {id: 'r1b2', title: 'Scientist B', detail: 'representation shift', color: COLORS.purple, y: 260, start: 94},
  {id: 'r1b3', title: 'Scientist C', detail: 'sequence / debiasing', color: COLORS.orange, y: 402, start: 112},
];

function BranchCard({branch}: {branch: Branch}) {
  const frame = useCurrentFrame();
  const p = progress(frame, branch.start, branch.start + 24);
  return <div className="product-branch-card" style={{top: branch.y, opacity: p, transform: `translate3d(${(1 - p) * 22}px, 0, 0)`, borderColor: `${branch.color}70`}}><span className="product-branch-id" style={{color: branch.color, borderColor: `${branch.color}70`}}>{branch.id}</span><div><strong>{branch.title}</strong><small>{branch.detail} · isolated worktree</small></div><b style={{color: branch.color}}>DONE</b></div>;
}

export const ProductParallelHumanScene: React.FC = () => {
  const frame = useCurrentFrame();
  const branchProgress = progress(frame, 45, 170);
  const review = progress(frame, 198, 240);
  const pointer = progress(frame, 244, 288);
  return (
    <ProductFrame chapter="08 / BREADTH WITH A HUMAN GATE" accent={COLORS.rose}>
      <div className="product-parallel-copy">
        <div style={reveal(frame, 16, 22, 18)}><Kicker color={COLORS.rose}>WHEN ONE PATH IS NOT ENOUGH</Kicker></div>
        <Hero>Open the search<br /><span className="product-muted">in parallel.</span></Hero>
        <Caption>Independent Scientists start from the same<br />research world. A reviewer compares the worlds.</Caption>
        <div className="product-parallel-command" style={reveal(frame, 168, 22, 12)}><span className="product-muted">$</span> ./scripts/research-agent <b>parallel</b><br /><span className="product-muted">&nbsp;&nbsp;--branches 3 --keep 1</span></div>
      </div>
      <div className="product-parallel-stage">
        <div className="product-parallel-origin" style={scaleIn(frame, 28, 0.84)}><World size={168} color={COLORS.green} start={36} /><span>R0 · research world</span></div>
        <svg className="product-parallel-lines" viewBox="0 0 1040 600" aria-hidden="true">
          <DrawnPath d="M130 302 C280 302 310 118 485 118 H970" color={COLORS.blue} start={40} duration={90} width={2.5} />
          <DrawnPath d="M130 302 H970" color={COLORS.purple} start={58} duration={90} width={2.5} />
          <DrawnPath d="M130 302 C280 302 310 440 485 440 H970" color={COLORS.orange} start={76} duration={90} width={2.5} />
          <circle cx="130" cy="302" r="9" fill={COLORS.green} opacity={branchProgress} />
          <circle cx="970" cy="302" r="10" fill={COLORS.rose} opacity={review} />
        </svg>
        {branches.map(branch => <BranchCard key={branch.id} branch={branch} />)}
        <div className="product-review-card" style={{opacity: review, transform: `translateY(${(1 - review) * 16}px)`}}><span className="product-review-icon">⌁</span><div><strong>Post-hoc review</strong><small>compare evidence · select explicitly</small></div><b style={{color: COLORS.purple}}>promote r1b2 →</b></div>
        <div className="product-operator-cursor" style={{opacity: pointer, transform: `translate3d(${pointer * 180}px, ${pointer * 28}px, 0)`}}><span /> operator</div>
      </div>
      <div className="product-parallel-foot" style={{opacity: progress(frame, 300, 330)}}><Rule color={COLORS.rose} start={300} style={{width: 106}} /><span>review is explicit</span><i>·</i><span>branch code is never merged automatically</span></div>
    </ProductFrame>
  );
};
