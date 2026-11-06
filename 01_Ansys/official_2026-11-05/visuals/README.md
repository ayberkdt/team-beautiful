# Visuals — official initial S275N bracket (5 Nov 2026)

Still visuals of the organisers' initial bracket for the jury deck. **Nothing here is an FEA result**; no stress
colours are drawn. Every number on a figure is read at run time from `../derived/features.json` (via
`scripts/geom.py`), `../setup/setup_official_fixed_bores.json` and `scripts/out/volume_check.json`.

## Files

| File | What it shows |
|---|---|
| `hero_iso.png` (3600 × 2400) | studio iso render, light background, soft contact shadow, thin B-rep edges |
| `hero_iso_dark.png` (3600 × 2400) | same view, dark background with faint floor glow |
| `bc_loads.png` (3602 × 1712) / `.pdf` | supports and loads: fixed support on the 4 bolt bores (blue faces + triangle/hatch symbols), Fz 97 kN per pin bore (arrow above each lug; bore upper halves red), Fy ±24 kN along the pin axis at both lugs, global triad; right: pin-bore detail seen along +y (cosine bearing arrows on the upper half, My 1000 N·m per bore, clockwise = +My) and LC1a / LC1b / LC2. `bc_loads.cvd.png` = colour-blind preview |
| `views_dimensioned.png` (3602 × 1712) / `.pdf` / `.svg` | front (x–z), right (y–z) and top (x–y) views, third-angle, mm; 661.01, 341.12, 70, 4× Ø60 + 2× Ø60, 510 × 210, 230 from datum A, lugs 70 / 200 / 71.12, R80 top, 4× R80 root, 4× R100, 291.37 overall height |
| `turntable/frame_000.png … frame_071.png` | 360° turntable, 5° per frame, 1920 × 1080; camera table in `turntable/README.md` |
| `initial_exact.step` | exact OCC solid (28 B-rep faces), mm, CAD frame |
| `initial_exact.stl` | binary display mesh of that solid (129 088 triangles) |
| `*.denetim.txt`, `*.dw.json` | datawiz audit reports / fingerprints of the two 2-D figures |
| `scripts/` | all code; `scripts/out/volume_check.json`, `scripts/out/brep_edges.npz` |

## How to rebuild (one command)

From the project root, Git Bash:

```
export TEMP=D:/tmp_ideathon/visual TMP=D:/tmp_ideathon/visual MPLCONFIGDIR=D:/tmp_ideathon/visual/mpl \
       PYTHONPATH="src;D:/tmp_ideathon/pylib" PYTHONIOENCODING=utf-8
python studies/final_2026/ansys/official_2026-11-05/visuals/scripts/make_visuals.py   # ~4 min; --skip-turntable ~1 min
```

Steps: `build_exact.py` (gmsh 4.15.2 OCC: rounded plate R100 → 2 extruded lug profiles → fuse → cut 6 Ø60
cylinders; writes STEP, STL, B-rep edges, volume check; exits 1 if the volume is off by > 0.5 %) → `hero.py` →
`bc_loads.py` → `views.py` → `turntable.py`. The runner stops if any datawiz report is not 0 HATA.
Rendering: pyvista 0.46.5 / VTK 9.5.2 off-screen on the GTX 1660 Ti, 2× supersampling + Lanczos, SSAO
(bias 3; lower bias banded the R80 fillets), edges hidden by a depth-buffer test (polygon offset alone let hidden
edges poke through near silhouettes). Nothing was installed.

## Exact rebuild and volume check (`scripts/out/volume_check.json`)

| Quantity | Value |
|---|---|
| Exact B-rep volume | 19 397 542 mm³ = **0.0193975 m³ → 152.27 kg** at 7850 kg/m³ |
| Reference (boundary_conditions.md, facet STL) | 0.019400 m³ (152.29 kg); recomputed from the STL here: 19 399 664 mm³ |
| Difference | **−0.013 %** vs 0.019400 m³; −0.011 % vs the recomputed facet volume (limit 0.5 %) — accepted |
| Organisers' mass monitor (boundary_conditions.md) | 152.27 kg — the exact solid matches it to 0.01 kg |
| Display STL vs B-rep | −0.0008 % |
| Bounding box | x 170–831.01, y 30–371.12, z 30–321.37 mm (facet STL: same to 0.005 mm) |

Lug flanks were not taken as "80°" but built as the common tangent of the R80 top arc and the R80 root fillet
(both centres from features.json). Result: 80.18° / 80.15° to the plate, normal (0.9854, 0.1705), offset 613.84 mm
— features.json says (0.985, 0.171) and 613.84, so the tangent construction reproduces the measured face.
Left offset −371.34 vs −371.42 measured (0.08 mm). The left fillet centre 326.95 (not 327) is used as measured,
so the lug is symmetric about x = 500 only to 0.05 mm.

## Notes the reader of the figures should know

* **Pin height**: the pin axis is at CAD z = 260; the underside (datum A) is at CAD z = 30, so the pin axis is
  **230 mm above the underside**. The drawing dimensions 230 from datum A and states the CAD z values in the notes.
  "260" is a coordinate, not a height.
* Loads are per pin bore and the cases are separate (boundary_conditions.md §3, our reading [Y]). LC1c
  (opposite Fy, sensitivity) is not drawn. Fy is drawn on the pin axis; the md notes it may physically enter
  through the pin head / washer.
* +My is drawn by the right-hand rule about +y (rotates +z towards +x); in the "view along +y" detail that is
  clockwise.

## Design gates (user rules)

### FİGÜR BRİFİ — bc_loads
Mesaj: parça 4 cıvata deliğinden ankastre; her pim deliğine Fz 97 kN (üst yarıda yatak yükü) + Fy ±24 kN, ayrı
durumda My 2000 N·m. · Okur: karma (jüri) · Ortam: sunum:sunum-tam (305 × 145 mm, ≥ 18 pt) · Veri: setup JSON'dan
6 delik, 3 yük durumu (nominal) · Karşılaştırma: yok — şema · Biçim: açıklamalı 3-B şema + 2-B ayrıntı (grafik
türü değil; teknik-atlası dışı) · Tema: akademik (mavi = mesnet, vermilyon = kuvvet, eflatun = moment) + doğrudan
etiket.

### FİGÜR BRİFİ — views_dimensioned
Mesaj: başlangıç parçasının bütün ana ölçüleri tek bakışta, datum açık. · Okur: uzman/karma · Ortam: sunum-tam ·
Veri: features.json ölçüleri · Biçim: üçüncü açı izdüşüm teknik resim (3 görünüş) · Tema: akademik (ölçüler mavi,
çizgiler mürekkep).

Process deviation, stated plainly: both briefs and the GÖREV BÜTÇESİ below were written down while the
figures were being built, not before the first plotting line; the content above is what the figures were built to.

### datawiz audit (`*.denetim.txt`)

* `bc_loads`: first run 1 HATA (label on triad) + 1 UYARI (5 font sizes) → layout rebuilt; second run 2 HATA (Fy/My
  labels overlapping) → My moved to a 2-D detail; third run 3 HATA (label off the edge, triad on title, mixed short
  labels read as panel letters) → fixed; now **0 HATA · 0 UYARI**. CVD preview checked: forces and moment differ in
  hue under protan/deutan only weakly, but every arrow carries its own text label.
* `views_dimensioned`: first run 5 HATA (callout off the edge, callout on view title, three lines through text) →
  fixed; now **0 HATA · 0 UYARI**. Saved as PDF, PNG and SVG.
* `python -m datawiz.kod_denetimi scripts` → 9 files, 0 HATA · 0 UYARI.
* The datawiz figure audit cannot read the 3-D renders (`hero_*`, turntable): those were checked by eye only.

### Eye-check findings fixed (PNG opened after each run)

1. Hero: part filled only ~45 % of the frame and the lug faces were almost black → camera closer, light rig
   rebalanced (key from camera-left at 0.95, fill on end faces).
2. Hero: 2–5 px edge "ticks" poking through the plate top at the back corners (hidden tangent edges, polygon
   offset) → depth-buffer edge-visibility test + removal of runs shorter than 4 pieces.
3. Dark hero: top face blown out, shadow invisible → light gain 0.78, steel slightly darker, faint floor glow.
4. Turntable: concentric banding on the R80 fillets from SSAO → bias 0.6 → 3.0 (compared side by side).
5. BC figure: all labels correct in 3-D but confusing — Fz label of the near lug sat next to the far lug's arrow,
   one bolt bore was hidden behind a lug, the bearing arrows (~60 px bore) read as a saw-tooth → camera raised to
   36° (all 4 bolt bores tested visible with the depth buffer), labels put beside their own tip, bearing and My moved
   into the x–z detail.
6. BC figure: red/blue face colouring spilled onto the flat faces around the bore mouths → selection restricted to
   cells whose normal is perpendicular to the bore axis.
7. Drawing: datum box on the 661.01 dimension line, "2× Ø60" crossed by the 291.37 extension line, "71.12"
   crossed by its extension line → dimension rows moved, text gap increased.

### GÖREV BÜTÇESİ — jury slide images (yüzey: slayt; statik görsel)
Birincil görev: (1) parçayı tanımak, (2) yükleri/mesnetleri okumak, (3) ölçüleri okumak · Birincil eylem: yok
(statik görsel) · Eylem/görünüm ≤ 5: 0 · Gezinti: 0 · Seçenek kümesi: kapsam dışı · Form: kapsam dışı ·
Geri bildirim: kapsam dışı · Stil bütçesi: ≤ 4 punto (bc 18/20/22; çizim 18/20), 3 anlam rengi + mürekkep/gri,
gölge 1 (yer gölgesi), yarıçap yok · Sisteme yüklenen: bütün sayılar dosyadan okunur, el ile yazılmaz.

### YASA DENETİMİ — visuals/*.png · 2026-11-05 · denetleyici: koşmadı (yüzey: statik PNG/PDF, HTML yok)

Sonuç: 20/20 yasa değerlendirildi · 0 HATA · 1 UYARI (gerekçeli) · karar: TESLİM

| # | Yasa | Ölçüm (sayı/gözlem) | Eşik | Durum | Gerekçe (yalnız UYARI) |
|---|---|---|---|---|---|
| 1 | Hick | etkileşimli öğe 0 (statik görsel) | ≤ 5 eylem | kapsam dışı | |
| 2 | Fitts | hedef yok; en küçük yazı 18 pt = 75 px @ 3602 px genişlik | — | kapsam dışı | |
| 3 | Jakob | Ansys gelenekleri: mesnet mavi + üçgen, kuvvet kırmızı ok, z yukarı, üçüncü açı izdüşüm, ISO çizgi tipleri | tanıdık desen | geçti | |
| 4 | Seçim Yükü | seçim yok | ≤ 5 | kapsam dışı | |
| 5 | Yakınlık | her etiket kendi okunun ucunda 14–34 px; bc sağ sütun: ayrıntı ile LC listesi ayrı bloklar | etiket öğesine bitişik | geçti | |
| 6 | Benzerlik | bc: 3 punto (18/20/22), çizim: 2 punto (18/20); aynı tür ok aynı renk/kalınlık (Fz 5 pt, Fy 4 pt çift başlı) | ≤ 4 punto | geçti | |
| 7 | Tekdüze Bağlılık | kart 0, iç içe kutu 0 | 0 | geçti | |
| 8 | Ortak Bölge | bc: 2 bölge (3-B görünüm, sağ sütun zemin tonu); çizim: 3 görünüş + not sütunu | ≤ 4 | geçti | |
| 9 | Prägnanz | cam 0 · ışıma 0 · dekoratif degrade 0 (koyu kahramanda zemin parıltısı 1, gölgeyi görünür kılmak için) | 0 · 0 · ≤ 3 | geçti | |
| 10 | Von Restorff | bc'de tek doygun aile (vermilyon kuvvet) en büyük ok; mesnet mavi, moment eflatun ikincil | 1 vurgu | geçti | |
| 11 | Miller | bc 3-B etiket 6 (2 Fz, 2 Fy, 1 mesnet, eksen); LC listesi 3 satır + 2 not | ≤ 7 öbek | geçti | |
| 12 | Sıra Konumu | bc sağ sütun: ilk "Pin bore" ayrıntısı, son "Set-up only, not an FEA result" | ilk/son önemli | geçti | |
| 13 | Doherty | etkileşim yok | — | kapsam dışı | |
| 14 | Zeigarnik | çok adımlı akış yok; döner tabla 72 kare tam tur | — | kapsam dışı | |
| 15 | Zirve-Son | döner tabla kare 0 = kahraman görünüşü, kare 71 bir adım önce → döngü kesintisiz | — | geçti | |
| 16 | Parkinson | form yok | — | kapsam dışı | |
| 17 | Tesler | sayıların hepsi JSON'dan çalışma anında; kullanıcıdan girdi 0 | her girdiye gerekçe | geçti | |
| 18 | Postel | tek biçim: birimler SI, "kN", "N·m", "mm"; eksi işareti U+2212 | tek çıktı biçimi | geçti | |
| 19 | Occam | bc: LC1c ve "H1–H6" kimlikleri çıkarıldı; çizimde kenar mesafeleri (75/65) çıkarıldı | eşlenemeyen öğe 0 | geçti | |
| 20 | Pareto | bc yüzeyinin ~%58'i 3-B yük görünümüne (birincil görev 2) | ≥ %60 | UYARI | %42'lik sağ sütun My yönünü ve üst yarı yatak dağılımını taşıyor; 3-B görünüşte okunamıyordu (göz kontrolü 5) |

Riskler: renk ayrımı protan/deutan altında kuvvet–moment arasında zayıf; kimlik yazıyla da taşındığı için kabul.
Projektörde 18 pt notlar 1920 px slaytta ~13 px yüksekliğe iner (305 mm = tam slayt genişliği varsayımı).

## Not done

* No video encoded (no ffmpeg on this machine); frames + camera table are ready for assembly.
* Turntable is light background only (`turntable.py --theme dark` makes a dark set; not rendered).
* The datawiz audit does not cover the 3-D renders; they were eye-checked only.
* Tangent edges are drawn thin in the drawing (ISO allows omission); the plate-corner tangent lines on the front
  and side views are omitted.
