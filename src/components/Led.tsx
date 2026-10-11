import React from 'react';
import {theme} from '../theme';

// Orangefarbene Punktmatrix: leuchtender Text + Raster, das ihn in einzelne LEDs zerlegt.
export const Led: React.FC<{
  children: React.ReactNode;
  size: number;
  color?: string;
  weight?: number;
  brightness?: number;
  dots?: boolean; // Punktraster nur auf dem dunklen Anzeigegrund sinnvoll
  style?: React.CSSProperties;
}> = ({children, size, color = theme.amber, weight = 800, brightness = 1, dots = true, style}) => {
  // kleine Schrift: feineres Raster, sonst wird sie unlesbar
  const pitch = size >= 80 ? Math.round(size / 11) : 3;
  return (
    <span
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        fontFamily: theme.fontMono,
        fontWeight: weight,
        fontSize: size,
        lineHeight: 1,
        letterSpacing: size * 0.04,
        color,
        opacity: brightness,
        textShadow: `0 0 ${size * 0.12}px ${color}, 0 0 ${size * 0.35}px ${theme.amberGlow}`,
        whiteSpace: 'pre',
        ...style,
      }}
    >
      {children}
      {dots && (
        <span
          style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: `radial-gradient(circle, rgba(0,0,0,0) 0 ${size >= 80 ? 48 : 58}%, ${theme.ledPanel} ${size >= 80 ? 72 : 90}%)`,
            backgroundSize: `${pitch}px ${pitch}px`,
            pointerEvents: 'none',
          }}
        />
      )}
    </span>
  );
};

// Pfeil als SVG – die Webfont-Subsets enthalten kein "→".
export const Arrow: React.FC<{size: number; color: string; style?: React.CSSProperties}> = ({
  size,
  color,
  style,
}) => (
  <svg width={size} height={size * 0.6} viewBox="0 0 50 30" style={{display: 'inline-block', ...style}}>
    <path d="M2 15 H40 M30 4 L44 15 L30 26" stroke={color} strokeWidth={6} fill="none" strokeLinecap="square" />
  </svg>
);
