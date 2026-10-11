// Ton- und Sprecherliste einer Folge: npm run cues -- day-01  →  episodes/day-01.cues.md
import {readFileSync, writeFileSync} from 'node:fs';
import {resolve} from 'node:path';

const id = process.argv[2] ?? 'day-01';
const ep = JSON.parse(readFileSync(resolve('episodes', `${id}.json`), 'utf8'));
const fps = ep.fps ?? 30;
const fmt = (sec) => `${Math.floor(sec / 60)}:${(sec % 60).toFixed(1).padStart(4, '0')}`;
const NAMES = {platz47: 'Platz 47', zugchef: 'Zugchef', rentner: 'Rentner', businessmann: 'Businessmann',
  studentin: 'Studentin', ansage: 'Ansage (Durchsage-Stimme)'};

const rows = [];
const shots = [];
let start = 0;
const addSfx = (base, list, where) => {
  for (const c of list ?? []) {
    const t = base + (c.at ?? 0);
    const end = c.length ? ` – ${fmt(t + c.length)}` : '';
    rows.push({t, line: `| ${fmt(t)}${end} | SFX | \`${c.sound}\`${c.loop ? ' (Loop)' : ''} | ${where} | ${c.note ?? ''} |`});
  }
};
for (const s of ep.shots) {
  shots.push(`| ${s.id} | ${fmt(start)} | ${s.duration} s | ${s.set} | ${s.note ?? ''} |`);
  addSfx(start, s.sfx, s.id);
  for (const l of s.lines ?? []) {
    const who = l.kind === 'vo' ? `${NAMES[l.who] ?? l.who} (Off-Stimme)` : NAMES[l.who] ?? (l.who.startsWith('fahrgast') ? 'Fahrgast' : l.who);
    rows.push({t: start + l.t + 0.001, line: `| ${fmt(start + l.t)} – ${fmt(start + l.t + l.d)} | Stimme | ${who} | ${s.id} | „${l.text}“ |`});
  }
  start += s.duration;
}
shots.push(`| Cliffhanger | ${fmt(start)} | ${ep.cliffhanger.duration} s | – | ${[...ep.cliffhanger.lines, ep.cliffhanger.punch].join(' ')} |`);
addSfx(start, ep.cliffhanger.sfx, 'Cliffhanger');
const total = start + ep.cliffhanger.duration;
rows.sort((a, b) => a.t - b.t);

const md = `# Ton und Sprecher – ${ep.title} (${id})

Gesamtlänge: ${fmt(total)} (${Math.round(total * fps)} Frames @ ${fps} fps). Zeiten als m:ss.s.

So kommt Ton hinein:
- **SFX:** Datei nach \`public/sfx/\` legen und in \`src/sfx.ts\` eintragen (z. B. \`gong: 'sfx/gong.wav'\`).
- **Stimmen:** Aufnahme nach \`public/voice/${id}/\` legen und an der Zeile im Drehbuch \`"voice": "voice/${id}/s07.mp3"\` setzen.
  Die Münder der Figuren bewegen sich bereits während der Zeitfenster unten.

| Zeit | Spur | Sound / Sprecher | Shot | Hinweis / Text |
|---|---|---|---|---|
${rows.map((r) => r.line).join('\n')}

## Shots

| Shot | Start | Länge | Set | Inhalt |
|---|---|---|---|---|
${shots.join('\n')}
`;
const out = resolve('episodes', `${id}.cues.md`);
writeFileSync(out, md);
console.log(`Cue-Liste: ${out}`);
