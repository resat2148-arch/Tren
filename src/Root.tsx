import React from 'react';
import {Composition, staticFile} from 'remotion';
import {Film, type FilmProps} from './Film';
import {EPISODES} from './episodes';
import {buildFilm} from './film';
import {loadFonts} from './fonts';
import type {RenderManifest} from './types';

loadFonts();

const loadManifest = async (id: string): Promise<RenderManifest> => {
  try {
    const res = await fetch(staticFile(`renders/${id}/manifest.json`));
    if (!res.ok) return {shots: {}};
    return (await res.json()) as RenderManifest;
  } catch {
    return {shots: {}};
  }
};

export const Root: React.FC = () => (
  <>
    {EPISODES.map(({id, data}) => (
      <Composition
        key={id}
        id={id}
        component={Film}
        durationInFrames={buildFilm(data, data.fps).totalFrames}
        fps={data.fps}
        width={1080}
        height={1920}
        defaultProps={{episodeId: id, episode: data, manifest: {shots: {}}} as FilmProps}
        calculateMetadata={async ({props}) => ({props: {...props, manifest: await loadManifest(props.episodeId)}})}
      />
    ))}
  </>
);
