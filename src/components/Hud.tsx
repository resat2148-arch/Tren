import React from 'react';
import {Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {Arrow, Led} from './Led';
import {theme} from '../theme';

// Kleine LED-Anzeige oben links: Tag, Strecke, Uhrzeit, Verspätung.
// Wenn die Verspätung steigt, springt sie kurz groß in die Bildmitte.
export const Hud: React.FC<{
  day: number;
  route: {from: string; to: string};
  clock: string;
  delay: number;
  changing: boolean;
  since: number;
  visible: number;
}> = ({day, route, clock, delay, changing, since, visible}) => {
  const frame = useCurrentFrame();
  const pop = interpolate(since, [0, 8, 45, 60], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const flicker = changing ? 0.75 + 0.25 * random(`hud-${frame}`) : 1;
  const scale = 1 + pop * 0.9;
  return (
    <div style={{position: 'absolute', left: 48, top: 96, opacity: visible}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
        <div
          style={{
            padding: '8px 20px',
            borderRadius: 999,
            background: theme.amber,
            color: theme.ledPanel,
            fontFamily: theme.fontSans,
            fontWeight: 800,
            fontSize: 34,
          }}
        >
          TAG {day}
        </div>
        <div
          style={{
            padding: '10px 16px',
            borderRadius: 12,
            background: 'rgba(7,9,12,0.82)',
            border: `2px solid ${theme.panelBorder}`,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}
        >
          <Led size={24}>{route.from.toUpperCase()}</Led>
          <Arrow size={22} color={theme.amber} />
          <Led size={24}>{route.to.toUpperCase()}</Led>
          <span style={{width: 12}} />
          <Led size={24}>{clock}</Led>
        </div>
      </div>
      <div
        style={{
          marginTop: 12,
          display: 'inline-flex',
          alignItems: 'center',
          gap: 14,
          padding: '10px 18px',
          borderRadius: 12,
          background: 'rgba(7,9,12,0.86)',
          border: `2px solid ${pop > 0.05 ? theme.amber : theme.panelBorder}`,
          transform: `scale(${scale})`,
          transformOrigin: 'top left',
          boxShadow: pop > 0.05 ? `0 0 ${40 * pop}px ${theme.amberGlow}` : 'none',
        }}
      >
        <span style={{fontFamily: theme.fontSans, fontWeight: 600, fontSize: 18, letterSpacing: 2, color: theme.muted}}>
          VERSPÄTUNG
        </span>
        <Led size={44} brightness={flicker}>{`+${Math.round(delay)} MIN`}</Led>
      </div>
    </div>
  );
};
