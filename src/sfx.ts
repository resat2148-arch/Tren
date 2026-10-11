import type {SoundId} from './types';

// Platzhalter: Sobald eine Datei unter public/sfx/ liegt, hier den Pfad eintragen
// (z. B. gong: 'sfx/gong.wav'). Einträge mit null werden beim Rendern übersprungen.
export const SFX_FILES: Record<SoundId, string | null> = {
  gong: null, // eigener Ansage-Gong (kein Bahn-Gong!)
  brake: null, // Vollbremsung, Metall auf Metall
  rail_loop: null, // Fahrgeräusch, loopbar
  crowd_murmur: null, // Gemurmel im Wagen, loopbar
  crowd_argue: null, // Streit, zwei, drei Stimmen
  crowd_panic: null, // Aufschrei + Fußgetrampel
  typing: null, // leise Tastatur/Schreibmaschine
  led_tick: null, // Klicken der Anzeige beim Hochzählen
  crickets: null, // Grillen, Nacht auf dem Feld
  impact: null, // dumpfer Schlag für die Pointe
  cash: null, // Kasse/Münzen
};
