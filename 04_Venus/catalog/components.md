# Bileşen kataloğu: v0.7, v0.6'dan +0.979 kg ağır; en büyük fark battery (+0.422 kg)

Kaynak: `outputs/design.json` (v0.6) ve `outputs/variants/v0_7_44p6kg/design.json` (v0.7, onaylanmadı). Sıra, `design.json` sırasıdır. Kütleler kaynaktaki 3 ondalıkla yazılır. Toplam satırı bileşenlerin toplamıdır; `total_mass_kg` alanı v0.6'da 43.66, v0.7'de 44.63 kg yazar.

## Kütle

| id | Etiket | Veri türü | v0.6 (kg) | v0.7 (kg) | Fark (kg) |
|---|---|---|---:|---:|---:|
| `rotors` | Rotors & motors | K | 6.080 | 6.353 | +0.273 |
| `arms` | Folding arms | K | 7.660 | 7.660 | 0.000 |
| `body` | Sealed Ti vessel | K | 3.153 | 3.203 | +0.050 |
| `battery` | Li-ion battery | K | 6.740 | 7.162 | +0.422 |
| `solar` | Bifacial solar deck | K | 4.007 | 4.007 | 0.000 |
| `payload` | Science payload | Y | 3.000 | 3.000 | 0.000 |
| `avionics` | Avionics & IMU | D-ag (MSH 1.2 kg) | 1.200 | 1.200 | 0.000 |
| `antenna` | UHF relay antenna | Y | 0.800 | 0.800 | 0.000 |
| `thermal` | Heat pipe & insulation | K | 0.876 | 0.902 | +0.026 |
| `coating` | Acid-proof FEP skin | K | 0.686 | 0.702 | +0.016 |
| `attach` | Bridle & release | Y | 0.800 | 0.800 | 0.000 |
| `wiring` | Harness | K | 1.373 | 1.403 | +0.030 |
| `contingency` | Mass margin 20 % | D-ag | 7.276 | 7.438 | +0.162 |
| **toplam** |  |  | **43.651** | **44.630** | **+0.979** |

## Ad, malzeme, renk

v0.7 sütunu v0.6'dan farklıysa dolu, aynıysa `=`.

| id | Ad v0.6 | Ad v0.7 | Malzeme | Renk |
|---|---|---|---|---|
| `rotors` | 6 folding 2-blade rotors + 5:1 geared motors + collective actuators | = | CFRP blades with FEP film wrap; Sm2Co17-magnet motors + planetary gearbox in PFA-sealed cans | `#c9cdd3` |
| `arms` | 6 folding CFRP arms with Ti hinges | = | CFRP tube, FEP sleeve, Ti-6Al-4V hinge and latch | `#2b2b2b` |
| `body` | Sealed Ti vessel: battery, avionics, payload electronics | = | Ti-6Al-4V shell, silvered-FEP skin (α 0.08, ε 0.52), dry N2 fill | `#e8e4da` |
| `battery` | Li-ion battery 1044 Wh (inside vessel) | Li-ion battery 1109 Wh (inside vessel) | 18650 energy cells (243 Wh/kg cell), charge 0-45 °C | `#4f6d7a` |
| `solar` | Bifacial solar deck 4.45 m² (6 folding petals) | = | triple-junction cells, Parylene + FEP cover, CFRP frame | `#1f3a5f` |
| `payload` | Science: nephelometer, aerosol mass spectrometer, T/p/wind/turbulence, camera | = | sapphire windows, PTFE inlets | `#d98e04` |
| `avionics` | Flight computer, IMU, baro, sun sensor, radio | = | inside the vessel | `#6b8e23` |
| `antenna` | UHF crossed dipole on mast (relay link) | = | Ti mast, PTFE radome | `#b0b7bf` |
| `thermal` | Aerogel blanket + variable-conductance heat pipe to shell fins | = | silica aerogel, Al/NH3 VCHP, coated fins | `#f2f2f2` |
| `coating` | Acid-protection skin on all exposed parts | = | FEP/PTFE film, PFA coat, Parylene on cells | `#ffffff` |
| `attach` | Bridle ring, pyro release, deployment fittings | = | Ti fittings, Kevlar/PBO bridle | `#a0522d` |
| `wiring` | Harness and connectors | = | PTFE-insulated wire | `#555555` |
| `contingency` | Mass contingency 20 % (MSH practice) | = | — | `#999999` |

## Konum ve boyut

Metre. Çerçeve: başlangıç gövde merkezi, x ileri, y sol, z yukarı. v0.7 sütunu v0.6'dan farklıysa dolu, aynıysa `=`.

| id | Konum v0.6 | Konum v0.7 | Boyut v0.6 | Boyut v0.7 |
|---|---|---|---|---|
| `rotors` | [0.000, 0.000, 0.140] | = | [8.000, 8.000, 0.120] | = |
| `arms` | [0.000, 0.000, 0.140] | = | [5.400, 5.400, 0.060] | = |
| `body` | [0.000, 0.000, 0.000] | = | [0.600, 0.600, 0.320] | = |
| `battery` | [0.000, 0.000, -0.060] | = | [0.420, 0.420, 0.120] | = |
| `solar` | [0.000, 0.000, 0.090] | = | [2.700, 2.700, 0.012] | = |
| `payload` | [0.000, 0.000, -0.250] | = | [0.320, 0.320, 0.180] | = |
| `avionics` | [0.000, 0.000, 0.080] | = | [0.260, 0.260, 0.080] | = |
| `antenna` | [0.000, 0.000, 0.460] | = | [0.340, 0.340, 0.600] | = |
| `thermal` | [0.000, 0.000, 0.000] | = | [0.640, 0.640, 0.320] | = |
| `coating` | [0.000, 0.000, 0.000] | = | — | = |
| `attach` | [0.000, 0.000, 0.190] | = | [0.180, 0.180, 0.060] | = |
| `wiring` | — | = | — | = |
| `contingency` | — | = | — | = |
