import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Arrow} from './Led';
import {layout, theme} from '../theme';

// Groß in der Mitte während des Intros, danach klein oben links.
export const DayCounter: React.FC<{
  day: number;
  introFrames: number;
  route: {from: string; to: string};
  subtitle: string;
}> = ({day, introFrames, route, subtitle}) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [introFrames - 14, introFrames + 4], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const pop = interpolate(frame, [0, 8], [0.82, 1], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.back(2)),
  });
  const lerp = (a: number, b: number) => a + (b - a) * t;

  const fontSize = lerp(250, 40);
  const cx = lerp(540, layout.side + 92);
  const cy = lerp(800, layout.pillTop + 34);
  const scrim = interpolate(frame, [introFrames - 10, introFrames + 6], [0.86, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const subOpacity = interpolate(frame, [6, 14, introFrames - 14, introFrames - 6], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <>
      <div style={{position: 'absolute', inset: 0, background: `rgba(5,7,10,${scrim})`}} />
      <div
        style={{
          position: 'absolute',
          left: cx,
          top: cy,
          transform: `translate(-50%, -50%) scale(${t < 1 ? pop : 1})`,
          padding: `${lerp(0, 10)}px ${lerp(0, 26)}px`,
          borderRadius: 999,
          background: `rgba(255,159,28,${t})`,
          color: t > 0.5 ? theme.ledPanel : theme.text,
          fontFamily: theme.fontSans,
          fontWeight: 800,
          fontSize,
          letterSpacing: -fontSize * 0.02,
          lineHeight: 1,
          whiteSpace: 'nowrap',
        }}
      >
        TAG {day}
      </div>
      <div
        style={{
          position: 'absolute',
          left: layout.side + 200,
          top: layout.pillTop + 20,
          opacity: t,
          fontFamily: theme.fontSans,
          fontWeight: 600,
          fontSize: 26,
          letterSpacing: 4,
          color: theme.muted,
        }}
      >
        GESTRANDET IM ZUG
      </div>
      <div
        style={{
          position: 'absolute',
          top: 980,
          width: '100%',
          textAlign: 'center',
          opacity: subOpacity,
          fontFamily: theme.fontSans,
          color: theme.text,
        }}
      >
        <div style={{fontSize: 68, fontWeight: 800, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 22}}>
          {route.from}
          <Arrow size={64} color={theme.amber} />
          {route.to}
        </div>
        <div style={{fontSize: 40, fontWeight: 400, color: theme.muted, marginTop: 22}}>{subtitle}</div>
      </div>
    </>
  );
};
