# Trade-off figures — datawiz brief (5 Nov 2026)

```
SET SÖZLEŞMESİ — tradeoff.seti.json
Hedef              : springer-cift (174 mm ≤ 176 mm report text width, 9 pt, min 8 pt) — all trade-off figures
Varlıklar          : S275N (reference, grey context, solid) · Ti-8Al-1Mo-1V (selected, blue #0072b2, solid)
                     · Al 2618-T6 (eliminated, orange #e69f00, dashed)
Nicelikler         : vol = "Part volume (% of initial design)" x, 0–110 · co2 = "Life-cycle CO₂-eq (t)" y
                     · cost = "Material cost (USD)" y
Kategori sırası    : S275N, Al 2618-T6, Ti-8Al-1Mo-1V (organisers' report order)
Birim yazımı       : "Quantity (unit)"   · Ondalık: "."   · Panel harfi: profile default
```

```
FİGÜR BRİFİ — fig_tradeoff_table
Mesaj        : Only Ti-8Al-1Mo-1V meets every card requirement; Al 2618-T6 fails T > 300 °C (and oxidation/SCC).
Okur         : karma (jury of Ansys engineers)
Ortam/hedef  : rapor (Word, A4) → springer-cift 174 mm
Veri         : 3 materials × 11 criteria, organisers' Granta report p.5–13 (ranges) + 300 °C allowable [K]
Karşılaştırma: materials across each criterion (columns = materials so the eye compares along a row)
Biçim adayı  : booktabs-style table figure with pass/fail chips (double coded: light tone + word)
               · alternative: native Word table — chosen figure because the user asked for a visual
Tema         : akademik / Okabe–Ito (set)
```

```
FİGÜR BRİFİ — fig_tradeoff_breakeven
Mesaj        : Use phase dominates, so Ti beats the initial steel part at any volume below 164 %; an optimised
               steel part would have to reach 0.61 × the Ti volume to tie on CO₂, while Ti costs ~20× more per kg.
Okur         : karma
Ortam/hedef  : springer-cift 174 mm, two panels side by side
Veri         : linear models (organisers' eco formulas × density × price), x = volume 0–110 %
Karşılaştırma: (a) life CO₂ per material vs volume, with the initial steel level; (b) material cost vs volume
Biçim adayı  : line chart, direct end labels, reference line, one worked read-out (Ti 45 % → steel tie)
Tema         : set
```

## FİGÜR TESLİMİ (5 Nov 2026)

| Figür | Denetim | Göz | CVD |
|---|---|---|---|
| fig_tradeoff_table | 0 HATA · 0 UYARI | baktım: çakışma yok (ilk sürümde ✓/✗ glifleri fontta yoktu ve "Granta stage 2" hücreye biniyordu; denetim ikisini de görmedi, göz yakaladı) | ikili kodlama: şekil (● / ✖) + renk |
| fig_tradeoff_indices | 0 HATA · 0 UYARI · 2 BİLGİ (birimsiz eksenler: oran ve kategori, bilinçli) | baktım | tek seri |
| fig_tradeoff_breakeven | 0 HATA · 0 UYARI | baktım | protan/deutan/tritan/gri: üç çizgi ayrışıyor (Al kesikli + doğrudan etiket) |

Set: 0 HATA · 2 UYARI — `cizim-alani-hizasi` ve `izgara`: tablo figürünün ekseni yok, gerekçeli; indices figürünün
uzun kategori etiketleri sol kenarı kaydırıyor, raporda bu figürler alt alta değil ayrı yerlerde duracak.
Hedef springer-cift 174 mm · 9 pt (rapor metin genişliği 176 mm). Altyazılar: `TRADEOFF_SECTION.md`.

### Revizyon 2 (5 Nov 2026 ~15:00) — kullanıcı: ızgara, tema, konumlar, eksenler, değerlerin tekrar kontrolü
- Tema `derin` (lacivert Ti, kehribar Al, gri çelik; tabloda petrol ✔ / kızıl ✖). Eski çıktılar: `D:\tmp_ideathon\ansys\anchor\trade_off_v1_1440\`.
- Izgara: açık gri (#e4e4e4, 0.6 pt), yalnız ana çizgiler; (a) 20 % × 10 t, indeks 20 %, (b) log on'luklar.
- Eksenler: (a) 0–120 % / 0–70 t; indeks "% of S275N"; (b) "×, log scale". Çıktı ayrıca SVG (Word'e net yerleşim).
- `check_values.py`: 97 kontrol, 0 FAIL (eco fazları organizatör PDF'iyle ±1 %, her figür etiketi, metindeki her sayı).
- 300 °C katsayıları kaynağından okundu: MIL-HDBK-5J Şekil 5.3.2.1.1/5.3.2.1.4 (PDF), EN 1993-1-2 Tablo 3.1 ve E.1 (dnaop.com).
- Göz kontrolü: (a) not kutusu referans çizgisine biniyordu ve (b) sol kenarda çift çizgi vardı — denetim görmedi, düzeltildi.
