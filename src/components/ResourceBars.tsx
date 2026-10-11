import React from 'react';
import {useCurrentFrame} from 'remotion';
import {layout, theme} from '../theme';
import type {Resources} from '../types';

const SEGMENTS = 12;

const Bar: React.FC<{ratio: number; low: boolean; blinkOn: boolean}> = ({ratio, low, blinkOn}) => {
  const lit = Math.round(Math.max(0, Math.min(1, ratio)) * SEGMENTS);
  const color = low ? theme.alert : theme.amber;
  return (
    <div style={{display: 'flex', gap: 5}}>
      {Array.from({length: SEGMENTS}, (_, i) => {
        const on = i < lit;
        return (
          <div
            key={i}
            style={{
              opacity: on && low && !blinkOn ? 0.35 : 1,
              flex: 1,
              height: 20,
              borderRadius: 3,
              background: on ? color : '#1C2028',
              boxShadow: on ? `0 0 10px ${low ? 'rgba(255,91,46,0.6)' : theme.amberGlow}` : 'none',
            }}
          />
        );
      })}
    </div>
  );
};

const Signal: React.FC<{bars: number}> = ({bars}) => (
  <div style={{display: 'flex', alignItems: 'flex-end', gap: 6, height: 34}}>
    {[0, 1, 2, 3].map((i) => {
      const on = i < Math.round(bars);
      return (
        <div
          key={i}
          style={{
            width: 14,
            height: 10 + i * 8,
            borderRadius: 3,
            background: on ? theme.amber : '#1C2028',
            boxShadow: on ? `0 0 10px ${theme.amberGlow}` : 'none',
          }}
        />
      );
    })}
  </div>
);

export const ResourceBars: React.FC<{
  values: Resources;
  max: Resources;
  changing: Partial<Record<keyof Resources, boolean>>;
}> = ({values, max, changing}) => {
  const frame = useCurrentFrame();
  const blinkOn = Math.floor(frame / 9) % 2 === 0;

  const items: {key: keyof Resources; label: string; unit: string}[] = [
    {key: 'kaffee', label: 'Kaffee', unit: 'Becher'},
    {key: 'brezeln', label: 'Brezeln', unit: 'Stück'},
    {key: 'steckdosen', label: 'Steckdosen', unit: 'frei'},
  ];

  const valueStyle = (k: keyof Resources): React.CSSProperties => ({
    fontFamily: theme.fontMono,
    fontWeight: 700,
    fontSize: 26,
    color: changing[k] ? theme.amber : theme.text,
    textShadow: changing[k] ? `0 0 14px ${theme.amberGlow}` : 'none',
  });

  const wlan = Math.round(values.wlan);

  return (
    <div
      style={{
        position: 'absolute',
        left: layout.side,
        top: layout.resourcesTop,
        width: layout.lowerWidth,
        padding: '18px 28px 22px',
        borderRadius: 22,
        background: theme.panel,
        border: `2px solid ${theme.panelBorder}`,
        boxSizing: 'border-box',
      }}
    >
      <div style={{fontFamily: theme.fontSans, fontWeight: 600, fontSize: 20, letterSpacing: 4, color: theme.muted, marginBottom: 12}}>
        VORRÄTE AN BORD
      </div>
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: 40, rowGap: 16}}>
        {items.map(({key, label, unit}) => {
          const ratio = values[key] / max[key];
          return (
            <div key={key}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 8}}>
                <span style={{fontFamily: theme.fontSans, fontWeight: 600, fontSize: 28, color: theme.text}}>{label}</span>
                <span style={valueStyle(key)}>
                  {Math.round(values[key])} <span style={{fontSize: 20, color: theme.muted}}>{unit}</span>
                </span>
              </div>
              <Bar ratio={ratio} low={ratio <= 0.2} blinkOn={blinkOn} />
            </div>
          );
        })}
        <div>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span style={{fontFamily: theme.fontSans, fontWeight: 600, fontSize: 28, color: theme.text}}>WLAN</span>
            <span style={{display: 'flex', alignItems: 'center', gap: 14}}>
              <span style={{...valueStyle('wlan'), color: wlan === 0 ? theme.alert : valueStyle('wlan').color}}>
                {wlan === 0 ? 'weg' : wlan === 1 ? 'schwach' : 'ok'}
              </span>
              <Signal bars={values.wlan} />
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
