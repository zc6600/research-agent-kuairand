import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {Headline, WindowBar} from './components';
import {narration, progress, travel} from './motion';
import {AgentJourney} from './scenes/AgentJourney';
import {Opening, Closing} from './scenes/Bookends';
import {EvidenceJourney} from './scenes/EvidenceJourney';
import {HumanJourney} from './scenes/HumanJourney';
import {TerminalJourney} from './scenes/TerminalJourney';
import './keynote.css';

export type KeynoteProps = {
  voiceOverSrc?: string;
  musicSrc?: string;
  soundEffectsSrc?: string;
  soundDesign?: boolean;
  showSubtitles?: boolean;
};

export const SciOdysseyKeynoteFilm: React.FC<KeynoteProps> = ({voiceOverSrc, musicSrc, soundEffectsSrc, soundDesign = true, showSubtitles = false}) => {
  const frame = useCurrentFrame();
  const width = travel(frame, [130, 225, 750, 820, 1050, 1130, 1380, 1450, 1640, 1710], [1350, 1350, 1350, 1480, 1480, 1640, 1640, 1450, 1450, 1400]);
  const height = travel(frame, [130, 225, 750, 820, 1050, 1130, 1380, 1450, 1640, 1710], [490, 510, 510, 670, 670, 754, 754, 600, 600, 630]);
  const top = travel(frame, [130, 225, 750, 820, 1050, 1130, 1380, 1450, 1640, 1710], [355, 292, 292, 238, 238, 186, 186, 258, 258, 250]);
  // Close in to read an operation, pull out to see its consequences.
  const camera = travel(frame,
    [130, 212, 278, 360, 450, 494, 548, 618, 750, 840, 1050, 1140, 1380, 1480, 1530, 1600, 1650, 1720, 1800, 1880, 1908, 1965],
    [1.75, 1.75, 1.75, 1, 1, 1.45, 1.45, 1, 1, 0.96, 0.96, 1, 1, 1, 1.12, 1.12, 1, 1.22, 1.1, 1, 1, 0.92]);
  return <AbsoluteFill className="kn-root">
    <Sequence name="Opening promise" from={0} durationInFrames={155}><Opening frame={frame} /></Sequence>
    <Headline frame={frame} start={345} end={448}>One step.</Headline>
    <Headline frame={frame} start={610} end={748}>Let it run.</Headline>
    <Headline frame={frame} start={840} end={1040}>Now, explore wider.</Headline>
    <Headline frame={frame} start={1080} end={1190}>See what stays.</Headline>
    <Headline frame={frame} start={1400} end={1490}>The next move is yours.</Headline>
    <Headline frame={frame} start={1650} end={1720}>Already in your workflow.</Headline>
    <div className="kn-stage" style={{left: (1920 - width) / 2 + (frame < 750 ? Math.max(0, camera - 1) * 240 : 0), top, width, height, scale: camera, opacity: progress(frame, 130, 169) * (1 - progress(frame, 1910, 1952)), boxShadow: `0 ${22 + (camera - 1) * 65}px ${66 + (camera - 1) * 100}px rgba(22,34,48,0.09), 0 3px 9px rgba(22,34,48,0.025)`}}>
      <WindowBar frame={frame} />
      <div className="kn-stage-body">
        <Sequence name="Terminal: step to run to parallel" from={130} durationInFrames={980} layout="none"><TerminalJourney frame={frame} /></Sequence>
        <Sequence name="Recorded dashboard: inspect evidence" from={1080} durationInFrames={360} layout="none"><EvidenceJourney frame={frame} /></Sequence>
        <Sequence name="Human chooses: explicit promotion" from={1400} durationInFrames={280} layout="none"><HumanJourney frame={frame} /></Sequence>
        <Sequence name="Skill enters the coding agent" from={1650} durationInFrames={300} layout="none"><AgentJourney frame={frame} /></Sequence>
      </div>
    </div>
    <Sequence name="Closing promise" from={1908} durationInFrames={252}><Closing frame={frame} /></Sequence>
    {showSubtitles && narration.map(line => <Sequence key={line.from} from={line.from} durationInFrames={line.to - line.from} name="Narration guide"><div className="kn-subtitle">{line.text}</div></Sequence>)}
    {voiceOverSrc ? <Audio src={voiceOverSrc} /> : null}
    {musicSrc ? <Audio src={musicSrc} volume={0.2} /> : soundDesign ? <Audio src={staticFile('audio/keynote/score.wav')} volume={0.65} /> : null}
    {soundEffectsSrc ? <Audio src={soundEffectsSrc} volume={0.5} /> : soundDesign ? <Audio src={staticFile('audio/keynote/cues.wav')} volume={0.7} /> : null}
  </AbsoluteFill>;
};
