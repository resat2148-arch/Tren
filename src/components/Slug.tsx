import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';

// Ortsangabe wie im Film ("Wagen 7 · Bordbistro · 20:48"), tippt sich ein und blendet aus.
export const Slug: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const chars = Math.floor(interpolate(frame, [3, 3 + text.length * 0.9], [0, text.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const o = interpolate(frame, [0, 4, 62, 72], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div
      style={{
        position: 'absolute',
        left: 48,
        top: 330,
        opacity: o,
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        padding: '10px 18px',
        borderLeft: `6px solid ${theme.amber}`,
        background: 'rgba(7,9,12,0.7)',
        fontFamily: theme.fontMono,
        fontWeight: 700,
        fontSize: 32,
        letterSpacing: 1,
        color: theme.text,
      }}
    >
      {text.slice(0, chars).toUpperCase()}
      <span style={{width: 16, height: 30, background: theme.amber, opacity: Math.floor(frame / 8) % 2 ? 0 : 1}} />
    </div>
  );
};
