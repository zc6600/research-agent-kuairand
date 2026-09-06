import React from 'react';
import {spring} from 'remotion';
import {Detail, Typed} from '../components';
import {progress, visible} from '../motion';

export function AgentJourney({frame}: {frame: number}) {
  const dock = spring({frame: frame - 1670, fps: 30, config: {damping: 28, stiffness: 80}});
  return <div className="kn-agent" style={{opacity: visible(frame, 1665, 1944, 22)}}>
    <div className="kn-skillfile" style={{left: 565 - 480 * dock, top: 96 - 42 * dock, scale: 1.4 - 0.4 * dock}}>
      <svg width="35" height="43" viewBox="0 0 35 43"><path d="M3 2 H22 L32 12 V40 H3 Z M22 2 V12 H32" fill="none" stroke="#1476b5" strokeWidth="2" /></svg>
      <div><strong>SKILL.md</strong><small>research-agent</small></div>
    </div>
    <div className="kn-agent-prompt" style={{opacity: progress(frame, 1724, 1742)}}><Typed frame={frame} start={1728} duration={62} text="Use the research-agent skill." /><div style={{opacity: progress(frame, 1790, 1806)}}>Explore in parallel. Let me review what to keep.</div></div>
    <div className="kn-agent-response" style={{opacity: progress(frame, 1820, 1840), translate: `0 ${(1 - progress(frame, 1820, 1850)) * 15}px`}}><span className="kn-agent-spark">✳</span><div>Research workflow, connected.<small>Task, memory and evidence stay with the project.</small></div></div>
    <div className="kn-worldfiles" style={{opacity: progress(frame, 1860, 1884)}}><span>task.md</span><i /><span>research_record/</span><i /><span>system/</span></div>
    <Detail style={{position: 'absolute', right: 50, top: 32, fontSize: 18}}>Coding-agent interaction concept</Detail>
  </div>;
}
