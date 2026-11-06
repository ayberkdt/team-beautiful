# R4 — Sensor technologies and failure rates (canopy "not locked" alert, Extra NG)

- read by: subagent R4
- date read: 2026-11-04
- Tags: **[D-ag]** = read directly from the source in this session (page or table given). **[Y]** = secondary source, derived value or R4's own interpretation. Every [Y] item says which one.
- Local copies: `D:\tmp_ideathon\easa\dl\hf\` (page images R4 checked by eye: `D:\tmp_ideathon\easa\r4_img\`)

## Sources

| ID | Document | Edition / date | URL | Access |
|---|---|---|---|---|
| S1 | MIL-HDBK-217F Notice 2, Reliability Prediction of Electronic Equipment | Notice 2, 28 Feb 1995 (a scanned PDF; R4 read the page images, not the OCR) | https://www.dinfo.unifi.it/upload/sub/laboratori/labmaq/labme_1/mil_hdbk_217f_2.pdf | open (university mirror; same document as everyspec MIL-HDBK-217F_NOTICE-2_14590) |
| S2 | MIL-HDBK-217F base document | 2 Dec 1991 | https://www.dinfo.unifi.it/upload/sub/laboratori/labmaq/labme_1/mil_hdbk_217f.pdf | open mirror |
| S3 | exida FMEDA + proven-in-use report, P+F inductive NAMUR sensors, Report P+F 03/11-10 R015 | V1 R1.1, July 2004 | https://files.pepperl-fuchs.com/webcat/navi/productInfo/cert/cert0707.pdf | open |
| S4 | P+F SIL Manufacturer's Declaration PF22CERT6588 (NCN4-V3-N0 inductive sensor), exida 2002+FS-0085PF-25N | June 2022 | https://files.pepperl-fuchs.com/webcat/navi/productInfo/cert/cert6588.pdf | open |
| S5 | Honeywell GAPS & HAPS Series Aerospace Proximity Sensors datasheet | 000843-2-EN, 04/21 | https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/siot/en-us/products/sensors/motion-position-sensors/common/documents/sps-siot-haps-gaps-combined-datasheet-000843-1-en-ciid-180941.pdf | open |
| S6 | Schmersal BNS 33-12Z magnetic (reed) safety sensor datasheet | generated 24/08/2024 (hosted by a reseller, indmall.in) | https://indmall.in/datasheets/schmersal/safety-sensors/schmersal-bns-33-12z-101109211.pdf | open; third-party host |
| S7 | FAA AC 43.13-1B CHG 1, ch. 11 | 9/8/98, CHG 1 9/27/01 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf | open |
| S8 | Quanterion FMD-2016 preview (introduction only) | 2016 | https://www.quanterion.com/wp-content/uploads/2015/12/FMD-2016-1.pdf | open preview; **no switch data in it** |

## 1. MIL-HDBK-217F Notice 2: switches, circuit breakers, connectors, connections

### 1.1 Switches, §14.1 (S1 p.14-1, 14-2) [D-ag]
- Model: λp = λb·πL·πC·πQ·πE, in failures per 10^6 h (p.14-1).
- λb (F/10^6 h): Sensitive (MIL-S-8805, 13484, 22614) = **0.49**; Limit (MIL-S-8805) = **4.3**; Reed (MIL-S-55433) = **0.0010**; Pushbutton = 0.10; Toggle = 0.10; Rocker = 0.023; Rotary = 0.11; Thermal = 0.031; Thumbwheel = 0.18; Liquid level = 2.3; Pressure = 2.8; Centrifugal = 3.4; Dual-in-line package = 0.00012 (p.14-1). "Sensitive" is the 217F name for snap-action (micro) switches.
- πL: S = operating load current divided by rated resistive load current. πL = exp((S/0.8)^2) for resistive loads, exp((S/0.4)^2) for inductive loads and exp((S/0.2)^2) for lamp loads. Table values for a resistive load: S = 0.05 gives 1.00, S = 0.1 gives 1.02, S = 0.5 gives 1.48 and S = 1.0 gives 4.77 (p.14-1).
- πC = (NC)^0.33 applies only to toggle and pushbutton switches. All other types use πC = 1. Examples: SPST = 1.0, SPDT = 1.3, DPDT = 1.6 (p.14-1).
- πQ: MIL-SPEC = 1, Lower = 2 (p.14-2).
- πE (switches): GB 1.0, GF 3.0, GM 18, NS 8.0, NU 29, **AIC 10, AIF 18, AUC 13, AUF 22**, ARW 46, SF 0.50, MF 25, ML 67, CL 1200 (p.14-2).

### 1.2 Circuit breakers, §14.2 (S1 p.14-3) [D-ag]
- Model: λp = λb·πC·πU·πQ·πE.
- λb: magnetic, thermal and thermal-magnetic are all **0.34**.
- πC: SPST 1.0, DPST 2.0. πU: 1.0, or 2.5 if the breaker is also used as the power on/off switch.
- πQ: MIL-SPEC 1.0, Lower **8.4**.
- πE: GB 1.0, GF 2.0, GM 15, NS 8.0, NU 27, AIC 7.0, AIF 9.0, AUC 11, AUF 12, ARW 46.

### 1.3 Connectors, general, §15.1 (S1 p.15-1, 15-2) [D-ag]
- Model: λp = λb·πT·πK·πQ·πE, **for a mated pair**. For a single connector, divide by 2 (p.15-1).
- λb: Circular/cylindrical (MIL-C-5015, 26482, 38999, 83723 …) **0.0010**; Rectangular 0.046; Card edge (PCB) 0.040; Rack and panel 0.021; Hexagonal 0.15; RF coaxial 0.00041; Power 0.0070 (p.15-1).
- πT: 20 °C 0.91, 30 °C 1.1, 40 °C 1.3, 50 °C 1.5, 60 °C 1.8, 70 °C 2.0. T0 is the connector ambient plus the insert temperature rise ΔT (p.15-1). Default ΔT for 22 AWG contacts: 2 A gives 4 °C, 5 A gives 19 °C (p.15-2).
- πK (mating/unmating cycles per 1000 h): 0 to 0.05 gives 1.0; >0.05 to 0.5 gives 1.5; >0.5 to 5 gives 2.0; >5 to 50 gives 3.0; >50 gives 4.0 (p.15-2).
- πQ: MIL-SPEC 1, Lower 2. πE: GB 1.0, GF 1.0, GM 8.0, NS 5.0, NU 13, **AIC 3.0, AIF 5.0, AUC 8.0, AUF 12**, ARW 19 (p.15-2).

### 1.4 Connections, §17.1 (S1 p.17-1) [D-ag]
- Model: λp = λb·πE for **one** connection.
- λb: hand solder without wrapping 0.0013; hand solder with wrapping 0.000070; **crimp 0.00026**; weld 0.000015; solderless wrap 0.0000068; clip termination 0.00012; reflow solder 0.000069; **spring contact 0.17**; terminal block 0.062.
- πE: GB 1.0, GF 2.0, GM 7.0, NS 4.0, NU 11, AIC 4.0, AIF 6.0, AUC 6.0, AUF 8.0, ARW 16.

### 1.5 Environment definitions (S2 Table 3-2, p.3-5) [D-ag]
- **AIC** (Airborne, Inhabited, Cargo): the description also covers "inhabited areas in lower performance smaller aircraft such as the T38".
- **AIF** (Airborne, Inhabited, Fighter): the same as AIC but on high-performance aircraft such as fighters.
- **AUC/AUF**: environmentally uncontrolled areas that crew cannot occupy in flight.
- R4 interpretation [Y]: the cockpit annunciator is AIC. The Extra NG is cleared to ±10 g (ACRO I; TCDS EASA.A.620 Issue 04, §A.III.6). **AIF is the conservative case for the aerobatic load spectrum.** The canopy-frame sensor sits in the inhabited cockpit but is exposed to rain and sun whenever the canopy is open. Bracket it between AIC and AUF in the Monte Carlo.

### 1.6 Optoelectronics and lamps (S2 = base 217F; Notice 2 lists no change to these sections) [D-ag]
- §6.11, p.6-19: LED λb = **0.00023**; infrared LED 0.0013. Model λp = λb·πT·πQ·πE.
  - πT: Tj 25 °C 1.0, 50 °C 2.1, 75 °C 3.8.
  - πQ: JANTXV 0.70, JANTX 1.0, JAN 2.4, Lower 5.5, **Plastic 8.0**.
  - πE: GB 1.0, AIC 4.0, AIF 6.0, AUC 6.0, AUF 8.0.
- §20.1, p.20-1, incandescent lamps (aviation service, MIL-L-6363): λb = 0.074·Vr^1.29. Table values: 12 V 1.8, **14 V 2.2**, 24 V 4.5, 28 V 5.4. Model λp = λb·πU·πA·πE.
  - πU (illuminated hours divided by equipment operating hours): <0.10 gives 0.10; 0.10 to 0.90 gives 0.72; >0.90 gives 1.0.
  - πA: AC 1.0, **DC 3.3**.
  - πE: GB 1.0, AIC 4.0, AIF 4.0, AUC 5.0, AUF 6.0.
  - The application note says the model includes tungsten filament wear-out.
- Notice 2 foreword (S1, Foreword item 1.0): Notice 2 updated the models for "relays, switches, circuit breakers, connectors, printed circuit boards … and connections". Optoelectronics and lamps are not in that list. R4 therefore treats the base-document §6.11 and §20.1 as current. [D-ag for the list; the "unchanged" conclusion is Y]

## 2. Proximity / magnetic sensors (vendor and IEC 61508 data)

- **S3, Table 2, p.3** [D-ag]: P+F inductive NAMUR sensors with a standard NAMUR amplifier. The amplifier's own failure rates are excluded.
  - NJ 5-30GK-S1N and most types: λsafe = **15.4 FIT**, λdangerous = **9.63 FIT**, SFF 61.48 %.
  - NJ 2-11-SN types: 19.1 / 10.7 FIT, SFF 64.14 %.
- **S3, Table 4** [D-ag]: with a P+F fail-safe interface (e.g. KFD2-SH-Ex1), NJ 5-30GK-S1N gives 24.9 FIT safe and 0.09 FIT dangerous, SFF 99.64 %.
- **S3 assumptions** (§4–5) [D-ag]:
  - Basic rates come from Siemens SN 29500.
  - Constant failure rate; wear is not included.
  - Average temperature 40 °C; stresses comparable to MIL-HDBK-217F **Ground Fixed**.
  - "Dangerous" means the output current stays above 1.2 mA when the target is within the assured release distance.
- **S3 field experience** (§6.2, p.38) [D-ag]: the variants have between ">35,500,000" and ">2,490,500,000" operating hours.
- **S4 p.2** [D-ag]: NCN4-V3-N0. λsafe 33.3 FIT, λno effect 21.3 FIT, λdangerous **22.1 FIT**, λtotal **76.7 FIT**, SFF 71.24 %, MTTF 1488 years, mission time 20 years, DC 0 %. Same SN 29500, 40 °C, GF-like assumptions.
- **S5 p.3** [D-ag]: Honeywell GAPS and HAPS aerospace proximity sensors.
  - MTBF **500,000 flight hours**, both series.
  - Technology: an improved ECKO (eddy-current killed oscillator) design, i.e. inductive (p.1).
  - Supply 12–32 Vdc (GAPS) or 12–28 Vdc (HAPS); <10 mA; −55 to 115 °C.
  - Sensing distance 3.5 mm (GAPS) or 4 mm (HAPS) maximum; target response time 5 ms.
  - Optional health-monitoring third output state (p.1).
  - The datasheet does not state how the MTBF was derived.
- **S6** [D-ag]: Schmersal BNS 33-12Z magnetic safety sensor with reed contacts. B10D (NC/NO) = **25,000,000 operations**; mission time 20 years (EN ISO 13849-1); maximum switching current 0.4 A, 10 W; assured switching distance ON 5 mm, OFF 8 mm. This is an industrial part, not aerospace-qualified.
- **S7 §11-53c, p.11-16** [D-ag]: proximity switches are "usually solid-state" and "usually rated 0.5 amps or less".
- **S7 §11-53g, p.11-17** [D-ag]: do not use silver contacts for loads below 8 V or below 0.5 A unless the switch is rated for low-energy loads. **This matters for a microswitch that only drives a low-current logic input.** Specify gold or bifurcated contacts.

## 3. Machine-readable table

Rate units: failures per 10^6 h, unless the "failure mode" column says otherwise. "base" means λb before any π factor. Rows marked "computed-R4" are R4's own arithmetic from the factors in §1. They are not source values.

| component | failure mode | rate_per_1e6h_or_prob | environment | source | page_table | tag |
|---|---|---|---|---|---|---|
| switch_sensitive_snap_action | all modes (λb) | 0.49 | base (πE=1) | MIL-HDBK-217F N2 §14.1 | p.14-1 λb table | D-ag |
| switch_limit | all modes (λb) | 4.3 | base (πE=1) | MIL-HDBK-217F N2 §14.1 | p.14-1 λb table | D-ag |
| switch_reed | all modes (λb) | 0.0010 | base (πE=1) | MIL-HDBK-217F N2 §14.1 | p.14-1 λb table | D-ag |
| switch_pushbutton | all modes (λb) | 0.10 | base (πE=1) | MIL-HDBK-217F N2 §14.1 | p.14-1 λb table | D-ag |
| switch_toggle | all modes (λb) | 0.10 | base (πE=1) | MIL-HDBK-217F N2 §14.1 | p.14-1 λb table | D-ag |
| switch_any | πE factor | 10 | AIC | MIL-HDBK-217F N2 §14.1 | p.14-2 πE | D-ag |
| switch_any | πE factor | 18 | AIF | MIL-HDBK-217F N2 §14.1 | p.14-2 πE | D-ag |
| switch_any | πE factor | 13 | AUC | MIL-HDBK-217F N2 §14.1 | p.14-2 πE | D-ag |
| switch_any | πE factor | 22 | AUF | MIL-HDBK-217F N2 §14.1 | p.14-2 πE | D-ag |
| switch_any | πE factor | 1.0 | GB | MIL-HDBK-217F N2 §14.1 | p.14-2 πE | D-ag |
| switch_any | πQ factor (non-MIL) | 2 | any | MIL-HDBK-217F N2 §14.1 | p.14-2 πQ | D-ag |
| switch_sensitive_snap_action | all modes, MIL, S=0.1 resistive | 4.98 | AIC | computed-R4 0.49×1.016×1×1×10 | from p.14-1/14-2 | Y |
| switch_sensitive_snap_action | all modes, non-MIL, S=0.1 resistive | 17.9 | AIF | computed-R4 0.49×1.016×2×18 | from p.14-1/14-2 | Y |
| switch_reed | all modes, MIL, S=0.1 resistive | 0.0102 | AIC | computed-R4 0.0010×1.016×10 | from p.14-1/14-2 | Y |
| switch_reed | all modes, non-MIL, S=0.1 resistive | 0.0366 | AIF | computed-R4 0.0010×1.016×2×18 | from p.14-1/14-2 | Y |
| switch_limit | all modes, MIL, S=0.1 resistive | 43.7 | AIC | computed-R4 4.3×1.016×10 | from p.14-1/14-2 | Y |
| circuit_breaker_thermal | all modes (λb) | 0.34 | base (πE=1) | MIL-HDBK-217F N2 §14.2 | p.14-3 | D-ag |
| circuit_breaker_thermal | all modes, MIL, SPST | 2.38 | AIC | computed-R4 0.34×7.0 | from p.14-3 | Y |
| circuit_breaker_thermal | all modes, non-MIL (πQ 8.4), SPST | 20.0 | AIC | computed-R4 0.34×8.4×7.0 | from p.14-3 | Y |
| connector_circular_mated_pair | all modes (λb) | 0.0010 | base (πE=1) | MIL-HDBK-217F N2 §15.1 | p.15-1 | D-ag |
| connector_rectangular_mated_pair | all modes (λb) | 0.046 | base (πE=1) | MIL-HDBK-217F N2 §15.1 | p.15-1 | D-ag |
| connector_circular_mated_pair | all modes, MIL, 40 °C, πK=1 | 0.0039 | AIC | computed-R4 0.0010×1.3×1×1×3.0 | from p.15-1/15-2 | Y |
| connector_circular_mated_pair | all modes, non-MIL, 40 °C, πK=1 | 0.0312 | AUF | computed-R4 0.0010×1.3×1×2×12 | from p.15-1/15-2 | Y |
| connection_crimp | per connection (λb) | 0.00026 | base (πE=1) | MIL-HDBK-217F N2 §17.1 | p.17-1 | D-ag |
| connection_crimp | per connection | 0.00104 | AIC | computed-R4 0.00026×4.0 | from p.17-1 | Y |
| connection_spring_contact | per connection (λb) | 0.17 | base (πE=1) | MIL-HDBK-217F N2 §17.1 | p.17-1 | D-ag |
| connection_terminal_block | per connection (λb) | 0.062 | base (πE=1) | MIL-HDBK-217F N2 §17.1 | p.17-1 | D-ag |
| connection_hand_solder | per connection (λb) | 0.0013 | base (πE=1) | MIL-HDBK-217F N2 §17.1 | p.17-1 | D-ag |
| led_emitter | all modes (λb) | 0.00023 | base (πE=1) | MIL-HDBK-217F §6.11 | p.6-19 | D-ag |
| led_emitter | all modes, plastic, Tj 50 °C | 0.0155 | AIC | computed-R4 0.00023×2.1×8.0×4.0 | from p.6-19 | Y |
| lamp_incandescent_14V | all modes incl. filament wear-out (λb) | 2.2 | base (πE=1) | MIL-HDBK-217F §20.1 | p.20-1 | D-ag |
| lamp_incandescent_14V | all modes, DC, lit >90 % | 29.0 | AIC | computed-R4 2.2×1.0×3.3×4.0 | from p.20-1 | Y |
| lamp_incandescent_14V | all modes, DC, lit <10 % | 2.90 | AIC | computed-R4 2.2×0.10×3.3×4.0 | from p.20-1 | Y |
| prox_inductive_namur_NJ5-30GK | safe (output to <1.2 mA) | 0.0154 | GF-like, 40 °C | exida P+F 03/11-10 R015 | Table 2 p.3 | D-ag |
| prox_inductive_namur_NJ5-30GK | dangerous (stuck >1.2 mA) | 0.00963 | GF-like, 40 °C | exida P+F 03/11-10 R015 | Table 2 p.3 | D-ag |
| prox_inductive_namur_NCN4-V3-N0 | total | 0.0767 | GF-like, 40 °C | P+F PF22CERT6588 | §4 p.2 | D-ag |
| prox_inductive_namur_NCN4-V3-N0 | dangerous | 0.0221 | GF-like, 40 °C | P+F PF22CERT6588 | §4 p.2 | D-ag |
| prox_inductive_aero_Honeywell_GAPS | all modes (1/MTBF; MTBF 500,000 FH) | 2.0 | aerospace, vendor claim | Honeywell 000843-2-EN | Table 1 p.3 | Y |

The next row is kept in its own table because it counts operations (cycles), not hours:

| component | failure mode | B10D_operations | environment | source | page_table | tag |
|---|---|---|---|---|---|---|
| reed_safety_sensor_Schmersal_BNS33 | B10D, NC/NO contact | 25000000 | industrial | Schmersal datasheet | p.1 safety data | D-ag |

Notes on the table:
- Each value keeps the number of decimals its source printed. The datawiz `tablo.denetle` check (run 2026-11-04) flagged the mixed decimals and the five orders of magnitude in this column as warnings (UYARI). These are deliberate: rounding would change the cited numbers. Use scientific notation in code.
- Units in the sources: S3 and S4 give FIT (failures per 10^9 h). R4 divided by 1000 to get the per-10^6 h values in the table. S5 gives MTBF in flight hours. The 2.0 per 10^6 FH row assumes a constant rate (R4's arithmetic, hence [Y]).
- B10D is a cycle-based figure. Converting it to a rate needs the cycles per hour (e.g. canopy cycles per flight hour). The conversion method in EN ISO 13849-1 is **not verified in this session**.

## 4. Failure-mode split (fails open vs fails closed)

- **Not found in open sources.** FMD-97, FMD-2013 and FMD-2016 (Quanterion) are sold, not free. The open FMD-2016 preview (S8) holds only the introduction and an actuator example; its "Open 75 / Short 15 / Drift 10" table is a made-up example of the method (Table 1-1), **not switch data**. Do not use it.
- The only open, mode-split data R4 found: the safe/dangerous splits in S3 and S4 (inductive NAMUR). Safe failures go to the high-impedance state, which in that convention means "target present / off". Before using them, map the canopy logic (locked ⇔ target present?) onto these definitions [Y].
- AC 43.13-1B §11-53a (S7 p.11-16) [D-ag]: an internal failure of a spring-loaded switch "may allow the switch to remain closed". Inspection is an ohmmeter check: opens in the ON position, shorts in the OFF position. This is qualitative evidence that a stuck-closed mode exists.

## NOT VERIFIED (not read in this session, or not accessible)

1. NPRD-2016 / NPRD-95, NSWC-11 (mechanical), FIDES 2009, IEC 61709, SN 29500 tables, IEC 62380: not opened (paywalled or registration-only). No values taken from them.
2. FMD-2016 switch / reed / Hall failure-mode percentages: paywalled.
3. Hall-effect sensor failure rate: **no open source found**. MIL-HDBK-217F has no Hall-sensor model.
4. Buzzer / piezo sounder failure rate: no source found.
5. Wire (per metre) failure rate: not found. 217F §17.1 covers only connections.
6. Exida SERH (Safety Equipment Reliability Handbook) values for proximity switches: not accessible.
7. Crane and Eaton aerospace proximity sensor MTBFs: not found. Only Honeywell (S5) was read.
8. That MIL-HDBK-217F §6.11 and §20.1 are unchanged in Notice 2: inferred from the Notice 2 foreword list, not by page-by-page comparison.
9. The B10D-to-MTTFD conversion formula (EN ISO 13849-1 Annex C): from general knowledge, not read here.
