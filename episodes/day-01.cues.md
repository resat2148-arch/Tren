# Ton-Cues – Tag 1 (day-01)

Gesamtlänge: 0:40.5 (1215 Frames @ 30 fps). Zeiten als m:ss.s.

Die Tonspur ist noch leer. So kommen Töne hinein:
- **SFX:** Datei nach `public/sfx/` legen und in `src/sfx.ts` eintragen (z. B. `gong: 'sfx/gong.wav'`).
- **Stimme:** Aufnahme nach `public/voice/day-01/` legen und bei der Szene in `episodes/day-01.json` `"voice": "voice/day-01/02.mp3"` setzen. Sie startet 0,2 s nach Szenenbeginn.

| Zeit | Spur | Sound / Sprecher | Hinweis / Text |
|---|---|---|---|
| 0:00.0 – 0:12.5 | SFX | `rail_loop` (Loop) | Fahrgeräusch läuft bis zur Vollbremsung |
| 0:02.7 – 0:05.5 | SFX | `typing` | leises Tippen, solange der Text erscheint |
| 0:02.7 – 0:07.5 | Stimme | Platz 47 (Erzähler) | „Köln Hbf, Gleis 4. Abfahrt mit 20 Minuten Verspätung. Ich habe Platz 47, einen Kaffee und einen Plan: Hamburg, 17:52.“ |
| 0:07.5 | SFX | `gong` | eigener Ansage-Gong, drei Töne aufwärts |
| 0:07.6 – 0:08.8 | SFX | `led_tick` | Anzeige zählt +20 → +45 |
| 0:07.7 – 0:11.5 | Stimme | Ansage | „Sehr geehrte Fahrgäste, unsere Ankunft verzögert sich um 45 Minuten. Grund dafür sind Verzögerungen im Betriebsablauf.“ |
| 0:11.5 – 0:13.5 | SFX | `brake` | Bremsen kreischen, Zug kommt ruckartig zum Stehen |
| 0:11.7 – 0:16.0 | Stimme | Platz 47 (Erzähler) | „15:48. Vollbremsung. Kein Bahnhof, kein Signal. Nur Feld, so weit das Auge reicht.“ |
| 0:13.3 – 0:31.3 | SFX | `crowd_murmur` (Loop) | Gemurmel setzt ein und bleibt bis zur Nacht |
| 0:16.0 | SFX | `gong` |  |
| 0:16.1 – 0:17.3 | SFX | `led_tick` | Anzeige zählt +45 → +90 |
| 0:16.2 – 0:20.0 | Stimme | Ansage | „Sehr geehrte Fahrgäste, die Verspätung beträgt nun 90 Minuten. Grund dafür sind Verzögerungen im Betriebsablauf.“ |
| 0:20.2 – 0:25.0 | Stimme | Platz 47 (Erzähler) | „Ein Rentner mit BahnCard 100 übernimmt das Kommando. „Ich fahre seit 1987. Das ist noch gar nichts.““ |
| 0:25.0 | SFX | `gong` |  |
| 0:25.1 – 0:26.3 | SFX | `led_tick` | Anzeige zählt +90 → +180 |
| 0:25.2 – 0:29.0 | Stimme | Ansage | „Die Verspätung beträgt nun 180 Minuten. Grund dafür sind Verzögerungen im Betriebsablauf. Wir bitten um Ihr Verständnis.“ |
| 0:29.0 – 0:37.5 | SFX | `crickets` (Loop) | Grillen draußen auf dem Feld |
| 0:29.2 – 0:34.0 | Stimme | Platz 47 (Erzähler) | „Es wird dunkel. In Wagen 7 kämpfen elf Menschen um die letzte freie Steckdose. Das WLAN hat aufgegeben.“ |
| 0:30.2 – 0:33.7 | SFX | `crowd_argue` | Streit um die Steckdose |
| 0:34.0 | SFX | `gong` |  |
| 0:34.2 – 0:37.5 | Stimme | Ansage | „Das Bordbistro schließt in 5 Minuten.“ |
| 0:36.2 – 0:40.5 | SFX | `crowd_panic` | Stille, dann Aufschrei und Getrampel |
| 0:38.6 | SFX | `impact` | dumpfer Schlag genau auf „PANIK.“ |

## Szenen

| # | Start | Länge | Typ | Inhalt |
|---|---|---|---|---|
| 0 | 0:00.0 | 2.5 s | intro | Tag 1 – Ankunft planmäßig 17:52 |
| 1 | 0:02.5 | 5 s | diary | Köln Hbf, Gleis 4. Abfahrt mit 20 Minuten Verspätung. Ich habe Platz 47, einen Kaffee und einen Plan: Hamburg, 17:52. |
| 2 | 0:07.5 | 4 s | durchsage | Sehr geehrte Fahrgäste, unsere Ankunft verzögert sich um 45 Minuten. Grund dafür sind Verzögerungen im Betriebsablauf. |
| 3 | 0:11.5 | 4.5 s | mapEvent | 15:48. Vollbremsung. Kein Bahnhof, kein Signal. Nur Feld, so weit das Auge reicht. |
| 4 | 0:16.0 | 4 s | durchsage | Sehr geehrte Fahrgäste, die Verspätung beträgt nun 90 Minuten. Grund dafür sind Verzögerungen im Betriebsablauf. |
| 5 | 0:20.0 | 5 s | mapEvent | Ein Rentner mit BahnCard 100 übernimmt das Kommando. „Ich fahre seit 1987. Das ist noch gar nichts.“ |
| 6 | 0:25.0 | 4 s | durchsage | Die Verspätung beträgt nun 180 Minuten. Grund dafür sind Verzögerungen im Betriebsablauf. Wir bitten um Ihr Verständnis. |
| 7 | 0:29.0 | 5 s | mapEvent | Es wird dunkel. In Wagen 7 kämpfen elf Menschen um die letzte freie Steckdose. Das WLAN hat aufgegeben. |
| 8 | 0:34.0 | 3.5 s | durchsage | Das Bordbistro schließt in 5 Minuten. |
| 9 | 0:37.5 | 3 s | cliffhanger | 312 Fahrgäste. 12 Brezeln. PANIK. |
