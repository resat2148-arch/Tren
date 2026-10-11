import React from 'react';
import {Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {Arrow, Led} from './Led';
import {layout, theme} from '../theme';
import type {WagenId} from '../types';

// Kartenmaße = Pixelmaße (SVG wird 1:1 dargestellt)
const W = layout.fullWidth;
const H = layout.mapHeight;
const TRACK_Y = 168;
const CAR_W = 196;
const CAR_H = 108;
const GAP = 8;
const NOSE = 44;
const START_X = (W - (2 * NOSE + 4 * CAR_W + 3 * GAP)) / 2;
const TOP = TRACK_Y - CAR_H / 2;
const BOTTOM = TRACK_Y + CAR_H / 2;
const BED = 66; // halbe Breite des Schotterbetts

const CARS: {id: WagenId; name: string; first?: boolean}[] = [
  {id: 5, name: 'WAGEN 5'},
  {id: 6, name: 'WAGEN 6'},
  {id: 7, name: 'WAGEN 7'},
  {id: '1. Klasse', name: '1. KLASSE', first: true},
];

const carX = (i: number) => START_X + NOSE + i * (CAR_W + GAP);
const carCx = (i: number) => carX(i) + CAR_W / 2;

type Seat = {car: number; x: number; y: number; occupied: boolean; me: boolean};

const SEATS: Seat[] = CARS.flatMap((car, ci) => {
  const rows = car.first ? [-32, -15, 26] : [-34, -18, 18, 34];
  const cols = car.first ? 6 : 8;
  const step = (CAR_W - 44) / (cols - 1);
  const seats: Seat[] = [];
  rows.forEach((ry, r) => {
    for (let c = 0; c < cols; c++) {
      const me = car.id === 6 && r === 0 && c === 5; // Platz 47
      seats.push({
        car: ci,
        x: carX(ci) + 22 + c * step,
        y: TRACK_Y + ry,
        me,
        occupied: me || random(`seat-${ci}-${r}-${c}`) < (car.first ? 0.45 : 0.78),
      });
    }
  });
  return seats;
});

export type MapHighlight = {
  wagen: WagenId;
  label?: string;
  marker?: string;
  crowd?: boolean;
  local: number; // Frame innerhalb der Szene
} | null;

// Wiederkehrende Objekte (Masten, Feldwege, Bäume) ziehen mit der Fahrt vorbei.
const repeat = (period: number, offset: number, distance: number) => {
  const xs: number[] = [];
  const shift = distance % period;
  for (let k = -1; k <= Math.ceil(W / period) + 1; k++) xs.push(offset + k * period - shift);
  return xs;
};

export const TrainMap: React.FC<{
  distance: number;
  speed: number;
  night: number;
  location: string;
  destination: string;
  highlight: MapHighlight;
}> = ({distance, speed, night, location, destination, highlight}) => {
  const frame = useCurrentFrame();
  const d = distance;
  const hi = highlight ? CARS.findIndex((c) => c.id === highlight.wagen) : -1;
  const hiIn = highlight ? interpolate(highlight.local, [0, 8], [0, 1], {extrapolateRight: 'clamp'}) : 0;
  const pulse = 0.55 + 0.45 * Math.sin(frame / 4);
  const crowdT =
    highlight?.crowd
      ? interpolate(highlight.local, [6, 48], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.inOut(Easing.cubic),
        })
      : 0;

  // Rütteln: leicht während der Fahrt, stark beim Bremsen
  const brake = speed * (1 - speed) * 4;
  const jx = (random(`jx-${frame}`) - 0.5) * 7 * brake;
  const jy = Math.sin(frame * 2.1) * 0.7 * speed + (random(`jy-${frame}`) - 0.5) * 3 * brake;

  const fieldDark = interpolate(night, [0, 1], [0, 0.74]);
  const kmh = Math.round(speed * 236);

  const shell = '#39404B';
  const floor = night > 0.5 ? '#1D1A16' : '#171B21';

  return (
    <div
      style={{
        position: 'absolute',
        left: layout.side,
        top: layout.mapTop,
        width: W,
        height: H,
        borderRadius: 26,
        overflow: 'hidden',
        border: `3px solid ${theme.panelBorder}`,
        boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
      }}
    >
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{display: 'block'}}>
        <defs>
          <pattern id="rowsTop" x={-(d % 18)} y={0} width={18} height={20} patternUnits="userSpaceOnUse">
            <rect width={18} height={20} fill="#26321C" />
            <rect width={8} height={20} fill="#33421F" />
          </pattern>
          <pattern
            id="rowsBottom"
            x={-(d % 26)}
            y={0}
            width={26}
            height={26}
            patternUnits="userSpaceOnUse"
            patternTransform="skewX(-28)"
          >
            <rect width={26} height={26} fill="#18271D" />
            <rect width={10} height={26} fill="#203427" />
          </pattern>
          <pattern id="sleepers" x={-(d % 24)} y={TRACK_Y - BED} width={24} height={BED * 2} patternUnits="userSpaceOnUse">
            <rect width={24} height={BED * 2} fill="#2B2A29" />
            <rect x={6} y={10} width={10} height={BED * 2 - 20} fill="#423C35" />
          </pattern>
          <filter id="blur14" x="-20%" y="-50%" width="140%" height="200%">
            <feGaussianBlur stdDeviation={14} />
          </filter>
          <filter id="blur6" x="-20%" y="-50%" width="140%" height="200%">
            <feGaussianBlur stdDeviation={6} />
          </filter>
        </defs>

        {/* Landschaft */}
        <rect x={0} y={0} width={W} height={TRACK_Y - BED} fill="url(#rowsTop)" />
        <rect x={0} y={TRACK_Y + BED} width={W} height={H - TRACK_Y - BED} fill="url(#rowsBottom)" />
        <rect x={0} y={TRACK_Y - BED} width={W} height={BED * 2} fill="url(#sleepers)" />
        {[-44, 44].map((dy) => (
          <line key={dy} x1={0} x2={W} y1={TRACK_Y + dy} y2={TRACK_Y + dy} stroke="#8D8F93" strokeWidth={3} />
        ))}
        {repeat(1300, 420, d).map((x) => (
          <g key={`road-${x}`} fill="#3A3328">
            <rect x={x} y={0} width={34} height={TRACK_Y - BED} />
            <rect x={x} y={TRACK_Y + BED} width={34} height={H} />
          </g>
        ))}
        {repeat(820, 150, d).map((x) => (
          <g key={`tree-${x}`} fill="#0E1A12">
            <circle cx={x} cy={292} r={26} />
            <circle cx={x + 30} cy={304} r={20} />
            <circle cx={x + 12} cy={318} r={17} />
          </g>
        ))}
        {repeat(1070, 700, d).map((x) => (
          <g key={`tree2-${x}`} fill="#121F14">
            <circle cx={x} cy={46} r={22} />
            <circle cx={x + 26} cy={34} r={16} />
          </g>
        ))}

        {/* Nacht */}
        <rect x={0} y={0} width={W} height={H} fill="#02040A" opacity={fieldDark} />
        {night > 0 && (
          <g opacity={night}>
            <rect
              x={START_X}
              y={TOP - 22}
              width={W - 2 * START_X}
              height={CAR_H + 44}
              fill={theme.amber}
              opacity={0.2}
              filter="url(#blur14)"
            />
            <polygon
              points={`${W - START_X - 6},${TRACK_Y - 20} ${W + 40},${TRACK_Y - 90} ${W + 40},${TRACK_Y + 90} ${W - START_X - 6},${TRACK_Y + 20}`}
              fill="#FFE2B0"
              opacity={0.16}
              filter="url(#blur6)"
            />
          </g>
        )}

        {/* Zug */}
        <g transform={`translate(${jx} ${jy})`}>
          {/* Endwagen-Nasen */}
          <path
            d={`M ${carX(0)} ${TOP} L ${carX(0) - 12} ${TOP} Q ${carX(0) - NOSE} ${TOP + 6} ${carX(0) - NOSE} ${TRACK_Y} Q ${carX(0) - NOSE} ${BOTTOM - 6} ${carX(0) - 12} ${BOTTOM} L ${carX(0)} ${BOTTOM} Z`}
            fill={shell}
          />
          <path
            d={`M ${carX(3) + CAR_W} ${TOP} L ${carX(3) + CAR_W + 12} ${TOP} Q ${carX(3) + CAR_W + NOSE} ${TOP + 6} ${carX(3) + CAR_W + NOSE} ${TRACK_Y} Q ${carX(3) + CAR_W + NOSE} ${BOTTOM - 6} ${carX(3) + CAR_W + 12} ${BOTTOM} L ${carX(3) + CAR_W} ${BOTTOM} Z`}
            fill={shell}
          />
          {[-26, 26].map((dy) => (
            <React.Fragment key={dy}>
              <rect x={carX(3) + CAR_W + NOSE - 12} y={TRACK_Y + dy - 6} width={6} height={12} rx={3} fill="#FFE7B8" />
              <rect x={carX(0) - NOSE + 6} y={TRACK_Y + dy - 5} width={5} height={10} rx={2} fill={theme.alert} opacity={0.8} />
            </React.Fragment>
          ))}

          {CARS.map((car, i) => {
            const isHi = i === hi;
            return (
              <g key={car.name}>
                {isHi && (
                  <rect
                    x={carX(i) - 8}
                    y={TOP - 8}
                    width={CAR_W + 16}
                    height={CAR_H + 16}
                    rx={20}
                    fill={theme.amber}
                    opacity={0.45 * pulse * hiIn}
                    filter="url(#blur6)"
                  />
                )}
                <rect x={carX(i)} y={TOP} width={CAR_W} height={CAR_H} rx={12} fill={shell} />
                <rect x={carX(i) + 7} y={TOP + 7} width={CAR_W - 14} height={CAR_H - 14} rx={7} fill={floor} />
                {/* Einstiegsbereiche */}
                <rect x={carX(i) + 7} y={TOP + 7} width={8} height={CAR_H - 14} fill="#232830" />
                <rect x={carX(i) + CAR_W - 15} y={TOP + 7} width={8} height={CAR_H - 14} fill="#232830" />
                {/* eigenes Design-Merkmal: durchlaufende LED-Leiste */}
                <line x1={carX(i) + 4} x2={carX(i) + CAR_W - 4} y1={TOP + 3} y2={TOP + 3} stroke={theme.amber} strokeWidth={2} opacity={0.55} />
                <line x1={carX(i) + 4} x2={carX(i) + CAR_W - 4} y1={BOTTOM - 3} y2={BOTTOM - 3} stroke={theme.amber} strokeWidth={2} opacity={0.55} />
                {isHi && (
                  <rect
                    x={carX(i) + 1}
                    y={TOP + 1}
                    width={CAR_W - 2}
                    height={CAR_H - 2}
                    rx={12}
                    fill="none"
                    stroke={theme.amber}
                    strokeWidth={4}
                    opacity={(0.5 + 0.5 * pulse) * hiIn}
                  />
                )}
              </g>
            );
          })}

          {/* Sitze und Fahrgäste */}
          {SEATS.map((s, idx) => (
            <rect key={`seat-${idx}`} x={s.x - 7} y={s.y - 6} width={14} height={12} rx={3} fill="#2A313B" />
          ))}
          {SEATS.map((s, idx) => {
            if (!s.occupied) return null;
            let x = s.x;
            let y = s.y;
            if (crowdT > 0 && s.car === hi && !s.me) {
              const angle = idx * 2.39996;
              const radius = 16 + (idx % 4) * 8;
              const tx = carCx(hi) + Math.cos(angle) * radius * 1.6;
              const ty = TRACK_Y + Math.sin(angle) * Math.min(radius, 40);
              const wobble = Math.sin(frame * 0.6 + idx) * 2.5 * crowdT;
              x = s.x + (tx - s.x) * crowdT * 0.9 + wobble;
              y = s.y + (ty - s.y) * crowdT * 0.9 + Math.cos(frame * 0.5 + idx) * 2 * crowdT;
            }
            if (s.me) {
              const ring = (frame % 36) / 36;
              return (
                <g key={`p-${idx}`}>
                  <circle cx={x} cy={y} r={7 + ring * 16} fill="none" stroke={theme.amber} strokeWidth={2} opacity={1 - ring} />
                  <circle cx={x} cy={y} r={7.5} fill={theme.amber} />
                  <text
                    x={x}
                    y={TOP - 8}
                    textAnchor="middle"
                    fontFamily={theme.fontMono}
                    fontWeight={800}
                    fontSize={16}
                    fill={theme.amber}
                  >
                    47
                  </text>
                </g>
              );
            }
            return <circle key={`p-${idx}`} cx={x} cy={y} r={6} fill="#E6DFD0" opacity={night > 0.5 ? 0.92 : 1} />;
          })}

          {/* Markierung in der Wagenmitte */}
          {highlight?.marker && hi >= 0 && (
            <g opacity={hiIn}>
              <circle
                cx={carCx(hi)}
                cy={TRACK_Y}
                r={10 + ((frame % 30) / 30) * 22}
                fill="none"
                stroke={theme.amber}
                strokeWidth={3}
                opacity={1 - (frame % 30) / 30}
              />
              <rect
                x={carCx(hi) - 10}
                y={TRACK_Y - 10}
                width={20}
                height={20}
                fill={theme.amber}
                transform={`rotate(45 ${carCx(hi)} ${TRACK_Y})`}
              />
            </g>
          )}

          {/* Oberleitung + Masten */}
          <line x1={0} x2={W} y1={TRACK_Y} y2={TRACK_Y} stroke="#9AA3B0" strokeWidth={1.5} opacity={0.35} />
          {repeat(250, 60, d).map((x) => (
            <g key={`mast-${x}`} opacity={0.75}>
              <line x1={x} x2={x} y1={TRACK_Y - BED - 6} y2={TRACK_Y + 8} stroke="#7A828E" strokeWidth={3} />
              <rect x={x - 6} y={TRACK_Y - BED - 14} width={12} height={12} fill="#6B7380" />
            </g>
          ))}
        </g>
      </svg>

      {/* Beschriftungen */}
      {CARS.map((car, i) => (
        <div
          key={car.name}
          style={{
            position: 'absolute',
            left: carCx(i),
            top: BOTTOM + 14,
            transform: 'translateX(-50%)',
            fontFamily: theme.fontSans,
            fontWeight: 600,
            fontSize: 18,
            letterSpacing: 2,
            padding: '4px 10px',
            borderRadius: 8,
            background: 'rgba(7,9,12,0.78)',
            color: i === hi ? theme.amber : theme.muted,
            whiteSpace: 'nowrap',
          }}
        >
          {car.name}
        </div>
      ))}

      {highlight && hi >= 0 && highlight.label && (
        <div
          style={{
            position: 'absolute',
            left: Math.min(Math.max(carCx(hi), 170), W - 170),
            top: TOP - 62,
            transform: `translateX(-50%) translateY(${(1 - hiIn) * 12}px)`,
            opacity: hiIn,
            padding: '7px 18px',
            borderRadius: 10,
            background: theme.amber,
            color: theme.ledPanel,
            fontFamily: theme.fontSans,
            fontWeight: 800,
            fontSize: 24,
            letterSpacing: 1,
            whiteSpace: 'nowrap',
            boxShadow: `0 0 30px ${theme.amberGlow}`,
          }}
        >
          {highlight.label.toUpperCase()}
        </div>
      )}

      {highlight?.marker && hi >= 0 && (
        <div
          style={{
            position: 'absolute',
            left: Math.min(Math.max(carCx(hi), 120), W - 120),
            top: BOTTOM + 52,
            transform: 'translateX(-50%)',
            opacity: hiIn,
            fontFamily: theme.fontSans,
            fontWeight: 600,
            fontSize: 22,
            padding: '5px 14px',
            borderRadius: 8,
            border: `2px solid ${theme.amber}`,
            background: 'rgba(7,9,12,0.85)',
            color: theme.amber,
            whiteSpace: 'nowrap',
          }}
        >
          {highlight.marker}
        </div>
      )}

      <div
        style={{
          position: 'absolute',
          right: 14,
          top: 12,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '5px 12px',
          borderRadius: 8,
          background: 'rgba(7,9,12,0.75)',
          fontFamily: theme.fontSans,
          fontWeight: 600,
          fontSize: 18,
          letterSpacing: 2,
          color: theme.muted,
        }}
      >
        RICHTUNG {destination.toUpperCase()} <Arrow size={22} color={theme.muted} />
      </div>

      <div
        style={{
          position: 'absolute',
          left: 14,
          bottom: 12,
          padding: '6px 12px',
          borderRadius: 8,
          background: 'rgba(7,9,12,0.8)',
          fontFamily: theme.fontMono,
          fontWeight: 700,
          fontSize: 20,
          color: theme.text,
        }}
      >
        <span style={{color: theme.muted}}>STANDORT </span>
        {location}
      </div>

      <div
        style={{
          position: 'absolute',
          right: 14,
          bottom: 12,
          padding: '8px 14px',
          borderRadius: 8,
          background: theme.ledPanel,
        }}
      >
        <Led size={26} color={kmh === 0 ? theme.alert : theme.amber}>{`${String(kmh).padStart(3, ' ')} km/h`}</Led>
      </div>
    </div>
  );
};
