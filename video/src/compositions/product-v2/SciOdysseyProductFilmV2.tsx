import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {V2RevealScene} from './scenes/RevealScene';
import {V2ProductMapScene} from './scenes/ProductMapScene';
import {V2FirstUseScene} from './scenes/FirstUseScene';
import {V2KeynoteCutScene} from './scenes/KeynoteCutScene';
import {V2ParallelScene} from './scenes/ParallelScene';
import {V2RuntimeScene} from './scenes/RuntimeScene';
import {V2ProofScene} from './scenes/ProofScene';
import {V2ResumeScene} from './scenes/ResumeScene';
import {V2FinalScene} from './scenes/FinalScene';
import {KineticCut} from './v2-components';
import {V2C} from './v2-motion';
import './v2.css';

export type ProductFilmV2Props = {
  voiceOverSrc?: string;
  musicSrc?: string;
  soundEffectsSrc?: string;
  soundDesign?: boolean;
};

const cutPoints = [540, 1290, 2130, 2880, 3450, 4170, 4890, 5190];

const KineticCuts: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill className="v2-cut-layer">
      {cutPoints.map((at, index) => <KineticCut frame={frame} at={at - 6} color={index % 2 === 0 ? V2C.cyan : V2C.violet} key={at} />)}
    </AbsoluteFill>
  );
};

/** V2 product film: one continuous question moving through a research world. */
export const SciOdysseyProductFilmV2: React.FC<ProductFilmV2Props> = ({voiceOverSrc, musicSrc, soundEffectsSrc, soundDesign = true}) => {
  return (
    <AbsoluteFill className="v2-film">
      <Sequence name="01 / Product reveal" from={0} durationInFrames={540}><V2RevealScene /></Sequence>
      <Sequence name="02 / Product map" from={540} durationInFrames={750}><V2ProductMapScene /></Sequence>
      <Sequence name="03 / Keynote cut" from={1290} durationInFrames={840}><V2KeynoteCutScene /></Sequence>
      <Sequence name="04 / Parallel search" from={2130} durationInFrames={750}><V2ParallelScene /></Sequence>
      <Sequence name="05 / Runtime" from={2880} durationInFrames={570}><V2RuntimeScene /></Sequence>
      <Sequence name="06 / Proof" from={3450} durationInFrames={720}><V2ProofScene /></Sequence>
      <Sequence name="07 / How to use" from={4170} durationInFrames={720}><V2FirstUseScene /></Sequence>
      <Sequence name="08 / Resume" from={4890} durationInFrames={300}><V2ResumeScene /></Sequence>
      <Sequence name="09 / Final" from={5190} durationInFrames={210}><V2FinalScene /></Sequence>
      <KineticCuts />
      {voiceOverSrc ? <Audio src={voiceOverSrc} /> : null}
      {musicSrc ? <Audio src={musicSrc} volume={0.32} loop /> : soundDesign ? <Audio src={staticFile('audio/keynote/score.wav')} volume={0.36} loop loopVolumeCurveBehavior="extend" /> : null}
      {soundEffectsSrc ? <Audio src={soundEffectsSrc} volume={0.38} loop /> : soundDesign ? <Audio src={staticFile('audio/keynote/cues.wav')} volume={0.24} loop loopVolumeCurveBehavior="extend" /> : null}
    </AbsoluteFill>
  );
};
