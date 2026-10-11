// Schreibt die Ton-Cue-Liste einer Folge: npm run cues -- day-01
import {writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {FPS, fmt, loadEpisode, scenesOf} from './episode.mjs';

const id = process.argv[2] ?? 'day-01';
const ep = loadEpisode(id);
const scenes = scenesOf(ep);
const total = scenes.at(-1).from + scenes.at(-1).frames;

const voiceOf = (s) =>
  s.type === 'durchsage' ? 'Ansage' : s.type === 'diary' || s.type === 'mapEvent' ? 'Platz 47 (Erzähler)' : null;

const rows = [];
for (const s of scenes) {
  for (const c of s.sfx ?? []) {
    const start = s.from + Math.round((c.at ?? 0) * FPS);
    const end = c.length ? ` – ${fmt(start + Math.round(c.length * FPS))}` : '';
    rows.push({start, line: `| ${fmt(start)}${end} | SFX | \`${c.sound}\`${c.loop ? ' (Loop)' : ''} | ${c.note ?? ''} |`});
  }
  const who = voiceOf(s);
  if (who) {
    const start = s.from + Math.round(0.2 * FPS);
    rows.push({
      start: start + 0.5,
      line: `| ${fmt(start)} – ${fmt(s.from + s.frames)} | Stimme | ${who} | „${s.text}“ |`,
    });
  }
}
rows.sort((a, b) => a.start - b.start);

const md = `# Ton-Cues – Tag ${ep.day} (${id})

Gesamtlänge: ${fmt(total)} (${total} Frames @ ${FPS} fps). Zeiten als m:ss.s.

Die Tonspur ist noch leer. So kommen Töne hinein:
- **SFX:** Datei nach \`public/sfx/\` legen und in \`src/sfx.ts\` eintragen (z. B. \`gong: 'sfx/gong.wav'\`).
- **Stimme:** Aufnahme nach \`public/voice/${id}/\` legen und bei der Szene in \`episodes/${id}.json\` \`"voice": "voice/${id}/02.mp3"\` setzen. Sie startet 0,2 s nach Szenenbeginn.

| Zeit | Spur | Sound / Sprecher | Hinweis / Text |
|---|---|---|---|
${rows.map((r) => r.line).join('\n')}

## Szenen

| # | Start | Länge | Typ | Inhalt |
|---|---|---|---|---|
${scenes
  .map(
    (s) =>
      `| ${s.index} | ${fmt(s.from)} | ${s.duration} s | ${s.type} | ${
        s.text ?? (s.type === 'intro' ? `Tag ${ep.day} – ${s.subtitle}` : [...(s.lines ?? []), s.punch].join(' '))
      } |`,
  )
  .join('\n')}
`;

const out = resolve('episodes', `${id}.cues.md`);
writeFileSync(out, md);
console.log(`Cue-Liste: ${out}`);
