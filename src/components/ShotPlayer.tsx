import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {theme} from '../theme';
import type {RenderManifest, Shot} from '../types';

// Spielt die in Blender gerenderte Bildfolge eines Shots ab (public/renders/<folge>/<shot>/0001.jpg …).
// Fehlt der Render noch, erscheint eine Storyboard-Tafel mit der Szenenbeschreibung.
export const ShotPlayer: React.FC<{episodeId: string; shot: Shot; manifest: RenderManifest}> = ({
  episodeId,
  shot,
  manifest,
}) => {
  const frame = useCurrentFrame();
  const info = manifest.shots[shot.id];
  if (!info) {
    return (
      <AbsoluteFill
        style={{
          background: '#14181E',
          justifyContent: 'center',
          alignItems: 'center',
          padding: 90,
          textAlign: 'center',
          fontFamily: theme.fontSans,
          color: theme.muted,
        }}
      >
        <div style={{fontFamily: theme.fontMono, fontSize: 44, color: theme.amber}}>{shot.id.toUpperCase()}</div>
        <div style={{fontSize: 40, marginTop: 30, lineHeight: 1.4}}>{shot.note ?? 'noch nicht gerendert'}</div>
        <div style={{fontSize: 28, marginTop: 40}}>Render fehlt – npm run shots</div>
      </AbsoluteFill>
    );
  }
  const step = info.step || 1;
  const f = Math.min(info.frames, 1 + Math.floor(frame / step) * step);
  const src = staticFile(`renders/${episodeId}/${shot.id}/${String(f).padStart(4, '0')}.jpg`);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Img src={src} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
    </AbsoluteFill>
  );
};
