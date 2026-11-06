YASA DENETİMİ — par_cue_demo.html · 2026-11-06 · denetleyici koşuldu · 20/20 ölçüldü · 0 HATA · 0 UYARI · TESLİM

Göz testi ölçümleri tarayıcıda canlı DOM'dan alındı (1280×720 ve 375×812).

| # | Yasa | Ölçüm | Eşik | Durum |
|---|---|---|---|---|
| 1 | Hick | nav 0 · eylem 2 (Play, Sound) · seçim 3 radyo | ≤ 7 · ≤ 5 · ≤ 7 | geçti |
| 2 | Fitts | Play 160×44, radyo 168×44, Sound 104×44, çubuk 44 yüksek; metin girdisi yok | ≥ 44 px | geçti |
| 3 | Jakob | ILS benzeri çapraz ibre, Play/Pause, kaydırıcı, Space; imleç/kaydırma kaçırma 0 | 0 sapma | geçti |
| 4 | Seçim Yükü | canlı DOM 3 radyo, A işaretli (denetleyici JS ile kurulan için 0 sayıyor) | ≤ 5 ya da varsayılan | geçti |
| 5 | Yakınlık | grup içi 8 px / bölgeler arası 16 px = 1:2 | ≤ 1:2 | geçti |
| 6 | Benzerlik | denetleyici 2 punto (JS'siz) · yarıçap 2 · gölge 0; CSS jetonu 6 punto | ≤ 8 · ≤ 4 · ≤ 2 | geçti |
| 7 | Tekdüze Bağlılık | kart 0, iç içe 0 | ≤ 12 · 0 | geçti |
| 8 | Ortak Bölge | üst düzey bölge 3 (pilot, dış görünüm, replay); tek öğeli kutu 0 | 0 · ≤ 4 | geçti |
| 9 | Prägnanz | cam 0 · ışıma 0 · degrade 0 | 0 · 0 · ≤ 3 | geçti |
| 10 | Von Restorff | birincil 1 (Play) · doygun ton 0 | 1 · ≤ 2 | geçti |
| 11 | Miller | form alanı 0 · tablo 0 | ≤ 7 · ≤ 7 | geçti |
| 12 | Sıra Konumu | nav yok; denetim sırası ilk Play, son Sound | birincil görevler | geçti |
| 13 | Doherty | kare çizimi 0,9 ms; ibre geçişi 300 ms; 2× hızda kare aralığı 500 ms, ibre hareketi göstergedir | < 400 ms yanıt | geçti |
| 14 | Zeigarnik | bölüm göstergesi "2 of 4: Correcting" | ≥ 3 adımda gösterge | geçti |
| 15 | Zirve-Son | başarı MINIMUMS + son özet; boş ACQUIRING/STAND BY; hata LOST + GO AROUND; 3/3 ekran görüldü | 3/3 | geçti |
| 16 | Parkinson | zorunlu alan 0 | ≤ %50 | geçti |
| 17 | Tesler | zorunlu girdi 0; filtre, geçerlilik, ses önceliği otomatik | her girdiye gerekçe | geçti |
| 18 | Postel | metin girdisi yok | 0 · normalizasyon | geçti |
| 19 | Occam | 51 öğe; her biri okuma, izleme ya da replay görevine bağlı | ≤ 900 · 0 eşlenemeyen | geçti |
| 20 | Pareto | pilot %40 + dış görünüm + replay: üç bölge de birincil görev; 1280×720 kaydırmasız sığıyor | ≥ %60 | geçti |

Riskler: pilotla kullanılabilirlik testi yapılmadı. Ses Windows SAPI kaydı; hoparlörden dinleme testi yapılmadı (yazılı karşılığı ekranda).

Doğrulama: 329 karenin tamamı dolaşıldı, ibre/bayrak durumu veriyle uyuşmayan kare 0. 375 px'te yatay taşma yok.
