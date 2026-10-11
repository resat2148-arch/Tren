# Serie: "Gestrandet im Zug" (Arbeitstitel) — YouTube Shorts

Bu dosya Claude Code için proje özetidir. Proje klasörüne `CLAUDE.md` olarak koy.

## Konsept
Köln → Hamburg hattında bir hızlı tren tarlanın ortasında duruyor ve bir daha hareket etmiyor. Yolcular günler içinde kendi küçük toplumlarını kuruyor. Deutsche Bahn hicvi + gün gün hayatta kalma serisi. Her bölüm = 1 gün ("Tag X"), her bölüm bir sürpriz/merak sorusuyla biter.

- Hedef kitle: Almanya, Almanca
- Platform: YouTube Shorts (sonra Reels/TikTok)
- Yayın: her gün aynı saatte

## Yasal/marka notu
DB logosu, DB kurum fontu ve DB'nin birebir renk paleti KULLANILMAYACAK. Tren, gösterge ve anons tasarımı özgün olacak; gecikme anonsu tarzı hicvi zaten anlatıyor. Seri adında "ICE" yerine nötr "Zug" tercih edildi.

## Teknik özellikler (güncel: kısa film yapısı)
- **Blender 5.x (EEVEE)** = çekimler. Mekânlar ve karakterler bir kez üretilip `assets/` altına `.blend` olarak kaydedilir:
  - `assets/sets/`: `wagen5` (2+2 Großraum), `wagen6` (masalı bölüm, Platz 47 = `T3La`), `wagen7` (Bordbistro + tezgâh + vitrin), `wagen1` (1. Klasse, cam kapı `DOOR_1K`), `aussen` (tren dıştan), `umgebung` (tarla, ray, direkler)
  - `assets/characters/`: `platz47`, `zugchef`, `rentner`, `businessmann`, `studentin`, `fahrgast_a`–`fahrgast_d`
  - `assets/props/props.blend`: becher, laptop, handy, karte100, brezel
  - Kaynak kod: `blender/lib/` (wagon.py, exterior.py, character.py, cast.py, world.py). Yeniden üretmek: `npm run assets -- all`
- **Senaryo = JSON**: `episodes/day-XX.json` içinde çekim listesi (set, saat, kamera, oyuncular + işaret/poz/ifade/bakış, replikler, anonslar, efektler). Şablon kodu değişmez.
  - Pozlar ve ifadeler: `blender/lib/character.py` → `POSES`, `EXPRESSIONS`
  - Kamera tipleri: `preset`, `free`, `close`, `ots` (omuz üstü), `two` (ikili çekim); `push`, `drift`, `shake`, `fstop`
  - İşaretler (oturma/ayakta durma yerleri): `blender/lib/wagon.py` başındaki açıklama
- **Remotion = kurgu**: Blender çekimlerini birleştirir; altyazı, anons balonu, LED gecikme göstergesi (HUD), mekân başlığı, Tag-X başlığı ve cliffhanger kartını ekler.
- Komutlar: `npm run shots -- day-01 --quality final` (Blender) → `npm run render -- day-01` (Remotion MP4 + kontrol görüntüleri)
- 1080×1920, 30 fps, bölüm başına 30–50 sn

## Görsel bileşenler (Remotion katmanı)
1. **TitleCard / HUD** — ilk çekimde büyük "Tag X", sonra sol üstte küçük gösterge (saat + gecikme)
2. **HUD gecikme** — turuncu LED ("+20 Min" → "+180 Min"); değer artınca büyüyüp sayarak yükselir
3. **Durchsage** — anons balonu + gong (özgün chime, DB gongu değil)
4. **Subtitle** — replikler (konuşanın adıyla) ve Platz 47'nin iç sesi (daktilo)
5. **Slug** — mekân başlığı ("Wagen 7 · Bordbistro · 20:48")
6. **CliffhangerCard** — son 3 sn, kararan ekran + son cümle
(Eski kuşbakışı TrainMap/ResourceBars panosu kaldırıldı; vagonlar artık 3D sahne.)

## Ses
- Anlatıcı (Platz 47): Almanca TTS sesi (örn. ElevenLabs)
- Anonslar: ayrı, "anons" tonunda ikinci bir ses
- SFX: anons gongu, tren fren sesi, kalabalık uğultusu, kasa/para sesi (Brezel ticareti)
- Arka plan müziği yok

## Bölüm JSON şeması (öneri)
```json
{
  "day": 1,
  "delay": { "from": 20, "to": 180 },
  "resources": { "kaffee": 40, "brezeln": 60, "steckdosen": 8, "wlan": 1 },
  "scenes": [
    { "type": "diary", "text": "..." },
    { "type": "durchsage", "text": "..." },
    { "type": "mapEvent", "wagen": 7, "text": "..." }
  ],
  "cliffhanger": "..."
}
```

## Karakterler
- **Platz 47** — anlatıcı, sıradan bir yolcu
- **Der Zugchef** — kondüktör, otoriteyi korumaya çalışıyor
- **Rentner mit BahnCard 100** — her şeyi bildiğini düşünen emekli, liderlik iddiasında
- **1. Klasse** — kapıyı kapatıp ayrı yaşayan "elit" vagon

## Tag 1
- Ekranda "Köln → Hamburg", gösterge "+20 Min"
- Gösterge artar: +45, +90, +180. Her artışta anons: *"Grund dafür sind Verzögerungen im Betriebsablauf."*
- Tren bir tarlada duruyor, gece çöküyor
- Cliffhanger — anons: *"Das Bordbistro schließt in 5 Minuten."* Panik.

## Tag 2
- Sabah, tren hâlâ yerinde
- Brezel para birimine dönüşüyor: *"1 Brezel = 30 Min Steckdose."*
- 1. Klasse kapısını kapatıyor
- ResourceBars: Kaffee 12 Becher kaldı
- Cliffhanger: *"In Wagen 7 gibt es WLAN – aber nur für eine Person."*

## Tag 3
- Seçim: Zugchef vs. BahnCard-100-Rentner
- Rezervasyonlar tapu gibi: *"Ich habe Platz 63 reserviert. Der Tisch gehört mir."*
- Cliffhanger — anons: *"Wir setzen unsere Fahrt in Kürze fort."* Tren hareket ediyor… geriye doğru.

## İlk görev (Claude Code için)
1. Remotion projesini kur
2. Bileşenleri yukarıdaki listeye göre yap
3. `episodes/day-01.json` ile Tag 1'i render et
4. Tag 2 ve 3'ü aynı şablonla, sadece JSON değiştirerek üret
