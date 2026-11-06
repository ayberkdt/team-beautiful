# 18 · Advionics — "Automated Approach Guidance": who asks, what they will reward, how we answer

Prepared 2026-11-03. Tags as in doc 17: **[D]** read from the source in this session · **[D-ag]** read from the
source by the research agent (note: `prev_guess/03_Advionics/research/R_advionics_research.md`, 762
lines) · **[A]** snippet only · **[K]** computed here (`prev_guess/00_general/scripts/challenges_2026_numbers.py`,
`prev_guess/00_general/challenges_2026/tables.md`) · **[Y]** judgement.

> **Özet (TR).** Advionics NV, Brugge'nin ~10 km yanında, Oostkamp'ta bir **RF / radar / IFF** üreticisi
> (Intersoft Electronics Group; amiral ürün: gemi için dönmeyen L-bandı IFF dizisi L-IESA®). Kendi sitesinde
> yaklaşma/iniş ürünü **yok**; ILS ölçen ve süzülme yolunu kendi kendine uçan **SkyRF®** dronları kardeş şirket
> Intersoft'ta. Jüri büyük olasılıkla RF/radar mühendisleri: **sensör fiziği, açı-menzil hatası, bütünlük
> (integrity), GNSS karıştırma/aldatmaya dayanıklılık** konuşursak kazanırız. En olası görevler: (P1) GNSS'ten
> bağımsız, yer radarı/transponder tabanlı otomatik yaklaşma ("auto-PAR"), (P2) İHA'nın gemiye/dar sahaya
> otomatik inişi, (P3) karıştırma altında çok sensörlü dayanıklı yaklaşma. Hesap aracı `aerokit.approach`:
> pist çerçevesi, sapmalar, rüzgâr üçgeni, soğuk hava baro hatası, FSF stabil yaklaşma kapısı ve sensör
> karşılaştırmalı Monte Carlo yaklaşma simülatörü.

## 1. The sponsor (verified)

- **Advionics NV, Siemenslaan 16, 8020 Oostkamp**; "Innovation for aviation AND defense"; "part of the Intersoft
  Electronics Group"; "RF engineering for defense, aviation, and aerospace solutions"; product **L-IESA® IFF**,
  "the L-band Integrated Electronic Scanning Array, developed for ship-board IFF". The home page mentions **no**
  approach, landing, ILS, guidance, drone or UAS product [D, advionics.be read this session].
- Further [D-ag]: ~200 staff (2025), new 6 000 m² hall opened March 2026, EN 9100 / ISO 9001 / ISO 14001, RF work
  5 MHz–26 GHz, FPGA and embedded firmware in-house, LoI with Kongsberg (GBAD, March 2026), IFF installations in
  more than 20 countries, IDI (France) majority owner since June 2025.
- Sister company **Intersoft Electronics** [D-ag]: **SkyRF®** drone measuring ILS/VOR/DME/GBAS/PAPI with a
  "Mini-Approach" mode that *flies the drone on the glidepath*; Skyguide/FOCA accepted **> 50 % fewer aircraft
  flight checks**; GroundRF ILS receivers; ILS installation/maintenance; MLAT; ASR-M radar with drone detection;
  NORA® non-rotating arrays.
- Not found: any public sponsor list naming Advionics; Advionics software/DO-178C job ads; patents [D-ag].

**Consequence [Y].** Expect RF/radar/IFF engineers on the jury. Every concept must show (1) which sensor, which band,
which aperture, what angular accuracy at which range; (2) integrity — alert limit, time to alert, what happens when a
source lies; (3) what Advionics could *build* (RF front-end, array, transponder, test). A pure "AI camera autoland"
answer can still score, but only framed with an RF/radar monitor around it.

## 2. Predicted formulations, ranked [Y]

1. **P1 · GNSS-independent approach guidance from the ground** (radar/transponder "auto-PAR", datalinked to the
   aircraft as ILS-look-alike deviations). Precedents: precision approach radar; Sierra Nevada TALS ("operates
   without GPS", > 99.95 % recoveries, interoperable with ship UCARS) [D-ag].
2. **P2 · Automated UAS approach and landing on a ship deck or confined site** (frigate customer base; L-IESA).
3. **P3 · Multi-sensor approach guidance that stays safe under GNSS jamming/spoofing** — EASA SIB 2022-02R4 (3 Jul
   2026) asks ANSPs to keep ILS/DME/VOR running and to report all spoofing [D-ag]; EU Council note: Poland
   1 908 → 2 732 monthly cases Oct 2024 → Jan 2025 [D-ag].
4. **P4 · A drone that flies approach paths autonomously for navaid flight inspection** (SkyRF-style): the drone's
   position truth must be independent of the ILS it measures and better than CAT II/III course-alignment σ 1.5 m
   [D-ag CS-AWO] → RTK + optical/laser tracker.
5. **P5 · Low-noise CDO / steep / curved approach guidance** — CDO saves 35 kg fuel and 110 kg CO₂ per arrival on
   average, 1–5 dB [D-ag EUROCONTROL]; LCY 5.5° [D-ag].
6. **P6 · Emergency autoland beyond GNSS** — Garmin Autoland (FAA, 18 May 2020, Piper M600) needs "a GPS approach
   with lateral and vertical guidance" [D-ag] → the gap is GNSS-denied or non-instrument runways.
7. **P7 · HEMS/eVTOL PinS + guided "last mile"** — 97 of > 1015 EGNOS LPV procedures are PinS [D-ag]; vertiport
   specs (PTS-VPT-DSN) are VFR-only [D-ag].

**One architecture slide that serves all seven [Y]:** sensors → fusion with fault detection and exclusion →
protection level vs alert limit → guidance law → annunciation (NAV SOURCE, SPOOF SUSPECTED) → fallback ladder
(ILS → GNSS-verified → ground RF → vision+INS → go-around).

## 3. Numbers to have on the table

Standards [D-ag unless noted]: 3° path, ILS reference datum 15 m (50 ft); CAT I DH 200 ft / RVR 550 m, CAT II
≥ 100 ft / ≥ 300 m, CAT IIIA < 100 ft; localizer sensitivity 0.00145 DDM/m at threshold (→ full scale ≈ ±107 m, [Y]
derived); glide path 0.0875 DDM ↔ 0.12θ; LPV-200 HAL 40 m / VAL 35 m; GLS output latency 400 ms in the CS-AWO
model; > 1015 LPV procedures at 546 European airports (AIRAC 2510); FSF stabilised approach: stable by 1000 ft
IMC / 500 ft VMC, **VREF to VREF + 20 kt**, ≤ 1000 fpm, within one dot [D, FSF BN 7.1 read this session].

Computed for this challenge [K, `prev_guess/00_general/challenges_2026/tables.md`]:
- **Angle error → position error** (`approach_radar_angle`): 0.1° is 32 m at 10 NM, 6.5 m at 2 NM, 1.9 m at
  0.6 NM (≈ the 200 ft point on 3°). Ground-sensor guidance gets *better* as the aircraft closes — the opposite of
  an airborne camera's range-scaled error. Range resolution c/(2B): 1.0 m at 150 MHz bandwidth, 0.3 m at 500 MHz.
- **Monte Carlo at the 200 ft gate** (`approach_montecarlo`; 200 runs per source, 10 m/s wind 40° off the course,
  σ 2 m/s gusts, start 150 m off centreline and 60 m high; `aerokit.approach.simulate_approach`): vertical 95th
  percentile |deviation| — SBAS-like 2.8 m, **0.1° monopulse radar 1.9 m**, 0.3° radar 4.1 m, baro-VNAV at ISA−30 K
  7.6 m with a mean 5.2 m *low*, vision/INS with a 2 %-of-range error 24 m. These are model results with stated
  sensor parameters, not equipment data — say so on the slide.
- **Cold-temperature baro error** (`approach_cold`): at ISA−30 K an aircraft indicating 1000 ft above the station is
  ~104 ft low; at 3000 ft, ~316 ft low. A GNSS-independent *geometric* vertical source removes this.
- **Descent rate** (`approach_descent`): GS × tan γ; 3° at 140 kt = 743 fpm; 5.5° crosses the FSF 1000 fpm line
  above ~103 kt ground speed.
- **CDO length** (`approach_cda`): a continuous 3° descent from 6000 ft starts 18.8 NM out.

## 4. Concept kit for P1 (the one to rehearse)

- **Ground segment:** a compact X- or Ka-band monopulse tracker (or a non-rotating array, Advionics' NORA/L-IESA
  know-how) beside the touchdown zone, plus 3–4 MLAT receivers as a dissimilar second source; cooperative reply
  from the aircraft's transponder (identity + SNR; IFF heritage) [Y].
- **Fusion and integrity:** ground EKF (radar range/az/el + MLAT TDOA), solution separation between the two
  sources, protection level vs alert limit (LPV-200's 35 m vertical as the yardstick), time-to-alert ≤ 2 s [Y].
- **Uplink:** encrypted datalink of deviations formatted like ILS DDM, so existing autopilot ILS/GLS modes couple
  without new airborne certification of the guidance law ("make it look like an ILS") [Y]; INS coasting 5–10 s on
  dropouts; radar altimeter for the flare.
- **Known physics risks to raise ourselves:** elevation multipath below ~0.5° near the ground; Ka-band rain
  attenuation; datalink jamming; wrong-aircraft association (Mode S addressing solves it); spoofed uplink
  (authentication) [Y].
- **Validation:** fly-check the guidance volume with the sponsor's own SkyRF drone [D-ag product; Y use].
- **Certification path:** ground part approved like a navaid (Annex 10-type performance, ground software
  assurance); airborne DO-178C DAL A if coupled below 200 ft; CS-AWO for low-visibility credit [Y].
- **Sustainability:** small or temporary airfields get precision guidance without ILS civil works; fewer
  low-visibility diversions; any path shape (curved, steeper, CDO) can be uplinked, which a fixed ILS beam cannot
  do; operations continue under GNSS interference.

## 5. Tools (`aerokit.approach`, tests `tests/test_approach.py`)

```python
from aerokit import approach as A
rwy = A.Runway(lat, lon, elev_m, course_deg, length=2500, glide_path_deg=3.0, tch=15.24)
x, y, z = rwy.to_runway(lat_ac, lon_ac, h_ac)            # exact ECEF/ENU, curvature included
d = A.deviation(rwy, x, y, z)                             # angular + linear, vertical + lateral
crab, gs, head = A.wind_triangle(tas, course, wind_from, wind_speed)
A.cold_temperature_true_height(indicated_m, station_elev_m, isa_dev_K)
A.stability_violations(h, speed_above_vref, sink, v_dots, l_dots)   # FSF BN 7.1 gate
stats = A.monte_carlo_approach(rwy, [A.NavSensor("radar", sigma=(3, 2, 2), tau=2)], runs=200)
```

Checks [K]: runway-frame round trip to 1 µm; 3° path height and GPIP by hand; wind-triangle crab asin(w/V);
ISA column gives true = indicated; −30 K ≈ (1 − 30/287) of the height near sea level; with perfect navigation the
simulator holds < 2 m vertical / < 1 m lateral at 200 ft in a 10 m/s crosswind; a +15 m sensed-height bias puts the
aircraft ~15 m low. Two simulator defects were found and fixed during this work: the L1 law first used heading
instead of ground track (a 55 m steady offset in crosswind), and the path angle was air-referenced (a −5 m steady
offset in headwind).

### 5a. Integrity, spoofing and the RF link — day command (added 3 Nov evening) [K]

`python prev_guess/03_Advionics/scripts/approach_day.py <card>.json` (~1 min, progress printed) reads runway, conditions and the sensor
list from a card and returns: gate deviation per sensor (Monte Carlo), protection levels VPL/HPL = K·σ + |bias| vs
the LPV-200 limits, a spoofing run and a link budget, plus figures `A1_gate_accuracy`, `A2_spoof_monitor`,
`A3_angle_error_range`.

- **K factor**: K = Q⁻¹(P/2); at P = 10⁻⁷ this is the SBAS K_v = 5.33 [D, Rippl & Perea, ION GNSS+ 2018, read
  this session]. Alert limits: LPV-200 HAL 40 m / VAL 35 m [D-ag]; APV-I/II [A] only.
- **Spoof ramp vs a dissimilar monitor** (`NavSensor(ramp=…, ramp_start=…)`, `simulate_approach(monitor=…,
  threshold=…)`): threshold T = Q⁻¹(P_FA/2)·√(σ_a² + σ_b²) per axis; bound on the undetected error T + Q⁻¹(P_MD)·σ
  (simplified single-fault, two-source form). Rehearsal card (SBAS-like primary, 0.1° radar monitor, −1 m/s vertical
  ramp from 20 s, P_FA 10⁻⁵): alarm after **14 s** at ~670 ft, largest undetected error 13.5 m (bound 19.3 m),
  aircraft **1 m** from the path at 200 ft after excluding the spoofed source; without the monitor it crosses the
  GPIP 68 m high and never gets below ~220 ft. Slide line: "the monitor turns a silent spoof into a 14-second
  alarm".
- **Link budget**: an assumed 250 W reply at 1090 MHz into a 20 dBi receive antenna (8 MHz, NF 4 dB) gives ≥ 53 dB
  SNR at 10 NM, so the monopulse thermal-noise angle error is ~0.002° (k_m = 1.6 assumed, secondary source).
  **Thermal noise is not the limit; calibration bias, ground multipath and reply timing are.** Read the 0.1° used in
  the Monte Carlo as that bias/multipath budget — this is the sentence an RF jury will test.

### 5b. Autoland on fused navigation with fault detection and exclusion (added 4 Nov, 00:30) [K]

`aerokit.autoland` (tests `tests/test_autoland.py`): a 7-state EKF (position, velocity, baro bias) driven by the
IMU, fusing GNSS, a ground radar (range/azimuth/elevation, analytic Jacobian), the baro and a radio altimeter
(< 2500 ft); guidance on the *estimate*; exponential flare from the height where the flare command matches the path
sink (h_f = (V_s − sink_td)·τ, 9.2 m with the defaults); touchdown point, sink and lateral offset per run. Two FDE
modes: per-sensor χ² innovation gating, and a **solution-separation bank** (one sub-filter per left-out sensor,
separation tested with (Pᵢ − P₀) + a 0.5 m floor — the floor is our assumption, needed so the baro, whose bias is
a state, cannot trip the test on linearisation noise).

`approach_day.py` now runs it (card block `autoland`, 20 runs per scenario; the whole command took 3 min 44 s here) and draws `A4_autoland_fde`:

| Scenario (rehearsal card, 10 m/s wind at 40°, gusts σ 2 m/s) | Landed | In touchdown box | GNSS excluded | Honest sensor excluded |
|---|---:|---:|---:|---:|
| Fault-free, all sensors | 100 % | 100 % | 0 % | 0 % |
| GNSS spoof ramp −1 m/s, solution-separation FDE | 100 % | 100 % | 100 % | 0 % |
| GNSS spoof ramp −1 m/s, innovation FDE | 10 % | 10 % | 10 % | **90 %** |
| No GNSS, baro 6.4 m high (ISA−30 K) | 100 % | 100 % | 0 % | 0 % |

Touchdown 354 ± 5–6 m past the threshold; sink at touchdown ~1.1 m/s (target 0.6 m/s; the 1 s sink lag doubles it —
stated, not tuned away). **The finding to put on a slide**: per-sensor innovation tests exclude the *honest*
sensors when the precise source drifts slowly (it drags the estimate with it) — in 90 % of the runs here the
aircraft never lands; testing whole solutions with one sensor left out excludes the spoofed GNSS in every run (5.7 s
after the ramp starts in the run plotted; the delay was not measured across the Monte Carlo). Without GNSS, radar + radio altimeter learn the cold-baro bias (6.2 of 6.4 m) and the
landing is unchanged — the GNSS-independent case Advionics can build.

## 6. Five-hour plan for this slot [Y]

- 0:00–0:20 Restate: vehicle class, environment, minima target, infrastructure allowed, GNSS assumed or not. Ask the
  Advionics mentor whether they care most about sensor hardware, algorithms or the operational concept.
- 0:20–0:50 Requirement table: accuracy at DH, integrity (alert limit, time to alert, risk per approach),
  continuity, availability, latency/update rate, SWaP, cost.
- 0:50–1:40 Two or three architectures → trade matrix weighted by the four jury criteria → choose.
- 1:40–2:40 Detail: sensor physics table (R·δ), fusion + FDE, fallback ladder, 6–8 failure modes, certification.
  Run `monte_carlo_approach` with *our* sensor σ to get one quantified slide.
- 2:40–3:20 Sustainability numbers (CDO 35 kg/arrival; avoided diversions; no ILS hardware; drone flight checks).
- 3:20–4:30 Slides: problem → numbers → concept diagram → approach timeline FAF→touchdown → integrity & failures →
  certification & TRL roadmap → sustainability → why Advionics can build it → summary.
- 4:30–5:00 Rehearse three Q&A: "what if it is spoofed?", "multipath near the ground?", "how do you certify the ML
  part?" (answer: non-ML monitor around it; EASA AI Level 1/2 [D-ag]).

## 7. Open items

Belgian LPV count; ROAAS EU applicability date; Annex 10 primary values; Frankfurt 3.2° primary source; Daedalean
PilotEye status — not verified by anyone this session [D-ag §9].
