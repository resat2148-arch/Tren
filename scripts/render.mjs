// Rendert eine Folge als MP4 und die markierten Standbilder ("still": true).
//   npm run render -- day-01            Video + Standbilder
//   npm run render -- day-01 --stills   nur Standbilder
// Optional: BROWSER_EXECUTABLE=/pfad/zu/chromium
import {mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import {loadEpisode, scenesOf} from './episode.mjs';

const id = process.argv[2] ?? 'day-01';
const stillsOnly = process.argv.includes('--stills');
const browserExecutable = process.env.BROWSER_EXECUTABLE || null;

const outDir = resolve('out');
const stillDir = resolve('out', 'stills', id);
mkdirSync(stillDir, {recursive: true});

const serveUrl = await bundle({entryPoint: resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id, browserExecutable});

if (!stillsOnly) {
  const outputLocation = resolve(outDir, `${id}.mp4`);
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
      if (pct !== last) {
        last = pct;
        console.log(`Render ${pct}%`);
      }
    },
  });
  console.log(`Video: ${outputLocation}`);
}

const scenes = scenesOf(loadEpisode(id)).filter((s) => s.still);
for (const [n, s] of scenes.entries()) {
  // Intro: Titel steht groß im Bild; Cliffhanger: Pointe ist da; sonst: Text fertig getippt
  const at = s.type === 'intro' ? 0.4 : s.type === 'cliffhanger' ? 0.9 : 0.75;
  const frame = s.from + Math.floor(s.frames * at);
  const output = resolve(stillDir, `${String(n + 1).padStart(2, '0')}-${s.type}-f${frame}.jpg`);
  await renderStill({serveUrl, composition, frame, output, imageFormat: 'jpeg', jpegQuality: 90, browserExecutable});
  console.log(`Standbild: ${output}`);
}
