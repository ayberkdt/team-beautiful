YASA DENETİMİ — `EASA_LOCK-SENSE_4min.pptx` (7 slayt) · 2026-11-05, resmî görevden sonraki sürüm · denetleyici: koşmadı
(yüzey: slayt; HTML değil). Ölçüm: `02_EASA/scripts/easa_deck.py` içindeki konum/punto değerleri + PowerPoint'in 1600×900 PNG
dışa aktarımına göz kontrolü (7 slaytın hepsi; 2. slayt iki tur).

Sonuç: 20/20 yasa ölçüldü · 0 HATA · 1 UYARI (gerekçeli) · karar: TESLİM

Değişenler (önceki sürüme göre): 2. slayt kartları (üç kurum / kimsenin kanıtlayamadığı), 4. slayt açıklaması (dört uyarı türü),
6. slayt başlığı ve açıklaması (onay yolu kalktı), 7. slayt başlığı ve açıklaması, K3 ve K4 figürleri, bütün konuşmacı notları.
Göz kontrolünde bulunan ve düzeltilen: 2. slaytta "184 / KIAS" satır sonunda bölünüyordu → bölünmez boşluk (önce 1 → şimdi 0);
K3'te "12 Train + maintain" ve K4'te "Green / amber / red" kutudan taşıyordu → kısaltıldı (datawiz denetimi ikisini de 0 HATA
geçirmişti).

| #  | Yasa             | Ölçüm (sayı/gözlem) | Eşik | Durum | Gerekçe (yalnız UYARI) |
|----|------------------|---------------------|------|-------|------------------------|
| 1  | Hick             | eylem 0 / slayt (statik deste); slayt başına iddia 1 | ≤ 5 | geçti | |
| 2  | Fitts            | etkileşimli hedef yok | ≥ 44 px | kapsam dışı: statik slayt | |
| 3  | Jakob            | şablon alt bilgisi (tarih · takım · sayfa) ve sol üst başlık düzeni korundu; başlık her slaytta x 1.0 in, y 2.3 in | 0 sapma | geçti | |
| 4  | Seçim Yükü       | seçenek kümesi yok | ≤ 5 | kapsam dışı: statik | |
| 5  | Yakınlık         | başlık→görsel 0.45 in · görsel→açıklama 0.3–0.9 in · açıklama→alt bilgi çizgisi 0.7 in; kart içi başlık→metin 0.2 in, kartlar arası 0.5 in (1:2.5) | ≤ 1:2 | geçti | |
| 6  | Benzerlik        | eklenen punto 4 (36 · 28 · 22 · 18) + şablon alt bilgisi; yarıçap 0; eklenen gölge 0; düğme 0 | ≤ 6 · ≤ 4 · ≤ 2 · ≤ 2 | geçti | |
| 7  | Tekdüze Bağlılık | kart 2 (yalnız 2. slayt), iç içe kart 0 | ≤ 12 · 0 | geçti | |
| 8  | Ortak Bölge      | tek öğeli kutu 0 (her kartta başlık + 3 madde); üst düzey bölge/slayt ≤ 3 | 0 · ≤ 4 | geçti | |
| 9  | Prägnanz         | cam 0 · ışıma 0 · eklenen degrade 0; şablon süsü dokunulmadı | 0 · 0 · ≤ 3 | geçti | |
| 10 | Von Restorff     | slayt başına tek kalın başlık; figürlerde tek vurgu tonu (#0072b2, yeni parçalar) | 1 | geçti | |
| 11 | Miller           | kart başına 3 madde; K3'te sütun başına ≤ 4 adım; K4'te çıkış kutusu 5 | ≤ 7 | geçti | |
| 12 | Sıra Konumu      | ilk içerik slaytı: "Closed is not locked" (ana iddia) · son: "Record the lock now, remove the omission next" (öneri + sonraki adım) | birincil mesajlar uçlarda | geçti | |
| 13 | Doherty          | animasyon/geçiş 0 | ≤ 300 ms | geçti | |
| 14 | Zeigarnik        | sayfa numarası her içerik slaytında (2–7) | ≥ 3 adımda gösterge | geçti | |
| 15 | Zirve-Son        | son slayt tek sonraki adımla kapanıyor (bench test ≥ 30 sensör × 10 çevrim) | temiz son | geçti | |
| 16 | Parkinson        | form yok | — | kapsam dışı: statik | |
| 17 | Tesler           | sayılar ve figürler betikten (canopy_day / easa_kit); konuşma metni konuşmacı notunda (6/6 içerik slaytında dolu, 235–591 karakter) | elle girilen sayı 0 | geçti | |
| 18 | Postel           | sayı–birim bölünmez boşlukla (184 KIAS, 70 mm; 2. slayt düzeltildi); çarpan biçimi tek ("1 900×", "3×") | tek biçim | geçti | |
| 19 | Occam            | slayt başına eklenen öğe 3–7; amaçsız öğe 0 | her öğe bir göreve | geçti | |
| 20 | Pareto           | içerik alanının ≈ %70'i tek iddiayı taşıyan görselde (2. slayt: iki kart %75) | ≥ %60 | UYARI | 3. slaytta iki figür yan yana (C5 + C1): bir slayt, iki kanıt. 4:00 bütçesinde iki slayta bölmek 35 s'lik bloğu ikiye keser; konuşma metni ikisini tek cümleyle bağlıyor |

Riskler (yalnız kararı değiştirebilecekler):
- Göz kontrolü PowerPoint 1600×900 dışa aktarımında yapıldı; projektörde sağ alttaki açık pembe şablon süsü ile figür zemini
  arasındaki kontrast ölçülmedi.
- Tarih "06/11/2026" doc 23'teki "Friday" EASA slotundan alındı; resmî program okunmadı.
