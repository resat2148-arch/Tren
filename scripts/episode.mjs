// Zeitachse einer Folge für die Node-Skripte (gleiche Regeln wie src/timeline.ts).
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';

export const FPS = 30;

export const loadEpisode = (id) => JSON.parse(readFileSync(resolve('episodes', `${id}.json`), 'utf8'));

export const scenesOf = (ep) => {
  const all = [{...ep.intro, type: 'intro'}, ...ep.scenes, {...ep.cliffhanger, type: 'cliffhanger'}];
  let from = 0;
  return all.map((s, index) => {
    const frames = Math.round(s.duration * FPS);
    const timed = {...s, index, from, frames};
    from += frames;
    return timed;
  });
};

export const fmt = (frame) => {
  const s = frame / FPS;
  return `${Math.floor(s / 60)}:${(s % 60).toFixed(1).padStart(4, '0')}`;
};
