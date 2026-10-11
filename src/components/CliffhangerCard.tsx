import React from 'react';
import {Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {theme} from '../theme';

// Letzte Sekunden: Bild wird schwarz, Zeilen nacheinander, dann die Pointe.
export const CliffhangerCard: React.FC<{lines: string[]; punch: string; teaser: string}> = ({lines, punch, teaser}) => {
  const frame = useCurrentFrame();
  const dark = interpolate(frame, [0, 10], [0, 0.94], {extrapolateRight: 'clamp'});
  const punchAt = 8 + lines.length * 11 + 4;
  const punchT = interpolate(frame, [punchAt, punchAt + 7], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.back(2.2)),
  });
  const punchShake = frame >= punchAt && frame < punchAt + 14 ? (random(`p-${frame}`) - 0.5) * 18 : 0;
  const teaserO = interpolate(frame, [punchAt + 16, punchAt + 24], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{position: 'absolute', inset: 0, background: `rgba(3,4,6,${dark})`}}>
      <div
        style={{
          position: 'absolute',
          top: 620,
          left: 60,
          right: 60,
          textAlign: 'center',
          fontFamily: theme.fontSans,
          color: theme.text,
        }}
      >
        {lines.map((line, i) => {
          const at = 8 + i * 11;
          const o = interpolate(frame, [at, at + 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          return (
            <div
              key={i}
              style={{
                fontWeight: 600,
                fontSize: 72,
                lineHeight: 1.25,
                opacity: o,
                transform: `translateY(${(1 - o) * 20}px)`,
              }}
            >
              {line}
            </div>
          );
        })}
        <div
          style={{
            marginTop: 50,
            fontWeight: 800,
            fontSize: 190,
            letterSpacing: -4,
            color: theme.amber,
            textShadow: `0 0 40px ${theme.amberGlow}`,
            opacity: punchT > 0 ? 1 : 0,
            transform: `translateX(${punchShake}px) scale(${0.4 + 0.6 * punchT})`,
          }}
        >
          {punch}
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          top: 1300,
          width: '100%',
          textAlign: 'center',
          opacity: teaserO,
          fontFamily: theme.fontSans,
          fontWeight: 600,
          fontSize: 40,
          letterSpacing: 2,
          color: theme.muted,
        }}
      >
        {teaser}
      </div>
    </div>
  );
};
