import {Easing, interpolate} from 'remotion';
import type {FilmEpisode, Shot} from './types';

export type TimedShot = Shot & {index: number; from: number; frames: number};

export type FilmTimeline = {
  fps: number;
  shots: TimedShot[];
  cliffFrom: number;
  cliffFrames: number;
  totalFrames: number;
};

export const buildFilm = (ep: FilmEpisode, fps: number): FilmTimeline => {
  let from = 0;
  const shots = ep.shots.map((s, index) => {
    if (!(s.duration > 0)) throw new Error(`Shot ${s.id}: "duration" fehlt`);
    const frames = Math.round(s.duration * fps);
    const timed = {...s, index, from, frames};
    from += frames;
    return timed;
  });
  const cliffFrames = Math.round(ep.cliffhanger.duration * fps);
  return {fps, shots, cliffFrom: from, cliffFrames, totalFrames: from + cliffFrames};
};

export const shotAt = (tl: FilmTimeline, frame: number) =>
  tl.shots.find((s) => frame >= s.from && frame < s.from + s.frames) ?? null;

// Verspätung: zählt im Shot, der einen neuen Wert setzt, innerhalb von 1,2 s hoch
export const delayAt = (tl: FilmTimeline, frame: number) => {
  let value = 0;
  let changing = false;
  for (const s of tl.shots) {
    if (s.from > frame) break;
    const target = s.hud?.delay;
    if (target === undefined) continue;
    if (value === 0) {
      value = target;
      continue;
    }
    const ramp = Math.round(1.2 * tl.fps);
    if (frame < s.from + ramp) {
      changing = true;
      return {
        value: interpolate(frame, [s.from, s.from + ramp], [value, target], {
          easing: Easing.inOut(Easing.cubic),
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        }),
        changing,
        since: frame - s.from,
      };
    }
    value = target;
  }
  return {value, changing, since: Infinity};
};

export const clockAt = (tl: FilmTimeline, frame: number) => {
  let clock = '';
  for (const s of tl.shots) {
    if (s.from > frame) break;
    if (s.hud?.clock) clock = s.hud.clock;
  }
  return clock;
};

// Anzeigenamen für Untertitel
export const NAMES: Record<string, string> = {
  platz47: 'Platz 47',
  zugchef: 'Zugchef',
  rentner: 'Rentner',
  businessmann: 'Businessmann',
  studentin: 'Studentin',
  fahrgast_a: 'Fahrgast',
  fahrgast_b: 'Fahrgast',
  fahrgast_c: 'Fahrgast',
  fahrgast_d: 'Fahrgast',
};
