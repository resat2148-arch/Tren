import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {CardFrame} from './Card';
import {theme} from '../theme';

// Tagebuch von Platz 47 mit Schreibmaschinen-Effekt.
// Der noch nicht getippte Rest ist unsichtbar vorhanden, damit der Zeilenumbruch nicht springt.
export const DiaryText: React.FC<{text: string; heading: string; frames: number; accent?: boolean}> = ({
  text,
  heading,
  frames: durationInFrames,
  accent,
}) => {
  const frame = useCurrentFrame();
  const typingEnd = Math.max(12, Math.round(durationInFrames * 0.6));
  const chars = Math.floor(
    interpolate(frame, [4, typingEnd], [0, text.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
  );
  const done = chars >= text.length;
  const cursorOn = !done || Math.floor(frame / 12) % 2 === 0;

  return (
    <CardFrame frames={durationInFrames}>
      <div
        style={{
          padding: '30px 36px 36px',
          borderRadius: 24,
          background: '#10141A',
          border: `2px solid ${accent ? theme.amberDim : theme.panelBorder}`,
          boxShadow: '0 24px 60px rgba(0,0,0,0.5)',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            marginBottom: 20,
            fontFamily: theme.fontSans,
            fontWeight: 600,
            fontSize: 22,
            letterSpacing: 4,
            color: accent ? theme.amber : theme.muted,
          }}
        >
          <span style={{width: 12, height: 12, borderRadius: 6, background: theme.amber}} />
          {heading.toUpperCase()}
        </div>
        <div
          style={{
            fontFamily: theme.fontMono,
            fontWeight: 400,
            fontSize: 39,
            lineHeight: 1.42,
            color: theme.text,
          }}
        >
          <span>{text.slice(0, chars)}</span>
          <span style={{position: 'relative'}}>
            <span
              style={{
                position: 'absolute',
                left: 2,
                top: '0.12em',
                width: '0.52em',
                height: '1.1em',
                background: theme.amber,
                opacity: cursorOn ? 1 : 0,
              }}
            />
          </span>
          <span style={{opacity: 0}}>{text.slice(chars)}</span>
        </div>
      </div>
    </CardFrame>
  );
};
