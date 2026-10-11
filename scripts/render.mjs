// Schneidet die Folge in Remotion zusammen (Blender-Shots + Untertitel, Durchsagen, HUD, Cliffhanger)
// und erzeugt Kontrollbilder für alle Shots mit "poster": true.
//   npm run render -- day-01            Video + Kontrollbilder
//   npm run render -- day-01 --posters  nur Kontrollbilder
// Optional: BROWSER_EXECUTABLE=/pfad/zu/chromium
import {mkdirSync, readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';

const id = process.argv[2] ?? 'day-01';
const postersOnly = process.argv.includes('--posters');
const browserExecutable = process.env.BROWSER_EXECUTABLE || null;
const ep = JSON.parse(readFileSync(resolve('episodes', `${id}.json`), 'utf8'));
const fps = ep.fps ?? 30;

const posterDir = resolve('out', 'posters', id);
mkdirSync(posterDir, {recursive: true});

const serveUrl = await bundle({entryPoint: resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id, browserExecutable});

if (!postersOnly) {
  const outputLocation = resolve('out', `${id}.mp4`);
  let last = -1;
  await renderMedia({
    serveUrl,
    composition,
    codec: 'h264',
    crf: 18,
    imageFormat: 'jpeg',
    jpegQuality: 92,
    outputLocation,
    browserExecutable,
    onProgress: ({progress}) => {
      const pct = Math.floor(progress * 10) * 10;
      if (pct !== last) console.log(`Render ${(last = pct)}%`);
    },
  });
  console.log(`Video: ${outputLocation}`);
}

let from = 0;
const posters = [];
for (const s of ep.shots) {
  const frames = Math.round(s.duration * fps);
  if (s.poster) posters.push({name: s.id, frame: from + Math.floor(frames * 0.72)});
  from += frames;
}
posters.push({name: 'cliffhanger', frame: from + Math.round(ep.cliffhanger.duration * fps * 0.9)});
for (const p of posters) {
  const output = resolve(posterDir, `${p.name}.jpg`);
  await renderStill({serveUrl, composition, frame: p.frame, output, imageFormat: 'jpeg', jpegQuality: 90, browserExecutable});
  console.log(`Kontrollbild: ${output}`);
}
