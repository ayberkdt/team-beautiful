# R2 — How Precision Approach Radar really works (sourced reference)

Prepared 2026-11-06 for the Advionics challenge. Educational use only. Simulated data only. Nothing here is approved for
flight use.

## 0. How to read this file

**Tags**

| Tag | Meaning |
|---|---|
| [D] | I read the source text itself in this session (PDF text extracted, or page image viewed). |
| [D-sum] | The page was fetched, but I saw only a machine summary of it. Treat as weaker than [D]. Check before you quote it. |
| [A] | Search snippet or search summary only. The page was not opened. Never present this as read. |
| [Y] | My inference or my calculation. |

A source can be [D] and still be old or secondary. The "Class" column below tells you which.

**Sources.** All were read or searched on **2026-11-06**. Each number below carries a source ID and a section. The URL
and date are in this table.

| ID | Document | URL | Class | What I read |
|---|---|---|---|---|
| S1 | ICAO Doc 4444 PANS-ATM, 16th ed. 2016. Record of amendments lists up to No. 13 (27/11/25). Pages used carry 10/11/16, except 8-27 (amended). | https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf | Primary, national authority copy | §8.9.6, §8.9.7, §12.4.2.4–12.4.2.5 [D] |
| S2 | ICAO Annex 10 Vol I, 7th ed. July 2018, Amendments 1–91. | https://ffac.ch/wp-content/uploads/2020/09/ICAO-Annex-10-Aeronautical-Telecommunications-Vol-I-Radio-Navigation-Aids.pdf | Primary, third-party copy | §2.1.5, §3.2, Att. C §4 [D]. Amendments after 91 not checked. |
| S3 | FAA JO 7110.65X, effective 12 Oct 2017. | https://skybrary.aero/sites/default/files/bookshelf/4141.pdf | Primary, but **old edition** | Ch 5 Sections 10–13 complete [D] |
| S4 | FAA AIM 5-4-11 and 5-4-12, page footers 2/20/25. | https://faraim.org/faa/aim/chapter-5/section-5-4-11.pdf | Primary text, mirror | Complete [D] |
| S5 | UK MAA RA 3291 Issue 4, PDF created Sept 2025. | https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf | Primary, current | Complete; Tables 2 and 3 also viewed as page images [D] |
| S6 | UK MAA RA 3292 Issue 4. | https://assets.publishing.service.gov.uk/media/67ea52174a226ab6c41b2083/RA3292_Issue_4.pdf | Primary | ¶11–12 only [D] |
| S7 | UK MMATM Issue 14, file dated May 2025. | https://assets.publishing.service.gov.uk/media/681c9855155568d3da1d2a64/MMATM_Issue_14.pdf | Primary | Ch 3 Figure 2 and ¶1–9; ¶69 radio failure [D]. It sends PAR detail to RA 3291–3295. |
| S8 | UK CAP 413 Edition 23 Corr, 8 June 2020. | https://skybrary.aero/sites/default/files/bookshelf/5761.pdf | Primary, may not be the latest | Ch 10 PAR phraseology [D] |
| S9 | UK CAP 493 Edition 12, 31 Oct 2025. | https://www.caa.co.uk/media/eegmhceu/cap493-edition-12.pdf | Primary, civil | Sect 3 Ch 2 ¶11–15 (surveillance radar approach). No PAR section found by text search. [D] |
| S10 | US Navy RADEIGHT-A Aircraft Control Manual, 21 June 1950, Ch 20. | https://www.ibiblio.org/hyperwar/USN/ref/RADEIGHTA/RADEIGHTA-20.html | Primary, **historic** | Extracts on wave-off, phraseology, sample talk-downs [D] |
| S11 | USAF facility note CATCODE 116401, undated. | https://www.wbdg.org/FFC/AF/AFMAN/116401_Precision_Approach_Radar.pdf | Official, secondary on procedure | Complete [D] |
| S12 | Raytheon patent US 6,600,442 B2, filed 5 Jul 2001, granted 29 Jul 2003. | https://patents.google.com/patent/US6600442B2/en | Patent, exemplary values | Background and Tables 5–8 [D] |
| S13 | ITT patent US 5,907,568, filed 22 Nov 1996. | https://patents.google.com/patent/US5907568A/en | Patent | Text searched [D]; overall summary [D-sum] |
| S14 | L3Harris PAR-2020 sell sheet, 03/2022. | https://www.l3harris.com/sites/default/files/2022-04/PAR-2020_Sell%20Sheet.pdf | Vendor | Complete [D] |
| S15 | ITT Gilfillan brochure, PDF dated 2005. | http://www.mobileradar.org/Documents/ATC_Product_Line_Brochure.pdf | Vendor | PAR-2000, GCA-2000 parts [D] |
| S16 | Raytheon ATNAVICS / FBPAR sheet, 10/06. | http://www.mobileradar.org/Documents/TPN-31.pdf | Vendor | Complete [D] |
| S17 | ENRI slides, "Overview of PAR", Soumu document SAR-2-5. | https://www.soumu.go.jp/main_content/000376472.pdf | Secondary | Slide 3 viewed as an image [D]. Slide 4 numbers only. |
| S18 | FAS page on AN/TPN-22, updated 9 Jan 1999. | https://man.fas.org/dod-101/sys/ac/equip/an-tpn-22.htm | Secondary | [D-sum] |
| S19 | CSG, PAR-E product page. | https://defence.csg.com/en/products/precision-approach-radar | Vendor | [D-sum] |
| S20 | code7700.com, PAR page. Cites AFM 51-37 ¶6-17 and AIM. | https://code7700.com/par.htm | Secondary | [D-sum] |
| S21 | CFI Notebook, Radar Approaches. | https://www.cfinotebook.net/notebook/aircraft-operations/approaches/radar-approaches | Secondary | [D-sum] |
| S22 | AVweb, "Flying the PAR", from IFR magazine Sept 2006. | https://avweb.com/features_old/flying-the-par/ | Secondary | [D-sum] |
| S23 | JetCareers forum, MikeD GCA review. | https://jetcareers.com/forums/threads/mikeds-gca-asr-and-par-approach-review.4099/ | Forum | [D-sum] |
| S24 | VATSIM-PAR-Scope, docs/PAR-RESEARCH.md, hobbyist notes. | https://github.com/yanjz124/VATSIM-PAR-Scope | **Lead only** | Read [D], but its citations to NAVAIR, AFMAN and NAVEDTRA were not checked at source. Use as a pointer, not as proof. |
| S25 | Flight Crew Guide §6.12. | https://www.flightcrewguide.com/guide/approach-and-landing/radar-guided-approaches/ | Secondary | [D-sum] |

Other items appear inline with [A] and their URL.

---

## 1. What the radar measures and outputs

### 1.1 Raw measurement and output

- A PAR has two scanned beams. One scans in azimuth and one scans in elevation. Delay gives range. The radar head sits
  beside the runway near touchdown [D] S13.
- Annex 10 requires detection of an aircraft of 15 m² echoing area or larger [D] S2 §3.2.3.1.1. Its note gives 5–10 m²
  for a single-engine private aircraft, so the standard does not cover the smallest aircraft [Y].
- Older displays plot angle against range, so the straight path looks curved. Modern processing converts to Cartesian
  coordinates centred on touchdown, so the path is straight [D] S12.
- The modern output is a track, not a raw plot: centroid, history dots, and a data block with height and offset
  information [D] S5 ¶23–25; [D] S13 (centroid and history); [D-sum] S13 (offsets in feet, velocity).
- The radar must also let the controller appreciate ground speed and the rate of departure from or approach to the path
  [D] S2 §3.2.3.4.
- PAR measures position only. It does not measure heading or wind [Y]. This is why the controller works from position
  trend and from the last assigned heading (section 2.4).

### 1.2 Scan pattern, update rate, coverage per system

Annex 10 demands a full renewal once per second. Every modern system meets it at about 1 s. Coverage varies widely.

| System | Scan method | Update | Azimuth | Elevation | Range | Tag and source |
|---|---|---|---|---|---|---|
| ICAO minimum | not specified | ≥ 1 per s | 20° sector | 7° sector | ≥ 9 NM (16.7 km) from antenna | [D] S2 §3.2.3.1.1, §3.2.3.5 |
| Radar, Japan c.1975 | Fan beam, mechanical scan | 1 Hz (slide adds 2 scans per second) | not stated | not stated | not stated | [D] S17 slide 3 |
| GCA, US Navy 1950 | Precision radar | not stated | 20° arc | not stated | 10 mi | [D] S10 |
| PAR-2000, GCA-2000 | Solid-state T/R modules | "< 1 per second" as printed | 30° | −1° to +7° | 20 NM clear, 15 NM rain | [D] S15 |
| PAR-2020, AN/FPN-68A | AESA | period < 1 s | 30° | −1° to +7° | 20 NM clear, 15 NM rain | [D] S14 |
| AN/TPN-31 ATNAVICS PAR | Solid-state X-band | 1 s | ±15° | −1° to +6° (sign garbled in the PDF) | 15 NM | [D] S16 |
| AN/FPN-67 FBPAR | Same as ATNAVICS PAR | see ATNAVICS | ±10° [A] | −1° to +6° [A] | see ATNAVICS | [D] S16 for shared hardware; [A] https://www.radartutorial.eu/19.kartei/03.atc/karte032.en.html |
| AN/TPN-22 | Electronically steered array, 3-D pencil beam, tracks 6 aircraft | not found | not found | −1° to +7° [A] | 10 NM pencil beam [A] | [D-sum] S18; [A] https://www.radartutorial.eu/19.kartei/03.atc/karte048.en.html |
| AN/GPN-22 | Phased array, tracks 6 aircraft | not found | 20° [A] | 8° [A]; one card says 15° [A] | 20 NM [A] | [A] https://armsnet.duckdns.org/equipment/b06f7f33-979f-42dc-8bc6-08decb838d08 |
| AN/FPN-63 | Modified AN/CPN-4A antennas | about 1 s, marked unverified in S24 | 20° (S24) | 8° (S24) | 10 or 20 NM (S24) | Lead only, S24. Modified antenna and outputs: [A] search summary on AN/FPN-63; exact page not identified |
| PAR-E (CSG) | AESA in both axes | < 1 s | ±15° | −1° to +14° | 40 km | [D-sum] S19 |
| PAR-2090 | X-band | not found | ±15° [A] | 10° [A] | not found | [A] https://defencetalk.com/par-2090-precision-approach-radar-system-completes-the-validation-phase-8484 |

Other scan details:

- Japan c.1975 example: X-band 9080 ± 80 MHz, azimuth beam < 0.8° by < 3.0°, elevation beam printed as < 0.5° horizontal by
  < 4.0° vertical, gain > 40 dBi, peak power ≥ 30 kW, PRF 1833 pps [D] S17. An elevation fan should be narrow in the
  vertical, so the printed labels look swapped [Y]. "1 Hz, 2 scans per second" means one azimuth plus one elevation scan
  each second [Y].
- Annex 10 siting: complete coverage of a sector with apex 150 m beyond touchdown, ±5° about the centreline, −1° to +6°
  [D] S2 §3.2.3.2.1. Example siting: set-back 915 m with offset 120 m, or 1 200 m with offset 185 m, for a ±10° scan
  [D] S2 Note 1.
- The azimuth element is in effect a sector search radar. It can show traffic up to about 30 000 ft [D] S5 ¶20.
- Rain mode on the UK system cuts usable range by 5 NM to 15 NM. A mode change resets the processor: targets vanish for
  typically 4–5 s, up to 10 s [D] S5 ¶36. This matches PAR-2000 figures in S15, but RA 3291 does not name the model [Y].
- Two targets merge inside the resolution "bubble". They separate on the display within 2–3 s normally [D] S5 ¶21.
- A US Navy expeditionary PAR notice asked for a track update of once per second, objective five per second, and
  range accuracy ±2 % [A] https://sam.gov/opp/dc8036ee5e84479b9a5a4b51be5017dc/view

### 1.3 Accuracy by axis and how the errors combine (Annex 10)

All [D] S2 §3.2.3.3.

| Axis | Maximum permissible error | Measured from | Touchdown limits | Resolution |
|---|---|---|---|---|
| Azimuth | greater of (0.6 % R + 10 % of deviation) or 9 m (30 ft) | R = distance from **PAR antenna** | error ≤ 9 m; displayed error ≤ greater of 0.3 % R or 4.5 m | 1.2° |
| Elevation | greater of (0.4 % R + 10 % of displacement) or 6 m (20 ft) | R = distance from **PAR antenna** | error ≤ 6 m; displayed error ≤ greater of 0.2 % R or 3 m | 0.6° |
| Distance | 30 m (100 ft) **plus** 3 % of distance | distance from **touchdown** | none extra | 120 m |

How the terms combine:

- Inside one axis the terms **add**: a range term plus a deviation term. The result is then compared with a floor, and
  the greater value applies [D] S2.
- Azimuth, elevation and distance each have their own limit. Annex 10 gives no combined 3-D error [D] S2.
- Annex 10 says "maximum permissible error". It gives no percentile, no bias and noise split, and no correlation time
  [D] S2. Our "limit = 2 sigma" is therefore our assumption [Y].
- 0.6 % and 0.4 % are the same as 0.34° and 0.23° (atan) [Y]. The ATNAVICS sheet prints exactly 0.34°, 0.23° and 88 ft
  for its PAR [D] S16. Vendors seem to quote the Annex 10 limit as their accuracy [Y].
- Raytheon says the elevation accuracy of a typical PAR is about a tenth of a degree [D] S12. That is near limit / 2.3,
  so sigma ≈ limit / 2 is a fair model [Y].

The Annex 10 limit falls to its floor only in the last 0.3 NM. Calculated [Y] from S2, antenna set back 915 m, zero
deviation:

| From touchdown (NM) | From antenna (m) | Azimuth limit (m) | Elevation limit (m) | Range limit (m) |
|---:|---:|---:|---:|---:|
| 9.00 | 17 583 | 105 | 70 | 530 |
| 5.00 | 10 175 | 61 | 41 | 310 |
| 4.00 | 8 323 | 50 | 33 | 250 |
| 3.00 | 6 471 | 39 | 26 | 200 |
| 2.00 | 4 619 | 28 | 18 | 140 |
| 1.00 | 2 767 | 17 | 11 | 90 |
| 0.63 | 2 082 | 12 | 8 | 60 |
| 0.25 | 1 378 | 9 | 6 | 40 |
| 0.00 | 915 | 9 | 6 | 30 |

0.63 NM is the 200 ft point on a 3° path. The elevation limit equals 60 ft (18 m) at about 2 NM. Outside that distance
the radar limit is wider than the UK "slightly" band [Y]. This fits the ICAO rule that gives tolerance before 2 NM
(section 2.3).

### 1.4 Elevation multipath

**No PAR-specific measured multipath data was found.** What follows is what exists.

Sourced:

- UK practice: height on the data block can fluctuate strongly, mostly with larger aircraft or formations. Controllers
  must read the overall trend and not single values [D] S5 ¶25. RA 3291 does not name multipath as the cause.
- Formations and big aircraft are tracked at their centre; a split can make the position jump [D] S5 ¶31. Larger aircraft
  can show short-lived ghost tracks behind them [D] S5 ¶35.
- Accuracy near touchdown degrades. The antenna offset makes angle error dominate. A tenth-degree error becomes a large
  percentage of low height. Deviations can fall under one display pixel [D] S12.
- General low-angle tracking work says multipath is the main low-angle error, is quasi-periodic, fluctuates more at low
  angles, and falls as elevation angle rises [A] https://apps.dtic.mil/sti/pdfs/ADA023265.pdf and
  https://apps.dtic.mil/sti/tr/pdf/AD0781100.pdf
- A transportable PAR paper reduces ground reflections with a narrow elevation beam [A]
  https://ieeexplore.ieee.org/document/522600
- The standard reference is Barton, "Low-Angle Radar Tracking", Proc. IEEE 62(6), 1974 [A]. Its formula was **not read**.

My geometry [Y]. Antenna set back 915 m, 3° path, λ = 3.3 cm, antenna height 3–5 m (assumed):

- Elevation seen from the antenna: 2.7° at 5 NM, 2.4° at 2 NM, 2.0° at 1 NM, 1.7° at 200 ft height, 1.0° at 0.25 NM,
  0.5° at 0.1 NM.
- The ground image sits at minus that angle, so the separation is twice that angle. With a 0.5–0.8° beam the image stays
  out of the main beam until about 0.1–0.2 NM. Above that, the reflection enters by the sidelobes.
- Lobe spacing in angle is λ / (2 h) = 0.19–0.32°.
- At 120 kt, the angle changes about 0.002°/s at 5 NM and about 0.03°/s near 1 NM. The error therefore has a period of
  about 100–160 s at 5 NM (looks like a slow bias) and about 6–10 s near 1 NM (looks like a slow wobble).
- Both periods are longer than the 1 s plot interval, so white-noise filtering will not remove them. A 5σ gate will not
  see them either.

### 1.5 Display, cursors, safety lines, how the controller reads deviation

- Two views share a range axis: elevation against the glidepath, azimuth against the centreline [D] S12, S13.
- Cursors, UK system [D] S5:
  - Centreline, drawn 50 ft wide (Table 2).
  - 2° and 5° azimuth lines, blue, diverging from touchdown (¶24).
  - Glidepath cursor (Table 3).
  - Lower Safe Limit Line Cursor, LSLLC, set by engineers per runway from the obstacle clearance surface of the lowest
    approved glidepath angle (¶26).
  - Decision height cursor line (¶1f).
  - Range lines (¶19).
- ITT shows a line for minimum safe altitude below the glideslope [D] S13.
- FAA text names safety limits but gives no numbers [D] S3 §5-10-14, §5-13-3; S4.
- UK range scales: inside 4 NM use the 5 NM scale. The 3 NM and 1 NM scales should not be used [D] S5 ¶1a.
- Reading method: the controller reads position from the cursors and judges trend from the track history trail [D] S5
  ¶24–25.
- Trap: the target, the centreline and the glidepath are drawn at similar widths. A small deviation can look large and
  tempt over-correction. Controllers must allow for this [D] S5 ¶22.
- Patent view: the words vary between operators and with display zoom. Operator latency can make pilots over-correct or
  oscillate [D] S12.

---

## 2. What the controller computes and says

### 2.1 What is computed

A controller computes four things [Y], from [D] S3 §5-12-4, S5 ¶24–25:

1. Lateral position class relative to the course.
2. Vertical position class relative to the glidepath.
3. Trend of each, from the history trail.
4. A new heading, if needed. There is no vertical command except the word "adjust".

### 2.2 Call sequence

FAA wording below is from S3 (2017 edition). ICAO wording is paraphrased. Unit conversions are [Y].

| Point | US, S3 | ICAO, S1 | UK, S5, S7, S8 |
|---|---|---|---|
| Before the approach | Type of approach, lost-comm instruction, missed approach procedure. §5-10-2, -4, -11 | Runway, OCA/H, glide path angle, rate of descent if prescribed or asked, failure procedure. §8.9.6.1.3 | Procedure minimum, MACF, read back altimeter. S8; S7 ¶4 |
| Transfer to final controller | Comm check: HOW DO YOU HEAR ME. §5-10-9 | At least 2 km (1 NM) before glide path intercept. §8.9.7.2.2 | Handover at 7–8 miles in the figure. S7 Fig 2 |
| On final course | DO NOT ACKNOWLEDGE FURTHER TRANSMISSIONS. §5-10-10 | Pilot told no more acknowledgement is needed. §8.9.7.2.3 | Same, unless requested. S8 |
| Before descent | APPROACHING GLIDEPATH, about 10–30 s before descent. §5-12-1 | Told when approaching intercept. §8.9.7.2.5.1 | Warning normally 200 ft below the glidepath. S5 ¶25 |
| Descent point | BEGIN DESCENT. §5-12-3 | Told to begin descent and check DA/H. Rate or angle may follow. §8.9.7.2.5.1; §12.4.2.5.4 | Begin descent now for a (number) degree glidepath. S8. Normal start 5 miles. S7 Fig 2 |
| During final | About every 5 s (section 2.3). §5-12-4 | Gaps no more than 5 s. §8.9.7.2.3 | Position plus trend. S5 ¶25 |
| Distance | Once per mile at least. §5-12-5 | Each 2 km (1 NM) to 8 km (4 NM), then more often. Azimuth and elevation have priority. §8.9.7.2.6 | 1 NM from 15–18 NM, ½ NM inside 15 NM and on final. S5 ¶19 |
| Gear | Landing check is USA/USN. §5-10-6 | Reminder on final. §8.9.6.1.5 | Positive gear check before clearance. S5 ¶1d |
| Landing clearance | Issue with wind. §5-10-13 | Notify at about 8 NM, again at 4 NM; pass before 2 NM. §8.9.6.1.6–7 | Pass by 2 NM or break off. Ask at 2½ NM if late. S5 ¶1e, ¶29 |
| 2 NM | No rule | Feet or metres from here on, preferably. §8.9.7.2.5.3 | Clearance gate. S5 ¶1e |
| Decision height | DH only if asked. §5-12-2. AT DECISION HEIGHT. §5-12-6 | Check DA/H call exists. §12.4.2.5.6 | Approaching, and passing, decision height. S5 ¶1f; S8. Advice at 0.5 miles in the figure. S7 Fig 2 |
| Below DH | Same calls, advisory only. §5-12-7a | Information continues to threshold or a set distance. §8.9.7.2.7 | Direction of turn and degrees only. S5 ¶24. Glidepath calls to 50 ft below minimum if possible. ¶25 |
| Approach lights | OVER APPROACH LIGHTS. §5-12-7b | Phrase exists. §12.4.2.5.5 | none found |
| Threshold | OVER LANDING THRESHOLD, (position to course). §5-12-7c | Told if monitored past it. §8.9.7.2.7 | Over touchdown. S8 |
| End of guidance | §5-12-8: pilot asks; safe approach questionable; over threshold; or pilot reports lights in sight and says will proceed visually. | Terminated where glide path meets OCA/H. §8.9.7.2.7 | Talkdown free. S5 ¶8 |

Current FAA edition: S24 says 7110.65BB uses AT DECISION ALTITUDE at §5-12-6. A search snippet of the live FAA page still
showed AT DECISION HEIGHT [A]. This is unresolved.

### 2.3 Talk-down cadence and words

**Interval.**

- FAA: transmissions on precision final occur approximately every 5 s [D] S3 §5-12-4a. Surveillance final: about every
  15 s [D] S3 §5-11-5a. Before final: about every minute [D] S3 §5-10-2a.
- ICAO: transmission "should not be interrupted for intervals of more than five seconds" on final [D] S1 §8.9.7.2.3.
- USAF note: minimum of every 5 s [D] S11. Raytheon: about 5 s [D] S12.
- Neither rule means one fixed tick. The controller must also unkey the radio, and the timing is the controller's choice
  [D] S3 §5-12-4 Note.

**Standard words, US** [D] S3 §5-12-4:

- HEADING (heading).
- ON GLIDEPATH. ON COURSE.
- SLIGHTLY/WELL ABOVE/BELOW GLIDEPATH.
- SLIGHTLY/WELL LEFT/RIGHT OF COURSE.
- Trend examples: going above/below glidepath; going right/left of course; above/below glidepath and coming down/up;
  above/below glidepath and holding; left/right of course and holding/correcting. Modifiers: RAPIDLY, SLOWLY.

**ICAO adds** [D] S1 §12.4.2.5 (paraphrased): closing slowly or quickly from a side; heading is good; on track; distance
in metres left or right; rate of descent is good; a number of metres or feet too high or too low, with "still" for
emphasis; adjust rate of descent; coming back slowly or quickly; resume normal rate of descent; elevation element
unserviceable. ICAO also says when the aircraft starts to regain the path and just before it reaches it [D] S1 §8.9.7.2.5.1.

**UK adds** [D] S5 Table 3, ¶25; S8:

- A middle band with no adjective: above/below, left/right.
- Trend words rapidly, nicely, slowly, not correcting.
- DANGEROUSLY BELOW GP, ACKNOWLEDGE.
- RA 3291 says trend applies to the glidepath only, yet CAP 413 shows trend on the centreline too. The two UK documents
  differ [Y].

**US 1950, for comparison:** numbers in feet counted down every call, for example 75, 60, 50, 40, 30, 20, 10, on glide path
[D] S10 sample talk-down.

**What "slightly" and "well" mean.** ICAO and FAA give **no** number [D] S1, S3. The only official numbers found are UK.

| Band | UK azimuth, S5 Table 2 [D] | UK elevation, S5 Table 3 [D] | Raytheon, S12 Tables 5, 7 [D] (exemplary, both axes) |
|---|---|---|---|
| On | Return on or touching CL (CL drawn 50 ft wide) | Return on or touching GP cursor | within ±0.05° |
| Slightly | Between CL and the 2° line, touching neither | Off the cursor, within 60 ft | 0.05° to 0.15° |
| (no adjective) | Between 2° and 5° lines, or touching either | 61 ft to 100 ft | 0.15° to 0.25° |
| Well | Outside the 5° line | More than 100 ft | beyond 0.25° |
| Dangerously | none | Return touches LSLLC, or heading fast for it | none |

- UK azimuth is an **angle** from touchdown. UK elevation is a **height**. So azimuth bands shrink with range, and
  elevation bands do not.
- Raytheon says its limits can vary with airport, weather and aircraft type [D-sum] S12; its angles are from touchdown
  [D] S12.
- US naval practice is said to divide the target return into quarters. The call depends on which quarter the cursor cuts
  (S24 lead, citing NAVEDTRA 14342A Table 10-1 and 00-80T-114 ¶7.2.6.7.4; **not checked at source**). Then bands grow with
  beam size and range [Y].
- ICAO allows some tolerance before 2 NM. There the number of metres need not be given unless it stresses the rate or size
  of deviation. Inside 2 NM any deviation should be given, preferably in metres or feet [D] S1 §8.9.7.2.5.3.

Size of angular bands in metres. Calculated [Y], measured from touchdown:

| From touchdown (NM) | UK 2° line (m) | UK 5° line (m) | Patent 0.05° (m) | Patent 0.25° (m) | 0.5° below path (m) |
|---:|---:|---:|---:|---:|---:|
| 8.0 | 520 | 1 300 | 12.9 | 64.6 | 129.3 |
| 5.0 | 320 | 800 | 8.1 | 40.4 | 80.8 |
| 3.0 | 190 | 500 | 4.8 | 24.2 | 48.5 |
| 2.0 | 130 | 300 | 3.2 | 16.2 | 32.3 |
| 1.0 | 60 | 200 | 1.6 | 8.1 | 16.2 |
| 0.5 | 30 | 100 | 0.8 | 4.0 | 8.1 |

**Trend thresholds.** Raytheon, exemplary, angle rate about touchdown, same for both axes [D] S12 Tables 6, 8:

| Class | Rate (°/s) |
|---|---|
| Correcting quickly | above 0.05 |
| Correcting | 0.025 to 0.05 |
| Correcting slowly | 0.01 to 0.025 |
| Holding | −0.01 to 0.01 |
| Diverging slowly | −0.025 to −0.01 |
| Diverging | −0.05 to −0.025 |
| Diverging quickly | below −0.05 |

Raytheon pairs one position phrase with one rate phrase, for example slightly right, diverging slowly, at a set interval
such as 5 s [D] S12.

### 2.4 Heading: how it is chosen

**No source gives a formula.** ICAO and FAA say only that corrections are given as needed [D] S1 §8.9.7.2.4.1; S3 §5-12-4.

What is defined:

- Who acts: the pilot must **not** correct in azimuth unless told. The pilot **should** correct in elevation from the
  information alone [D] S1 §8.9.7.2.4.2, §8.9.7.2.5.2. So heading is a command and glide path is information.
- Basis: the controller assumes the last assigned heading is being flown and builds on it [D-sum] S20 citing AFM 51-37
  ¶6-17; [D-sum] S23.
- Method: heading changes come from the trend of the track history. The history also shows the rate of correction
  [D] S5 ¶24.
- Size against range: corrections needed decrease as range decreases. Avoid small changes at long range unless a fine
  adjustment is needed. The aim is to settle smoothly on the centreline before DH [D] S5 ¶24.
- Workload: avoid instructions that make the aircraft capture centreline and glidepath at the same moment [D] S5 ¶28.
- Over-correction warning: see 1.5 [D] S5 ¶22.

Examples of size:

- US Navy 1950 sample, one final at 100 kt: 220 at 4 mi, 210, 200 at 2½ mi, 203 at 2 mi, 200 at 1½ mi, 200 at 1 mi. Steps
  are 10°, 10°, 3°, 3° [D] S10.
- One US account: a single 2° change on a KC-130 final; smaller corrections near the runway [D-sum] S22.
- Forum, not official: typically 3–5° [D-sum] S23.
- Simulator guide: 1–2° small, 5° or more to regain the path [A]
  https://www.digitalcombatsimulator.com/en/files/3348840/

Drift correction [Y]: because radar sees no heading and no wind, the controller finds the crab angle by trial. The
heading at which the target holds parallel to the centreline is the drift-corrected heading. All sources above are
consistent with this, but none states it as a rule.

**Turn rates.**

- Standard rate 3°/s for all turns, US Navy 1950 [D] S10.
- No-gyro on final: half-standard rate (1.5°/s) [D] S3 §5-10-3c; S4 5-4-11c3.
- Other final turns: half-standard is a training rule, not an ATC rule in S1 or S3. Bank not above 30° [D-sum] S20 citing
  AFM 51-37. No more than half standard rate, about 10° bank [A]
  https://navyflightmanuals.tpub.com/P-1215/Par-Final-Approach-P-12150114-114.htm
- Bank about equal to the degrees to turn [D-sum] S21, S23.

---

## 3. Safety limits

### 3.1 Tolerance lines

| Limit | Value | Tag and source |
|---|---|---|
| US safety limits | Exist, no number in FAA text | [D] S3 §5-10-14, §5-13-3; S4 5-4-11c1, 5-4-12 |
| UK lower limit (LSLLC) | Per runway, from the obstacle clearance surface | [D] S5 ¶26 |
| US lower safe limit | Glidepath angle minus 0.5°, from runway point of intercept | Lead only, S24, citing 00-80T-114 ¶7.2.6.7.3 and AFMAN 13-204v3 ¶7.4.1.1. **Primary not read.** |
| US lateral limit | 100 ft at ½ NM, plus 200 ft per NM, to 1 200 ft at 6 NM | Lead only, S24, citing AFMAN 13-204v3 Table 7.1. **Primary not read.** This equals a constant 1.89° from touchdown [Y]. |
| Canadian-style simulator | Low warning 0.5° below path; course limit ±1.25° | Lead only, S24 (vPAR). Not official. |
| One-mile gate | At one mile, a target below and not touching the glidepath cursor counts as too low; the cursors converge | [A] https://navyaviation.tpub.com/14342A/Safety-Limits-Exceeded-349.html |
| Course limit at threshold, Navy training text | 30 ft or 0.2°, the greater; range ±2 % | [A] https://navyaviation.tpub.com/14342A/Facsfac-Air-Control-Tracking-System-Fyk-17-233.html; S24 gives the same for MCAS Cherry Point (lead) |

The tpub pages could not be opened because their TLS certificate does not match. I did not bypass this.

### 3.2 When a go-around is instructed

**ICAO** [D] S1 §8.9.6.1.8. The reason should be given in all cases.

- *Directed* when: dangerously positioned on final; traffic conflict; no clearance by 4 km (2 NM) or an agreed distance;
  aerodrome controller says so.
- *Advised to consider* when: a successful approach appears impossible; target not visible for any significant interval in
  the last 2 NM; position or identity in doubt on final.

**FAA** [D] S3 §5-10-14. Missed approach unless runway environment is in sight, or specified climb and course, when:

- (a) Safety limits are exceeded or there are radical target deviations.
- (b) Position or identity is in doubt.
- (c) Radar contact is lost or radar malfunction is suspected.
- (d) Airport conditions or traffic prevent completion.

(a), (b) and (c) **do not apply after DH**. Reasons include radar contact lost, too high/low for safe approach, too far
right/left for safe approach. AIM says the trigger is going outside the limits *and* staying outside [D] S4 5-4-11c1.

**Pilot appears to go around** [D] S1 §8.9.7.2.8:

- More than 2 NM from touchdown: pass height above the path, ask if a missed approach is intended.
- 2 NM or less: no time for a reply. Continue with emphasis on displacement to the normal end point, unless the missed
  approach is apparent.

**UK** [D] S5, S9:

- Break off if no clearance by 2 NM [D] S5 ¶1e(4).
- DANGEROUSLY BELOW GP needs a pilot acknowledgement. Its priority is above normal bands near DH [D] S5 Table 3, ¶27.
- SRA list in S9 ¶15 repeats the ICAO direct and advise split.

**Wave-off, US Navy 1950** [D] S10:

- A GCA wave-off is mandatory and is flown without hesitation.
- No conditional wave-offs were allowed. This is the opposite of modern FAA wording, which is conditional on visual
  reference [Y].
- Given at 50 ft or more above the glide path over the end of the runway, or when the aircraft does not take corrections
  properly. The reason is given to the pilot.
- Current US naval phrase is said to be tower directs waveoff (S24 lead).

**Too low, modern US naval** (S24 lead and [A] tpub page above): after final descent, target well below glidepath and
touching the lower safe limit; call TOO LOW FOR SAFE APPROACH. A radical descent gets a low altitude alert (S24 lead only).

### 3.3 Lost communications: the 5 s figure now has primary sources

There are **three different timers**. Our note mixed them.

| Timer | Value | Who | Source |
|---|---|---|---|
| Voice silence heard by pilot on PAR final | **5 s** | Pilot starts lost-comm actions | [D] S3 §5-10-4a; phrase FIVE/FIFTEEN SECONDS |
| Same, surveillance final | 15 s | Pilot | [D] S3 §5-10-4a |
| Same, vector to final | not more than 1 min | Pilot | [D] S3 §5-10-4a |
| Maximum gap in controller transmissions on final | **5 s** | Controller | [D] S1 §8.9.7.2.3 |
| Radar target lost | **more than 3 s** | Controller informs pilot and treats it as a radar fault | [D] S5 ¶5 |

- Interval in FAA text is set by the instruction issued to the pilot. S24 says published pages vary by facility, for
  example 15 s on final at Whiteman (lead only).
- FAA actions after the timer: try a secondary or tower frequency; go VFR if possible; else fly a non-radar approach or the
  specified lost-comm procedure [D] S3 §5-10-4a. **It is not an automatic go-around.**
- The FAA note says US Army and US Air Force facilities need not transmit these instructions to military aircraft
  [D] S3 §5-10-4 Note.
- Origin: 1950 Navy talk-down script says if no transmissions for five seconds, take a wave-off and pull up [D] S10.
- Navy pilots: cleared for any published approach unless told otherwise (P-553 [A]
  https://navyflightmanuals.tpub.com/P-553/Radar-Approaches-P-5530091-91.htm).
- Pilot acknowledges nothing on final, so a controller cannot detect a pilot's receiver failure by voice. The controller
  tests with a turn or other observable action [D] S5 ¶17; S10 phrase for this case. UK: an aircraft with radio failure
  is traced and other traffic moved clear [D] S7 ¶69.

At 120 kt, 5 s is 309 m of travel; at 140 kt, 360 m [Y].

### 3.4 Radar failure

- **Any radar approach cannot continue:** tell the aircraft at once. Continue by non-radar aids or visually if possible;
  else give an alternative clearance [D] S1 §8.9.6.1.4.
- **Elevation fails, ICAO:** tell the aircraft at once; change to a surveillance approach with the revised OCA/H if
  possible; else missed approach [D] S1 §8.9.7.2.5.4.
- **Elevation fails, FAA:** NO GLIDEPATH INFORMATION AVAILABLE. Take over visually or go missed. A surveillance approach
  can then be offered [D] S3 §5-12-10.
- **Elevation fails, UK:** failure of elevation alone is highly unlikely on the UK system [D] S5 ¶37.
- **Azimuth or distance lost:** system unusable; glidepath loss gives non-precision minima [A]
  https://www.faa.gov/documentLibrary/media/Notice/ND/N8260.57.pdf
- **Radar contact lost, UK** [D] S5 ¶4–7:
  - More than 3 s: inform pilot and treat as a fault.
  - Back within 3 s: resume if within 1 NM of the lost position, correlated, and matching its history.
  - Back later or further away, outside 4 NM: resume only after formal re-identification.
  - Back inside 4 NM: treat as a fault. No resume.
  - Fault early on: try a surveillance approach or resume. Before final clearance: contact tower, or missed approach.
    After final clearance: continue under the clearance, or missed approach, depending on visual contact.
- **Major alert:** does not by itself end the approach. Check system status [D] S5 ¶3, ¶33.
- **Alignment monitor:** PAR needs a continuous MTI reflector signal; loss gives a major alert and it resets itself
  [D] S5 ¶34.
- **Target jump:** temporary loss of data block or a jump to another contact is not a radar fault in itself [D] S5 ¶23.
- **Monitoring an ILS:** loss of monitoring is no reason to end a good approach [D] S3 §5-13-2 Note.

---

## 4. How a pilot flies it

**Rate of descent.**

- Pilot sets a predetermined rate at BEGIN DESCENT and adjusts power to hold speed [A]
  https://navyflightmanuals.tpub.com/P-553/Precision-Approach-Radar-Par-P-5530092-92.htm; [D-sum] S23.
- The rate depends on angle and groundspeed; charts exist on approach plates [A]
  tpub.com Navy PAR final approach text; exact page not identified (P-1204 or P-1215 family).
- ICAO allows the controller to pass an approximate rate, or the pilot to ask [D] S1 §8.9.6.1.3c.
- Exact: rate (ft/min) = 101.3 × groundspeed (kt) × tan(angle) [Y].
- Multipliers: 4.42 at 2.5°, 5.31 at 3.0°, 6.19 at 3.5° [Y].
- 3° examples: 90 kt 480, 120 kt 640, 140 kt 740, 160 kt 850 ft/min [Y].
- Rule of thumb: half groundspeed × 10, so 160 kt gives 800 ft/min [D-sum] S21, S23. This is about 6 % low at 3° [Y].
- Sample: begin descent at 500 ft/min at 100 kt on the 1950 Navy final [D] S10. Glide path angle not stated there.
- Published glidepath angles at US sites run from 2.5° to at least 3.6° (S24 lead).

**Reaction to calls.**

- Heading: turn immediately to the exact heading given, then hold it [D-sum] S20, S23.
- If drifted off heading: return to last assigned heading; do not chase the course [D-sum] S21.
- Glide path: correct on the information alone; adjust rate of descent [D] S1 §8.9.7.2.5.2; S4 5-4-11c1.
- Corrections are small: about 1° pitch or less [D-sum] S23.
- Note the double delay: the controller must see and decide, then the pilot must fly it, then the result must show
  [D-sum] S22; also S12 latency point [D].
- Small changes keep the loop stable. This is my reading of the pilot accounts [Y], from [D-sum] S22, S23.

**Typical corrections.** See 2.4: 10° at long range; 2–5° inside about 3 NM.

**Equipment and minima.**

- Only a working radio is required [D] S4 5-4-11a.
- Glideslope usually 2.5–3° [D-sum] boldmethod page, https://www.boldmethod.com/learn-to-fly/navigation/how-to-fly-par-precision-approach-radar-instrument-approach/
- Minimum HAT 200 ft civil, 100 ft military [A]
  https://www.faa.gov/documentLibrary/media/Notice/ND/n8260_64.pdf. PAR-2020 advertises 100 ft and 0.25 nmi [D] S14.
- Below DH the pilot must meet the visual rule; controller calls are advisory [D] S3 §5-12-7 Note.
- UK: civil pilots are not offered PAR unless the captain asks [D] S5 ¶38–39 under Regulation 3291(2).
- UK: all pilots go around at their own DH/DA; missed approach climb gradient at least 2.5 % assumed [D] S7 ¶9.

---

## 5. Rules map

| Rule | Status this session | Where |
|---|---|---|
| ICAO Doc 4444 §8.9.6, §8.9.7, §12.4.2.5 | **Read** [D] | S1 |
| ICAO Annex 10 Vol I §3.2 | **Read** [D]; Amendments after 91 not checked | S2 |
| FAA JO 7110.65 Ch 5 Sec 12 (and 10, 11, 13) | **Read in the 2017 X edition** [D]. Current edition: snippets only [A] | S3 |
| FAA AIM 5-4-11, 5-4-12 | **Read** [D] via mirror | S4 |
| USAF AFMAN 11-217 | **Not read.** Only a USAF facility note S11 [D], study notes, and AFM 51-37 via S20 [D-sum] | section 7 |
| NATOPS 00-80T-112, 00-80T-114 | **Not read** | section 7 |
| UK MMATM | **Read**, little PAR detail; it points to RA 3291–3295 | S7 |
| UK RA 3291 | **Read**, best numeric source found | S5 |
| UK CAP 493 | **Read**; surveillance only | S9 |
| UK CAP 413 Ch 10 | **Read** | S8 |

**Prior art that the jury may know.**

- Raytheon patent US 6,600,442: computer-generated PAR voice instructions with the same bands, trends and 5 s rate
  [D] S12. Our concept is not new in this respect [Y].
- L3Harris RAILS option: PAR measures deviation and transmits it on ILS frequencies, so a normal ILS receiver displays it
  [D] S14. This is a fielded form of radar-to-cockpit needles [Y]. We should say so in the pitch.

---

## 6. What this changes in our notes

Read-only review of `research/R_par_enri_soumu.md`, `cases/case_10_par_hybrid_cue/TECHNICAL.md`, `src/aerokit/atc/par.py`,
`src/aerokit/atc/parcue.py`. Nothing was changed. All points are [Y] unless tagged.

1. **Wrong in R_par_enri_soumu.md:** distance accuracy is 30 m **plus** 3 %, not "or" [D] S2 §3.2.3.3.3. Azimuth and
   elevation floors are "whichever is greater", not a choice.
2. **`par_measure` uses range to touchdown.** Annex 10 uses distance from the antenna. With a 915 m set-back, the
   limit at 1 NM is 11 m, not 7 m, in elevation. There is no range error in the model. Noise is white.
3. **"About 5 s" for LOST in TECHNICAL.md §3 and §6.** Now sourced, but for voice silence. For radar target loss the only
   source is 3 s, UK [D] S5 ¶5. Suggest two timers: track lost above 3 s; cue link silent above 5 s.
4. **Go-around on LOST.** Sourced as go-around if not visual [D] S3 §5-10-14c, but not after DH. ICAO only asks to advise
   in the last 2 NM [D] S1 §8.9.6.1.8b.
5. **Latch.** A returned radar inside 4 NM is treated as failed in the UK [D] S5 ¶7b, so our latch matches there. Outside
   4 NM the UK allows resume after re-identification.
6. **Voice silent on path.** Our voice is only used off path, at least 4 s apart, median 6 calls. Real PAR tells the pilot
   regularly that it is on the path [D] S1 §8.9.7.2.5.1. Silence over 5 s means lost comm to a PAR pilot. A cue needs a
   heartbeat, either on-path voice or a clear live indicator.
7. **Limits.** Our 0.7° vertical full scale is symmetric and our lateral is 2.5°. The US leads say 0.5° low and 1.89°
   lateral, unverified. Below-path and above-path limits should differ; all sources treat low as the danger.
8. **Limits off near the runway.** Our "angle limit off below 1000 m" matches the idea that (a)–(c) stop after DH [D] S3
   §5-10-14, but the rule is tied to DH, not a range.
9. **Slightly/well.** We can now cite real bands. Cue words could use the UK table.
10. **Filter.** RA 3291 says read the overall height trend, not snapshots [D] S5 ¶25. This supports our position-only law.
    Multipath periods in 1.4 are outside what the current filter and gate see.

---

## 7. What we could not read

| Document | What happened | Effect |
|---|---|---|
| Current FAA JO 7110.65 (html and PDF on faa.gov) | WebFetch: HTTP 403 on all faa.gov URLs. Browser pane loaded the page, but all reads failed with "Policy check temporarily unavailable" (more than eight tries). | Text is from 2017 X edition. Later changes unknown, including AT DECISION ALTITUDE. |
| Live FAA AIM, 8200.1D, 8260.3G, N 8260.57, N 8260.64 | 403 | No flight inspection tolerances for PAR. OCS numbers are leads only. |
| AFMAN 11-217 (e-publishing, columbus.af.mil, code7700 PDF) | 403, or browser offered a file save, or file over 10 MB. gitbooks copy: 401. | No USAF pilot text read. |
| AFMAN 13-204v3 | 403 at e-publishing. | US lateral and lower limits are leads only. |
| NAVAIR 00-80T-112, 00-80T-114 (publicintelligence) | Fetch tool failed twice. | Same. |
| NAVEDTRA 14342A, P-553, P-1204, P-1215, AV0914A (tpub.com) | TLS certificate mismatch. Not bypassed. | Snippets only. |
| DTIC reports (GCA-2000 evaluation ADA379662, JSR 74-7), DoD 00-163 test plan, MCRP 3-20F.7 | 403 | No measured PAR accuracy or multipath data. GCA-2000 scan: search summary only, 30° electronic scan at least once per second [A] https://media.defense.gov/2000/Jul/20/2001713987/-1/-1/1/00-163.pdf |
| Barton 1974; IEEE 522600 | Paywall or empty fetch. | No multipath formula. |
| ICAO Doc 9426 (rate of descent note) | Not found | Formula is my calculation. |
| Radartutorial pages | 404 to our tools | System cards are [A]. |
| Annex 10 Amendments 92 on | Fiji copy over 10 MB | Search summary suggests the −1° to +6° text remains [A]. |
| FM 3-04.303, TC 3-04.15, RA 3293–3295 | Not found or not opened | No Army or further UK text. |

Web archive routes were refused by the fetch tool. Large PDFs were not downloaded by other means.

---

## 8. Numbers to use in the algorithm

Rows marked [Y] are design choices or calculations, not rules. "Lead" means S24 only; do not state as fact.

| Item | Value | Unit | Source tag |
|---|---|---|---|
| Plot update | 1 | s | [D] S2 §3.2.3.5 |
| Coverage minimum, azimuth | 20 | ° | [D] S2 §3.2.3.1.1 |
| Coverage minimum, elevation | 7 | ° | [D] S2 §3.2.3.1.1 |
| Coverage minimum, range from antenna | 9 | NM | [D] S2 §3.2.3.1.1 |
| Antenna set-back (example) | 915 | m | [D] S2 §3.2.3.2.1 Note 1 |
| Antenna offset (example) | 120 | m | [D] S2 §3.2.3.2.1 Note 1 |
| Azimuth error limit | max(0.006·R + 0.1·\|dev\|, 9) | m, R from antenna | [D] S2 §3.2.3.3.1 |
| Elevation error limit | max(0.004·R + 0.1·\|dev\|, 6) | m, R from antenna | [D] S2 §3.2.3.3.2 |
| Range error limit | 30 + 0.03·D | m, D from touchdown | [D] S2 §3.2.3.3.3 |
| Noise 1σ | limit / 2 | m | [Y]; supported by 0.1° in [D] S12 |
| Multipath term (elevation) | sinusoid in antenna angle, spacing 0.19–0.32° | ° | [Y] section 1.4; amplitude not sourced |
| Talk-down call interval | about 5 | s | [D] S3 §5-12-4a; S12 |
| Maximum silence on final | 5 | s | [D] S1 §8.9.7.2.3 |
| Pilot lost-comm, PAR final | 5 | s | [D] S3 §5-10-4a |
| Pilot lost-comm, surveillance final | 15 | s | [D] S3 §5-10-4a |
| Pilot lost-comm, vector to final | ≤ 60 | s | [D] S3 §5-10-4a |
| Radar target lost, tell pilot | > 3 | s | [D] S5 ¶5 |
| Resume after short loss, position window | 1 | NM | [D] S5 ¶6 |
| No resume after loss, inside | 4 | NM | [D] S5 ¶7b |
| Approaching glidepath call | 10–30 | s before descent | [D] S3 §5-12-1 |
| Range call interval | 1 | NM | [D] S3 §5-12-5; S1 §8.9.7.2.6 |
| Range call, closer in | 0.5 | NM | [D] S5 ¶19 |
| Clearance gate | 2 | NM | [D] S1 §8.9.6.1.7, §8.9.6.1.8a |
| Numeric height calls start | 2 | NM | [D] S1 §8.9.7.2.5.3 |
| Pilot-missed-approach query boundary | 2 | NM | [D] S1 §8.9.7.2.8 |
| Elevation "slightly" upper | 60 | ft | [D] S5 Table 3 |
| Elevation "above/below" upper | 100 | ft | [D] S5 Table 3 |
| Azimuth "slightly" upper | 2 | ° from touchdown | [D] S5 Table 2 |
| Azimuth "left/right" upper | 5 | ° from touchdown | [D] S5 Table 2 |
| Centreline width on display | 50 | ft | [D] S5 Table 2 |
| Alternative bands, both axes | 0.05, 0.15, 0.25 | ° | [D] S12 Tables 5, 7 (exemplary) |
| Trend bands, both axes | 0.01, 0.025, 0.05 | °/s | [D] S12 Tables 6, 8 (exemplary) |
| Lower safe limit | glidepath − 0.5 | ° | Lead S24; primary not read |
| Lateral safe limit | 1.89 | ° from touchdown | Lead S24; [Y] conversion; primary not read |
| High at threshold, wave-off | 50 | ft | [D] S10, historic |
| Glidepath calls end | 50 ft below minimum | ft | [D] S5 ¶25 |
| Guidance ends | DH; advisory to threshold | — | [D] S3 §5-12-7; S4 |
| Limit rules stop | at DH | — | [D] S3 §5-10-14 |
| Rate of descent | 101.3 × GS × tan(γ) | ft/min, GS in kt | [Y] |
| Heading step, far | 10 | ° | [D] S10, one historic sample |
| Heading step, inside about 3 NM | 2–5 | ° | [D] S10; [D-sum] S22, S23 |
| Turn rate on final | 1.5 | °/s | [D] S3 §5-10-3c (no-gyro case); used generally [Y] |
| Reaction time, pilot | not sourced | s | Gap. No source found. |

**Single line for the talk:** PAR gives about one call every 5 s; a pilot who hears nothing for 5 s starts lost-comm
actions; a controller who loses the target for over 3 s tells the pilot; and only the UK publishes what "slightly" and
"well" mean.
