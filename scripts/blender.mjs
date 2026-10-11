// Startet ein Blender-Skript aus blender/ im Hintergrundmodus.
//   node scripts/blender.mjs render_shots.py day-01 --quality final
// Blender wird über $BLENDER gefunden (sonst "blender" im PATH).
// Alternativ: BLENDER_PY=/pfad/zu/python (Python mit pip-Paket "bpy").
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';

const [script, ...args] = process.argv.slice(2);
if (!script) {
  console.error('Aufruf: node scripts/blender.mjs <skript.py> [argumente]');
  process.exit(1);
}
const file = resolve('blender', script);
const py = process.env.BLENDER_PY;
const cmd = py ? py : process.env.BLENDER || 'blender';
const argv = py ? [file, ...args] : ['-b', '--factory-startup', '-P', file, '--', ...args];
const res = spawnSync(cmd, argv, {stdio: 'inherit'});
if (res.error) {
  console.error(`Blender nicht gefunden (${cmd}). BLENDER=/pfad/zu/blender setzen.`);
  process.exit(1);
}
process.exit(res.status ?? 0);
