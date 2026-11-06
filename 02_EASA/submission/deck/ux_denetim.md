# UX denetimi · Team_Beetiful_EASA_4min.pptx

## GÖREV BÜTÇESİ (tasarımdan önce yazıldı)

```
GÖREV BÜTÇESİ — EASA 4:00 sunumu, 9 slayt          (yüzey: slayt, 16:9, 20 × 11.25 in, projeksiyon)
Birincil görev(ler)       : 1) jüri sorunu ve kapsamı anlar  2) seçimi ve tasarımı anlar  3) değeri, sınırı, sonraki adımı hatırlar   Pareto · Occam
Birincil eylem            : yok (izleyici tıklamaz); slayt başına 1 iddia başlığı = tek mesaj               Von Restorff
Eylem / görünüm           : 0 tıklanır hedef · içerik grubu ≤ 3 sütun/kutucuk                              Hick
Üst düzey gezinti         : yok; 9 slayt, akış sorun → kanıt → seçim → tasarım → mantık → kurulum → sonuç → değer   Hick · Miller
Seçenek kümesi            : seçim tablosu 6 satır, seçilen sütun ayrı, 1 vurgulu satır (Barrier)             Seçim Yükü
Form alanı / adım         : form yok · kurulum 12 adım = 3 grup × 4                                         Miller · Parkinson
Geri bildirim             : animasyon/geçiş 0                                                               Doherty
Stil bütçesi              : gövde ≤ 3 punto (26/22/18) + görüntü 2 (34 başlık, 54 sayı) · 1 vurgu tonu (şablon A95FA0) · 0 gölge · 0 yarıçap   Benzerlik · Prägnanz
Sisteme yüklenen karmaşıklık : konuşma metni slayta değil konuşmacı notuna; sayılar ve rapor figürleri taşır; şablon başlık/altbilgi sabit   Tesler
Süre bütçesi              : ≤ 230 s konuşma (4:00 kesim, 10 s yedek) · ≤ 2.4 kelime/s                         Parkinson
```

Bütçe aşımı yok. Kurulum 12 adım (rapor Tablo 2) → 3 grup × 4 adım (Miller parça boyutu 3–5).

## YASA DENETİMİ — Team_Beetiful_EASA_4min.pptx · 2026-11-05 · denetleyici: koşmadı (yüzey: slayt; `ux-yasa-denetimi.mjs` yalnız HTML okur)

Ölçüm kaynakları: `build_easa_deck.py` METRICS çıktısı (punto, kelime, sol eksen, sınır dışı/çerçeve dışı şekil),
pptx XML taraması (geçiş/animasyon), PowerPoint COM ile 1600 px PNG (`png/slide01–09.png`) göz kontrolü.

Sonuç: 20/20 yasa ölçüldü · 0 HATA · 3 UYARI (3 gerekçeli) · karar: TESLİM

| #  | Yasa             | Ölçüm (sayı/gözlem) | Eşik | Durum | Gerekçe (yalnız UYARI) |
|----|------------------|---------------------|------|-------|------------------------|
| 1  | Hick             | tıklanır hedef 0; slayt başına paralel grup en çok 3 (kutucuk/sütun); tablo 6 satır | ≤ 5 grup · ≤ 7 satır | geçti | |
| 2  | Fitts            | kapsam dışı: projeksiyon slaytı, etkileşimli hedef yok | — | kapsam dışı | |
| 3  | Jakob            | şablon düzeni korundu: kapak alanları, üst bant, "POWERED BY" hapı, altbilgi tarih/takım/sayfa; başlık sol üstte her slaytta aynı yerde (x 0.9 in, y 2.28 in); sapma 0 | 0 sapma | geçti | |
| 4  | Seçim Yükü       | slayt 4: 6 seçenek satırı, seçilen "Our choice" sütununda kalın, reddedilen gerekçeli; vurgulu satır 1 | ≤ 5 ya da varsayılan işaretli | geçti | |
| 5  | Yakınlık         | kutucuk içi sayı→etiket 0 in (bitişik), kutucuklar arası 0.7 in; slayt 7 adım arası 0.07 in, sütun arası 0.7 in; başlık→içerik 0.22 in | iç:dış ≤ 1:2 | geçti | |
| 6  | Benzerlik        | kendi punto: görüntü 2 (34, 54) · gövde 3 (26, 22, 18); şablonun sabit puntoları (altbilgi 18/21, kapak 24/34, "POWERED BY/EUROAVIA") ayrı ve değiştirilmedi; metin rengi 3 (400941, 3A3A3A, A95FA0); gölge 0; yarıçap 0; çizgi stili 1 | gövde ≤ 5 · ≤ 2 gölge · ≤ 4 yarıçap | geçti | |
| 7  | Tekdüze Bağlılık | sütun eksenleri 0.9 / 7.2(7.5) / 13.5(13.8) in tüm 3-sütunlu slaytlarda aynı; iç içe kart 0; sol eksen sayısı slayt başına 3–4 (sütun + iç girinti) | ≤ 3 sütun ekseni · iç içe 0 | geçti | |
| 8  | Ortak Bölge      | dolgulu kutu 1 (slayt 4 "Barrier" satırı, 3 hücre); tek öğeli kutu 0 (slayt 2 bandı önce 1 → kaldırıldı, şimdi 0) | tek öğeli 0 · bölge ≤ 4 | geçti | |
| 9  | Prägnanz         | cam 0 · ışıma 0 · kendi degrade 0 · dekoratif şekil yalnız şablonun; figür arka planı saydam (beyaz kutu 0) | 0 · 0 · ≤ 3 | geçti | |
| 10 | Von Restorff     | slayt başına 1 iddia başlığı + en büyük öğe sayı/figür; vurgu dolgusu 1 (slayt 4); doygun ton 2 (şablon moru + mor çubuk); kırmızı/yeşil yalnız rapor figürlerinde (anlamsal) | 1 vurgu · ≤ 2 ton | geçti | |
| 11 | Miller           | liste en çok 4 madde/grup (slayt 7, 9); tablo 3 sütun × 6 satır; kutucuk 3 | ≤ 7 | geçti | |
| 12 | Sıra Konumu      | ilk içerik slaytı: sorun (G-MIIL, AD); son slayt: değer + sınır + sonraki adım, iddia başlığıyla ("Teşekkürler" tek başına değil) | açılış/kapanış taşıyıcı | geçti | |
| 13 | Doherty          | geçiş/animasyon 0 (pptx XML'de `<p:transition>`/`<p:timing>` 0 slayt) | 0 · ≤ 300 ms | geçti | |
| 14 | Zeigarnik        | sayfa numarası her içerik slaytında (2–9); kurulum adımları 1–12 numaralı, grup aralıkları başlıkta ("1–4", "5–8", "9–12") | ≥ 3 adımda gösterge | geçti | |
| 15 | Zirve-Son        | zirve: slayt 8 "71×"; son: slayt 9 değer/sınır/sonraki adım + "Thank you. Questions?"; kapanış en sade 3 sütun | son ekran tasarlı | geçti | |
| 16 | Parkinson        | konuşma 229 s (≤ 240, 11 s yedek); 4 konuşmacı 60/56/57/56 s; slayt başına hedef saniye notta; hız 2.20–2.38 kelime/s | ≤ 230 s · ≤ 2.4 k/s | geçti | |
| 17 | Tesler           | izleyiciden girdi 0; anlatı notlara taşındı (slaytta 38–108 kelime, notta 14–79 kelime) | her girdiye gerekçe | geçti | |
| 18 | Postel           | tek sayı biçimi: binlik boşluk ("200 000", "1 000"), birimden önce boşluk ("70 mm", "38 %", "1.5 s"), çarpan bitişik ("71×", "2.8×"), aralık en tire ("0.45–0.85 kg") | tek biçim | geçti | |
| 19 | Occam            | kendi şekil sayısı slayt başına 11–31; eşlenemeyen öğe 0 (her öğe başlıktaki iddiaya hizmet eder); slayttaki kelime: 2→88, 3→38, 4→108, 5→44, 6→43, 7→138*, 8→64, 9→95 (*12 adım no + 12 ✓ dahil) | ≤ 150 öğe · 0 eşlenemeyen | UYARI | Slayt 4 (rapor Tablo 1) ve 7 (Tablo 2, görev "step-by-step" istiyor) 75 kelimeyi aşıyor; her hücre ≤ 6 kelime, ayrıntı konuşulmuyor, yalnız gruplar okunuyor. |
| 20 | Pareto           | figür/büyük sayı alanı içerik çerçevesinin %58–77'si (slayt 3, 5, 6, 8); metin slaytlarında (4, 7, 9) tüm alan tek tablo/3 sütun | ≥ %60 birincil | UYARI | Slayt 8'de %58: rapor Şekil 5 oranı (3.05:1) ve üç büyük sayı sütunu birlikte; boşluk notu taşıyor, figür büyütülse sayı sütunu küçülür. |

Ek göz kontrolü (her PNG'ye bakıldı, son tur 9/9): taşma 0, çakışma 0, kırpılma 0, altbilgi çizgisine (10.33 in) değen metin 0,
en küçük kendi punto 18 pt (slayt 4 tablo başlığı, slayt 7 kontrol satırı, slayt 8 not).

| UYARI (ek) | Gerekçe |
|---|---|
| Rapor figürlerinin en küçük yazısı slaytta ≈ 17–18 pt: 1600 px PNG'de rakam yüksekliği slayt 3 eksen 13 px, slayt 8 eksen 14 px; kendi 18 pt metnimizin rakam yüksekliği 14 px, slayt 6 "back to Taxi" satırı 19 px = kendi 18 pt satırımızla aynı. Şekil 1 eksen rakamları (≈ 17 pt) önerilen 18 pt'nin hemen altında | Kullanıcı isteği: "prefer report figures as they are". Figür değiştirilseydi datawiz kapısı gerekirdi; bu yüzden piksel içeriği değiştirilmedi, yalnız beyaz arka plan saydam yapıldı. |

Riskler (kararı değiştirebilecekler):
- Montserrat yerel olarak kurulu değil (Windows Fonts ve kayıt defterinde yok); PowerPoint render'ı bulut yazı tipiyle doğru çizdi. Sunum bilgisayarı çevrimdışıysa yazı tipi yedeğe düşer ve satır kırılmaları değişebilir. Sunumdan önce o makinede bir kez açın.
- Altbilgi tarihi 07/11/2026: Yönetmelik 1.1 §1.1 (s. 5) ve kitapçık s. 8 takım sunumlarını 7 Kasım'da gösteriyor (önceki 06/11 bir takım notundan alınmıştı, yanlıştı).
- Konuşma hızı kelime sayısından tahmin (2.3 kelime/s); gerçek prova ile ölçülmedi.

Önce/sonra izi: konuşma hızı 2.12–2.75 → 2.22–2.37 kelime/s; slayt 2 tek öğeli band 1 → 0; kapak metni ortalı → sola hizalı (şablon hizası);
slayt 5/6 üç satıra taşan etiket 2 → 0; slayt 9 yetim "2.0×" satırı 1 → 0.
