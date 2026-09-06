import React from 'react';
import {Command, Detail} from '../components';
import {progress, visible} from '../motion';

export function HumanJourney({frame}: {frame: number}) {
  return <div className="kn-human" style={{opacity: visible(frame, 1405, 1665, 22)}}>
    <div className="kn-reviewline" style={{opacity: progress(frame, 1410, 1434)}}><span>Reviewed branches</span><span>r1b1</span><strong>r1b2</strong><span>r1b3</span><span className="kn-demo">Illustrative selection</span></div>
    <Command frame={frame} start={1430} verb="parallel-promote" fontSize={38} options={['--target ./project', '--parallel-dir ./project/research_record/parallel/demo', '--branch r1b2 --allow-edits']} />
    <div className="kn-enter" style={{opacity: progress(frame, 1510, 1530), background: frame < 1590 ? '#f5f6f7' : '#eaf5fb', scale: frame >= 1590 && frame < 1595 ? 0.92 : 1}}>{frame < 1590 ? 'return ↵' : '↵ submitted'}</div>
    <Detail style={{position: 'absolute', left: 88, bottom: 42, opacity: progress(frame, 1589, 1610)}}>Your choice. Explicit adoption.</Detail>
  </div>;
}
