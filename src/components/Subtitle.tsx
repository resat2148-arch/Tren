import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';

// Dialog-Untertitel mit Sprechername; vo = Gedanken/Tagebuch von Platz 47 (kursiv, Amber-Rand).
export const Subtitle: React.FC<{speaker: string; text: string; frames: number; vo?: boolean}> = ({
  speaker,
  text,
  frames,
  vo,
}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 4, frames - 4, frames], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const words = text.split(' ');
  const shown = vo ? interpolate(frame, [2, frames * 0.65], [0, words.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : words.length;
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        right: 140,
        top: vo ? 1160 : 1300,
        opacity: o,
        display: 'flex',
        flexDirection: 'column',
        alignItems: vo ? 'flex-start' : 'center',
      }}
    >
      <div
        style={{
          fontFamily: theme.fontSans,
          fontWeight: 800,
          fontSize: 24,
          letterSpacing: 3,
          color: theme.amber,
          marginBottom: 10,
          textShadow: '0 2px 10px rgba(0,0,0,0.8)',
        }}
      >
        {vo ? `${speaker.toUpperCase()} · GEDANKEN` : speaker.toUpperCase()}
      </div>
      <div
        style={{
          padding: vo ? '18px 24px' : '14px 24px',
          borderRadius: 16,
          background: vo ? 'rgba(10,12,16,0.72)' : 'rgba(0,0,0,0.62)',
          borderLeft: vo ? `6px solid ${theme.amber}` : 'none',
          fontFamily: vo ? theme.fontMono : theme.fontSans,
          fontWeight: vo ? 400 : 700,
          fontStyle: vo ? 'italic' : 'normal',
          fontSize: vo ? 38 : 52,
          lineHeight: 1.3,
          color: '#FFFFFF',
          textAlign: vo ? 'left' : 'center',
        }}
      >
        {words.map((w, i) => (
          <span key={i} style={{opacity: Math.max(0, Math.min(1, shown - i))}}>
            {w}
            {i < words.length - 1 ? ' ' : ''}
          </span>
        ))}
      </div>
    </div>
  );
};
