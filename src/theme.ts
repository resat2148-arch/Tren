// Eigene Farbwelt – bewusst ohne Bahn-Rot.
export const theme = {
  bg: '#0B0E13',
  bgTop: '#151B25',
  panel: '#11161D',
  panelBorder: '#242C38',
  ledPanel: '#07090C',
  ledOff: '#1F1810',
  amber: '#FF9F1C',
  amberDim: '#8A560F',
  amberGlow: 'rgba(255, 150, 20, 0.55)',
  alert: '#FF5B2E',
  text: '#ECE8E1',
  muted: '#8B94A3',
  fontSans: 'Inter, "Helvetica Neue", Arial, sans-serif',
  fontMono: '"JetBrains Mono", "DejaVu Sans Mono", monospace',
};

// Raster für 1080×1920 mit Rücksicht auf die Shorts-Bedienelemente
// (oben Suche/Kamera, rechts Like-Spalte, unten Titelzeile).
export const layout = {
  side: 60,
  fullWidth: 960,
  lowerWidth: 880, // unterhalb der Karte bleibt rechts Platz für die Like-Spalte
  pillTop: 96,
  boardTop: 186,
  boardHeight: 310,
  mapTop: 526,
  mapHeight: 340,
  resourcesTop: 896,
  cardTop: 1136,
};
