import React from 'react';
import {random, useCurrentFrame} from 'remotion';
import {Arrow, Led} from './Led';
import {layout, theme} from '../theme';

export const DelayBoard: React.FC<{
  route: {from: string; to: string};
  delay: number;
  delayChanging: boolean;
  clock: string;
  ticker: string;
  urgent: boolean;
}> = ({route, delay, delayChanging, clock, ticker, urgent}) => {
  const frame = useCurrentFrame();
  const flicker = delayChanging ? 0.75 + 0.25 * random(`flicker-${frame}`) : 1;
  const blink = urgent ? (Math.floor(frame / 8) % 2 === 0 ? 1 : 0.35) : 1;
  const tickerText = `${ticker}     `;
  const tickerShift = (frame * 5) % (tickerText.length * 30 * 0.64);

  return (
    <div
      style={{
        position: 'absolute',
        left: layout.side,
        top: layout.boardTop,
        width: layout.fullWidth,
        height: layout.boardHeight,
        borderRadius: 26,
        background: theme.ledPanel,
        border: `3px solid ${urgent && blink === 1 ? theme.alert : theme.panelBorder}`,
        boxShadow: '0 20px 60px rgba(0,0,0,0.55), inset 0 0 0 6px #0D1116',
        overflow: 'hidden',
        backgroundImage: `radial-gradient(circle, ${theme.ledOff} 0 1.6px, transparent 2.2px)`,
        backgroundSize: '7px 7px',
      }}
    >
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '26px 34px 0'}}>
        <span style={{display: 'flex', alignItems: 'center', gap: 16}}>
          <Led size={38}>{route.from.toUpperCase()}</Led>
          <Arrow size={36} color={theme.amber} />
          <Led size={38}>{route.to.toUpperCase()}</Led>
        </span>
        <Led size={38}>{clock}</Led>
      </div>
      <div style={{height: 3, margin: '20px 34px 0', background: '#1A1F27'}} />
      <div style={{padding: '12px 34px 0', display: 'flex', alignItems: 'center', gap: 30}}>
        <div
          style={{
            fontFamily: theme.fontSans,
            fontWeight: 600,
            fontSize: 22,
            letterSpacing: 2,
            color: theme.muted,
            lineHeight: 1.35,
            width: 180,
          }}
        >
          AKTUELLE
          <br />
          VERSPÄTUNG
        </div>
        <Led size={128} brightness={flicker * blink}>{`+${Math.round(delay)} Min`}</Led>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: 58,
          background: '#0A0B0E',
          borderTop: '3px solid #1A1F27',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <div style={{transform: `translateX(${-tickerShift}px)`, display: 'flex', whiteSpace: 'nowrap'}}>
          <Led size={30} weight={700} color={urgent ? theme.alert : theme.amber}>
            {tickerText.repeat(4)}
          </Led>
        </div>
      </div>
    </div>
  );
};
