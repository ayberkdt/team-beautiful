# R7: Visual feedback for the canopy alert (annunciator numbers, placement, EFIS integration, passive indicators, products)

- Read by: subagent R7-visual
- Date read: 2026-11-05 (16:49 to about 17:10 laptop time, UTC+3)
- Tags:
  - **[D-ag]**: read at the source in this session. URL and page or section given. Pages are the printed page; the PDF page is in brackets where it differs.
  - **[Y]**: R7's own arithmetic or interpretation, or a fact taken from another R-file without re-reading it.
- Not repeated here (already in R4): CS 23.1322 colours, 25.1322 alert levels, AC 25.1322-1 aural rules, AC 23.1311-1C §22 colour rules, §18.5 visual + aural pairing.
- Local copies: `D:\tmp_ideathon\easa\dl\r7_visual\` (PDF + pdftotext `.txt`, HTML pages). Untrusted data. All parsing ran with `python -I` from scripts in the scratchpad, not from that folder.
- No paywall, login, Cloudflare page or 403 was bypassed. Each block was tried once and recorded in "NOT VERIFIED".

## Sources

| ID | Document | Edition / date | URL | sha256 (first 16) |
|---|---|---|---|---|
| V1 | FAA HF-STD-001B, Human Factors Design Standard | 30 Dec 2016 | https://hf.tc.faa.gov/publications/2016-12-human-factors-design-standard/full_text.pdf | bcbbe0276186f204 |
| V2 | MIL-STD-411F, Aircrew Station Alerting Systems (HTML transcription on emilspec, pages 10–16 and 23) | 411F | https://aircraftandairframestructuralcompone.emilspec.com/MIL-STD-411/page12.html (and page10, 11, 13, 15, 16, 23) | HTML |
| V3 | FAA AC 25.1322-1, Flightcrew Alerting, Appendix 1 and 5 | 13 Dec 2010 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_25.1322-1.pdf | d58f98b67c7584f4 |
| V4 | FAA AC 23.1311-1C, §15–17 (field of view, luminance, flashing STALL) | 17 Nov 2011 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC%2023.1311-1C.pdf | 3612b925206c7580 |
| V5 | FAA AC 25-11B, §3.2.3 Luminance | 7 Oct 2014 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_25-11B.pdf | accd6c34956243be |
| V6 | FAA Rotorcraft, "NVIS/NVG ground compatibility evaluation: daylight readability" test form, r1 | undated | https://www.faa.gov/sites/faa.gov/files/aircraft/air_cert/design_approvals/rotorcraft/ROT_NVISLightingDaylightReadability_r1.pdf | 08ab557304802de2 |
| V7 | Paananen et al., NASA TN D-5174, Compilation of data … optical pilot warning indicator system | May 1969 | https://ntrs.nasa.gov/api/citations/19690017889/downloads/19690017889.pdf | 64ae4456050a1109 |
| V8 | Walters, Wickens, Sebok & McCormick (2016), Field of View Issues on the Flight Deck, Proc. HFES 60(1), 56–60. doi:10.1177/1541931213601013 | abstract only (OpenAlex) | https://api.openalex.org/works/doi:10.1177/1541931213601013 | — |
| V9 | Nikolic, Orr & Sarter (2004), Why pilots miss the green box, IJAP 14(1). doi:10.1207/s15327108ijap1401_3 | abstract only (OpenAlex) | https://api.openalex.org/works/doi:10.1207/s15327108ijap1401_3 | — |
| G1 | Garmin G3X/G3X Touch Avionics Installation Manual 190-01115-01 | Rev. AZ, Sept 2025 | https://static.garmin.com/pumac/190-01115-01_az.pdf | 73d7d1c8748ca0f7 |
| G2 | Garmin G1000 Pilot's Guide, Cessna Nav III, 190-00498-08 | Rev. A | https://static.garmin.com/pumac/190-00498-08_0A_Web.pdf | 4c0e6bdb875f6fad |
| G3 | Dynon SkyView System Installation Guide | Rev. AT (Oct 2024) | https://dynonavionics.com/includes/guides/skyview/SkyView_System_Installation_Guide-Rev_AT.pdf | 1c764a8ce4dff975 |
| P1 | Van's, G3X Touch Canopy Warning Read-Me | 20 Jan 2017 | https://www.vansaircraft.com/wp-content/uploads/2019/02/G3X_Touch_Canopy_Warning_Read-Me_01-20-17.pdf | 502aee34cb7c2caa |
| P2 | Van's, SkyView Canopy Warning Read-Me | 20 Jan 2017 | https://www.vansaircraft.com/wp-content/uploads/2019/02/SkyView_Canopy_Warning_Read-Me_01-20-17.pdf | b141514cfbd7a8d9 |
| P3 | Van's Notification 14-05-22, RV-12 Canopy Latch Warning | 22 May 2014 | https://www.vansaircraft.com/wp-content/uploads/2019/01/Notification-14-05-22.pdf | 14fba094f29517df |
| P4 | Van's Service Bulletin 00103, Dynon canopy warning software | 11 Jun 2024 | https://vansaircraft.com/wp-content/uploads/2024/07/SB-00103-Dynon-Canopy-Warning-Software.pdf | 022cc07bbd5bba77 |
| P5 | Van's OP-61, RV-6/7/9 Tip-Up Canopy Latch Warning System | Rev. 0, 13 Sep 2022 | https://www.vansaircraft.com/wp-content/uploads/2022/10/OP-61-RV-679-Tip-Up-Canopy-Latch-Warning.pdf | ab9f2d5996d0700d |
| P6 | Van's store page, RV-6/7/9 Canopy Latch Warning Kit | read 2026-11-05 | https://store.vansaircraft.com/tip-up-canopy-latch-warning.html | HTML |
| P7 | Aircraft Spruce Europe, AN-21 Annunciator Control Unit | read 2026-11-05 | https://www.aircraftspruce.eu/an-21-annunciator-control-unit.htm | HTML |
| P8 | Streckenflug shop, SOTECC Haubenblitzer Bausatz | read 2026-11-05 | https://shop.streckenflug.at/?p=2423 | HTML |
| E1 | NTSB FTW99LA062, DA 20-A1 N527SS | final report | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/45557/pdf | 1d77bca95ae7f901 |
| E2 | NTSB MIA97LA240, DA 20-A1 N560SS | final report | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/38332/pdf | 85a5fcfbfce3e940 |
| E3 | NTSB CEN23FA359, Van's RV-14 N6161 | final report (15 pp.) | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/192848/pdf | 689dbee8222890e3 |
| E4 | NTSB LAX96LA159, VariEze N88VE | final report | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/29410/pdf | 0c3abf776751f21a |
| E5 | EASA AD 2024-0059, Schempp-Hirth Duo Discus / Nimbus-4 canopy locking | 5 Mar 2024 | https://www.daec.de/media/files/Dateien/Fachbereiche/Luftfahrttechnik/EASA_AD_2024-0059_1.pdf | 619fec548e0d8a5b |
| E6 | AAIB Safety Recommendation document, G-DDGX (Standard Cirrus) | updated 18 Dec 2025 | https://assets.publishing.service.gov.uk/media/62a32ed58fa8f50390d450dc/G-DDGX_Safety_Recommendation_Document.pdf | 9bdfa86840db7b2f |
| E7 | AAIB Special Bulletin S8/2006 (SF27 HGM and ASW 19B GDP) | Nov 2006 | https://assets.publishing.service.gov.uk/media/542304a9e5274a1317000cbb/Special_Bulletin_S8-2006_Scheibe_SF27_glider__HGM_andSchleicher_ASW_19B_glider__GDP_12-06.pdf | 36f5d4eba2a8475b |
| E8 | Scottish Gliding Centre, Topic of the month June 2026: Canopies | Jun 2026 | https://pilots.scottishglidingcentre.co.uk/lib/exe/fetch.php/safety/totm/topic_of_the_month_202606_canopies_.pdf | 8b92253ed7be2892 |
| E9 | ASK 21 Pilot Information v2 (Waikerie Gliding Club) | 2017 | https://www.waikerieglidingclub.com.au/wp-content/uploads/2017/04/ASK-21-Pilot-Information-v2.pdf | 36f6f4dfc792de70 |

## 1. Annunciator design numbers

### 1.1 Flash rate and duty cycle
1. **MIL-STD-411F §4.1.3.5** [D-ag, V2 page 11]: avoid flashing. Where it is needed for alerting, the flash rate is **3–5 Hz**, ON time about equal to OFF time. Use at most two flash rates. The second rate is **1–2 Hz**. Flashes that can be active at the same time should be synchronised.
2. **MIL-STD-411F §5.1.3.4** [D-ag, V2 page 13]: warning signals in the cockpit are **steady ON**. The one exception is the **"WHEELS" legend**, which flashes because it "must attract the aircrew's attention during a critical mission phase". §5.1.3.6 (page 13–15): WHEELS flashes when the aircraft is configured for landing and the gear is not down and locked, with a time delay to avoid nuisance flashing.
   - [Y] A canopy-not-locked alert at take-off power is the same kind of signal: a configuration warning in a critical phase. So flashing is justified for our red stage only.
3. **MIL-STD-411F §5.1.4.4** [D-ag, V2 page 16]: master caution is steady ON; all other caution signals are steady ON.
4. **HF-STD-001B §5.4.2.1.1.5** [D-ag, V1 p.204 (PDF 218)]: flashing red denotes emergency conditions that need immediate action, with "approximately equal on and off time", **3 to 5 flashes per second**. Source cited: MIL-STD-1472G.
5. **HF-STD-001B §5.4.2.1.1.6 and §5.4.2.2.1.31** [D-ag, V1 p.204, p.208]: if the flasher fails, the light must **burn steadily**, not go dark.
6. **HF-STD-001B §5.4.2.2.1.28–.30** [D-ag, V1 p.208 (PDF 222)]: minimise flashing lights. Use them only for conditions needing immediate action. Flash rate 3–5 per second, on ≈ off. Several flashing indicators in view must be synchronised.
7. **HF-STD-001B §5.6.6.11.3** [D-ag, V1 p.302 (PDF 316)]: for flash coding on screens, **2–5 Hz with at least 50 % ON**. §5.6.6.11.5: the user should be able to acknowledge, which stops the flashing. §5.6.6.11.2: only a small area should flash.
8. **AC 25.1322-1 App. 1 §1.c** [D-ag, V3 p.A1-1]: steady or flashing master visual alerts are both acceptable if they give "positive attention-getting characteristics". If flashing, all master visual alerts flash in sync.
9. **NASA TN D-5174** [D-ag, V7 printed p.75–76 (PDF 79)]: at low signal contrast, flashing signals are more conspicuous than steady ones, even when energy is removed to make the flash. Quoted from Gerathewohl (1954, J. Opt. Soc. Am. 47): "the most conspicuous signal is one flashing three times per second when it is at least twice as bright as its background". [Y: the Gerathewohl paper itself was not read.]
10. **G1000 behaviour** [D-ag, G2 p.73 (PDF 89) and p.590 (PDF 606)]: a warning shows red text in the Annunciation Window with a **continuous aural tone** and a **flashing WARNING softkey**. Annunciation flashes and the aural sounds **until acknowledged** by pressing the softkey. Cautions: yellow, single tone, flashing CAUTION softkey.

### 1.2 Luminance and contrast in high ambient light
1. **MIL-STD-411F §4.1.2.1** [D-ag, V2 page 10]: at any location, visual signals must be "fully readable and easily recognizable in a **10,000 fc** lighting environment". 10,000 fc = **107,640 lx** (conversion factor 10.764, V2 page 23).
2. **MIL-STD-411F §5.1.1** [D-ag, V2 page 12]: an energised legend must be readable at 10,000 fc with the light striking the face at 90° incidence. When not energised, the legend must **not be perceptible** in high ambient light. Average contrast ratio of a lit legend to its background **≥ 2.0** at 10,000 fc, 5,000 ± 500 K. Unlit legend to background **< 0.1**.
3. **MIL-STD-411F §5.1.3.3** [D-ag, V2 page 13]: warning-light luminance **≥ 150 fL** (= 514 cd/m², factor 3.427 from V2 page 23) at rated voltage. **At least two lamps or LEDs in parallel** per warning legend. Auto-dim to **15 ± 3 fL** (51 cd/m²) when interior lights are ON, and the design "shall preclude inadvertent dimming during daylight conditions". §5.1.5.3 (page 16): advisories ≥ 150 fL too.
4. **MIL-STD-411F §5.1.3.2** [D-ag, V2 page 13]: warning legend is **opaque letters on a translucent (lit) background** (non-NVIS). §5.1.3.1 (page 12): colour "aviation red".
5. **HF-STD-001B §5.4.2.2.1.11–.12** [D-ag, V1 p.207 (PDF 221)]: a transilluminated display is at least **10 % brighter** than its surround. Where glare must be reduced, it is **not more than 300 %** of the surround.
6. **HF-STD-001B §5.4.2.2.1.15** [D-ag, V1 p.207]: direct or reflected light must not make an indicator look lit when it is off, or off when it is lit.
7. **HF-STD-001B §5.4.2.2.1.17–.18** [D-ag, V1 p.207]: luminance contrast within an indicator ≥ **2.0**, with C = (L1 − L2)/L2. Displays designed for sunlight are exempt. At low ambient light, contrast ≥ **9.0**.
8. **HF-STD-001B §5.4.2.2.2.4–.5** [D-ag, V1 p.209–210]: an illuminated label on an opaque background is used if ambient light is high. But a **critical alerting indicator such as a master warning** uses an **opaque label on an illuminated background**. (Same rule as MIL-STD-411F §5.1.3.2.)
9. **HF-STD-001B §5.3.3.3.3–.4** [D-ag, V1 p.158 (PDF 172)], see-through displays: for legibility in direct sunlight or a background ≥ 34,000 cd/m² (10,000 fL), character luminance ≥ **5,000 cd/m²**. For most high-ambient uses, **6,900–10,300 cd/m²**.
   - [Y] The standard prints "5000 cd/m² (15,000 footlamberts)". 5,000 cd/m² is about 1,460 fL, so the bracket is a typo in the source. Use the cd/m² value.
   - [Y] This is for HUD-type see-through displays, the worst case. A panel annunciator is not see-through, but under a bubble canopy it can get direct sun, so this is an upper bound for a design target.
10. **HF-STD-001B §5.3.1.6.4** [D-ag, V1 p.148 (PDF 162)]: displays near windows must be shielded from sunlight or designed to be legible in sunlight.
11. **AC 25.1322-1 App. 1 §1.d** [D-ag, V3 p.A1-2]: master visual alerts bright enough in **all ambient light**. Manual dimming only if the minimum setting still attracts attention. §2.d (p.A1-4): visual alert information readable by both pilots in all ambient light. Automatic luminance adjustment allowed.
12. **AC 25-11B §3.2.3** [D-ag, V5 p.3-2 (PDF 15)]: readable with **direct sunlight on the display**, sunlight reflecting from white shirts, and sun in the pilot's eyes. Auto-brightness must work "including the extreme cases of a forward low sun and a quartering rearward sun shining directly on the display". It refers to SAE ARP4256A, AS8034B and AS8055 for numbers (not read, paywalled).
13. **AC 23.1311-1C §16.1–16.2** [D-ag, V4 p.36 (PDF 38)]: legible "from the night environment to direct sunlight through any window" at the luminance expected at the display's **end of life**. Provide a manual luminance control that is not affected by failure of any automatic control. Refers to AS8034 and ARP4256 (not read).
14. **FAA daylight readability ground test** [D-ag, V6 pp.1–2]:
    - Aircraft in full sun, preferably **low sun** (early morning or late afternoon). Rotate the aircraft so the sun hits the panel at different angles. A **mirror** to throw sunlight onto the panel "has been shown to be effective".
    - A "sun-gun" of 10,000 cd/m² at the instrument face "has not been shown to be as effective and is not recommended".
    - Pass criteria: warning lights distinguishable as **red, not orange or amber**; lights "bright and distinguishable enough to capture pilot's attention at all external light levels and sun angles".

### 1.3 Size and lettering
1. **MIL-STD-411F §5.1.3.2** [D-ag, V2 page 13]: warning legend character height **≥ 20 arcmin** from the aft-most design eye point.
2. **HF-STD-001B §5.6.2.5.6.5–.9** [D-ag, V1 p.259 (PDF 273)]: preferred character height **20–22 arcmin**; minimum **16 arcmin** where legibility matters; maximum **45 arcmin** for non-contextual groups of characters.
3. **AC 25.1322-1 App. 1 §1.e(2)** [D-ag, V3 p.A1-2]: alerts should subtend **at least 1°** of visual angle. §2.b(6) Note 1 (p.A1-3): minimum character height **1/200 of viewing distance**. Note 2: stroke width 10–15 % of character height; sans-serif fonts acceptable.
4. **HF-STD-001B Exhibit 5.4.2.2.3.3** [D-ag, V1 p.211 (PDF 225)]: simple indicator lights: **13 mm** or smaller steady = ordinary status; **≥ 25 mm** steady = master summation or "extreme caution"; **≥ 25 mm flashing (3–5 per s), red = emergency** (impending personnel or equipment disaster).
5. **HF-STD-001B §5.4.2.2.2.3** [D-ag, V1 p.209]: legend lights for hazards (flashing red, red, yellow) and the master summation "go" (green) and "no-go" (red) must be **discriminably larger** than other legend lights.
6. **HF-STD-001B §5.4.2.2.2.1** [D-ag, V1 p.209]: legend lights are preferred to simple indicator lights.
7. **Converted sizes for our panel** [Y; arithmetic, assuming the AC 23.1311-1C reference viewing distance of 762 mm (30 in, V4 Table 3 Note 1); the real Extra NG rear-seat eye-to-panel distance was not measured]:

Table 1. At 762 mm, the alert must be at least 13 mm high to meet the 1° rule; letters need 4–5 mm.

| Requirement | Source | Size at 762 mm (mm) | Size at 650 mm (mm) |
|---|---|---:|---:|
| Minimum character height, 16 arcmin | HF-STD-001B | 3.5 | 3.0 |
| Character height 1/200 of distance | AC 25.1322-1 | 3.8 | 3.2 |
| Warning legend character height, 20 arcmin | MIL-STD-411F | 4.4 | 3.8 |
| Preferred character height, 22 arcmin | HF-STD-001B | 4.9 | 4.2 |
| Maximum for a non-contextual group, 45 arcmin | HF-STD-001B | 10.0 | 8.5 |
| Whole alert subtends 1° | AC 25.1322-1 | 13.3 | 11.3 |

### 1.4 Logic and test
1. **HF-STD-001B §5.4.2.2.1.3** [D-ag, V1 p.205 (PDF 219)]: lights "shall indicate **equipment response** and not simply control position".
   - [Y] This is the standard's version of our rule "green must be earned": LOCKED comes from the bolt sensors, not from the handle.
2. **HF-STD-001B §5.4.2.2.1.5** [D-ag, V1 p.205]: no illumination must not be used to mean a malfunction or "no-go". It must not mean a "ready" condition **unless the bulb can easily be tested** by the operator.
3. **HF-STD-001B §5.4.2.2.1.21** [D-ag, V1 p.208]: provide lamp test. With three or fewer lamps, a press-to-test per lamp is preferred. **AC 25.1322-1 App. 1 §1.g** [D-ag, V3 p.A1-2]: provide a test of the master visual alerts.
4. **HF-STD-001B §5.4.2.1.1.8** [D-ag, V1 p.204]: a visual alarm (other than master lights) is "singular in purpose" and complete without referring to other alarms.
5. **AC 25.1322-1 App. 1 §1.b** [D-ag, V3 p.A1-1]: master visual onset at the same time as the aural and the alert text, and **at each pilot's station**. It stays on until cancelled or until the condition clears, then re-arms.
6. **AC 25.1322-1 App. 1 §2.b(2)** [D-ag, V3 p.A1-3]: message = general heading + location + nature of the condition (e.g. "HYD … FAIL").

## 2. Placement and peripheral detection

1. **AC 23.1311-1C §15.2–15.3** [D-ag, V4 p.33 (PDF 35)]: normal line of sight is **15° below the horizontal**. Primary optimum field of view = **±15°** vertical and horizontal around it (eye rotation only). Primary maximum = **±35° horizontal, +40°/−20° vertical** (eye plus minimal head rotation). "Warning or cautionary information that requires immediate pilot action or awareness, should be placed in the primary FOV."
2. **AC 23.1311-1C Table 3 and Note 4** [D-ag, V4 p.35 (PDF 37)]: system warnings and cautions within **15°** (about 8 in, 203 mm, from the pilot's centreline at 30 in). Some may be within **35°** only if paired with a **unique aural tone** or a master warning within 15°, and with a pilot evaluation.
3. **AC 25.1322-1 App. 1 §1.a, §3.a and App. 5** [D-ag, V3 p.A1-1, p.A1-4, p.A5-4]: master visual alerts and time-critical warnings in each pilot's primary field of view (same ±15° optimum / ±35° maximum definition). Note on p.A1-5 (PDF 24): the PFD is "practical and preferred" for time-critical warnings "since the pilot constantly scans the PFD".
4. **MIL-STD-411F §5.1.2** [D-ag, V2 page 12]: warning signals within the pilot's **30° total included forward cone of vision**. If they must go outside it, a **master warning must be inside** the cone. Master caution also inside.
5. **HF-STD-001B §5.4.2.2.1.8** [D-ag, V1 p.206 (PDF 220)]: indicators for critical functions within **15°** of the normal line of sight.
6. **Peripheral colour** [D-ag, V1 §5.6.6.2.3.1–.2, p.294–295 (PDF 308–309)]: colour coding is for items in the direct line of sight. In peripheral vision use blue, yellow, black or white; **red and green "should not be used for items located in peripheral vision"**. Discussion: peripheral vision is very poor at discriminating colours; only large coloured objects are distinguished.
7. **Eccentricity meta-analysis** [D-ag abstract only, V8]: 28 studies. Detection gets worse with eccentricity, more so when eye movements are prevented. **No sharp break at 15°**, but at 15° there was a **14 % miss rate** and a **21 % discrimination error rate**. Expectancy and salience have a "profound influence". (The data table and the miss rate at 30° or more were not read.)
8. **Display context** [D-ag abstract only, V9]: detection of abrupt-onset signals fell with **colour similarity** to the background, **movement of background elements**, and **greater eccentricity**. The authors use this to explain why pilots miss mode changes on glass cockpits.
   - [Y] On the take-off roll the out-of-window scene moves and the G1000 PFD is full of colour. A red message among other red/amber/green PFD elements is the "green box" case. A dedicated lamp outside the PFD avoids colour-similar clutter.
9. **NASA TN D-5174 review** [D-ag, V7 printed p.76–77 (PDF 79–80)]: Kobrick (1965) found no slower response to a 0.25 s flash anywhere in the lower half of the visual field; responses slowed only above **30° up** and beyond **55° lateral**. But with a demanding central task (Elliott & Howard; Webster & Haslerud) peripheral flashes got slower responses, and the authors say no findings are complete for a pilot doing a complex task. [Y: the primary studies were not read.]
10. **Our case, rear-seat pilot on take-off** [Y]:
    - The Extra NG is flown from the rear seat (R0 AAIB note). On the take-off roll the pilot looks out, not at the panel. The normal line of sight is then near the horizontal or to the side of the nose, not 15° down. So the PFD and any panel lamp sit **outside the ±15° optimum cone**, likely 25–40° away. Eccentricity and size of the panel from the rear seat were **not measured**.
    - At 15° the miss rate is already ~14 % (V8), and red is poorly recognised in the periphery (V1). So a panel-only red light is not enough at take-off. That matches R6/S7: an aural alone is missed ~38 % under high workload.
    - The visual must therefore be: (a) as high and central as possible (top of panel / glareshield, on the pilot's centreline); (b) large (≥ 25 mm, V1 Exhibit 5.4.2.2.3.3); (c) flashing at 3–5 Hz, which is detectable in the periphery even when the colour is not; (d) paired with an aural/voice that tells the pilot where to look (V4 Note 4).
11. **AC 23.1311-1C §17.7.c** [D-ag, V4 p.41 (PDF 43)]: for stall warning, designers "might consider … flashing a large red 'STALL' in the center of the PFD and MFD … large enough to direct the pilot's attention using **peripheral vision**".
    - [Y] Direct precedent for a large flashing "CANOPY" in the centre of the PFD as the second visual channel.

## 3. EFIS crew-alerting integration

### 3.1 Garmin G3X / G3X Touch (G1, Rev. AZ)
1. **§30.4.32.26 Discrete Inputs** [D-ag, G1 p.30-213 (PDF 707)]:
   - Discrete inputs can create an audible alert and a **CAS message on the PFD** when an external switch closes.
   - GEA 24 and GSU 73: up to **4 dedicated discrete inputs**. GAD 27: 9 more. GEA 24 GP1–GP7 and RPM2 can also be used.
   - Choose **Active Low** or **Active High** first. Active Low = active below a threshold, inactive above it **or if floating**. "Most switch-type inputs that are either open or connected to ground should be configured as Active Low."
2. **Built-in "Canopy Closed" function** [D-ag, G1 p.30-214 (PDF 708)], quoted in substance:
   - Used with a switch that activates the input when the canopy is **closed and locked**.
   - Input not active → **solid yellow "CANOPY OPEN"** message on the PFD.
   - If engine power is increased or the aircraft is airborne → the message **flashes red and an alert tone sounds**.
   - A **Logic Signal** can be chosen (Alert Mode setting) to replace "engine power and airborne state" as the trigger.
   - "Door Closed" is the same with text DOOR OPEN.
   - "User-Defined Alert": custom text and colour; **"A red alert will generate an audible warning tone."**
   - Also available: Master Warning Reset / Master Caution Reset discrete inputs (acknowledge).
   - [Y] This is exactly the organisers' worked example (amber/yellow on the ground, red flashing + tone at power). It confirms the logic exists in a certified-family EFIS. But the fixed text is "CANOPY OPEN", which is wrong for a closed-but-partially-locked canopy. Use a User-Defined Alert with the text "CANOPY UNLOCKED" if the text matters.
3. **Wiring note 13** [D-ag, G1 Figure 26-1, p.26-1 (PDF 463)]: "When using a discrete input for … canopy closure, it is recommended to use the **grounded state as the normal switch position** (e.g. canopy closed) to avoid the possibility of a latent failure such as a broken wire or microswitch."
   - [Y] Garmin's rule protects against an open-circuit fault. It does **not** protect against a **short to ground**, which would give a silent false "closed". Our per-bolt sensors with plausibility checks cover that case.
4. **GEA 24 discrete thresholds** [D-ag, G1 §23.4.9, p.23-30 (PDF 362)]: Active Low input is **active below 3.5 VDC or below 375 Ω** to ground; **inactive above 8 VDC or above 100 kΩ**. GP inputs used as active-low discretes need an extra pull-up resistor (Figure 26-2.2).
5. **Recorded data** [D-ag, E3 p.12 (PDF 12)]: in the RV-14 accident, Garmin extracted the G3X log and found canopy-open warnings recorded **while airborne** on flights 28, 39 and 40.
   - [Y] An EFIS discrete gives a free flight-data record of the lock state, as we planned for the G1000 (R-12).

### 3.2 Garmin G1000 (G2, Cessna Nav III guide)
1. [D-ag, G2 p.590 (PDF 606)]: the alerts listed are "configured specifically for the Cessna Nav III aircraft". Alert levels: WARNING (red, continuous tone, flashing softkey until acknowledged), CAUTION (yellow, single tone), MESSAGE ADVISORY.
2. [D-ag, G2 p.73 (PDF 89)]: the Annunciation Window is **to the right of the vertical speed indicator** on the PFD. Warnings red, cautions yellow, advisories white, **safe operating annunciations green**.
3. [Y] So a G1000 CAS "CANOPY" message would be an **airframe-specific configuration made by the OEM (Extra)**, not by a field installer. The G1000 installation/configuration documents for discrete inputs (GEA 71 / GIA) are not public; not found. This supports our "standalone unit + optional G1000 discrete" plan.

### 3.3 Dynon SkyView (G3, Rev. AT)
1. [D-ag, G3 p.7-75 (PDF 221)]: general-purpose EMS inputs are read as **contacts**: set two voltage ranges, 0–2 V (closed to ground) and 2–5 V (open). Inputs are 0–5 V, protected to 30 V spikes.
2. [D-ag, G3 p.7-87 to 7-88 (PDF 233–234)], "Example Contact Sensor Setup": pin C37 P9 named CANOPY. If the config file contains `canopy_warn_rpm_v16 = XXXX`, the **audio "Check Canopy Latch"** plays when engine RPM exceeds that value and the canopy input is open. The example widget shows OPEN in **red** and CLOSED in **green**.
   - [Y] Again "closed", not "locked", and the trigger is RPM only.
3. **Van's SB 00103** [D-ag, P4 p.1–2]: after a SkyView v16.7 software change, the canopy warning fired **at 200 RPM** instead of the set value (a nuisance alert from a config error). Fix: new file, thresholds **1,500 RPM (Lycoming)** and **3,700 RPM (Rotax)**; ground test with the canopy unlatched, then latched.

## 4. Passive (non-electrical) visual indicators: evidence

### 4.1 What exists
1. **Extra NG** [Y, from R0 AAIB note p.9–11]: a green "LOCK" area on the handle; POH since Dec 2022 says "Verify handle is in the LOCK position (green marking)". AD 2025-0156 adds new placards. But a **partially locked handle "just enters the green lock area"** (AAIB p.9). So the green marking on the handle does not separate partial from full lock. Handle distance is 70 mm open and 70 mm locked, 60 mm partial.
2. **EASA AD 2024-0059** (Schempp-Hirth Duo Discus, Nimbus-4) [D-ag, E5 p.1–2]: in one occurrence the investigation could not rule out that the canopy "remained unlocked, unnoticed by the crew (**the handle in locked position but not connected with the fuselage pins**)". A fatal accident in 2023 "again highlighted" the risk. The AD requires a mechanical modification of the locking mechanism within 12 months, not an indicator.
3. **Standard Cirrus tailplane lever** [D-ag, E6 p.4–5]: after G-DDGX the club added "**tell-tale markings**" for the locking-lever position; "EASA recommended that such markings … should be **green** in colour". EASA then issued **AD 2020-0260** mandating an "**optical indicator**" for the elevator attachment lever within 90 days, with an AFM change. The AAIB judged this "Adequate – Closed".
   - [Y] Precedent: EASA accepts a passive optical indicator as the fix for a hidden lock state, but it was mandated together with an AFM check, not alone.
4. **Europa** [Y, from R1 and R2 row AAIB-25]: LAA mod SM 15833 is a mechanical stop that blocks the lever unless the door is latched, plus coloured marks.
5. **Slingsby T67** [Y, from R2 row AAIB-03]: mod M810 placard made mandatory by the CAA after partial-latch openings.
6. **ASK 21** [D-ag, E9 p.3–4]: the front canopy cannot be locked until the rear canopy is locked (mechanical interlock). "If the rear canopy is opened after the front canopy is closed, the inter-lock is bypassed."
7. **Gliders, helper check** [D-ag, E8 p.1]: "Some glider types (e.g. Vega) may require a helper to check the canopy is locked." The wing runner should check canopy and brakes before hooking on.
8. **Jettison and wiring** [D-ag, E7 pp.2–3]: in the ASW 19B fatal accident, cables tied to the canopy frame and glare shield would probably have **prevented canopy jettison**. AAIB SR 2006-127/128 ask for checks that nothing stops full jettison.
   - [Y] Any sensor wiring that crosses onto the Extra NG canopy frame must have a break-away connector so it cannot hold the canopy during jettison.

### 4.2 Evidence that indicators were present but missed or wrong
| Case | What the indicator did | Source | Tag |
|---|---|---|---|
| DA 20-A1 N527SS, 1998 | Canopy warning light fitted. Pilot "did not observe the canopy warning light during taxi". Canopy separated at about 400 ft. NTSB factor: "failure to detect the canopy warning light" | E1 p.1–2 | D-ag |
| DA 20-A1 N560SS, 1997 | Pilot forgot to latch. After the accident "the canopy unlocked light was still illuminated" | E2 p.1 | D-ag |
| RV-14 N6161, 2023 (fatal) | Microswitch set so it "would have signaled a closed canopy before the canopy pins were fully seated". In taxi the warning stopped, "consistent with the pilot at least partially closing the canopy for the annunciator to extinguish". In flight, "intermittent but frequent canopy open warnings" until the upset | E3 p.1–2, p.12–13 | D-ag |
| VariEze N88VE, 1996 | Two aborted take-offs for a canopy-unlatched light, then a steep climb and stall at about 100 ft. NTSB factor: "diverted attention to the unlatched canopy warning light" | E4 p.1 | D-ag |
| DA 40 fleet | Shared canopy/door light lit during normal open-canopy taxi, "the pilot ignores the annunciation" | R0 FAA AD 2010-25-01 note | Y (from R0) |
| PA-31 G-UKCS, 2021 | Door-ajar light out and indicator showed SAFE before departure; door opened at 2,000 ft | R2 row AAIB-26 | Y (from R2) |

- [Y] Lessons:
  1. A **light that is on before take-off is easily missed** in taxi (DA 20 ×2). The alert must escalate at throttle advance (flash + aural), not just sit there.
  2. **Rigging defines the truth.** Van's own read-me warns that adjusting the switch to stop in-flight false warnings "may result in the canopy latch handle not being fully closed when the canopy switch engages" [D-ag, P1 p.4; P2 p.4]. The RV-14 accident (E3) is that failure. Pilots then use the lamp as the closing criterion ("close until the light goes out").
  3. **An alert during the take-off roll can itself distract** (VariEze, E4). The procedure must be "reject and stop", not "fix it while rolling". So the red stage should arm before high speed, and in flight the cue should say "fly the aircraft".
  4. Van's (P1 p.4, P2 p.4): "the canopy warning should not be the only means of checking that canopy is latched. A visual inspection of the canopy latch is still required." [D-ag]

### 4.3 Evidence that passive indicators work
- **None found.** No study or before/after occurrence count for coloured bands, flags or windows on canopy or door locks was found. EASA's AD 2020-0260 and the Europa and T67 mods show regulators accept them, not that they were measured to work. [Y]

## 5. Commercial canopy/door warning products

Table 2. Only Van's (micro-switch kits) and EFIS built-ins were found; no glider canopy-lock warning product was found.

| Product | Sensing | Indication | Price (as listed) | Mass | Source | Tag |
|---|---|---|---|---|---|---|
| Van's RV-6/7/9 tip-up Canopy Latch Warning Kit | 2 micro-switches: "canopy closed" switch + "latch" switch | EFIS discrete, or AV-01957 board | USD 187.95 (backorder, 60–90 days) | not listed | P6; P5 p.OP-61-01/02 | D-ag |
| Van's AV-01957 Canopy Latch Warning PCB | latch sense circuit + engine RPM (tach / P-lead) | red LED in a panel push-button (ES-GPB508AL05BR), lit whenever latch circuit is open; voice "CHECK CANOPY LATCH" above 1,600 RPM (3,000 Rotax); mute mode for run-ups or a failed switch | store page 404 (not read) | not listed | P5 PDF p.4–5 | D-ag |
| Van's RV-12 canopy latch warning (Notification 14-05-22) | switch at latch | SkyView/G3X visual + intercom audio above 3,700 RPM | not listed | not listed | P3 p.1 | D-ag |
| Van's RV-14 G3X Touch config | switch to GEA 24 P244 pin 42 "Discrete 3" | visual + audible above 1,700 RPM; audible repeats 10 times | free file | — | P1 p.1 | D-ag |
| Van's RV-14 SkyView config | switch | visual + audible above 1,500 RPM | free file | — | P2 p.1 | D-ag |
| Garmin G3X Touch "Canopy Closed" discrete | any ground-closing switch | yellow CANOPY OPEN; flashing red + tone at power / airborne | part of EFIS | — | G1 p.30-214 | D-ag |
| Dynon SkyView contact input | contact to ground | widget OPEN red / CLOSED green; voice "Check Canopy Latch" above set RPM | part of EFIS | — | G3 p.7-88 | D-ag |
| Aircraft Spruce AN-21 Annunciator Control Unit (experimental) | 21 channels: 16 ground-activated, 5 positive | per channel: steady light, flashing light, alert tone; lamp test; dim | EUR 397.85 incl. 19 % VAT | 0.272 kg | P7 | D-ag |
| SOTECC canopy strobe kit (gliders) | none (anti-collision strobe, not a lock warning) | LED strobe; option "mit Haubenkontakt" (canopy contact) | EUR 299, contact option +59.50 | not listed | P8 | D-ag (what the "Haubenkontakt" does: not verified) |
| Honeywell GAPS proximity sensor | inductive | — | — | < 60 g | R0 Honeywell note | Y (from R0) |

## Design implications [Y]

All numbers below are R7's proposals, derived from the sources above.

1. **Two visual channels, one logic.** (a) A dedicated lamp at the **top centre of the rear panel, just below the glareshield, on the pilot's centreline**. (b) The same state as a G1000 CAS message (if Extra configures it) or, in the standalone version, only the lamp. A **repeater lamp in the front cockpit**, same logic, so both seats get it at the same time (V3 App. 1 §1.b(1)(c)).
2. **Placement target:** inside **±15°** of the normal line of sight for the head-down case (V4 §15.2, V1 §5.4.2.2.1.8, V2 §5.1.2). Accept that on the take-off roll the pilot looks out, so the lamp will be 25–40° off-axis [not measured]. Compensate with size, flash and aural, not colour (red is poorly seen in the periphery, V1 §5.6.6.2.3.2).
3. **Size:** lit face **≥ 25 mm** high (V1 Exhibit 5.4.2.2.3.3), e.g. a 25 × 38 mm legend lamp. That is about 1.9° at 762 mm, above the 1° minimum (V3). Legend characters **6 mm** high (about 27 arcmin at 762 mm, between the 20 arcmin minimum and the 45 arcmin maximum). Opaque black letters on a lit background for the red warning (V2 §5.1.3.2, V1 §5.4.2.2.2.5).
4. **Legend:** one lamp, three states, words not just colour (R4 §1.1, AC 23.1311-1C §22.6):
   - dark = system off or not armed. Dark never means "locked" (V1 §5.4.2.2.1.5);
   - **green steady "CANOPY LOCKED"** only when all bolt sensors and the seated sensor agree (V1 §5.4.2.2.1.3: equipment response, not control position);
   - **amber steady "CANOPY UNLOCKED"** on the ground below take-off power (caution: steady, V2 §5.1.4.4);
   - **red flashing "CANOPY UNLOCKED"** at take-off power or airborne, with voice.
   - Do **not** use "CANOPY OPEN": the pilot sees a closed canopy and may disbelieve the alert. If a G3X is used, use a User-Defined Alert with this text (G1).
5. **Flash:** red stage at **4 Hz, 50 % duty (125 ms on / 125 ms off)**, inside the 3–5 Hz band of V1 and V2. Flash **until acknowledged**, then steady red until the condition clears (G1000 pattern, G2; V3 §1.b). If the flasher fails, **steady ON** (V1 §5.4.2.1.1.6). Only one flash rate in the system; if the front repeater flashes, synchronise it (V2 §4.1.3.5).
6. **Luminance and contrast:**
   - **≥ 514 cd/m² (150 fL)** at rated voltage as the floor (V2 §5.1.3.3). Design target **about 1,000 cd/m² (≈ 300 fL)** at beginning of life to keep margin at end of life (V4 §16.1).
   - Lit-legend contrast ratio **≥ 2.0** at **107,640 lx (10,000 fc)**; unlit legend **< 0.1**, so a sunlit dark lamp never looks lit (V2 §5.1.1, V1 §5.4.2.2.1.15).
   - **Two LEDs in parallel** per legend (V2 §5.1.3.3).
   - Auto-dim at night to about **51 cd/m² (15 fL)**, but the red stage can never be dimmed below an attention-getting level, and no daylight dimming (V2 §5.1.3.3, V3 §1.d).
   - Under a bubble canopy, aim the lamp face slightly up and back toward the pilot's eye and give it a short hood that does not cut the view angle (V1 §5.3.1.6.3–.4).
7. **Test:** press-to-test on the lamp (V1 §5.4.2.2.1.21) and a power-up self-test that lights all three colours for 1 s. Ground acceptance test with the **FAA daylight readability method**: low sun, rotate the aircraft, mirror; red must look red, not orange, and catch attention at every sun angle (V6).
8. **Passive indicator (recommended as a complement, not a replacement):**
   - Put the mark on the **bolts**, not on the handle. The handle reads 70 mm both open and locked and the partial lock already reaches the green zone (AAIB p.9).
   - One small **inspection window per shoot bolt** in the frame inner skin, with a **red band on the bolt shank that is visible until the bolt is fully home** and a green band visible only at full engagement. Red visible = not locked.
   - It costs grams and no power, gives the "direct visual inspection" CS 23.783(e)(2) asks for (R4), and lets the pilot verify a red alert in seconds, which lowers the cry-wolf cost (R4 implication 6, H13).
   - Limits: the windows are on the left canopy rail, so they are hard to see from the seat in flight; and no evidence was found that passive marks alone prevent events (§4.3). Keep it as the walk-round and pre-take-off cross-check.
9. **Rigging rule:** set each sensor so it reports LOCKED only at full bolt engagement, with the partial-lock position (60 mm handle) as the test case. Do **not** move the sensor to stop in-flight nuisance alerts; fix the cause instead. This is the RV-14 lesson (E3, P1).
10. **Procedure link:** red at take-off = **reject**, never "fix it on the roll" (E4). In flight: aviate first (E8), do not hold the canopy.

## NOT VERIFIED

1. **SAE ARP4256A, AS8034B, AS8055, ARP4102** (display luminance and contrast numbers): paywalled, not read. Only the FAA ACs that cite them were read.
2. **MIL-STD-411F** was read from the emilspec HTML transcription, not from the official DLA ASSIST PDF. The everyspec URL tried returned 404. The revision letter "411F" appears in the page headers; whether this is 411F with Change 1 is not checked.
3. **MIL-STD-1472H** itself was not read. Its rules are taken from HF-STD-001B, which cites MIL-STD-1472G (2012).
4. **Yeh et al. (2016) DOT/FAA/TC-16/56**, Human Factors Considerations … Flight Deck Displays and Controls V2: ROSA P returned **403** and the Volpe copy returned **403**. Not read.
5. **Boucek et al., FAA Aircraft Alerting Systems Standardization Study Vol. II (DTIC ADA106732)**: DTIC returned **403**. Its master-warning location and flash guidance are not verified.
6. **Walters et al. (2016)** and **Nikolic et al. (2004)**: closed access; abstract only. Miss rates at angles other than 15° are not known.
7. **Wickens et al. (2009) HFES papers on NASA Ames** (off-nominal event detection by location): server `human-factors.arc.nasa.gov` timed out (curl and WebFetch). Not read.
8. **UMTRI-99-20 (Sivak et al. 1999), colour identification in the periphery**: Deep Blue and CORE both returned **403**. The claim that peripheral red is often seen as yellow is from a search summary only. **Do not cite.**
9. **Gerathewohl (1953, 1954)** and **Kobrick (1965)**: known only through the NASA TN D-5174 review.
10. **EASA AD 2020-0260** (optical indicator, Standard Cirrus elevator lever): ad.easa.europa.eu showed a maintenance page. Its content is known only from the AAIB SR document (E6).
11. **G1000 discrete-input installation data** (GEA 71 / GIA pins, how Extra would configure a CANOPY CAS message): no public document found. The Extra NG G1000 CAS list is not known.
12. **Extra SB-NG-1-24 placard wording and colours**: not obtainable (as in R0).
13. **Extra NG rear-seat geometry** (eye-to-panel distance, angle from take-off line of sight to the PFD and to the glareshield): not measured. The 762 mm distance and the 25–40° estimate are assumptions.
14. **Van's AV-01957 price** (search snippet USD 192.50) and **RV-12 kit ES-00300 price** (forum post USD 87.50): store page 404 and forum not read. Not verified. Mass of the Van's kits not listed.
15. **ATSB AAIR 1988-00735** (glider canopy handle fully closed without pins engaged, "not easy to detect from inside the cockpit", per a search summary): download failed (connection error). Not read.
16. **Glider canopy-lock warning products** (DG, Schempp-Hirth, Schleicher, Jonker, LAK factory options): none found in two searches. Absence is not proven.
17. **What the SOTECC "Haubenkontakt" option does**: not verified (it may only power the strobe across the canopy break).
18. **Effectiveness data for passive lock indicators** (flags, bands, windows): none found.
19. The two tables above were written by hand. The `datawiz` table generator was not run on them.
