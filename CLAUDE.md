# Serie: "Gestrandet im Zug" (Arbeitstitel) — YouTube Shorts

Bu dosya Claude Code için proje özetidir. Proje klasörüne `CLAUDE.md` olarak koy.

## Konsept
Köln → Hamburg hattında bir hızlı tren tarlanın ortasında duruyor ve bir daha hareket etmiyor. Yolcular günler içinde kendi küçük toplumlarını kuruyor. Deutsche Bahn hicvi + gün gün hayatta kalma serisi. Her bölüm = 1 gün ("Tag X"), her bölüm bir sürpriz/merak sorusuyla biter.

- Hedef kitle: Almanya, Almanca
- Platform: YouTube Shorts (sonra Reels/TikTok)
- Yayın: her gün aynı saatte

## Yasal/marka notu
DB logosu, DB kurum fontu ve DB'nin birebir renk paleti KULLANILMAYACAK. Tren, gösterge ve anons tasarımı özgün olacak; gecikme anonsu tarzı hicvi zaten anlatıyor. Seri adında "ICE" yerine nötr "Zug" tercih edildi.

## Teknik özellikler
- Remotion (React + TypeScript)
- 1080×1920, 30 fps, bölüm başına 30–50 sn
- Veri odaklı: her bölüm `episodes/day-XX.json` dosyasından üretilir; şablon kodu değişmez
- Render: `npx remotion render` ile her gün için ayrı MP4

## Görsel bileşenler
1. **DayCounter** — ilk karede büyük "Tag X", sonra köşede küçük
2. **TrainMap** — vagonların kuşbakışı planı (Wagen 5, 6, 7, 1. Klasse), yolcular nokta/ikon; olaylar ilgili vagonda vurgulanır
3. **DelayBoard** — turuncu LED tarzı gösterge ("+20 Min" → "+180 Min"), sayı yukarı sayarak animasyonlanır
4. **ResourceBars** — Bordbistro stoğu (Kaffee, Brezeln), freie Steckdosen, WLAN sinyali
5. **Durchsage** — anons balonu + gong sesi (özgün bir chime, DB gongu değil)
6. **DiaryText** — anlatıcı "Platz 47"nin günlük metni, daktilo efektiyle
7. **CliffhangerCard** — son 3 sn, kararan ekran + son cümle

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
