import React from 'react';
import {Command, Detail} from '../components';
import {blue, linear, progress, sky, visible} from '../motion';

function SerialRail({frame}: {frame: number}) {
  const stepProgress = linear(frame, 302, 390);
  const runProgress = linear(frame, 544, 712);
  const p = frame < 480 ? stepProgress : runProgress;
  const positions = [110, 443, 777, 1110];
  const labels = ['META', 'Scientist', 'Evidence', 'Your turn'];
  return <div className="kn-serial" style={{opacity: visible(frame, 286, 790, 24)}}>
    <svg width="1220" height="160" viewBox="0 0 1220 160">
      <path d="M110 60 H1110" stroke="#e6e6e8" strokeWidth="3" />
      <path d="M110 60 H1110" stroke={sky} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - p} />
      {positions.map((x, i) => <g key={x}>
        <circle cx={x} cy="60" r={p >= i / 3 ? 11 : 7} fill={p >= i / 3 ? sky : '#e6e6e8'} />
        <circle cx={x} cy="60" r="21" fill="none" stroke={sky} opacity={p >= i / 3 ? 0.18 : 0} />
      </g>)}
      <circle cx={110 + p * 1000} cy="60" r="7" fill={blue} />
    </svg>
    <div className="kn-serial-labels" aria-hidden="true">
      {positions.map((x, i) => (
        <span key={x} style={{left: x}}>{frame < 520 ? labels[i] : `Cycle 0${i + 1}`}</span>
      ))}
    </div>
    <Detail style={{position: 'absolute', top: 163, width: '100%', textAlign: 'center', opacity: visible(frame, 398, 482, 14)}}>Evidence retained. Control returned.</Detail>
    <Detail style={{position: 'absolute', top: 163, width: '100%', textAlign: 'center', opacity: progress(frame, 590, 615)}}>Up to four cycles. A fresh Scientist each time.</Detail>
  </div>;
}

function ParallelRail({frame}: {frame: number}) {
  const spread = progress(frame, 792, 850);
  const collect = progress(frame, 970, 1025);
  const flatten = progress(frame, 1040, 1108);
  return <div className="kn-parallel" style={{opacity: visible(frame, 790, 1110, 20)}}>
    <svg width="1260" height="330" viewBox="0 0 1260 330">
      <text x="110" y="305" textAnchor="middle" fill="#797d84" fontSize="22">Research world</text>
      {/* Draw paths and moving nodes first. Cards deliberately sit above this layer. */}
      {[0, 1, 2].map(i => {
        const y = 154 + (i - 1) * 100 * spread * (1 - flatten);
        const p = linear(frame, 844 + i * 12, 962 + i * 9);
        const path = `M110 154 C270 154 265 ${y} 390 ${y} H865 C1000 ${y} 1015 154 1140 154`;
        return <g key={`path-${i}`}>
          <path d={path} fill="none" stroke="#e6e6e8" strokeWidth="2" />
          <path d={path} fill="none" stroke={i === 1 ? blue : sky} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - p} />
          <circle cx={390 + 490 * p} cy={y} r="6" fill={blue} opacity={(1 - collect) * (1 - flatten)} />
        </g>;
      })}
      {/* Paint every card background together, then paint every label last. This prevents
          neighboring cards from hiding Scientist B during the opening spread. */}
      {[0, 1, 2].map(i => {
        const y = 154 + (i - 1) * 100 * spread * (1 - flatten);
        return <rect key={`card-${i}`} x="430" y={y - 32} width="390" height="64" rx="32" fill="white" stroke="#e6e6e8" opacity={1 - flatten} />;
      })}
      {[0, 1, 2].map(i => {
        const y = 154 + (i - 1) * 100 * spread * (1 - flatten);
        return <g key={`label-${i}`} opacity={1 - flatten}>
          <text x="459" y={y + 8} fill="#111217" fontSize="24">Scientist {String.fromCharCode(65 + i)}</text>
          <text x="785" y={y + 8} textAnchor="end" fill={blue} fontSize="22">r1b{i + 1}</text>
        </g>;
      })}
      <circle cx="110" cy="154" r="13" fill={blue} />
      <circle cx="1140" cy="154" r="13" fill={collect > 0.5 ? blue : '#d1d4d9'} />
      <circle cx="1140" cy="154" r={22 + 8 * collect} fill="none" stroke={sky} opacity={collect * 0.45} />
      <text x="1140" y="212" textAnchor="middle" fill={blue} fontSize="22">Reviewer</text>
    </svg>
    <Detail style={{textAlign: 'center', opacity: progress(frame, 906, 940)}}>Three isolated worktrees. One post-hoc review.</Detail>
  </div>;
}

export function TerminalJourney({frame}: {frame: number}) {
  return <div className="kn-terminal-content" style={{opacity: 1 - progress(frame, 1070, 1110)}}>
    <div style={{opacity: visible(frame, 150, 480, 18)}}><Command frame={frame} start={170} verb="step" options={['--cli codex --target ./project --allow-edits']} /></div>
    <div style={{opacity: visible(frame, 480, 778, 18)}}><Command frame={frame} start={480} verb="run" options={['--cli codex --target ./project', '--max-cycles 4 --allow-edits']} /></div>
    <div style={{opacity: visible(frame, 778, 1108, 18)}}><Command frame={frame} start={778} verb="parallel" options={['--cli codex --target ./project', '--branches 3 --parallelism 3 --keep 1 --allow-edits']} /></div>
    <SerialRail frame={frame} />
    <ParallelRail frame={frame} />
  </div>;
}
