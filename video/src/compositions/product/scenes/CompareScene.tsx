import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, progress, reveal, revealX} from '../motion';
import {Caption, DrawnPath, Hero, Kicker, ProductFrame, Rule} from '../components';

type ComparisonRow = {label: string; direct: string; scio: string; color: string};

const comparisonRows: ComparisonRow[] = [
  {label: 'JOB', direct: 'solve a task now', scio: 'run a research loop', color: COLORS.blue},
  {label: 'MEMORY', direct: 'prompt + repo context', scio: 'evidence + State on disk', color: COLORS.green},
  {label: 'SEARCH', direct: 'one active trajectory', scio: 'handoff + parallel branches', color: COLORS.purple},
  {label: 'CONTROL', direct: 'prompt and review', scio: 'step · run · resume · promote', color: COLORS.rose},
];

function AgentBadge({name, color, start}: {name: string; color: string; start: number}) {
  const frame = useCurrentFrame();
  const p = progress(frame, start, start + 24);
  return <div className="product-agent-badge" style={{opacity: p, transform: `translate3d(${(1 - p) * 24}px, 0, 0)`, borderColor: `${color}66`}}><span style={{backgroundColor: color}} />{name}</div>;
}

export const ProductCompareScene: React.FC = () => {
  const frame = useCurrentFrame();
  const table = progress(frame, 62, 155);
  const connector = progress(frame, 110, 190);
  return (
    <ProductFrame chapter="07 / WHY IT IS DIFFERENT" accent={COLORS.blue}>
      <div className="product-compare-copy">
        <div style={reveal(frame, 16, 22, 18)}><Kicker color={COLORS.blue}>A WORKFLOW LAYER</Kicker></div>
        <Hero>Use the model<br /><span className="product-muted">you already trust.</span></Hero>
        <Caption>SciOdyssey does not compete with Codex,<br />Claude Code, Gemini, or AGY. It gives them<br />a longer-lived research job to do.</Caption>
        <div className="product-compare-runtime" style={reveal(frame, 150, 22, 12)}><span className="product-blue-dot" /> one research protocol · many agent runtimes</div>
      </div>
      <div className="product-compare-stage">
        <div className="product-agent-stack">
          <div className="product-stack-kicker">DIRECT CODING AGENT</div>
          <AgentBadge name="Codex" color={COLORS.blue} start={30} />
          <AgentBadge name="Claude Code" color={COLORS.orange} start={50} />
          <AgentBadge name="Gemini CLI" color={COLORS.purple} start={70} />
          <AgentBadge name="AGY" color={COLORS.rose} start={90} />
        </div>
        <svg className="product-compare-flow" viewBox="0 0 780 650" aria-hidden="true">
          <DrawnPath d="M112 170 C248 170 285 250 438 250" color={COLORS.blue} start={38} duration={65} width={2} />
          <DrawnPath d="M112 260 C248 260 285 290 438 290" color={COLORS.orange} start={58} duration={65} width={2} />
          <DrawnPath d="M112 350 C248 350 285 330 438 330" color={COLORS.purple} start={78} duration={65} width={2} />
          <DrawnPath d="M112 440 C248 440 285 370 438 370" color={COLORS.rose} start={98} duration={65} width={2} />
          <DrawnPath d="M438 310 H716" color={COLORS.green} start={110} duration={70} width={3} />
          <circle cx="438" cy="310" r="12" fill={COLORS.green} opacity={connector} />
          <circle cx="716" cy="310" r="13" fill={COLORS.green} opacity={connector} />
        </svg>
        <div className="product-scio-layer" style={{opacity: connector, transform: `scale(${0.92 + connector * 0.08})`}}><div className="product-scio-layer-mark">✦</div><strong>SCIODYSSEY</strong><small>research protocol</small></div>
        <div className="product-compare-table" style={{opacity: table, transform: `translateY(${(1 - table) * 18}px)`}}>
          <div className="product-compare-table-head"><span /> <b>DIRECT USE</b><b className="product-green">SCIODYSSEY ON TOP</b></div>
          {comparisonRows.map((row) => <div className="product-compare-row" key={row.label} style={{borderColor: `${row.color}45`}}><span className="product-compare-label" style={{color: row.color}}>{row.label}</span><span>{row.direct}</span><strong>{row.scio}</strong></div>)}
        </div>
      </div>
      <div className="product-compare-foot" style={{opacity: progress(frame, 208, 240)}}><Rule color={COLORS.blue} start={208} style={{width: 120}} /><span>the model remains replaceable</span><i>·</i><span>the research world remains durable</span></div>
    </ProductFrame>
  );
};
