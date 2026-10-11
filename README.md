# Gestrandet im Zug – kısa film boru hattı

YouTube Shorts serisi, 1080×1920, 30 fps. Her bölüm bir senaryo dosyasından (`episodes/day-XX.json`) üretilir.

```
episodes/day-01.json ──► Blender (EEVEE) ──► public/renders/day-01/<çekim>/0001.jpg …
   (çekim listesi)        3D çekimler            │
                                                  ▼
                          Remotion ──► out/day-01.mp4 (altyazı, anons, HUD, cliffhanger)
```

## Kurulum

1. `npm install`
2. **Blender 5.x** kur ([blender.org](https://www.blender.org/download/)). Hazır `.blend` dosyaları Blender 5.2 ile üretildi.
   Daha eski bir sürüm (4.2+) kullanacaksan önce `npm run assets -- all` ile kütüphaneyi kendi sürümünde yeniden üret.
3. Blender PATH'te değilse yolunu ver:
   - Windows: `set BLENDER=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`
   - macOS: `export BLENDER=/Applications/Blender.app/Contents/MacOS/Blender`

## Final render (ekran kartlı bilgisayarda)

```bash
npm run shots -- day-01 --quality final      # 1080×1920 Blender çekimleri, hareket bulanıklığı ve ışın izleme açık
npm run render -- day-01                     # out/day-01.mp4 + out/posters/day-01/*.jpg
```

Kalite seçenekleri: `draft` (360×640), `preview` (540×960), `final` (1080×1920).
Diğer seçenekler:
- `--shots s04,s07`: sadece belirtilen çekimleri render eder.
- `--step 2`: her ikinci kareyi render eder (hızlı önizleme).
- `--stills`: her çekimden tek bir kontrol görüntüsü alır (`out/stills/`).
- `--save-blend`: her çekimin animasyonlu `.blend` dosyasını `out/shots/` altına kaydeder. Blender'da açıp elle ince ayar yapabilirsin.

Önizleme: `npm run dev` (Remotion Studio). Henüz render edilmemiş çekimler storyboard kartı olarak görünür.

## Kütüphane: her şey bir kez üretilir

| Klasör | İçerik |
|---|---|
| `assets/sets/` | `wagen5` (2+2 oturma düzeni), `wagen6` (masalı bölüm), `wagen7` (Bordbistro), `wagen1` (1. Klasse), `aussen` (tren dıştan), `umgebung` (tarla, ray, direkler) |
| `assets/characters/` | `platz47`, `zugchef`, `rentner`, `businessmann`, `studentin`, `fahrgast_a`–`d` |
| `assets/props/` | Kahve bardağı, laptop, telefon, "100" kartı, Brezel |

Kütüphaneyi yeniden üretmek ve kontrol görüntüsü almak için:

```bash
npm run assets -- all --lookdev
npm run assets -- chars --only rentner --lookdev
```

Yeni karakter eklemek için `blender/lib/cast.py` dosyasına bir giriş ekle. Yeni vagon için `blender/lib/wagon.py` içindeki `WAGONS` listesine ekle.

## Senaryo (çekim listesi)

```jsonc
{
  "id": "s07", "duration": 2.8, "set": "wagen6", "time": "nachmittag",   // tag | nachmittag | abend | nacht
  "camera": { "type": "close", "on": "zugchef", "angle": -25, "dist": 1.0, "lens": 40, "fstop": 2.2, "push": 0.06 },
  "cast": [
    { "id": "zugchef", "mark": "G1", "pose": "stand_talk", "expr": "worried", "look": "platz47", "facing": 270,
      "keys": [{ "t": 2.1, "expr": "smile", "pose": "stand" }] },
    { "id": "platz47", "mark": "T3La", "pose": "sit_talk", "expr": "worried", "look": "zugchef" }
  ],
  "lines": [{ "who": "zugchef", "kind": "say", "t": 0.2, "d": 1.9, "text": "Das kann ich Ihnen leider nicht sagen." }]
}
```

- **Kamera tipleri:**
  - `preset` (setteki hazır kameralar)
  - `free` (`pos` ve `target` verilir)
  - `close` (bir karakterin yakın planı)
  - `ots` (omuz üstü: `from` → `to`)
  - `two` (ikili çekim)

  Kamera hareketleri: `push`, `drift`, `shake`, `fstop` (alan derinliği).
- **İşaretler:**
  - `T{n}{L|R}{a|b|c|d}`: masalı bölüm
  - `R{n}{L|R}{w|a}`: koltuk sırası
  - `G{y}`: koridorda ayakta
  - `STEH1–3`, `BAR1–3`, `BAR_personal`: Bistro
- **Pozlar:** `stand`, `stand_talk`, `arms_crossed`, `point`, `raise_card`, `shrug`, `hands_up`, `sit`, `sit_table`, `sit_talk`, `sit_phone`, `sit_back` … (`blender/lib/character.py`)
- **İfadeler:** `neutral`, `smile`, `grin`, `annoyed`, `angry`, `surprised`, `shocked`, `worried`, `smug`, `tired`, `determined`, `panic`, `sceptical`
- **Bakış (`look`):** başka bir karakter, `camera`, `window`, `ceiling`, `down` ya da `[x,y,z]` koordinatı
- **Hareket:** `keys` içinde `"move": "G1"` (ya da `[x,y,z]`), `"dur"` ve `"gait": "walk" | "run"`
- **Replik türleri:**
  - `say`: konuşulan replik; altyazı çıkar ve ağız hareket eder
  - `vo`: Platz 47'nin iç sesi
  - `durchsage`: anons (`urgent: true` = alarm)

## Ses

Videonun ses izi şimdilik boş. `npm run cues -- day-01` komutu `episodes/day-01.cues.md` dosyasını üretir; içinde efektler ve tüm replikler saniye saniye listelenir.
- **Efektler:** dosyayı `public/sfx/` klasörüne koy ve `src/sfx.ts` içine kaydet.
- **Sesler:** dosyayı `public/voice/day-01/` klasörüne koy ve ilgili repliğe `"voice": "voice/day-01/s07.mp3"` alanını ekle. Karakterlerin ağız hareketleri zaten bu zaman aralıklarına göre animasyonlu.

## Marka notu

Tren, üniforma, gösterge ve kart tamamen özgün tasarım. DB logosu, DB fontu ve DB kırmızısı kullanılmadı; vurgu rengi amber (#FF9F1C).
