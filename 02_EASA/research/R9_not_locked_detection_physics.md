# R9: The physics and measurement of "not locked" on the Extra NG

- read by: subagent R9-physics
- date: 2026-11-05
- Tags:
  - **[D-ag]**: read at the source in this session. URL and page or section given.
  - **[Y]**: R9's own derivation or assumption. The working is shown, or the script output is quoted.
  - **[Y-snippet]**: seen only in a search-result snippet. The page itself was not read.
  - "(via Rx note)": taken from another project note and **not re-read** here.
- Local copies (untrusted data): `D:\tmp_ideathon\easa\dl\r9_physics\`. Text came from `pdftotext`. Images were rendered with `pdftoppm` / `pdfimages`.
- Scripts (outside the download folder): `C:\Users\ayber\AppData\Local\Temp\claude\429c22ca9402d02f\bc5cb9f5-fba6-452b-96c5-6704133e8ca0\scratchpad\r9\` (`r9_calc.py`, `r9_window.py`, `crop.py`). The output is quoted in the Appendix.
- **All tables in this note are hand-written.** The script numbers were copied in by hand.
- Table check: datawiz `tablo.denetle` was run on 2026-11-05 on the numeric columns of §3.1 (bands), §4.3 (MC inputs) and the σ-effect table. It found **0 HATA**. It gave UYARI for mixed decimals, which come from the float input (0.10 is read as 0.1); the tables print every column with one decimal count or in x.xe-yy form. It also gave UYARI for a 9-decade spread in the miss and false columns. That spread is deliberate, and those columns are already in scientific notation.

## Sources

| ID | Document | Edition | URL | Pages read |
|---|---|---|---|---|
| A1 | AAIB Bulletin report AAIB-28120, Extra NG G-MIIL | Bulletin 4/2024 | https://assets.publishing.service.gov.uk/media/65d61630188d77001103883c/Extra-NG_G-MIIL_04-24.pdf (local: `dl\aaib\G-MIIL.pdf`) | pp. 8, 9, 10 (incl. the Fig. 7 photo), 20, 24, 25, 26 |
| A2 | Extra SB-NG-2-22, Issue A | 23.12.2022 | https://extraaircraft.com/wp-content/uploads/2024/02/SB-NG-2-22A.pdf (local: `dl\reg\`) | p. 4, step 19 |
| S1 | Honeywell GAPS/HAPS aerospace proximity sensors datasheet, 000843-2-EN | 04/21 | URL in `R4_sensor_failure_rates.md` row S5 (local: `dl\hf\honeywell_gaps_haps.pdf`) | p. 3 Table 1, p. 4 Table 2, p. 5 Fig. 1 (range codes), p. 8 Figs 3–4 |
| S2 | Honeywell ZS-00417-02 hermetic aerospace proximity sensor datasheet (third-party mirror) | undated | https://hkjdwchip.com/image//files/honeywell-zs0041702-datasheets-6889.pdf | p. 1 |
| S3 | Crouzet "Electronic position detectors and proximity switches" (catalogue section, distributor copy) | undated | https://flamecorp.com/PDF/Crouzet/Electronic_Position_Detectors_and_Proximity_Switches.pdf | PDF p. 2 (printed pp. 54–55), p. 8 (pp. 64–65, DPI799153), p. 16 (DPI799339) |
| S4 | Pepperl+Fuchs NJ2-12GK-N inductive NAMUR sensor datasheet | release 2025-09-17 | https://files.pepperl-fuchs.com/webcat/navi/productInfo/pds/70133049_eng.pdf | pp. 1–2 |
| S5 | Honeywell HM Series hermetic basic switches datasheet, 003123-2-EN (mirror) | Jan 2016 | https://media.e-sonic.com/productfiles/mf-mr/mr-38hm102-54275971.pdf (local: `dl\r7_sensing\`) | pp. 5, 7, 8 |
| S6 | Honeywell HM Series catalogue pages | undated | https://www.farnell.com/datasheets/2015007.pdf (local: `dl\r7_sensing\`) | p. 1 front text; application notes 1–2 |
| S7 | Samtec blog, "Connector plating FAQs: normal force, cycles, temperature …" | read 2026-11-05 | https://blog.samtec.com/post/connector-plating-faqs-normal-force-cycles-temperature-and-other-essentials/ | whole page (WebFetch) |
| S8 | Advanced Plating Technologies, "Gold verses Tin for Use in Contact Applications" | undated | https://advancedplatingtech.com/wp-content/uploads/2013/10/Gold-vs-Tin-for-Use-In-Contact-Applications.pdf | pp. 1–2 |
| S9 | Arnold Magnetics N42H sintered NdFeB datasheet | 151021 | https://www.arnoldmagnetics.com/wp-content/uploads/2017/11/N42H-151021.pdf | p. 1 |
| S10 | Solartron SM series miniature LVDT datasheet | undated | https://solartron.cdistore.com/datasheets/solartron/Solartronsm_series2.pdf | p. 1 |
| P1 | Project `02_EASA\inputs\inputs.json`: `tolerance`, `rates`, `exposure`, `options` blocks | read 2026-11-05 | local | — |
| P2 | Project `src\aerokit\canopy\mechanism.py` (`trip_probabilities`, `trip_window`) | read 2026-11-05 | local | — |

**Tried once and not obtained:**
- Eaton aerospace proximity sensors: the search found only Eaton industrial sensors (E55, E59). No aerospace datasheet was found.
- Safran proximity sensors: not searched (time).
- Omron SS-series datasheet (gold-contact minimum load): **403**.
- AMP "Tin Commandments" report: the mikrocontroller.net copy gave **403**. The Scribd copy needs a login and was not tried.
- Delphi "What is fretting corrosion": the server returned a 114-byte HTML stub, not the PDF.
- P+F NJ2-12GK-N copy at soselectronic: **403**. The P+F original was used instead (S4).
- IEC 60947-5-2 general limits (hysteresis, repeat accuracy): standard paywalled, not read.

---

## 1. What physically differs between the states

### 1.1 Facts the derivation rests on [D-ag]

- There are three steel shoot bolts on one linkage tube, held towards "locked" by a tension spring. They engage roller lugs on the fuselage along the left cockpit edge (A1 pp. 8–9).
- Each bolt end is a ramp **15 mm long with a 5 mm rise**. With the rollers on the ramp the mechanical advantage is 3:1. The ramp compresses the weather seal (A1 p. 8).
- The bolts lock by moving **rearward**: "allowing the shoot bolt spring to ease the shoot bolts rearward to the fully locked condition" (A1 p. 25).
- Handle centre distance (A1 p. 9):
  - **70 mm** "with either the canopy open or correctly locked shut";
  - **60 mm** partially locked: with the canopy closed and the handle released, the spring stops the handle "just as it enters the green lock area".
- Full lock needs a manual pull rearwards and gives a "distinct 'clunk'" (A1 pp. 9–10).
- Partial lock: "the shoot bolt lead wedge section is only engaged with the lug roller". Full lock: "the lug roller is located on the top flat position of the shoot bolt" (A2 p. 4, step 19).
- Forces measured on another Extra NG (A1 p. 20):
  - open from full lock: 136 N;
  - partial to full: 60 N;
  - open from partial: 90 N.
- "There were no observable visual differences" at the frame-to-fuselage edge between full and partial lock (A1 p. 20).
- In partial lock, "the roller in the lug would not have travelled fully along the 'ramp'". Driving the bolts open from there needs "at least 270 newtons" (A1 p. 24).
- Positive g above 1 g compresses the seal, so the spring can ease the bolts to full lock (A1 p. 25).
- After the break-up, the spring pulled the bolts "back into an apparently locked position" (A1 p. 26).

### 1.2 What the AAIB photo shows (Fig. 7, A1 p. 10) [Y, read from the image]

The picture was extracted with `pdfimages` (1443 × 591 px) and enlarged (`crop.py`).
- In the "fully locked" panel, the dark wedge tip of the bolt sticks out past the right edge of the roller-lug bracket by about **0.8 bracket widths**.
- In the "partially locked" panel, the tip only just reaches the bracket edge (about 0–0.1 bracket widths).
- So the bolt tip moves about **0.7–0.85 bracket widths** between the two states.
- The photo has no scale and the bracket width is not published. If the bracket is 12–18 mm wide [Y], the tip moves about 8–15 mm.
- That matches a bolt-to-handle travel ratio r of about 0.8–1.5. It is a consistency check only, not a measurement.

### 1.3 Assumptions for the magnitudes [Y]

- **r** = bolt axial travel per mm of handle travel. It is not published. The sliding handle "protrudes through the canopy frame" from the linkage (A1 p. 9), which suggests a direct link, so r ≈ 1. Bracketed **0.5 / 1.0 / 1.5**.
- **d_flat** = how far the roller sits along the top flat, past the ramp top, at full lock. Not published. Bracketed 0 / 2 / 5 mm.
- **r_s** = spring stretch per mm of handle travel. Not published. Probably ≈ r.
- Ramp deficit at partial = min(15, max(0, 10·r − d_flat)) mm of ramp. The canopy then sits higher by deficit/3 (5/15 slope).

### 1.4 State × quantity table (hand-written; [D-ag] where marked, otherwise [Y])

States:
- **A** = fully locked.
- **B** = partially locked (60 mm).
- **C** = one bolt out of its lug.
- **D** = canopy closed but not seated.
- **E** = open, handles released.

| Quantity | A full | B partial | C one bolt out | D not seated | E open-released |
|---|---|---|---|---|---|
| Handle centre distance (mm) | 70 [D-ag] | 60 [D-ag] | 70 if the other two bolts reach full lock | 70 if the bolts run free past the lugs (BD-10 type, R7 note); 60–70 if a tip butts the lug | 70 [D-ag] |
| Tube stroke vs full (mm) | 0 | −10·r_h (r_h ≈ 1) | 0 | 0 or short | 0 |
| Bolt tip axial position vs full (mm) | 0 | −10·r = −5 / −10 / −15 | that bolt: tip beside, above or below its lug (loose fitting, bent bolt, frame flex) | tip displaced vertically by about the seal free height | no lug present |
| Roller on the bolt | top flat [D-ag A2] | on the lead wedge [D-ag A2], 0–15 mm of ramp left | none on that bolt | none, or the wedge tip | none |
| Seal compression deficit (mm) | 0 (design) | deficit/3 = 0–5; central 1.7–3.3 (r = 1, d_flat 5…0) | local, grows near that bolt under uplift | about the free seal height (several mm) | fully open |
| Frame-to-rim gap seen on the ground | reference | no visible difference [D-ag A1 p. 20] | probably not visible | visible if the gap is large | open |
| Spring length vs full (mm) | 0 | +10·r_s (longer, more tension) | 0 | 0 | 0 |
| Load path for canopy uplift | roller on the flat: force normal to the bolt axis, **no back-drive** | roller on a 1:3 slope: axial force ≈ 0.23–0.33 × uplift drives the bolt **open**, held only by spring + friction | two bolts carry the left-side load (about +50 % each), frame bends between them | no positive retention | none |

### 1.5 Which quantity tells partial from full, and by how much [Y]

Ranked by the size of the difference:

1. **Bolt-tip axial position at the lug: 10·r = 5–15 mm (central 10 mm).** It is local to each bolt, so it also sees C and D.
2. **Handle / tube stroke: 10 mm at the handle** [D-ag]. It is the same for all bolts, so it is blind to C. It reads 70 mm in E as well.
3. **Spring length: 10·r_s mm.** It is hard to reach and gives the same information as 2.
4. **Seal compression / frame gap: 0–5 mm (central 1.7–3.3 mm).** It is only fully present when the canopy is pulled upward. On the ground, the canopy weight may hold the frame down, so the AAIB saw no difference (A1 p. 20).
5. **Force or strain** carries no clean position information. A jammed bolt can carry load without being engaged (R7 note).

**The margin that matters is smaller than 10 mm.**
- The project trip point is 68 mm handle-equivalent, against 70 mm at full lock (P1 `tolerance.trip_mm`).
- The real margin to full lock is therefore **2 mm of handle = 2·r mm of bolt = 1–3 mm**.
- The "hazard" boundary (P1 `hazard_below_mm` 67) is 1 mm below the trip point.
- Every sensor below is judged against this 1–3 mm, not against 10 mm.

### 1.6 Why partial lock is mechanically hazardous: a size check [Y]

- On a 1:3 ramp with a rolling contact, axial back-drive = uplift × (tan α − μ)/(1 + μ tan α):
  - 0.333 × uplift at μ = 0;
  - 0.226 × uplift at μ = 0.1 (script §2).
- At full lock the roller is on the flat, so no axial component exists (A2 geometry).
- Order of magnitude of the canopy uplift at 184 KIAS (A1 p. 5 speed, via R0 note): q = 5 488 Pa.
  - The canopy area (0.8–1.2 m²) and mean suction Cp (−0.2 to −0.5) are **assumed, not sourced**.
  - Half the load is assumed to go to the bolt side.
  - Result: **146–549 N uplift per bolt** and **49–183 N axial back-drive per bolt** (script §2).
- The AAIB's 270 N threshold (A1 p. 24) lies **inside** this range.
- This does not overturn the AAIB analysis, because the Cp and area are guesses. It does show that "≥ 270 N needed" is not a large margin at high speed. It is consistent with the BFU view and with the PKBWL "suction + vibration" cause (R0/R1 notes).

---

## 2. Sensing points × sensor types

### 2.1 Sensor data read this session [D-ag]

**Inductive, aerospace (Honeywell GAPS, S1):**
- Sensing distance 3.5 mm max; head Ø13.5 mm; < 60 g inline; −55 to 115 °C; response 5 ms (p. 3 Table 1).
- Calibrated on a 17-4PH target, 25 × 18 × 3 mm (p. 3).
- Icing DO-160G §24 Cat A; vibration §8 Cat R (p. 4 Table 2).
- **Range codes Ga/Gd** (guaranteed actuate / guaranteed de-actuate, p. 5 Fig. 1): 1.75/2.75, 2.00/3.00, 2.25/3.25, 2.50/3.50 mm. **Every code has a 1.00 mm grey band.**
- Slide-by curves (p. 8 Fig. 3), read from the graph [Y]:
  - At 1 mm head-on gap, guaranteed actuation is at about −2.4 mm slide-by and guaranteed de-actuation at about −3.6 mm, so the guaranteed band is ≈ 1.2 mm.
  - The typical curves are about 0.3 mm apart (typical hysteresis).
- **Keep-out zone: Ø40.64 mm, 20.32 mm in front of the flange** (p. 8 Fig. 4).

**Inductive, aerospace (Honeywell ZS-00417-02, S2 p. 1):**
- Guaranteed actuation 1.70 mm, guaranteed de-actuation 2.80 mm (band 1.10 mm).
- Measured with a 12 × 12 × 1 mm steel target (1.0110, ST 37). Weight < 60 g.

**Inductive, aerospace (Crouzet, S3):**
- Hysteresis is "realised intentionally on the electronic board" to prevent random switching "when target is on the detection curve and submitted to vibrations". The **grey zone** between the guaranteed curves covers part tolerance and "temperature drift" (PDF p. 2).
- Keep-off zone: no metal between target and face; > 25 mm free on the sides; > 15 mm behind the face; a 25 mm radius half-circle in front (PDF p. 2).
- Landing-gear switch DPI799153 (PDF p. 8): target approaching actuates at min 0.12 in (3.05 mm); receding at max 0.16 in (4.06 mm); hysteresis max 0.015 in (0.38 mm); −55 to +95 °C.
- DPI799339 (PDF p. 16): "Hysteresis: < 0.015 in (0.381 mm)".

**Inductive, industrial NAMUR reference (P+F NJ2-12GK-N, S4 pp. 1–2):**
- Rated distance sn 2 mm; assured distance sa 0 … 1.62 mm (= 0.81·sn [Y arithmetic]).
- Steel 304 reduction factor 0.85; Al 0.4; Cu 0.3.
- Current: target not detected ≥ 3 mA, detected ≤ 1 mA. 8.2 V via about 1 kΩ.
- −25 to 100 °C; MTTFd 5 887 a; DC 0 %.
- **No hysteresis, repeatability or temperature-drift figure on the datasheet.**

**Snap-action (Honeywell 9HM1 = MS27216-6, bifurcated gold, S5 p. 7):**
- Operating force max 198 g (≈ 1.9 N); release force min 28 g.
- Pretravel max 0.76 mm; overtravel min 0.08 mm; differential travel max 0.15 mm; operating position 8.38 mm.
- With the JS-254 leaf lever (p. 8): operating force 255 g; pretravel 3.56 mm; overtravel ≥ 0.76 mm; differential travel 0.76 mm.
- Vibration 15 g, 10–2000 Hz (p. 5).
- S6: silver cadmium oxide contacts are "not recommended" for non-arcing loads "less than 12 volts and/or 0.5 amp"; use the 9/10/19/20HM series. For "sub-freezing temperatures" contact Honeywell (front text).

**Magnet for a Hall sensor (Arnold N42H, S9 p. 1):**
- Reversible temperature coefficient of Br **−0.12 %/°C** (measured 20–120 °C).

**LVDT (Solartron SM, S10 p. 1):**
- Ranges ±1 mm and ±3 mm; linearity 0.25 % FRO; "infinite resolution and repeatability"; for wet or oily environments.
- These ranges are too short for a 10–15 mm stroke. A longer-stroke part was not sourced.

### 2.2 Option table (hand-written)

Δ = what the option has to resolve. The full/partial difference is 5–15 mm of bolt; the real trip margin is 1–3 mm (§1.5).

| Option, sensing point | Measures | Switching band / resolution | Temperature, vibration, contamination, ice | Misses | Installation on the Extra NG |
|---|---|---|---|---|---|
| 1. Inductive per bolt, fuselage wall beside each roller lug, facing where the tip arrives at full lock | tip presence at the lug | grey band 1.0–1.2 mm guaranteed (S1, S2); hysteresis ≤ 0.38 mm (S3) | Non-contact; hermetic; icing Cat A (S1). Grease, water and ice films are not metal, so they barely matter [Y]. Steel debris or a nearby steel part shifts the trip [Y]. | Nothing among A–E if mounted per bolt. A tip offset vertically less than about 1 mm (D) may still read NEAR [Y] | Wires stay in the fuselage, with **no harness across the hinge**. The steel roller lug is inside the 40.64 mm keep-out (S1 Fig. 4), so the trip must be calibrated **on the aircraft**. The bolt tip is smaller than the 25 × 18 mm test target, so the range is shorter [Y]. 3 × < 60 g |
| 2. Snap-action at the receiver (9HM1 + lever), tip presses it at full lock | tip passed one point | differential travel ≤ 0.15 mm (plunger) / 0.76 mm (lever); overtravel ≥ 0.08 / 0.76 mm (S5) | Ice or debris holding the plunger down gives a false LOCKED [Y]; sub-freezing limit (S6). Force 1.9–2.5 N sits in the bolt path | Same coverage as 1 | Same place as 1. Needs a rigid bracket. Bolt overtravel past the flat must not crush the switch, so use the lever |
| 3. Hall + magnet per bolt | field from a magnet in the bolt tip | Br −0.12 %/°C (S9): about 10 % over 80 K. With a field gradient of 20–40 %/mm near a small magnet [Y], the trip moves 0.25–0.5 mm | Attracts steel swarf [Y]. Magnet loss or swap [R7] | Same as 1 | The magnet must go **into the bolt**, which sits inside the bonded frame (A1 p. 8): a bolt change. Hall datasheet data not in hand (R7 NOT VERIFIED 4) |
| 4. Bare contact per bolt (team idea) | electrical closure bolt ↔ plate at full lock | contact closes at one position. Scatter ≈ tip-position scatter (§4.3) | Grease, oxide, fretting, water and salt dominate (§3) | Same as 1 | Plate on the fuselage beyond each lug, **insulated** from the lug and the carbon structure. Resistor pair potted at the plate |
| 5. Linear pot / LVDT on the linkage tube or handle (canopy side) | analogue stroke | resolution well below 0.1 mm; linearity 0.25 % FRO (S10) | Temperature drift is small. Analogue output allows a trend and learning the full-lock position each flight [Y] | **One bolt out** (common tube). **Not seated** if the bolts run free. **Open-released reads 70 mm** (A1 p. 9) | The mechanism is enclosed before the outer skin is bonded (A1 p. 8), so it is hard to reach. The handle slot is accessible. The harness crosses the hinge (flex loop) |
| 6. Seal-gap / "seated" sensor (inductive looking at a steel tab on the frame) | frame height over the rim | as option 1 | Seal ageing and temperature change the gap [Y, no data] | **Partial lock on the ground**: 0–5 mm deficit, not visible (A1 p. 20). One bolt out | Fuselage side; easy. Best used as the **seated channel** next to a linkage sensor |
| 7. Handle microswitch in the green zone | handle at the end stop | as option 2 | as option 2 | One bolt out, not seated, **open-released** (70 mm) | Easy, but same blind spots as 5 |

Key physical point [Y]: a **fuselage-side, per-bolt sensor reads NOT LOCKED whenever the canopy is open**, because no bolt is near it. It sees E for free. A canopy-side linkage sensor cannot tell E from A without a second channel (A1 p. 9: 70 mm in both).

---

## 3. The bare-contact idea in depth

### 3.1 Circuit and states (script §3) [Y]

- Contact = bolt tip touching a plate that it reaches only at full lock. The return path is via the bolt sleeve.
- A **1 kΩ resistor in series** and a **10 kΩ resistor across the contact** are potted at the plate.
- Read with 5 V through a 3.3 kΩ pull-up. 3.3 kΩ is about the geometric mean of 1 k and 11 k, which spreads the states evenly.

| State | Loop R (Ω) | Input V | Loop current (mA) |
|---|---|---|---|
| Short (chafe upstream of the resistors) | 0 | 0.00 | 1.52 |
| Locked (contact closed) | 1 000 | 1.16 | 1.16 |
| Not locked (contact open) | 11 000 | 3.85 | 0.35 |
| Open wire | ∞ | 5.00 | 0 |

**Proposed bands [Y]:**

| Band | R (Ω) | V | Unit reads |
|---|---|---|---|
| Short | 0–500 | 0.00–0.66 | FAULT (red on the ground) |
| Locked | 500–1 600 | 0.66–1.63 | LOCKED |
| Grey | 1 600–8 000 | 1.63–3.54 | NOT LOCKED (and log "contact degraded") |
| Not locked | 8 000–14 000 | 3.54–4.05 | NOT LOCKED |
| Open | > 14 000 | 4.05–5.00 | FAULT |

- With 1 % resistors, LOCKED is 990–1 010 Ω and NOT LOCKED 10 890–11 110 Ω. With 5 %, 950–1 050 Ω and 10 450–11 550 Ω. Both sit well inside their bands.
- **Keep the LOCKED band narrow.**
  - With an upper limit of 1 600 Ω, a leak across the open contact must be **below 638 Ω** to read LOCKED.
  - If the limit were 3 300 Ω (the geometric midpoint), a 2 987 Ω leak would already read LOCKED (script §3).
- **Degradation of a closed contact is fail-safe.** Fretting, oxide or grease adds resistance. Above about 600 Ω the reading leaves LOCKED and goes to GREY, which shows as NOT LOCKED. That is a **nuisance alarm, never a false LOCKED**.

### 3.2 Contact force versus the "few newtons" limit

- Gold needs "less normal force, like 30-40 grams" (≈ 0.3–0.4 N). Tin needs "100 grams of normal force per mated contact" (≈ 1 N) (S7) [D-ag]. S8 p. 2 also gives "the minimum recommended level of 100 grams" for tin [D-ag].
- **The bolt is steel** (A1 p. 8) and probably greased [Y]. The interface is then steel/oxide/grease against the plate, not gold on gold. Gold on one side does not make the pair noble [Y].
- Two fixes:
  - a hard-gold insert on the bolt tip. This changes the bolt, which sits inside the bonded frame;
  - a gold spring finger on the plate that the bolt pushes, with ≥ 0.5 N force and a wiping stroke [Y]. That is close to a sealed switch.
- Force budget [Y]:
  - The spring alone already stops 10 mm short of full lock; the pilot must add 60 N (A1 p. 20).
  - A 0.5–2 N contact load is small against 60 N, but it acts at the very end of travel.
  - The finger must close **after** the "clunk" detent and must have its own compliance (≥ 1 mm). Otherwise it can hold the bolt short of the flat and **create** a partial lock.

### 3.3 Wetting current and contact material

- Honeywell does not recommend silver cadmium oxide for loads < 12 V / 0.5 A and points to its gold series for such non-arcing loads (S6, notes 1–2) [D-ag].
- The circuit above gives **1.16 mA** when locked (script §3).
  - Gold-contact snap switches are rated down to about 1 mA at 5 V DC (Omron SS-01) [Y-snippet; datasheet 403].
  - Silver-type contacts need 50–160 mA [Y-snippet, EAO / Omron SS-10].
- So 1.16 mA works only with gold on **both** sides.
- A steel bolt would need a periodic higher "wetting" pulse, for example 10–20 mA for a few ms [Y]. A pulse cannot clean grease.

### 3.4 Fretting under ±10 g aerobatic vibration

- Fretting comes from relative motion of 10–200 µm, from vibration or from differential thermal expansion (S8 p. 1) [D-ag].
- In one test, clean tin contacts went from 1 mΩ to > 1 Ω "in less than 20 minutes" at 10 cycles/min. Lubricated tin and gold "showed no change" (S8 p. 1) [D-ag].
- Mechanical stability helps: high force, large area, or two separate contact points (S8 p. 1) [D-ag].
- The Extra NG is certified to −10 g / +10 g (A1 p. 7, via R0 note). The SP-HMM slider handle had a wear groove from vibration (PKBWL, via R0 note).
- The bolt tip moves relative to a fuselage plate by far more than 10 µm (canopy flex, seal compliance) [Y]. The contact is **certainly in the fretting regime**.
- Gold resists the oxide, but thin gold wears through to the nickel underplate [Y]. Use hard gold ≥ 30 µin ("the standard for reliability", S7) and a contact lubricant.
- Expected effect [Y]: intermittent openings of 1–10 ms under vibration and slowly rising resistance. Both are fail-safe (§3.1) but drive **nuisance alarms**. The unit needs a debounce or latch, for example NOT LOCKED only if it persists for ≥ 0.5 s in flight. It must also never mask a steady opening.

### 3.5 Insulation and sneak paths through the structure

- **The bolt always touches the steel roller**: on the wedge in partial lock and on the flat in full lock (A2). The roller lug is screwed to the fuselage (PKBWL: two screws per fitting, via R1 note).
- Carbon-fibre laminate conducts [Y, general; not measured here].
- Sneak path: if the plate touches the structure, then plate → structure → lug → roller → bolt **closes the circuit in partial lock**. That is a **false LOCKED**.
- Rules [Y]:
  1. Mount the plate on an insulating spacer (G10/PEEK) with insulated fasteners. Check ≥ 1 MΩ to the lug at installation.
  2. Measure **differentially**, with both conductors floating from airframe ground. Do not use the switch-to-ground convention (R7 §3: a chafe to ground reads "closed").
  3. Pot the 1 k / 10 k pair **at the plate**. A chafe upstream then reads SHORT (0 Ω) and a broken wire reads OPEN. Only a bridge **downstream** of the resistors, millimetres long, can fake LOCKED.
- Residual false-LOCKED path: a conductive bridge across the open contact (or plate to lug) **below 638 Ω** (§3.1).
- Film estimate (script §3): a water film 1 mm long × 5 mm wide × 0.1 mm thick gives:
  - **rain (assumed ρ 100 Ω·m): 200 kΩ**;
  - **tap water (20 Ω·m): 40 kΩ**;
  - **seawater (0.2 Ω·m): 400 Ω**.
  - The resistivities are textbook values [Y], not read this session.
- So only salty contamination or metal debris (bolt or roller wear swarf, a dropped washer) can fake LOCKED. Rain or condensation cannot.

### 3.6 Bare contact compared with inductive (qualitative + the data in hand)

| Aspect | Bare contact (§3.1 circuit) | Inductive per bolt (GAPS / NAMUR class) |
|---|---|---|
| False LOCKED: component | Few modes. Contact welding cannot happen at mA. Only a bridge < 638 Ω or swarf | Output stuck "near": NAMUR dangerous 9.63 FIT → 1.7e-7 /h airborne (P1 `rates.stuck_active_per_h`, exida via R4) |
| False LOCKED: installation | Plate not insulated (structure sneak path); plate set too far forward | Trip set short of full lock (RV-14 type, R7); nearby steel lug shifts the trip; steel debris on the face |
| Nuisance | Grease, oxide, fretting, wear-through, ice gap between tip and plate. 217F "spring contact" connection 0.17e-6 /h × π_E AIF 6 = 1.0e-6 /h per contact (via R4 note, arithmetic here) — a lower bound for a sealed connection, not an exposed one | Electronics "safe" 15.4 FIT → 2.8e-7 /h (P1). Mechanical margin: the full-lock tip must sit > 1 mm inside the grey band |
| Detects its own wiring faults | Yes: 4 states with the resistors at the plate | Yes, if NAMUR (≤ 0.2 mA break, ≥ 7 mA short, R7) or GAPS IHM third state (S1) |
| Field data on canopies | none found | none on canopies. Landing-gear and thrust-reverser use (S3) |

---

## 4. Recommended architecture and model inputs

### 4.1 Recommendation [Y]

**Recommended: three line-monitored inductive sensors on the fuselage wall, one at each roller lug. They are set to "near" only when the bolt tip has passed the ramp top onto the flat. Add a per-flight transition self-test. Optionally keep the analogue handle channel (LOCK-SENSE Plus) for trend and self-calibration.**

Why:
1. Only a **per-bolt, fuselage-side** sensor sees all four hazards with one part type:
   - partial lock: 5–15 mm of tip travel;
   - one bolt out: that tip is missing;
   - not seated: the tips are displaced;
   - open-released: no tip is present.
2. The wiring stays in the fuselage, with no harness across the canopy hinge.
3. Non-contact sensing is not affected by grease, oxide, fretting or water films.
4. The transition self-test (each power-up the sensor must go NOT LOCKED → LOCKED) catches a stuck-"near" sensor within one flight. That cuts the latent false-LOCKED time from about 50 h to about 1 h.

What must be done first:
- **Measure r on the aircraft.** The trip margin is 2·r mm of bolt (§1.5).
- **Calibrate each trip on the aircraft** with a gauge at "roller just on the flat" and at "60 mm partial" (R7 implication 2). The lug sits in the keep-out zone, so datasheet ranges do not apply directly.

**Second choice: bare contact (option 4)**, if cost and mass dominate.
- It has the same coverage and very few false-LOCKED modes.
- It needs insulation, potted resistors at the plate, hard gold on both sides and a debounce.
- Its expected nuisance rate is about 10× the inductive one [Y].

### 4.2 Ranked trade-off table (hand-written; [Y] unless a source is cited)

| Rank | Option | Partial | One bolt out | Not seated | Open-released | Main false-LOCKED failure | Nuisance | Mass (sensors only) | Installation |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Inductive × 3 at the lugs, line-monitored, self-test (+ optional handle analogue) | yes | yes | yes (if the tip offset > about 1.5 mm) | yes | trip mis-set; steel debris; stuck "near" (1.7e-7 /h) | low | < 180 g (S1) | fuselage side; calibrate in place; keep-out conflict with the lug |
| 2 | Bare contact × 3, 1 k / 10 k at the plate, floating input | yes | yes | yes | yes | salt or swarf bridge < 638 Ω; uninsulated plate | **high** (fretting, grease, ice) | about 30 g [Y] | fuselage side; insulation and gold finger needed |
| 3 | Snap-action × 3 (9HM1 + lever) | yes | yes | yes | yes | plunger held by ice or debris; contact stuck | medium | not in datasheet | fuselage side; 1.9–2.5 N in the bolt path |
| 4 | Hall + magnet × 3 | yes | yes | yes | yes | magnet shift, swarf; trip drift 0.25–0.5 mm | low–medium | low | magnet inside the bolt: bolt change |
| 5 | Linear pot / LVDT on the tube + seat-gap sensor | yes (best resolution) | **no** | yes (seat channel) | yes (seat channel) | one bolt out is invisible | low | about 50–100 g [Y] | canopy interior (enclosed); harness across the hinge |
| 6 | Linear pot / LVDT or handle switch alone | yes | **no** | **no** | **no** (reads 70 mm) | blind to three of four hazards | low | low | as 5 |

### 4.3 Monte Carlo inputs per option [Y with basis]

**Basis for σ_trip** (script §4):
- σ is combined as a root sum of squares of three parts, all in bolt mm:
  - sensor band;
  - bolt-tip position scatter at full lock (canopy fore-aft play, frame build), assumed 0.25 mm;
  - residual rigging after on-aircraft calibration, assumed 0.15 mm.
- The sensor-band part for each option:
  - inductive: 1.0 mm grey band (S1) taken as ±3σ, so 0.17 mm;
  - snap-action: differential travel 0.15 mm (S5) taken as ±1σ, so 0.075 mm;
  - bare contact: 0.10 mm assumed;
  - Hall: 0.35 mm, from the Br drift (S9) [Y];
  - LVDT: 0.03 mm. The LVDT has no tip-position term because it sits on the tube.
- Handle-equivalent σ = σ_bolt / r. The range given is for r = 1.5 … 0.5.

**Basis for p_false_locked:**
- inductive: P1 `stuck_active_per_h` × 1 h, with the self-test, so latent time = 1 flight;
- snap-action: 30 % stuck-closed share of the 217F sensitive-switch λ 0.49e-6 × π_E 18 (via R4);
- bare contact, Hall: no data; values set by judgement [Y].
- The common mis-rig term `p_misrig_common` (1e-3, P1) stays as it is for all fuselage-side options. It is cut by `plus_misrig_factor` if the analogue channel is kept.

**Basis for p_nuisance:**
- none of the nuisance values has field data;
- the inductive value is set 3× below the P1 default of 3e-4, because the sensor is non-contact and hermetic;
- the bare-contact value is set about 10× above the inductive one, for exposed contacts.
- Treat every nuisance value as a sweep range.

| Option | σ_trip handle-eq (mm), central | σ range (mm) | p_false_locked per flight, central | p_false range | p_nuisance per flight, central | p_nuisance range | Sees partial / one bolt / unseated / open |
|---|---|---|---|---|---|---|---|
| Inductive × 3 + self-test | 0.34 | 0.22–0.67 | 1.7e-07 | 1.7e-07–8.7e-06 | 1.0e-04 | 1.0e-05–1.0e-03 | Y / Y / Y / Y |
| Bare contact × 3 | 0.31 | 0.21–0.62 | 1.0e-06 | 1.0e-07–1.0e-05 | 1.0e-03 | 1.0e-04–1.0e-02 | Y / Y / Y / Y |
| Snap-action × 3 + self-test | 0.30 | 0.20–0.60 | 2.6e-06 | 2.6e-06–1.3e-04 | 3.0e-04 | 1.0e-04–3.0e-03 | Y / Y / Y / Y |
| Hall + magnet × 3 | 0.46 | 0.30–0.91 | 1.0e-06 | 1.7e-07–1.0e-05 | 3.0e-04 | 1.0e-04–1.0e-03 | Y / Y / Y / Y |
| LVDT on tube + seat sensor | 0.10 | 0.07–0.21 | 1.7e-07 | 1.7e-07–8.7e-06 | 1.0e-04 | 1.0e-05–1.0e-03 | Y / N / Y / Y |
| LVDT or handle switch alone | 0.10 | 0.07–0.21 | 1.7e-07 | 1.7e-07–8.7e-06 | 1.0e-04 | 1.0e-05–1.0e-03 | Y / N / N / N |

- The upper ends of the p_false ranges are the "no self-test, latent 100 h" case: λ × 50 h (script §5).
- "N" means the option is blind to that hazard. In the model, set P(miss | hazard) = 1 for it.

**What σ does to the model** (P2 functions, trip 68 mm, hazard below 67 mm, σ_full = σ_trip; script §4 and `r9_window.py`):

| σ (mm) | Best trip (mm) | P(LOCKED given hazardous partial) | P(NOT LOCKED given full lock) | Trip window with both ≤ 1e-3 (mm) |
|---|---|---|---|---|
| 0.20 | 68.14 | 2.8e-11 | 2.4e-11 | 67.29–69.12 |
| 0.30 | 68.06 | 2.2e-06 | 2.4e-06 | 67.48–68.68 |
| 0.45 | 67.91 | 5.1e-04 | 5.1e-04 | 67.80–68.03 |
| 0.60 | 67.76 | 4.2e-03 | 4.1e-03 | none |
| 0.90 | 67.48 | 2.4e-02 | 2.4e-02 | none |

**Decision-relevant reading [Y]:**
- With the project's 67/70 mm hazard definition, a trip window exists only for **σ ≤ about 0.45 mm handle-equivalent**.
- Every per-bolt option meets that if r ≥ 1. **None reliably meets it if r ≈ 0.5.** That is why measuring r comes first.
- Two modelling caveats:
  1. A rigging error is **fixed per aircraft**, not random per flight. A trip set too close to 70 mm gives a nuisance alarm on **every** flight, which is found at the installation test. It does not give a 1e-3 per-flight rate.
  2. `exposure.p_hazard` has no "open-released" hazard. Fuselage-side options see it anyway; linkage-only options do not.

---

## NOT VERIFIED

1. **The bolt-to-handle ratio r, the d_flat position and the spring rate** are not published. Every bolt-mm figure scales with r. The Fig. 7 photo estimate (0.7–0.85 bracket widths) has no scale.
2. Canopy area, mean Cp and the hinge/bolt load share in §1.6 are assumptions. The uplift figures are order-of-magnitude only.
3. The slide-by values (≈ 1.2 mm guaranteed band, ≈ 0.3 mm typical hysteresis) were read off the GAPS graph (S1 Fig. 3), not from a table.
4. GAPS/ZS ranges apply to their flat steel test targets. The real bolt-tip size and alloy, and the effect of the steel roller lug inside the keep-out zone, are unknown until a bench or aircraft test.
5. IEC 60947-5-2 hysteresis and repeat-accuracy limits for industrial NAMUR sensors were not read (paywalled). The P+F datasheet gives none.
6. Wetting-current minimums (about 1 mA gold, 50–160 mA silver) are search snippets only. The Omron datasheet returned 403.
7. Water resistivities (rain 100, tap 20, sea 0.2 Ω·m) are textbook values, not read this session. Carbon-laminate conductivity was not measured.
8. Eaton and Safran aerospace proximity data: not obtained. Hall-switch operate-point drift: not obtained (only the magnet Br coefficient).
9. Every p_false_locked and p_nuisance value for the bare contact, Hall and LVDT options, and every nuisance value, is judgement without field data.
10. A long-stroke (≥ 15 mm) LVDT or potentiometer datasheet was not read. The SM series (±1/±3 mm) only shows the linearity class.
11. R0, R1, R4 and R7 facts marked "via … note" were not re-read here.

## Appendix: script output (verbatim excerpts)

```
=== 1. Geometry ===
   r d_flat bolt_dx_mm ramp_left_mm dz_seal_mm
 0.5    0.0        5.0          5.0       1.67
 0.5    5.0        5.0          0.0       0.00
 1.0    0.0       10.0         10.0       3.33
 1.0    5.0       10.0          5.0       1.67
 1.5    0.0       15.0         15.0       5.00
 1.5    5.0       15.0         10.0       3.33
=== 2. Load path ===
mu=0.00: axial back-drive = 0.333 x uplift per bolt (uplift 270 N -> 90 N axial)
mu=0.10: axial back-drive = 0.226 x uplift per bolt (uplift 270 N -> 61 N axial)
q=5488 Pa; A=0.8 m2, Cp=-0.2: uplift 878 N, per bolt 146 N, axial back-drive per bolt 49 N
q=5488 Pa; A=1.2 m2, Cp=-0.5: uplift 3293 N, per bolt 549 N, axial back-drive per bolt 183 N
=== 3. Bare contact ===
LOCKED (contact closed)      R=  1000.0 ohm  V=1.16 V  loop current=1.16 mA
NOT LOCKED (contact open)    R= 11000.0 ohm  V=3.85 V  loop current=0.35 mA
LOCKED threshold 1600 ohm: a leak across the open contact below 638 ohm reads LOCKED
LOCKED threshold 3300 ohm: a leak across the open contact below 2987 ohm reads LOCKED
closed-contact resistance + wiring above 600 ohm leaves the LOCKED band -> nuisance, never false-locked
water film ... rain, 100 ohm*m: 200,000 ohm | tap water, 20 ohm*m: 40,000 ohm | sea water, 0.2 ohm*m: 400 ohm
=== 4. Trip scatter ===
Inductive per bolt (GAPS-class)        sigma_bolt=0.34 mm ->  r=0.5: 0.67  r=1.0: 0.34  r=1.5: 0.22
Snap-action at receiver (HM + lever)   sigma_bolt=0.30 mm ->  r=0.5: 0.60  r=1.0: 0.30  r=1.5: 0.20
Bare contact per bolt                  sigma_bolt=0.31 mm ->  r=0.5: 0.62  r=1.0: 0.31  r=1.5: 0.21
Hall + magnet per bolt                 sigma_bolt=0.46 mm ->  r=0.5: 0.91  r=1.0: 0.46  r=1.5: 0.30
Linear pot / LVDT on tube              sigma_bolt=0.10 mm ->  r=0.5: 0.21  r=1.0: 0.10  r=1.5: 0.07
=== 5. Per-flight ===
NAMUR dangerous 1.73e-07/h, safe 2.77e-07/h
spring contact connection 1.02e-06/h each; two per bare-contact channel 2.04e-06/h
snap-action switch (sensitive, AIF) 8.82e-06/h
inductive: false LOCKED per flight, latent 1 flight = 1.7e-07; latent 100 h (mean 50 h) = 8.7e-06
snap-action, 30% stuck-closed: latent 1 flight = 2.6e-06; latent 100 h = 1.3e-04
```
