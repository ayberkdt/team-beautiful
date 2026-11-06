# Materials catalogue: bracket redesign (EUROAVIA Ideathon 2026, Ansys challenge)

Built on 2026-11-05. The data for each property is in `materials_catalogue.json`, in the same folder. Each record there has a value, unit, temperature, condition, tag, source and the original imperial value. The build script is `D:/tmp_ideathon/ansys/build_catalogue.py` and the figure reader is `figread.py`.

**Tags.** **[D]**: read in a primary or authoritative source this session. **[D-org]**: from the organisers' files. **[S]**: secondary source, with a URL given in the JSON. **[Y]**: my own arithmetic or judgement; the JSON `condition`/`note` field says how. **—** or **-**: NOT FOUND.

**Product basis.** The plate is 70 mm (2.76 in) thick, so every value uses that thickness band:
- S275N: EN 10025-3 band >63–80 mm.
- 2618-T61: MIL-HDBK-5J hand forging, 2.000–3.000 in, minimum direction (LT/ST).
- Ti-8Al-1Mo-1V single annealed: MIL-HDBK-5J plate, 2.501–4.000 in.

All MIL-HDBK-5J values are S-basis.

## 1. At 300 °C, only the titanium has a sourced strength; the 2618 has none

| Material | T (°C) | rho (kg/m³) | E (GPa) | Fty (MPa) | Ftu (MPa) | e (%) | CTE (10⁻⁶/K) | k (W/(m·K)) |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| S275N | 23 | 7 850 | 210.0 | 237 | 422 | 23 | 12.0 | 50.4 |
| S275N | 300 | 7 850 | 168.0 | 185 | — | — | 13.3 | 44.0 |
| S275N | 350 | 7 850 | 157.5 | 170 | — | — | 13.5 | 42.3 |
| 2618 | 23 | 2 768 | 73.8 | 290 | 358 | 4 | 20.8 | 155.8 |
| 2618 | 204 | — | 69.3 | 210 | 215 | 19 | — | — |
| 2618 | 300 | — | — | — | — | — | 24.2 | — |
| 2618 | 350 | — | — | — | — | — | 24.7 | — |
| Ti-8-1-1 | 23 | 4 373 | 120.7 | 758 | 827 | 8 | 8.7 | 6.1 |
| Ti-8-1-1 | 300 | — | 104.8 | 518 | 637 | — | 9.4 | 9.7 |
| Ti-8-1-1 | 350 | — | 102.6 | 488 | 607 | — | 9.6 | 10.4 |

Tags for the cells above:

| Material | T (°C) | rho | E | Fty | Ftu | e | CTE | k |
|:---|---:|:---|:---|:---|:---|:---|:---|:---|
| S275N | 23 | D-org | D-org | D-org | D-org | S | D-org | D-org |
| S275N | 300 | D | Y | Y | - | - | Y | Y |
| S275N | 350 | D | Y | Y | - | - | Y | Y |
| 2618 | 23 | D | D | D | D | D | D | D |
| 2618 | 204 | - | Y | Y | Y | D | - | - |
| 2618 | 300 | - | - | - | - | - | D | - |
| 2618 | 350 | - | - | - | - | - | D | - |
| Ti-8-1-1 | 23 | D | D | D | D | D | D | D |
| Ti-8-1-1 | 300 | - | Y | Y | Y | - | D | D |
| Ti-8-1-1 | 350 | - | Y | Y | Y | - | D | D |

### Notes on the table

**S275N**
- **Source of the 300 °C values.** I took the organisers' 23 °C values [D-org] and multiplied them by the EN 1993-1-2 reduction factors [D]. That source is DSTU-N B EN 1993-1-2:2010, an identical national adoption, read from https://dnaop.com/html/62813_6.html and …/62813_17.html.
- **Reduction factors at 300 °C.** From Table 3.1: k_y,θ = 1.000, k_p,θ = 0.613, k_E,θ = 0.800. From Annex E Table E.1: k_p0.2,θ = 0.78.
- **0.2 % proof stress.** Fty in the table is the 0.2 % proof stress, 237.4 × k_p0.2 [Y]. Two other measures at 300 °C:
  - Effective yield at 2 % strain (k_y): 237 MPa.
  - Proportional limit: 146 MPa.
- **350 °C.** Factors are interpolated linearly between 300 and 400 °C [Y].
- **Thermal values.** CTE (mean from 20 °C) and k come from the EN formulas in §3.4 [Y].
- **Elongation.** The 23 °C value of 23 % is the EN 10025-3 minimum [S].

**2618**
- **Basis.** RT values are from MIL-HDBK-5J Table 3.2.13.0(c), p. 3-211 (PDF p. 513) [D]. The organisers name "T6"; the handbook gives only T61.
- **Directions.** Fty and Ftu are the minimum-direction values:
  - Fty: LT/ST = 42 ksi (290 MPa). L = 46 ksi (317 MPa).
  - Ftu: ST = 52 ksi (358 MPa). L = 57 ksi (393 MPa).
- **No data at 300 °C.** The handbook's effect-of-temperature curves end at 400 °F (204 °C), so the 204 °C row is the hottest point that has data. It uses the 1000 h curves (Fig. 3.2.13.1.1(a)/(b), p. 3-212):
  - Fty: 72.7 % of RT.
  - Ftu: 60.0 % of RT.
- **Elongation at 204 °C.** 18.6 % is the "typical" 1000 h curve in Fig. 3.2.13.1.5.
- **CTE.** Fig. 3.2.13.0, p. 3-209. These are means from 70 °F. The "23 °C" value is actually the 70–205 °F mean, because the curve starts at 200 °F.
- **Conductivity.** 90 Btu/(hr·ft·°F) at 77 °F [D].

**Ti-8-1-1**
- **Basis.** RT values are from MIL-HDBK-5J Table 5.3.2.0(b1), p. 5-29 (PDF p. 921) [D].
- **Strength ratios.** From Fig. 5.3.2.1.1, p. 5-32. This is a single curve for sheet, "Exposure up to 5000 hr", so there is no breakdown by exposure time. The sheet ratios are applied to plate RT values [Y].

  | T | Fty (% of RT) | Ftu (% of RT) |
  |---:|---:|---:|
  | 300 °C (572 °F) | 68.3 | 77.0 |
  | 350 °C (662 °F) | 64.3 | 73.4 |

- **Modulus ratios.** From Fig. 5.3.2.1.4, exposure ≤ ½ h: 86.9 % of RT at 300 °C and 85.0 % at 350 °C.
- **Thermal values.** α (mean from 70 °F) and K are from Fig. 5.3.2.0, p. 5-28.

**Reading uncertainty.** Curve values were read by pixel scan of 300–450 dpi renders, after detecting the gridlines:

| Figure set | Uncertainty |
|:---|:---|
| 2618 strength ratios | ±1 % of RT |
| 2618 residual (exposure) ratios | ±1.5 % |
| Ti strength ratios (scanned figure) | ±1.5 % |
| Ti E ratios | ±1 % |
| 2618 CTE | ±0.03 × 10⁻⁶/°F |
| Ti α and K | ±0.05 (figure units) |

**Conversions.** 1 ksi = 6.894757 MPa; 1 lb/in³ = 27 679.9 kg/m³; 1 Btu/(hr·ft·°F) = 1.7307 W/(m·K); 1 Btu/(lb·°F) = 4186.8 J/(kg·K).

### 2618-T61: strength after exposure (MIL-HDBK-5J, hand forging)

**Strength at temperature, 400 °F (204 °C), % of RT.** Fig. 3.2.13.1.1(a)/(b), PDF p. 514 [D].

| Exposure | Fty | Ftu |
|:---|---:|---:|
| ½ h | 84.5 | 76.2 (same curve as 10 h) |
| 10 h | 82.4 | 76.2 |
| 100 h | 78.3 | 71.1 |
| 1000 h | 72.7 | 60.0 |

**Residual RT strength after exposure at 400 °F, % of as-aged RT.** Fig. 3.2.13.1.1(c)/(d), PDF p. 515 [D].

| Exposure | Fty | Ftu |
|:---|---:|---:|
| 10 h | 97 | 95 |
| 100 h | 90 | 89 |
| 1000 h | 77 | 80 |

**Exposure times covered.** The handbook gives ½, 10, 100 and 1000 h. There is **no 10 000 h curve**, and **no data above 400 °F**. Strength at 300 °C after 1000 h or 10 000 h exposure: NOT FOUND.

## 2. Non-thermal properties, processing, footprint and price

| Item | S275N | 2618 (T61) | Ti-8Al-1Mo-1V (SA) |
|:---|:---|:---|:---|
| K1c (MPa·m^½) | NOT FOUND (EN 10025-3 specifies Charpy energy) | NOT FOUND. Not in MIL-HDBK-5J Table 3.1.2.1.6 [D]; only a generic "2000-series 22–35" web value | 82 [S] (74.6 ksi·in^½), condition not stated. MIL Table 5.1.2.1.1 lists only Ti-6Al-4V [D] |
| Max service T | NOT FOUND. k_y = 1 up to 400 °C is a short-time fire-design factor, not a service limit | 316 °C ("−452 to 600 °F") [D] | 454 °C ("up to about 850 °F") [D] |
| Castable | No as this grade: S275N is an EN 10025-3 hot-rolled product [Y] | No evidence. "Available as hand and die forgings"; all three specs are for forgings [D] | No evidence. Product forms are billet, bar, plate, sheet, strip, extrusions and forgings [D] |
| L-PBF / powder | NOT FOUND | Only after modification: crack-free L-PBF is reported for TiB₂- or Zr-modified 2618. The modified alloy in T6 reached YS 370 and UTS 468 MPa [S] | NOT FOUND (no peer-reviewed study); a supplier sells Ti-8-1-1 powder [S]. "Can be fusion welded readily" [D] |
| CO₂, virgin (kg CO₂e/kg) | 2.031 [D-org]. worldsteel global 1.92 t/t, BF-BOF 2.33 [S] | Not alloy-specific: IAI primary Al 2023 global 14.8 [D]; Europe 6.3 [S] | NOT FOUND for alloy or ingot. Kroll sponge only: 51 [S] |
| CO₂, recycled route | Scrap-EAF 0.69–0.70 t/t [S] | NOT FOUND (recycled-only). IAI primary + recycled mix 10.04 [D] | 7.8 [S] (company claim, recycled Ti powder) |
| Embodied energy (MJ/kg) | 20.17 [D-org] | NOT FOUND | NOT FOUND |
| Price | 0.60–0.70 EUR/kg, Europe plate ex-works, 2025 [S] | NOT FOUND | NOT FOUND. Ti-6Al-4V plate proxy 22–42 USD/kg [S, low reliability] |
| ρ (kg/m³), E (GPa), ν at 23 °C | 7850, 210, 0.3046 [D-org] | 2768, 73.8, 0.33 [D] | 4373, 120.7, 0.32 [D] |
| cp (J/(kg·K)) | 479.4 [D-org]; 565 at 300 °C [Y, EN] | 963 at 100 °C [D] | 502 [D] |

## 3. Specific indices (ρ taken at room temperature for every row [Y])

**Inputs.**
- S275N at 300 °C: Fty = 0.2 % proof stress (k_p0.2 = 0.78), E = 168 GPa.
- 2618: no 300 °C data, so its row is at **204 °C with 1000 h exposure**. Its true 300 °C index is NOT FOUND.
- Ti at 300 °C: plate Fty 518 MPa, E 104.8 GPa.

**CO₂ values used.**
- S275N: 2.031 [D-org].
- 2618: 14.8 [D]. This is global primary aluminium, not the alloy.
- Ti: 51 [S]. This is Kroll sponge only, so it understates the alloy plate.

| Material | T (°C) | Fty/rho (kN·m/kg) | E/rho (MJ/kg) | E^½/rho (GPa^½·m³/Mg) | rho/E^½ (Mg/m³/GPa^½) | CO2·rho/E^½ (kg CO₂·Mg/m³/(kg·GPa^½)) |
|:---|---:|---:|---:|---:|---:|---:|
| S275N | 23 | 30.2 | 26.8 | 1.85 | 0.542 | 1.10 |
| S275N | 300 | 23.6 | 21.4 | 1.65 | 0.606 | 1.23 |
| 2618 | 23 | 104.6 | 26.7 | 3.10 | 0.322 | 4.77 |
| 2618 | 204 | 76.1 | 25.0 | 3.01 | 0.333 | 4.92 |
| Ti-8-1-1 | 23 | 173.4 | 27.6 | 2.51 | 0.398 | 20.30 |
| Ti-8-1-1 | 300 | 118.5 | 24.0 | 2.34 | 0.427 | 21.79 |

**What the indices show** (all rows are [Y]).
- Per unit mass, Ti-8-1-1 at 300 °C is the strongest. Its Fty/ρ is about 5× that of S275N at 300 °C.
- Ti-8-1-1 also has about 1.4× the stiff-beam index E^½/ρ.
- On the CO₂ index the steel is best, by about 4× over the aluminium and about 18× over the titanium. The titanium ratio is a lower bound, because only the sponge footprint is known.

## 4. Contradictions in the organisers' list

**1. 2618 passes "Max service temperature ≥ 300 °C", but nothing sourced shows usable strength at 300 °C.**
- MIL-HDBK-5J claims "excellent properties … to 600 °F" (p. 3-209) [D]. However, every effect-of-temperature figure for 2618-T61 stops at 400 °F (204 °C), PDF pp. 514–517 [D].
- Even at 204 °C, 1000 h exposure leaves only 60 % of RT Ftu and 73 % of RT Fty. After 1000 h at 204 °C, the residual RT Fty is only 77 % [D]. That is the over-ageing signature, and it gets worse with time and temperature.
- AZoM says strength falls at about 200–250 °C and lists 50 % elongation at 260 °C [S]. This is consistent with heavy softening.
- A T6/T61 aluminium alloy at 300 °C sits well above its 195 °C ageing temperature. That ageing temperature comes from the BAM 2618A dataset, https://pmc.ncbi.nlm.nih.gov/articles/PMC12477942/ [S]. The ">300 °C" pass therefore rests on a database ceiling, not on design data.
- The grade label also differs: the organisers name "T6", but the handbook and AMS 4132 are T61.

**2. Ti-8Al-1Mo-1V "single annealed" passes "Additive manufacturing OR Casting".**
- "Single anneal" is a mill-product heat treatment: 1450 °F for 8 h, furnace cool, applied to sheet and plate (p. 5-27) [D]. The handbook lists no cast form [D].
- I found no peer-reviewed AM study of this alloy; only a powder supplier's listing [S].
- The handbook also says the single anneal gives the highest RT strength, while the duplex anneal gives the highest fracture toughness [D]. Yet the selection is gated on K1c. A furnace-cooled near-alpha alloy can also suffer α₂ embrittlement: Horiya et al., Tetsu-to-Hagané 76 (1990) 606, report a >20 % toughness loss [S].
- The Granta record's process flag is therefore not supported by the alloy's documented product forms.

**3. 2618 passes "castable or printable".**
- It is a wrought forging alloy (MIL p. 3-209) [D], and fusion welding is not recommended [S].
- Published crack-free L-PBF work uses chemically modified 2618 (TiB₂ or Zr additions) [S]. Unmodified 2618 is not what those studies printed.

**4. Reference S275N.**
- The organisers' Fty of 237.4 MPa is below the EN 10025-3 minimum of 245 MPa for a 70 mm plate (63–80 mm band) [S]. It is also below the nominal 275 MPa.
- The eco audit models a hot-rolled, normalised plate grade as "Metal powder forming", which is not how this grade is made (`Reference steel bracket eco assessment.prd`) [D-org].
- The organisers' card has no temperature dependence. At 300 °C the 0.2 % proof stress falls by 22 % (k_p0.2 = 0.78) and E falls by 20 % [D, EN 1993-1-2].

**5. Use phase dominates the footprint.** The eco audit uses mass 152, a 1-year life, and a long-haul kerosene aircraft at 4000 km/day for 180 days [D-org]. With those settings, the mass term will outweigh the material's production CO₂. This explains why the organisers rank by ρ/E^½ and not by CO₂ alone.

## 5. Not found (honest gaps)

- **S275N:** ν, Ftu and elongation at 300 °C; K1c; max service temperature; AM evidence.
- **2618:** every mechanical property at 300 °C and 350 °C (E, Fty, Ftu, e), plus ρ, ν and k at 300 °C; K1c; 10 000 h exposure data; recycled-only CO₂; embodied energy; price.
- **Ti-8-1-1:** ρ, ν and elongation at 300 °C; alloy CO₂ and embodied energy; price; AM evidence.

The DTIC report AD0801499 ("Mechanical properties of 2618 aluminum alloy") and ASM Handbook Vol. 2B pp. 328–329 probably hold the 2618 data above 400 °F. Neither could be read: DTIC returned 403, and the ASM chapter is paywalled.
