import React from 'react';
import {interpolate, random, useCurrentFrame} from 'remotion';
import {CardFrame} from './Card';
import {Led} from './Led';
import {theme} from '../theme';

const Speaker: React.FC<{color: string; frame: number}> = ({color, frame}) => (
  <svg width={64} height={48} viewBox="0 0 64 48">
    <path d="M4 17 H15 L29 5 V43 L15 31 H4 Z" fill={color} />
    {[0, 1, 2].map((i) => {
      const phase = ((frame / 6 + i) % 3) / 3;
      return (
        <path
          key={i}
          d={`M${36 + i * 9} ${14 - i * 4} Q${44 + i * 11} 24 ${36 + i * 9} ${34 + i * 4}`}
          stroke={color}
          strokeWidth={4}
          fill="none"
          strokeLinecap="round"
          opacity={0.25 + 0.75 * (1 - phase)}
        />
      );
    })}
  </svg>
);

// Ansage-Blase. Wörter erscheinen im Sprechtempo; "urgent" blinkt und wackelt.
export const Durchsage: React.FC<{text: string; frames: number; urgent?: boolean}> = ({
  text,
  frames: durationInFrames,
  urgent,
}) => {
  const frame = useCurrentFrame();
  const words = text.split(' ');
  const revealEnd = Math.max(10, Math.round(durationInFrames * 0.55));
  const shown = interpolate(frame, [6, revealEnd], [0, words.length], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const color = urgent ? theme.alert : theme.amber;
  const blinkOn = !urgent || Math.floor(frame / 7) % 2 === 0;
  const shake = urgent ? (random(`ds-${frame}`) - 0.5) * 10 * interpolate(frame, [0, 30], [1, 0.3], {extrapolateRight: 'clamp'}) : 0;
  const glitch = frame < 6 ? (random(`g-${frame}`) - 0.5) * 16 : 0;

  return (
    <CardFrame frames={durationInFrames}>
      <div style={{position: 'relative', transform: `translateX(${shake + glitch}px)`}}>
        {/* Sprechblasen-Spitze nach oben zum Zug */}
        <div
          style={{
            position: 'absolute',
            left: 70,
            top: -20,
            width: 0,
            height: 0,
            borderLeft: '22px solid transparent',
            borderRight: '22px solid transparent',
            borderBottom: `22px solid ${color}`,
          }}
        />
        <div
          style={{
            padding: '28px 36px 36px',
            borderRadius: 26,
            background: urgent ? 'linear-gradient(180deg, #2A130C, #160C08)' : 'linear-gradient(180deg, #1E1810, #120F0B)',
            border: `3px solid ${color}`,
            boxShadow: `0 0 ${urgent && blinkOn ? 60 : 30}px ${urgent ? 'rgba(255,91,46,0.45)' : 'rgba(255,159,28,0.25)'}`,
          }}
        >
          <div style={{display: 'flex', alignItems: 'center', gap: 18, marginBottom: 22, opacity: blinkOn ? 1 : 0.35}}>
            <Speaker color={color} frame={frame} />
            <Led size={34} color={color} dots={false}>
              DURCHSAGE
            </Led>
          </div>
          <div style={{fontFamily: theme.fontSans, fontWeight: 600, fontSize: urgent ? 58 : 44, lineHeight: 1.3, color: theme.text}}>
            {words.map((w, i) => {
              const o = Math.max(0, Math.min(1, shown - i));
              return (
                <span key={i} style={{opacity: o}}>
                  {w}
                  {i < words.length - 1 ? ' ' : ''}
                </span>
              );
            })}
          </div>
        </div>
      </div>
    </CardFrame>
  );
};
