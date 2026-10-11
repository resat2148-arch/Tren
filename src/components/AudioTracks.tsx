import React from 'react';
import {Audio, Sequence, staticFile} from 'remotion';
import {SFX_FILES} from '../sfx';
import type {FilmTimeline} from '../film';
import type {SfxCue} from '../types';

const cueSeq = (key: string, from: number, fps: number, cue: SfxCue) => {
  const file = SFX_FILES[cue.sound];
  if (!file) return null;
  return (
    <Sequence key={key} from={from + Math.round((cue.at ?? 0) * fps)}
      durationInFrames={cue.length ? Math.round(cue.length * fps) : undefined} layout="none">
      <Audio src={staticFile(file)} volume={cue.volume ?? 1} loop={cue.loop} />
    </Sequence>
  );
};

// Platzhalter-Tonspur: spielt nur, was in src/sfx.ts bzw. per "voice" an einer Zeile eingetragen ist.
export const AudioTracks: React.FC<{tl: FilmTimeline; cliffSfx?: SfxCue[]}> = ({tl, cliffSfx}) => (
  <>
    {tl.shots.flatMap((s) => [
      ...(s.sfx ?? []).map((cue, i) => cueSeq(`sfx-${s.id}-${i}`, s.from, tl.fps, cue)),
      ...(s.lines ?? []).map((ln, i) =>
        ln.voice ? (
          <Sequence key={`voice-${s.id}-${i}`} from={s.from + Math.round(ln.t * tl.fps)} layout="none">
            <Audio src={staticFile(ln.voice)} />
          </Sequence>
        ) : null,
      ),
    ])}
    {(cliffSfx ?? []).map((cue, i) => cueSeq(`sfx-cliff-${i}`, tl.cliffFrom, tl.fps, cue))}
  </>
);
