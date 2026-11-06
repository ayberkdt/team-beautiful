# 26 · Venus rotorcraft simulator — engineering data book (LuGus "Fly on Venus")

Written 5 Nov 2026 for the Friday 6 Nov LuGus slot. Companion to doc 25 (VESPER); it does **not** change doc 25,
`sim_params.json` or any code. Source notes: `04_Venus/research/E_*.md` (index `E_00_index.md`); data files:
`04_Venus/research/data/venus_atmosphere_40_70km.csv` (+ `.md`) and `venus_turbulence_model.json`.

**Tags.** **[D]** read at the primary source in this session (5 Nov) · **[D-ag]** secondary source, or read by an
earlier agent/session (notes A_–D_, not re-read today) · **[A]** abstract or search snippet only · **[K]** computed
today from [D] values · **[Y]** our judgement. "E_xx" = the note that holds the page/section reference.

> **Özet (TR).** Bu belge, LuGus'un Mars Drone Simulator'ının Venüs karşılığı için **fizik motoruna doğrudan girecek
> sayıları** topluyor. (1) **Atmosfer 40–70 km, 0,5 km adımlı** tablo: Pioneer Venus 4 sondası + VEGA-2 iniş aracı ham
> verisinden T, p, ρ ortalama ve zarf; NIST'ten CO₂/N₂ karışımı için ses hızı, viskozite, γ; 55 km: 299 K, 0,508 bar,
> ρ 0,889 (0,854–0,907) kg/m³, a 271 m/s. 64 km üstünde veri ince; enlem etkisi orada %25–30. (2) **Rüzgâr**: süper-
> rotasyon 50 km'de 60, 60 km'de 85 m/s; VEGA balonlarından düşey rüzgâr σ 0,7 m/s, −3,5…+2 m/s, **korelasyon süresi
> ~25 dakika** (doc 25'teki 80 s değil) → simülatörde iki bileşenli model: yavaş konvektif hücre + Dryden küçük ölçek.
> (3) **Bulut**: üç katman, orta bulut ~7,5 mg/m³, görüş ~2 km; 55 km'de doğrudan güneş yok, ışık tamamen dağınık;
> alttan yansıma %86. (4) **Rotor fiziği**: Re 10⁴–10⁶, uç Mach < 0,7; Lock sayısı ~9 (Mars'ta 0,3) → kanat çırpması
> Dünya'daki gibi sönümlü; **girdap halkası** 1,2–3,9 m/s dikey inişte, ≥ 2,5 m/s ileri hızla kaçılır; rotorlar arası
> boşluk 0,04D (NASA çalışmasındaki en dar 0,3D'de bile %2 kayıp). (5) Yapım: malzeme/motor/güneş/batarya verileri ve
> MSH kütle bağıntıları. (6) LuGus'un Mars simülatörü Liftoff (Unity) tabanlı bir **pilot eğitim** aracı; fizik
> ayrıntısı kamuya açık değil → mentora sorulacak. Doc 25 ile 7 tutarsızlık/uyarı listelendi (§8).

---

## 1. Atmosphere, 40–70 km

### 1.1 Data and method
- Five in-situ soundings, raw tables downloaded today: Pioneer Venus Sounder (4.4°N, 07:38 LT), Day (31.3°S, 06:46),
  Night (28.7°S, 00:07), North (59.3°N, 03:35), all 9 Dec 1978 [D, E_01]; VEGA-2 lander (~7°S, ~01 LT, 11 Jun 1985)
  [D, E_04]. Probe accuracy: p and ρ 0.5 % of reading, T 1 K, altitude 0.4 % of reading [D, E_01].
- Gas properties from NIST CO₂ and N₂ isobars, mixed 96.5/3.5 % by mole (M = 43.45 g/mol) [K on D, E_05].
  Measured bulk composition: CO₂ 96.4 %, N₂ 3.41 % at 21.6 km (PV gas chromatograph) [D-ag, A_pv_lgc_composition].
- Gravity g = GM/(6052.0 km + z)², GM = 324 858.592 km³/s² [D, E_06].
- Reference model for comparison: Venus-GRAM (VIRA-based) average and 10/40/60/80°N density [D-ag tertiary, E_07].
  VIRA itself (Seiff et al. 1985) is still **not obtained**.

### 1.2 Density halves about every 5 km near 55 km; the site-to-site band is only −4/+2 % there (table every 1 km; full 0.5 km grid in the csv)
n = soundings with data (PV probes + VEGA-2). Mean = PV probes only; min–max = all soundings. a, µ, ν at the mean
state. u = zonal wind, westward, PV DLBI interpolated per probe (E_02). [K on D]; GRAM column [D-ag].

| z km | n | T K mean (min–max) | p kPa | ρ kg/m³ mean (min–max) | a m/s | µ µPa·s | ν 10⁻⁵ m²/s | u west m/s mean (min–max) | ρ GRAM 10N / 80N |
|---:|---:|---|---:|---|---:|---:|---:|---|---|
| 40 | 5 | 415.8 (413.5–417.2) | 341.38 | 4.314 (4.125–4.380) | 314.6 | 20.44 | 0.47 | 38 (35–42) | 4.404 / 4.459 |
| 41 | 5 | 409.0 (406.3–410.9) | 305.36 | 3.922 (3.752–3.975) | 312.2 | 20.14 | 0.51 | 40 (38–44) | 4.015 / 4.070 |
| 42 | 5 | 402.3 (400.0–404.8) | 272.67 | 3.560 (3.336–3.604) | 309.9 | 19.84 | 0.56 | 42 (40–46) | 3.646 / 3.706 |
| 43 | 5 | 395.8 (393.1–398.6) | 243.01 | 3.224 (3.053–3.264) | 307.6 | 19.55 | 0.61 | 45 (42–49) | 3.303 / 3.366 |
| 44 | 5 | 389.9 (387.2–392.3) | 216.22 | 2.911 (2.757–2.952) | 305.5 | 19.28 | 0.66 | 49 (44–54) | 2.985 / 3.055 |
| 45 | 5 | 384.3 (381.7–387.6) | 192.07 | 2.623 (2.478–2.665) | 303.5 | 19.02 | 0.73 | 52 (48–59) | 2.693 / 2.766 |
| 46 | 5 | 377.8 (374.5–381.4) | 170.29 | 2.365 (2.235–2.407) | 301.2 | 18.72 | 0.79 | 56 (50–64) | 2.426 / 2.499 |
| 47 | 5 | 371.0 (366.6–373.4) | 150.68 | 2.130 (2.029–2.163) | 298.8 | 18.41 | 0.86 | 57 (52–62) | 2.186 / 2.248 |
| 48 | 5 | 364.2 (358.3–366.9) | 133.02 | 1.916 (1.835–1.945) | 296.4 | 18.10 | 0.94 | 58 (55–61) | 1.967 / 2.017 |
| 49 | 5 | 356.0 (350.4–360.4) | 117.16 | 1.725 (1.654–1.757) | 293.4 | 17.72 | 1.03 | 59 (54–65) | 1.773 / 1.803 |
| 50 | 5 | 347.9 (343.7–351.8) | 102.88 | 1.550 (1.492–1.584) | 290.4 | 17.34 | 1.12 | 60 (53–68) | 1.594 / 1.613 |
| 51 | 5 | 339.0 (333.9–343.2) | 90.04 | 1.392 (1.341–1.421) | 287.0 | 16.92 | 1.22 | 61 (52–70) | 1.432 / 1.438 |
| 52 | 5 | 329.8 (323.5–334.3) | 78.54 | 1.248 (1.204–1.271) | 283.5 | 16.49 | 1.32 | 61 (53–70) | 1.284 / 1.275 |
| 53 | 5 | 319.8 (313.4–323.8) | 68.23 | 1.118 (1.078–1.139) | 279.6 | 16.02 | 1.43 | 62 (55–70) | 1.153 / 1.134 |
| 54 | 5 | 309.5 (303.0–313.8) | 59.01 | 0.999 (0.962–1.019) | 275.5 | 15.53 | 1.55 | 63 (57–70) | 1.032 / 1.004 |
| **55** | 5 | **299.1 (292.6–302.8)** | **50.79** | **0.889 (0.854–0.907)** | **271.4** | **15.03** | **1.69** | **63 (59–73)** | 0.921 / 0.885 |
| 56 | 5 | 288.5 (282.1–291.6) | 43.49 | 0.789 (0.754–0.804) | 267.0 | 14.52 | 1.84 | 66 (60–77) | 0.818 / 0.779 |
| 57 | 5 | 278.9 (271.6–281.8) | 37.03 | 0.695 (0.657–0.710) | 263.0 | 14.06 | 2.02 | 69 (61–81) | 0.721 / 0.681 |
| 58 | 5 | 271.1 (262.2–276.0) | 31.37 | 0.606 (0.572–0.622) | 259.8 | 13.68 | 2.26 | 74 (66–84) | 0.629 / 0.588 |
| 59 | 5 | 263.7 (251.1–272.0) | 26.46 | 0.525 (0.495–0.539) | 256.6 | 13.32 | 2.54 | 80 (72–87) | 0.545 / 0.494 |
| 60 | 5 | 257.8 (243.4–268.1) | 22.21 | 0.451 (0.425–0.464) | 254.0 | 13.03 | 2.89 | 85 (77–91) | 0.469 / 0.410 |
| 61 | 5 | 251.6 (236.1–259.7) | 18.57 | 0.386 (0.362–0.395) | 251.4 | 12.73 | 3.30 | 91 (84–95) | 0.400 / 0.339 |
| 62 | 4 | 251.7 (249.4–256.3) | 15.89 | 0.330 (0.302–0.338) | 251.4 | 12.74 | 3.86 | 100 (96–104) | 0.341 / 0.280 |
| 63 | 3 | 247.2 (246.0–249.3) | 13.24 | 0.280 (0.272–0.287) | 249.4 | 12.52 | 4.47 | 99 (1 probe) | 0.289 / 0.232 |
| 64 | 3 | 243.7 (241.2–247.0) | 11.00 | 0.236 (0.228–0.243) | 247.9 | 12.35 | 5.23 | 98 (1 probe) | 0.244 / 0.192 |
| 65 | 2 | 239.0 (238.6–239.4) | 9.20 | 0.201 (0.200–0.203) | 245.8 | 12.12 | 6.02 | — | 0.205 / 0.159 |
| 66 | 1 | 236.0 (Day probe) | 7.55 | 0.167 | 244.4 | 11.97 | 7.16 | — | 0.173 / 0.131 |
| 67 | 1 | 230.0 (North, entry data) | 5.02 | 0.114 | 241.7 | 11.68 | 10.24 | — | 0.145 / 0.108 |
| 68 | 1 | 239.2 (North, entry data) | 4.14 | 0.090 | 245.9 | 12.13 | 13.42 | — | 0.121 / 0.089 |
| 69 | 1 | 242.1 (North, entry data) | 3.46 | 0.075 | 247.3 | 12.27 | 16.44 | — | 0.101 / 0.074 |
| 70 | 1 | 236.7 (North, entry data) | 2.85 | 0.063 | 244.8 | 12.00 | 19.08 | — | 0.084 / 0.061 |

**Above 64 km the in-situ data are thin**: 66 km is one probe (Day), 67–70 km is the North probe's entry data (59°N),
which matches the GRAM 60–80°N density, not the equator. For a low-latitude simulator use the GRAM 10N column above
64 km and treat the PV value as the thin edge [Y].

### 1.3 Variation with latitude, local time and year — envelopes, not only means
| Effect | Size | Tag, source |
|---|---|---|
| Site-to-site (31°S–59°N, 00–08 LT) at 55 km | T 292.6–302.8 K; ρ 0.854–0.907 kg/m³ (−4 %/+2 %) | [K on D] csv |
| VIRA/GRAM vs PV mean, 50–60 km | GRAM 2.5–5 K warmer, 3–4 % denser | [K] on E_01, E_07 |
| Latitude, density | < 5 % below 55 km; **−25…−30 % at 65–70 km from 10°N to 80°N** | [D-ag] E_07 |
| Latitude, temperature | T rises with latitude above ~65 km, falls below ~65 km; cold collar ~65°, 65 km; ~30 K equator–pole at 1 bar | [D] E_08; [A] Tellmann 2009 |
| Convective layer depth vs latitude | 0–1 K/km stability at 50–58 km (low lat.); reaches down to ~42 km poleward of 75° | [D] E_08 |
| Local time, temperature at cloud level | "very low variability with local time" in VeRa profiles (equator) | [D] E_09 citing VeRa |
| RO vs model uncertainty | ±5 K at 50–60 km low latitude; ±10–15 K poleward of 50° above 60 km | [D-ag] A_limaye2018_banerjee2026 |
| VEGA-1 vs VEGA-2 at the same pressure (~54 km) | 6.5 K | [D-ag] A_00_index |
| Afternoon soundings | **none exist** (all in-situ profiles 00–08 LT) | [D] E_01, E_04 |

Suggested sim envelope [Y]: mean = csv mean; "hot/thin" = T_max with ρ_min; "cold/dense" = T_min with ρ_max; above
60 km scale ρ by GRAM latitude ratio.

### 1.4 Constants
g(55 km) 8.710 m/s² [K]; surface equatorial 8.87 m/s²; R 6051.8 km; sidereal day −243.018 d → Ω 2.99×10⁻⁷ rad/s [D, E_06].
At 55 km: γ 1.294, cp 853 J/(kg K), k 0.0169 W/(m K) [K on D, E_05]. ρ(55 km) is 0.73 × Earth sea level [K].

---

## 2. Winds, turbulence and the recommended sim model

### 2.1 Mean zonal wind (super-rotation)
- PV DLBI, 4-probe interpolation: 38 m/s at 40 km, 60 at 50, 63 at 55, 74 at 58, 85 at 60, ~98–100 at 62–64 km [K on D,
  E_02]. Probe spread at 55 km 59–73 m/s.
- VEGA balloons, 53–54 km (00–08 LT, ±8° lat.): U 68.7 ± 1.7 and 64.8 ± 1.8 m/s [K on D, E_04].
- Cloud-tracked: ~100 m/s at 65–70 km and 70 m/s at ~60 km, both nearly constant between ±45°, falling toward the poles;
  long-term fluctuations ~10 %; cloud-top increase from ~100 to ~120 m/s between 2006–09 and 2009–12 [D, E_11].
- Local time: at 65–70 km and 10–40° latitude, +5…15 m/s from 07 h to 17 h (solar tide); **no LT dependence detected
  at 60 km and 47 km** [D, E_11]. Decadal change of lower-cloud nightside winds up to ±15 m/s [D-ag].

### 2.2 Meridional and vertical mean motion
- Meridional in the cloud region: −5…+5 m/s (PV) [D, E_11]; −7.1…+7.7 m/s at 40–62 km in today's DLBI interpolation
  [K on D, E_02]; VEGA −6.3…+4.4 m/s [K on D, E_04]. At 65–70 km: 0 at the equator to 10–15 m/s poleward near 60° [D, E_11].
- Hadley-cell vertical velocity ~0.1 m/s (model); waves/convection 0.5–5 m/s (models) [D, E_11].

### 2.3 Shear
- From the csv: ~0.5 m/s per km at 50–55 km, rising to ~5–6 m/s per km at 56–61 km [K on D]; PV Large probe 56→60 km
  ≈ 6.5 m/s per km [K, E_02]; VEX 61–66 km 8 ± 2 m/s per km [D-ag, A_winds note].
- Sim effect [K]: a 3 km downdraft excursion from 55 to 52 km changes the mean wind by only ~2 m/s; a climb from 55 to
  60 km changes it by ~21 m/s — that is an airspeed transient the controller must absorb (the vehicle carries the
  momentum of the old air mass).

### 2.4 Convection and turbulence — measured
| Quantity | Value | Tag, source |
|---|---|---|
| Vertical wind σ, 53–54 km | 0.663 (VEGA-1), 0.731 m/s (VEGA-2) | [K on D] E_04 |
| Vertical wind extremes | −3.50…+1.96 m/s | [D] E_04 |
| P(abs w > 1 m/s) / > 2 m/s | 0.17 / 0.04–0.06 | [K on D] E_04 |
| **Vertical wind autocorrelation** | 0.78 at 300 s, 0.53–0.56 at 1200 s, 0.28 at 1800 s → **1/e ≈ 1500 s** | [K on D] E_04 |
| Largest 1-h mean downdraft | −2.23 (VEGA-1), −1.71 m/s (VEGA-2); excursions to 882 / 901 hPa from ~535 hPa | [K on D] E_04 |
| Downdraft episodes | 2–4 m/s for ~1–2 h; VEGA-2 pushed ~3 km down | [D-ag] A_vega1985 |
| Horizontal fluctuations, 30–130 s periods | 0.05–1 m/s (VEGA-2), up to 2 m/s (VEGA-1), true ≈ 1.5× measured | [D-ag] A_vega1985 (Kerzhanovich) |
| Convective layer (models vs RO) | 46–55 km, 9 km thick | [D] E_10 |
| Cells | 6 km (noon) to 15 km (midnight) wide; ~20 km with full radiative transfer; broad updrafts, narrow downdrafts; aspect ratio ~3 | [D] E_09, E_10 |
| LES vertical wind | +2 / −3 m/s (2018); −4.7…+2.8 m/s without large-scale heating (2017) | [D] E_09, E_10 |
| Gravity waves above the layer | 0.5–1 K; horizontal wavelength 1–6 km, up to 20 km with shear | [D] E_10 |

### 2.5 Recommended turbulence model (full parameters in `venus_turbulence_model.json`)
Four additive parts on top of the mean wind, in the air-mass frame [Y structure; values tagged in the json]:
1. **A — convective vertical wind**, 47.5–56.5 km: Ornstein–Uhlenbeck, σ_w = 0.70 m/s, correlation 1/τ = 1/1500 s +
   V_air/5000 m (Lagrangian decay + advection through ~10 km cells). Zero mean.
2. **B — downdraft events**: −2…−3.5 m/s, 1–2 h plateau, 10 min ramps, ~1 per 33 h [Y rate].
3. **C — small-scale turbulence**: Dryden (MIL-F-8785C form), σ_u = σ_v = 1.0 m/s, σ_w = 0.5 m/s, L = 533 m;
   V in the filters = max(V_air, 2 m/s). Scale all σ by 0.3 outside 47–57 km (stable layers).
4. **D — gravity waves** above 57 km: ±0.5–1 K temperature (→ ±0.2–0.4 % density) with 1–20 km wavelength; mainly
   visual (cloud banding).
Presets: calm (σ_w 0.3), nominal (0.7), severe (1.2 m/s, −3.5 m/s downdraft).

Why two time scales: the VEGA vertical record (75 s sampling) shows that almost all of the 0.7 m/s variance has
25-minute correlation — it is a convective-cell field the vehicle drifts with, not a fast gust. The fast part (30–130 s)
is seen in the horizontal Doppler data. A single 80 s process with σ 0.7 m/s puts the cell-scale energy at gust
frequencies.

---

## 3. Clouds, aerosols, light

### 3.1 Cloud structure (Pioneer Venus LCPS) [D, E_12; column mapping of Table 1 is ours]
| Layer | Altitude km | τ (Table 5) | Modes, mean diameter µm | Number density cm⁻³ | Mean mass loading [K] |
|---|---|---|---|---|---|
| Upper cloud | 56.5–70 | 7.27 | 0.4, 2.0 | 1500 / 50 | ~0.8 mg/m³ |
| Middle cloud | 50.5–56.5 | 11.07 | 0.3, 2.5, 7.0 | 300 / 50 / 10 | **~7.5 mg/m³** |
| Lower cloud | 47.5–50.5 | 12.20 | 0.4, 2.0, 8.0 | 1200 / 50 / 50 | **~21 mg/m³** |
| Above the LCPS range | > ~66 km | ~3.5 | — | — | — |
Mode 3 (7–8 µm) dominates the mass; its nature is disputed [A, E_20]. Droplets 75–90 wt % H₂SO₄ (98 % at the cloud base
in models) [D-ag, A_titov2018]. Models give 10–15 mg/m³ peaks near the cloud base [A, E_20].

Visual range [K]: middle-cloud extinction ≈ 11.07/6 km ≈ 1.8 km⁻¹ → contrast-threshold visibility ≈ 3.9/1.8 ≈ **2 km**;
lower cloud ≈ 4 km⁻¹ → ~1 km; upper cloud ~0.5 km⁻¹ → ~7 km. For the renderer: dense uniform haze, no hard cloud
edges inside a layer, sharper changes at the 50.5 and 56.5 km layer boundaries [Y].

### 3.2 Light: direct, diffuse, albedo
- Overhead-Sun optical depth above 55 km ≈ 3.5 + 7.27 + (1.5/6)·11.07 ≈ 13.5 → direct beam ~e⁻¹³·⁵ ≈ 10⁻⁶ of the top
  value: **all light at 55 km is diffuse** [K on D, E_12]. Above ~66 km τ ≈ 3.5 → direct beam ~3 % for an overhead Sun [K].
- Measured hemispheric down flux (PV LSFR, 0.41–1.78 µm, SZA 65.7°), relative to 64.3 km: 0.44 at 50 km, 0.58 at 55,
  0.76 at 60 [K on D, E_03].
- **Up/down ratio (albedo seen by a bifacial underside)**: 0.84 at 50 km, 0.86 at 55, 0.87 at 60, 0.89 at 64 km [K on D,
  E_03] — matches doc 25's 84–89 %.
- Absolute array output, 29 % AM0 triple-junction, overhead Sun: 256 / 404 / 559 W/m² at 50 / 55 / 60 km; Venus top-of-
  atmosphere 2600 W/m²; the GaAs middle junction limits current; 2J ≈ 3J [D-ag, D_landis_haag_2013].

### 3.3 Corrosion facts for designers [D-ag, D_00_index]
FEP keeps 95 % tensile strength after 168 h in concentrated H₂SO₄ at 120 °C, 0 % weight gain; JPL aerobot FEP/Kapton
laminate survived 96.2 % acid at 100 °C under 63 N; Parylene-coated solar coupons: no loss after 96 h in 96 % acid;
CP titanium 1.57 mm/y in concentrated acid at room temperature but nil in 96 % vapour at 38–66 °C; 316L-type steel
< 0.1 mm/y at ≤ 30 °C, > 1 mm/y at 80 °C; **no primary data for CFRP/epoxy in concentrated acid**. FFKM seals: listed for
98 % acid at 150 °C [A, E_20].

Leading-edge wetting [K, Y inputs]: at 70 m/s tip speed and 47 mm tip chord, droplet Stokes number ≈ 0.48 for 7 µm
(mode 3), 0.06 for 2.5 µm, 0.001 for 0.3 µm (ρ_drop 1780 kg/m³ [Y]) → mode 3 droplets hit the leading edge, smaller ones
mostly follow the flow. With ~7.5 mg/m³ mostly in mode 3 and a collection efficiency ~0.3 [Y], the outer leading edge
receives ~0.6 kg of acid per m² of frontal area per hour [K] — a continuous liquid film, so every blade surface must be
acid-proof (FEP/PFA), and impact erosion at 70 m/s is low-energy but continuous. Icing: not relevant.

### 3.4 Lightning
Unproven: Akatsuki LAC 16.8 h with no flashes → optical rate > 1000× below Earth's [A via A_lorenz2018]; "sporadic
discharges different from Earth not excluded" [D-ag, A_lorenz2018]. Sim: none by default; optional rare-event visual [Y].

---

## 4. Rotorcraft physics at Venus conditions

### 4.1 Reynolds and Mach regimes [K on csv]
Re at 0.75R with c/R = 0.042 (2 blades, σ 0.027, as VESPER):

| D (m) | 55 km, V_tip 70 m/s (M 0.26) | 55 km, 120 m/s (M 0.44) | 55 km, 180 m/s (M 0.66) | 50 km, 70 m/s | 60 km, 70 m/s |
|---:|---:|---:|---:|---:|---:|
| 0.5 | 3.3×10⁴ | 5.6×10⁴ | 8.4×10⁴ | 4.9×10⁴ | 1.9×10⁴ |
| 1.0 | 6.5×10⁴ | 1.1×10⁵ | 1.7×10⁵ | 9.9×10⁴ | 3.8×10⁴ |
| 2.0 | 1.3×10⁵ | 2.2×10⁵ | 3.4×10⁵ | 2.0×10⁵ | 7.6×10⁴ |
| 2.6 | 1.7×10⁵ | 2.9×10⁵ | 4.4×10⁵ | 2.6×10⁵ | 9.9×10⁴ |
| 3.0 | 2.0×10⁵ | 3.4×10⁵ | 5.0×10⁵ | 3.0×10⁵ | 1.1×10⁵ |

Speed of sound 254–290 m/s at 60–50 km, so tip Mach ≤ 0.7 (the MSH limit [D, E_17]) allows tip speeds up to ~180–200 m/s.
Venus rotors of 0.5–3 m sit at Re 2×10⁴–5×10⁵: Earth small-UAV to light-helicopter regime, 10–50× Ingenuity's ~10⁴
[D-ag, C_00_index].

### 4.2 Airfoils at Re 10⁵–10⁶
- Available validation polar: NACA 0015 at Re 2.42×10⁵ (Knight & Hefner 1937 Tables V–VI), cd_min 0.0113; used for the
  doc 25 BEMT check (torque rms 6.3 %) [D-ag, C_knight_hefner1937].
- Free-stream turbulence changes conventional sections strongly near Re 2.5×10⁵ (NACA 0015 cl_max +30 %) [D-ag,
  C_koning2020] — relevant inside a turbulent convective cloud.
- Below Re ~10⁵ (small rotors, upper cloud) thin cambered plates beat conventional sections (Mars work: double-edged
  plate L/D +15–28 % vs the MH section) [D-ag, C_koning2020].
- Recommendation [Y]: sim polars as tables cl(α, Re, M), cd(α, Re, M) with a laminar-separation-bubble drag rise below
  Re ~1.5×10⁵; start from NACA 0012/0015 data for Re > 2×10⁵. (Specific low-Re airfoil data were not read today.)

### 4.3 Inflow: BEMT + dynamic inflow
- Pitt–Peters 3-state: apparent mass M = diag(8/(3π), 16/(45π), 16/(45π)); hover time constants (1/v0)·diag(4/(3π),
  16/(45π), 16/(45π)); "works well overall" vs test data at μ 0.15–0.30 [D, E_15].
- VESPER hover inflow lag τ0 = (4/(3π))·R/v_h ≈ **0.21 s** at 55 km [K]. Peters–He (more states) is only needed for
  blade-load/vibration work, not for flight dynamics and training [Y].
- Real-time: BEMT with 10–20 radial stations × 6 rotors at 200–500 Hz is light; a 3-state inflow per rotor adds 18 ODEs [Y].

### 4.4 Vortex ring state (VRS) and descent [D, E_14]
- VRS scales with v_h = sqrt(T/(2ρA)); unstable where d(Vz+v)/dVz < 0, roughly Vz/v_h = −0.45 to −1.5; the effect
  vanishes for Vx/v_h ≥ 0.95. Johnson's Table 4: VzN −0.45, (V+v)N 0.85; VzX −1.5, (V+v)X 1.25; VzD −0.2; VzE −2.0;
  VxM 0.95; baseline A −1.5, B −2.1, C 0.75. First-order lag on the VRS increment. Fluctuation frequencies scale with v_h/R.
- VESPER [K]: v_h 2.59 m/s → **unstable descent 1.17–3.89 m/s**; escape with ≥ 2.5 m/s airspeed. Small v_h (low disk
  loading, dense gas) means slow vertical descents are already VRS — every descent in the sim should be flown with
  forward speed, and a downdraft does *not* cause VRS by itself (the vehicle moves with the air) [Y].
- Simpler closed form for real time: Vz + v = Vz(0.373 Vz² − 0.991 + 0.598 Vx²) inside 1.5Vx² + (2Vz+3)² < 1 (normalised
  by v_h) [D, E_14].

### 4.5 Rotor–rotor interaction (multirotor)
NASA Ames CFD: tip gap 0.3D → ~2 % hover efficiency loss; 2D ≈ isolated; strong unsteady pressure waves at 0.3–0.5D
[D, E_16]; up to 4 % (other papers) [A, E_20]. Correction 6 Nov: the "−28 % for rear rotors" snippet was a misquote.
Yoon et al. 2017, as read by the simulator agent [D-ag]: aft rotors make 30 % more thrust than fore, against 58 %
isolated, so 28 percentage points; the aft-rotor loss is −17.7 % at 10 m/s and −12.8 % at 5 m/s.
VESPER: rotor centres 2.70 m apart, D 2.6 m → **gap 0.10 m = 0.04D** [K] — outside the studied range. Sim: per-rotor
thrust factor 0.97 in hover [Y], wake-ingestion loss for downstream rotors in forward flight (azimuth-dependent) [Y].

### 4.6 Blade loading, flapping and the Lock number
- Lock number γ = ρ a c R⁴ / I_b. Mars Helicopter: **γ = 0.3, flap ~2/rev, ~3 % critical damping**; Earth blades ~50 %
  critical [D, E_17].
- VESPER at 55 km: **γ ≈ 9.3** (16 at 50 km, 4.7 at 60 km, 2.5 at 64 km) [K; I_b and a are Y inputs, E_17].
  Rough flap damping ζ ≈ γ/16 ≈ 0.6 at 55 km [K, textbook relation, not read today]. → Venus blades are well damped:
  quasi-steady flapping (tip-path-plane tilt follows cyclic/gusts within ~1 rev) is adequate for the sim; Mars-type
  resonant flap modes are not a problem below ~60 km [Y].
- Dense CO₂ raises aerodynamic loads per unit blade area at a given tip speed (q = ½ρV², ρ 0.89 vs 0.015 kg/m³ on Mars):
  VESPER's blade root bending and fatigue come from aerodynamics, not centrifugal stiffening; doc 25 sizes the blade
  flap frequency at 1.7/rev [D-ag doc 25].
- Large slow rotors respond slowly in rpm (VESPER 0.30 s for 20 % rpm, sim_params) → attitude by collective pitch [D-ag doc 25].

### 4.7 Gust response [K/Y]
Heave damping (BEMT ∂T/∂w = −31.8 N per m/s for the whole vehicle, sim_params) gives a heave time constant m/|∂T/∂w| ≈
43.7/31.8 ≈ 1.4 s. Against component A (τ ≈ 1500 s) the vehicle simply drifts vertically with the cell; altitude hold
then costs ΔP ≈ T·w_air (≈ 0.38 kW per m/s at hover thrust 380 N) for many minutes. Against component C (seconds) the
response is a thrust/attitude transient. Both must be in the sim.

### 4.8 What a realistic sim needs (minimum set) [Y, with sources]
1. 6-DOF rigid body, quaternion attitude, gravity g(z) [E_06].
2. Atmosphere lookup ρ, T, a, µ (z, latitude, envelope case) [csv].
3. Per-rotor BEMT (thrust, torque, H-force, rolling/pitching hub moment), Re/M-dependent polars, Pitt–Peters inflow,
   Johnson VRS increment, interaction factor [E_14–E_16].
4. Quasi-steady flapping (γ ~9) — tip-path-plane tilt from cyclic and gusts [E_17].
5. Motor: DC model (K_t, R, L), gearbox (ratio 5, efficiency), rotor+gear inertia, current/voltage limits; collective
   actuator first-order 0.1 s [sim_params, Y].
6. Battery: equivalent circuit (OCV(SOC), R0, one RC), temperature-dependent resistance and limits: charge 0–45 °C,
   discharge −20…60 °C (NCR18650B) [D-ag]; thermal node.
7. Solar: diffuse model P(μ0) and bifacial underside × up/down ratio [E_03, D-ag].
8. Flight controller: cascaded attitude/rate (200–500 Hz; Ingenuity 500 Hz [D-ag]), altitude and airspeed loops in the
   air frame; motor-out mixing for the hexacopter.
9. Wind: mean profile + shear + the four turbulence parts [json].
10. Sensors: IMU noise/bias, baro altitude (±0.19 km site spread [D-ag doc 25]), airspeed, relay Doppler fixes; no GNSS,
    no magnetometer heading (no global magnetic field [D-ag VAPS]).
11. Comms: relay windows and 2.3–14.3 min one-way light time [D-ag doc 25].

---

## 5. How to build it

### 5.1 Concepts compared [Y, anchors tagged]
| Concept | For | Against | Precedent |
|---|---|---|---|
| Hexacopter (VESPER) | motor-out tolerant, folds into an aeroshell, solar deck between rotors | tight rotor spacing; many actuators | MSH chose a hexacopter for 17.7–31 kg [D-ag]; hub/arm weight relations [D, E_17] |
| Coaxial (Ingenuity-like) | compact, one mast | coax induced-power penalty κ_int ≈ 1.28 [D-ag Syal]; large coax judged hard to control in MSH [D-ag] | Ingenuity 1.8 kg, 72 flights [D-ag] |
| Single main rotor + tail | best hover efficiency | tail rotor power, complex hub, one point of failure | — |
| Octo-coax (Dragonfly) | redundancy, compact | coax penalty, mass | Dragonfly, Titan ρ 5.4 kg/m³ [D-ag] |
| Tilt-rotor / lift+cruise | faster cruise | the mission needs no speed (air-mass frame); station keeping would need 49–84 m/s | VAPS solar airplane needs ~100 m/s to stay on the day side [D-ag] |
| Rotor–balloon hybrid | survives the night (buoyancy carries weight) | larger, slower; mentor approval needed | VEGA 3.5 m SP balloon, 46 h [D-ag]; VFM 15 m + 7.5 m variable-altitude aerobot [D, E_19]; JPL 1/3-scale flights 2022 [D-ag] |

### 5.2 Materials (acid + 0…80 °C)
FEP/PFA skins and leading-edge strips; titanium vessel; CFRP structure *wrapped* in FEP (CFRP acid data missing — a
qualification item); FFKM seals; Parylene + FEP over solar cells [D-ag/A, §3.3]. JPL aerobot: Teflon FEP/Kapton,
silvered (α 0.08, ε 0.52), targets 60 °C and > 94 % acid [D-ag, B_izraelevitz2025].

### 5.3 Motors and drive
NdFeB SH grade max working 150 °C; standard N grade 80 °C [D-ag, D_eclipse_magnets]; SmCo ~300 °C [D-ag doc 25].
Sealed can per rotor with a planetary gearbox (doc 25: 5:1). Motor sizing rule (MSH): 150 % of hover power [D, E_17].
Motor mass W = 0.076·Q^0.86 (MH-calibrated; small-motor scale, unit of Q not printed) [D, E_17].

### 5.4 Electronics, thermal
Venus' problem is heat: ambient 26 °C at 55 km but 75 °C at 50 km [csv]; automotive grade-1 electronics 125 °C [D-ag,
D_aec_q100]. Use the k (W/m K) and µ columns of the csv for convection; doc 25 uses a diode heat pipe and aerogel [D-ag].

### 5.5 Power
Solar: triple-junction, Parylene/FEP coated; JPL target > 20 % efficiency, > 40 W/kg, > 100 days at 52–62 km [D-ag,
D_jpl_solar_acid_2022]; MSH cell mass 2.0 kg/m² [D, E_17]. Batteries: Li-ion cells 243 Wh/kg (NCR18650B), Ingenuity
pack cells 163 Wh/kg [D-ag]; MSH pack 230 Wh/kg, 218.5 Wh/kg end of life, 70 % usable [D, E_17]; primary LiCFx 450 Wh/kg
(VLF) or Li-SOCl₂ 468 Wh/kg, −60…+85 °C [D-ag].

### 5.6 Comms and navigation
Relay orbiter UHF/S-band: VLF ~16 contacts of 8–10 min per circumnavigation [D-ag, D_agrawal_2022]; VFM aerobot one
10-min contact per day via SmallSats, 2 Gbit storage, altitude from ranging ±1 km [D, E_19]; VEVA 400 MHz, 1 W, 200 km,
500 kbps [D-ag]. Navigation: IMU + airspeed + baro + relay Doppler; no magnetic field; Sun fixes in cloud impractical
[D-ag VAPS]; Skypersonic's GPS-denied "Skyloc" tracking is the Earth analogue [D-ag, E_18].

### 5.7 Entry and deployment
Rigid 45° aeroshell (VFM aerobot 2.8 m, 4000 W/cm², two 27.4 kg chutes [D, E_19]); spin-up under the parachute and
release below 2.9 m/s at 1000–800 m (Dragonfly) [D-ag]; mid-air helicopter delivery: 3 s free fall, 12 s spin-up
[D-ag, C_delaune2022]; Landis entry-mass fractions: chute 10 %, deployment 15 %, airplane 20 % [D-ag].

### 5.8 Mass-estimation relations a designer can use
| Item | Relation | Tag |
|---|---|---|
| Ideal hover power | P = T^1.5 / sqrt(2ρA) / FM (FM 0.6 for VESPER-type rotors) | standard; FM [D-ag doc 25] |
| Blade | 1.1 kg per m² blade area (Mars-calibrated, thin blades; Venus loads are higher → treat as lower bound) | [D, E_17] + [Y] |
| Hub | 0.05·(W/N_rotor) kg per rotor | [D, E_17] |
| Arm (hexacopter) | 0.2·R kg per rotor (Mars); doc 25 sizes CFRP arms at 0.36 kg/m | [D, E_17]; [D-ag doc 25] |
| Fuselage | 28·(W/1000)^(2/3), W in kg | [D, E_17] |
| Motor | 0.076·Q^0.86 | [D, E_17] |
| Flight controls | 0.84 × blade weight | [D, E_17] |
| Solar array | 2.0 kg/m² (Mars cells) or P/(40 W/kg) target | [D, E_17]; [D-ag] |
| Battery | E / (e_pack · usable fraction); e_pack 218.5–230 Wh/kg, usable 0.7 | [D, E_17] |
| Contingency | 20 % of empty weight; MSH designs stop closing above ~35 % | [D, E_17] |
| Entry system | VFM aerobot: aeroshell 572.8 of 1142.9 kg subsystems (50 %); Landis: vehicle = 20 % of entry mass | [D, E_19]; [D-ag] |

---

## 6. LuGus / Skypersonic Mars Drone Simulator, and other Venus aerial platforms

### 6.1 What is public about the Mars simulator
- LuGus portfolio: client Skypersonic, date 01/09/2022, **"Powered by Liftoff"**, a training tool for NASA's Mars Analog
  Mission, tested by ESA astronaut Roberto Vittori, a testing ground for *Liftoff: Offworld* [D, E_18].
- Liftoff: Offworld (announced Aug 2022): "physics sandbox layer on top of the Liftoff simulation", exploration and
  physics experiments, Ingenuity-inspired; Early Access PC/Mac/Linux [D, E_18].
- Liftoff is a Unity title whose 2022 update rebuilt flight physics with a new flight controller relying less on Unity
  physics [D-ag, E_18].
- Skypersonic: five-year NASA contract for drones/rovers in simulated Mars missions (CHAPEA, one-year crew stay in a
  1,700 ft² habitat at JSC); July 2022 Mt Etna trials flown from Houston; GPS-denied "Skyloc"; NASA staff trained on a
  "Martian Simulator" built from photos/videos of the Martian surface [D-ag, E_18].
- **Not public:** the Mars simulator's gravity/atmosphere/rotor model, latency model, or validation [E_18].

### 6.2 Mirror it for Venus — "what a Venus version needs" [Y]
| Mars simulator element (inferred) | Venus version |
|---|---|
| Mars gravity 3.71 m/s², thin air ρ ~0.015 | g 8.71 m/s², ρ 0.4–1.6 kg/m³ over 60–50 km with envelope (§1) |
| Terrain from orbital imagery | no surface in view: cloud volume, layer boundaries, diffuse light, 1–2 km visual range (§3) |
| Local winds | super-rotation as a moving frame + shear + convective cells/downdrafts (§2) |
| Drone physics (Liftoff core) | slow large rotors, collective control, VRS at 1.2–3.9 m/s descent, rotor interaction (§4) |
| Battery sag | battery + solar energy budget, temperature limits in dives, night = end (doc 25) |
| GPS-denied piloting, delay | air-frame navigation, relay windows, 2.3–14.3 min light time → supervised autonomy |
| Training scenarios | parachute release and pull-out, ride the downdraft, dive budget, relay windows, sunset (doc 25 §6.1) |

### 6.3 Other Venus aerial platforms — key numbers
| Platform | Numbers | Tag, note |
|---|---|---|
| VEGA balloons (1985) | 3.5 m SP balloon, 7 kg gondola, 53–54 km, ~46 h, ~11 000 km | [D-ag] B_vaps2018 |
| JPL Venus Aerial Platforms study (VAPS 2018) | 7.4 m SP balloon carries 110 kg gondola with 25–30 kg payload at 54 km; variable-altitude 50–60 km; 30 kg payload → ~750 kg arrival (SP) / ~1200 kg (variable altitude); solar airplane needs ~100 m/s | [D-ag] B_vaps2018 |
| Venus Flagship aerobot (2020) | 15 m ZP + 7.5 m SP, 52–62 km, ≥ 60 days, 1403.5 kg MEV, 124.9 W day / 35.9 W night, 2.8 m aeroshell | [D] E_19 |
| JPL aerobot prototype (2022) | 1/3 scale; balloon 21.3 kg, control module 19.5 kg, gondola 7.0 kg; flown at Venus 54–55 km density (1.1–2.2 km on Earth) | [D-ag] B_izraelevitz2025 |
| Full-scale aerobot | ~12.5 m, 100 kg gondola, 52–62 km, goal 117 days | [D-ag] B_izraelevitz2025 |
| Venus Life Finder balloon | entry 11.33 km/s, −10°, 1.5 m probe; cycles 48–60 km; LiCFx 450 Wh/kg + ~12 W solar | [D-ag] D_agrawal_2022 |
| VAMP (NG/L'Garde) | inflated before entry, β < 50 Pa, 50–60 km, months to a year | [A] B_vamp |
| NASA Ames survey 2026 | no rotorcraft concept inside the 50–60 km cloud layer | [D-ag] C_young2026 |

---

## 7. What the simulator must model and why — ranked by impact

| Rank | Model | Why (number) | Source |
|---:|---|---|---|
| 1 | **Density vs altitude with envelope** | thrust ∝ ρ at fixed rpm/pitch: ρ(52)/ρ(55) = 1.40, ρ(58)/ρ(55) = 0.68; a 3 km downdraft excursion changes thrust by ±30–40 %; site spread −4/+2 % at 55 km | [K] csv |
| 2 | **Air-mass frame + super-rotation + shear** | 60–85 m/s at 50–60 km vs ~23 m/s max airspeed (doc 25): the vehicle cannot hold ground position; a 5 km climb changes the wind by ~21 m/s | [K] csv; [D-ag] doc 25 |
| 3 | **Convective vertical wind (slow) + downdraft events** | σ_w 0.7 m/s ≈ 0.27 v_h with 25 min correlation; −3.5 m/s downdrafts for 1–2 h; holding altitude costs ~0.38 kW per m/s | [K on D] E_04 |
| 4 | **Rotor model: BEMT + dynamic inflow + VRS** | v_h only 2.6 m/s → VRS at 1.2–3.9 m/s descent; inflow lag 0.21 s; deployment pull-out crosses the VRS band | [D] E_14, E_15; [K] |
| 5 | **Energy: diffuse solar + albedo + battery** | all light diffuse at 55 km; underside gets 0.86 of the down flux; night ends the mission (doc 25) | [K on D] E_03, E_12 |
| 6 | **Battery/electronics thermal vs altitude** | air 75 °C at 50 km vs Li-ion discharge limit 60 °C → dive limits | [K] csv; [D-ag] |
| 7 | **Rotor–rotor interaction** | 0.04D tip gap; ≥ 2 % hover loss, larger in forward flight | [D] E_16; [K] |
| 8 | **Small-scale turbulence (Dryden)** | σ_u ~1 m/s at 30–130 s periods; exercises the attitude loop | [D-ag] A_vega1985; E_13 |
| 9 | **Comms/autonomy** | 2.3–14.3 min light time; relay passes minutes per orbit → no live stick | [D-ag] doc 25; E_19 |
| 10 | **Visuals: cloud layers, haze, light** | visual range ~2 km (middle), ~1 km (lower), ~7 km (upper); layer tops at 50.5/56.5/70 km; no shadows | [K on D] E_12 |
| 11 | Flapping dynamics | γ ≈ 9 → well damped; quasi-steady is enough (unlike Mars, γ 0.3) | [D] E_17; [K] |
| 12 | Acid exposure counter, gravity waves | slow degradation; GW ±0.5–1 K, visual banding | [D-ag]; [D] E_10 |

---

## 8. Discrepancies with doc 25 and `sim_params.json`

| # | Item | Doc 25 / sim_params | This data book | Effect / suggestion |
|---:|---|---|---|---|
| 1 | Vertical gust correlation | `vertical_gust_correlation` 80 s [Y] ("inside the measured 30–130 s periods"); doc 25 §4.7 "80 s correlation [Y]" | VEGA W_a autocorrelation 1/e ≈ **1500 s** (R 0.53–0.56 at 1200 s) [K on D, E_04]; the 30–130 s periods are *horizontal* fluctuations | The 4 m RMS / 14 % thrust result in doc 25 §4.7 uses the wrong time scale. Re-run gust response with component A (τ 1500 s) + component C (Dryden). Expect slower, longer altitude-hold power excursions, smaller fast transients. |
| 2 | Atmosphere above 64 km | VIRA-like table, no envelope (`density_low/high` null) | GRAM 10N matches it within ~2 % at 65–70 km, but 80°N and the PV North probe are **25–30 % less dense** [D-ag E_07; D E_01] | Add a latitude envelope above 60 km (csv `rho_gram_lat_lo/hi`). |
| 3 | Descent to cruise | doc 25 §5: "3 m/s to 55 km (~33 min)" | VRS band for VESPER 1.17–3.89 m/s unless airspeed ≥ 2.5 m/s [K on D, E_14] | State that the descent is flown with forward speed (or ≤ 1.1 m/s vertical); add a sim check. |
| 4 | Rotor spacing | doc 25 §4.1 "rotors do not overlap" | true, but tip gap is 0.10 m = 0.04D; NASA CFD shows ~2 % loss already at 0.3D [D, E_16] | BEMT power has no interaction loss; add ≥ 2–4 % hover penalty and a forward-flight wake factor. |
| 5 | VRS model | `vortex_ring_band` [0.5, 1.5] v_h, "thrust −20 % inside unless airspeed > v_h" [Y] | Johnson: −0.45…−1.5 v_h, effect vanishes at Vx ≥ 0.95 v_h; parametric model with lag [D, E_14] | Consistent band; replace the flat −20 % by Johnson's model. |
| 6 | Wind column at 55 km | 65 m/s (probes within ±0.5 km) | 63.4 m/s (4-probe interpolation) [K on D, E_02] | Already disclosed in doc 25 §3; no change. Listed for completeness. |
| 7 | Downdraft attribution | doc 25 §3: "the largest downdraft … pushed VEGA-2 ~2.9 km down" | both balloons had large excursions (VEGA-1 to 882 hPa, VEGA-2 to 901 hPa); the strongest 1-h mean was VEGA-1 (−2.23 vs −1.71 m/s) [K on D, E_04] | Wording only; the event parameters (−2…−3.3 m/s, ~2 h, ~3 km) stay valid. |
| 8 | Viscosity | sim_params: pure CO₂ (14.96 µPa·s at 55 km) | mixture 15.03 µPa·s [K on D, E_05] | < 0.5 %; no action. |
Checked and consistent: ρ, T, p at 40–64 km (sim_params = csv mean within 0.1 %); cloud layer limits; up/down light
ratio 0.84–0.89; VEGA σ_w 0.65–0.75 m/s; rotation rate 2.99×10⁻⁷ rad/s; MH flap ~2/rev.

---

## 9. Open questions for the LuGus mentor
1. Is the target a **pilot-training simulator** (like the Mars one, real time, Liftoff/Unity) or an **engineering physics
   engine** (offline, higher fidelity)? Which frame rate and hardware?
2. Can a custom atmosphere + rotor model plug into the Liftoff physics core, or is a stand-alone engine expected?
3. What did the Mars simulator model (gravity, density, wind, latency, sensors)? Was it validated against Ingenuity data?
4. Who flies: a pilot with a 2.3–14.3 min delay, or a supervisor of an autonomous vehicle? Which training tasks matter?
5. "Beautiful visuals" at 55 km means cloud volume with ~2 km visibility and no ground — is that acceptable, or should
   scenarios include the upper-cloud top (~70 km) with a view of the cloud sea and sun?
6. Rotorcraft only, or is a rotor–balloon hybrid acceptable (night survival)?
7. Which data formats and frames do they ingest (JSON/CSV, SI, ENU)?
8. Should the sim include the entry/parachute/release phase, or start in flight?
9. Collaboration path after the Ideathon: student project, internship, or co-developed scenario?

---

## 10. Sources (notes hold page/section references)
E_01–E_04 PDS (Pioneer Venus SED, DLBI, LSFR; VEGA balloons/lander) · E_05 NIST WebBook · E_06 JPL SSD · E_07 Venus-GRAM
(AMAT) · E_08 Ando et al. 2020 Sci. Rep. · E_09 Lefèvre et al. 2017 JGR · E_10 Lefèvre et al. 2018 JGR · E_11
Sánchez-Lavega et al. 2017 SSR · E_12 Knollenberg & Hunten 1980 JGR · E_13 MathWorks Dryden (MIL-F-8785C) · E_14 Johnson
2005 NASA/TP-2005-213477 · E_15 Chen 1989 NASA TM-102219 · E_16 Yoon et al. 2016 · E_17 Johnson et al. 2020 NASA/TM-2020-
220485 · E_18 LuGus / Liftoff / Skypersonic pages · E_19 Venus Flagship Mission Study 2020 · E_20 snippets. Earlier notes:
A_, B_, C_, D_ indexes (tag [D-ag]).
