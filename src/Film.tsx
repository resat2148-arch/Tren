import React, {useMemo} from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {AudioTracks} from './components/AudioTracks';
import {CliffhangerCard} from './components/CliffhangerCard';
import {Durchsage} from './components/Durchsage';
import {Hud} from './components/Hud';
import {ShotPlayer} from './components/ShotPlayer';
import {Slug} from './components/Slug';
import {Subtitle} from './components/Subtitle';
import {TitleCard} from './components/TitleCard';
import {buildFilm, clockAt, delayAt, NAMES} from './film';
import type {FilmEpisode, RenderManifest} from './types';

export type FilmProps = {episodeId: string; episode: FilmEpisode; manifest: RenderManifest};

export const Film: React.FC<FilmProps> = ({episodeId, episode, manifest}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tl = useMemo(() => buildFilm(episode, fps), [episode, fps]);
  const first = tl.shots[0];
  const delay = delayAt(tl, frame);
  const hudIn = first.titleCard
    ? interpolate(frame, [first.frames - 10, first.frames + 4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
    : 1;
  const hudOut = interpolate(frame, [tl.cliffFrom, tl.cliffFrom + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{background: '#000'}}>
      {tl.shots.map((s) => (
        <Sequence key={s.id} from={s.from} durationInFrames={s.frames}>
          <ShotPlayer episodeId={episodeId} shot={s} manifest={manifest} />
        </Sequence>
      ))}

      <Hud
        day={episode.day}
        route={episode.route}
        clock={clockAt(tl, frame)}
        delay={delay.value}
        changing={delay.changing}
        since={delay.since}
        visible={Math.min(hudIn, hudOut)}
      />

      {tl.shots.map((s) => (
        <React.Fragment key={`ov-${s.id}`}>
          {s.titleCard && (
            <Sequence from={s.from} durationInFrames={s.frames} layout="none">
              <TitleCard day={episode.day} route={episode.route} subtitle={episode.intro.subtitle} frames={s.frames} />
            </Sequence>
          )}
          {s.slug && (
            <Sequence from={s.from} durationInFrames={Math.min(s.frames, 75)} layout="none">
              <Slug text={s.slug} />
            </Sequence>
          )}
          {(s.lines ?? []).map((ln, i) => {
            const from = s.from + Math.round(ln.t * fps);
            const frames = Math.max(8, Math.round(ln.d * fps));
            return (
              <Sequence key={`${s.id}-l${i}`} from={from} durationInFrames={frames} layout="none">
                {ln.kind === 'durchsage' ? (
                  <Durchsage text={ln.text} frames={frames} urgent={ln.urgent} />
                ) : (
                  <Subtitle speaker={NAMES[ln.who] ?? ln.who} text={ln.text} frames={frames} vo={ln.kind === 'vo'} />
                )}
              </Sequence>
            );
          })}
        </React.Fragment>
      ))}

      <Sequence from={tl.cliffFrom} durationInFrames={tl.cliffFrames} layout="none">
        <CliffhangerCard lines={episode.cliffhanger.lines} punch={episode.cliffhanger.punch} teaser={episode.cliffhanger.teaser} />
      </Sequence>

      <AudioTracks tl={tl} cliffSfx={episode.cliffhanger.sfx} />
    </AbsoluteFill>
  );
};
