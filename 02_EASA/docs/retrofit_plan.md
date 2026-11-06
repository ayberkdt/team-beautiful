# Extra NG canopy LOCK-SENSE retrofit — 12-step plan (EASA Ideathon 2026)

Tags: **[D]** read by the main session from the primary source · **[D-ag]** read by a subagent (note file named) ·
**[K]** computed by `python 02_EASA/scripts/canopy_day.py 02_EASA/inputs/inputs.json` (→ `outputs/day/analysis.md`) · **[Y]** our
design choice or judgement. Evidence files: `02_EASA/research/` (index `00_INDEX.md`).

Conceptual plan for the competition. It does not authorise any modification of a real aircraft: only an approved change,
installed and released by authorised staff, may be flown (steps 11–12).

---

## 0. What we retrofit, in one paragraph

Four fuselage-side **inductive proximity sensors with line-monitored (self-checking) outputs**: one per roller lug on the
left cockpit rim, sensing the steel **shoot-bolt tip at full engagement depth**, plus one **seated** sensor seeing a steel
target in the canopy frame. They feed a small **alert unit** that ANDs "seated" with "all three bolts engaged". The unit
lights a **green CANOPY LOCKED** lamp only when that is positively sensed, an **amber** caution in taxi and a **red flashing
CANOPY + voice** warning when take-off power is applied (or in flight) with the canopy not locked. Nothing is mounted
across the canopy/fuselage split line, so the emergency opening/jettison path is untouched. Architecture **A3** in the study [K].

Why this and not a door switch: on the Extra NG a "closed" switch cannot see the hazard. The partially locked canopy looks
identical at the frame edge (AAIB p. 20) [D], and the handle sits at 70 mm both when the canopy is locked and when it is open
with the handles released (AAIB p. 9) [D]. A seated-only switch misses **every** partial lock in the Monte Carlo (C1) [K].

---

## The 12 steps

### 1 · Choose the example aircraft — **Extra NG** (TCDS EASA.A.620)

> **Selected example aircraft: Extra NG** (two-seat ±10 g aerobatic aeroplane, CS-23 Amdt 4, ELA1). We picked it for four
> reasons:
> - It is the aircraft of the challenge's own accident (G-MIIL).
> - It is the only type for which **two regulators** (EASA AD 2025-0156; FAA AD 2026-04-12) state that in-flight canopy
>   openings were mostly due to a partially or improperly locked canopy.
> - Its latch is published in measurable detail: three shoot bolts on one spring-loaded linkage, a 60 mm vs 70 mm handle
>   gap, the wedge-vs-flat roller position (SB-NG-2-22 step 19), and no visible difference at the frame. That lets us size a
>   real sensor and trip point.
> - It has no canopy warning today; the fixes so far are placards and wording (~$180 per aircraft per the FAA cost estimate)
>   and a new pawl contour.
>
> **Back-up type: Diamond DA40.** It is a very common trainer with a front canopy and a rear door. Its one shared "door open"
> light is routinely lit during open-canopy taxi and ignored (FAA AD 2010-25-01 comment) [D], which makes it the textbook
> cry-wolf case. The same 12 steps apply; the DA40 TCDS and its latch geometry have **not** been read.

| Why | Source |
|---|---|
| It is the challenge's aircraft (G-MIIL, 2 Apr 2022) | AAIB-28120 [D] |
| The unlocked-canopy hazard is documented **on this type**: EASA AD 2025-0156 reason "in most cases ... a partially or improperly locked canopy" | AD p. 2 [D] |
| Two in-flight openings of SP-HMM (18 Mar 2022, 4 Aug 2023); 2023 cause: pawls only partially engaged, "not precluded" by the design | PKBWL 2023-0061 p. 6 [D] |
| Mechanism published in detail (3 shoot bolts, ramp 15/5 mm, handle 60/70 mm, forces 60/90/136 N) | AAIB pp. 8–10, 20 [D] |
| No electrical canopy warning exists on the type; current mitigations are placards, POH wording, pawl/spring ECOs | AD [D]; PKBWL pp. 7–8 [D]; R1 [D-ag] |
| FAA mirrors the EASA AD (AD 2026-04-12, effective 21 Apr 2026): 30 US aircraft, $95 placards + $85 POH revision per aircraft | Fed. Reg. 91:51, 17 Mar 2026 [D] |
| SB-NG-2-22 step 19 describes the partial lock (lead wedge only on the roller) vs full lock (roller on the top flat, audible/tactile) | SB-NG-2-22A p. 4 [D] |
| ELA1 (MTOW 950 kg) → simplest approval and maintenance regime | R3 [D-ag] |


### 2 · Baseline survey of the aircraft (as-is)

- **Read:** POH/AFM §4 (pre-flight) and §7.7 (canopy) at the current revision (rev. 16 accepted by AD 2025-0156 [D]); AMM
  canopy chapter; SB-NG-1-24 (placards), SB-NG-2-22 (frame bonding), ECO-NG-22-09/23-07 and AI-NG-02-23 (new pawl contour +
  spring, standard from NG061) [D, PKBWL pp. 7–8]. **Not read by us: POH, AMM, SB-NG-1-24, the ECOs**, so the first real task
  is to obtain them from the TC holder.
- **Measure on the aircraft:** handle gap vs bolt-tip depth at each lug (the mapping our tolerance model assumes linear [Y]);
  free space behind each roller lug for a sensor body; rim thickness; cable route to the panel; bus voltage and spare CB
  (12 V battery / 60 A alternator in the Extra lookbook → 14 V bus inferred, R4 [D-ag + Y]).
- **Configuration split:** pre- and post-ECO pawls (s/n < NG061 vs ≥ NG061) need separate sensor brackets and trip settings.

### 3 · Hazard definition

| ID | Hazard | Evidence |
|---|---|---|
| H1 | Canopy seated, handle released but not pulled aft: all three bolts **partially** engaged (common linkage tube) | AAIB p. 9 [D]; PKBWL 2023-0061 p. 6 [D] |
| H2 | One bolt not engaged / loose aft retainer | PKBWL 2022/1097 contributing factor (quoted in 2023-0061 p. 4) [D] |
| H3 | Canopy not seated at all | generic; most visible |
| H4 | Canopy locked at take-off, unlocked in flight (occupant knocks handle; vibration on a partial lock) | PKBWL 2023-0061 findings (9), causes (3) [D] |
| H5 | System gives a **false "locked"** | the design's own hazard; AC 23.1309-1E §11.b forbids a probable misleading safe indication (R4 [D-ag]) |
| H6 | System obstructs emergency opening / jettison | CS 23.807(b)(5) aerobatic egress VSO–VD (R3 [D-ag]); POH jettison (AAIB p. 11) [D] |
| H7 | Structural failure of frame/transparency (the AAIB G-MIIL cause) | AAIB pp. 25–27 [D] — **not addressed by a latch alert**; see option O5 |

Data context [D-ag, R2 + R5]: 241 investigated openings in the public reports searched, **126 lock-related**, **76 of
those in the initial climb**, 16 fatal; spread over many type families (a sample of investigated events, not a rate)
[K, `outputs/day/analysis.md` §7, figures C5–C6].

### 4 · Requirements (numbered, testable)

| Req | Statement [Y unless tagged] | Verified by |
|---|---|---|
| R-1 | Indicate LOCKED only when the canopy is seated **and** every shoot bolt is beyond the engagement threshold | analysis + bench test (step 8) |
| R-2 | P(LOCKED shown \| partial lock) ≤ 1e-3 per check at installation; trip set inside the computed window (67.5–68.7 mm handle-equivalent for 0.3 mm rigging s.d.) | C2 [K]; rigging test |
| R-3 | P(false/nuisance alert) per flight ≤ 1/10 of the unalerted-hazard rate (keeps PPV ≥ 0.9) | C3 [K]; in-service log |
| R-4 | No probable failure gives a misleading LOCKED (green) | FMEA; self-checking outputs; AC 23.1309-1E §11.b [D-ag] |
| R-5 | Loss of power or unit failure → green lamp **off** (positive indication), never "all clear" | design + test |
| R-6 | Red flashing warning + voice "CANOPY, CANOPY" within 1 s of take-off power with canopy not locked; ≤ 1 s after persistence (0.5 s) in flight | logic tests (`tests/test_canopy.py`) |
| R-7 | Colours: red warning, amber caution, green safe | CS 23.1322 (R3 [D-ag]); CS-SC110a §3 [D] |
| R-8 | Voice audible over the cockpit noise (AC 25.1322-1 App. 2 guidance: 200–4 500 Hz, 20–30 dB above ambient, R4 [D-ag]) and always paired with the light (39 % of GA pilots missed an aural alert under load, Dehais 2014 abstract, R4 [D-ag]) | ground run with headsets |
| R-9 | Nothing bridges canopy and fuselage; emergency opening force and jettison unchanged | ground test (step 9) |
| R-10 | Mass ≤ 0.6 kg, power ≤ 2 W at 14 V (4 aerospace sensors < 60 g and < 10 mA each, Honeywell GAPS datasheet [D]; unit + lamps + harness [Y]); corrected in round 3 from an earlier < 0.3 kg guess | weighing, current measurement |
| R-11 | Self-test at power-up (lamps + voice) and an open-canopy plausibility check (bolt sensed while canopy not seated → SENS) | logic tests |
| R-12 | Time-stamped event log (state changes, in-flight loss of lock) readable on the ground; optional discrete to the G1000 data card | design |

### 5 · Sensor selection (with the mechanical reason)

| Option | Senses | Verdict |
|---|---|---|
| Frame-edge "closed" microswitch | seated only | **rejected**: misses every partial lock (C1: P(miss) = 1.0) [K] |
| Handle-travel switch | handle position | **not alone**: 70 mm both locked and open-released (AAIB p. 9) [D]; needs wiring onto the moving canopy |
| **Inductive proximity at each roller lug** (fuselage side), steel bolt tip as target | true bolt engagement depth | **chosen**: no contact, no wire to the canopy, one per bolt catches H1 and H2; NAMUR-type sensors 15.4 FIT safe / 9.63 FIT dangerous, 0.09 FIT dangerous with a line-monitoring interface (exida Table 2, p. 3–4) [D]. Aerospace-grade example: Honeywell GAPS, sealed stainless body, < 60 g, 12–32 Vdc, < 10 mA, −55…115 °C, MTBF 500 000 FH (vendor), optional health-monitoring third output, **sensing distance ≤ 3.5 mm**: the face must sit within 3.5 mm of the bolt tip at full engagement (measure in step 2) [D] |
| Hall sensor + magnet | seated | possible, but magnet near the compass (DO-160 §15 magnetic effect, R4 [D-ag]) → prefer inductive + steel target |
| Reed switch | seated | very low λb (0.0010/10⁶ h, 217F §14.1, R4 [D-ag]) but shock/vibration-sensitive contacts under ±10 g [Y] |

Redundancy: the study shows dual channels (A4) add almost nothing over A3. The residual risk is set by **systematic
rigging error** and **pilot compliance**, not by random sensor failure (Fussell-Vesely ≈ 1e-15 for the sensor terms) [K].
So the money goes to the rigging gauge and nuisance control, not to more sensors.

### 6 · Installation design

- Sensor brackets bolted to existing lug fittings where possible (no new holes in primary structure if avoidable; any
  new hole → structural substantiation). Bonding to the carbon rim only with an approved adhesive and process. [Y]
- Harness: fuselage side only; 22 AWG on a 5 A breaker or smaller (AC 43.13-1B Table 11-3, R4 [D-ag]); dedicated ground
  wire because the carbon fuselage is not a return path (AC 43.13-1B §11-66c, R4 [D-ag]); gold or low-energy contacts for
  signals < 0.5 A (§11-53g, R4 [D-ag]).
- Annunciator in the rear-seat primary field of view (glareshield) + small repeater in the front cockpit [Y]; legend text
  identical to the AFMS ("CANOPY LOCKED" / "CANOPY UNLOCKED" / "CANOPY OPEN" / "CANOPY SENS").
- Voice into the audio panel's unswitched alert input [Y; panel interface not verified].
- Electrical load analysis (ASTM F2490 named in CS-SC110a §3 [D]); separate CB; powered from the same bus as the avionics.
- Environmental: DO-160G sections to address: §4 temperature/altitude, §7 shock (crash safety for the bracket), §8 vibration,
  §15 magnetic effect, §16 power input, §17 voltage spike, §20 RF susceptibility, §21 emission, §22 lightning induced (R4
  [D-ag]; categories not read, DO-160G itself not accessed). Reference point: Honeywell GAPS sensor qualified to §4 D3, §7 B,
  §8 R, §16 A, §22 B3K3L3 (R4 [D-ag]).

### 7 · Electronics and alert logic

As implemented and tested in `src/aerokit/canopy/logic.py` (tests `tests/test_canopy.py` + `tests/test_canopy_day.py`, 24 tests / 125 checks pass) [K]:

| Phase (detected from) | LOCKED | CLOSED, NOT LOCKED | OPEN | SENSOR FAULT |
|---|---|---|---|---|
| Power-up 3 s | lamp + voice test | lamp + voice test | lamp + voice test | lamp + voice test |
| Parked (engine off) | green | white advisory | dark | amber SENS |
| Taxi (engine on, throttle < 60 %) | green | **amber + single chime** | white advisory (taxi-open allowed) | amber SENS + chime |
| Take-off (throttle ≥ 60 % or IAS ≥ 30 kt on ground) | green | **red flashing + voice** | red flashing + voice | **red SENS + voice** (unconfirmed = not locked) |
| Airborne (IAS ≥ 55 kt for 3 s) | green | red flashing + voice after 0.5 s persistence | red | amber SENS |

- Voice for a **new** alert is deferred between 40 kt and 10 s after lift-off (red light still shows); an alert already
  present before the roll keeps its voice: that is the one meant to stop the take-off. Analogy: take-off inhibits in
  AC 25.1322-1 §8d/§13 and the FAR 25.703 take-off configuration warning (R4 [D-ag]). All thresholds [Y].
- Master acknowledge silences the voice; the light stays steady red until the condition clears; a new condition re-arms.
  A breaker pull is not an acceptable primary silencer (AC 25.1322-1 §12e, R4 [D-ag]).
- Green lamp driven by a hardware AND of the sensor outputs (no software in the path to "safe") [Y].
- **Fault-injection demo** (`aerokit.canopy.faults`, 13 cases through the real logic; `outputs/day/fault_demo.html`, ux gate 0 HATA):
  every single sensor fault is either caught or annunciated. A false green appears only for two **double** conditions:
  (a) a hazard + a latent stuck-ACTIVE sensor on the same bolt, and (b) a partial lock + all three sensors mis-rigged early
  with one wrong gauge. Both are left to the pilot's handle check and the ICA gauge test. The demo also found that a sensor
  fault at take-off power gave only amber; it is now red ("unconfirmed is not locked") [K].

### 8 · Bench test

- Mount the three sensors in a lug/bolt rig at the measured geometry; drive the bolt with a micrometer stage from 60 to 70 mm
  handle-equivalent; record switch points of ≥ 30 sensors × 10 cycles → measured σ_trip (the study assumes 0.3 mm [Y]; the
  trip window shrinks to 67.9–68.2 mm at 0.5 mm and closes for worse [K]).
- Fault injection on every channel: open, short, stuck target, supply loss, intermittent (chatter) — the same faults the code
  injects (`aerokit.canopy.sensors.Channel`); expected annunciation per the table above.
- Temperature, vibration and shock per the DO-160G sections in step 6.

### 9 · Ground / functional test on the aircraft

- Rigging with a **go/no-go gauge**: spacer that holds the handle at 67.0 mm (must read NOT LOCKED) and at 69.0 mm (must read
  LOCKED) for every bolt sensor [Y values from C2].
- Every state sequence: open → seated → partial (handle released, not pulled) → full lock; one bolt pulled back by hand
  (H2); master off/on; CB pulled (green must go dark).
- **Emergency opening and jettison test** with the system installed: forces and motion identical to before (R-9).
- Engine ground run: nuisance check at all rpm (vibration chatter), voice audibility with both headset types the
  operator uses (the G-MIIL pilot used in-ear headphones, AAIB p. 7 [D]).
- Compass swing if any magnet is used.

### 10 · Safety assessment

- Functional hazard assessment of the change: missed alert = today's un-equipped aircraft **only if pilots keep their own check**; with complacency (pilots trusting
  the green) a false green is worse than today, so it is treated as at least major (jury Q2; complacency sensitivity in
  `outputs/day/analysis.md` §1); false "locked" =
  potentially major if pilots rely on it → designed out (R-4) and mitigated by keeping the handle check primary; false
  alarm = minor (distraction, possible unnecessary rejected take-off). Class I ceilings per FH (AC 23.1309-1E Fig. 2,
  R4 [D-ag]): minor < 1e-3, major < 1e-4, hazardous < 1e-5, catastrophic < 1e-6.
- Quantified [K]: residual "take-off not locked, no effective alert" per FH: no system 6.0e-4 → A3 3.1e-7 with full
  compliance, ≈ 2e-4 if pilots only probability-match a 3e-4/flight nuisance rate. The design target is therefore a
  nuisance budget, not more sensors.
- FMEA (15 rows) and fault tree with importance measures: `outputs/day/analysis.md` §3 and §5 [K].
- ERCS view (Reg. 2020/2034 scheme as implemented in `aerokit.investigation.ercs_score`): take-off with a partial lock moves
  from **M1 RED** to **M3 YELLOW** when the warning barrier exists [K; barrier states Y].

### 11 · Compliance and approval route

| Item | Route | Source |
|---|---|---|
| Certification basis | CS-23 **Amendment 4** (Extra NG TCDS EASA.A.620); later amendments/ASTM only where they do not affect compliance (21.A.95(c)) | R3 [D-ag] |
| Applicable paragraphs | 23.1309 (system safety), 23.1322 (colours), 23.807(b)(5) (aerobatic egress), 23.783 as analogy (its (e)(3) "not closed and locked" warning only binds doors forward of the propeller → voluntary here); Amdt 6 equivalents 23.2250(e), 23.2315(b), 23.2510, 23.2605(b)(c) | R3 [D-ag] |
| Classification | **Minor change** (21.A.91) — no limitation change, failure effects at most minor/major; consult EASA early because GM 21.A.91 §3.3 says so when in doubt, and §3.4(g) would make it major if a failure effect were hazardous | R3 [D-ag] |
| Who approves | **EASA** directly (21.A.95(a)1, any applicant) or a **DOA** under 21.A.263(c)(1)(2) — best the TC holder Extra or a partner DOA (it owns the latch data) | R3 [D-ag] |
| Why not a standard change | CS-SC110a covers the annunciator only (awareness only, §4; not pilot-owner releasable, §6); the latch sensors are not listed → CS STAN.00 | CS-STAN Issue 4 pp. 128–131 [D] |
| Why not an STC | an STC (Subpart E) is for major changes; only if EASA classifies the change major | R3 [D-ag] |
| UK (G-MIIL was UK-registered) | UK CAA minor change approval or a UK standard change | R3 [D-ag], detail not read |
| Documents | change description; compliance checklist; FHA/SSA + FMEA; wiring diagram + load analysis; environmental qualification statement; bench + ground test reports; installation check flight report; **AFMS**; **ICA** (21.A.7); weight & balance | R3 [D-ag], CS-SC110a §5 [D] |

### 12 · Operation, maintenance and training

- **AFMS (normal procedures):** pre-flight item "CANOPY — handle fully aft to the end stop, LOCK legend visible, **green CANOPY
  LOCKED on**". The handle check stays the primary means; the light is a second, independent confirmation.
- **AFMS (abnormal):** "CANOPY UNLOCKED" on the ground → close throttle, stop, re-lock; on the take-off roll → reject if
  safely possible [Y; to be agreed with the TC holder's existing canopy-opening procedure, not read]; in flight → reduce
  speed, keep flying the aeroplane, do not try to close the canopy, land as soon as practicable [Y].
- **ICA (21.A.7):** functional test and rigging check with the go/no-go gauge at every 100 h / annual inspection and after any
  canopy or lug work (incl. canopy removal per AMM 53-20-01 and SB-NG-2-22, whose foam injection can itself block the locking
  mechanism, SB p. 2 [D]); sensor face cleaning; harness inspection; event-log download. Add to the AMP (ML.A.302(c)(5)(a), R3 [D-ag]).
- **Installation and release:** Part-CAO or Part-145 organisation, or independent Part-66 B1/B3/L certifying staff
  (ML.A.801(b)); **not** the pilot-owner (R3 [D-ag]; CS-SC110a §6 [D] for the annunciator part).
- **Inoperative system:** non-required equipment → deferral under ML.A.403(b)(1), placard **"CANOPY WARN INOP"**, record
  (ML.A.403(d)); an MEL is optional under NCO (NCO.GEN.155(a)) (R3 [D-ag]). With the system INOP the aircraft is flown as
  today (handle + legend check), so no extra operating limitation [Y].
- **Training:** one-page briefing + a ground demonstration of each annunciation (the pilot sees partial-lock → amber,
  throttle-up → red) before first flight; no rating change [Y]. Cry-wolf countermeasure: every nuisance alert written in
  the tech log; the event log lets maintenance find the cause (R-3).
- **Monitoring after entry into service:** collect nuisance-alert rate and caught partial locks per 1 000 flights → this
  replaces our assumed rates [Y] with fleet data; feed back to the TC holder and EASA.

---

## Options beyond the baseline (creative / costly), with feasibility

Options B (LOCK-SENSE Plus), C (powered over-centre lock) and D (two-stage restraint) are worked to full depth, with risk,
mass, power, certification route and cost class, in `02_EASA/docs/23_easa_canopy_retrofit.md` §3.3.

| ID | Option | What it adds | Feasibility [Y] |
|---|---|---|---|
| O1 | **Analog bolt-depth sensing** (analog-output inductive sensor per lug, or a linkage-tube encoder) instead of on/off switching | continuous bolt depth: the unit learns the full-lock position each flight and detects **rigging drift**, the dominant residual in our fault tree [K]. It also trends **bolt play and vibration** in each lug, so a loose fitting gives an amber CANOPY CHECK before an opening (SP-HMM 2022: loose rear-fitting screws and a vibration precursor one flight earlier, PKBWL 2022/1097 pp. 4–7) [D] | medium; cost ↑; still fuselage-side; thresholds need flight data |
| O2 | **G1000 integration** (discrete → CAS message + recorded on the EFIS data card) | one alerting philosophy; a recorded lock state would have **settled the AAIB/BFU disagreement** on G-MIIL (AAIB p. 28) [D] | needs TC holder + avionics configuration → likely TC-holder change; medium |
| O3 | **Haptic cue** (throttle-lever or seat vibration) on take-off power with canopy not locked | salient when the voice is masked (inattentional deafness, R4 [D-ag]) | medium |
| O4 | **Soft take-off interlock**: throttle friction detent that must be overridden when not locked | stronger than an alert | **not recommended**: anything that can restrict power is a new hazard (go-around, rejected-take-off energy); would make the change major [Y] |
| O5 | **Structural health monitoring** of the canopy frame bond and PMMA edge (acoustic emission, fibre-Bragg strain, guided-wave disbond detection) | the only option that addresses the **actual G-MIIL cause** (bond → fatigue, AAIB p. 27) [D] | in-flight SHM low maturity for GA (not researched in this session); realistic near-term: **ICA ground NDT** — tap/ultrasonic bond check of the frame + edge-crack inspection of the transparency at each annual [Y] |
| O6 | **RFID/NFC tag in each bolt tip**, reader at each lug | identity + presence per bolt, no wires to the canopy | low: read range in carbon/metal surroundings, temperature [Y] |
| O7 | **Camera + vision check** of the aft handle legend, EFB app | independent visual channel, logs a picture with each take-off | low–medium; awareness only; software assurance [Y] |
| O8 | **EFB / phone app** via Bluetooth from the alert unit | pre-flight checklist auto-tick, event log, fleet statistics | high (awareness only); cyber and RF-emission checks [Y] |
| O9 | **Helmet with visor** recommendation in the AFMS/Safety Sense | survivability when a canopy is lost (AAIB pp. 23–24: a visor would "probably" have avoided the injury) [D] | high, non-technical |
