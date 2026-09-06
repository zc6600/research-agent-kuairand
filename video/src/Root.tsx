import React from 'react';
import {Composition} from 'remotion';
import {SciOdysseyFilm} from './compositions/launch/SciOdysseyFilm';
import {SciOdysseyUXFilm} from './compositions/ux/SciOdysseyUXFilm';
import {SciOdysseyUXWorkflowFilm} from './compositions/ux/SciOdysseyUXWorkflowFilm';
import {SciOdysseyKeynoteFilm} from './compositions/keynote/SciOdysseyKeynoteFilm';
import {SciOdysseyProductFilm} from './compositions/product/SciOdysseyProductFilm';
import {SciOdysseyProductFilmV2} from './compositions/product-v2/SciOdysseyProductFilmV2';

export const RemotionRoot: React.FC = () => {
  return (
    <>
    <Composition
      id="SciOdysseyFilm"
      component={SciOdysseyFilm}
      durationInFrames={2250}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{}}
    />
    <Composition
      id="SciOdysseyUXFilm"
      component={SciOdysseyUXFilm}
      durationInFrames={1890}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{}}
    />
    <Composition
      id="SciOdysseyUXWorkflowFilm"
      component={SciOdysseyUXWorkflowFilm}
      durationInFrames={2250}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{}}
    />
    <Composition
      id="SciOdysseyKeynoteFilm"
      component={SciOdysseyKeynoteFilm}
      durationInFrames={2160}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{soundDesign: true, showSubtitles: false}}
    />
    <Composition
      id="SciOdysseyProductFilm"
      component={SciOdysseyProductFilm}
      durationInFrames={5400}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{soundDesign: true}}
    />
    <Composition
      id="SciOdysseyProductFilmV2"
      component={SciOdysseyProductFilmV2}
      durationInFrames={5400}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{soundDesign: true}}
    />
    </>
  );
};
