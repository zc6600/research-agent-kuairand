import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {ProductOpeningScene} from './scenes/OpeningScene';
import {ProductProblemScene} from './scenes/ProblemScene';
import {ProductIdentityScene} from './scenes/IdentityScene';
import {ProductHowToScene} from './scenes/HowToScene';
import {ProductKeynoteScene} from './scenes/KeynoteScene';
import {ProductDashboardScene} from './scenes/DashboardScene';
import {ProductCompareScene} from './scenes/CompareScene';
import {ProductParallelHumanScene} from './scenes/ParallelHumanScene';
import {ProductProofScene} from './scenes/ProofScene';
import {ProductClosingScene} from './scenes/ClosingScene';
import './product.css';

export type ProductFilmProps = {
  voiceOverSrc?: string;
  musicSrc?: string;
  soundEffectsSrc?: string;
  soundDesign?: boolean;
};
/**
 * Three-minute product film. Each sequence is a chapter with its own local
 * clock, which keeps the scenes editable in Remotion while preserving one
 * continuous camera language across the full film.
 */
export const SciOdysseyProductFilm: React.FC<ProductFilmProps> = ({
  voiceOverSrc,
  musicSrc,
  soundEffectsSrc,
  soundDesign = true,
}) => {
  return (
    <AbsoluteFill className="product-film-root">
      <Sequence name="01 / Meet SciOdyssey" from={0} durationInFrames={450}>
        <ProductOpeningScene />
      </Sequence>
      <Sequence name="02 / The problem" from={450} durationInFrames={510}>
        <ProductProblemScene />
      </Sequence>
      <Sequence name="03 / What SciOdyssey is" from={960} durationInFrames={420}>
        <ProductIdentityScene />
      </Sequence>
      <Sequence name="04 / How to use it" from={1380} durationInFrames={660}>
        <ProductHowToScene />
      </Sequence>
      <Sequence name="05 / Keynote cut" from={2040} durationInFrames={900}>
        <ProductKeynoteScene />
      </Sequence>
      <Sequence name="06 / Observe the run" from={2940} durationInFrames={480}>
        <ProductDashboardScene />
      </Sequence>
      <Sequence name="07 / Why it is different" from={3420} durationInFrames={480}>
        <ProductCompareScene />
      </Sequence>
      <Sequence name="08 / Breadth with a human gate" from={3900} durationInFrames={510}>
        <ProductParallelHumanScene />
      </Sequence>
      <Sequence name="09 / Evidence, not promises" from={4410} durationInFrames={450}>
        <ProductProofScene />
      </Sequence>
      <Sequence name="10 / Start your odyssey" from={4860} durationInFrames={540}>
        <ProductClosingScene />
      </Sequence>
      {voiceOverSrc ? <Audio src={voiceOverSrc} /> : null}
      {musicSrc ? <Audio src={musicSrc} volume={0.24} loop /> : soundDesign ? <Audio src={staticFile('audio/keynote/score.wav')} volume={0.38} loop /> : null}
      {soundEffectsSrc ? <Audio src={soundEffectsSrc} volume={0.42} loop /> : soundDesign ? <Audio src={staticFile('audio/keynote/cues.wav')} volume={0.26} loop /> : null}
    </AbsoluteFill>
  );
};
