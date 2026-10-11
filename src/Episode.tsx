import React, {useMemo} from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {AudioTracks} from './components/AudioTracks';
import {CliffhangerCard} from './components/CliffhangerCard';
import {DayCounter} from './components/DayCounter';
import {DelayBoard} from './components/DelayBoard';
import {DiaryText} from './components/DiaryText';
import {Durchsage} from './components/Durchsage';
import {ResourceBars} from './components/ResourceBars';
import {TrainMap} from './components/TrainMap';
import {theme} from './theme';
import {activeScene, buildTimeline, stateAt, type TimedScene} from './timeline';
import type {Episode, Resources} from './types';

const wagenName = (w: TimedScene['wagen']) => (w === '1. Klasse' ? '1. Klasse' : `Wagen ${w}`);

const SceneCard: React.FC<{scene: TimedScene}> = ({scene}) => {
  switch (scene.type) {
    case 'diary':
      return <DiaryText text={scene.text} frames={scene.frames} heading={`Platz 47${scene.clock ? ` · ${scene.clock}` : ''}`} />;
    case 'mapEvent':
      return <DiaryText text={scene.text} frames={scene.frames} heading={wagenName(scene.wagen)} accent />;
    case 'durchsage':
      return <Durchsage text={scene.text} frames={scene.frames} urgent={scene.urgent} />;
    default:
      return null;
  }
};

export const EpisodeVideo: React.FC<{episode: Episode}> = ({episode}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tl = useMemo(() => buildTimeline(episode, fps), [episode, fps]);
  const st = stateAt(episode, tl, frame);
  const prev = stateAt(episode, tl, Math.max(0, frame - 1));
  const scene = activeScene(tl, frame);
  const cliff = tl.scenes[tl.scenes.length - 1];

  const max: Resources = {...episode.resources, wlan: 4, ...episode.resourcesMax};
  const changing = Object.fromEntries(
    (Object.keys(st.resources) as (keyof Resources)[]).map((k) => [k, Math.abs(st.resources[k] - prev.resources[k]) > 0.01]),
  );

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse 120% 70% at 50% 0%, ${theme.bgTop} 0%, ${theme.bg} 60%)`,
        overflow: 'hidden',
      }}
    >
      <DelayBoard
        route={episode.route}
        delay={st.delay}
        delayChanging={Math.abs(st.delay - prev.delay) > 0.01}
        clock={st.clock}
        ticker={st.ticker}
        urgent={scene.type === 'durchsage' && !!scene.urgent}
      />
      <TrainMap
        distance={st.distance}
        speed={st.speed}
        night={st.night}
        location={st.location}
        destination={episode.route.to}
        highlight={scene.wagen ? {...scene, wagen: scene.wagen, local: frame - scene.from} : null}
      />
      <ResourceBars values={st.resources} max={max} changing={changing} />

      {tl.scenes.map((s) => (
        <Sequence key={s.index} from={s.from} durationInFrames={s.frames} layout="none">
          <SceneCard scene={s} />
        </Sequence>
      ))}

      <DayCounter day={episode.day} introFrames={tl.introFrames} route={episode.route} subtitle={episode.intro.subtitle} />

      <Sequence from={cliff.from} durationInFrames={cliff.frames} layout="none">
        {cliff.type === 'cliffhanger' && <CliffhangerCard lines={cliff.lines} punch={cliff.punch} teaser={cliff.teaser} />}
      </Sequence>

      <AudioTracks tl={tl} />
    </AbsoluteFill>
  );
};
