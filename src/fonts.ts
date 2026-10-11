import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Schriften liegen lokal in public/fonts (OFL), damit der Render offline funktioniert.
const faces = [
  {family: 'Inter', file: 'inter-latin-400-normal.woff2', weight: '400'},
  {family: 'Inter', file: 'inter-latin-600-normal.woff2', weight: '600'},
  {family: 'Inter', file: 'inter-latin-800-normal.woff2', weight: '800'},
  {family: 'JetBrains Mono', file: 'jetbrains-mono-latin-400-normal.woff2', weight: '400'},
  {family: 'JetBrains Mono', file: 'jetbrains-mono-latin-700-normal.woff2', weight: '700'},
  {family: 'JetBrains Mono', file: 'jetbrains-mono-latin-800-normal.woff2', weight: '800'},
];

export const loadFonts = () =>
  Promise.all(
    faces.map((f) =>
      loadFont({family: f.family, url: staticFile(`fonts/${f.file}`), weight: f.weight}),
    ),
  );
