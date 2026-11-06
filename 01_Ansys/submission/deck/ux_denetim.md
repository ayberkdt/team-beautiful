# UX gate — Team Beetiful, Ansys 4-minute deck

## Kapı 1 · GÖREV BÜTÇESİ (written before the build script)

```
GÖREV BÜTÇESİ — Ansys 4:00 deck, 9 slides            (yüzey: slayt, 20 × 11.25 in, template 16:9)
Birincil görev(ler)       : 1) jury understands problem → solution → value in 4:00
                            2) jury can check every number against the submitted report   Pareto · Occam
Birincil eylem            : none (projected talk; no interactive element)                  Von Restorff → 1 accent element per slide
Eylem / görünüm           : ≤ 5     · planlanan: 0                                         Hick
Üst düzey gezinti         : ≤ 7     · planlanan: 0 (linear deck)                           Hick · Miller
Seçenek kümesi            : ≤ 5     · planlanan: 0                                         Seçim Yükü
Form alanı / adım         : ≤ 7     · items per group on a slide ≤ 7                        Miller · Parkinson
Geri bildirim             : no transitions, no animation (0 ms)                             Doherty
Stil bütçesi              : ≤ 6 punto per slide, ≤ 8 deck-wide
                            display 96 / 60 / 40 (+ template cover 34) · body 28 / 24 / 18 (18 = template footer)
                            1 accent tone #7C2480 (template pill) · ink #400941 (template) · grey #595959
                            0 shadow · 0 gradient · 1 corner radius (light card fill #F5EEF5)   Benzerlik · Prägnanz
Sisteme yüklenen karmaşıklık : figures are cropped from the report files by the build script;
                            footer team name + slide number set by script; overflow is measured
                            by the script with the real Montserrat metrics; seconds per slide are
                            computed from note word counts                                      Tesler
```

No budget overrun planned. The report has 8 requirement rows (Table 1); slide 3 splits
them into 2 groups (3 load tiles + 4 limit tiles + 1 line) so no group exceeds 7.

## Kapı 3 · YASA DENETİMİ

```
YASA DENETİMİ — Team_Beetiful_Ansys_4min.pptx (9 slides) · 2026-11-05 · denetleyici: koşmadı (yüzey: slayt/.pptx;
ux-yasa-denetimi.mjs yalnız HTML okur). Ölçüm kaynakları: build_check.txt (build_ansys_deck.py: Montserrat
metrikleriyle taşma + çakışma + punto + süre), python-pptx şekil sayımı, png/slide01–09.png göz testi.
```

Sonuç: 20/20 yasa ölçüldü · 0 HATA · 1 UYARI (1 gerekçeli) · 2 kapsam dışı · karar: **TESLİM**

| #  | Yasa | Ölçüm (sayı/gözlem) | Eşik | Durum | Gerekçe (yalnız UYARI) |
|----|------|---------------------|------|-------|------------------------|
| 1  | Hick | eylem 0 · gezinti 0 (doğrusal deste) · üst düzey grup/slayt max 3 (s2 hero/sağ sütun/soru; s3 şekil/yük/limit; s4 huni/kart/geri ödeme; s7 karo/yöntem/modellenmeyen) | ≤ 5 eylem · ≤ 7 | geçti | |
| 2  | Fitts | etkileşimli hedef 0 (yansıtılan deste) | ≥ 44 px | kapsam dışı | |
| 3  | Jakob | şablon düzeni korundu: başlık sol üst, alt bilgi tarih/takım/sayfa, kapak→içerik→kapanış; sapma 0; ana şablon ve 11 düzen C14N ile şablonla birebir (0 fark) | 0 sapma | geçti | |
| 4  | Seçim Yükü | seçenek kümesi yok; s4 aday kümesi 3, karar işaretli ("Selected") | ≤ 5 ya da varsayılan | geçti | |
| 5  | Yakınlık | grup içi: sayı→etiket 0.05 in, grup başlığı→ilk sayı 0.10 in; gruplar arası 0.45–0.75 in (s3 0.45, s8 0.75) → iç:dış ≤ 1:4.5; s7 karo iç öğe aralığı 0.10 in / karolar arası 0.30 in = 1:3 | ≤ 1:2 | geçti | |
| 6  | Benzerlik | slayt başına punto max 6 (s2), diğerleri 1–5; deste: görüntü 96/60/40 (+ şablon kapak 34) · gövde 28/24/18 = betik 6 punto, kapakla 7; köşe yarıçapı 1 (0.12 in); gölge 0; düğme stili 0 | ≤ 6/slayt · ≤ 8 deste · ≤ 4 · ≤ 2 | geçti | |
| 7  | Tekdüze Bağlılık | kart/slayt max 3 (s4, s7); iç içe kart 0 | ≤ 12 · 0 | geçti | |
| 8  | Ortak Bölge | tek öğeli kutu 0 (s9 adım kutuları kaldırıldı: önce 4 → şimdi 0, tek satır ok dizisi); üst düzey bölge/slayt max 3 | 0 · ≤ 4 | geçti | |
| 9  | Prägnanz | cam 0 · ışıma 0 · eklenen degrade 0 · gölge 0 (şablon illüstrasyonları şablona ait, değişmedi) | 0 · 0 · ≤ 3 | geçti | |
| 10 | Von Restorff | vurgu tonu #7C2480 slayt başına 1 öğe: s2 "97 %", s3 "1.65 mm", s4 "Selected", s5 "Final geometry", s6 "27 %", s7 "78.5 MPa", s8 "−72 %", s9 "−72 %" (s9 "Thank you" ilk sürümde vurguluydu: önce 2 → şimdi 1); kapak 0 | 1/slayt | geçti | |
| 11 | Miller | grup başına öğe max 4 (s3 limitler 4, s4 huni 4, s7 modellenmeyen 4, s9 adım 4); tablo 0 | ≤ 7 | geçti | |
| 12 | Sıra Konumu | ilk içerik slaytı = problem (97 %), son slayt = ana fikir + 3 sonuç sayısı + sonraki adım; "Teşekkürler" tek başına değil | birincil mesaj başta/sonda | geçti | |
| 13 | Doherty | slayt geçişi/animasyon 0 (`<p:transition>`/`<p:timing>` sayımı 0) | ≤ 300 ms · 0 | geçti | |
| 14 | Zeigarnik | 9 slayt; her içerik slaytında alt bilgi sayfa no 2–9 (şablon); konuşma bölümleri sabit sırada | ≥ 3 adımda gösterge | geçti | |
| 15 | Zirve-Son | zirve s8 (−72 %, 114 kg, 38 t), son s9 (tek cümle fikir + sonraki adım + soru çağrısı) | zirve ve son tasarlanmış | geçti | |
| 16 | Parkinson | form 0; süre kutusu: notlar 228 s (3:48) ≤ 230 s hedef, 4:00 kesim; konuşma hızı 2.19–2.30 kelime/s | ≤ 230 s · ≤ 2.3 k/s | geçti | |
| 17 | Tesler | kırpma, alt bilgi no, taşma/çakışma, süre ve kelime hızı betikte hesaplanıyor; jüri raporu okumadan her sayıyı birim + etiketle görüyor; kaynak satırı her slaytta | her yük sistemde | geçti | |
| 18 | Postel | girdi 0; çıktı tek biçim: binlik ayırıcı ve sayı–birim arası bölünmez boşluk (keep_together), birimler SI, "%" önünde boşluk tüm slaytlarda | tek biçim | geçti | |
| 19 | Occam | betik öğesi/slayt max 26 (s4), eşlenemeyen öğe 0 (her öğe başlık iddiasına ya da kaynağa hizmet ediyor); slayt kelime sayısı (kaynak hariç) 6–90, max s4 90 | ≤ 150 öğe · 0 | UYARI | s3/s4/s7 83–90 kelime: hepsi sayı + kısa etiket, paragraf yok; rapordaki 8 gereksinim ve 3 doğrulama sonucu tek slayta sığmak zorunda. |
| 20 | Pareto | içerik alanının ≥ %96'sı başlık iddiasına hizmet ediyor (kalan: 0.32 in kaynak şeridi ≈ %4); s6'da şekil + 3 sayı içerik alanının %68'i | ≥ %60 | geçti | |

Riskler (yalnız kararı değiştirebilecekler):
- En küçük punto 18 pt (kaynak satırları, s3 şekil altı); slayt 20 in genişlikte, yani 10 in slayttaki 9 pt'ye eşdeğer. Şablonun kendi alt bilgisi de 18 pt. Mesaj taşıyan metin ≥ 24 pt.
- Montserrat Regular şablona gömülü değil (yalnız Bold gömülü); bu makinede Office bulut yazı tipi olarak var. Sunum bilgisayarında Office 365 yoksa gövde metni yedek yazı tipine düşebilir; satır kırılımı değişebilir.
- Fig. 2 içindeki eksen yazıları rapordaki görüntüden geldiği için ~14 pt; mesajı sağdaki 60 pt sayılar taşıyor.
- Göz testi 1920 px PNG üzerinde yapıldı (png/slide01–09.png); projeksiyonda kontrol edilmedi.
