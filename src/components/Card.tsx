import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {layout} from '../theme';

// Gemeinsame Ein-/Ausblendung für die Textkarten im unteren Bereich.
export const CardFrame: React.FC<{children: React.ReactNode; frames: number; style?: React.CSSProperties}> = ({
  children,
  frames: durationInFrames,
  style,
}) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [0, 8], [0, 1], {extrapolateRight: 'clamp'});
  const exit = interpolate(frame, [durationInFrames - 6, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        position: 'absolute',
        left: layout.side,
        top: layout.cardTop,
        width: layout.lowerWidth,
        boxSizing: 'border-box',
        opacity: Math.min(enter, exit),
        transform: `translateY(${(1 - enter) * 40}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};
