import {Easing, interpolate} from 'remotion';
import type {Episode, Resources, Scene} from './types';

export type TimedScene = Scene & {index: number; from: number; frames: number};

export type Timeline = {
  fps: number;
  scenes: TimedScene[];
  totalFrames: number;
  introFrames: number;
  distance: number[]; // zurückgelegte Strecke in px pro Frame (für die Karte)
};

const PX_PER_FRAME = 13;
const ease = Easing.inOut(Easing.cubic);

export const buildTimeline = (ep: Episode, fps: number): Timeline => {
  const all: Scene[] = [
    {...ep.intro, type: 'intro'},
    ...ep.scenes,
    {...ep.cliffhanger, type: 'cliffhanger'},
  ];
  let from = 0;
  const scenes = all.map((s, index) => {
    if (!(s.duration > 0)) throw new Error(`Szene ${index} (${s.type}): "duration" fehlt oder ist 0`);
    const frames = Math.round(s.duration * fps);
    const timed = {...s, index, from, frames} as TimedScene;
    from += frames;
    return timed;
  });

  const tl: Timeline = {fps, scenes, totalFrames: from, introFrames: scenes[0].frames, distance: []};
  let d = 0;
  for (let f = 0; f < from; f++) {
    tl.distance.push(d);
    d += speedAt(tl, f) * PX_PER_FRAME;
  }
  return tl;
};

// Wert, den Szenen setzen können; beim Szenenstart geht er weich in den neuen Wert über.
const track = (
  tl: Timeline,
  frame: number,
  pick: (s: TimedScene) => number | undefined,
  initial: number,
  rampSeconds: number,
) => {
  let value = initial;
  for (const s of tl.scenes) {
    if (s.from > frame) break;
    const target = pick(s);
    if (target === undefined) continue;
    const ramp = Math.max(1, Math.min(s.frames, Math.round(rampSeconds * tl.fps)));
    if (frame < s.from + ramp) {
      return interpolate(frame, [s.from, s.from + ramp], [value, target], {
        easing: ease,
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });
    }
    value = target;
  }
  return value;
};

// Diskreter Wert: der zuletzt gesetzte gilt.
const latest = <T,>(tl: Timeline, frame: number, pick: (s: TimedScene) => T | undefined, initial: T) => {
  let value = initial;
  for (const s of tl.scenes) {
    if (s.from > frame) break;
    const v = pick(s);
    if (v !== undefined) value = v;
  }
  return value;
};

export const speedAt = (tl: Timeline, frame: number) =>
  track(tl, frame, (s) => (s.stop ? 0 : s.go ? 1 : undefined), 1, 1.5);

export const activeScene = (tl: Timeline, frame: number) =>
  tl.scenes.find((s) => frame >= s.from && frame < s.from + s.frames) ?? tl.scenes[tl.scenes.length - 1];

export const stateAt = (ep: Episode, tl: Timeline, frame: number) => {
  const resources = {} as Resources;
  (Object.keys(ep.resources) as (keyof Resources)[]).forEach((k) => {
    resources[k] = track(tl, frame, (s) => s.resources?.[k], ep.resources[k], 1.2);
  });
  return {
    delay: track(tl, frame, (s) => s.delay, ep.delay.from, 1.2),
    resources,
    night: track(tl, frame, (s) => s.night, 0, 2.5),
    speed: speedAt(tl, frame),
    distance: tl.distance[Math.min(Math.max(0, frame), tl.distance.length - 1)] ?? 0,
    clock: latest(tl, frame, (s) => s.clock, ''),
    location: latest(tl, frame, (s) => s.location, ''),
    ticker: latest(tl, frame, (s) => s.ticker, ep.ticker),
  };
};

export type FrameState = ReturnType<typeof stateAt>;
