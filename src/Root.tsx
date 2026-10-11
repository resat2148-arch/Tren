import React from 'react';
import {Composition} from 'remotion';
import {EpisodeVideo} from './Episode';
import {EPISODES} from './episodes';
import {loadFonts} from './fonts';
import {buildTimeline} from './timeline';

const FPS = 30;

loadFonts();

export const Root: React.FC = () => (
  <>
    {EPISODES.map(({id, data}) => (
      <Composition
        key={id}
        id={id}
        component={EpisodeVideo}
        durationInFrames={buildTimeline(data, FPS).totalFrames}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{episode: data}}
      />
    ))}
  </>
);
