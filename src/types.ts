// Drehbuch einer Folge (episodes/day-XX.json). Zeiten in Sekunden.
// Die 3D-Felder (set, cast, camera, props, motion …) liest nur Blender (blender/render_shots.py);
// Remotion nutzt Dauer, Dialoge, Durchsagen, HUD, Ortsangaben und Töne.

export type SoundId =
  | 'gong'
  | 'brake'
  | 'rail_loop'
  | 'crowd_murmur'
  | 'crowd_argue'
  | 'crowd_panic'
  | 'typing'
  | 'led_tick'
  | 'crickets'
  | 'impact'
  | 'cash';

export type SfxCue = {
  sound: SoundId;
  at?: number;
  length?: number;
  loop?: boolean;
  volume?: number;
  note?: string;
};

export type Line = {
  who: string; // Figuren-ID oder "ansage"
  kind: 'say' | 'vo' | 'durchsage';
  t: number;
  d: number;
  text: string;
  urgent?: boolean;
  voice?: string; // Aufnahme unter public/, z. B. "voice/day-01/s07.mp3"
};

export type Shot = {
  id: string;
  note?: string;
  duration: number;
  set: string;
  time?: string;
  slug?: string;
  titleCard?: boolean;
  poster?: boolean; // Kontrollbild für das Handy
  hud?: {delay?: number; clock?: string};
  lines?: Line[];
  sfx?: SfxCue[];
  [blenderOnly: string]: unknown;
};

export type FilmEpisode = {
  day: number;
  title: string;
  route: {from: string; to: string};
  fps: number;
  intro: {subtitle: string};
  shots: Shot[];
  cliffhanger: {
    duration: number;
    lines: string[];
    punch: string;
    teaser: string;
    sfx?: SfxCue[];
  };
};

export type RenderManifest = {
  shots: Record<string, {frames: number; step: number; res: [number, number]; quality: string}>;
};
