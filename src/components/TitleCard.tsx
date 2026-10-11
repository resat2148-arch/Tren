import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Arrow} from './Led';
import {theme} from '../theme';

// Großes "TAG X" über dem ersten Shot, dann Übergabe an das HUD.
export const TitleCard: React.FC<{day: number; route: {from: string; to: string}; subtitle: string; frames: number}> = ({
  day,
  route,
  subtitle,
  frames,
}) => {
  const frame = useCurrentFrame();
  const inT = interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.8))});
  const outT = interpolate(frame, [frames - 14, frames - 2], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        background: `linear-gradient(180deg, rgba(5,7,10,${0.55 * outT}) 0%, rgba(5,7,10,${0.15 * outT}) 45%, rgba(5,7,10,${0.6 * outT}) 100%)`,
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 640,
          width: '100%',
          textAlign: 'center',
          opacity: outT,
          transform: `scale(${0.8 + 0.2 * inT})`,
          fontFamily: theme.fontSans,
          color: theme.text,
          textShadow: '0 6px 40px rgba(0,0,0,0.6)',
        }}
      >
        <div style={{fontSize: 230, fontWeight: 800, letterSpacing: -6, lineHeight: 1}}>TAG {day}</div>
        <div style={{marginTop: 30, fontSize: 64, fontWeight: 800, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 20}}>
          {route.from}
          <Arrow size={60} color={theme.amber} />
          {route.to}
        </div>
        <div style={{marginTop: 18, fontSize: 38, color: '#D6D9DE'}}>{subtitle}</div>
      </div>
    </div>
  );
};
