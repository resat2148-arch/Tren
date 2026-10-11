import React from 'react';
import {Audio, Sequence, staticFile} from 'remotion';
import {SFX_FILES} from '../sfx';
import type {Timeline} from '../timeline';

// Platzhalter-Tonspur: spielt nur Dateien ab, die in src/sfx.ts bzw. per "voice" eingetragen sind.
export const AudioTracks: React.FC<{tl: Timeline}> = ({tl}) => (
  <>
    {tl.scenes.flatMap((s) => {
      const out: React.ReactNode[] = [];
      (s.sfx ?? []).forEach((cue, i) => {
        const file = SFX_FILES[cue.sound];
        if (!file) return;
        out.push(
          <Sequence
            key={`sfx-${s.index}-${i}`}
            from={s.from + Math.round((cue.at ?? 0) * tl.fps)}
            durationInFrames={cue.length ? Math.round(cue.length * tl.fps) : undefined}
            layout="none"
          >
            <Audio src={staticFile(file)} volume={cue.volume ?? 1} loop={cue.loop} />
          </Sequence>,
        );
      });
      if (s.voice) {
        out.push(
          <Sequence key={`voice-${s.index}`} from={s.from + Math.round(0.2 * tl.fps)} layout="none">
            <Audio src={staticFile(s.voice)} />
          </Sequence>,
        );
      }
      return out;
    })}
  </>
);
