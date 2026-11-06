# R8: Similar warning systems: design, effectiveness, cost (input for CHEAP vs EXPENSIVE tiers)

- read by: subagent R8-systems
- date read: 2026-11-05
- Tags:
  - **[D-ag]**: read at the source in this session. URL and page/section given.
  - **[D-ag abstract]**: only the abstract was read (Europe PMC record).
  - **[Y]**: a secondary source (search snippet, news report) or R8's own interpretation or arithmetic. Each [Y] says which.
- Local copies (untrusted data): `D:\tmp_ideathon\easa\dl\r8_systems_cost\`. Text extracted with `pdftotext`. Scripts were kept in the session scratchpad, outside that folder; Python that read downloads ran with `python -I`.
- Not repeated here (already recorded): Van's canopy kit USD 187.95, AN-21 EUR 397.85, G3X/Dynon canopy functions, RV-14/BD-10/L-39 cases, SAFO 13003 (`R7_sensing_integration_products.md`, `R7_visual_alerting.md`); TOWS accident mechanics (NW255, DL1141, Spanair), G-IV gust lock, the 1974 belt interlock (`R7_interlock_engine_shutdown.md`); gear-horn NTSB cases (`R7_auditory_alerting.md`); FAA AD 2026-04-12 USD 95 (`R1_faa_ad.md`).
- **Tables are hand-written.** The AD cost table was first generated with the datawiz `tablo` tool. Its `denetle` check returned no issues. But its 2-significant-digit rounding changed quoted figures (e.g. USD 10 parts became 0). Regulator figures are therefore printed exactly as published. Sort order and units-in-header follow the datawiz rules.

## Sources

| ID | Document | URL | Read |
|---|---|---|---|
| A1 | FAA AD 2011-26-01, Piaggio P.180 baggage door, 76 FR 77369 (13 Dec 2011) | https://www.govinfo.gov/content/pkg/FR-2011-12-13/pdf/2011-31623.pdf | summary, MCAI text, Costs of Compliance, PDF p.1 |
| A2 | FAA AD 2013-14-10, Gulfstream 100 / Astra main entry door, 78 FR 47546 (6 Aug 2013) | https://www.govinfo.gov/content/pkg/FR-2013-08-06/pdf/2013-18768.pdf | summary, MCAI, Costs, PDF p.1; para (h) p.3 |
| A3 | FAA AD 2009-18-11, Fokker 70/100 passenger door, 74 FR 46334–46335 (9 Sep 2009) | https://www.govinfo.gov/content/pkg/FR-2009-09-09/pdf/E9-20834.pdf | summary, MCAI, Costs (p.46335) |
| A4 | FAA AD 96-20-04, Fokker F28 Mk 1000–4000 door lock warning, 61 FR 50992–50994 (30 Sep 1996) | https://www.govinfo.gov/content/pkg/FR-1996-09-30/html/96-24652.htm | summary, comments, Cost Impact |
| A5 | FAA NPRM, Docket FAA-2026-4633, Diamond DA 40 series passenger door (public-inspection copy 2026-09574) | https://public-inspection.federalregister.gov/2026-09574.pdf | summary p.1, Costs of Compliance p.7, para (3) p.11 |
| A6 | FAA AD 2011-10-13, Diamond DA 42 family rear door, 76 FR 27861–27863 (13 May 2011) | https://www.govinfo.gov/content/pkg/FR-2011-05-13/pdf/2011-11267.pdf | MCAI text p.1, Costs p.2 |
| A7 | FAA AD 2010-25-01, Diamond DA 40 rear door, 75 FR 75868–75869 (7 Dec 2010) | https://www.govinfo.gov/content/pkg/FR-2010-12-07/pdf/2010-30199.pdf | comment "Disconnect the Front Canopy Latch Sensor" + FAA response p.75868–69; Costs p.75869 |
| B1 | NTSB AAR-92/02, United 811, B747-122 N4713U, 24 Feb 1989 | https://www.faa.gov/sites/faa.gov/files/AAR92-02.pdf | pp.2–3, 15–16, 57–58, 61, 64–65, 93–94 |
| T1 | FAA SAFO 08021 (5 Nov 2008), TOWS and SOP, DC-9/MD-80/MD-90/B717 | https://www.faa.gov/sites/faa.gov/files/other_visit/aviation_industry/airline_operators/airline_safety/SAFO08021.pdf | pp.1–2 |
| T2 | FAA AC 25.703-1, Takeoff Configuration Warning Systems (17 Mar 1993) | https://www.faa.gov/sites/faa.gov/files/2022-11/AC%20025.703-1.pdf | §5b–5e, pp.3–6 |
| G1 | D. J. Kenny, "The cost of non-accidents", AOPA Flight School Business, 23 Jun 2017 | https://www.aopa.org/training-and-safety/flight-schools/flight-school-business/newsletter/2017/june/23/cost-of-non-accidents | whole article (via WebFetch) |
| G2 | D. J. Kenny, "Taking our lumps", AOPA Flight School Business, 1 Dec 2014 | https://www.aopa.org/training-and-safety/flight-schools/flight-school-business/newsletter/2014/december/01/taking-our-lumps | whole article (via WebFetch) |
| G3 | Gliding Australia, "Technical briefing: key safety and operations update", 3 May 2026 (canopy section by D. Villers) | https://www.magazine.glidingaustralia.org/operations/gliding-australia-technical-briefing-key-safety-and-operations-update | canopy section (via WebFetch) |
| G4 | EASA AD 2024-0059 (Duo Discus / Nimbus-4D canopy locking), DAeC German translation | https://www.daec.de/media/files/Dateien/Fachbereiche/Luftfahrttechnik/AD_2024-0059_SHK_ua_DUO_Haubenverriegelung_Deutsche_UEbersetzung.pdf | pp.1–2 (translation; English original is binding) |
| G5 | SUST Safety Recommendation 469 (airbrakes not locked, winch launch), 19 Jun 2013 | https://www.sust.admin.ch/de/sicherheitsempfehlungen/aviatik/av_se_469.pdf | full |
| G6 | SUST Safety Recommendation 409 (glider stall warning), status update 2026 | https://www.sust.admin.ch/de/sicherheitsempfehlungen/aviatik/av_se_409.pdf | full |
| G7 | Österreichischer Aero-Club, Safety-News 04/2023 "Geschlossen und verriegelt?", 14 Aug 2023 | https://aeroclub.at/uploads/download/Safety-News_04_2023_Haube_geschlossen_verriegelt.pdf | full |
| C1 | Lie, Krafft, Kullgren, Tingvall (2008), Traffic Inj. Prev. 9(5), doi 10.1080/15389580802149690 | Europe PMC REST search (core record) | abstract |
| C2 | European Commission, ERSO, "Seat belt reminders" (eSafety measures, known safety effects) | https://road-safety.transport.ec.europa.eu/european-road-safety-observatory/statistics-and-analysis-archive/esafety/esafety-measures-known-safety-effects/seat-belt-reminders_en | whole page (via WebFetch) |
| C3 | NHTSA final rule, FMVSS 208 seat belt warning (rear seats; front), 90 FR 389 ff. (3 Jan 2025) | https://www.govinfo.gov/content/pkg/FR-2025-01-03/html/2024-30340.htm | pp.392, 394, 405, 447 |
| C4 | IIHS news, "Fewer drivers are opting out of lane departure prevention", 1 Oct 2024 | https://www.iihs.org/news/detail/fewer-drivers-are-opting-out-of-lane-departure-prevention | whole (via WebFetch) |
| C5 | IIHS news, "Lane departure warning, blind spot detection help drivers avoid trouble", 23 Aug 2017 | https://www.iihs.org/news/detail/lane-departure-warning-blind-spot-detection-help-drivers-avoid-trouble | whole (via WebFetch) |
| C6 | Reagan & McCartt (2016), Traffic Inj. Prev., doi 10.1080/15389588.2016.1149698 | Europe PMC REST search | abstract |
| C7 | Reagan, Cicchino, Montalbano (2019), Traffic Inj. Prev., doi 10.1080/15389588.2019.1569759 | Europe PMC REST search | abstract |
| P1 | Aircraft Spruce, Voice Alert 2040 page | https://www.aircraftspruce.com/catalog/avpages/voicegearalert.php | seen 2026-11-05 |
| P2 | Aircraft Spruce Europe, Press-To-Test MS25041-2 Red, P/N 11-03910 | https://www.aircraftspruce.eu/press-to-test-ms25041-2-red.htm | seen 2026-11-05 |
| P3 | Aircraft Spruce, Garmin GEA 24B, P/N 11-11452 (010-02770-00) | https://www.aircraftspruce.com/catalog/pnpages/11-11452.php | seen 2026-11-05 |
| P4 | Online Components, Honeywell MS27216-6 | https://www.onlinecomponents.com/en/productdetail/honeywell/ms272166-11939722.html | seen 2026-11-05 |
| P5 | Precision Microdrives 307-103 product page | https://www.precisionmicrodrives.com/product/307-103-9mm-vibration-motor-25mm-type | seen 2026-11-05 (no price shown) |

Tried once, not obtained: SWOV library pages (Cloudflare Turnstile bot check); NHTSA DOT HS 811 097 landing page nhtsa.gov/node/10226 (**403**); RS Online micro-switch page (**403**); Aviation Consumer "Landing Gear Alerters" (paywall after intro); Garmin "Experimental Pricing Sheet 2023" (**404**); EASA AD 2008-0197 page (EASA maintenance page); BGA 2022 Accident Review (**404**); Europe PMC full text of Williams et al. 2002 (HTTP 500); one Europe PMC search returned 503. None were bypassed.

---

## 1. Door and canopy warning retrofits mandated by ADs

### 1.1 Regulator cost estimates (USD as printed in each rule, rule-year dollars)

**Brief.** The reader wants a cost anchor for each kind of fix. Figures are the FAA's own "Costs of Compliance" numbers. The labour rate differs by year, so compare work-hours, not dollars, across decades.

Table 1. FAA cost estimates for door/canopy warning-related ADs span USD 95 to USD 6,947 per aircraft. Sorted by total. Hand-written; values exactly as printed.

| Action (AD) | Year | US fleet | Labour (work-h) | Rate (USD/h) | Parts (USD) | Total per aircraft (USD) | Source |
|:---|---:|---:|---:|---:|---:|---:|:---|
| Extra NG, AD 2026-04-12: canopy placards (+ 1 h POH revision, USD 85, separate) | 2026 | 30 | 1 | 85 | 10 | 95 | R1 (D-ag, final rule p.12685) |
| Diamond DA 42, AD 2011-10-13: rear-door retaining bracket | 2011 | 162 | 2 | 85 | 71 | 241 | A6 p.2 [D-ag] |
| Diamond DA 40, AD 2010-25-01: rear-door bracket retrofit (428 aircraft); AFM 0.5 h = 42.50 for all 699 | 2010 | 428 | 2 | 85 | 75 | 245 | A7 p.75869 [D-ag] |
| Diamond DA 40, NPRM 2026: initial inspection incl. "canopy and passenger door warning light", placards | 2026 | 987 | 3 | 85 | 76 | 331 | A5 p.7 [D-ag] |
| Fokker 70/100, AD 2009-18-11: warning placard + lock-switch clearance check | 2009 | 10 | 4 | 80 | 20 | 340 (computed [Y]) | A3 p.46335 [D-ag] |
| Fokker F28, AD 96-20-04: modify passenger-door lock **warning system** | 1996 | 37 | 22 | 60 | 865 | 2,185 | A4 Cost Impact [D-ag] |
| Gulfstream 100 / Astra, AD 2013-14-10: split shared caution light, make it a red warning, rewire panel and harness, AFM | 2013 | 160 | 60 | 85 | 600 | 5,700 | A2 p.1 [D-ag] |
| Piaggio P.180, AD 2011-26-01: inspect/adjust baggage-door lock pins; modify mechanism if needed | 2011 | 102 | 29 | 85 | 4,482 | 6,947 | A1 p.1 [D-ag] |

Reading [Y]: paperwork and placard fixes cost ~1–4 work-hours. Changing a warning system on an existing aircraft (new switches, panel, harness) cost **22–60 work-hours**. That is the best regulator-published anchor we have for retrofit labour.

### 1.2 What these ADs say about warning-system design and effectiveness

1. **Piaggio P.180 (A1) [D-ag, p.1].** MCAI: one in-flight baggage door opening; "the BAG DOOR warning light went on properly before the event, but was ignored by the pilot, who misinterpreted it as a false warning." False BAG DOOR lights had occurred with the door shut. The AD fixed the **mechanism** (lock-pin engagement), not the light. Operators that had seen false indications got the full modification.
2. **Fokker 70/100 (A3) [D-ag, p.46334–35].** A **false** steady red "DOOR NOT LOCKED" light after lift-off led the cabin crew to work the door handle, and the airstair door opened in flight. Cause: up-limit switch clearance out of tolerance; pressurisation then made the light come on. The clearance was later tightened from 1.3 ± 0.3 mm to **0.3 ± 0.2 mm**. Fix = placard ("do not operate handle in flight; tell the flight crew") + clearance check. **A false alarm can provoke a harmful action, not only be ignored.**
3. **Fokker F28 (A4) [D-ag].** Doors opened in flight because they were not properly locked; "the door warning signal was not sufficiently visible to alert the flight crew". The fix was a warning-system modification, 22 work-hours. A commenter asked for interim preflight guidance; the FAA forwarded it but did not require it.
4. **Gulfstream 100 / Astra (A2) [D-ag, p.1].** The MCAI split one common CABIN DOOR caution light (it served both "improper closure" and "seal failure") into CABIN DOOR and CABIN DOOR SEAL, and changed CABIN DOOR from caution to **red warning**. The superseding AD was prompted by a door opening in flight on an **unmodified** aircraft. Lesson: one cause per light, warning colour for "not locked".
5. **Diamond DA 40 / DA 42 (A6, A7, A5) [D-ag].**
   - A6 p.1: "All DA 40 and DA 42 aeroplanes have a system installed that provides a warning if the main door latch is not fully closed." Yet: "Since 2004, more than 30 reports … of in-flight loss of a rear passenger door", root cause "the crew not properly securing the rear passenger door by the main locking mechanism".
   - A7 p.75868–69: the DA 40 door light is shared with the canopy, and pilots who taxi with the canopy cracked open learn to ignore it (already in R0). **New this session: the FAA's response.** "The FAA does not agree nor disagree"; it was investigating with ACG, EASA and Diamond, and Diamond planned a design and flight-test review. The AD was not changed. This closes the "not verified" item in `R0_FAA_AD_2010-25-01_DA40_door_annunciation.md`.
   - After these ADs, the FAA in 2024 still counted ≥ 20 door separations and > 30 aborted flights (R7 F2, already recorded). A5 (2026) now adds a mandatory inspection of the warning light itself plus placards: 3 work-hours + USD 76 parts.
   - **Effectiveness reading [Y]:** a fitted, shared, frequently-lit warning did not stop about 50 door losses over ~20 years. The fixes chosen were mechanical (bracket), procedural (AFM "land at the next suitable airfield", A7) and inspection-based. No AD separated the light.
6. **United 811 / Pan Am 125, B747 cargo door (B1) [D-ag].**
   - The cockpit cargo-door light was switched **by the pressure relief doors**, which are linked to the lock sectors, not by the latch cams themselves (p.15–16).
   - Pan Am 125, 10 Mar 1987: door found open ~1.5 in with cams unlatched, handle stowed, **cockpit light off** (§1.17.1, pp.57–58).
   - In 1970 the FAA approved Boeing's request to drop the eight view-port / alignment-stripe check in favour of checking the relief doors; the view-port maintenance procedures then disappeared from the UAL manual (pp.64–65).
   - After UAL811 the FAA's telegraphic AD 89-05-54 reinstated the view-port check, added confidence checks and accelerated steel doublers on the lock sectors (§1.17.3, p.61).
   - NTSB A-89-93 (p.93): positive indicators "confirming the actual position of both the latch cams and locks, independently". At the hearing Boeing said it was "looking into" a position switch directly on the cams (p.65).
   - **Effectiveness reading [Y]:** a warning that senses a proxy (relief door, handle) can say "safe" while the latches are open. This is the same failure as BD-10 / L-39 in R7. Per-point sensing is the regulator-endorsed answer.
7. **No before/after event counts were found** for any of these ADs. None of the Federal Register texts quantifies the reduction they expect. [D-ag, absence in A1–A7]

## 2. Gear-up warning systems in GA

1. **Counts despite horns [D-ag, G1].** AOPA ASI logged gear-ups from FAA preliminary reports: **159 in calendar 2016**, of which 154 unintended, "about three per week". **Fewer than 10 %** reached the NTSB accident database. FY2013: 58 gear-ups in FAA daily reports; only 5 in the NTSB database; about 90 % were below "substantial damage"; 10 were twins (G2) [D-ag].
2. **Why horns fail (G1, G2) [D-ag].** Distraction is the pilots' most common explanation. Horn mistaken for the stall horn. A pilot "so distracted by the noise of the gear horn that he forgot to lower the gear". Earlier R7 evidence: breaker pulled because of nuisance activation at normal power, horn not routed to headsets (SAIB CE-16-08).
3. **Design point [Y, from AOPA snippet seen in search, not the fetched text]:** the horn is armed by throttle at idle, so a power-on approach can keep it silent. Treat as secondary.
4. **Retrofit price.** Voice Alert 2040 (voice "CHECK LANDING GEAR" in the headset, driven by the existing horn): **USD 721.00** (2040-1-2, P/N 10-00394) to **USD 1,084.00** (2040-1-1 custom / -1P primary). Installed unit **< 1 lb**. A&P installation; 1 A fuse not included. [D-ag, P1, seen 2026-11-05]
5. **Effectiveness data for voice gear alerters: none found.** The Aviation Consumer comparison was paywalled.
6. Reading [Y]: a cheap, universal, decades-old horn still leaves ~150 gear-ups a year in the US. The residual failure modes are exactly ours: arming logic, masking by headsets, confusion with another tone, nuisance-driven disabling.

## 3. Take-off configuration warning (TOWS)

1. **Scale [D-ag, T1 p.1].** Worldwide, take-off configuration errors figured in **49 accidents and incidents since 1968, with 392 fatalities**. "A warning system and SOP can only be effective mitigations if the system is properly maintained and the SOP is properly designed and followed."
2. **EASA response after Spanair [D-ag, T1 p.2].** EASA AD 2008-0197 revised the AFM to require a TOWS check **before engine start prior to every flight**. McDonnell Douglas had recommended this after the 1987 accident, but EASA noted the check had drifted to "less frequently". (The EASA AD page itself showed a maintenance page; content read via the FAA SAFO only.)
3. **Design rules from AC 25.703-1 [D-ag, T2].**
   - Ordinary alerting systems are typically shown to ≈ **1.0 × 10⁻³ per flight hour** probability of failure to warn, single channel with limited monitoring (§5b(2), p.3). For TOWS that is **not adequate**; it must meet the "major" failure-condition criteria (§5b(3)).
   - A false warning near V1 should be "improbable" (§5b(5)).
   - Suppress the warning where acting on it is more dangerous (e.g. between V1 and VR) (§5c(3), p.4).
   - Aural signals should exceed the masked threshold by **8 ± 3 dB**, with automatic volume adjustment (§5c(5)).
   - "Attempting to eliminate nuisance warnings cannot be overemphasized": nuisance warnings tempt crews to deactivate the system and condition them "to ignore a valid warning" (§5c(6), pp.4–5).
   - **No MMEL relief**; the design should annunciate a detected failure or loss of power immediately (§5c(9), p.5).
   - Tests must verify **each input sensor** individually, plus logic and output devices, and show the warning self-cancels (§5d(2), p.6).
   - Digital self-monitoring has brought "an improvement in reliability, fewer unwanted warnings and enhanced safety" (§5c(1), p.4).
4. **TOWS cost: not found** this session (no TOWS AD cost paragraph was located).

## 4. Automotive analogues

### 4.1 Seat-belt reminders (SBR)

1. **Effect size, Europe [D-ag abstract, C1].** Field observations in six countries and five Swedish cities. Belt use **97.5 % ± 0.5 % with SBR vs 85.8 % ± 0.8 % without**. Brussels 92.6 % vs 69.6 %; Paris 99.8 % vs 96.9 %. **82.2 % ± 8.6 %** of drivers who would not buckle up do so with an SBR that has a light plus a "loud and clear" sound.
2. **Intensity matters [D-ag, C2].** Swedish study: **99 %** belt use with the most advanced reminders, **93 %** with "mild" reminders (visual + soft sound), **82 %** without. EEVC (2002) recommended progressive, multi-step visual + sound signals aimed at part-time users. ETSC (2004) cost-benefit for front-seat audible reminders ≈ **6 : 1** (costs ≈ EUR 11 M, benefits ≈ EUR 66 M over 12 years).
3. **US, Ford Belt-Minder [Y, search snippets + C2].** Chime and light for 6 s, pause 30 s, repeat up to 5 min. Belt use 71 % without vs 76 % with (Williams, Wells, Farmer 2002, Inj. Prev. 8:293). C2 [D-ag] summarises it as a "7 % increase". Full text not obtained (Europe PMC 500).
4. **Cost per vehicle [D-ag, C3].** NHTSA teardown: rear-seat buckle sensor + wiring **USD 6.28 per seat**, i.e. **USD 19.59 per vehicle** at 3.12 rear seats (p.447). Occupant detection adds **USD 39.74**, total **USD 59.33** per vehicle (2020 USD) (p.405). Front outboard passenger warning ≈ **USD 2.13** per vehicle (p.394). NHTSA assumed rear belt use rises only **3 to 5 percentage points** for occupants ≥ 11 years (p.392).
5. Reading [Y]: the cheap part is sensing and logic (single-digit USD per point in mass production). Effectiveness is driven by **signal intensity and persistence**: mild reminders recover about half of the non-users, loud persistent ones about 80 %.

### 4.2 Lane-departure warning (LDW): haptic vs audible, use rates

1. **Crash effect [D-ag, C5].** LDW lowers single-vehicle, sideswipe and head-on crash rates by **11 %** (all severities) and injury crashes of those types by **21 %** (controlled analysis). IIHS called the effect modest because "U.S. drivers … frequently turn off lane departure warning".
2. **Use rates [D-ag abstract, C6].** 2013–2015 Hondas (audible/visual alert): LDW on in **87 of 265 (32.8 %)**; forward collision warning on in all but one.
3. **Haptic is left on more [D-ag, C4].** 2023 survey of nearly 2,400 vehicles: lane systems on in **87 %** (51 % eight years earlier). Earlier work showed "higher activation rates for systems that used haptic alerts such as seat or steering wheel vibrations". Four of six makers now use haptic or offer it; "activation rates for the two that continued to use visual and audible alerts were substantially lower". For speed warnings: visual on in **71 %**, audible in **14 %**.
4. **Behaviour quality also matters [D-ag abstract, C7].** Makers whose lane-keeping acted earlier and prevented > 35 cm departures had higher observed use.
5. **Door-ajar warnings:** no effectiveness data or cost found.
6. Reading [Y]: annoyance decides whether an alert survives in service. Haptic and visual channels are tolerated; repeated audible alerts get switched off. This supports using sound only for the high-urgency state and vibration as the persistent channel.

## 5. Glider canopy warnings and campaigns

1. **Australia, 2011–2026 [D-ag, G3].** **59** uncommanded canopy openings since 2011; **25** appear to result from interrupted pre-take-off checks; **18 (~30 %)** were Astir types (sliding-bar latch; spring failure, binding, misalignment, corrosion, dirt, heat). Recommendations: maintenance and functional checks; an Operational Service Bulletin in preparation. "Multiple people checking a canopy does not improve safety and may reduce it." **No warning device is mentioned.**
2. **EASA AD 2024-0059, Duo Discus / Nimbus-4D [D-ag, G4 pp.1–2].** Canopies opened during aerotow (fuselage flexing let the lock move). In another event it could not be determined whether the canopy was locked or left unlocked unnoticed (handle in "locked" position but not engaged with the fuselage pins). A **fatal accident in 2023** showed the risk remained. Schempp-Hirth had published modification TMs in **2004/2005**; EASA made them **mandatory within 12 months** only in 2024. Reading [Y]: a voluntary mechanical fix existed for ~19 years without full uptake.
3. **SUST SE 469 (2013) [D-ag, G5].** For unlocked airbrakes on winch launch, SUST asked for a device that prevents unwanted extension "without additional manipulation for the pilot". The OSTIV Sailplane Development Panel proposed AMC 22.697(b) wording: airbrakes closed but not locked "shall remain substantially closed during the launch phase". Analogue [Y]: for gliders the authorities preferred a **passive design fix** over a warning.
4. **SUST SE 409 status 2026 [D-ag, G6].** No stall-warning devices exist on the market for gliders (except touring motor gliders). A retrofit prototype is being developed because glider operation near the stall needs a special design to avoid false alarms "that could lead pilots to deactivate it"; flight tests planned for summer 2026. Same cry-wolf constraint as ours.
5. **Campaign material [D-ag, G7].** Austrian Aero-Club checklist item 13: "Haube geschlossen und verriegelt … hinten und vorne!" No effectiveness data given.
6. **BGA / LBA:** no canopy campaign effectiveness data and no glider canopy-lock warning product found (BGA 2022 review returned 404). R7 already found none.

---

## 6. Cost-tier table for our canopy alert (Extra NG retrofit)

**Brief.** The reader must choose between cheap and expensive designs. Each tier adds to the one above. Parts are catalogue prices (date seen 2026-11-05). Labour hours are R8 estimates **[Y]**, anchored on the AD work-hours in Table 1. Labour is priced at the FAA's 2026 rate, USD 85/h (A5). Certification and engineering are excluded, as the brief says. EUR is shown separately (no FX conversion verified). The number of lock points is taken as **n**; the totals use n = 3 only as an example, to match the 3 bolts in the AAIB G-MIIL report (R0), not verified here for every serial number.

Table 2. Cost rises about 50-fold from Tier 0 to Tier 5, while the evidence for effectiveness is strongest for per-point sensing with a loud, persistent cue. Hand-written.

| Tier | What is fitted | Parts (catalogue) | Labour (work-h) [Y] | Approx. cost per aircraft, USD [Y] | Added mass [Y unless cited] | Effectiveness evidence this tier can claim |
|---|---|---|---|---|---|---|
| 0 Procedures / placards | New placards, POH limitation, "closed–locked–checked" callout | Placard USD 10 (FAA estimate, R1) | 2 (1 placard + 1 POH; R1) | **180** | ≈ 0 | Weakest. TOWS: SOP drifts without enforcement (T1). Australia: 25/59 openings from interrupted checks (G3). Omission HEP 0.001–0.01 per item (R0 NUREG). Duo Discus fix existed 19 years, still fatal 2023 (G4). |
| 1 Passive mechanical marks | Witness stripes / colour bands on each bolt, inspection window or mirror, placard | ~USD 20–80 (anchors: Fokker placard USD 20, A3; DA 40 placards + parts USD 76, A5) | 3–4 (A5 3 h; A3 4 h) | **275–420** | < 50 g | Regulators accept them (B747 view ports reinstated by AD 89-05-54, B1 p.61) but **no measured effect** (R7 visual: none found). Proxy-free if it shows the bolt itself. |
| 2 Single switch + lamp / EFIS (organisers' example) | 1 switch at handle or one bolt, red press-to-test lamp or EFIS discrete | Van's 2-switch kit USD 187.95 (R7); MS25041-2 red lamp EUR 35.30, 0.001 kg as listed (P2); EFIS discrete: no hardware cost if a G3X is fitted | 6–10 (between A5 3 h and A4 22 h) | **≈ 700–1,050** + EUR 35 | ≈ 0.1–0.2 kg | Mixed. DA 40/42 had a latch warning on every aircraft and still lost > 30 doors (A6), partly because the shared light was normal during taxi (A7). P.180 light ignored as false (A1). Proxy sensing misses open latches (B1, BD-10, L-39). Car analogue: "mild" reminder 93 % vs 82 % (C2). |
| 3 Per-point sensing + lamp + voice | One sensor per lock point (n), "CANOPY UNLOCKED" red lamp/annunciator, voice in headset | Sensors: ≈ USD 94 each (Van's kit price / 2) commercial, or **USD 908.84 each** for MIL MS27216-6 (P4); AN-21 annunciator EUR 397.85, 0.272 kg (R7); Voice Alert 2040 **USD 721** (< 1 lb, P1) or EFIS/audio-panel voice | 15–30 (A4 22 h, A1 29 h) | n = 3: **≈ 2,300–3,600** + EUR 398 (commercial sensors); **≈ 4,700–6,000** + EUR 398 with MIL sensors | ≈ 0.5–0.8 kg | Strongest documented. NTSB A-89-93: indicate actual position of each latch and lock independently (B1 p.93). Loud + light reminders convert ~82 % of non-users (C1); advanced 99 % vs 82 % (C2). One cause per light, red for warning (A2). |
| 4 + vibration + ground take-off gate | Tier 3 + ERM vibration on stick/throttle (persistent channel) + solenoid detent that blocks throttle past run-up power on the ground while unlocked | ERM motor 4.6 g (P5; **price not shown**); driver, solenoid detent: **no catalogue price obtained** | 40–60 (A2 60 h: panel, harness, wiring) | **≈ 6,000–9,000** [Y, parts guessed] | + 0.3–0.6 kg | Haptic alerts are left switched on far more than audible (C4, C6). Gate: TOWS teaches no-dispatch-when-failed and failure annunciation (T2 §5c(9)); interlocks get defeated ≈ 1/3 if they block normal use (R7). |
| 5 Integrated EFIS + recorder | Tier 4 + line-monitored sensors into EFIS (e.g. GEA 24B), CAS message, self-test, event logging | GEA 24B **USD 975** (experimental, non-PMA, P3), only if a G3X system is installed; logging uses the EFIS | 60–80+ | **≈ 8,000–12,000+** [Y] | + 0.3–0.5 kg on top of Tier 4 | Digital self-monitoring → better reliability and fewer unwanted warnings (T2 §5c(1)). Each sensor testable individually (T2 §5d(2)). Recorder answers "was it locked?" which PKBWL and EASA AD 2024-0059 could not (R0, G4). |

Notes on the table [Y]:
- Labour bands are judgement. The only regulator-printed numbers are the anchors cited.
- Tier 3 MIL sensors: USD 908.84 is a single distributor's qty-1 price for a discontinued part (P4). Industrial sealed switches cost far less, but the RS price page returned 403.
- Mass of the Van's kit and of the switches is not listed by the vendors.
- Tier 4 and 5 parts totals are guesses where no catalogue price was obtained. They are marked [Y] and should be presented as "order of magnitude".

## 7. Design implications [Y]

1. **Sense the bolt, not the handle.** UAL811/Pan Am 125, BD-10 and L-39 all had proxy sensing that showed "safe" with latches open. Per-point sensing (Tier 3) is the minimum tier that answers the AAIB/EASA "partially locked" hazard.
2. **The cheapest tiers are cheap but unproven.** Placards (USD ~180) and marks (USD ~275–420) are what regulators actually mandated (Extra AD, DA 40 NPRM). No source measured their effect. Present them as the baseline that every tier keeps.
3. **The light alone has a poor field record.** DA 40/42 had a door-latch warning on every aircraft and kept losing doors. The two reasons were a shared light that was normally on and a crew that dismissed it. Our design must stay dark/white in normal taxi and only go red when unlocked with intent to take off.
4. **False alarms are dangerous, not only annoying.** Fokker 100: a false red light made the crew open the door in flight. Rig tolerances tightly (Fokker went to 0.3 ± 0.2 mm). Add a "don't touch the handle in flight" placard.
5. **Persistence and intensity buy effectiveness; annoyance loses it.** Car data: loud + persistent reminders reach ~80 % conversion, mild ones about half. But audible lane and speed alerts get switched off (14 % on vs 71 % for visual). Use voice only for the high-urgency state, vibration as the persistent channel, and never sound during normal open-canopy taxi.
6. **Treat the alert as a no-go item with failure annunciation.** TOWS lesson (AC 25.703-1): ordinary alert systems at ~10⁻³/fh are not good enough when the hazard is catastrophic. Self-test, per-sensor test and "CANOPY SYS" failure message belong to Tier 4–5.
7. **Recommended presentation:** CHEAP = Tier 1 + Tier 3 with commercial sensors (≈ USD 2,500–4,000 + EUR 398). EXPENSIVE = Tier 5 (≈ USD 8,000–12,000+). Show that the step from Tier 2 to Tier 3 buys the most evidence per dollar.
8. **Mandate matters.** Duo Discus: a voluntary fix was available from 2004 and only mandated in 2024 after a fatal accident. A retrofit proposal should say whether it is to be optional (SB) or mandated (AD).

## 8. NOT VERIFIED / gaps

1. **No before/after event statistics** for any door/canopy warning AD (A1–A7, B1). The effectiveness claims for aircraft warnings are therefore case-based, not rate-based.
2. Labour hours per tier and all Tier 4–5 totals are R8 estimates [Y], not quotes.
3. Vibration motor price (P5 shows none), solenoid/throttle-gate price, industrial sealed switch price (RS 403), Van's AV-01957 board price (R7: 404).
4. Williams et al. 2002 (Ford Belt-Minder) numbers 71 % → 76 %: search snippets only; full text not obtained.
5. NHTSA DOT HS 811 097 (enhanced SBR features): 403, not read.
6. EASA AD 2008-0197 text: not read directly (EASA maintenance page); content taken from FAA SAFO 08021.
7. TOWS retrofit cost: not found.
8. Gear-up horn "power-on approach keeps it silent" and headset masking: AOPA wording seen in a search summary; the fetched AOPA texts (G1, G2) confirm distraction and stall-horn confusion only.
9. BGA/LBA canopy campaign statistics: not reachable (BGA 2022 review 404). No glider canopy-lock warning product found.
10. Aviation Consumer comparison of gear alerters (prices, install hours): paywalled.
11. Number of lock points on every Extra NG serial: not checked here; n = 3 in Table 2 is an example.
12. EUR prices were not converted; any USD total that includes them is approximate.
