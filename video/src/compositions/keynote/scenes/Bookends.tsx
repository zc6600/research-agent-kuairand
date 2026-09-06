import React from 'react';
import {progress, sky, travel, visible} from '../motion';

export function Opening({frame}: {frame: number}) {
  return <div className="kn-opening" style={{opacity: 1 - progress(frame, 112, 151)}}>
    <div style={{opacity: progress(frame, 8, 30), translate: `0 ${(1 - progress(frame, 8, 55)) * 35}px`}}>Your research.</div>
    <div style={{color: '#85868c', opacity: progress(frame, 45, 67), translate: `0 ${(1 - progress(frame, 45, 90)) * 30}px`}}>Your rhythm.</div>
    <div className="kn-opening-line" style={{width: travel(frame, [60, 98, 135], [8, 460, 1000]), opacity: progress(frame, 54, 75)}} />
  </div>;
}

export function Closing({frame}: {frame: number}) {
  const p = progress(frame, 1908, 2000);
  return <div className="kn-closing" style={{opacity: progress(frame, 1908, 1945)}}>
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
      {[-1, 0, 1].map(i => <path key={i} d={`M${190 + p * 430} ${800 - p * 55} C650 ${800 - p * 55 + i * (1 - p) * 130} 1200 ${650 + p * 95 + i * (1 - p) * 110} ${1730 - p * 430} ${800 - p * 55}`} fill="none" stroke={sky} strokeWidth={2.5} opacity={i === 0 ? 1 : 1 - p} />)}
    </svg>
    <div className="kn-closing-copy" style={{opacity: progress(frame, 1940, 1970), translate: `0 ${(1 - progress(frame, 1940, 1995)) * 24}px`}}>Let it run.<br /><span style={{color: '#85868c'}}>Make it yours.</span></div>
    <div className="kn-brand" style={{opacity: progress(frame, 2025, 2060)}}>SciOdyssey<span>Automated research. Human judgment.</span></div>
    <div style={{position: 'absolute', inset: 0, background: 'white', opacity: visible(frame, 2200, 2300)}} />
  </div>;
}
