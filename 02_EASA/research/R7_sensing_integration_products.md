# R7: Sensing options, EFIS integration and existing products (canopy "not locked" alert, Extra NG)

- read by: subagent R7-sensing
- date read: 2026-11-05
- Tags:
  - **[D-ag]**: read at the source in this session. The URL and page or section are given.
  - **[Y]**: a secondary source, a search-result snippet, or R7's own interpretation. Each [Y] item says which.
- Local copies (untrusted data): `D:\tmp_ideathon\easa\dl\r7_sensing\`. Text was extracted with `pdftotext -layout`. Page numbers are PDF pages ("p") plus the printed page label where one exists.
- Not repeated here (already in other notes): MIL-HDBK-217F switch λ, the exida NAMUR FMEDA, the GAPS datasheet and the Schmersal reed sensor (`R4_sensor_failure_rates.md`, `R0_Honeywell_GAPS_proximity_sensor.md`). The same goes for DO-160 and wiring practice (`R4_do160_wiring.md`), FAA AD 2010-25-01 (`R0_FAA_AD_2010-25-01_DA40_door_annunciation.md`) and NTSB ERA10LA221 / SEA01LA058 (`R6_hf_full_texts.md`).

## Sources

| ID | Document | Edition / date | URL | Access |
|---|---|---|---|---|
| G1 | Garmin G3X/G3X Touch Avionics Installation Manual 190-01115-01 | Rev. AZ (revision table 04/09/25; cover "September, 2025") | https://static.garmin.com/pumac/190-01115-01_az.pdf | open. Rev. AV (the search hit) returns 404, and so do the probes for BA–BH. |
| G2 | Dynon SkyView System Installation Guide, doc. 101320-045 | Rev. AT, Oct 2024 (SW 16.7.4 / HDX 17.1) | https://dynonavionics.com/includes/guides/skyview/SkyView_System_Installation_Guide-Rev_AT.pdf | open |
| G3 | Garmin G1000/GFC 700 ICA, Diamond DA 40 / DA 40 F, 190-00492-03 | Rev. A, May 2006 | https://static.garmin.com/pumac/G1000:Diamond_G1000_GFC700InstructionsforContinuedAirworthiness_DA40_DA40F_.pdf | open |
| G4 | LXNAV LX90xx/LX80xx User Manual | Version 9, Rev #56, May 2024 | https://gliding.lxnav.com/wp-content/uploads/manuals/lx90xx-80xxUserManualEnglishVer900rev56.pdf | open |
| H1 | Honeywell MICRO SWITCH HM Series Hermetic Sealed Basic Switches datasheet, 003123-2-EN | Jan 2016 | https://media.e-sonic.com/productfiles/mf-mr/mr-38hm102-54275971.pdf (distributor mirror; same file at peerlesselectronics.com 9HM1.pdf) | open mirror. The Arrow copies reset the connection. |
| H2 | Honeywell Basic Switches catalogue pages, HM Series (older catalogue pp. 80–82) | undated (MIL-S-8805 era) | https://www.farnell.com/datasheets/2015007.pdf | open |
| H3 | Honeywell 200 FW series Hall-effect proximity sensor, product page | read 2026-11-05 | https://automation.honeywell.com/ca/en/products/sensing-solutions/sensors/motion-and-position-sensors/proximity-sensors/200-fw-series | open (the specification tab needs a sign-in; not used) |
| H4 | Honeywell 21 FW series Hall-effect proximity sensor, product page | read 2026-11-05 | https://automation.honeywell.com/gb/en/products/sensing-solutions/sensors/motion-and-position-sensors/proximity-sensors/21-fw-series | open |
| N1 | Beckhoff EL1054, 4-channel NAMUR digital input terminal, technical data | read 2026-11-05 | https://www.beckhoff.com/el1054 | open |
| N2 | Suprema BioStar 2 "Supervised Input" support article | read 2026-11-05 | https://support.supremainc.com/en/support/solutions/articles/24000026274--biostar-2-supervised-input | open |
| V1 | Van's SB 00103, Dynon Canopy Warning Software/Settings | 11 Jun 2024 | https://vansaircraft.com/wp-content/uploads/2024/07/SB-00103-Dynon-Canopy-Warning-Software.pdf | open |
| V2 | Van's SkyView Canopy Warning Read-Me (RV-14 context), 4 pp. | 01/20/17 | https://www.vansaircraft.com/wp-content/uploads/2019/02/SkyView_Canopy_Warning_Read-Me_01-20-17.pdf | open |
| V3 | Van's Notification 14-05-22, RV-12 Canopy Latch Warning, 11 pp. | 22 May 2014 | https://www.vansaircraft.com/wp-content/uploads/2019/01/Notification-14-05-22.pdf | open |
| V4 | Van's OP-61, RV-6/7/9 Tip-Up Canopy Latch Warning System | Rev. 0, 09/13/22 | https://www.vansaircraft.com/wp-content/uploads/2022/10/OP-61-RV-679-Tip-Up-Canopy-Latch-Warning.pdf | open (drawing-heavy; text partly garbled by the extraction) |
| V5 | Van's Service Letter (Incorrect Switches in RV-10 Door Warning Light Kit) + RV-10 Door Latch Indicator System instructions | 13 Feb 2008 | https://www.vansaircraft.com/wp-content/uploads/2022/03/RV-10-Door-Latch-SL-for-web.pdf | open |
| V6 | Van's Service Letter 16-11-04, Tip-Up Canopies | 2016 | https://www.vansaircraft.com/wp-content/uploads/2019/01/Tip_Up_Canopies.pdf | open |
| F1 | FAA SAFO 13003, Canopy Separation on the Aero Vodochody L-39 | 1/18/13 | https://www.faa.gov/sites/faa.gov/files/other_visit/aviation_industry/airline_operators/airline_safety/SAFO13003.pdf | open |
| F2 | FAA Airworthiness Concern Sheet, DA 40 / DA 42 In-flight Passenger Door Separations | 10/18/2024 | https://www.faasafety.gov/files/notices/2024/Oct/FAA_ACS_-_Diamond_Door_Separation.pdf | open |
| F3 | FAA NPRM, Docket FAA-2026-4633, Diamond DA 40 series passenger door (public-inspection copy, 2026-09574) | to be published 2026-05-13 | https://public-inspection.federalregister.gov/2026-09574.pdf | open |
| X1 | NTSB CEN23FA359, Van's RV-14 N6161, 12 Aug 2023, 15 pp. | final | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/192848/pdf | open |
| X2 | NTSB CHI94LA288, Bede BD-10 N2BD, 27 Aug 1994, 6 pp. | final | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/9645/pdf | open |
| X3 | NTSB CEN14LA087, Zenith 601XL(B) N581SL, 16 Dec 2013 | final | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/88556/pdf | open |
| X4 | AAIB Bulletin 4/2005, L-39C G-OALB, EW/G2004/12/04 | 2005 | https://assets.publishing.service.gov.uk/media/5422ff5740f0b6134200091d/G-OALB_4-05.pdf | open |

Tried once and not obtained: Pepperl+Fuchs NAMUR page (pepperl-fuchs.com/usa/en/46792.htm) returned **403**. Phoenix Contact MACX MCR-SL-2NAM-RO-SP returned **403**. The TSIB Singapore DA42 N181CW report (mot.gov.sg) returned **404** to both curl and WebFetch. The Cherry/ZF MP2017 reed datasheet: Mouser served HTML (a bot page) and two mirrors timed out. The Verkada supervised-wiring page returned "page not found". The Garmin GEA 71 installation manual 190-00303-40 is not on static.garmin.com (probes returned 404). It exists only as third-party copies (Scribd, ManualsLib), which were not opened.

---

## 1. Sensing principles for "bolt fully engaged"

**Brief.** The reader wants to choose a principle. The table holds the numbers that drive that choice: the switching window in mm, mass, life and the failure that gives a false LOCKED. Every number keeps the decimals its source printed.

| Principle (example part) | What it actually senses | Switching window / tolerance (mm) | Mass | Life or rate | Failure that gives a false LOCKED | Cost class [Y] | Source |
|---|---|---|---|---|---|---|---|
| Snap-action, hermetic, plunger (Honeywell HM, e.g. 9HM1 = MS27216-6, bifurcated gold) | Presence: the plunger has passed one operate point. It does not measure depth. | Pretravel max **0.76**; overtravel min **0.08**; differential travel max **0.15**; operating position 8.38 (no tolerance printed) | not in datasheet | Mechanical endurance **25,000 operations min.**; 217F λb 0.49 per 10^6 h (R4) | Operate point set short of full engagement (X1). Plunger held down by ice, debris or a bent bracket [Y]. Contact welding or stuck-closed (AC 43.13-1B in R4). Short of the N.O. wire to ground (§3). | low (MIL-qualified: medium) | H1 p.5 Table 1, p.7 listing table [D-ag] |
| Same, with a JS-254 straight-leaf lever | Presence, through a lever | Pretravel **3.56** nom; overtravel **0.76** min; differential travel **0.76** max; operating force 255 g max | not given | as above | as above, plus lever bending | low | H1 p.8 [D-ag] |
| Snap-action, environment-sealed bushing mount (Honeywell EN) | Presence | Overtravel 0.250 in standard, extendable to 0.860 in (6.35–21.8 mm); force 6–12 lb (26.7–53.4 N) | not checked | not checked | as above | medium | search snippet of the EN catalogue [Y]; datasheet not opened |
| Hall effect (Honeywell 212FW10-R, magnet target 101MG7) | Magnetic field above a threshold. A magnet is needed on the bolt. | Nominal sensing distance **2.4 to 11.4** | not on page | no figure on page; no open Hall λ (R4) | Output transistor shorted "on" [Y]. Magnet moved, demagnetised or swapped [Y]. Steel debris on the face [Y]. | medium | H3 [D-ag]; H4 says 21 FW is Hall effect with magnet targets, first specified for the JSF [D-ag] |
| Reed + magnet (Van's RV-10 kit: Cherry MP201701, magnet glued in the latch pin) | Field above the reed's pull-in level | Operate **3.81 min**, release **12.7 max** (from the AS201701 magnet) | not checked | 217F λb 0.0010 (R4); Schmersal BNS 33 B10D 25,000,000 (R4) | Contacts stick closed [Y]. **Wrong part fitted: an N.C. reed shipped instead of N.O.** (V5). Magnet depth set by hand with epoxy (V5). | low | Cherry values: search snippet only [Y]. Van's use and set-up: V5 [D-ag]. |
| Inductive proximity (Honeywell GAPS) | Metal target within range; presence | ≤ **3.5** sensing distance | < 60 g | MTBF 500,000 FH (vendor) | Shorted output; target-like metal near the face [Y]; NAMUR "dangerous" 9.63 FIT (R4) | high | R0 / R4 notes (not re-read) |
| Optical / fibre-optic | Beam blocked or reflected | no aircraft-qualified datasheet found | — | — | Dirt or ice changes the light level. One patent cites "contamination problems" of intensity-modulated sensors. | high | patents US 5042905, 10001367, 10069494 seen in search results only [Y] |
| Strain / force (load on the bolt or lug) | Preload or contact force, **not engagement** | no source | — | — | A bolt jammed against the lug side carries force without being engaged [Y] | high | none found |
| RFID / NFC / battery wireless | Tag presence within RF range | no source | — | — | Range is centimetres, so it cannot resolve millimetres; battery; RF interference [Y] | medium | none found |

Notes on Table 1:
- Table check: datawiz `tablo.denetle` was run on 2026-11-05 on all three tables and on a numeric extract of the window column. It found **0 HATA**. It gave two UYARI on the numeric extract (mixed decimals; too many digits). Both are deliberate: each value keeps its source's decimals. The script is in the R7 scratchpad and is not part of the project.
- H1 p.7 gives the HM operating position as "8,38 [0.33]" with no tolerance column. The tolerance of the operating point is **not stated**.
- The HM catalogue (H2 p.2) says to contact Honeywell for "special design variations" if the switch must "function electrically during exposure to sub-freezing temperatures" [D-ag]. Freezing is therefore a recognised limit of the standard part.
- H1 p.5: vibration "symbol 2 (15 g), 10 to 2000 Hz"; shock "type M (100 G, saw tooth)"; −65 °C to 121 °C standard; hermetic "symbol 5" to MIL-PRF-8805 [D-ag].
- H1 p.7 note: torque on the #2 mounting screws "must not exceed 0,17 Nm" (0.28 Nm with the 19PA137-HM force-spreading plate) [D-ag]. The mounting is delicate.
- H2 p.2, application note 1: silver cadmium oxide contacts are not recommended for non-arcing loads, generally "less than 12 volts and/or 0.5 amp". Use the 9, 10, 19 or 20HM series for such loads [D-ag]. An EFIS discrete input is a non-arcing load, so specify gold or bifurcated gold contacts.

## 2. EFIS discrete inputs

### 2.1 Garmin G3X Touch: GEA 24 (G1, Rev. AZ) [D-ag]
- **Pinout** (p.359 = page 23-27): connector J244 pins **40, 41, 42 and 43 = DISCRETE IN 1, 2, 3 and 4**. The organisers' "Pin 42 on the GEA 24" is therefore **DISCRETE IN 3**.
- **Thresholds** (§23.4.9, p.362 = page 23-30). When configured Active Low:
  - Active: Vin < 3.5 VDC, or Rin < 375 Ω.
  - Inactive: Vin > 8 VDC, or Rin > 100 kΩ.
  - Active High is the mirror image. The manual defines no state between 375 Ω and 100 kΩ, or between 3.5 V and 8 V.
- §23.4.9: the GP1–GP7 inputs and RPM2 can be used as extra discrete inputs. Used Active Low, GP1–GP7 "require an additional pull-up resistor" (Fig. 26-2.2). This implies the four DISCRETE IN pins have an internal pull-up.
- **Floating input** (p.707 = page 30-213): an Active Low input is inactive when the voltage is above the threshold "or if the input is floating (not connected)". Most open-or-ground switch inputs "should be configured as Active Low".
- **Built-in canopy logic** (p.708 = page 30-214), discrete input function "Canopy Closed":
  - It is "used with a switch that activates the input when the aircraft canopy is closed and locked".
  - Input not active: solid yellow **CANOPY OPEN**.
  - "If engine power is increased or the aircraft is airborne", the message flashes red and an alert tone sounds.
  - An optional "Logic Signal" (the Alert Mode setting) can replace the engine-power and airborne condition.
  - "Door Closed" is the same function with the text DOOR OPEN.
  - Other functions on the list include "User-Defined Alert" (custom text and colour; red gives an aural tone) and Master Warning / Caution Reset.
- **Garmin's wiring advice** (Fig. 26-1 note 13, p.463 = page 26-1): "it is recommended to use the grounded state as the normal switch position (e.g. canopy closed) to avoid the possibility of a latent failure such as a broken wire or microswitch". Fig. 26-2.2 (p.468 = page 26-6) shows DISCRETE IN 1 wired to a DOOR/CANOPY OPEN switch "see note 13".
- GEA 24 discrete outputs (§23.4.10): OUT 1 = master warning and OUT 2 = master caution. Both are active when a red or yellow CAS message is shown. When active, an output sinks up to 20 mA (Fig. 26-1 note 17).
- The GAD 27 has 9 discrete inputs with the same 3.5 V / 375 Ω and 8 V / 100 kΩ thresholds. On the GAD 27, a floating input reads High on inputs 1–7 and Low on inputs 8–9 (§23.1.6, p.337).

### 2.2 Dynon SkyView (G2, Rev. AT) [D-ag]
- **Contacts** section (p.221 = page 7-75; the table of contents says 7-74):
  - A contact may go on "any general purpose input pin" of the SV-EMS-220/221 D37.
  - "The EMS Software reads the voltage state of general purpose inputs." To set an input up as a contact, define two voltage ranges, 0–2 V and 2–5 V.
  - The GP inputs are **0–5 V analogue inputs**, protected to 30 V spikes.
  - "Dynon Avionics does not sell contacts or switches."
- **Canopy** (pp.233–234 = pages 7-87/7-88): the example maps C37 P9 as a contact named CANOPY.
  - "Canopy Contact is a special case input."
  - If a configuration file holds `canopy_warn_rpm_v16 = XXXX`, the audio "Check Canopy Latch" plays when RPM exceeds XXXX and the input is open.
  - The example ranges are 2.5–5.0 V = OPEN (red) and 0–2.5 V = CLOSED (green).
- The display "Contact Input #1–#4" pins are a different thing (p.103): #1 = LEVEL button, #2 = GO AROUND button, #3 and #4 are "not supported".
- Van's SB 00103 (V1 p.1) [D-ag]: from SkyView software v16.7 the RPM variable changed. After an upgrade, the canopy alert "will activate erroneously at 200 RPM". The thresholds are 1500 RPM (Lycoming) and 3700 RPM (Rotax).

### 2.3 Garmin G1000 (Extra NG's EFIS)
- The **GEA 71 installation manual (190-00303-40) is not published on static.garmin.com**: probes for revisions 00–0H returned 404. The only copies found are third-party (Scribd, ManualsLib). They were not read.
- A search snippet [Y] says the GEA 71B has "23 Discrete Inputs" and that the GEA 71 needs "FAA approved configuration data" loaded from an aircraft-specific loader card. A spare input's function is set by approved configuration data, not by the owner.
- The public DA 40 G1000 ICA (G3, Rev. A, 2006) lists GEA 71 removal and replacement and flap discrete tests, but **no door or canopy input** (grep of the full text) [D-ag].
- **No public, first-party description of spare G1000 discrete inputs for a canopy annunciation was found.** Treat G1000 integration as needing Garmin/OEM configuration data that is not available to us.

### 2.4 Gliders: LXNAV V5/V9 + LX90xx (G4) [D-ag]
- p.88: there are six programmable digital inputs (VP, SC, IN1–IN4). The selectable functions include **"Canopy locked"**, "Gear down and locked" and "Airbrakes locked".
- p.89: "Digital input shall be wired via a switch to ground". An Invert check box reverses the logic. The automatic warnings named are airbrakes open on take-off and gear not locked before landing. **No canopy warning logic is stated**; the canopy input only shows a state.

## 3. How a switch-to-ground fails silently, and how line monitoring detects it

- **The convention.** Garmin's note 13 (G1 page 26-1) [D-ag] and Van's (V2 p.1; V3 step 21; LXNAV G4 p.89) [D-ag] all wire the switch so that "closed and latched = contact to ground". A broken wire or a dead switch then reads OPEN, which is a safe alarm. Garmin states this aim.
- **The other half [Y, R7 interpretation].** With that convention, a **short from the signal wire to airframe ground** gives the same < 375 Ω the GEA 24 reads as Active, meaning "closed and locked". Chafe through the insulation onto structure is that short. So is a pinched wire under a canopy-frame clamp, or a contaminated connector. The input has only two states (§2.1), so it cannot tell "switch closed" from "wire grounded". The failure is silent until the canopy is actually unlocked. No document read here quantifies chafe-to-ground rates.
- **NAMUR (IEC 60947-5-6)**, from the Beckhoff EL1054 technical data (N1) [D-ag]:
  - Signal "0" ≤ 1.2 mA; signal "1" ≥ 2.1 mA.
  - Cable break I ≤ 200 µA; short circuit I ≥ 7.0 mA.
  - Hysteresis typ. 350 µA; open-circuit sensor supply typ. 8.2 V DC.
  - Other vendors set their own break and short thresholds. In search snippets [Y], Pepperl+Fuchs gives ≤ 0.15 mA / ≥ 6.5 mA. Phoenix Contact gives 0.05–0.35 mA for line break and 100–360 Ω for short. Both pages returned 403, so these were not read at source. **The normative fault limits of IEC 60947-5-6 itself were not read.**
- **End-of-line resistors (supervised input)**, Suprema (N2) [D-ag]:
  - Four states: ON 2.2 kΩ, OFF 4.4 kΩ, open = infinite resistance, short = 0 Ω.
  - Open reads about 3.1–3.3 V and short reads about 0–0.2 V.
  - The article shows no figure of the resistor placement. From the values, R7 infers [Y] a series resistor plus a resistor across the contact.
  - With such a pair placed **at the sensor**, a chafe to ground gives 0 Ω, which is distinct from both "locked" and "unlocked".
- **Fit to the EFIS inputs [Y]:**
  - The GEA 24 discrete cannot decode four states.
  - The SkyView GP input is an analogue 0–5 V input with up to five configurable ranges (G2 p.233–234). In principle, an EOL-resistor network can be decoded there as SHORT / LOCKED / UNLOCKED / OPEN, with SHORT and OPEN mapped to red. This is not a Dynon-documented use for canopies.
  - On the G1000, a separate alert unit must decode the line state. Any EFIS discrete it drives should be "active = fault or unlocked", so that a dead unit also alarms. This needs a design check.

## 4. Existing canopy and door warning installations

| Aircraft / product | Sensor type | Sensing points | Senses closed or locked? | Logic / gating | Source |
|---|---|---|---|---|---|
| Van's RV-12 (Notification 14-05-22) | Microswitch ES E22-50K, long arm, roller removed | 1 (latch plate) | Latch handle "fully latched": the switch is aligned so it "is only activated … when the WD-1218 Canopy Latch is fully latched" (step 20) | N.O. to ground into SkyView EMS / G3X; visual + aural above 3700 RPM | V3 steps 19–21, 27 [D-ag] |
| Van's RV-14 | Microswitch on the left canopy pin | 1 | The pin "begins to depress the micro switch's plunger when the pin is fully seated" (Van's build method, as described by the NTSB) | Visual + aural above 1500 RPM; Van's warns that in flight the switch "may become disengaged" | X1 p.8; V2 pp.1–4 [D-ag] |
| Van's RV-6/7/9 tip-up (OP-61, 2022) | 2 switches: ES E22-50K "canopy closed" + subminiature ES-SW-SS-01GL111-E "canopy latch" | 2 (canopy seated + latch handle) | Both: "continuity only when the canopy is completely closed" and "only when the C-607-1 is fully latched" | N.O. contacts to a "latch sense" wire (series wiring inferred from the drawing [Y]) | V4 [D-ag, drawing text] |
| Van's RV-10 doors (kit standard since 2015 per store page [Y]) | Reed switch + magnet epoxied in each latch pin | 4 (2 per door), in series | Pin at the latched position; the magnet depth is set by hand with a meter | Relays invert the logic; panel LED lights if either pin is not engaged | V5 pp.2–3 [D-ag] |
| Diamond DA 40 / DA 42 | Microswitch per door (AMM snippet [Y]); a shared canopy/door light (FAA AD 2010-25-01, recorded) | DA 42 NG: one per door [Y] | "Door unlocked" alert [Y] | The DA 40 MSB 40-103 (2025) inspections include the "canopy and passenger door warning light" | F3 pp.1, 4–5 [D-ag]; AMM 52-10 not read |
| Aero L-39C/ZA | Microswitches in the front and rear canopy lock mechanisms | ≥ 2 | "CANOPY LOCKED" indication | Annunciator light | F1 [D-ag] |
| Bede BD-10 (1994) | Canopy lock indicator on lock-pin extension | ≥ 1 | Pin extended, **not pin in lug** | "CANOPY OPEN" light | X2 pp.1, 3 [D-ag] |
| Zenith 601XL (homebuilt, Dynon SkyView) | Latch sensor into the PFD | 1 | Latch secured | Recorded by the PFD | X3 [D-ag] |
| Gliders with LXNAV V5/V9 | Any switch to ground | per input | "Canopy locked" input state | No canopy alert logic stated | G4 pp.88–89 [D-ag] |
| Extra NG | none on the type | — | — | — | R1 note (not re-read) |
| Extra 330, CAP, Sbach, Pitts, Cirrus, Schempp-Hirth, DG | no first-party information found | — | — | — | searches 2026-11-05 |
| STC kits | none found | — | — | — | search 2026-11-05 |

## 5. Field evidence: "indication said closed or locked, but it was not"

1. **NTSB CEN23FA359, RV-14 N6161, 2023, fatal** (X1) [D-ag].
   - p.8–9: the builder had set the microswitch "in the full aft position". In that position "the switch would signal the canopy as closed when additional canopy pin travel would be needed". The switch itself "operated within tolerances".
   - Probable cause (p.2): "improper configuration of the canopy latch micro switch, which incorrectly signaled a closed canopy before flight".
   - p.1: in flight, "the canopy open inflight annunciator began to intermittently and frequently display" before the upset.
   - **Lesson:** the sensor worked and the set-up was wrong. One switch, adjusted by hand, set the definition of "closed".
2. **Van's own caution** (V2 p.4) [D-ag]: adjusting the RV-14 switch so that it does not disengage in flight "may result in the canopy latch handle not being fully closed when the canopy switch engages". "This should be noted in any checklists." The maker accepts the trade-off between nuisance alerts and false CLOSED in writing.
3. **NTSB CHI94LA288, Bede BD-10, 1994** (X2) [D-ag].
   - The lock pins were "fully extended, extinguishing the 'CANOPY OPEN' light, but had not engaged the locking lugs". The forward pin passed "below the lock hole lug instead of through it" (pp.1, 3).
   - Probable cause: a design that gave "a 'closed and locked' indication without the canopy lock pin being engaged".
   - Fix: lengthened lugs, plus match marks.
   - **Lesson:** sensing pin *travel* is not sensing *engagement*.
4. **FAA SAFO 13003, L-39C/ZA** (F1) [D-ag]. Canopies separated or partly opened "with a CANOPY LOCKED indication". The possible causes listed:
   - "misalignment of the microswitches";
   - right-side latches not fully engaging (an obstruction or foreign object);
   - a distorted hold-open bar;
   - worn, corroded or misaligned latches.
   - The SAFO recommends a microswitch inspection every 100 h, "with the canopy both installed and removed".
5. **AAIB G-OALB, L-39C, 2004** (X4) [D-ag]. This is the reverse case.
   - The "unlocked" light stayed on. The pilot "believed that the micro switch … was incorrectly adjusted" and took off anyway, partly because the light had gone out on an earlier flight after "twisting and pushing the internal front canopy lock vigorously".
   - The rear canopy detached at about 100 ft.
   - The locking handle "can be stowed without first locking the canopy".
   - **Lesson:** a sensor history the pilot does not trust turns a true alarm into a dismissed one.
6. **Diamond DA 40 / DA 42**, aircraft fitted with door warning lights.
   - F2 [D-ag]: after ADs 2010-25-01 and 2011-10-13, the FAA received "at least 20 reports of passenger door separations … in flight and over 30 reports of aborted flights". It asks for reports of "problems with mechanical or electronic door indications".
   - F3 p.4 [D-ag]: Diamond attributed "certain instances" to the door not being properly latched, and "was unable to find a definitive root cause of the remaining occurrences".
   - Whether the warning light was lit in these events is **not stated** in F2 or F3.
7. **NTSB CEN14LA087, Zenith 601XL** (X3) [D-ag]. The PFD recorded the canopy latch "becoming unsecured about 14 seconds into" an 18-s flight. Whether the pilot was alerted before take-off is not stated. This is evidence that a latch sensor *can* log the event. It is not evidence of a false CLOSED.
8. **Wrong part from the kit supplier** (V5 p.1) [D-ag]. RV-10 kits after August 2006 "may have been supplied with incorrect normally closed" reed switches (Cherry MP201702 instead of MP201701). Builders were told to check them with an ohmmeter.

## Design implications [Y] (R7 interpretation, for the trade-off)

1. **Sense at the lug, not at the drive.** BD-10 (X2) and L-39 (F1) show that sensing pin extension or handle position misses a bolt that runs beside its receiver. On the Extra NG, each sensor should look at the bolt tip *inside* or at the roller lug. That supports one sensor per bolt over one switch on the linkage or handle.
2. **The set-up is a failure mode.** RV-14 (X1) shows a correctly working switch adjusted to the wrong point. A retrofit step must set and *verify* each sensor's switch point against a gauge at "full engagement" and at "partial engagement". Inserting a feeler or stop-block is one way to do this. The pass/fail record must be kept.
3. **The switching window must be smaller than the partial-engagement gap.**
   - HM plunger: differential travel ≤ 0.15 mm, but overtravel only ≥ 0.08 mm. A bare plunger cannot absorb bolt-position tolerance; it needs a lever (JS-254: overtravel ≥ 0.76 mm) and a rigid bracket (0.17 Nm screw limit).
   - Reed: operate ≥ 3.81 mm and release ≤ 12.7 mm. The hysteresis is too wide to resolve millimetre-scale partial engagement reliably.
   - Inductive GAPS: ≤ 3.5 mm range. Its hysteresis was not found here.
4. **The two-state ground-closed convention cannot see a chafe to ground.** Garmin chose it to catch open wires (G1 note 13). The cost is that a short reads "locked". A line-monitored sensor (NAMUR bands or EOL resistors at the sensor) turns both open and short into a distinct FAULT. The alert unit must show FAULT as "not locked" (red) on the ground.
5. **G1000 integration is not open.** No public spare-discrete description exists (§2.3). A standalone alert unit with its own annunciator and audio is the realistic path for an Extra NG retrofit. G3X / SkyView could host the logic directly: SkyView's analogue GP input could even decode EOL states.
6. **Series chains hide which point failed.** RV-10 (4 reeds in series) and OP-61 (2 switches) give one light per door or canopy. Per-bolt indication helps the pilot and the mechanic find the unlocked or failed point.
7. **Flight loads cause nuisance alarms, and nuisance alarms erode trust.** Van's warns that canopy distortion at speed can disengage the switch (V2 p.3–4). In RV-14 the annunciator flickered in flight (X1 p.1). In G-OALB the pilot dismissed a "mis-rigged" switch (X4). The Extra NG flies to ±10 g. Sensor brackets and the switch window must be checked across the flight envelope, and any filtering must not hide a real opening.
8. **Incoming inspection.** The wrong N.C. reed was supplied (V5). Bench-test every sensor's state with and without the target before installation.

## NOT VERIFIED

1. HM switch **mass** and **operating-point tolerance**: not printed in H1.
2. Honeywell EN, HE and SE series values: snippets only. The datasheets were not opened.
3. Cherry/ZF MP201701 operate 3.81 mm / release 12.7 mm: search snippet; the datasheet was not obtained.
4. Hall sensor (200 FW / 21 FW) temperature, sealing, mass and MTBF: not on the public pages. The specification tab needs a sign-in.
5. Optical, strain and RFID/wireless sensing for latch engagement: no datasheet or field use found. Table rows are R7 reasoning.
6. IEC 60947-5-6 normative fault limits: not read (standard paywalled). The P+F and Phoenix pages returned 403.
7. G1000 GEA 71 / GIA 63 spare discrete inputs: no first-party public document. Only a snippet says "23 discrete inputs".
8. Diamond DA 40 / DA 42 sensor type and count (AMM 52-10): third-party copies only; not read.
9. TSIB DA42 N181CW report (the door-closed microswitch on the front locking bolt, per snippet): 404.
10. Cirrus door sensing, Extra 330 / CAP / Sbach / Pitts canopy warnings, Schempp-Hirth / DG canopy lock warnings, glider "Air Glide" / "Butterfly" displays, and STC kits: nothing first-party found in this session.
11. GAPS hysteresis (difference between the operate and release distance): not in the R0 note. Not re-read here.
12. The OP-61 series wiring of the two switches: inferred from the drawing text, not stated in words.
