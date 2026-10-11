// Datenschema einer Folge (episodes/day-XX.json).
// Alle Zeitangaben in Sekunden.

export type WagenId = 5 | 6 | 7 | '1. Klasse';

export type Resources = {
  kaffee: number; // Becher
  brezeln: number; // Stück
  steckdosen: number; // freie Steckdosen
  wlan: number; // Balken, 0–4
};

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
  at?: number; // relativ zum Szenenstart
  length?: number; // ohne Angabe: bis Dateiende
  loop?: boolean;
  volume?: number;
  note?: string; // Regieanweisung für die Cue-Liste
};

// Felder, die jede Szene setzen kann. Was nicht gesetzt ist, bleibt wie in der Szene davor.
export type SceneBase = {
  duration: number;
  clock?: string; // Uhrzeit auf der Anzeige, z. B. "15:48"
  location?: string; // Standort-Zeile auf der Karte
  delay?: number; // neue Verspätung in Minuten (zählt animiert hoch)
  resources?: Partial<Resources>;
  night?: number; // 0 = Tag, 1 = Nacht
  stop?: boolean; // Zug bremst in dieser Szene bis zum Stillstand
  go?: boolean; // Zug fährt in dieser Szene wieder an
  ticker?: string; // Lauftext unten in der Anzeige
  // Hervorhebung auf der Karte
  wagen?: WagenId;
  label?: string; // kurzes Schlagwort über dem Wagen
  marker?: string; // Markierung in der Wagenmitte, z. B. "1 Steckdose"
  crowd?: boolean; // Fahrgäste im Wagen drängen zur Markierung
  sfx?: SfxCue[];
  voice?: string; // Sprachaufnahme unter public/, z. B. "voice/day-01/02.mp3"
  still?: boolean; // Standbild für die Kontrolle rendern
};

export type IntroScene = SceneBase & {type: 'intro'; subtitle: string};
export type DiaryScene = SceneBase & {type: 'diary'; text: string};
export type DurchsageScene = SceneBase & {type: 'durchsage'; text: string; urgent?: boolean};
export type MapEventScene = SceneBase & {type: 'mapEvent'; wagen: WagenId; text: string};
export type CliffhangerScene = SceneBase & {
  type: 'cliffhanger';
  lines: string[];
  punch: string;
  teaser: string;
};

export type Scene = IntroScene | DiaryScene | DurchsageScene | MapEventScene | CliffhangerScene;

export type Episode = {
  day: number;
  route: {from: string; to: string};
  delay: {from: number; to: number};
  resources: Resources;
  resourcesMax?: Partial<Resources>;
  ticker: string;
  intro: Omit<IntroScene, 'type'>;
  scenes: (DiaryScene | DurchsageScene | MapEventScene)[];
  cliffhanger: Omit<CliffhangerScene, 'type'>;
};
