# Gestrandet im Zug – Remotion şablonu

1080×1920, 30 fps YouTube Shorts serisi. Her bölüm `episodes/day-XX.json` dosyasından üretilir. Şablon kodu bölümden bölüme değişmez.

## Komutlar

```bash
npm install
npm run dev                        # Remotion Studio (önizleme)
npm run render -- day-01           # out/day-01.mp4 + out/stills/day-01/*.jpg
npm run render -- day-01 --stills  # sadece kontrol ekran görüntüleri
npm run cues -- day-01             # episodes/day-01.cues.md (ses listesi)
npm run typecheck
```

Chromium indirilemeyen ortamlarda: `BROWSER_EXECUTABLE=/yol/headless_shell npm run render -- day-01`

## Yeni bölüm (Tag 2, 3 …)

1. `episodes/day-01.json` dosyasını `episodes/day-02.json` olarak kopyala ve içeriği değiştir.
2. `src/episodes.ts` dosyasına bir satır ekle.
3. `npm run render -- day-02`

## JSON alanları

Her sahne (`intro`, `scenes[]`, `cliffhanger`) şu alanları alabilir. Bir alan verilmezse önceki sahnedeki değer geçerli kalır.

| Alan | Etkisi |
|---|---|
| `duration` | Sahne süresi (sn). Video süresi bunların toplamıdır. |
| `delay` | Göstergenin yeni değeri, sayarak yükselir. |
| `resources` | `kaffee`, `brezeln`, `steckdosen`, `wlan` (0–4) |
| `clock`, `location`, `ticker` | Göstergedeki saat, haritadaki konum ve kayan yazı |
| `night` | 0 = gündüz, 1 = gece (geçiş yumuşak) |
| `stop` / `go` | Tren frenleyip durur / yeniden hareket eder |
| `wagen`, `label`, `marker`, `crowd` | Haritada vagon vurgusu, üstte etiket, vagonun ortasında işaret, yolcuların işarete doğru toplanması |
| `sfx` | Ses ipuçları (`at` sahne başına göre sn) |
| `voice` | Seslendirme dosyası (`public/` altında) |
| `still: true` | Bu sahneden kontrol amaçlı ekran görüntüsü alınır |

Sahne tipleri: `diary` (Platz 47 günlüğü), `durchsage` (`urgent: true` = kırmızı/turuncu alarm), `mapEvent` (vagon olayı).

## Ses

Şu an ses dosyası yok. Videodaki ses izi sessiz.
- Hangi saniyede hangi ses girecek: `episodes/day-01.cues.md`
- Efektleri eklemek için: dosyayı `public/sfx/` klasörüne koy ve `src/sfx.ts` içindeki ilgili `null` değerini dosya yoluyla değiştir.
- Seslendirmeyi eklemek için: dosyayı `public/voice/day-01/` klasörüne koy ve sahneye `"voice": "voice/day-01/02.mp3"` alanını ekle.

## Tasarım / marka

Tren, gösterge ve renkler özgün tasarım. DB logosu, DB fontu veya DB kırmızısı kullanılmadı. Fontlar Inter ve JetBrains Mono (her ikisi de OFL lisanslı), `public/fonts/` klasöründe yerel olarak duruyor.
