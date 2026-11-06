# Figür kataloğu: 18 taban figürün 18 tanesi denetimden 0 HATA ile geçti

İddia metni `docs/25_lugus_venus_rotorcraft.md` altyazısından, denetim sonucu `*.denetim.txt` dosyasından okunur. Her figürün `pdf`, `denetim.txt` ve `dw.json` eşi aynı klasördedir.

## Taban ve bütçe figürleri

| Figür | Dosya | İddia (doc 25) | Denetim |
|---|---|---|---|
| F1 | `outputs/F1_altitude_justification.png` | Only 53–58 km gives a battery that can charge (0–45 °C) in air as dense as Earth's. | 0 HATA · 0 UYARI · 1 BİLGİ |
| F2 | `outputs/F2_power_vs_altitude.png` | An overhead Sun covers even hover at every altitude from 50 to 64 km; loiter is covered down to cos z ≈ 0.6. | 0 HATA · 1 UYARI · 2 BİLGİ |
| F3 | `outputs/F3_entry.png` | A shallow, low-β entry keeps VESPER near 56 g; Pioneer Venus' steep entry reached 288 g in our model (276–280 g reported). | 0 HATA · 0 UYARI · 2 BİLGİ |
| F4 | `outputs/F4_mass_budget.png` | Arms, contingency and battery are the largest items of the 43.7 kg; the geared drive is only 3.3 kg. | 0 HATA · 0 UYARI · 1 BİLGİ |
| F5 | `outputs/F5_risk_matrix.png` | Mitigations move every risk at least one cell down or left. | 0 HATA · 0 UYARI · 0 BİLGİ |
| F6 | `outputs/F6_mission.png` | VESPER flies 49 h, 44 h of it on sunlight, and ends in a sunset dive. | 0 HATA · 0 UYARI · 2 BİLGİ |
| F7 | `outputs/F7_trade.png` | Bigger rotors buy sunlight-sustained flight at a mass cost. | 0 HATA · 1 UYARI · 1 BİLGİ |
| F8 | `outputs/F8_bemt_validation.png` | BEMT predicts measured rotor torque within ±10 % at 26 of 27 points (rms 6.3 %; worst 21 %: 5-blade rotor at 4° pitch, near zero thrust). | 0 HATA · 0 UYARI · 1 BİLGİ |
| F9 | `outputs/F9_sensitivity.png` | With the geared drive no single assumption costs more than ~8 h of flight — except a 1 h no-sun battery reserve, which does not close at all. | 0 HATA · 0 UYARI · 0 BİLGİ |
| F10 | `outputs/F10_robustness.png` | The geared 2.6 m design keeps ≥ 43.8 h under every adverse assumption; direct drive does not even close for two of them. | 0 HATA · 1 UYARI · 2 BİLGİ |
| F11 | `outputs/F11_entry_validation.png` | The entry model reproduces 12 historical peak decelerations within 8 %; heating within 10 % for spheres (±10 % is the Venera 11–14 angle range), 20–34 % low for the small Pioneer Venus cones. | 0 HATA · 0 UYARI · 2 BİLGİ |
| F12 | `outputs/F12_deployment_monte_carlo.png` | Pulling out in forward flight keeps every release under ~41 m of altitude loss and out of the vortex-ring state. | 0 HATA · 0 UYARI · 1 BİLGİ |
| F13 | `outputs/F13_day_and_station_keeping.png` | Sunlight carries VESPER for ~2 of the ~6.4 days of a drifting Venus day; holding a ground position would cost tens of kW. | 0 HATA · 1 UYARI · 2 BİLGİ |
| F14 | `outputs/F14_end_of_mission.png` | VESPER never lands alive: with windmilling rotors it takes ~12 h to fall, and its electronics pass 125 °C near 34 km. | 0 HATA · 0 UYARI · 2 BİLGİ |
| F15 | `outputs/F15_margins.png` | Every margin is above 1 except the night; the battery temperature in dives is the thinnest. | 0 HATA · 0 UYARI · 0 BİLGİ |
| B1 | `outputs/variants/budget_update/B1_power_curve.png` | Interaction lifts the minimum power at 55 km and moves it from 8 to 9 m/s. | 0 HATA · 0 UYARI · 0 BİLGİ |
| B2 | `outputs/variants/budget_update/B2_mission.png` | In every interaction case the battery stays above 65 % until the sun is lost; more interaction only shortens the day. | 0 HATA · 0 UYARI · 2 BİLGİ |
| B3 | `outputs/variants/budget_update/B3_options.png` | Small changes buy hours for about 1 kg per hour; a bigger deck costs far more. | 0 HATA · 1 UYARI · 0 BİLGİ |

Set tutarlılığı:

- F1–F15: 0 HATA · 10 UYARI · 2 BİLGİ · SET TUTARLI
- B1–B3: 0 HATA · 0 UYARI · 0 BİLGİ · SET TUTARLI

## v0.7 varyant figürleri: 15 figürün 15 tanesi yeniden üretildi

Kaynak: `figures_status.json`. Altyazı yoktur, iddia için aynı numaralı taban figüre bakın.

| Figür | Dosya | Üretildi | Tabanla aynı piksel | Denetim |
|---|---|---|---|---|
| F1 | `outputs/variants/v0_7_44p6kg/F1_altitude_justification.png` | evet | evet | 0 HATA · 0 UYARI · 1 BİLGİ |
| F2 | `outputs/variants/v0_7_44p6kg/F2_power_vs_altitude.png` | evet | hayır | 0 HATA · 1 UYARI · 2 BİLGİ |
| F3 | `outputs/variants/v0_7_44p6kg/F3_entry.png` | evet | hayır | 0 HATA · 0 UYARI · 2 BİLGİ |
| F4 | `outputs/variants/v0_7_44p6kg/F4_mass_budget.png` | evet | hayır | 0 HATA · 0 UYARI · 1 BİLGİ |
| F5 | `outputs/variants/v0_7_44p6kg/F5_risk_matrix.png` | evet | evet | 0 HATA · 0 UYARI · 0 BİLGİ |
| F6 | `outputs/variants/v0_7_44p6kg/F6_mission.png` | evet | hayır | 0 HATA · 0 UYARI · 1 BİLGİ |
| F7 | `outputs/variants/v0_7_44p6kg/F7_trade.png` | evet | hayır | 0 HATA · 0 UYARI · 2 BİLGİ |
| F8 | `outputs/variants/v0_7_44p6kg/F8_bemt_validation.png` | evet | evet | 0 HATA · 0 UYARI · 1 BİLGİ |
| F9 | `outputs/variants/v0_7_44p6kg/F9_sensitivity.png` | evet | hayır | 0 HATA · 0 UYARI · 0 BİLGİ |
| F10 | `outputs/variants/v0_7_44p6kg/F10_robustness.png` | evet | hayır | 0 HATA · 1 UYARI · 2 BİLGİ |
| F11 | `outputs/variants/v0_7_44p6kg/F11_entry_validation.png` | evet | evet | 0 HATA · 0 UYARI · 2 BİLGİ |
| F12 | `outputs/variants/v0_7_44p6kg/F12_deployment_monte_carlo.png` | evet | hayır | 0 HATA · 0 UYARI · 1 BİLGİ |
| F13 | `outputs/variants/v0_7_44p6kg/F13_day_and_station_keeping.png` | evet | hayır | 0 HATA · 1 UYARI · 2 BİLGİ |
| F14 | `outputs/variants/v0_7_44p6kg/F14_end_of_mission.png` | evet | hayır | 0 HATA · 0 UYARI · 2 BİLGİ |
| F15 | `outputs/variants/v0_7_44p6kg/F15_margins.png` | evet | hayır | 0 HATA · 0 UYARI · 0 BİLGİ |

Set tutarlılığı: 0 HATA · 10 UYARI · 2 BİLGİ · SET TUTARLI
