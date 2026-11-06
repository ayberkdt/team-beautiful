# R_mentor_roleplay_2026-11-04: five challenge statements that H1–H7 do not cover

- **What this is:** a role-play written on 4 Nov 2026. I play a senior RF/surveillance engineer at Advionics /
  Intersoft and mentor the 6-hour "Automated Approach Guidance" challenge. I read doc 24 cold. The question was: what
  else could the real statement be, given only the briefing words "Advionics → radar expertise", "if communication
  with the tower is lost", "translate signal" and "how does the [voice] signal reach the display"?
- **Status:** these are **invented statements [Y]**, not leaked or official text. They are ways to stress-test the
  dossier.
- **Tags** are the same as in doc 24:
  - [D] read from the source by this session;
  - [D-ag] taken from an agent note in this folder;
  - [K] computed in this session;
  - [Y] judgement.
- **Code checked in this session [D]:** I read the APIs of `src/aerokit/approach.py`, `src/aerokit/autoland.py`,
  `src/aerokit/atc/{modes,radar,par,ils,traffic,datalink,guidance,tracker,asterix,psr_processing}.py` and
  `src/aerokit/comms/` (function and class lists, plus the module docstrings).
- **Format:** no tables or figures, on purpose. This is a text note.

**Overlap with doc 18, stated up front.** Doc 18 §2 already *predicted* three nearby topics in one line each:

- P2 ship-deck UAS;
- P3 GNSS jamming/spoofing;
- P4 drone flight inspection.

Statements 1–3 below go at those topics from a different side:

- S1 uses the **ship's IFF array as the sensor on a moving platform**;
- S2 is about **proving an aid's signal in space**, not flying the aircraft;
- S3 is about **spoofed surveillance (ADS-B/Mode S) on the ground**, not spoofed GNSS on the aircraft.

Statements 4 and 5 are in neither doc.

---

## S1 · Ship-deck UAS recovery with the IFF the ship already carries

**Statement (as I would say it on the day).** "A frigate with a non-rotating IFF array like our L-IESA has to recover
a UAS on deck automatically, at night, in sea state 5, and you may not trust GNSS. Use the cooperative IFF/Mode 5 link
the ship already has as your guidance sensor. Tell me what accuracy you really get at 2 NM and at the deck edge. Tell
me how you deal with the deck moving and with the sea acting as a mirror. Tell me when the drone must wave off. I will
judge your error budget built from the antenna's own numbers, and your go/no-go logic. I will not judge the autopilot."

**What I would reward.**

1. An accuracy-vs-range budget built from the array's published numbers [D-ag S_intersoft_liesa_leaflet]:
   - azimuth < 0.1° RMS (stationary);
   - elevation beamwidth > 17°;
   - ±15° roll/pitch compensation;
   - beam re-pointing in 100 ms.

   0.1° is 32 m at 10 NM, 6.5 m at 2 NM and 1.6 m at 0.5 NM [K, R·δ]. Saying out loud that **elevation is the weak
   axis** (a wide beam, sea-surface multipath at low grazing angles) shows the team understands the physics.
2. Pointing out that the ship's array alone cannot do the last 200 m. Then proposing a dissimilar short-range sensor
   for that segment and arguing for it. Candidates:
   - a ranging/monopulse beacon;
   - differential ranging;
   - a Ka-band tracker of the TALS/UCARS kind that doc 18 cites [D-ag].
3. A moving landing frame, landing in a deck-motion quiescent window, and a wave-off rule written as monitor logic
   (alert limit, time to alert).
4. Using Mode 5 for authentication, not only for identity. Leaving the details out of the slide is fine.
5. Validation at sea with SkyRF. The naval IFF blog says SkyRF is "increasingly used at sea" [D-ag
   S_intersoft_naval_iff_blog]. Also AIMS / NATO AEtP 12 test practice [D-ag S_intersoft_aims_cert].

**First hour: what they can reuse.**

- `aerokit.autoland`. `ApproachEKF` already fuses a ground radar as range/azimuth/elevation with an analytic Jacobian
  (`radar_measurement`). `GroundRadar` has a separate sigma per axis. The solution-separation FDE and
  `monte_carlo_autoland` exist. Steps:
  1. Set `sigma_az_deg=0.1`.
  2. Set a much larger `sigma_el_deg`.
  3. Turn GNSS off (`gnss_sigma=None`).
  4. Get the first "no-GNSS, IFF-only" touchdown dispersion.
- `aerokit.approach` provides:
  - `protection_level`, `separation_threshold` and `fault_bound` for the wave-off monitor;
  - `monte_carlo_approach` for gate statistics.
- `atc.radar.ssr_link`, `radar_horizon_m` and `hits_per_scan` give the 1030/1090 MHz link and the update rate.
- `atc.tracker.ImmCv` tracks the UAS from the ship.
- In `atc.guidance`, the rule "needles removed, FLAG, never centred" becomes "wave off".

**Biggest gap.** The landing reference does not move in our code.

- `approach.Runway` is a fixed geodetic threshold (`LocalFrame(lat, lon, elevation)`).
- `GroundRadar.position` is a fixed point in the runway frame [D, code].

The team would need four things:

1. a ship frame with heave/pitch/roll;
2. a deck-motion model and a short-horizon predictor;
3. an elevation-error model for an L-band array over the sea (multipath);
4. a second sensor for the final segment.

None of the four exists. Elevation over water is the part an Advionics engineer will push on.

---

## S2 · Prove the approach aid before anyone flies it: an automated drone inspection campaign

**Statement.** "You have just installed a new approach aid. It can be an ILS or a ground-radar guidance station like
the one in your own concept. Design the automated drone campaign that proves the guidance *in space* is within
tolerance before a manned flight check. Give me:

- the trajectories;
- the truth reference and why it is independent of the aid;
- what you measure;
- the pass/fail rule;
- how many passes you need.

Bonus: the same drone, flown between campaigns, catches an aid that is slowly degrading."

**What I would reward.**

1. A truth reference that is independent of the aid and clearly better than its tolerance, with an uncertainty
   budget:
   - RTK position;
   - time synchronisation;
   - antenna phase centre against the drone's reference point;
   - lever arms.

   Doc 18 already says this in one line (CAT II/III course-alignment σ 1.5 m, so RTK plus an optical/laser tracker).
2. Mapping the campaign onto the sponsor's own patterns [D-ag S_intersoft_skyrf_brochure]:
   - Mini-Orbit (LLZ/DME);
   - Vertical (GP profile);
   - Mini-Approach (LLZ + GP + DME together).

   The sponsor claims a "10-minute flight" and "one campaign per year according to ICAO 8071".
3. A real acceptance statistic. How many samples and passes support "within tolerance with X % confidence"? How do
   you separate the aid's error from the drone's error?
4. The inspection receiver obeys our own rule: a lost or broken signal must read as FLAG, never as a good DDM.
5. A trend/monitoring story. This is how Intersoft sells it: Level 1 monitoring, Level 2 baseline, Level 3
   commissioning [D-ag S_intersoft_radar_services]. SMS already monitors "ILS LOC & GP" [D-ag
   S_intersoft_sms_adsb_leaflet].

**First hour: what they can reuse.**

- `atc.ils`:
  - `ils_baseband(ddm, …, tones=…, carrier=…)` builds the detected 90/150 Hz signal for any DDM, including a dead
    tone or no carrier;
  - `read_ils` reads it back with FLAG logic.

  Sampled along a trajectory, these two are already the measurement half of an inspection receiver.
- `aerokit.approach` provides:
  - `Runway`, `deviation` and `to_dots`, the nominal path and the deviation → DDM/dots conversion (full scale is an
    explicit parameter);
  - `simulate_approach` / `monte_carlo_approach` with a `NavSensor` (bias + Gauss–Markov noise), used to model the
    drone's *truth* error.
- For the radar-aid variant, `atc.par.par_measure`.
- `atc.traffic.surveillance_kpis` is the template for "measured vs truth: bias, sigma, Pd". The same report style
  gives the inspection report.

**Biggest gap.** There is no signal-in-space model. `atc.ils` is a *receiver*: it turns a given DDM into audio and
back again [D, code]. Nothing produces the DDM a real localizer and glide path radiate at a given point. Missing:

- the antenna array pattern;
- beam bends from hangars and terrain multipath;
- the GP's dependence on the ground plane.

The tolerance values are also missing. ICAO Doc 8071 and the Annex 10 tolerances were **not read** in this session.
Without both, "pass/fail" has nothing to measure against. A further gap: no drone dynamics or RTK error model beyond
the generic `NavSensor`.

---

## S3 · Someone is injecting fake aircraft into your approach picture

**Statement.** "An airport wants to monitor automated approaches with ADS-B and Mode S only, because its PSR does not
see low on final. Near the field someone transmits fake ADS-B positions and replays Mode S replies. Show me how the
ground system notices a false or displaced target on final within a few seconds, and still knows who is really there.
Use only equipment an ANSP can install. Then tell me how you would test it with our RES."

**What I would reward.**

1. Saying early that **CRC is not authentication**. A spoofer generates squitters with valid CRCs.
2. An independent check of the reported position from the same 1090 MHz signal:
   - multilateration/WAM by TDOA. One measured campaign gave WAM 6–7 m, ADS-B ~20 m and Mode S radar ~200 m
     horizontal against RTK, with position detection 99.8 % [D-ag R_icao_suricg7_ip14_wam]. That is a State
     information paper, not a specification.
   - Mode S roll-call range from the round-trip time;
   - the PSR presence check where PSR exists.
3. A consistency test with a stated Pfa and Pmd, plus a receiver-siting and GDOP argument (TDOA basics in
   R_mlat_wiki).
4. A test plan that uses the sponsor's tools. RES generates up to 2048 Mode S/ADS-B targets with FRUIT, reflectors
   and "jammer frequencies" [D-ag S_intersoft_res_page]. SMS already monitors MLAT and ADS-B sensors [D-ag
   S_intersoft_sms_adsb_leaflet].
5. Integrity language. Reward a team that says what the display shows while a target is unverified, which is the
   doc 24 rule again. Reward also saying what it must never show.

**First hour: what they can reuse.**

- The `atc.modes` encoders (`encode_df17`, `encode_position`, `encode_identification`, `encode_velocity`,
  `encode_df5`) synthesise the spoofer's squitters exactly as the 20/20 vector tests decode them. With `crc24`,
  `is_valid` and `correct_single_bit`, the team can show "valid CRC, false position".
- `atc.traffic`. `Aircraft` has `adsb` and `transponder` flags and timed `events`. Two ways to attack:
  - add a ghost aircraft;
  - change the reported position of a real one at time t.

  `simulate()` runs the decode → IMM → KPI chain.
- `atc.tracker`: χ² gating and identity-gated association. This is exactly where a displaced ADS-B report should fail
  against the radar track.
- `aerokit.approach.separation_threshold` / `fault_bound` give a two-source position-consistency test with a stated
  false-alert rate.
- `atc.asterix` CAT021 for the output records.

**Biggest gap.** There is no multilateration anywhere in the repository. A search of `src/` and `scripts/` for
`tdoa|multilat` finds nothing [D]. To build it the team needs:

- a TDOA solver;
- a receiver clock-synchronisation model;
- a GDOP map for receiver siting;
- a threat model (what a spoofer can and cannot fake, e.g. it can fake content but not each receiver's time of
  arrival).

Also, the ADS-B quality indicators (NIC/NACp/SIL) are not decoded: `modes.py` has no such field [D, code search]. So
the system cannot yet compare "claimed accuracy" against "measured consistency".

---

## S4 · Design the uplink: radar-derived guidance as data, not voice

**Statement.** "Our ground radar measures the aircraft on final better than a controller can describe it on the
radio. Design the datalink that carries that guidance to the aircraft:

- what is in each message, bit by bit;
- at what rate;
- on which RF channel;
- with what end-to-end latency;
- with what integrity and authentication.

Then tell me what the aircraft shows and does when messages stop. I want a format I could implement and a link budget
I could check."

**What I would reward.**

1. A bit-level message with each field's LSB justified against the guidance tolerance. That means showing the
   quantisation error is small compared with the alert limit. Typical fields:
   - deviation;
   - range;
   - time of measurement (not of transmission);
   - sequence number;
   - integrity/validity flag;
   - authentication tag.
2. A channel choice argued on capacity and spectrum. Candidates:
   - the Mode S 1030 MHz uplink (Comm-A). The 56-bit payload is from general knowledge, **not read this session**;
   - VDL Mode 2 at 31.5 kbit/s [D-ag C_ETSI_EN301841_1];
   - a dedicated link.

   Interrogator load and FRUIT count against the 1030/1090 option.
3. A latency and time-to-alert budget: measurement → processing → transmit → decode → display.
4. Receiver behaviour when messages stop or arrive stale. Coast on INS for N seconds, then remove the needles and
   annunciate.
5. Protection against a spoofed uplink, with a key-management sentence.
6. An "ILS look-alike" output so existing autopilot modes can couple (doc 18 §4).
7. A test with RES or the drone-borne SkyRF Generator, which emulates transponders and interrogators [D-ag
   S_intersoft_skyrf_generator].

**First hour: what they can reuse.**

- `atc.asterix` is a worked example of a bit-exact format with documented LSBs, two's-complement fields, FSPEC and
  round-trip tests. The 1.38 m worst CAT021 round trip against a ~2.4 m LSB is the same quantisation argument the new
  format needs.
- `atc.modes.crc24` and the "20 000/20 000 two-bit errors rejected" test pattern give the integrity check and how to
  test it.
- `atc.par.par_measure` / `talkdown_series` are the guidance source at 1 Hz.
- `atc.guidance.GuidancePanel` is the receiver side. It already has GND GUIDANCE LOST after 5 s, source age, and
  needles removed on V/L FLAG.
- `atc.commhealth` can be reused as the link-state machine.
- `aerokit.comms` (repo code, not listed in doc 24 §5) has:
  - `evaluate_link`, `Transmitter`, `Receiver` and the antennas for the link budget;
  - `uncoded_ber_awgn`, `FixedRateDigitalLink` and `occupied_bandwidth_hz` for the bit error rate (BER) and the
    bandwidth.

  `atc.radar.ssr_link` does the same for 1030/1090.

**Biggest gap.** No message-loss, latency or authentication model exists. `atc.datalink` only maps four CPDLC
uplink elements onto the voice display (UM20/74/117/190) [D, code]. It is not a transport. The team must still build:

- a simulation of message loss and delay over the chosen channel, giving time-to-alert;
- the authentication scheme (nothing cryptographic is in the code);
- the channel-capacity argument under interrogator load.

---

## S5 · You are the test engineer: verification and certification plan for an automated guidance station

**Statement.** "A supplier delivers a radar-based automated approach guidance ground station. You work for the ANSP
and must accept it. Write the verification plan that convinces you and the regulator:

- what you inject with target simulators (RES, RTG);
- what you fly (SkyRF, then an aircraft);
- what you monitor once it is in service;
- how you argue the integrity requirement when you can never fly enough approaches to show it.

Show me your three hardest test cases and your KPI acceptance list."

**What I would reward.**

1. The statistical point, made first: zero failures in n independent trials supports p < 3/n at 95 %. Showing
   10⁻⁷ by test alone would need **about 3.0 × 10⁷ approaches** (10⁻⁵ → 3.0 × 10⁵) [K, −ln 0.05 / p]. So the
   argument must combine:
   - analysis;
   - fault injection;
   - monitoring in service.
2. Layered verification in the sponsor's own ladder:
   - Level 3 commissioning with RTG/RES;
   - Level 2 baseline;
   - Level 1 continuous monitoring [D-ag S_intersoft_radar_services].

   Add regression testing after any firmware or settings change, which RES lists [D-ag S_intersoft_res_page].
3. Hard cases chosen for the guidance function, not for generic radar:
   - a site-survey or calibration bias, which is invisible to noise statistics;
   - a reflection or split plot that puts a second target on final;
   - wrong-aircraft association;
   - transponder failure on short final;
   - a jammer or 4G/5G interference (RTG lists both [D-ag S_intersoft_psr_rtg]);
   - latency growth.
4. A KPI list in the jury's language: Pd, Pfa, accuracy, resolution, plot latency, load (RTG list [D-ag]).
   Thresholds should be tied to the guidance alert limit, not copied from en-route radar.
5. A hazard classification that sets the software assurance level and explains how the architecture keeps it low.
   Doc 24 already has the line "advisory, crew in the loop". For automated guidance the team must say what changes.

**First hour: what they can reuse.**

- `atc.traffic` is already a software RES/RTG stand-in. It has:
  - FRUIT;
  - bit errors;
  - garbling;
  - the I/Q PSR chain with terrain and wind-farm clutter;
  - timed events such as squawk changes.

  `surveillance_kpis` produces the acceptance table against truth: Pd, code correctness, range/azimuth bias and sigma,
  false plots.
- `aerokit.approach.monte_carlo_approach` and `aerokit.autoland.monte_carlo_autoland` give statistical campaigns.
  `k_factor` / `protection_level` give the integrity side.
- Test discipline that carries over directly:
  - the randomised invariant test in `commhealth` (displayed ⊆ received);
  - the two-bit-error rejection test;
  - `03_Advionics/scripts/atc_doc_check.py`, whose "every number in the doc is in the report" check is requirement → evidence
    traceability in small form.

**Biggest gap.**

- No requirements set and no hazard analysis exist. Every test needs a "shall" to trace to.
- The simulator injects *environment* effects, not *equipment* faults. `traffic.Scenario` has noise sigmas but no
  bias, latency or clock-fault inputs [D, code]. Yet a calibration bias is the fault an Advionics engineer will ask
  about first.
- Rare-event statistics (importance sampling or fault-tree budgets) would be new.
- The real RES/RTG scenario interfaces are unknown to us.

---

## Close candidates I did not write up (one line each, [Y])

- **Wind farm planned near the final approach.** Will automated guidance from PSR still work, and what mitigation?
  Reuse is high (the `psr_processing` wind-farm scene; EUROCONTROL zones in R_eurocontrol_wind_turbines). But this
  is close to H3's clutter work.
- **Drones in the approach corridor.** Detection of drones near the approach path and approach-safety alerting,
  using the sponsor's ASR-M drone channel [D-ag S_intersoft_drone_detection]. It is more C-UAS than guidance.
- **Weather and wind shear on final.** The RTG lists weather scenarios [D-ag]. I did not see a weather-radar product
  in the sponsor notes in this folder; I did not search the folder fully for one.

## What the dossier should take from this [Y]

- Add a mentor question to doc 24 §9: "Is the guided vehicle a manned aircraft, a UAS, or the inspection drone
  itself?" The answer separates H5/H7 from S1/S2.
- The three gaps that recur across S1–S5 are:
  1. a moving or arbitrary reference frame;
  2. multilateration (TDOA);
  3. equipment-fault injection (bias, latency).

  None of them is in the code. Any one of them would take more than the first hour on the day.
